"""Canonical study representation for GazeAudit."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class GazeStudy:
    """A validated, tabular representation of an eye-tracking study.

    Parameters
    ----------
    data:
        Long-form gaze or fixation table.
    x, y:
        Column names containing horizontal and vertical gaze coordinates.
    timestamp:
        Column containing monotonically increasing time within each trial.
    participant:
        Participant identifier column.
    trial:
        Trial identifier column.

    Notes
    -----
    GazeAudit deliberately does not impose a vendor-specific schema. The
    canonical object stores the original table and the semantic column mapping
    required by uncertainty and robustness analyses.
    """

    data: pd.DataFrame
    x: str = "x"
    y: str = "y"
    timestamp: str = "timestamp"
    participant: str = "participant"
    trial: str = "trial"

    def __post_init__(self) -> None:
        if not isinstance(self.data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")

        required = [self.x, self.y, self.timestamp, self.participant, self.trial]
        missing = [column for column in required if column not in self.data.columns]
        if missing:
            raise ValueError(f"missing required columns: {missing}")

        for column in (self.x, self.y, self.timestamp):
            if not pd.api.types.is_numeric_dtype(self.data[column]):
                raise TypeError(f"column {column!r} must be numeric")

        if len(self.data) == 0:
            raise ValueError("data must contain at least one observation")

    @property
    def n_participants(self) -> int:
        """Number of unique participants."""

        return int(self.data[self.participant].nunique(dropna=True))

    @property
    def n_trials(self) -> int:
        """Number of unique participant-by-trial units."""

        return int(self.data[[self.participant, self.trial]].drop_duplicates().shape[0])

    def validate_time_order(self) -> None:
        """Raise if timestamps decrease within any participant-by-trial unit."""

        grouped = self.data.groupby([self.participant, self.trial], sort=False, dropna=False)
        bad_groups: list[tuple[object, object]] = []
        for key, frame in grouped:
            values = frame[self.timestamp].to_numpy(dtype=float)
            finite = values[np.isfinite(values)]
            if finite.size > 1 and np.any(np.diff(finite) < 0):
                if isinstance(key, tuple):
                    bad_groups.append(key)
                else:
                    bad_groups.append((key, None))

        if bad_groups:
            preview = bad_groups[:5]
            raise ValueError(
                "timestamps decrease within participant-by-trial units; "
                f"examples: {preview}"
            )

    def copy_with(self, data: pd.DataFrame) -> GazeStudy:
        """Return a new study with the same semantic column mapping."""

        return GazeStudy(
            data=data.copy(),
            x=self.x,
            y=self.y,
            timestamp=self.timestamp,
            participant=self.participant,
            trial=self.trial,
        )

    def require_columns(self, columns: Iterable[str]) -> None:
        """Raise if one or more additional columns are absent."""

        missing = [column for column in columns if column not in self.data.columns]
        if missing:
            raise ValueError(f"missing required columns: {missing}")
