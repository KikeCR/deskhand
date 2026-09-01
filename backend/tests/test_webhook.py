import pytest

from webhook import (
    HRISEmployee,
    HRISWebhookPayload,
    WebhookAuthError,
    normalize_hris_payload,
    normalize_location,
    verify_webhook_secret,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Remote", "remote"),
        ("work from home", "remote"),
        ("WFH", "remote"),
        ("Home Office", "remote"),
        ("Office", "in_office"),
        ("On-Site", "in_office"),
        ("HQ", "in_office"),
        ("Fully Remote", "remote"),
        ("Downtown Office", "in_office"),
    ],
)
def test_normalize_location(raw, expected):
    assert normalize_location(raw) == expected


def test_normalize_hris_payload_maps_external_shape_to_internal_hire_dict():
    payload = HRISWebhookPayload(
        employee=HRISEmployee(
            full_name="Jordan Reyes",
            job_title="Support Engineer",
            team="Engineering",
            work_location="Work From Home",
            hire_date="2026-10-01",
        )
    )

    hire = normalize_hris_payload(payload)

    assert hire == {
        "name": "Jordan Reyes",
        "role": "Support Engineer",
        "department": "Engineering",
        "location": "remote",
        "start_date": "2026-10-01",
    }


def test_verify_webhook_secret_allows_any_request_when_unset(monkeypatch):
    monkeypatch.delenv("WEBHOOK_SECRET", raising=False)

    verify_webhook_secret(None)  # should not raise
    verify_webhook_secret("anything")  # should not raise


def test_verify_webhook_secret_rejects_missing_or_wrong_secret(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET", "expected-secret")

    with pytest.raises(WebhookAuthError):
        verify_webhook_secret(None)
    with pytest.raises(WebhookAuthError):
        verify_webhook_secret("wrong-secret")


def test_verify_webhook_secret_accepts_matching_secret(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET", "expected-secret")

    verify_webhook_secret("expected-secret")  # should not raise
