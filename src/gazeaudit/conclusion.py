"""Predeclared conclusion-recovery diagnostics for robustness studies.

These utilities deliberately evaluate scientific-effect recovery without using
p-values, confidence-interval crossing, or specification selection. The
researcher declares the acceptable error and recovery fraction before examining
the robustness results.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .aoi import AOI, RectangleAOI
from .benchmark import fit_error_model_from_known_truth
from .scientific_benchmark import condition_dwell_effect, simulate_known_aoi_effect
from .sensitivity import scale_error_model
from .uncertainty import GaussianGazeErrorModel, aoi_probabilities


@dataclass(frozen=True)
class ConclusionRule:
    """Predeclared rule for deciding whether a scientific effect is recovered.

    At least one numerical tolerance must be supplied. When both absolute and
    relative tolerances are present, both must be satisfied. ``require_sign``
    additionally requires the estimated effect to have the same direction as
    the known/reference effect. ``minimum_recovery_fraction`` is applied only
    when a set of specifications is summarized.

    This is a scientific robustness rule, not a statistical-significance rule.
    """

    relative_tolerance: float | None = None
    absolute_tolerance: float | None = None
    require_sign: bool = True
    minimum_recovery_fraction: float = 0.90

    def __post_init__(self) -> None:
        if self.relative_tolerance is None and self.absolute_tolerance is None:
            raise ValueError(
                "at least one of relative_tolerance or absolute_tolerance is required"
            )
        for name, value in (
            ("relative_tolerance", self.relative_tolerance),
            ("absolute_tolerance", self.absolute_tolerance),
        ):
            if value is not None and (not np.isfinite(value) or value < 0):
                raise ValueError(f"{name} must be finite and non-negative")
        if not np.isfinite(self.minimum_recovery_fraction) or not (
            0.0 <= self.minimum_recovery_fraction <= 1.0
        ):
            raise ValueError("minimum_recovery_fraction must be between 0 and 1")


@dataclass(frozen=True)
class ConclusionBenchmark:
    """Known-truth benchmark output for one deliberately constructed case."""

    case: str
    true_effect: float
    specifications: pd.DataFrame
    recovery: pd.DataFrame
    summary: pd.Series


def conclusion_recovery_table(
    results: pd.DataFrame,
    true_effect: float,
    rule: ConclusionRule,
    *,
    estimate_col: str = "estimate",
) -> pd.DataFrame:
    """Evaluate effect recovery for every predeclared specification.

    The returned table preserves all input specification columns and appends
    absolute/relative error, effect ratio, direction recovery, tolerance
    recovery, and the combined conclusion-recovery indicator.
    """

    if estimate_col not in results.columns:
        raise ValueError(f"column {estimate_col!r} is not present in results")
    if results.empty:
        raise ValueError("results must contain at least one specification")
    if not np.isfinite(true_effect):
        raise ValueError("true_effect must be finite")

    estimates = pd.to_numeric(results[estimate_col], errors="coerce").to_numpy(dtype=float)
    if np.any(~np.isfinite(estimates)):
        raise ValueError("estimates must be finite")

    output = results.copy()
    absolute_error = np.abs(estimates - true_effect)
    output["true_effect"] = float(true_effect)
    output["absolute_error"] = absolute_error

    if true_effect == 0.0:
        relative_error = np.full(estimates.size, np.nan, dtype=float)
        effect_ratio = np.full(estimates.size, np.nan, dtype=float)
        sign_recovered = np.ones(estimates.size, dtype=bool)
    else:
        relative_error = absolute_error / abs(true_effect)
        effect_ratio = estimates / true_effect
        sign_recovered = np.sign(estimates) == np.sign(true_effect)

    output["relative_error"] = relative_error
    output["effect_ratio"] = effect_ratio
    output["sign_recovered"] = sign_recovered
    output["sign_flipped"] = ~sign_recovered

    tolerance_parts: list[np.ndarray] = []
    if rule.absolute_tolerance is not None:
        absolute_ok = absolute_error <= rule.absolute_tolerance
        output["absolute_tolerance_recovered"] = absolute_ok
        tolerance_parts.append(absolute_ok)
    if rule.relative_tolerance is not None:
        if true_effect == 0.0:
            raise ValueError(
                "relative_tolerance cannot be evaluated when true_effect is zero; "
                "provide absolute_tolerance"
            )
        relative_ok = relative_error <= rule.relative_tolerance
        output["relative_tolerance_recovered"] = relative_ok
        tolerance_parts.append(relative_ok)

    tolerance_recovered = np.logical_and.reduce(tolerance_parts)
    output["tolerance_recovered"] = tolerance_recovered
    if rule.require_sign:
        output["conclusion_recovered"] = tolerance_recovered & sign_recovered
    else:
        output["conclusion_recovered"] = tolerance_recovered
    return output


def summarize_conclusion_recovery(
    recovery: pd.DataFrame,
    rule: ConclusionRule,
) -> pd.Series:
    """Summarize recovery across the declared specification set.

    ``classification`` is determined solely by the predeclared
    ``minimum_recovery_fraction``: ``"robust"`` at or above the threshold and
    ``"fragile"`` below it. It is descriptive of the supplied specification
    space and is not evidence that omitted specifications are irrelevant.
    """

    required = {
        "absolute_error",
        "relative_error",
        "sign_recovered",
        "sign_flipped",
        "tolerance_recovered",
        "conclusion_recovered",
    }
    missing = required.difference(recovery.columns)
    if missing:
        raise ValueError(f"recovery is missing required columns: {sorted(missing)}")
    if recovery.empty:
        raise ValueError("recovery must contain at least one specification")

    recovered = recovery["conclusion_recovered"].astype(bool).to_numpy()
    sign_recovered = recovery["sign_recovered"].astype(bool).to_numpy()
    tolerance_recovered = recovery["tolerance_recovered"].astype(bool).to_numpy()
    absolute_error = pd.to_numeric(
        recovery["absolute_error"], errors="coerce"
    ).to_numpy(dtype=float)
    relative_error = pd.to_numeric(
        recovery["relative_error"], errors="coerce"
    ).to_numpy(dtype=float)

    recovery_fraction = float(np.mean(recovered))
    finite_relative = relative_error[np.isfinite(relative_error)]
    return pd.Series(
        {
            "n_specifications": int(len(recovery)),
            "conclusion_recovery_fraction": recovery_fraction,
            "sign_recovery_fraction": float(np.mean(sign_recovered)),
            "sign_flip_fraction": float(np.mean(~sign_recovered)),
            "tolerance_recovery_fraction": float(np.mean(tolerance_recovered)),
            "median_absolute_error": float(np.median(absolute_error)),
            "max_absolute_error": float(np.max(absolute_error)),
            "median_relative_error": (
                float(np.median(finite_relative)) if finite_relative.size else np.nan
            ),
            "max_relative_error": (
                float(np.max(finite_relative)) if finite_relative.size else np.nan
            ),
            "minimum_recovery_fraction": float(rule.minimum_recovery_fraction),
            "classification": (
                "robust"
                if recovery_fraction >= rule.minimum_recovery_fraction
                else "fragile"
            ),
        }
    )


def aoi_conclusion_specifications(
    data: pd.DataFrame,
    aoi: AOI,
    error_model: GaussianGazeErrorModel,
    *,
    error_scales: Iterable[float] = (0.5, 1.0, 1.5, 2.0),
    missing_fractions: Iterable[float] = (0.0, 0.05, 0.10, 0.20),
    draws: int = 1000,
    rng: np.random.Generator | int | None = None,
) -> tuple[float, pd.DataFrame]:
    """Build a known-truth AOI-effect specification set.

    Each missingness fraction uses one pre-generated row-retention mask that is
    shared by the hard and probabilistic AOI specifications. The deterministic
    hard-assignment baseline is evaluated once per missingness level; each
    probabilistic specification additionally perturbs the fitted spatial-error
    standard deviation by ``error_scale``.

    Missing rows are removed rather than imputed. Because the benchmark endpoint
    is total weighted dwell, missingness can attenuate the effect; that behavior
    is intentionally part of the challenge case rather than silently corrected.
    """

    _validate_known_truth_data(data)
    scales = tuple(float(value) for value in error_scales)
    fractions = tuple(float(value) for value in missing_fractions)
    if not scales:
        raise ValueError("error_scales must contain at least one value")
    if any(not np.isfinite(value) or value < 0 for value in scales):
        raise ValueError("error_scales must be finite and non-negative")
    if not fractions:
        raise ValueError("missing_fractions must contain at least one value")
    if any(not np.isfinite(value) or not 0.0 <= value < 1.0 for value in fractions):
        raise ValueError("missing_fractions must be finite and in [0, 1)")
    if draws < 1:
        raise ValueError("draws must be at least 1")

    truth_points = data[["true_x", "true_y"]].to_numpy(dtype=float)
    true_membership = np.asarray(aoi.contains_points(truth_points), dtype=float)
    true_effect = condition_dwell_effect(data, true_membership)

    generator = _as_rng(rng)
    rows: list[dict[str, Any]] = []
    n_rows = len(data)
    for missing_fraction in fractions:
        retained = _retained_positions(n_rows, missing_fraction, generator)
        subset = data.iloc[retained].reset_index(drop=True)
        observed = subset[["observed_x", "observed_y"]].to_numpy(dtype=float)

        hard_membership = np.asarray(aoi.contains_points(observed), dtype=float)
        hard_estimate = condition_dwell_effect(subset, hard_membership)
        rows.append(
            {
                "method": "hard",
                "error_scale": np.nan,
                "missing_fraction": missing_fraction,
                "n_rows": int(len(subset)),
                "retained_fraction": float(len(subset) / n_rows),
                "estimate": hard_estimate,
            }
        )

        for error_scale in scales:
            scaled_model = scale_error_model(error_model, sd_scale=error_scale)
            child_seed = int(
                generator.integers(0, np.iinfo(np.uint32).max, dtype=np.uint32)
            )
            probabilities = aoi_probabilities(
                observed,
                [aoi],
                scaled_model,
                draws=draws,
                rng=child_seed,
                include_outside=False,
            )[aoi.name].to_numpy(dtype=float)
            estimate = condition_dwell_effect(subset, probabilities)
            rows.append(
                {
                    "method": "probabilistic",
                    "error_scale": error_scale,
                    "missing_fraction": missing_fraction,
                    "n_rows": int(len(subset)),
                    "retained_fraction": float(len(subset) / n_rows),
                    "estimate": estimate,
                }
            )

    return float(true_effect), pd.DataFrame(rows)


def run_canonical_conclusion_benchmark(
    case: str,
    *,
    rule: ConclusionRule | None = None,
    n_participants: int = 80,
    trials_per_condition: int = 30,
    draws: int = 1000,
    rng: np.random.Generator | int | None = 123,
) -> ConclusionBenchmark:
    """Run a deliberately constructed robust or fragile known-truth benchmark.

    The two cases are synthetic methodological challenges, not empirical claims
    about a particular tracker. The ``robust`` case has a strong effect, gaze
    clusters well separated from the AOI boundary, and modest measurement error.
    The ``fragile`` case has a small effect, gaze concentrated near the boundary,
    and larger measurement error. Both are evaluated under the same predeclared
    error-scale and missingness specification space.
    """

    normalized_case = case.strip().lower()
    if normalized_case == "robust":
        parameters = {
            "control_probability": 0.20,
            "treatment_probability": 0.80,
            "left_center": -30.0,
            "right_center": 30.0,
            "center_sd": 4.0,
            "measurement_sd": 4.0,
        }
    elif normalized_case == "fragile":
        parameters = {
            "control_probability": 0.45,
            "treatment_probability": 0.55,
            "left_center": -4.0,
            "right_center": 4.0,
            "center_sd": 6.0,
            "measurement_sd": 8.0,
        }
    else:
        raise ValueError("case must be 'robust' or 'fragile'")

    if rule is None:
        rule = ConclusionRule(
            relative_tolerance=0.20,
            require_sign=True,
            minimum_recovery_fraction=0.90,
        )

    generator = _as_rng(rng)
    simulation_seed = int(
        generator.integers(0, np.iinfo(np.uint32).max, dtype=np.uint32)
    )
    specification_seed = int(
        generator.integers(0, np.iinfo(np.uint32).max, dtype=np.uint32)
    )
    data = simulate_known_aoi_effect(
        n_participants=n_participants,
        trials_per_condition=trials_per_condition,
        rng=simulation_seed,
        **parameters,
    )
    error_model = fit_error_model_from_known_truth(data)
    right_aoi = RectangleAOI("right", 0.0, -100.0, 100.0, 100.0)
    true_effect, specifications = aoi_conclusion_specifications(
        data,
        right_aoi,
        error_model,
        draws=draws,
        rng=specification_seed,
    )
    recovery = conclusion_recovery_table(specifications, true_effect, rule)
    summary = summarize_conclusion_recovery(recovery, rule)
    return ConclusionBenchmark(
        case=normalized_case,
        true_effect=true_effect,
        specifications=specifications,
        recovery=recovery,
        summary=summary,
    )


def run_paired_conclusion_benchmark(
    *,
    rule: ConclusionRule | None = None,
    n_participants: int = 80,
    trials_per_condition: int = 30,
    draws: int = 1000,
    rng: np.random.Generator | int | None = 123,
) -> dict[str, ConclusionBenchmark]:
    """Run matched robust and fragile challenge cases with independent seeds."""

    generator = _as_rng(rng)
    robust_seed = int(
        generator.integers(0, np.iinfo(np.uint32).max, dtype=np.uint32)
    )
    fragile_seed = int(
        generator.integers(0, np.iinfo(np.uint32).max, dtype=np.uint32)
    )
    return {
        "robust": run_canonical_conclusion_benchmark(
            "robust",
            rule=rule,
            n_participants=n_participants,
            trials_per_condition=trials_per_condition,
            draws=draws,
            rng=robust_seed,
        ),
        "fragile": run_canonical_conclusion_benchmark(
            "fragile",
            rule=rule,
            n_participants=n_participants,
            trials_per_condition=trials_per_condition,
            draws=draws,
            rng=fragile_seed,
        ),
    }


def _validate_known_truth_data(data: pd.DataFrame) -> None:
    required = {
        "participant",
        "condition",
        "duration",
        "true_x",
        "true_y",
        "observed_x",
        "observed_y",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"data is missing required columns: {sorted(missing)}")
    if data.empty:
        raise ValueError("data must contain at least one row")
    coordinate_columns = ["true_x", "true_y", "observed_x", "observed_y"]
    coordinates = data[coordinate_columns].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(coordinates.to_numpy(dtype=float)).all():
        raise ValueError("known-truth and observed coordinates must be finite")


def _retained_positions(
    n_rows: int,
    missing_fraction: float,
    generator: np.random.Generator,
) -> np.ndarray:
    n_missing = int(round(n_rows * missing_fraction))
    if n_missing == 0:
        return np.arange(n_rows, dtype=int)
    missing = generator.choice(n_rows, size=n_missing, replace=False)
    keep = np.ones(n_rows, dtype=bool)
    keep[missing] = False
    return np.flatnonzero(keep)


def _as_rng(rng: np.random.Generator | int | None) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)
