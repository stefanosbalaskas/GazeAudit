"""Partitioned execution for the frozen GazeBase multi-detector case study.

This module preserves the frozen scientific protocol while allowing each of the
seven predeclared detector families to run independently. It exists so long
real-data computations can survive infrastructure limits without changing the
cohort, endpoint, detector set, completeness gate, or conclusion rule.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .conclusion import conclusion_recovery_table, summarize_conclusion_recovery
from .gazebase_execution import (
    GAZEBASE_CASE_STUDY_ID,
    GAZEBASE_DETECTORS,
    GAZEBASE_PROTOCOL_FINGERPRINT,
    GAZEBASE_REFERENCE_LABEL_COLUMN,
    GAZEBASE_TASKS,
    GazeBaseExecution,
    PreparedGazeBaseData,
    _conclusion_rule,
    _frame_records,
    _safe_mapping,
    _validate_commit,
    _validate_execution_study,
    _validate_source_identity,
    verify_gazebase_protocol,
    verify_gazebase_software_versions,
)
from .peyes_adapter import make_peyes_detector, run_peyes_detector
from .provenance import canonical_json, fingerprint
from .publication import build_conclusion_audit_bundle, verify_publication_audit_bundle
from .task_contrast import DetectorRobustnessAudit, detector_task_contrast, fixed_reference_cohort

PARTITION_SCHEMA = "gazeaudit-gazebase-detector-partition-v1"


@dataclass(frozen=True)
class GazeBaseExecutionContext:
    """Frozen reference-defined state shared by all detector partitions."""

    protocol: dict[str, Any]
    gazeaudit_commit: str
    software_versions: dict[str, str]
    source_identity: dict[str, Any]
    reference_samples: pd.DataFrame
    fixed_cohort: tuple[Any, ...]
    reference_participant_tasks: pd.DataFrame
    reference_contrasts: pd.DataFrame
    reference_effect: float
    cohort_fingerprint: str
    context_fingerprint: str


@dataclass(frozen=True)
class GazeBaseDetectorPartition:
    """Compact auditable result for one predeclared detector family."""

    algorithm: str
    detector_parameters: dict[str, Any]
    participant_tasks: pd.DataFrame
    contrasts: pd.DataFrame
    effect: float
    coverage: float
    context_fingerprint: str
    partition_fingerprint: str


def prepare_gazebase_execution_context(
    prepared: PreparedGazeBaseData,
    *,
    gazeaudit_commit: str,
    protocol_document: Mapping[str, Any] | None = None,
    version_getter: Callable[[str], str] | None = None,
) -> GazeBaseExecutionContext:
    """Freeze all reference-only state before any alternative detector executes."""

    if not isinstance(prepared, PreparedGazeBaseData):
        raise TypeError("prepared must be PreparedGazeBaseData")
    protocol = verify_gazebase_protocol(protocol_document)
    _validate_commit(gazeaudit_commit)
    source_identity = _validate_source_identity(prepared.source_identity, protocol)
    software_versions = verify_gazebase_software_versions(version_getter)
    _validate_execution_study(prepared.study)

    reference_samples = prepared.study.data[
        ["participant", "trial", "timestamp", GAZEBASE_REFERENCE_LABEL_COLUMN]
    ].rename(columns={"trial": "task", GAZEBASE_REFERENCE_LABEL_COLUMN: "event_label"})
    cohort, reference_tasks, reference_contrasts, reference_effect = fixed_reference_cohort(
        reference_samples,
        task_a=GAZEBASE_TASKS[0],
        task_b=GAZEBASE_TASKS[1],
    )
    if reference_effect == 0.0:
        raise ValueError(
            "reference effect is exactly zero; frozen relative-error protocol must stop "
            "before alternative-detector execution"
        )

    cohort_fingerprint = fingerprint(list(cohort))
    identity = {
        "schema": "gazeaudit-gazebase-execution-context-v1",
        "protocol_fingerprint": GAZEBASE_PROTOCOL_FINGERPRINT,
        "gazeaudit_commit": gazeaudit_commit,
        "software_versions": software_versions,
        "source_identity": source_identity,
        "fixed_cohort": list(cohort),
        "cohort_fingerprint": cohort_fingerprint,
        "reference_effect": reference_effect,
    }
    return GazeBaseExecutionContext(
        protocol=protocol,
        gazeaudit_commit=gazeaudit_commit,
        software_versions=software_versions,
        source_identity=source_identity,
        reference_samples=reference_samples.reset_index(drop=True),
        fixed_cohort=cohort,
        reference_participant_tasks=reference_tasks.reset_index(drop=True),
        reference_contrasts=reference_contrasts.reset_index(drop=True),
        reference_effect=reference_effect,
        cohort_fingerprint=cohort_fingerprint,
        context_fingerprint=fingerprint(identity),
    )


def run_gazebase_detector_partition(
    prepared: PreparedGazeBaseData,
    context: GazeBaseExecutionContext,
    algorithm: str,
    *,
    detector_factory: Callable[..., Any] = make_peyes_detector,
    detector_runner: Callable[..., Any] = run_peyes_detector,
) -> GazeBaseDetectorPartition:
    """Execute exactly one detector from the frozen seven-detector space."""

    if algorithm not in GAZEBASE_DETECTORS:
        raise ValueError(f"algorithm must be one of the frozen detectors: {GAZEBASE_DETECTORS}")
    _verify_context_against_prepared(prepared, context)

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
    }

    detected = detector_runner(
        prepared.study,
        detector,
        viewer_distance_cm=float(
            context.protocol["coordinate_conversion"]["peyes_viewer_distance_cm"]
        ),
        pixel_size_cm=float(context.protocol["coordinate_conversion"]["peyes_pixel_size_cm"]),
        timestamp_unit="ms",
        coordinate_unit="px",
    )
    samples = getattr(detected, "samples", None)
    if not isinstance(samples, pd.DataFrame):
        raise TypeError("detector runner must return an object with pandas DataFrame samples")
    required = {"participant", "trial", "timestamp", "event_label"}
    missing = sorted(required.difference(samples.columns))
    if missing:
        raise ValueError(f"detector output is missing required columns: {missing}")
    detector_samples = samples[["participant", "trial", "timestamp", "event_label"]].rename(
        columns={"trial": "task"}
    )
    task_summary, contrasts, effect, coverage = detector_task_contrast(
        detector_samples,
        context.fixed_cohort,
        task_a=GAZEBASE_TASKS[0],
        task_b=GAZEBASE_TASKS[1],
    )
    core = {
        "schema": PARTITION_SCHEMA,
        "algorithm": algorithm,
        "context_fingerprint": context.context_fingerprint,
        "detector_parameters": parameters,
        "participant_tasks": _frame_records(task_summary),
        "contrasts": _frame_records(contrasts),
        "effect": None if not np.isfinite(effect) else float(effect),
        "coverage": float(coverage),
    }
    return GazeBaseDetectorPartition(
        algorithm=algorithm,
        detector_parameters=parameters,
        participant_tasks=task_summary.reset_index(drop=True),
        contrasts=contrasts.reset_index(drop=True),
        effect=float(effect),
        coverage=float(coverage),
        context_fingerprint=context.context_fingerprint,
        partition_fingerprint=fingerprint(core),
    )


def detector_partition_document(partition: GazeBaseDetectorPartition) -> dict[str, Any]:
    """Return a canonical JSON-safe detector-partition document."""

    core = {
        "schema": PARTITION_SCHEMA,
        "algorithm": partition.algorithm,
        "context_fingerprint": partition.context_fingerprint,
        "detector_parameters": partition.detector_parameters,
        "participant_tasks": _frame_records(partition.participant_tasks),
        "contrasts": _frame_records(partition.contrasts),
        "effect": None if not np.isfinite(partition.effect) else float(partition.effect),
        "coverage": float(partition.coverage),
    }
    actual = fingerprint(core)
    if actual != partition.partition_fingerprint:
        raise ValueError("detector partition contents do not match partition_fingerprint")
    return {**core, "partition_fingerprint": actual}


def write_gazebase_detector_partition(
    partition: GazeBaseDetectorPartition,
    path: str | Path,
) -> Path:
    """Write one compact partition atomically as canonical JSON."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    payload = canonical_json(detector_partition_document(partition)) + "\n"
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(target)
    return target


