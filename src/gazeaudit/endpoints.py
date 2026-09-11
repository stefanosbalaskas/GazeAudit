"""Uncertainty-aware eye-tracking endpoints."""

from __future__ import annotations

import numpy as np
import pandas as pd


def expected_dwell(
    probabilities: pd.DataFrame,
    durations: np.ndarray | pd.Series,
    aoi: str,
) -> float:
    """Return expected dwell time for an AOI.

    Each fixation/event duration is weighted by its probability of belonging to
    the requested AOI. Durations may be expressed in any consistent time unit.
    """

    if aoi not in probabilities.columns:
        raise ValueError(f"AOI {aoi!r} is not present in probabilities")
    duration_array = np.asarray(durations, dtype=float)
    if duration_array.ndim != 1 or len(duration_array) != len(probabilities):
        raise ValueError("durations must be one-dimensional and match probabilities")
    if np.any(~np.isfinite(duration_array)) or np.any(duration_array < 0):
        raise ValueError("durations must be finite and non-negative")

    weights = probabilities[aoi].to_numpy(dtype=float)
    _validate_probabilities(weights)
    return float(np.sum(weights * duration_array))


def expected_fixation_count(probabilities: pd.DataFrame, aoi: str) -> float:
    """Return expected fixation/event count for an AOI."""

    if aoi not in probabilities.columns:
        raise ValueError(f"AOI {aoi!r} is not present in probabilities")
    weights = probabilities[aoi].to_numpy(dtype=float)
    _validate_probabilities(weights)
    return float(np.sum(weights))


def _validate_probabilities(values: np.ndarray) -> None:
    if np.any(~np.isfinite(values)):
        raise ValueError("probabilities must be finite")
    if np.any((values < 0) | (values > 1)):
        raise ValueError("probabilities must lie in [0, 1]")
