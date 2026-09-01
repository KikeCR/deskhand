"""Intake Agent: validates and normalizes a new hire's profile."""

from __future__ import annotations

from crewai import Agent, Task

REQUIRED_FIELDS = ["name", "role", "department", "location", "start_date"]


def build_intake_agent(llm: str) -> Agent:
    return Agent(
        role="HR Intake Coordinator",
        goal=(
            "Confirm that a new hire's profile from the HR system is "
            "complete and clearly restate it so downstream agents have an "
            "unambiguous picture of who this onboarding is for."
        ),
        backstory=(
            "You've processed thousands of new-hire records and know "
            "exactly which fields matter for onboarding: name, role, "
            "department, work location, and start date. You never invent "
            "information that isn't in the record."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def build_intake_task(agent: Agent, hire: dict) -> Task:
    missing = [f for f in REQUIRED_FIELDS if not hire.get(f)]
    hire_summary = "\n".join(f"- {field}: {hire.get(field, '(missing)')}" for field in REQUIRED_FIELDS)

    return Task(
        description=(
            "Here is a new hire's raw record from the HR system:\n\n"
            f"{hire_summary}\n\n"
            f"Missing required fields: {missing if missing else 'none'}.\n\n"
            "Write a short, clear confirmation of this hire's profile "
            "(name, role, department, location, start date) that the "
            "Research and Reporting agents can rely on. If any required "
            "field is missing, call it out explicitly instead of "
            "guessing a value."
        ),
        expected_output=(
            "A short paragraph confirming the hire's name, role, "
            "department, location, and start date, noting any missing "
            "fields."
        ),
        agent=agent,
    )
