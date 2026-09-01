from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import pipeline


def _fake_crew_output(research_raw: str, checklist_raw: str):
    return SimpleNamespace(
        tasks_output=[
            SimpleNamespace(raw="intake confirmation"),
            SimpleNamespace(raw=research_raw),
            SimpleNamespace(raw=checklist_raw),
        ]
    )


def test_trim_memory_never_raises():
    pipeline._trim_memory()  # should be a safe no-op on any platform


def test_run_onboarding_trims_memory_after_a_successful_run(monkeypatch, remote_engineer_hire, tmp_path):
    monkeypatch.setattr(pipeline, "build_vectorstore", lambda: None)
    monkeypatch.setattr(
        pipeline,
        "kickoff_with_fallback",
        lambda hire, decision: _fake_crew_output("notes", "# Checklist"),
    )
    monkeypatch.setattr(pipeline, "OUTPUT_DIR", tmp_path)
    trim_spy = MagicMock()
    monkeypatch.setattr(pipeline, "_trim_memory", trim_spy)

    pipeline.run_onboarding(remote_engineer_hire)

    trim_spy.assert_called_once()


def test_run_onboarding_trims_memory_even_when_the_crew_run_fails(monkeypatch, remote_engineer_hire):
    monkeypatch.setattr(pipeline, "build_vectorstore", lambda: None)

    def _raise(hire, decision):
        raise RuntimeError("all providers failed")

    monkeypatch.setattr(pipeline, "kickoff_with_fallback", _raise)
    trim_spy = MagicMock()
    monkeypatch.setattr(pipeline, "_trim_memory", trim_spy)

    with pytest.raises(RuntimeError, match="all providers failed"):
        pipeline.run_onboarding(remote_engineer_hire)

    trim_spy.assert_called_once()
