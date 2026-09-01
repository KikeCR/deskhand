"""API contract tests. pipeline.run_onboarding is monkeypatched so this
suite never spins up a real crew or calls OpenAI.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

import api
from decision.engine import decide_onboarding_track
from pipeline import OnboardingResult


def _fake_run_onboarding(hire: dict) -> OnboardingResult:
    decision = decide_onboarding_track(hire)
    return OnboardingResult(
        hire=hire,
        decision=decision,
        research_notes=f"Fake grounded research for {hire['name']}.",
        checklist_markdown=f"# Week 1 Onboarding Checklist\n\nFor {hire['name']}.",
        output_path=f"/tmp/{hire['name']}.md",
    )


def test_health():
    client = TestClient(api.app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_sample_hires_returns_both_bundled_profiles():
    client = TestClient(api.app)

    response = client.get("/api/sample-hires")

    assert response.status_code == 200
    names = {hire["name"] for hire in response.json()}
    assert names == {"Priya Nakamura", "Marcus Delgado"}


def test_run_onboarding_returns_decision_and_checklist(monkeypatch, remote_engineer_hire):
    monkeypatch.setattr(api, "run_onboarding", _fake_run_onboarding)
    client = TestClient(api.app)

    response = client.post("/api/onboarding/run", json=remote_engineer_hire)

    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["location_track"] == "remote"
    assert body["decision"]["dept_track"] == "engineering"
    assert "Week 1 Onboarding Checklist" in body["checklist_markdown"]


def test_run_onboarding_branches_differently_for_the_two_sample_hires(
    monkeypatch, remote_engineer_hire, inoffice_sales_hire
):
    monkeypatch.setattr(api, "run_onboarding", _fake_run_onboarding)
    client = TestClient(api.app)

    remote_response = client.post("/api/onboarding/run", json=remote_engineer_hire)
    sales_response = client.post("/api/onboarding/run", json=inoffice_sales_hire)

    remote_decision = remote_response.json()["decision"]
    sales_decision = sales_response.json()["decision"]

    assert remote_decision["location_track"] != sales_decision["location_track"]
    assert remote_decision["dept_track"] != sales_decision["dept_track"]
    assert remote_decision["location_steps"] != sales_decision["location_steps"]
