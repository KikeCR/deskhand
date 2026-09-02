from unittest.mock import MagicMock

import pytest
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction, ONNXMiniLM_L6_V2

import rag.ingest as ingest_module
from rag.ingest import build_vectorstore, chunk_markdown, get_collection, load_and_chunk_docs


def test_vendored_model_files_are_present():
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


def test_default_embedding_function_never_attempts_a_download(monkeypatch):
    """Regression test for a real production incident: chromadb's
    DefaultEmbeddingFunction.__call__ hardcodes `ONNXMiniLM_L6_V2()(input)`,
    a fresh instance of a *different* class constructed by direct
    reference rather than via `self`. DOWNLOAD_PATH must be patched on
    ONNXMiniLM_L6_V2 itself for the vendored model to actually be used;
    patching DefaultEmbeddingFunction.DOWNLOAD_PATH (an earlier, wrong fix)
    silently does nothing, because nothing reads it. This exercises the
    real DefaultEmbeddingFunction() call path end to end and fails loudly
    if it ever tries to hit the network again, instead of a test that only
    checks an attribute nothing actually consults.
    """
    assert ONNXMiniLM_L6_V2.DOWNLOAD_PATH == ingest_module._VENDORED_MODEL_DIR

    def _fail_if_called(*args, **kwargs):
        raise AssertionError(
            "DefaultEmbeddingFunction attempted a network download instead "
            "of using the vendored model files"
        )

    monkeypatch.setattr(ONNXMiniLM_L6_V2, "_download", _fail_if_called)

    vector = DefaultEmbeddingFunction()(["a test sentence"])

    assert len(vector) == 1
    assert len(vector[0]) > 0


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
