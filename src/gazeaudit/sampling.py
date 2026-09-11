"""Sampling-rate perturbation utilities for robustness analysis."""

from __future__ import annotations

from collections.abc import Callable, Iterable

import numpy as np
import pandas as pd

from .study import GazeStudy


def downsample_gaze(
    study: GazeStudy,
    target_hz: float,
    *,
    timestamp_unit: str = "ms",
) -> GazeStudy:
    """Downsample each participant-by-trial stream to a target sampling rate.

    Existing samples nearest to an ideal regular target grid are retained; no
    gaze coordinates are interpolated. This is a controlled perturbation for
    robustness analysis, not a reconstruction of how a different physical eye
    tracker would have measured the same trial.
    """

    if not np.isfinite(target_hz) or target_hz <= 0:
        raise ValueError("target_hz must be finite and positive")
    if timestamp_unit == "ms":
        interval = 1000.0 / target_hz
    elif timestamp_unit == "s":
        interval = 1.0 / target_hz
    else:
        raise ValueError("timestamp_unit must be 'ms' or 's'")

    study.validate_time_order()
    timestamps = pd.to_numeric(study.data[study.timestamp], errors="coerce").to_numpy(float)
    if np.any(~np.isfinite(timestamps)):
        raise ValueError("timestamps must be finite for downsampling")

    kept_frames: list[pd.DataFrame] = []
    grouped = study.data.groupby(
        [study.participant, study.trial], sort=False, dropna=False
    )
    for _, frame in grouped:
        times = frame[study.timestamp].to_numpy(dtype=float)
        if len(frame) <= 1:
            kept_frames.append(frame.copy())
            continue

        start = float(times[0])
        stop = float(times[-1])
        grid = np.arange(start, stop + interval * 0.5, interval)
        positions = _nearest_unique_positions(times, grid)
        kept_frames.append(frame.iloc[positions].copy())

    output = pd.concat(kept_frames, axis=0).sort_index(kind="mergesort")
    return study.copy_with(output.reset_index(drop=True))


def sampling_sensitivity_curve(
    study: GazeStudy,
    target_rates: Iterable[float],
    endpoint: Callable[[GazeStudy], float],
    *,
    timestamp_unit: str = "ms",
) -> pd.DataFrame:
    """Evaluate one scientific endpoint across controlled sampling rates."""

    rates = tuple(float(rate) for rate in target_rates)
    if not rates:
        raise ValueError("target_rates must contain at least one value")

    rows: list[dict[str, float | int]] = []
    original_n = len(study.data)
    for rate in rates:
        perturbed = downsample_gaze(study, rate, timestamp_unit=timestamp_unit)
        estimate = float(endpoint(perturbed))
        if not np.isfinite(estimate):
            raise ValueError("endpoint must return a finite scalar")
        rows.append(
            {
                "target_hz": rate,
                "n_rows": int(len(perturbed.data)),
                "retained_fraction": float(len(perturbed.data) / original_n),
                "estimate": estimate,
            }
        )

    return pd.DataFrame(rows)


def _nearest_unique_positions(times: np.ndarray, grid: np.ndarray) -> np.ndarray:
    insertion = np.searchsorted(times, grid, side="left")
    right = np.clip(insertion, 0, len(times) - 1)
    left = np.clip(insertion - 1, 0, len(times) - 1)
    left_distance = np.abs(times[left] - grid)
    right_distance = np.abs(times[right] - grid)
    chosen = np.where(right_distance < left_distance, right, left)
    return np.unique(chosen)
