"""Chunk the mock company docs and embed them into a persistent Chroma collection."""

from __future__ import annotations

import re
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "mock_docs"
VECTORSTORE_DIR = Path(__file__).resolve().parent.parent / "vectorstore"
COLLECTION_NAME = "company_docs"


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
    """
    client = client or chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
    embedding_function = embedding_function or DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=embedding_function
    )


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
