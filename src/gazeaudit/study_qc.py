"""Conservative structural preflight checks for canonical gaze studies."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .study import GazeStudy


@dataclass(frozen=True)
class StudyQCReport:
    """Machine-readable structural QC summary for a :class:`GazeStudy`.

    The report is intentionally descriptive. It flags conditions that deserve
    inspection before downstream analysis but does not impose universal
    exclusion thresholds or infer scientific validity from structural checks.
    """

    n_rows: int
    n_participants: int
    n_trials: int
    missing_x_rows: int
    missing_y_rows: int
    missing_timestamp_rows: int
    infinite_x_rows: int
    infinite_y_rows: int
    infinite_timestamp_rows: int
    missing_identifier_rows: int
    duplicate_timestamp_rows: int
    decreasing_time_groups: int
    coordinate_issue_rows: int
    timestamp_issue_rows: int

    @property
    def has_structural_issues(self) -> bool:
        """Whether at least one structural condition requires review."""

        return any(
            value > 0
            for value in (
                self.coordinate_issue_rows,
                self.timestamp_issue_rows,
                self.missing_identifier_rows,
                self.duplicate_timestamp_rows,
                self.decreasing_time_groups,
            )
        )

    @property
    def status(self) -> str:
        """Return ``"pass"`` when no flagged condition is present, else ``"review"``."""

        return "review" if self.has_structural_issues else "pass"

    @property
    def issue_codes(self) -> tuple[str, ...]:
        """Stable symbolic labels for the flagged structural conditions."""

        issues: list[str] = []
        if self.coordinate_issue_rows:
            issues.append("coordinate_nonfinite")
        if self.timestamp_issue_rows:
            issues.append("timestamp_nonfinite")
        if self.missing_identifier_rows:
            issues.append("identifier_missing")
        if self.duplicate_timestamp_rows:
            issues.append("timestamp_duplicate")
        if self.decreasing_time_groups:
            issues.append("timestamp_decreasing")
        return tuple(issues)

    def to_dict(self) -> dict[str, int | str | bool | tuple[str, ...]]:
        """Return a serialisable-style mapping with derived QC fields included."""

        payload: dict[str, int | str | bool | tuple[str, ...]] = asdict(self)
        payload["status"] = self.status
        payload["has_structural_issues"] = self.has_structural_issues
        payload["issue_codes"] = self.issue_codes
        return payload

    def to_frame(self) -> pd.DataFrame:
        """Return one row per QC metric for compact reporting or export."""

        return pd.DataFrame(
            [
                {"metric": key, "value": value}
                for key, value in self.to_dict().items()
                if key != "issue_codes"
            ]
        )


def _count_decreasing_time_groups(study: GazeStudy) -> int:
    grouped = study.data.groupby(
        [study.participant, study.trial],
        sort=False,
        dropna=False,
    )
    count = 0
    for _, frame in grouped:
        values = frame[study.timestamp].to_numpy(dtype=float)
        finite = values[np.isfinite(values)]
        if finite.size > 1 and np.any(np.diff(finite) < 0):
            count += 1
    return count


def audit_study_qc(study: GazeStudy) -> StudyQCReport:
    """Audit structural properties of a canonical eye-tracking study.

    Checks cover missing and infinite coordinates/timestamps, missing
    participant or trial identifiers, duplicate timestamps within a
    participant-by-trial unit, and decreasing finite timestamps within such
    units. Duplicate timestamps are flagged for review rather than treated as
    automatically invalid because their meaning can depend on acquisition and
    representation choices.
    """

    if not isinstance(study, GazeStudy):
        raise TypeError("study must be a GazeStudy")

    data = study.data
    x = data[study.x]
    y = data[study.y]
    timestamp = data[study.timestamp]

    x_values = x.to_numpy(dtype=float)
    y_values = y.to_numpy(dtype=float)
    timestamp_values = timestamp.to_numpy(dtype=float)

    missing_x = x.isna().to_numpy()
    missing_y = y.isna().to_numpy()
    missing_timestamp = timestamp.isna().to_numpy()

    infinite_x = np.isinf(x_values)
    infinite_y = np.isinf(y_values)
    infinite_timestamp = np.isinf(timestamp_values)

    coordinate_issue = ~np.isfinite(x_values) | ~np.isfinite(y_values)
    timestamp_issue = ~np.isfinite(timestamp_values)
    missing_identifier = data[[study.participant, study.trial]].isna().any(axis=1).to_numpy()

    finite_time = np.isfinite(timestamp_values)
    duplicate_timestamp_rows = int(
        data.loc[finite_time]
        .duplicated(subset=[study.participant, study.trial, study.timestamp], keep=False)
        .sum()
    )

    return StudyQCReport(
        n_rows=int(len(data)),
        n_participants=study.n_participants,
        n_trials=study.n_trials,
        missing_x_rows=int(missing_x.sum()),
        missing_y_rows=int(missing_y.sum()),
        missing_timestamp_rows=int(missing_timestamp.sum()),
        infinite_x_rows=int(infinite_x.sum()),
        infinite_y_rows=int(infinite_y.sum()),
        infinite_timestamp_rows=int(infinite_timestamp.sum()),
        missing_identifier_rows=int(missing_identifier.sum()),
        duplicate_timestamp_rows=duplicate_timestamp_rows,
        decreasing_time_groups=_count_decreasing_time_groups(study),
        coordinate_issue_rows=int(coordinate_issue.sum()),
        timestamp_issue_rows=int(timestamp_issue.sum()),
    )
