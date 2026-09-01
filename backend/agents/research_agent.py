"""Research Agent: pulls grounded onboarding steps from the RAG vectorstore."""

from __future__ import annotations

from crewai import Agent, Task

from decision.engine import DecisionResult
from rag.tools import RAGSearchTool


def build_research_agent(llm: str) -> Agent:
    return Agent(
        role="Onboarding Research Specialist",
        goal=(
            "Find the exact company policy details that back up this "
            "hire's onboarding steps, so nothing in the final checklist is "
            "an unsupported guess."
        ),
        backstory=(
            "You know the company's onboarding policy, IT setup "
            "checklist, benefits FAQ, and remote-work policy live in a "
            "searchable knowledge base, and you always check it rather "
            "than relying on memory. You cite which document each detail "
            "came from."
        ),
        tools=[RAGSearchTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def build_research_task(agent: Agent, hire: dict, decision: DecisionResult, intake_task: Task) -> Task:
    return Task(
        description=(
            f"This hire is on the '{decision.location_track}' location "
            f"track and the '{decision.dept_track}' department track.\n\n"
            "Use the search_company_docs tool to run at least three "
            "targeted searches that ground this hire's onboarding in "
            "actual company policy, for example:\n"
            f"- Week 1 steps for a {decision.location_track.replace('_', ' ')} employee\n"
            f"- Tool access and setup for the {hire.get('department', 'their')} department\n"
            "- Any benefits or policy details specific to this hire's situation\n\n"
            "For each finding, report the excerpt and which source "
            "document it came from. Do not state a policy detail unless "
            "you found it via the tool. Never use an em dash (the — "
            "character); use a comma, period, or regular hyphen instead."
        ),
        expected_output=(
            "A list of grounded findings, each with the excerpt and its "
            "source document name."
        ),
        agent=agent,
        context=[intake_task],
    )
