"""Fixed-cohort task-contrast robustness diagnostics for detector comparisons.

The helpers in this module implement the core analysis contract used by
predeclared multi-detector case studies: reference-only cohort construction,
fixation-run duration summaries, a fixed denominator for detector coverage, a
fail-closed completeness gate, and conclusion recovery without p-values.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .conclusion import (
    ConclusionRule,
    conclusion_recovery_table,
    summarize_conclusion_recovery,
)


@dataclass(frozen=True)
class DetectorRobustnessAudit:
    """Complete fixed-cohort audit for one two-task detector comparison."""

    fixed_cohort: tuple[Any, ...]
    reference_participant_tasks: pd.DataFrame
    reference_contrasts: pd.DataFrame
    reference_effect: float
    detector_participant_tasks: pd.DataFrame
    detector_contrasts: pd.DataFrame
    coverage: pd.DataFrame
    effects: pd.DataFrame
    recovery: pd.DataFrame | None
    summary: pd.Series


def fixation_event_durations(
    samples: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    label_col: str = "event_label",
    fixation_labels: Iterable[Any] = ("fixation",),
) -> np.ndarray:
    """Return durations of maximal contiguous fixation runs.

    Event duration follows the frozen GazeAudit convention::

        (last_timestamp - first_timestamp) + median_positive_sample_interval

    Timestamps must therefore be finite and strictly increasing and the stream
    must contain at least two samples. A one-sample fixation event is valid
    when it occurs inside such a stream and receives one median sample interval.
    """

    _require_columns(samples, [timestamp_col, label_col])
    if len(samples) < 2:
        raise ValueError("a stream needs at least two samples to define sample interval")

    timestamps = pd.to_numeric(samples[timestamp_col], errors="coerce").to_numpy(dtype=float)
    if np.any(~np.isfinite(timestamps)):
        raise ValueError("timestamps must be finite")
    intervals = np.diff(timestamps)
    if np.any(intervals <= 0):
        raise ValueError("timestamps must be strictly increasing")
    sample_interval = float(np.median(intervals))

    allowed = {_normalize_label(value) for value in fixation_labels}
    if not allowed:
        raise ValueError("fixation_labels must contain at least one label")
    labels = samples[label_col].map(_normalize_label).to_numpy(dtype=object)
    is_fixation = np.fromiter((value in allowed for value in labels), dtype=bool, count=len(labels))

    durations: list[float] = []
    start: int | None = None
    for index, is_fix in enumerate(is_fixation):
        if is_fix and start is None:
            start = index
        if start is not None and (not is_fix or index == len(is_fixation) - 1):
            end = index if is_fix and index == len(is_fixation) - 1 else index - 1
            durations.append(float(timestamps[end] - timestamps[start] + sample_interval))
            start = None
    return np.asarray(durations, dtype=float)


def participant_task_fixation_summary(
    samples: pd.DataFrame,
    *,
    participant_col: str = "participant",
    task_col: str = "task",
    timestamp_col: str = "timestamp",
    label_col: str = "event_label",
    fixation_labels: Iterable[Any] = ("fixation",),
    invalid: str = "missing",
) -> pd.DataFrame:
    """Summarize median fixation-event duration for each participant and task.

    ``invalid="missing"`` converts an invalid stream or a stream with no
    fixation event to a missing participant-task summary. ``invalid="raise"``
    propagates invalid-stream errors.
    """

    if invalid not in {"missing", "raise"}:
        raise ValueError("invalid must be 'missing' or 'raise'")
    _require_columns(
        samples,
        [participant_col, task_col, timestamp_col, label_col],
    )

    rows: list[dict[str, Any]] = []
    grouped = samples.groupby([participant_col, task_col], sort=False, dropna=False)
    for (participant, task), frame in grouped:
        valid_stream = True
        try:
            durations = fixation_event_durations(
                frame,
                timestamp_col=timestamp_col,
                label_col=label_col,
                fixation_labels=fixation_labels,
            )
        except ValueError:
            if invalid == "raise":
                raise
            durations = np.asarray([], dtype=float)
            valid_stream = False

        has_fixation = bool(durations.size)
        rows.append(
            {
                participant_col: participant,
                task_col: task,
                "median_fixation_duration": (
                    float(np.median(durations)) if has_fixation else np.nan
                ),
                "n_fixation_events": int(durations.size),
                "valid_stream": valid_stream,
                "has_fixation": has_fixation,
            }
        )
    return pd.DataFrame(rows)


def fixed_reference_cohort(
    reference_samples: pd.DataFrame,
    *,
    task_a: Any,
    task_b: Any,
    participant_col: str = "participant",
    task_col: str = "task",
    timestamp_col: str = "timestamp",
    label_col: str = "event_label",
    fixation_labels: Iterable[Any] = ("fixation",),
) -> tuple[tuple[Any, ...], pd.DataFrame, pd.DataFrame, float]:
    """Construct the paired analytic cohort using reference data only."""

    summaries = participant_task_fixation_summary(
        reference_samples,
        participant_col=participant_col,
        task_col=task_col,
        timestamp_col=timestamp_col,
        label_col=label_col,
        fixation_labels=fixation_labels,
        invalid="missing",
    )
    contrasts = _paired_task_contrasts(
        summaries,
        task_a=task_a,
        task_b=task_b,
        participant_col=participant_col,
        task_col=task_col,
    )
    eligible = contrasts.loc[contrasts["paired_complete"], participant_col].tolist()
    if not eligible:
        raise ValueError("reference data define an empty paired fixed cohort")

    ordered_cohort = tuple(eligible)
    paired = contrasts.loc[contrasts["paired_complete"]].reset_index(drop=True)
    effect = float(np.median(paired["task_contrast"].to_numpy(dtype=float)))
    if not np.isfinite(effect):
        raise ValueError("reference effect must be finite")
    return ordered_cohort, summaries, paired, effect


def detector_task_contrast(
    detector_samples: pd.DataFrame,
    fixed_cohort: Sequence[Any],
    *,
    task_a: Any,
    task_b: Any,
    participant_col: str = "participant",
    task_col: str = "task",
    timestamp_col: str = "timestamp",
    label_col: str = "event_label",
    fixation_labels: Iterable[Any] = ("fixation",),
) -> tuple[pd.DataFrame, pd.DataFrame, float, float]:
    """Compute a detector effect against a frozen participant denominator."""

    cohort = tuple(fixed_cohort)
    if not cohort:
        raise ValueError("fixed_cohort must contain at least one participant")
    if len(set(cohort)) != len(cohort):
        raise ValueError("fixed_cohort must not contain duplicate participants")
    _require_columns(detector_samples, [participant_col, task_col, timestamp_col, label_col])

    subset = detector_samples.loc[detector_samples[participant_col].isin(cohort)].copy()
    summaries = participant_task_fixation_summary(
        subset,
        participant_col=participant_col,
        task_col=task_col,
        timestamp_col=timestamp_col,
        label_col=label_col,
        fixation_labels=fixation_labels,
        invalid="missing",
    )
    contrasts = _paired_task_contrasts(
        summaries,
        task_a=task_a,
        task_b=task_b,
        participant_col=participant_col,
        task_col=task_col,
        participants=cohort,
    )
    finite = contrasts["paired_complete"].to_numpy(dtype=bool)
    coverage = float(np.mean(finite))
    values = contrasts.loc[finite, "task_contrast"].to_numpy(dtype=float)
    effect = float(np.median(values)) if values.size else np.nan
    return summaries, contrasts, effect, coverage


def audit_detector_robustness(
    reference_samples: pd.DataFrame,
    detector_samples: Mapping[str, pd.DataFrame] | Iterable[tuple[str, pd.DataFrame]],
    *,
    expected_detectors: Sequence[str],
    task_a: Any,
    task_b: Any,
    rule: ConclusionRule,
    minimum_coverage_fraction: float = 0.95,
    participant_col: str = "participant",
    task_col: str = "task",
    timestamp_col: str = "timestamp",
    label_col: str = "event_label",
    fixation_labels: Iterable[Any] = ("fixation",),
) -> DetectorRobustnessAudit:
    """Run a fail-closed multi-detector task-contrast audit.

    The participant cohort and reference effect are constructed exclusively from
    ``reference_samples``. Every detector is evaluated over that fixed
    denominator. Missing, duplicate, or unexpected detector identities are
    rejected before endpoint aggregation.

    If any detector falls below ``minimum_coverage_fraction`` the final
    classification is ``"incomplete"`` and no robust/fragile recovery summary
    is issued.
    """

    if not np.isfinite(minimum_coverage_fraction) or not (
        0.0 <= minimum_coverage_fraction <= 1.0
    ):
        raise ValueError("minimum_coverage_fraction must be between 0 and 1")

    expected = tuple(expected_detectors)
    if not expected:
        raise ValueError("expected_detectors must contain at least one detector")
    if len(set(expected)) != len(expected):
        raise ValueError("expected_detectors must not contain duplicates")

    named_detectors = _normalize_detector_inputs(detector_samples)
    actual_names = tuple(named_detectors)
    missing = [name for name in expected if name not in named_detectors]
    unexpected = [name for name in actual_names if name not in expected]
    if missing or unexpected:
        raise ValueError(
            f"detector set does not match predeclared specification space; "
            f"missing={missing}, unexpected={unexpected}"
        )

    fixed_cohort, reference_tasks, reference_contrasts, reference_effect = (
        fixed_reference_cohort(
            reference_samples,
            task_a=task_a,
            task_b=task_b,
            participant_col=participant_col,
            task_col=task_col,
            timestamp_col=timestamp_col,
            label_col=label_col,
            fixation_labels=fixation_labels,
        )
    )
    if reference_effect == 0.0:
        raise ValueError(
            "reference effect is exactly zero; relative-error recovery is undefined "
            "for the frozen protocol"
        )

    task_frames: list[pd.DataFrame] = []
    contrast_frames: list[pd.DataFrame] = []
    coverage_rows: list[dict[str, Any]] = []
    effect_rows: list[dict[str, Any]] = []

    for detector in expected:
        task_summary, contrasts, effect, coverage = detector_task_contrast(
            named_detectors[detector],
            fixed_cohort,
            task_a=task_a,
            task_b=task_b,
            participant_col=participant_col,
            task_col=task_col,
            timestamp_col=timestamp_col,
            label_col=label_col,
            fixation_labels=fixation_labels,
        )
        task_summary = task_summary.copy()
        task_summary.insert(0, "detector", detector)
        contrasts = contrasts.copy()
        contrasts.insert(0, "detector", detector)
        task_frames.append(task_summary)
        contrast_frames.append(contrasts)
        coverage_rows.append(
            {
                "detector": detector,
                "n_fixed_cohort": len(fixed_cohort),
                "n_paired_complete": int(contrasts["paired_complete"].sum()),
                "coverage_fraction": coverage,
                "coverage_passed": bool(coverage >= minimum_coverage_fraction),
            }
        )
        effect_rows.append({"detector": detector, "estimate": effect})

    detector_tasks = pd.concat(task_frames, ignore_index=True)
    detector_contrasts = pd.concat(contrast_frames, ignore_index=True)
    coverage_table = pd.DataFrame(coverage_rows)
    effects = pd.DataFrame(effect_rows)
    complete = bool(coverage_table["coverage_passed"].all())

    recovery: pd.DataFrame | None = None
    summary_data: dict[str, Any] = {
        "n_detectors": len(expected),
        "fixed_cohort_size": len(fixed_cohort),
        "minimum_coverage_fraction": float(minimum_coverage_fraction),
        "minimum_observed_coverage": float(coverage_table["coverage_fraction"].min()),
        "completeness_passed": complete,
    }

    if not complete:
        summary_data["classification"] = "incomplete"
    else:
        if np.any(~np.isfinite(effects["estimate"].to_numpy(dtype=float))):
            raise RuntimeError(
                "completeness passed but at least one detector effect is non-finite"
            )
        recovery = conclusion_recovery_table(
            effects,
            reference_effect,
            rule,
            estimate_col="estimate",
        )
        recovery_summary = summarize_conclusion_recovery(recovery, rule)
        summary_data.update(recovery_summary.to_dict())

    return DetectorRobustnessAudit(
        fixed_cohort=fixed_cohort,
        reference_participant_tasks=reference_tasks,
        reference_contrasts=reference_contrasts,
        reference_effect=reference_effect,
        detector_participant_tasks=detector_tasks,
        detector_contrasts=detector_contrasts,
        coverage=coverage_table,
        effects=effects,
        recovery=recovery,
        summary=pd.Series(summary_data),
    )


def _paired_task_contrasts(
    summaries: pd.DataFrame,
    *,
    task_a: Any,
    task_b: Any,
    participant_col: str,
    task_col: str,
    participants: Sequence[Any] | None = None,
) -> pd.DataFrame:
    if task_a == task_b:
        raise ValueError("task_a and task_b must differ")

    if summaries.empty:
        pivot = pd.DataFrame(columns=[task_a, task_b])
        pivot.index.name = participant_col
    else:
        duplicate = summaries.duplicated([participant_col, task_col], keep=False)
        if duplicate.any():
            raise ValueError("participant-task summaries must be unique")
        pivot = summaries.pivot(
            index=participant_col,
            columns=task_col,
            values="median_fixation_duration",
        )

    if participants is None:
        participant_order = list(pivot.index)
    else:
        participant_order = list(participants)
    pivot = pivot.reindex(index=participant_order, columns=[task_a, task_b])

    output = pivot.rename(
        columns={task_a: "task_a_median", task_b: "task_b_median"}
    ).reset_index()
    task_a_values = pd.to_numeric(output["task_a_median"], errors="coerce").to_numpy(dtype=float)
    task_b_values = pd.to_numeric(output["task_b_median"], errors="coerce").to_numpy(dtype=float)
    paired = np.isfinite(task_a_values) & np.isfinite(task_b_values)
    output["paired_complete"] = paired
    output["task_contrast"] = np.where(paired, task_a_values - task_b_values, np.nan)
    return output


def _normalize_detector_inputs(
    detector_samples: Mapping[str, pd.DataFrame] | Iterable[tuple[str, pd.DataFrame]],
) -> dict[str, pd.DataFrame]:
    items = (
        list(detector_samples.items())
        if isinstance(detector_samples, Mapping)
        else list(detector_samples)
    )
    normalized: dict[str, pd.DataFrame] = {}
    for name, samples in items:
        if not isinstance(name, str) or not name:
            raise ValueError("detector names must be non-empty strings")
        if name in normalized:
            raise ValueError(f"duplicate detector identity: {name!r}")
        if not isinstance(samples, pd.DataFrame):
            raise TypeError(f"detector {name!r} samples must be a pandas DataFrame")
        normalized[name] = samples
    return normalized


def _normalize_label(value: Any) -> str:
    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        return name.strip().lower()
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def _require_columns(data: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"data are missing required columns: {missing}")
