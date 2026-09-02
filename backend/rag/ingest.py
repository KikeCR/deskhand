"""Chunk the mock company docs and embed them into a persistent Chroma collection."""

from __future__ import annotations

import re
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction, ONNXMiniLM_L6_V2

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "mock_docs"
VECTORSTORE_DIR = Path(__file__).resolve().parent.parent / "vectorstore"
COLLECTION_NAME = "company_docs"

# chromadb's DefaultEmbeddingFunction downloads its ~80MB model to
# Path.home()/.cache/chroma/onnx_models/... on first use. On a host whose
# disk doesn't survive a restart, that's a real crash loop: confirmed in
# production, a fresh instance re-downloaded the model on every restart,
# each one blocking a request for minutes and likely triggering the next
# restart before the download even finished. The model files are vendored
# into the repo instead (see data/onnx_model/).
#
# DefaultEmbeddingFunction.__call__ hardcodes `ONNXMiniLM_L6_V2()(input)`,
# constructing a fresh instance of that *other* class directly rather than
# via `self`, so DOWNLOAD_PATH must be patched on ONNXMiniLM_L6_V2 itself,
# not on DefaultEmbeddingFunction. An earlier version of this patched the
# wrong class: it looked like it worked locally only because this
# machine's persistent vectorstore already had every chunk embedded from
# prior local runs, so the embedding function was never actually called to
# expose the mistake, and separately because this machine's OS-default
# cache path (~/.cache/chroma/...) already happened to have the real
# model files downloaded from earlier testing.
_VENDORED_MODEL_DIR = Path(__file__).resolve().parent.parent / "data" / "onnx_model" / "all-MiniLM-L6-v2"
ONNXMiniLM_L6_V2.DOWNLOAD_PATH = _VENDORED_MODEL_DIR

_cached_collection = None


def chunk_markdown(text: str, source: str) -> list[dict]:
    """Split a markdown doc into chunks along its "## " section headers.

    Each chunk keeps its header as a prefix so it reads as a standalone
    excerpt once retrieved out of context.
    """
    sections = re.split(r"\n(?=## )", text.strip())
    chunks = []
    for section in sections:
        section = section.strip()
        if not section or section.startswith("# ") and "\n" not in section:
            continue  # skip a bare H1 title with no body content
        chunks.append({"content": section, "source": source})
    return chunks


def load_and_chunk_docs() -> list[dict]:
    chunks = []
    for doc_path in sorted(DATA_DIR.glob("*.md")):
        text = doc_path.read_text()
        chunks.extend(chunk_markdown(text, source=doc_path.name))
    return chunks


def get_collection(client: chromadb.ClientAPI | None = None, embedding_function=None):
    """Get (or create) the company-docs collection.

    Embeddings run on a free local model (chromadb's default all-MiniLM-L6-v2,
    via onnxruntime) rather than a paid API, so retrieval never depends on
    a provider's billing status. It downloads once to ~/.cache/chroma on
    first use and runs fully offline after that.

    With no explicit client/embedding_function (the production call shape,
    used on every request via build_vectorstore()), the collection is built
    once per process and cached, rather than reconstructing a new Chroma
    client and a new onnxruntime embedding session on every single request.
    The latter was measured to grow memory per request under load, enough
    to exceed a 512MB container's limit and trigger repeated restarts.
    Tests that pass an explicit client/embedding_function (a tmp_path client,
    a fake embedding function) bypass the cache entirely, so the offline
    test suite is unaffected.
    """
    global _cached_collection

    if client is not None or embedding_function is not None:
        client = client or chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
        embedding_function = embedding_function or DefaultEmbeddingFunction()
        return client.get_or_create_collection(
            name=COLLECTION_NAME, embedding_function=embedding_function
        )

    if _cached_collection is None:
        client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
        _cached_collection = client.get_or_create_collection(
            name=COLLECTION_NAME, embedding_function=DefaultEmbeddingFunction()
        )
    return _cached_collection


def build_vectorstore(
    client: chromadb.ClientAPI | None = None,
    force_rebuild: bool = False,
    embedding_function=None,
) -> int:
    """Embed and persist all mock docs. Returns the number of chunks stored.

    Idempotent: if the collection is already populated, this is a no-op
    unless force_rebuild=True (embedding calls cost money and don't need
    to be repeated on every run).
    """
    collection = get_collection(client, embedding_function=embedding_function)

    if force_rebuild and collection.count() > 0:
        existing_ids = collection.get()["ids"]
        collection.delete(ids=existing_ids)

    if collection.count() > 0:
        return collection.count()

    chunks = load_and_chunk_docs()
    collection.add(
        ids=[f"{c['source']}::{i}" for i, c in enumerate(chunks)],
        documents=[c["content"] for c in chunks],
        metadatas=[{"source": c["source"]} for c in chunks],
    )
    return len(chunks)


if __name__ == "__main__":
    count = build_vectorstore()
    print(f"Vectorstore ready with {count} chunks at {VECTORSTORE_DIR}")
