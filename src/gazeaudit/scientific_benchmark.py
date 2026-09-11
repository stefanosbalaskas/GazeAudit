"""Known-effect scientific benchmarks for GazeAudit."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .aoi import AOI
from .uncertainty import GaussianGazeErrorModel, aoi_probabilities


def simulate_known_aoi_effect(
    *,
    n_participants: int = 60,
    trials_per_condition: int = 30,
    control_probability: float = 0.40,
    treatment_probability: float = 0.60,
    left_center: float = -20.0,
    right_center: float = 20.0,
    center_sd: float = 5.0,
    measurement_sd: float = 8.0,
    duration_mean: float = 220.0,
    duration_sd: float = 40.0,
    rng: np.random.Generator | int | None = None,
) -> pd.DataFrame:
    """Simulate a repeated-measures study with a known AOI-attention effect.

    Each participant contributes equal numbers of control and treatment trials.
    Treatment changes the probability that latent gaze is generated from the
    right-side region. Observed gaze then adds isotropic Gaussian measurement
    error. The resulting latent coordinates remain the benchmark ground truth.
    """

    if n_participants < 2:
        raise ValueError("n_participants must be at least 2")
    if trials_per_condition < 1:
        raise ValueError("trials_per_condition must be at least 1")
    for name, value in {
        "control_probability": control_probability,
        "treatment_probability": treatment_probability,
    }.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be between 0 and 1")
    for name, value in {
        "center_sd": center_sd,
        "measurement_sd": measurement_sd,
        "duration_sd": duration_sd,
    }.items():
        if value < 0:
            raise ValueError(f"{name} must be non-negative")
    if duration_mean < 0:
        raise ValueError("duration_mean must be non-negative")

    generator = _as_rng(rng)
    rows: list[dict[str, object]] = []
    for participant in range(n_participants):
        trial = 0
        for condition, probability in (
            ("control", control_probability),
            ("treatment", treatment_probability),
        ):
            for _ in range(trials_per_condition):
                target_right = bool(generator.random() < probability)
                center = right_center if target_right else left_center
                true_x = float(generator.normal(center, center_sd))
                true_y = float(generator.normal(0.0, center_sd))
                observed_x = float(generator.normal(true_x, measurement_sd))
                observed_y = float(generator.normal(true_y, measurement_sd))
                duration = max(0.0, float(generator.normal(duration_mean, duration_sd)))
                rows.append(
                    {
                        "participant": f"p{participant + 1}",
                        "condition": condition,
                        "trial": trial,
                        "timestamp": 0.0,
                        "duration": duration,
                        "true_x": true_x,
                        "true_y": true_y,
                        "observed_x": observed_x,
                        "observed_y": observed_y,
                    }
                )
                trial += 1

    return pd.DataFrame(rows)


def condition_dwell_effect(
    data: pd.DataFrame,
    membership: np.ndarray,
    *,
    duration_col: str = "duration",
    participant_col: str = "participant",
    condition_col: str = "condition",
    control: str = "control",
    treatment: str = "treatment",
) -> float:
    """Estimate the mean within-participant treatment-minus-control dwell effect."""

    required = {duration_col, participant_col, condition_col}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"data is missing required columns: {sorted(missing)}")

    weights = np.asarray(membership, dtype=float)
    if weights.ndim != 1 or weights.size != len(data):
        raise ValueError("membership must be one-dimensional and match data rows")
    if np.any(~np.isfinite(weights)) or np.any((weights < 0) | (weights > 1)):
        raise ValueError("membership must contain finite values between 0 and 1")

    durations = pd.to_numeric(data[duration_col], errors="coerce").to_numpy(dtype=float)
    if np.any(~np.isfinite(durations)) or np.any(durations < 0):
        raise ValueError("durations must be finite and non-negative")

    frame = data[[participant_col, condition_col]].copy()
    frame["weighted_dwell"] = durations * weights
    totals = frame.groupby([participant_col, condition_col], sort=False)["weighted_dwell"].sum()
    wide = totals.unstack(condition_col)
    if control not in wide.columns or treatment not in wide.columns:
        raise ValueError("both control and treatment conditions must be present")
    complete = wide[[control, treatment]].dropna()
    if complete.empty:
        raise ValueError("no participant has both control and treatment data")
    return float((complete[treatment] - complete[control]).mean())


def benchmark_known_aoi_effect(
    data: pd.DataFrame,
    aoi: AOI,
    error_model: GaussianGazeErrorModel,
    *,
    draws: int = 2000,
    rng: np.random.Generator | int | None = None,
) -> pd.Series:
    """Compare true, hard-observed, and uncertainty-aware scientific effects."""

    required = {"true_x", "true_y", "observed_x", "observed_y"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"data is missing required columns: {sorted(missing)}")

    truth = data[["true_x", "true_y"]].to_numpy(dtype=float)
    observed = data[["observed_x", "observed_y"]].to_numpy(dtype=float)
    if np.any(~np.isfinite(truth)) or np.any(~np.isfinite(observed)):
        raise ValueError("truth and observed coordinates must be finite")

    true_membership = np.asarray(aoi.contains_points(truth), dtype=float)
    hard_membership = np.asarray(aoi.contains_points(observed), dtype=float)
    probabilities = aoi_probabilities(
        observed,
        [aoi],
        error_model,
        draws=draws,
        rng=rng,
        include_outside=False,
    )[aoi.name].to_numpy(dtype=float)

    true_effect = condition_dwell_effect(data, true_membership)
    hard_effect = condition_dwell_effect(data, hard_membership)
    probabilistic_effect = condition_dwell_effect(data, probabilities)

    return pd.Series(
        {
            "true_effect": true_effect,
            "hard_effect": hard_effect,
            "probabilistic_effect": probabilistic_effect,
            "hard_absolute_error": abs(hard_effect - true_effect),
            "probabilistic_absolute_error": abs(probabilistic_effect - true_effect),
            "hard_sign_recovered": bool(np.sign(hard_effect) == np.sign(true_effect)),
            "probabilistic_sign_recovered": bool(
                np.sign(probabilistic_effect) == np.sign(true_effect)
            ),
        }
    )


def _as_rng(rng: np.random.Generator | int | None) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)
