"""Trigger-agnostic core of DeskHand: run_onboarding(hire) -> OnboardingResult.

This is the one function every entry point (CLI, HTTP API, and eventually
a webhook/n8n trigger) calls. Keeping it here, decoupled from argparse or
FastAPI, means adding a new trigger is a matter of calling this function,
not duplicating pipeline logic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from agents.crew import kickoff_with_fallback  # noqa: E402
from decision.engine import DecisionResult, decide_onboarding_track  # noqa: E402
from rag.ingest import build_vectorstore  # noqa: E402

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


@dataclass
class OnboardingResult:
    hire: dict
    decision: DecisionResult
    research_notes: str
    checklist_markdown: str
    output_path: str


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "hire"


def _render_decision_log(decision: DecisionResult) -> str:
    lines = ["## Why These Steps (Decision Log)", ""]
    lines += [f"- {line}" for line in decision.explanation]
    return "\n".join(lines)


def run_onboarding(hire: dict) -> OnboardingResult:
    build_vectorstore()  # idempotent: no-op once the collection is seeded

    decision = decide_onboarding_track(hire)

    crew_output = kickoff_with_fallback(hire, decision)

    task_outputs = crew_output.tasks_output
    research_notes = str(task_outputs[1].raw)
    checklist_body = str(task_outputs[-1].raw)

    checklist_markdown = f"{checklist_body}\n\n{_render_decision_log(decision)}\n"

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"{_slugify(hire.get('name', 'hire'))}_onboarding_checklist.md"
    output_path.write_text(checklist_markdown)

    return OnboardingResult(
        hire=hire,
        decision=decision,
        research_notes=research_notes,
        checklist_markdown=checklist_markdown,
        output_path=str(output_path),
    )
