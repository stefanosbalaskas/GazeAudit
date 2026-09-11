"""Sensitivity analyses for gaze-position measurement uncertainty."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np
import pandas as pd

from .aoi import AOI
from .aoi_audit import compare_hard_probabilistic
from .endpoints import expected_dwell, expected_fixation_count
from .uncertainty import GaussianGazeErrorModel, aoi_probabilities


def scale_error_model(
    model: GaussianGazeErrorModel,
    *,
    sd_scale: float = 1.0,
    bias_scale: float = 1.0,
) -> GaussianGazeErrorModel:
    """Return a copy of a gaze-error model with controlled error scaling.

    ``sd_scale`` multiplies standard deviations, so the covariance matrix is
    multiplied by ``sd_scale**2``. ``bias_scale`` multiplies the systematic
    mean error. Values are explicit perturbations for sensitivity analysis,
    not estimates of a new physical tracker.
    """

    if sd_scale < 0:
        raise ValueError("sd_scale must be non-negative")
    if bias_scale < 0:
        raise ValueError("bias_scale must be non-negative")
    return GaussianGazeErrorModel(
        mean_error=np.asarray(model.mean_error, dtype=float) * bias_scale,
        covariance=np.asarray(model.covariance, dtype=float) * sd_scale**2,
        n_validation=model.n_validation,
    )


def spatial_sensitivity_curve(
    points: np.ndarray,
    aois: Sequence[AOI],
    error_model: GaussianGazeErrorModel,
    sd_scales: Iterable[float],
    *,
    durations: np.ndarray | None = None,
    draws: int = 2000,
    rng: np.random.Generator | int | None = None,
) -> pd.DataFrame:
    """Quantify AOI results as spatial precision is perturbed.

    Returns one row per ``sd_scale × AOI`` combination. For each row the
    function reports expected membership count, mean hard-to-probabilistic flip
    probability, mean boundary risk, and optionally expected dwell time.
    Child random seeds are generated deterministically from ``rng`` so repeated
    calls with the same seed are reproducible while scales receive independent
    Monte Carlo draws.
    """

    scales = tuple(float(value) for value in sd_scales)
    if not scales:
        raise ValueError("sd_scales must contain at least one value")
    if any(value < 0 for value in scales):
        raise ValueError("sd_scales must be non-negative")

    arr = _as_points(points)
    if durations is not None:
        duration_array = np.asarray(durations, dtype=float)
        if duration_array.ndim != 1 or duration_array.size != arr.shape[0]:
            raise ValueError("durations must be one-dimensional and match points")
        if np.any(~np.isfinite(duration_array)) or np.any(duration_array < 0):
            raise ValueError("durations must be finite and non-negative")
    else:
        duration_array = None

    generator = _as_rng(rng)
    rows: list[dict[str, object]] = []
    for scale in scales:
        model = scale_error_model(error_model, sd_scale=scale)
        child_seed = int(generator.integers(0, np.iinfo(np.uint32).max, dtype=np.uint32))
        probabilities = aoi_probabilities(
            arr,
            aois,
            model,
            draws=draws,
            rng=child_seed,
            include_outside=False,
        )
        comparison = compare_hard_probabilistic(
            arr,
            aois,
            model,
            draws=draws,
            rng=child_seed,
        )

        for aoi in aois:
            risk = comparison.loc[comparison["aoi"] == aoi.name]
            row: dict[str, object] = {
                "sd_scale": scale,
                "aoi": aoi.name,
                "expected_fixation_count": expected_fixation_count(probabilities, aoi.name),
                "mean_flip_probability": float(risk["flip_probability"].mean()),
                "mean_boundary_risk": float(risk["boundary_risk"].mean()),
            }
            if duration_array is not None:
                row["expected_dwell"] = expected_dwell(
                    probabilities,
                    duration_array,
                    aoi.name,
                )
            rows.append(row)

    return pd.DataFrame(rows)


def _as_points(points: np.ndarray) -> np.ndarray:
    arr = np.asarray(points, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError("points must have shape (n, 2)")
    if not np.all(np.isfinite(arr)):
        raise ValueError("points must contain only finite values")
    return arr


def _as_rng(rng: np.random.Generator | int | None) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)
