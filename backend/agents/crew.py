"""Assembles the Intake -> Research -> Reporting crew for one onboarding run."""

from __future__ import annotations

import os

from crewai import LLM, Crew, CrewOutput, Process

from agents.intake_agent import build_intake_agent, build_intake_task
from agents.reporting_agent import build_reporting_agent, build_reporting_task
from agents.research_agent import build_research_agent, build_research_task
from decision.engine import DecisionResult
from llm import build_llm_chain

# Off by default: verbose mode makes every agent step pretty-print a
# formatted panel via `rich`, which is useful when watching a run locally
# but is pure overhead (CPU + log volume) on a deployed instance where
# nobody is tailing the console. Opt in with CREWAI_VERBOSE=true.
VERBOSE = os.environ.get("CREWAI_VERBOSE", "false").lower() == "true"


def build_onboarding_crew(hire: dict, decision: DecisionResult, llm: LLM) -> Crew:
    intake_agent = build_intake_agent(llm, verbose=VERBOSE)
    research_agent = build_research_agent(llm, verbose=VERBOSE)
    reporting_agent = build_reporting_agent(llm, verbose=VERBOSE)

    intake_task = build_intake_task(intake_agent, hire)
    research_task = build_research_task(research_agent, hire, decision, intake_task)
    reporting_task = build_reporting_task(
        reporting_agent, hire, decision, intake_task, research_task
    )

    return Crew(
        agents=[intake_agent, research_agent, reporting_agent],
        tasks=[intake_task, research_task, reporting_task],
        process=Process.sequential,
        verbose=VERBOSE,
    )


def kickoff_with_fallback(hire: dict, decision: DecisionResult) -> CrewOutput:
    """Run the crew, trying each configured LLM provider in order.

    An operator with credits on DeepSeek or Kimi instead of OpenAI can
    still run the full crew: whichever provider's API key is set gets
    tried in LLM_PROVIDERS order, falling through to the next provider on
    failure (auth error, rate limit, out of quota, etc.) instead of
    hard-failing on the first provider that happens to be unavailable.
    """
    errors: list[str] = []
    for provider_name, provider_llm in build_llm_chain():
        crew = build_onboarding_crew(hire, decision, provider_llm)
        try:
            return crew.kickoff()
        except Exception as exc:  # noqa: BLE001 - any provider failure should fall through
            errors.append(f"{provider_name}: {exc}")

    raise RuntimeError("All configured LLM providers failed:\n" + "\n".join(errors))
