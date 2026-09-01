"""Shared fixtures: keep the whole backend test suite offline and free.

No test in this suite makes a real OpenAI API call. Embeddings are faked
deterministically and the crew's LLM calls are monkeypatched out wherever
they'd otherwise run, so `pytest` works with no OPENAI_API_KEY set and no
network access — important for a repo recruiters clone and run CI on.
"""

from __future__ import annotations

import json
from pathlib import Path

import chromadb
import pytest
from chromadb.api.types import EmbeddingFunction

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class FakeEmbeddingFunction(EmbeddingFunction):
    """Deterministic, offline stand-in for OpenAIEmbeddingFunction.

    Encodes each text as a bag-of-keywords vector so semantically related
    fixture text lands close together and unrelated text lands far apart,
    without any network call. Subclasses chromadb's EmbeddingFunction
    protocol class (rather than just duck-typing __call__) so it also
    picks up the default embed_query/embed_documents implementations
    chromadb's Collection.query() relies on.
    """

    VOCAB = [
        "remote",
        "office",
        "badge",
        "vpn",
        "engineering",
        "sales",
        "github",
        "crm",
        "benefits",
        "pto",
    ]

    def __init__(self) -> None:
        pass

    def __call__(self, input: list[str]) -> list[list[float]]:
        vectors = []
        for text in input:
            lowered = text.lower()
            vectors.append([float(word in lowered) for word in self.VOCAB])
        return vectors

    @staticmethod
    def name() -> str:
        return "fake-keyword-embedding"

    def get_config(self) -> dict:
        return {}


@pytest.fixture
def fake_embedding_function() -> FakeEmbeddingFunction:
    return FakeEmbeddingFunction()


@pytest.fixture
def empty_collection(fake_embedding_function):
    client = chromadb.EphemeralClient()
    return client.get_or_create_collection(
        name="test_company_docs", embedding_function=fake_embedding_function
    )


@pytest.fixture
def remote_engineer_hire() -> dict:
    return json.loads((DATA_DIR / "sample_hires" / "remote_engineer.json").read_text())


@pytest.fixture
def inoffice_sales_hire() -> dict:
    return json.loads((DATA_DIR / "sample_hires" / "inoffice_sales.json").read_text())
