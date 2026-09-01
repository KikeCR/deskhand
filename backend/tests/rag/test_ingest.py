from rag.ingest import build_vectorstore, chunk_markdown, load_and_chunk_docs


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


def test_build_vectorstore_is_idempotent(fake_embedding_function, tmp_path):
    import chromadb

    client = chromadb.PersistentClient(path=str(tmp_path))

    first_count = build_vectorstore(client=client, embedding_function=fake_embedding_function)
    second_count = build_vectorstore(client=client, embedding_function=fake_embedding_function)

    assert first_count == second_count
    assert first_count > 0
