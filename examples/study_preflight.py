"""Deterministic study-ingestion preflight and provenance example for GazeAudit."""

from __future__ import annotations

import pandas as pd

from gazeaudit import (
    GazeStudy,
    StudyQCAudit,
    StudyQCDecision,
    build_study_qc_audit,
)


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


def build_demo_audit() -> StudyQCAudit:
    """Build a structural QC record with explicit decisions for the flagged issues."""

    study = build_demo_study()
    decisions = (
        StudyQCDecision(
            issue_code="coordinate_nonfinite",
            action="retain for explicit downstream missingness handling",
            rationale=(
                "The missing coordinate is retained so its handling remains visible "
                "to the downstream sensitivity analysis."
            ),
            diagnostic_ids=("D000002",),
        ),
        StudyQCDecision(
            issue_code="timestamp_duplicate",
            action="retain after representation review",
            rationale=(
                "The repeated timestamp is documented rather than silently deduplicated "
                "in this synthetic example."
            ),
            diagnostic_ids=("D000001", "D000003"),
        ),
    )
    return build_study_qc_audit(study, decisions=decisions)


def run_demo() -> dict[str, object]:
    """Run the full preflight and return a compact machine-readable summary."""

    audit = build_demo_audit()
    summary = audit.report.to_dict()
    summary["study_fingerprint"] = audit.study_fingerprint
    summary["audit_fingerprint"] = audit.audit_fingerprint
    summary["n_diagnostics"] = len(audit.diagnostics)
    summary["n_decisions"] = len(audit.decisions)
    return summary


if __name__ == "__main__":
    summary = run_demo()
    print(f"status: {summary['status']}")
    print(f"issue_codes: {summary['issue_codes']}")
    print(f"coordinate_issue_rows: {summary['coordinate_issue_rows']}")
    print(f"duplicate_timestamp_rows: {summary['duplicate_timestamp_rows']}")
    print(f"diagnostics: {summary['n_diagnostics']}")
    print(f"decisions: {summary['n_decisions']}")
    print(f"study_fingerprint: {summary['study_fingerprint']}")
    print(f"audit_fingerprint: {summary['audit_fingerprint']}")
