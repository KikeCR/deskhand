"""FastAPI layer exposing the onboarding pipeline over HTTP for the frontend.

This is intentionally thin: no business logic lives here beyond request/
response shaping. That keeps pipeline.run_onboarding() the single source
of truth, so a future webhook or n8n trigger is a small addition here
rather than a rewrite.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from decision.engine import DecisionResult
from pipeline import run_onboarding
from webhook import (
    HRISWebhookPayload,
    WebhookAuthError,
    normalize_hris_payload,
    verify_webhook_secret,
)

SAMPLE_HIRES_DIR = Path(__file__).resolve().parent / "data" / "sample_hires"

app = FastAPI(title="DeskHand Onboarding API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # portfolio demo only; scope this down for a real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)


class HireProfile(BaseModel):
    name: str
    role: str
    department: str
    location: str
    start_date: str


class DecisionPayload(BaseModel):
    location_track: str
    location_steps: list[str]
    dept_track: str
    dept_steps: list[str]
    explanation: list[str]

    @classmethod
    def from_decision(cls, decision: DecisionResult) -> "DecisionPayload":
        return cls(
            location_track=decision.location_track,
            location_steps=decision.location_steps,
            dept_track=decision.dept_track,
            dept_steps=decision.dept_steps,
            explanation=decision.explanation,
        )


class OnboardingResponse(BaseModel):
    hire: HireProfile
    decision: DecisionPayload
    research_notes: str
    checklist_markdown: str
    output_path: str


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/sample-hires")
def sample_hires() -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(SAMPLE_HIRES_DIR.glob("*.json"))]


def _run_and_build_response(hire: dict) -> OnboardingResponse:
    result = run_onboarding(hire)
    return OnboardingResponse(
        hire=HireProfile(**hire),
        decision=DecisionPayload.from_decision(result.decision),
        research_notes=result.research_notes,
        checklist_markdown=result.checklist_markdown,
        output_path=result.output_path,
    )


@app.post("/api/onboarding/run", response_model=OnboardingResponse)
def run(hire: HireProfile) -> OnboardingResponse:
    return _run_and_build_response(hire.model_dump())


@app.post("/webhook/hris", response_model=OnboardingResponse)
def hris_webhook(
    payload: HRISWebhookPayload,
    x_webhook_secret: str | None = Header(default=None),
) -> OnboardingResponse:
    """Entry point for a real HRIS or an n8n workflow.

    Accepts the HRIS's own payload shape, normalizes it into the internal
    hire dict, and calls the exact same run_onboarding() the CLI and the
    UI use. See webhook.py for the normalization and auth logic.
    """
    try:
        verify_webhook_secret(x_webhook_secret)
    except WebhookAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    hire = normalize_hris_payload(payload)
    return _run_and_build_response(hire)
