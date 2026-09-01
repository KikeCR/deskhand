"""Reporting Agent: compiles the intake + research + decision output into a checklist."""

from __future__ import annotations

from crewai import Agent, Task

from decision.engine import DecisionResult


def build_reporting_agent(llm: str) -> Agent:
    return Agent(
        role="Onboarding Report Writer",
        goal=(
            "Turn the confirmed hire profile and grounded research into a "
            "clear, actionable Week 1 onboarding checklist."
        ),
        backstory=(
            "You write onboarding checklists that new hires and their "
            "managers actually use. You organize steps clearly, keep "
            "language plain, and never invent a step that isn't backed by "
            "the research you were given."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def build_reporting_task(
    agent: Agent,
    hire: dict,
    decision: DecisionResult,
    intake_task: Task,
    research_task: Task,
) -> Task:
    location_steps = "\n".join(f"- {s}" for s in decision.location_steps)
    dept_steps = "\n".join(f"- {s}" for s in decision.dept_steps)

    return Task(
        description=(
            "Write a Week 1 onboarding checklist in markdown for "
            f"{hire.get('name')}, a {hire.get('role')} joining "
            f"{hire.get('department')}, starting {hire.get('start_date')}.\n\n"
            "Structure it with these markdown sections, in this order:\n"
            "1. '# Week 1 Onboarding Checklist' with the hire's name, role, "
            "department, location, and start date underneath.\n"
            "2. '## IT & Equipment' — incorporate these required steps "
            f"(rephrase for clarity but keep the substance):\n{location_steps}\n"
            "3. '## Tool & System Access' — incorporate these required "
            f"steps:\n{dept_steps}\n"
            "4. '## From Company Policy' — 2-4 bullets drawn directly "
            "from the Research agent's grounded findings, each ending "
            "with its source document in parentheses.\n\n"
            "Do not add steps beyond what's grounded in the required "
            "lists above or the research findings."
        ),
        expected_output=(
            "A complete markdown onboarding checklist with the four "
            "sections described above."
        ),
        agent=agent,
        context=[intake_task, research_task],
    )
