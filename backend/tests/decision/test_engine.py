import pytest

from decision.engine import decide_onboarding_track


@pytest.mark.parametrize(
    "location, department, expected_location_track, expected_dept_track",
    [
        ("remote", "Engineering", "remote", "engineering"),
        ("in_office", "Sales", "in_office", "sales"),
        ("Remote", "engineering", "remote", "engineering"),
        ("In-Office", "sales", "in_office", "sales"),
    ],
)
def test_decide_onboarding_track_matches_expected_tracks(
    location, department, expected_location_track, expected_dept_track
):
    hire = {
        "name": "Test Hire",
        "role": "Some Role",
        "department": department,
        "location": location,
        "start_date": "2026-01-01",
    }

    result = decide_onboarding_track(hire)

    assert result.location_track == expected_location_track
    assert result.dept_track == expected_dept_track


def test_remote_and_in_office_get_different_location_steps(remote_engineer_hire, inoffice_sales_hire):
    remote_decision = decide_onboarding_track(remote_engineer_hire)
    office_decision = decide_onboarding_track(inoffice_sales_hire)

    assert remote_decision.location_steps != office_decision.location_steps
    assert any("VPN" in step for step in remote_decision.location_steps)
    assert any("badge" in step.lower() for step in office_decision.location_steps)


def test_engineering_and_sales_get_different_dept_steps(remote_engineer_hire, inoffice_sales_hire):
    eng_decision = decide_onboarding_track(remote_engineer_hire)
    sales_decision = decide_onboarding_track(inoffice_sales_hire)

    assert eng_decision.dept_steps != sales_decision.dept_steps
    assert any("GitHub" in step for step in eng_decision.dept_steps)
    assert any("CRM" in step for step in sales_decision.dept_steps)


def test_unknown_department_falls_back_to_default_steps():
    hire = {
        "name": "Test Hire",
        "role": "Some Role",
        "department": "Legal",
        "location": "remote",
        "start_date": "2026-01-01",
    }

    result = decide_onboarding_track(hire)

    assert result.dept_track == "general"
    assert len(result.dept_steps) > 0


def test_explanation_names_both_tracks(remote_engineer_hire):
    result = decide_onboarding_track(remote_engineer_hire)

    joined = " ".join(result.explanation)
    assert "remote" in joined
    assert "engineering" in joined
