"""Deterministic branching rules for onboarding steps.

This is plain Python, not an LLM call. Which IT/equipment steps and which
tool-access steps a new hire needs is a business rule, not a judgment
call — leaving it to an LLM's discretion risks silently inconsistent
results between runs. Keeping it as code also makes the branching
testable and gives the rest of the pipeline a structured, auditable
explanation of *why* each step was included.
"""

from __future__ import annotations

from dataclasses import dataclass, field

LOCATION_STEPS = {
    "remote": [
        "IT ships a company laptop and docking station to your home address.",
        "Install the company VPN client and connect on Day 1.",
        "Submit the one-time $500 home-office equipment stipend request.",
        "Read and electronically acknowledge the Remote Work Policy.",
    ],
    "in_office": [
        "Pick up your physical badge and access card at the front desk on Day 1.",
        "Confirm your assigned desk (and locker, if requested) with Facilities.",
        "Visit the on-site IT help desk on Day 1 for your laptop and peripherals.",
        "Pick up your parking permit or transit subsidy card from Facilities.",
    ],
}

DEPARTMENT_STEPS = {
    "engineering": [
        "Accept your invite to the company GitHub organization.",
        "Request access to the cloud sandbox/staging environment.",
        "Set up your local dev environment per the engineering onboarding doc.",
        "Get added to the on-call rotation training track (observer role).",
    ],
    "sales": [
        "Get provisioned in the CRM (Salesforce) with your territory assigned.",
        "Complete sales enablement portal training modules.",
        "Review your commission plan document with your manager.",
        "Shadow two customer calls with a senior account executive.",
    ],
}

DEFAULT_DEPARTMENT_STEPS = [
    "Get access to the department's shared drive and team tools from your manager.",
]


@dataclass
class DecisionResult:
    location_track: str
    location_steps: list[str]
    dept_track: str
    dept_steps: list[str]
    explanation: list[str] = field(default_factory=list)


def _normalize(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def decide_onboarding_track(hire: dict) -> DecisionResult:
    """Branch onboarding steps based on a hire's location and department.

    Unknown departments fall back to a generic step list rather than
    raising, since the rule table only needs to cover the departments this
    demo showcases (engineering, sales) but should degrade gracefully.
    """
    raw_location = hire.get("location", "")
    raw_department = hire.get("department", "")

    location_track = _normalize(raw_location)
    if location_track not in LOCATION_STEPS:
        location_track = "remote" if "remote" in location_track else "in_office"

    dept_track = _normalize(raw_department)
    dept_steps = DEPARTMENT_STEPS.get(dept_track)
    if dept_steps is None:
        dept_steps = DEFAULT_DEPARTMENT_STEPS

    location_steps = LOCATION_STEPS[location_track]

    explanation = [
        f"Location='{raw_location}' matched track '{location_track}' -> "
        f"added {len(location_steps)} IT/equipment step(s).",
        f"Department='{raw_department}' matched track '{dept_track}' -> "
        f"added {len(dept_steps)} tool-access step(s).",
    ]

    return DecisionResult(
        location_track=location_track,
        location_steps=location_steps,
        dept_track=dept_track if dept_track in DEPARTMENT_STEPS else "general",
        dept_steps=dept_steps,
        explanation=explanation,
    )
