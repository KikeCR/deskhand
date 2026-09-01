"""CLI entry point: run the onboarding pipeline for one hire.

Usage:
    python run.py --hire-file data/sample_hires/remote_engineer.json
    python run.py --name "Jane Doe" --role "Support Engineer" \\
        --department Engineering --location remote --start-date 2026-10-01
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline import run_onboarding


def _load_hire(args: argparse.Namespace) -> dict:
    if args.hire_file:
        return json.loads(Path(args.hire_file).read_text())
    return {
        "name": args.name,
        "role": args.role,
        "department": args.department,
        "location": args.location,
        "start_date": args.start_date,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the DeskHand onboarding pipeline for one new hire."
    )
    parser.add_argument("--hire-file", help="Path to a JSON file with the hire's profile")
    parser.add_argument("--name")
    parser.add_argument("--role")
    parser.add_argument("--department")
    parser.add_argument("--location", choices=["remote", "in_office"])
    parser.add_argument("--start-date")
    args = parser.parse_args()

    if not args.hire_file and not args.name:
        parser.error(
            "Provide either --hire-file or all of "
            "--name/--role/--department/--location/--start-date"
        )

    hire = _load_hire(args)
    result = run_onboarding(hire)

    print(f"\nOnboarding checklist written to: {result.output_path}\n")
    print(result.checklist_markdown)


if __name__ == "__main__":
    main()
