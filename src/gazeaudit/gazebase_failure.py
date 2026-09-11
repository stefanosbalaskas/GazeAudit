"""Fail-closed detector execution for the frozen GazeBase case study.

A predeclared detector that cannot execute on the frozen data/missingness policy
must not be silently removed or retuned. This module converts a detector-runner
failure into an auditable zero-coverage partition so the final frozen audit can
terminate as ``incomplete`` rather than crashing before the completeness gate.

Successful detector executions are delegated unchanged to the certified
partitioned runner.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

import numpy as np
import pandas as pd

from .gazebase_execution import (
    GAZEBASE_DETECTORS,
    GAZEBASE_TASKS,
    PreparedGazeBaseData,
    _frame_records,
    _safe_mapping,
)
from .gazebase_partitioned import (
    PARTITION_SCHEMA,
    GazeBaseDetectorPartition,
    GazeBaseExecutionContext,
    _verify_context_against_prepared,
    run_gazebase_detector_partition,
)
from .peyes_adapter import make_peyes_detector
from .provenance import fingerprint
from .task_contrast import detector_task_contrast


def run_gazebase_detector_partition_fail_closed(
    prepared: PreparedGazeBaseData,
    context: GazeBaseExecutionContext,
    algorithm: str,
    *,
    detector_factory: Callable[..., Any] = make_peyes_detector,
    detector_runner: Callable[..., Any],
    catch: tuple[type[BaseException], ...] = (ValueError,),
) -> GazeBaseDetectorPartition:
    """Run one frozen detector and encode backend failure as zero coverage.

    The function preserves the exact successful path by delegating to
    :func:`run_gazebase_detector_partition`. Only detector-execution failures
    matching ``catch`` are converted to an incomplete partition. Frozen-space
    identity and context checks happen before the guarded execution and are
    never converted into detector failures.

    The failed specification remains present in the seven-detector space. Its
    participant-task summaries are missing, its effect is non-finite, and its
    coverage is zero; therefore the existing completeness gate deterministically
    classifies the assembled case study as ``incomplete`` and suppresses any
    robust/fragile recovery classification or publication bundle.
    """

    if algorithm not in GAZEBASE_DETECTORS:
        raise ValueError(f"algorithm must be one of the frozen detectors: {GAZEBASE_DETECTORS}")
    _verify_context_against_prepared(prepared, context)
    valid_catch = all(
        isinstance(item, type) and issubclass(item, BaseException) for item in catch
    )
    if not catch or not valid_catch:
        raise TypeError("catch must be a non-empty tuple of exception classes")

    try:
        return run_gazebase_detector_partition(
            prepared,
            context,
            algorithm,
            detector_factory=detector_factory,
            detector_runner=detector_runner,
        )
    except catch as exc:
        return _failed_partition(
            prepared,
            context,
            algorithm,
            detector_factory=detector_factory,
            error=exc,
        )


def _failed_partition(
    prepared: PreparedGazeBaseData,
    context: GazeBaseExecutionContext,
    algorithm: str,
    *,
    detector_factory: Callable[..., Any],
    error: BaseException,
) -> GazeBaseDetectorPartition:
    shared = context.protocol["detector_space"]["shared_parameters"]
    detector = detector_factory(
        algorithm,
        missing_value=np.nan,
        min_event_duration=float(shared["min_event_duration_ms"]),
        pad_blinks_time=float(shared["pad_blinks_time_ms"]),
        name=algorithm,
    )
    defaults_getter = getattr(detector, "get_default_params", None)
    if not callable(defaults_getter):
        raise TypeError(f"detector {algorithm!r} must expose get_default_params()")
    defaults = defaults_getter()
    if not isinstance(defaults, Mapping):
        raise TypeError(f"detector {algorithm!r} defaults must be a mapping")

    parameters = {
        "algorithm": algorithm,
        "missing_value": "NaN",
        "min_event_duration_ms": float(shared["min_event_duration_ms"]),
        "pad_blinks_time_ms": float(shared["pad_blinks_time_ms"]),
        "algorithm_specific": _safe_mapping(defaults),
        "execution_failure": {
            "policy": "mark_incomplete",
            "stage": "detector_runner",
            "exception_type": type(error).__name__,
            "message": str(error),
        },
    }

    detector_samples = prepared.study.data[["participant", "trial", "timestamp"]].copy()
    detector_samples["event_label"] = pd.Series(
        pd.NA,
        index=detector_samples.index,
        dtype="object",
    )
    detector_samples = detector_samples.rename(columns={"trial": "task"})
    task_summary, contrasts, effect, coverage = detector_task_contrast(
        detector_samples,
        context.fixed_cohort,
        task_a=GAZEBASE_TASKS[0],
        task_b=GAZEBASE_TASKS[1],
    )
    if coverage != 0.0 or np.isfinite(effect):
        raise RuntimeError(
            "failed detector partition must have zero coverage and non-finite effect"
        )

    core = {
        "schema": PARTITION_SCHEMA,
        "algorithm": algorithm,
        "context_fingerprint": context.context_fingerprint,
        "detector_parameters": parameters,
        "participant_tasks": _frame_records(task_summary),
        "contrasts": _frame_records(contrasts),
        "effect": None,
        "coverage": 0.0,
    }
    return GazeBaseDetectorPartition(
        algorithm=algorithm,
        detector_parameters=parameters,
        participant_tasks=task_summary.reset_index(drop=True),
        contrasts=contrasts.reset_index(drop=True),
        effect=float("nan"),
        coverage=0.0,
        context_fingerprint=context.context_fingerprint,
        partition_fingerprint=fingerprint(core),
    )
