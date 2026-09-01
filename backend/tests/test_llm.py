import pytest

import llm

ALL_PROVIDER_ENV_VARS = [
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_MODEL",
    "KIMI_API_KEY",
    "KIMI_MODEL",
    "KIMI_BASE_URL",
    "LLM_PROVIDERS",
]


@pytest.fixture(autouse=True)
def clean_provider_env(monkeypatch):
    """Tests must control provider availability explicitly, not inherit
    whatever backend/.env (loaded by importing pipeline.py elsewhere in the
    suite) happens to have set."""
    for var in ALL_PROVIDER_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


def test_raises_when_no_provider_is_configured():
    with pytest.raises(llm.ProviderUnavailable):
        llm.build_llm_chain()


def test_uses_only_openai_when_only_openai_key_is_set(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    chain = llm.build_llm_chain()

    assert [name for name, _ in chain] == ["openai"]


def test_respects_llm_providers_order(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
    monkeypatch.setenv("KIMI_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_PROVIDERS", "deepseek,kimi,openai")

    chain = llm.build_llm_chain()

    assert [name for name, _ in chain] == ["deepseek", "kimi", "openai"]


def test_skips_providers_with_no_api_key(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_PROVIDERS", "openai,deepseek,kimi")

    chain = llm.build_llm_chain()

    assert [name for name, _ in chain] == ["deepseek"]


def test_ignores_unknown_provider_names(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_PROVIDERS", "unknown-provider,openai")

    chain = llm.build_llm_chain()

    assert [name for name, _ in chain] == ["openai"]
