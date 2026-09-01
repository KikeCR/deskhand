"""Assembles the Intake -> Research -> Reporting crew for one onboarding run."""

from __future__ import annotations

import os

from crewai import Crew, Process

from agents.intake_agent import build_intake_agent, build_intake_task
from agents.reporting_agent import build_reporting_agent, build_reporting_task
from agents.research_agent import build_research_agent, build_research_task
from decision.engine import DecisionResult


def build_onboarding_crew(hire: dict, decision: DecisionResult) -> Crew:
    llm = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    intake_agent = build_intake_agent(llm)
    research_agent = build_research_agent(llm)
    reporting_agent = build_reporting_agent(llm)

    intake_task = build_intake_task(intake_agent, hire)
    research_task = build_research_task(research_agent, hire, decision, intake_task)
    reporting_task = build_reporting_task(
        reporting_agent, hire, decision, intake_task, research_task
    )

    return Crew(
        agents=[intake_agent, research_agent, reporting_agent],
        tasks=[intake_task, research_task, reporting_task],
        process=Process.sequential,
        verbose=True,
    )
