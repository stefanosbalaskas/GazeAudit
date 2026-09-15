"""Optional plotting helpers for GazeAudit audit and robustness outputs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd

from .aoi import CircleAOI, RectangleAOI
from .study_qc import StudyQCReport


def _pyplot():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "GazeAudit plotting helpers require matplotlib; install with "
            "`pip install gazeaudit[plot]`."
        ) from exc
    return plt


def _new_axes(*, figsize: tuple[float, float] = (7.2, 4.2)):
    plt = _pyplot()
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    return fig, ax


def _finite_numeric(frame: pd.DataFrame, column: str) -> np.ndarray:
    if column not in frame.columns:
        raise ValueError(f"column {column!r} is not present")
    values = pd.to_numeric(frame[column], errors="coerce").to_numpy(dtype=float)
    if values.size == 0 or np.any(~np.isfinite(values)):
        raise ValueError(f"column {column!r} must contain finite numeric values")
    return values


def plot_qc_issue_profile(
    report: StudyQCReport | Mapping[str, Any],
):
    """Plot counts for the five structural-QC issue families."""

    if isinstance(report, StudyQCReport):
        values = report.to_dict()
    elif isinstance(report, Mapping):
        values = dict(report)
    else:
        raise TypeError("report must be StudyQCReport or a mapping")

    labels = [
        "Coordinate\nnon-finite",
        "Timestamp\nnon-finite",
        "Identifier\nmissing",
        "Duplicate\ntimestamp",
        "Decreasing\ntime",
    ]
    counts = [
        int(values["coordinate_issue_rows"]),
        int(values["timestamp_issue_rows"]),
        int(values["missing_identifier_rows"]),
        int(values["duplicate_timestamp_rows"]),
        int(values["decreasing_time_groups"]),
    ]
    fig, ax = _new_axes()
    positions = np.arange(len(labels))
    bars = ax.bar(positions, counts)
    ax.set_xticks(positions, labels)
    ax.set_ylabel("Flagged rows / groups")
    ax.set_title("Structural QC issue profile")
    ax.grid(axis="y", alpha=0.2)
    for bar, count in zip(bars, counts, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(count),
            ha="center",
            va="bottom",
            fontsize=9,
        )
    return fig


def plot_trial_readiness(
    summary: pd.DataFrame,
    *,
    max_units: int = 30,
):
    """Plot trial-level structural issue burden and policy pass/review status."""

    required = {"trial_unit_id", "any_row_issue_fraction", "passes_thresholds"}
    missing = required - set(summary.columns)
    if missing:
        raise ValueError(f"trial summary is missing columns: {sorted(missing)}")
    if max_units < 1:
        raise ValueError("max_units must be positive")

    frame = summary.head(max_units).copy()
    values = _finite_numeric(frame, "any_row_issue_fraction")
    labels = frame["trial_unit_id"].astype(str).tolist()
    passed = frame["passes_thresholds"].astype(bool).to_numpy()

    height = max(4.2, min(10.0, 0.32 * len(frame) + 1.7))
    fig, ax = _new_axes(figsize=(7.4, height))
    positions = np.arange(len(frame))
    bars = ax.barh(positions, values)
    ax.set_yticks(positions, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, max(1.0, float(values.max()) * 1.08 if len(values) else 1.0))
    ax.set_xlabel("Rows with ≥1 structural issue")
    ax.set_title("Trial-level readiness preview")
    ax.grid(axis="x", alpha=0.2)
    for i, (bar, ok) in enumerate(zip(bars, passed, strict=True)):
        ax.text(
            max(float(bar.get_width()) + 0.01, 0.02),
            i,
            "pass" if ok else "review",
            va="center",
            fontsize=8,
        )
    return fig


def plot_participant_readiness(
    summary: pd.DataFrame,
    *,
    max_units: int = 30,
):
    """Plot participant-level fraction of trials failing the declared policy."""

    required = {"participant_unit_id", "flagged_trial_fraction", "passes_thresholds"}
    missing = required - set(summary.columns)
    if missing:
        raise ValueError(f"participant summary is missing columns: {sorted(missing)}")
    frame = summary.head(max_units).copy()
    values = _finite_numeric(frame, "flagged_trial_fraction")
    labels = frame["participant_unit_id"].astype(str).tolist()

    height = max(4.0, min(9.0, 0.36 * len(frame) + 1.6))
    fig, ax = _new_axes(figsize=(7.4, height))
    positions = np.arange(len(frame))
    ax.barh(positions, values)
    ax.set_yticks(positions, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("Fraction of trials failing policy")
    ax.set_title("Participant readiness profile")
    ax.grid(axis="x", alpha=0.2)
    return fig


def plot_cohort_impact(
    impact: pd.DataFrame,
    *,
    metric: str = "rows",
):
    """Plot baseline versus retained cohort size for trial/participant filtering scope."""

    metric_map = {
        "rows": ("baseline_rows", "retained_rows", "Rows"),
        "trials": ("baseline_trial_units", "retained_trial_units", "Trial units"),
        "participants": (
            "baseline_participant_units",
            "retained_participant_units",
            "Participant units",
        ),
    }
    if metric not in metric_map:
        raise ValueError("metric must be 'rows', 'trials', or 'participants'")
    baseline_col, retained_col, axis_label = metric_map[metric]
    required = {"scope", baseline_col, retained_col}
    missing = required - set(impact.columns)
    if missing:
        raise ValueError(f"cohort impact is missing columns: {sorted(missing)}")

    frame = impact.copy()
    baseline = _finite_numeric(frame, baseline_col)
    retained = _finite_numeric(frame, retained_col)
    scopes = frame["scope"].astype(str).tolist()
    positions = np.arange(len(frame))
    width = 0.36

    fig, ax = _new_axes()
    ax.bar(positions - width / 2, baseline, width=width, label="Baseline")
    ax.bar(positions + width / 2, retained, width=width, label="Retained")
    ax.set_xticks(positions, scopes)
    ax.set_ylabel(axis_label)
    ax.set_title(f"Cohort impact preview · {metric}")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    return fig


def plot_repair_comparison(
    metrics: pd.DataFrame,
    *,
    metric_names: Sequence[str] = (
        "coordinate_issue_rows",
        "timestamp_issue_rows",
        "missing_identifier_rows",
        "duplicate_timestamp_rows",
        "decreasing_time_groups",
    ),
):
    """Plot selected structural-QC counts before and after a recorded repair."""

    required = {"metric", "before", "after"}
    missing = required - set(metrics.columns)
    if missing:
        raise ValueError(f"repair comparison is missing columns: {sorted(missing)}")
    frame = metrics.loc[metrics["metric"].isin(metric_names)].copy()
    if frame.empty:
        raise ValueError("none of metric_names are present in the comparison")
    before = _finite_numeric(frame, "before")
    after = _finite_numeric(frame, "after")
    labels = [value.replace("_", " ") for value in frame["metric"].astype(str)]
    positions = np.arange(len(frame))
    width = 0.36

    fig, ax = _new_axes(figsize=(8.0, 4.6))
    ax.bar(positions - width / 2, before, width=width, label="Before")
    ax.bar(positions + width / 2, after, width=width, label="After")
    ax.set_xticks(positions, labels, rotation=20, ha="right")
    ax.set_ylabel("Flagged rows / groups")
    ax.set_title("Before/after structural QC comparison")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    return fig


def plot_policy_tradeoffs(
    policy_table: pd.DataFrame,
):
    """Plot retained-row trade-offs across declared readiness policies."""

    required = {
        "policy",
        "trial_retained_row_fraction",
        "participant_retained_row_fraction",
    }
    missing = required - set(policy_table.columns)
    if missing:
        raise ValueError(f"policy table is missing columns: {sorted(missing)}")
    x = _finite_numeric(policy_table, "trial_retained_row_fraction")
    y = _finite_numeric(policy_table, "participant_retained_row_fraction")

    fig, ax = _new_axes()
    ax.scatter(x, y, s=55)
    for x_value, y_value, label in zip(
        x, y, policy_table["policy"].astype(str), strict=True
    ):
        ax.annotate(label, (x_value, y_value), xytext=(5, 5), textcoords="offset points")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Retained rows · trial scope")
    ax.set_ylabel("Retained rows · participant scope")
    ax.set_title("Readiness-policy cohort trade-offs")
    ax.grid(alpha=0.2)
    return fig


def plot_threshold_sweep(
    sweep: pd.DataFrame,
    *,
    threshold_col: str = "threshold",
    retained_col: str = "retained_fraction",
):
    """Plot cohort retention across a user-declared threshold sweep."""

    x = _finite_numeric(sweep, threshold_col)
    y = _finite_numeric(sweep, retained_col)
    order = np.argsort(x, kind="mergesort")
    fig, ax = _new_axes()
    ax.plot(x[order], y[order], marker="o")
    ax.set_xlabel(threshold_col.replace("_", " "))
    ax.set_ylabel(retained_col.replace("_", " "))
    ax.set_ylim(0, 1.02)
    ax.set_title("Threshold sensitivity of cohort retention")
    ax.grid(alpha=0.2)
    return fig


def plot_specification_curve(
    results: pd.DataFrame,
    *,
    estimate_col: str = "estimate",
):
    """Plot estimates ordered from lowest to highest specification result."""

    estimates = _finite_numeric(results, estimate_col)
    ordered = np.sort(estimates, kind="mergesort")
    positions = np.arange(1, len(ordered) + 1)
    fig, ax = _new_axes()
    ax.scatter(positions, ordered, s=35)
    ax.plot(positions, ordered, linewidth=1, alpha=0.6)
    ax.axhline(0, linewidth=1, linestyle="--")
    ax.set_xlabel("Ordered specification")
    ax.set_ylabel(estimate_col.replace("_", " "))
    ax.set_title("Specification curve")
    ax.grid(axis="y", alpha=0.2)
    return fig


def plot_factor_sensitivity(
    sensitivity: pd.DataFrame,
    *,
    factor_col: str = "factor",
    value_col: str = "marginal_eta2",
):
    """Plot a ranked factor-sensitivity summary."""

    values = _finite_numeric(sensitivity, value_col)
    labels = sensitivity[factor_col].astype(str).to_numpy()
    order = np.argsort(values, kind="mergesort")
    fig, ax = _new_axes()
    ax.barh(np.arange(len(order)), values[order])
    ax.set_yticks(np.arange(len(order)), labels[order])
    ax.set_xlabel(value_col.replace("_", " "))
    ax.set_title("Specification-factor sensitivity")
    ax.grid(axis="x", alpha=0.2)
    return fig


def plot_sensitivity_curve(
    curve: pd.DataFrame,
    *,
    x_col: str,
    y_col: str = "estimate",
    title: str = "Sensitivity curve",
    x_label: str | None = None,
    y_label: str | None = None,
):
    """Plot a deterministic one-dimensional sensitivity result."""

    x = _finite_numeric(curve, x_col)
    y = _finite_numeric(curve, y_col)
    order = np.argsort(x, kind="mergesort")
    fig, ax = _new_axes()
    ax.plot(x[order], y[order], marker="o")
    ax.set_xlabel(x_label or x_col.replace("_", " "))
    ax.set_ylabel(y_label or y_col.replace("_", " "))
    ax.set_title(title)
    ax.grid(alpha=0.2)
    return fig


def plot_gaze_trajectory(
    data: pd.DataFrame,
    *,
    x_col: str = "x",
    y_col: str = "y",
    timestamp_col: str = "timestamp",
    aoi: RectangleAOI | CircleAOI | None = None,
):
    """Plot one gaze trajectory with an optional AOI geometry overlay."""

    x = _finite_numeric(data, x_col)
    y = _finite_numeric(data, y_col)
    time = _finite_numeric(data, timestamp_col)
    order = np.argsort(time, kind="mergesort")

    fig, ax = _new_axes(figsize=(6.4, 5.2))
    ax.plot(x[order], y[order], linewidth=1.2, alpha=0.7)
    scatter = ax.scatter(x[order], y[order], c=np.arange(len(order)), s=32)
    fig.colorbar(scatter, ax=ax, label="Observed order")

    if aoi is not None:
        try:
            from matplotlib.patches import Circle, Rectangle
        except ImportError as exc:
            raise ImportError("matplotlib is required for AOI overlays") from exc
        if isinstance(aoi, RectangleAOI):
            patch = Rectangle(
                (aoi.xmin, aoi.ymin),
                aoi.xmax - aoi.xmin,
                aoi.ymax - aoi.ymin,
                fill=False,
                linewidth=2,
                linestyle="--",
            )
        elif isinstance(aoi, CircleAOI):
            patch = Circle(
                (aoi.cx, aoi.cy),
                aoi.radius,
                fill=False,
                linewidth=2,
                linestyle="--",
            )
        else:
            raise TypeError("aoi must be RectangleAOI, CircleAOI, or None")
        ax.add_patch(patch)

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title("Gaze trajectory and AOI geometry")
    ax.invert_yaxis()
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(alpha=0.15)
    return fig


def plot_aoi_probability_profile(
    profile: pd.DataFrame,
    *,
    position_col: str = "boundary_distance",
    probability_col: str = "membership_probability",
):
    """Plot probabilistic AOI membership across a signed boundary distance."""

    x = _finite_numeric(profile, position_col)
    y = _finite_numeric(profile, probability_col)
    order = np.argsort(x, kind="mergesort")
    fig, ax = _new_axes()
    ax.plot(x[order], y[order], marker="o")
    ax.axvline(0, linewidth=1, linestyle="--")
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("Signed distance from AOI boundary")
    ax.set_ylabel("Membership probability")
    ax.set_title("Probabilistic AOI boundary profile")
    ax.grid(alpha=0.2)
    return fig


def plot_recovery_matrix(
    recovery: pd.DataFrame,
    *,
    row_col: str,
    column_col: str,
    value_col: str,
    title: str = "Recovery matrix",
):
    """Plot a rectangular pivoted recovery/sensitivity matrix with annotations."""

    required = {row_col, column_col, value_col}
    missing = required - set(recovery.columns)
    if missing:
        raise ValueError(f"recovery table is missing columns: {sorted(missing)}")
    pivot = recovery.pivot(index=row_col, columns=column_col, values=value_col)
    values = pivot.to_numpy(dtype=float)
    if values.size == 0 or np.any(~np.isfinite(values)):
        raise ValueError("recovery matrix must be complete and finite")

    fig, ax = _new_axes(figsize=(7.0, 5.2))
    image = ax.imshow(values, aspect="auto")
    fig.colorbar(image, ax=ax, label=value_col.replace("_", " "))
    ax.set_xticks(np.arange(len(pivot.columns)), [str(v) for v in pivot.columns])
    ax.set_yticks(np.arange(len(pivot.index)), [str(v) for v in pivot.index])
    ax.set_xlabel(column_col.replace("_", " "))
    ax.set_ylabel(row_col.replace("_", " "))
    ax.set_title(title)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ax.text(j, i, f"{values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    return fig
