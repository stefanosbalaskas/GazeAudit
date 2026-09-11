"""Propagate spatial gaze uncertainty into scientific AOI effect estimates.

This module moves GazeAudit beyond marginal AOI-membership probabilities.  It
samples complete latent gaze realizations from a declared spatial-error model,
recomputes AOI membership for every realization, and passes those memberships
to a user-supplied scientific endpoint.  The resulting distribution therefore
quantifies *measurement-model uncertainty in the endpoint* conditional on the
observed data and supplied error model.

The distribution is deliberately not labelled a confidence or credible
interval for the population effect: it does not, by itself, include participant
sampling uncertainty, model uncertainty in the endpoint, or uncertainty about
the fitted gaze-error model.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .aoi import AOI
from .uncertainty import GaussianGazeErrorModel

AOIEffectEndpoint = Callable[[pd.DataFrame, np.ndarray], float]


@dataclass(frozen=True)
class AOIEffectUncertaintyAudit:
    """Measurement-uncertainty audit for one AOI-dependent scientific endpoint.

    Attributes
    ----------
    aoi:
        Name of the audited AOI.
    draw_effects:
        One endpoint estimate for each sampled latent gaze realization.
    membership_probabilities:
        Monte Carlo marginal membership probability for every observation,
        estimated from the same latent realizations used for ``draw_effects``.
    summary:
        Compact measurement-uncertainty summary including the deterministic
        hard-assignment effect, the endpoint evaluated on marginal membership
        probabilities, the Monte Carlo effect distribution, and probabilities
        relative to the requested reference value.
    """

    aoi: str
    draw_effects: pd.DataFrame
    membership_probabilities: pd.DataFrame
    summary: pd.Series


def audit_aoi_effect_uncertainty(
    data: pd.DataFrame,
    aoi: AOI,
    error_model: GaussianGazeErrorModel,
    endpoint: AOIEffectEndpoint,
    *,
    observed_x: str = "observed_x",
    observed_y: str = "observed_y",
    draws: int = 2000,
    batch_size: int = 200,
    interval: float = 0.95,
    reference: float = 0.0,
    rng: np.random.Generator | int | None = None,
) -> AOIEffectUncertaintyAudit:
    """Propagate gaze-position measurement uncertainty into an AOI endpoint.

    For each Monte Carlo draw, one latent true position is sampled for every
    observation under ``error_model``.  AOI membership is recomputed from that
    complete latent realization and supplied to ``endpoint(data, membership)``.
    This preserves across-observation endpoint structure within each draw (for
    example participant-level treatment-minus-control aggregation).

    ``expected_membership_effect`` in the returned summary evaluates the
    endpoint once using each observation's marginal AOI-membership probability.
    For nonlinear endpoints this need not equal the mean of the draw-specific
    endpoint distribution; both quantities are therefore retained explicitly.

    Notes
    -----
    The reported interval is a Monte Carlo interval induced by the declared
    gaze measurement-error model.  It is not a population confidence interval
    and must not be interpreted as incorporating sampling uncertainty.
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if not isinstance(error_model, GaussianGazeErrorModel):
        raise TypeError("error_model must be a GaussianGazeErrorModel")
    if not callable(endpoint):
        raise TypeError("endpoint must be callable")
    if draws < 2:
        raise ValueError("draws must be at least 2")
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    if not 0.0 < interval < 1.0:
        raise ValueError("interval must be strictly between 0 and 1")
    if not np.isfinite(reference):
        raise ValueError("reference must be finite")

    missing = [column for column in (observed_x, observed_y) if column not in data.columns]
    if missing:
        raise ValueError(f"data is missing observed gaze columns: {missing}")
    if data.empty:
        raise ValueError("data must contain at least one observation")

    points = data[[observed_x, observed_y]].apply(pd.to_numeric, errors="coerce").to_numpy(
        dtype=float
    )
    if np.any(~np.isfinite(points)):
        raise ValueError("observed gaze coordinates must be finite and complete")

    hard_membership = np.asarray(aoi.contains_points(points), dtype=float)
    _validate_membership(hard_membership, len(data), label="hard AOI membership")
    hard_effect = _endpoint_value(endpoint, data, hard_membership)

    generator = _as_rng(rng)
    estimates = np.empty(draws, dtype=float)
    membership_sum = np.zeros(len(data), dtype=float)
    completed = 0

    while completed < draws:
        current = min(batch_size, draws - completed)
        # Draw-major layout keeps every scientific endpoint evaluation tied to
        # one complete latent realization of the study.
        error_draws = generator.multivariate_normal(
            mean=error_model.mean_error,
            cov=error_model.covariance,
            size=(current, len(data)),
            check_valid="raise",
        )
        latent = points[None, :, :] - error_draws

        for offset in range(current):
            membership = np.asarray(aoi.contains_points(latent[offset]), dtype=float)
            _validate_membership(membership, len(data), label="sampled AOI membership")
            membership_sum += membership
            estimates[completed + offset] = _endpoint_value(endpoint, data, membership)
        completed += current

    membership_probability = membership_sum / float(draws)
    expected_membership_effect = _endpoint_value(endpoint, data, membership_probability)

    alpha = (1.0 - interval) / 2.0
    lower, upper = np.quantile(estimates, [alpha, 1.0 - alpha])
    above = float(np.mean(estimates > reference))
    below = float(np.mean(estimates < reference))
    equal = float(np.mean(estimates == reference))

    draw_effects = pd.DataFrame(
        {
            "draw": np.arange(draws, dtype=int),
            "estimate": estimates,
        }
    )
    membership_probabilities = pd.DataFrame(
        {
            "observation": np.arange(len(data), dtype=int),
            "membership_probability": membership_probability,
        }
    )
    summary = pd.Series(
        {
            "aoi": aoi.name,
            "n_observations": int(len(data)),
            "n_draws": int(draws),
            "interval_level": float(interval),
            "reference": float(reference),
            "hard_effect": hard_effect,
            "expected_membership_effect": expected_membership_effect,
            "monte_carlo_mean": float(np.mean(estimates)),
            "monte_carlo_median": float(np.median(estimates)),
            "monte_carlo_sd": float(np.std(estimates, ddof=1)),
            "interval_lower": float(lower),
            "interval_upper": float(upper),
            "probability_above_reference": above,
            "probability_below_reference": below,
            "probability_equal_reference": equal,
        }
    )
    return AOIEffectUncertaintyAudit(
        aoi=aoi.name,
        draw_effects=draw_effects,
        membership_probabilities=membership_probabilities,
        summary=summary,
    )


def _endpoint_value(
    endpoint: AOIEffectEndpoint,
    data: pd.DataFrame,
    membership: np.ndarray,
) -> float:
    value = endpoint(data, membership)
    array = np.asarray(value)
    if array.ndim != 0:
        raise TypeError("endpoint must return a scalar")
    try:
        scalar = float(array)
    except (TypeError, ValueError) as exc:
        raise TypeError("endpoint must return a numeric scalar") from exc
    if not np.isfinite(scalar):
        raise ValueError("endpoint must return a finite scalar")
    return scalar


def _validate_membership(values: np.ndarray, n: int, *, label: str) -> None:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or arr.size != n:
        raise ValueError(f"{label} must be one-dimensional and match data rows")
    if np.any(~np.isfinite(arr)) or np.any((arr < 0.0) | (arr > 1.0)):
        raise ValueError(f"{label} must contain finite values between 0 and 1")


def _as_rng(rng: np.random.Generator | int | None) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)
