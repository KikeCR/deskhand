from rag.retriever import query


def test_query_returns_grounded_chunk_for_remote_topic(empty_collection):
    empty_collection.add(
        ids=["it::remote", "it::office"],
        documents=[
            "Remote employees install the VPN client and get a laptop shipped home.",
            "In-office employees pick up a badge at the front desk.",
        ],
        metadatas=[{"source": "it_setup_checklist.md"}, {"source": "it_setup_checklist.md"}],
    )

    results = query("What does a remote employee need for VPN access?", k=1, collection=empty_collection)

    assert len(results) == 1
    assert "VPN" in results[0]["content"]
    assert results[0]["source"] == "it_setup_checklist.md"
    assert "distance" in results[0]


def test_query_distinguishes_engineering_from_sales_docs(empty_collection):
    empty_collection.add(
        ids=["eng::1", "sales::1"],
        documents=[
            "Engineering new hires get GitHub org access and cloud sandbox credentials.",
            "Sales new hires get CRM access and a commission plan document.",
        ],
        metadatas=[{"source": "onboarding_policy.md"}, {"source": "onboarding_policy.md"}],
    )

    results = query("What CRM access does a new sales hire need?", k=1, collection=empty_collection)

    assert "CRM" in results[0]["content"]


def test_query_returns_k_results(empty_collection):
    empty_collection.add(
        ids=["a", "b", "c"],
        documents=["remote doc one", "office doc two", "benefits doc three"],
        metadatas=[{"source": "a.md"}, {"source": "b.md"}, {"source": "c.md"}],
    )

    results = query("remote", k=2, collection=empty_collection)

    assert len(results) == 2
