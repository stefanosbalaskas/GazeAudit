"""Deterministic study-ingestion preflight example for GazeAudit."""

from __future__ import annotations

import pandas as pd

from gazeaudit import GazeStudy
from gazeaudit.study_qc import audit_study_qc


def build_demo_study() -> GazeStudy:
    """Return a small vendor-neutral table with deliberately flagged conditions."""

    frame = pd.DataFrame(
        {
            "participant_id": ["P01", "P01", "P01", "P02", "P02"],
            "trial_id": ["ad_1", "ad_1", "ad_1", "ad_2", "ad_2"],
            "time_ms": [0.0, 16.7, 16.7, 0.0, 33.4],
            "gaze_x_px": [520.0, 523.0, None, 610.0, 615.0],
            "gaze_y_px": [410.0, 412.0, 414.0, 390.0, 394.0],
        }
    )
    return GazeStudy(
        frame,
        x="gaze_x_px",
        y="gaze_y_px",
        timestamp="time_ms",
        participant="participant_id",
        trial="trial_id",
    )


def run_demo() -> dict[str, object]:
    """Run the structural preflight and return its machine-readable payload."""

    study = build_demo_study()
    report = audit_study_qc(study)
    return report.to_dict()


if __name__ == "__main__":
    summary = run_demo()
    print(f"status: {summary['status']}")
    print(f"issue_codes: {summary['issue_codes']}")
    print(f"coordinate_issue_rows: {summary['coordinate_issue_rows']}")
    print(f"duplicate_timestamp_rows: {summary['duplicate_timestamp_rows']}")
