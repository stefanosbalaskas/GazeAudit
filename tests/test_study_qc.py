from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from gazeaudit import GazeStudy
from gazeaudit.study_qc import StudyQCReport, audit_study_qc


def _study(frame: pd.DataFrame) -> GazeStudy:
    return GazeStudy(frame, x="gx", y="gy", timestamp="time", participant="pid", trial="trial")


def test_clean_study_passes_preflight() -> None:
    study = _study(
        pd.DataFrame(
            {
                "pid": ["p1", "p1", "p2", "p2"],
                "trial": ["a", "a", "b", "b"],
                "time": [0.0, 1.0, 0.0, 1.0],
                "gx": [100.0, 101.0, 200.0, 201.0],
                "gy": [50.0, 51.0, 60.0, 61.0],
            }
        )
    )

    report = audit_study_qc(study)

    assert isinstance(report, StudyQCReport)
    assert report.status == "pass"
    assert not report.has_structural_issues
    assert report.issue_codes == ()
    assert report.n_rows == 4
    assert report.n_participants == 2
    assert report.n_trials == 2
    assert report.coordinate_issue_rows == 0
    assert report.timestamp_issue_rows == 0
    assert report.duplicate_timestamp_rows == 0
    assert report.decreasing_time_groups == 0


def test_preflight_counts_coordinate_and_time_conditions() -> None:
    study = _study(
        pd.DataFrame(
            {
                "pid": ["p1", "p1", "p1", "p2", "p2", "p2"],
                "trial": ["a", "a", "a", "b", "b", "b"],
                "time": [0.0, 1.0, 1.0, 0.0, 2.0, 1.0],
                "gx": [100.0, np.nan, np.inf, 200.0, 201.0, 202.0],
                "gy": [50.0, 51.0, 52.0, 60.0, np.nan, 62.0],
            }
        )
    )

    report = audit_study_qc(study)

    assert report.status == "review"
    assert report.missing_x_rows == 1
    assert report.missing_y_rows == 1
    assert report.infinite_x_rows == 1
    assert report.infinite_y_rows == 0
    assert report.coordinate_issue_rows == 3
    assert report.duplicate_timestamp_rows == 2
    assert report.decreasing_time_groups == 1
    assert report.issue_codes == (
        "coordinate_nonfinite",
        "timestamp_duplicate",
        "timestamp_decreasing",
    )


def test_preflight_distinguishes_missing_and_infinite_timestamps() -> None:
    study = _study(
        pd.DataFrame(
            {
                "pid": ["p1", "p1", "p1"],
                "trial": ["a", "a", "a"],
                "time": [0.0, np.nan, np.inf],
                "gx": [100.0, 101.0, 102.0],
                "gy": [50.0, 51.0, 52.0],
            }
        )
    )

    report = audit_study_qc(study)

    assert report.missing_timestamp_rows == 1
    assert report.infinite_timestamp_rows == 1
    assert report.timestamp_issue_rows == 2
    assert report.issue_codes == ("timestamp_nonfinite",)


def test_preflight_flags_missing_identifiers_without_imposing_exclusion() -> None:
    study = _study(
        pd.DataFrame(
            {
                "pid": ["p1", None, "p2"],
                "trial": ["a", "a", None],
                "time": [0.0, 1.0, 2.0],
                "gx": [100.0, 101.0, 102.0],
                "gy": [50.0, 51.0, 52.0],
            }
        )
    )

    report = audit_study_qc(study)

    assert report.missing_identifier_rows == 2
    assert report.issue_codes == ("identifier_missing",)
    assert report.status == "review"


def test_preflight_supports_nullable_numeric_dtypes() -> None:
    frame = pd.DataFrame(
        {
            "pid": ["p1", "p1", "p1"],
            "trial": ["a", "a", "a"],
            "time": pd.Series([0.0, 1.0, pd.NA], dtype="Float64"),
            "gx": pd.Series([100.0, pd.NA, 102.0], dtype="Float64"),
            "gy": pd.Series([50.0, 51.0, 52.0], dtype="Float64"),
        }
    )

    report = audit_study_qc(_study(frame))

    assert report.missing_x_rows == 1
    assert report.missing_timestamp_rows == 1
    assert report.coordinate_issue_rows == 1
    assert report.timestamp_issue_rows == 1


def test_report_exports_derived_fields() -> None:
    report = StudyQCReport(
        n_rows=2,
        n_participants=1,
        n_trials=1,
        missing_x_rows=0,
        missing_y_rows=0,
        missing_timestamp_rows=0,
        infinite_x_rows=0,
        infinite_y_rows=0,
        infinite_timestamp_rows=0,
        missing_identifier_rows=0,
        duplicate_timestamp_rows=2,
        decreasing_time_groups=0,
        coordinate_issue_rows=0,
        timestamp_issue_rows=0,
    )

    payload = report.to_dict()
    table = report.to_frame()

    assert payload["status"] == "review"
    assert payload["has_structural_issues"] is True
    assert payload["issue_codes"] == ("timestamp_duplicate",)
    assert set(table.columns) == {"metric", "value"}
    assert "issue_codes" not in set(table["metric"])
    assert "status" in set(table["metric"])


def test_preflight_rejects_noncanonical_input() -> None:
    with pytest.raises(TypeError, match="study must be a GazeStudy"):
        audit_study_qc(pd.DataFrame({"x": [1.0]}))  # type: ignore[arg-type]