def read_gazebase_detector_partition(path: str | Path) -> GazeBaseDetectorPartition:
    """Read and verify one serialized detector partition."""

    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if document.get("schema") != PARTITION_SCHEMA:
        raise ValueError("unexpected detector partition schema")
    declared = document.pop("partition_fingerprint", None)
    actual = fingerprint(document)
    if declared != actual:
        raise ValueError("detector partition fingerprint verification failed")
    effect_value = document.get("effect")
    effect = np.nan if effect_value is None else float(effect_value)
    return GazeBaseDetectorPartition(
        algorithm=str(document["algorithm"]),
        detector_parameters=dict(document["detector_parameters"]),
        participant_tasks=pd.DataFrame(document["participant_tasks"]),
        contrasts=pd.DataFrame(document["contrasts"]),
        effect=effect,
        coverage=float(document["coverage"]),
        context_fingerprint=str(document["context_fingerprint"]),
        partition_fingerprint=actual,
    )


def assemble_gazebase_partitioned_execution(
    context: GazeBaseExecutionContext,
    partitions: Mapping[str, GazeBaseDetectorPartition]
    | Iterable[GazeBaseDetectorPartition],
) -> GazeBaseExecution:
    """Assemble independently computed partitions into the frozen final audit."""

    named = _normalize_partitions(partitions)
    missing = [name for name in GAZEBASE_DETECTORS if name not in named]
    unexpected = [name for name in named if name not in GAZEBASE_DETECTORS]
    if missing or unexpected:
        raise ValueError(
            "partition detector set does not match frozen specification space; "
            f"missing={missing}, unexpected={unexpected}"
        )
    for algorithm in GAZEBASE_DETECTORS:
        partition = named[algorithm]
        if partition.context_fingerprint != context.context_fingerprint:
            raise ValueError(f"partition {algorithm!r} belongs to a different execution context")
        detector_partition_document(partition)

    task_frames: list[pd.DataFrame] = []
    contrast_frames: list[pd.DataFrame] = []
    coverage_rows: list[dict[str, Any]] = []
    effect_rows: list[dict[str, Any]] = []
    detector_parameters: dict[str, dict[str, Any]] = {}
    minimum_coverage = float(
        context.protocol["completeness_gate"]["minimum_finite_participant_fraction_per_detector"]
    )
    for algorithm in GAZEBASE_DETECTORS:
        partition = named[algorithm]
        tasks = partition.participant_tasks.copy()
        tasks.insert(0, "detector", algorithm)
        contrasts = partition.contrasts.copy()
        contrasts.insert(0, "detector", algorithm)
        task_frames.append(tasks)
        contrast_frames.append(contrasts)
        n_complete = int(pd.Series(partition.contrasts["paired_complete"]).astype(bool).sum())
        coverage_rows.append(
            {
                "detector": algorithm,
                "n_fixed_cohort": len(context.fixed_cohort),
                "n_paired_complete": n_complete,
                "coverage_fraction": float(partition.coverage),
                "coverage_passed": bool(partition.coverage >= minimum_coverage),
            }
        )
        effect_rows.append({"detector": algorithm, "estimate": float(partition.effect)})
        detector_parameters[algorithm] = partition.detector_parameters

    detector_tasks = pd.concat(task_frames, ignore_index=True)
    detector_contrasts = pd.concat(contrast_frames, ignore_index=True)
    coverage = pd.DataFrame(coverage_rows)
    effects = pd.DataFrame(effect_rows)
    complete = bool(coverage["coverage_passed"].all())
    rule = _conclusion_rule(context.protocol)
    recovery = None
    summary_data: dict[str, Any] = {
        "n_detectors": len(GAZEBASE_DETECTORS),
        "fixed_cohort_size": len(context.fixed_cohort),
        "minimum_coverage_fraction": minimum_coverage,
        "minimum_observed_coverage": float(coverage["coverage_fraction"].min()),
        "completeness_passed": complete,
    }
    if not complete:
        summary_data["classification"] = "incomplete"
    else:
        if np.any(~np.isfinite(effects["estimate"].to_numpy(dtype=float))):
            raise RuntimeError("completeness passed but at least one detector effect is non-finite")
        recovery = conclusion_recovery_table(
            effects,
            context.reference_effect,
            rule,
            estimate_col="estimate",
        )
        summary_data.update(summarize_conclusion_recovery(recovery, rule).to_dict())

    audit = DetectorRobustnessAudit(
        fixed_cohort=context.fixed_cohort,
        reference_participant_tasks=context.reference_participant_tasks.copy(),
        reference_contrasts=context.reference_contrasts.copy(),
        reference_effect=context.reference_effect,
        detector_participant_tasks=detector_tasks,
        detector_contrasts=detector_contrasts,
        coverage=coverage,
        effects=effects,
        recovery=recovery,
        summary=pd.Series(summary_data),
    )
    metadata = {
        "case_study_id": GAZEBASE_CASE_STUDY_ID,
        "protocol_fingerprint": GAZEBASE_PROTOCOL_FINGERPRINT,
        "gazeaudit_commit": context.gazeaudit_commit,
        "software_versions": context.software_versions,
        "source_identity": context.source_identity,
        "cohort_size": len(context.fixed_cohort),
        "cohort_fingerprint": context.cohort_fingerprint,
        "detector_parameters": detector_parameters,
        "coordinate_conversion": context.protocol["coordinate_conversion"],
        "missingness": context.protocol["missingness"],
        "coverage_fingerprint": fingerprint(_frame_records(coverage)),
    }
    publication_bundle = None
    if complete:
        publication_bundle = build_conclusion_audit_bundle(
            effects,
            context.reference_effect,
            rule,
            title="GazeBase multi-detector inferential-robustness audit",
            endpoint=str(context.protocol["endpoint"]["name"]),
            source_description=(
                "GazeBase Round 1 Session 1 FXS versus TEX; EyeLink real-time parser "
                "labels used as an external reference rather than biological ground truth"
            ),
            metadata=metadata,
        )
        if not verify_publication_audit_bundle(publication_bundle):
            raise RuntimeError("generated GazeBase publication bundle failed verification")

    execution_manifest: dict[str, Any] = {
        "schema": "gazeaudit-gazebase-execution-v1",
        "case_study_id": GAZEBASE_CASE_STUDY_ID,
        "protocol_fingerprint": GAZEBASE_PROTOCOL_FINGERPRINT,
        "gazeaudit_commit": context.gazeaudit_commit,
        "software_versions": context.software_versions,
        "source_identity": context.source_identity,
        "coordinate_conversion": context.protocol["coordinate_conversion"],
        "missingness": context.protocol["missingness"],
        "endpoint": context.protocol["endpoint"],
        "detector_parameters": detector_parameters,
        "fixed_cohort_size": len(context.fixed_cohort),
        "fixed_cohort_fingerprint": context.cohort_fingerprint,
        "reference_effect": context.reference_effect,
        "coverage": _frame_records(coverage),
        "effects": _frame_records(effects),
        "recovery": None if recovery is None else _frame_records(recovery),
        "classification": str(audit.summary["classification"]),
        "completeness_passed": bool(audit.summary["completeness_passed"]),
        "publication_scientific_fingerprint": (
            None if publication_bundle is None else publication_bundle.scientific_fingerprint
        ),
        "publication_bundle_fingerprint": (
            None if publication_bundle is None else publication_bundle.bundle_fingerprint
        ),
    }
    execution_manifest["execution_fingerprint"] = fingerprint(execution_manifest)
    return GazeBaseExecution(
        protocol=context.protocol,
        protocol_fingerprint=GAZEBASE_PROTOCOL_FINGERPRINT,
        audit=audit,
        detector_parameters=detector_parameters,
        software_versions=context.software_versions,
        cohort_fingerprint=context.cohort_fingerprint,
        source_identity=context.source_identity,
        publication_bundle=publication_bundle,
        execution_manifest=execution_manifest,
    )


def _verify_context_against_prepared(
    prepared: PreparedGazeBaseData,
    context: GazeBaseExecutionContext,
) -> None:
    if not isinstance(prepared, PreparedGazeBaseData):
        raise TypeError("prepared must be PreparedGazeBaseData")
    _validate_execution_study(prepared.study)
    normalized_source = _validate_source_identity(prepared.source_identity, context.protocol)
    if normalized_source != context.source_identity:
        raise ValueError("prepared source identity differs from the frozen execution context")


def _normalize_partitions(
    partitions: Mapping[str, GazeBaseDetectorPartition] | Iterable[GazeBaseDetectorPartition],
) -> dict[str, GazeBaseDetectorPartition]:
    values = list(partitions.values()) if isinstance(partitions, Mapping) else list(partitions)
    named: dict[str, GazeBaseDetectorPartition] = {}
    for partition in values:
        if not isinstance(partition, GazeBaseDetectorPartition):
            raise TypeError("partitions must contain GazeBaseDetectorPartition objects")
        if partition.algorithm in named:
            raise ValueError(f"duplicate detector partition: {partition.algorithm!r}")
        named[partition.algorithm] = partition
    return named
