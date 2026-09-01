from unittest.mock import MagicMock

import pytest

import agents.crew as crew_module
from decision.engine import decide_onboarding_track


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
