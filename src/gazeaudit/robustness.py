"""Robustness summaries for eye-tracking specification analyses."""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd


def effect_stability(
    results: pd.DataFrame,
    *,
    estimate_col: str = "estimate",
    null: float = 0.0,
) -> pd.Series:
    """Summarize the stability of a scalar effect across specifications.

    The returned statistics are descriptive. They do not replace a formal
    inferential model and should not be interpreted as posterior probabilities.
    """

    estimates = _estimate_array(results, estimate_col)
    centered = estimates - null
    positive = float(np.mean(centered > 0))
    negative = float(np.mean(centered < 0))
    exact_null = float(np.mean(centered == 0))

    return pd.Series(
        {
            "n_specifications": int(estimates.size),
            "median_estimate": float(np.median(estimates)),
            "mean_estimate": float(np.mean(estimates)),
            "min_estimate": float(np.min(estimates)),
            "max_estimate": float(np.max(estimates)),
            "q025": float(np.quantile(estimates, 0.025)),
            "q975": float(np.quantile(estimates, 0.975)),
            "positive_fraction": positive,
            "negative_fraction": negative,
            "exact_null_fraction": exact_null,
            "sign_stability": max(positive, negative, exact_null),
        }
    )


def marginal_sensitivity(
    results: pd.DataFrame,
    factors: list[str] | tuple[str, ...],
    *,
    estimate_col: str = "estimate",
) -> pd.DataFrame:
    """Estimate marginal sensitivity of the endpoint to specification factors.

    For each factor, this computes the between-level sum of squares divided by
    the total sum of squares of the endpoint. Because factors in a multiverse can
    be dependent or interact, these marginal eta-squared values need not sum to
    one and are not a causal variance decomposition. They are intended as an
    auditable screening diagnostic for where result instability originates.
    """

    estimates = _estimate_array(results, estimate_col)
    grand_mean = float(np.mean(estimates))
    total_ss = float(np.sum((estimates - grand_mean) ** 2))

    rows: list[dict[str, object]] = []
    for factor in factors:
        if factor not in results.columns:
            raise ValueError(f"factor {factor!r} is not present in results")

        grouped = results.groupby(factor, dropna=False, sort=False)[estimate_col]
        level_summary = grouped.agg(["count", "mean"])
        between_ss = float(
            np.sum(level_summary["count"] * (level_summary["mean"] - grand_mean) ** 2)
        )
        eta2 = between_ss / total_ss if total_ss > 0 else 0.0
        level_range = float(level_summary["mean"].max() - level_summary["mean"].min())
        rows.append(
            {
                "factor": factor,
                "n_levels": int(level_summary.shape[0]),
                "marginal_eta2": eta2,
                "level_mean_range": level_range,
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["marginal_eta2", "level_mean_range"], ascending=False, ignore_index=True
    )


def pairwise_interaction_sensitivity(
    results: pd.DataFrame,
    factors: list[str] | tuple[str, ...],
    *,
    estimate_col: str = "estimate",
) -> pd.DataFrame:
    """Screen two-way specification interactions using descriptive effect variation.

    For each factor pair, cell means are compared with the additive prediction
    ``mean(A) + mean(B) - grand_mean``. The weighted squared deviation from that
    additive prediction is divided by total endpoint sum of squares. The result
    is a descriptive interaction-sensitivity ratio, not a causal decomposition
    and not a replacement for a fitted factorial model. In unbalanced or
    incomplete multiverses, ratios across pairs can overlap and need not sum to
    one.
    """

    estimates = _estimate_array(results, estimate_col)
    if len(factors) < 2:
        return pd.DataFrame(
            columns=[
                "factor_a",
                "factor_b",
                "n_cells",
                "interaction_ratio",
                "max_abs_interaction",
            ]
        )

    for factor in factors:
        if factor not in results.columns:
            raise ValueError(f"factor {factor!r} is not present in results")

    grand_mean = float(np.mean(estimates))
    total_ss = float(np.sum((estimates - grand_mean) ** 2))
    rows: list[dict[str, object]] = []

    for factor_a, factor_b in combinations(factors, 2):
        mean_a = results.groupby(factor_a, dropna=False)[estimate_col].mean()
        mean_b = results.groupby(factor_b, dropna=False)[estimate_col].mean()
        cells = (
            results.groupby([factor_a, factor_b], dropna=False)[estimate_col]
            .agg(["count", "mean"])
            .reset_index()
        )

        deviations: list[float] = []
        weighted_ss = 0.0
        for row in cells.itertuples(index=False):
            level_a = getattr(row, factor_a)
            level_b = getattr(row, factor_b)
            additive = float(mean_a.loc[level_a] + mean_b.loc[level_b] - grand_mean)
            deviation = float(row.mean - additive)
            deviations.append(deviation)
            weighted_ss += float(row.count) * deviation**2

        ratio = weighted_ss / total_ss if total_ss > 0 else 0.0
        rows.append(
            {
                "factor_a": factor_a,
                "factor_b": factor_b,
                "n_cells": int(len(cells)),
                "interaction_ratio": ratio,
                "max_abs_interaction": float(max(abs(value) for value in deviations)),
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["interaction_ratio", "max_abs_interaction"],
        ascending=False,
        ignore_index=True,
    )


def specification_curve(
    results: pd.DataFrame,
    *,
    estimate_col: str = "estimate",
) -> pd.DataFrame:
    """Return specifications ordered by their endpoint estimate."""

    _estimate_array(results, estimate_col)
    return results.sort_values(estimate_col, kind="mergesort", ignore_index=True).copy()


def _estimate_array(results: pd.DataFrame, estimate_col: str) -> np.ndarray:
    if estimate_col not in results.columns:
        raise ValueError(f"column {estimate_col!r} is not present in results")
    estimates = pd.to_numeric(results[estimate_col], errors="coerce").to_numpy(dtype=float)
    if estimates.size == 0:
        raise ValueError("results must contain at least one specification")
    if np.any(~np.isfinite(estimates)):
        raise ValueError("endpoint estimates must be finite")
    return estimates
