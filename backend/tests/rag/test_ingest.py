from unittest.mock import MagicMock

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

import rag.ingest as ingest_module
from rag.ingest import build_vectorstore, chunk_markdown, get_collection, load_and_chunk_docs


def test_default_embedding_function_points_at_the_vendored_model():
    """Regression test: chromadb's DefaultEmbeddingFunction downloads its
    model to Path.home()/.cache/... on first use, which caused a real
    crash loop in production (a fresh Render instance whose disk didn't
    survive a restart re-downloaded the ~80MB model every time, each
    download blocking a request for minutes). The model is vendored into
    the repo instead; this guards against that redirect quietly reverting.
    """
    assert DefaultEmbeddingFunction.DOWNLOAD_PATH == ingest_module._VENDORED_MODEL_DIR

    vendored_onnx_dir = ingest_module._VENDORED_MODEL_DIR / "onnx"
    for filename in (
        "config.json",
        "model.onnx",
        "special_tokens_map.json",
        "tokenizer_config.json",
        "tokenizer.json",
        "vocab.txt",
    ):
        assert (vendored_onnx_dir / filename).exists(), f"missing vendored file: {filename}"


def test_chunk_markdown_splits_on_h2_headers():
    text = (
        "# Doc Title\n\n"
        "## First Section\n\nFirst body text.\n\n"
        "## Second Section\n\nSecond body text."
    )

    chunks = chunk_markdown(text, source="doc.md")

    assert len(chunks) == 2
    assert chunks[0]["content"].startswith("## First Section")
    assert chunks[1]["content"].startswith("## Second Section")
    assert all(c["source"] == "doc.md" for c in chunks)


def test_chunk_markdown_drops_bare_title_with_no_body():
    text = "# Just A Title\n\n## Only Section\n\nSome content."

    chunks = chunk_markdown(text, source="doc.md")

    assert len(chunks) == 1
    assert chunks[0]["content"].startswith("## Only Section")


def test_load_and_chunk_docs_covers_all_mock_docs():
    chunks = load_and_chunk_docs()

    sources = {c["source"] for c in chunks}
    assert sources == {
        "onboarding_policy.md",
        "it_setup_checklist.md",
        "benefits_faq.md",
        "remote_work_policy.md",
    }
    assert len(chunks) > 4


def test_get_collection_caches_expensive_objects_across_calls(monkeypatch):
    """Regression test: get_collection() used to build a brand new Chroma
    client + onnxruntime embedding session on every call (i.e. on every
    request), which grew memory enough to exceed a 512MB container and
    trigger repeated restarts in production. With no explicit
    client/embedding_function, both should be constructed exactly once.
    """
    monkeypatch.setattr(ingest_module, "_cached_collection", None)

    fake_collection = object()
    fake_client = MagicMock()
    fake_client.get_or_create_collection.return_value = fake_collection
    fake_client_cls = MagicMock(return_value=fake_client)
    fake_embedding_fn_cls = MagicMock()

    monkeypatch.setattr(ingest_module.chromadb, "PersistentClient", fake_client_cls)
    monkeypatch.setattr(ingest_module, "DefaultEmbeddingFunction", fake_embedding_fn_cls)

    first = get_collection()
    second = get_collection()
    third = get_collection()

    assert first is second is third is fake_collection
    fake_client_cls.assert_called_once()
    fake_embedding_fn_cls.assert_called_once()


def test_get_collection_bypasses_cache_when_given_explicit_args(fake_embedding_function, tmp_path):
    import chromadb

    client_a = chromadb.PersistentClient(path=str(tmp_path / "a"))
    client_b = chromadb.PersistentClient(path=str(tmp_path / "b"))

    collection_a = get_collection(client=client_a, embedding_function=fake_embedding_function)
    collection_b = get_collection(client=client_b, embedding_function=fake_embedding_function)

    assert collection_a is not collection_b


def test_build_vectorstore_is_idempotent(fake_embedding_function, tmp_path):
    import chromadb

    client = chromadb.PersistentClient(path=str(tmp_path))

    first_count = build_vectorstore(client=client, embedding_function=fake_embedding_function)
    second_count = build_vectorstore(client=client, embedding_function=fake_embedding_function)

    assert first_count == second_count
    assert first_count > 0
