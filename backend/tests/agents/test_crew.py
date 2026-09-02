from unittest.mock import MagicMock

import pytest

import agents.crew as crew_module
from decision.engine import decide_onboarding_track


@pytest.fixture(autouse=True)
def reset_llm_chain_cache(monkeypatch):
    """_get_llm_chain() caches at module scope; each test must start from
    an empty cache so mocking build_llm_chain() actually takes effect."""
    monkeypatch.setattr(crew_module, "_cached_llm_chain", None)


def test_kickoff_with_fallback_falls_through_to_the_next_provider(
    monkeypatch, remote_engineer_hire
):
    decision = decide_onboarding_track(remote_engineer_hire)

    failing_crew = MagicMock()
    failing_crew.kickoff.side_effect = RuntimeError("openai: insufficient_quota")
    working_crew = MagicMock()
    working_crew.kickoff.return_value = "success"

    crews = iter([failing_crew, working_crew])
    monkeypatch.setattr(
        crew_module, "build_llm_chain", lambda: [("openai", object()), ("deepseek", object())]
    )
    monkeypatch.setattr(crew_module, "build_onboarding_crew", lambda *a, **k: next(crews))

    result = crew_module.kickoff_with_fallback(remote_engineer_hire, decision)

    assert result == "success"
    failing_crew.kickoff.assert_called_once()
    working_crew.kickoff.assert_called_once()


def test_kickoff_with_fallback_raises_when_every_provider_fails(
    monkeypatch, remote_engineer_hire
):
    decision = decide_onboarding_track(remote_engineer_hire)

    always_fails = MagicMock()
    always_fails.kickoff.side_effect = RuntimeError("boom")

    monkeypatch.setattr(
        crew_module, "build_llm_chain", lambda: [("openai", object()), ("deepseek", object())]
    )
    monkeypatch.setattr(crew_module, "build_onboarding_crew", lambda *a, **k: always_fails)

    with pytest.raises(RuntimeError, match="All configured LLM providers failed"):
        crew_module.kickoff_with_fallback(remote_engineer_hire, decision)


def test_get_llm_chain_builds_the_chain_only_once_across_calls(monkeypatch):
    """Regression test: build_llm_chain() constructs fresh LLM client
    objects (each wrapping its own native HTTP resources). Rebuilding it
    on every request measurably grew resident memory per request in
    production; _get_llm_chain() must reuse the same chain instead."""
    build_spy = MagicMock(return_value=[("openai", object())])
    monkeypatch.setattr(crew_module, "build_llm_chain", build_spy)

    first = crew_module._get_llm_chain()
    second = crew_module._get_llm_chain()
    third = crew_module._get_llm_chain()

    assert first is second is third
    build_spy.assert_called_once()
