"""Diagnostics for hard versus uncertainty-aware AOI assignment."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from .aoi import AOI
from .uncertainty import GaussianGazeErrorModel, aoi_probabilities


def hard_aoi_membership(
    points: np.ndarray,
    aois: Sequence[AOI],
    *,
    include_outside: bool = True,
) -> pd.DataFrame:
    """Return deterministic AOI-membership indicators for observed gaze points.

    AOIs may overlap. Consequently the AOI columns are marginal binary
    memberships and do not need to sum to one. ``outside`` indicates that an
    observed point belongs to none of the supplied AOIs.
    """

    arr = _as_points(points)
    _validate_aois(aois)

    output: dict[str, np.ndarray] = {}
    membership: list[np.ndarray] = []
    for aoi in aois:
        values = np.asarray(aoi.contains_points(arr), dtype=bool)
        membership.append(values)
        output[aoi.name] = values

    if include_outside:
        in_any = np.logical_or.reduce(membership)
        output["outside"] = ~in_any

    return pd.DataFrame(output)


def compare_hard_probabilistic(
    points: np.ndarray,
    aois: Sequence[AOI],
    error_model: GaussianGazeErrorModel,
    *,
    draws: int = 2000,
    rng: np.random.Generator | int | None = None,
) -> pd.DataFrame:
    """Compare observed hard AOI labels with uncertainty-aware probabilities.

    The output is long-form with one row per observation and AOI. The
    ``flip_probability`` is the probability that latent true AOI membership
    differs from the deterministic membership assigned to the observed point.
    ``boundary_risk`` rescales binary membership ambiguity to the interval
    ``[0, 1]``: zero means essentially certain in/out membership and one means
    a 50/50 membership probability.
    """

    arr = _as_points(points)
    _validate_aois(aois)
    hard = hard_aoi_membership(arr, aois, include_outside=False)
    probabilities = aoi_probabilities(
        arr,
        aois,
        error_model,
        draws=draws,
        rng=rng,
        include_outside=False,
    )

    rows: list[dict[str, object]] = []
    for observation in range(arr.shape[0]):
        for aoi in aois:
            observed_in = bool(hard.loc[observation, aoi.name])
            probability = float(probabilities.loc[observation, aoi.name])
            flip_probability = 1.0 - probability if observed_in else probability
            boundary_risk = 2.0 * min(probability, 1.0 - probability)
            rows.append(
                {
                    "observation": observation,
                    "aoi": aoi.name,
                    "observed_in_aoi": observed_in,
                    "membership_probability": probability,
                    "flip_probability": flip_probability,
                    "boundary_risk": boundary_risk,
                }
            )

    return pd.DataFrame(rows)


def summarize_aoi_risk(
    comparison: pd.DataFrame,
    *,
    high_risk_threshold: float = 0.25,
) -> pd.DataFrame:
    """Summarize probabilistic AOI-assignment fragility by AOI.

    ``high_risk_threshold`` is applied to the per-observation flip probability.
    It is a descriptive reporting threshold, not a universal exclusion rule.
    """

    required = {"aoi", "flip_probability", "boundary_risk"}
    missing = required.difference(comparison.columns)
    if missing:
        raise ValueError(f"comparison is missing required columns: {sorted(missing)}")
    if not 0.0 <= high_risk_threshold <= 1.0:
        raise ValueError("high_risk_threshold must be between 0 and 1")
    if comparison.empty:
        raise ValueError("comparison must contain at least one row")

    frame = comparison.copy()
    for column in ("flip_probability", "boundary_risk"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any():
            raise ValueError(f"column {column!r} must be numeric and complete")

    grouped = frame.groupby("aoi", sort=False, dropna=False)
    rows: list[dict[str, object]] = []
    for aoi, group in grouped:
        flips = group["flip_probability"].to_numpy(dtype=float)
        risk = group["boundary_risk"].to_numpy(dtype=float)
        rows.append(
            {
                "aoi": aoi,
                "n_observations": int(len(group)),
                "mean_flip_probability": float(np.mean(flips)),
                "max_flip_probability": float(np.max(flips)),
                "mean_boundary_risk": float(np.mean(risk)),
                "high_risk_fraction": float(np.mean(flips >= high_risk_threshold)),
            }
        )

    return pd.DataFrame(rows)


def _validate_aois(aois: Sequence[AOI]) -> None:
    if not aois:
        raise ValueError("at least one AOI is required")
    names = [aoi.name for aoi in aois]
    if len(names) != len(set(names)):
        raise ValueError("AOI names must be unique")


def _as_points(points: np.ndarray) -> np.ndarray:
    arr = np.asarray(points, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError("points must have shape (n, 2)")
    if not np.all(np.isfinite(arr)):
        raise ValueError("points must contain only finite values")
    return arr
