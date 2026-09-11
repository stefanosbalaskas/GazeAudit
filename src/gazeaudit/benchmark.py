"""Known-truth benchmark utilities for uncertainty-aware AOI analysis."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from .aoi import AOI
from .aoi_audit import hard_aoi_membership
from .uncertainty import GaussianGazeErrorModel, aoi_probabilities


def simulate_boundary_data(
    *,
    n: int = 1000,
    boundary_x: float = 0.0,
    true_x_sd: float = 8.0,
    y_sd: float = 8.0,
    measurement_sd: float = 6.0,
    bias_x: float = 0.0,
    bias_y: float = 0.0,
    rng: np.random.Generator | int | None = None,
) -> pd.DataFrame:
    """Simulate latent and observed gaze around a vertical AOI boundary.

    The latent coordinates are scientific ground truth. Observed coordinates
    add independent Gaussian measurement error with optional systematic bias.
    This intentionally simple generator is for method validation rather than a
    claim that real eye-tracker errors are globally isotropic or Gaussian.
    """

    if n < 2:
        raise ValueError("n must be at least 2")
    for name, value in {
        "true_x_sd": true_x_sd,
        "y_sd": y_sd,
        "measurement_sd": measurement_sd,
    }.items():
        if value < 0:
            raise ValueError(f"{name} must be non-negative")

    generator = _as_rng(rng)
    true_x = generator.normal(boundary_x, true_x_sd, size=n)
    true_y = generator.normal(0.0, y_sd, size=n)
    error_x = generator.normal(bias_x, measurement_sd, size=n)
    error_y = generator.normal(bias_y, measurement_sd, size=n)

    return pd.DataFrame(
        {
            "true_x": true_x,
            "true_y": true_y,
            "observed_x": true_x + error_x,
            "observed_y": true_y + error_y,
        }
    )


def evaluate_aoi_recovery(
    truth_points: np.ndarray,
    observed_points: np.ndarray,
    aois: Sequence[AOI],
    error_model: GaussianGazeErrorModel,
    *,
    draws: int = 2000,
    rng: np.random.Generator | int | None = None,
) -> pd.DataFrame:
    """Compare deterministic and probabilistic AOI recovery against truth.

    For each AOI, deterministic recovery is evaluated as a binary 0/1
    prediction from observed coordinates. Probabilistic recovery uses the
    uncertainty-aware AOI probability. The Brier score is the mean squared
    error of the prediction against known latent AOI membership; lower is
    better. Accuracy uses a 0.5 threshold for the probabilistic prediction.
    """

    truth = _as_points(truth_points, name="truth_points")
    observed = _as_points(observed_points, name="observed_points")
    if truth.shape != observed.shape:
        raise ValueError("truth_points and observed_points must have the same shape")
    if not aois:
        raise ValueError("at least one AOI is required")

    true_membership = hard_aoi_membership(truth, aois, include_outside=False)
    hard_observed = hard_aoi_membership(observed, aois, include_outside=False)
    probabilities = aoi_probabilities(
        observed,
        aois,
        error_model,
        draws=draws,
        rng=rng,
        include_outside=False,
    )

    rows: list[dict[str, object]] = []
    for aoi in aois:
        truth_binary = true_membership[aoi.name].to_numpy(dtype=float)
        hard_binary = hard_observed[aoi.name].to_numpy(dtype=float)
        probability = probabilities[aoi.name].to_numpy(dtype=float)
        probabilistic_binary = (probability >= 0.5).astype(float)

        rows.append(
            {
                "aoi": aoi.name,
                "n_observations": int(truth.shape[0]),
                "hard_accuracy": float(np.mean(hard_binary == truth_binary)),
                "probabilistic_accuracy": float(
                    np.mean(probabilistic_binary == truth_binary)
                ),
                "hard_brier": float(np.mean((hard_binary - truth_binary) ** 2)),
                "probabilistic_brier": float(
                    np.mean((probability - truth_binary) ** 2)
                ),
            }
        )

    return pd.DataFrame(rows)


def fit_error_model_from_known_truth(
    data: pd.DataFrame,
    *,
    observed_x: str = "observed_x",
    observed_y: str = "observed_y",
    true_x: str = "true_x",
    true_y: str = "true_y",
) -> GaussianGazeErrorModel:
    """Fit the MVP error model from simulated or known-target truth data."""

    renamed = data.rename(
        columns={
            observed_x: "observed_x",
            observed_y: "observed_y",
            true_x: "target_x",
            true_y: "target_y",
        }
    )
    return GaussianGazeErrorModel.fit(renamed)


def _as_points(points: np.ndarray, *, name: str) -> np.ndarray:
    arr = np.asarray(points, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError(f"{name} must have shape (n, 2)")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must contain only finite values")
    return arr


def _as_rng(rng: np.random.Generator | int | None) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)
