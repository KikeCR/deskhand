"""Trigger-agnostic core of DeskHand: run_onboarding(hire) -> OnboardingResult.

This is the one function every entry point (CLI, HTTP API, and eventually
a webhook/n8n trigger) calls. Keeping it here, decoupled from argparse or
FastAPI, means adding a new trigger is a matter of calling this function,
not duplicating pipeline logic.
"""

from __future__ import annotations

import ctypes
import gc
import os
import platform
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# setdefault, not direct assignment, so an operator who explicitly wants
# these on (e.g. to debug against CrewAI's own trace UI) can still opt in
# via their own .env / platform env vars.
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

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


def _trim_memory() -> None:
    """Return freed heap memory to the OS after a request.

    glibc's malloc (the allocator in Linux containers, i.e. production)
    caches freed memory for reuse instead of handing it back to the OS
    immediately, which makes a process's reported RSS look like it never
    shrinks even once a request's working memory is genuinely garbage
    collected. This keeps the *baseline* between requests lower on a
    memory-constrained host; it does not reduce the peak usage during a
    single crew execution, which is a separate, larger constraint (see
    the Deployment section of the README). No-op on non-Linux platforms
    (e.g. local macOS dev), which don't expose this call.
    """
    if platform.system() != "Linux":
        return
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except OSError:
        pass


def run_onboarding(hire: dict) -> OnboardingResult:
    build_vectorstore()  # idempotent: no-op once the collection is seeded

    decision = decide_onboarding_track(hire)

    try:
        crew_output = kickoff_with_fallback(hire, decision)

        task_outputs = crew_output.tasks_output
        research_notes = str(task_outputs[1].raw)
        checklist_body = str(task_outputs[-1].raw)
    finally:
        gc.collect()
        _trim_memory()

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
