"""HRIS webhook adapter: normalizes an external system's payload shape into
the internal hire dict pipeline.run_onboarding() expects.

This is the concrete version of "decoupled from the trigger": a real HRIS
or an n8n workflow will never send exactly the shape our pipeline uses
internally, so the trigger's job is to adapt its payload and call the same
run_onboarding() the CLI and the UI already call, not to duplicate pipeline
logic.
"""

from __future__ import annotations

import os

from pydantic import BaseModel

LOCATION_ALIASES = {
    "remote": "remote",
    "work from home": "remote",
    "wfh": "remote",
    "home office": "remote",
    "office": "in_office",
    "on-site": "in_office",
    "onsite": "in_office",
    "in-office": "in_office",
    "in office": "in_office",
    "hq": "in_office",
}


class WebhookAuthError(Exception):
    pass


class HRISEmployee(BaseModel):
    full_name: str
    job_title: str
    team: str
    work_location: str
    hire_date: str


class HRISWebhookPayload(BaseModel):
    """Shape of a mock external HRIS "employee hired" webhook event.

    Deliberately different field names/nesting than our internal hire
    dict (full_name vs. name, team vs. department, ...), since that
    mismatch is the realistic case a trigger adapter has to handle.
    """

    event: str = "employee.hired"
    employee: HRISEmployee


def normalize_location(raw: str) -> str:
    key = raw.strip().lower()
    if key in LOCATION_ALIASES:
        return LOCATION_ALIASES[key]
    return "remote" if "remote" in key or "home" in key else "in_office"


def normalize_hris_payload(payload: HRISWebhookPayload) -> dict:
    employee = payload.employee
    return {
        "name": employee.full_name,
        "role": employee.job_title,
        "department": employee.team,
        "location": normalize_location(employee.work_location),
        "start_date": employee.hire_date,
    }


def verify_webhook_secret(provided: str | None) -> None:
    """Check the shared-secret header, if WEBHOOK_SECRET is configured.

    With no WEBHOOK_SECRET set, the endpoint stays open, which keeps local
    development and the sample n8n workflow simple. Setting WEBHOOK_SECRET
    (e.g. in a real deployment) requires every request to send a matching
    X-Webhook-Secret header.
    """
    expected = os.environ.get("WEBHOOK_SECRET")
    if not expected:
        return
    if provided != expected:
        raise WebhookAuthError("Invalid or missing X-Webhook-Secret header.")
