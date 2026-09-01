"""Query interface over the persisted Chroma collection of company docs."""

from __future__ import annotations

from rag.ingest import get_collection


def query(text: str, k: int = 4, collection=None) -> list[dict]:
    """Return the top-k grounded chunks for a query.

    Each result is {"content": str, "source": str, "distance": float}.
    """
    collection = collection or get_collection()
    results = collection.query(query_texts=[text], n_results=k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {"content": doc, "source": meta["source"], "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]
