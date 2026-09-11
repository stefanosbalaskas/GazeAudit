"""Frozen-protocol execution support for the GazeBase multi-detector case study.

This module binds real-data execution to the scientific protocol frozen before
alternative-detector outcomes were inspected. It intentionally fails closed on
protocol drift, software-version drift, detector-set drift, incomplete detector
coverage, and a zero external-reference effect.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib import resources
from importlib.metadata import PackageNotFoundError, version as package_version
from typing import Any

import numpy as np
import pandas as pd
from packaging.version import InvalidVersion, Version

from .conclusion import ConclusionRule
from .peyes_adapter import make_peyes_detector, run_peyes_detector
from .provenance import fingerprint
from .publication import (
    PublicationAuditBundle,
    build_conclusion_audit_bundle,
    verify_publication_audit_bundle,
)
from .pymovements_adapter import PymovementsGazeAdapter
from .study import GazeStudy
from .task_contrast import (
    DetectorRobustnessAudit,
    audit_detector_robustness,
    fixed_reference_cohort,
)

GAZEBASE_PROTOCOL_FINGERPRINT = (
    "3f64122f62cbc9762b0bd0e0b95c7fef6ff40c4700215ee4b90f005af77003b1"
)
GAZEBASE_CASE_STUDY_ID = "gazebase-r1s1-fxs-vs-tex-multidetector-v1"
GAZEBASE_ARCHIVE_MD5 = "cb7eb895fb48f8661decf038ab998c9a"
GAZEBASE_TASKS = ("FXS", "TEX")
GAZEBASE_DETECTORS = ("ivt", "ivvt", "idt", "idvt", "engbert", "nh", "remodnav")
GAZEBASE_REFERENCE_LABEL_COLUMN = "reference_event_label"


@dataclass(frozen=True)
class PreparedGazeBaseData:
    """Canonical GazeBase subset plus deterministic, path-independent source identity."""

    study: GazeStudy
    source_identity: dict[str, Any]


@dataclass(frozen=True)
class GazeBaseExecution:
    """Auditable output of one frozen GazeBase multi-detector execution."""

    protocol: dict[str, Any]
    protocol_fingerprint: str
    audit: DetectorRobustnessAudit
    detector_parameters: dict[str, dict[str, Any]]
    software_versions: dict[str, str]
    cohort_fingerprint: str
    source_identity: dict[str, Any]
    publication_bundle: PublicationAuditBundle | None
    execution_manifest: dict[str, Any]

    @property
    def execution_fingerprint(self) -> str:
        """Return the deterministic identity of the execution manifest."""

        return str(self.execution_manifest["execution_fingerprint"])


def load_gazebase_protocol() -> dict[str, Any]:
    """Load the frozen protocol copy shipped inside the installed package."""

    text = (
        resources.files("gazeaudit.data")
        .joinpath("gazebase_multidetector_protocol.json")
        .read_text(encoding="utf-8")
    )
    document = json.loads(text)
    if not isinstance(document, dict):
        raise ValueError("packaged GazeBase protocol must be a JSON object")
    return document


def verify_gazebase_protocol(
    document: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify the immutable scientific identity and critical guardrails."""

    loaded = load_gazebase_protocol() if document is None else dict(document)
    if loaded.get("protocol_fingerprint") != GAZEBASE_PROTOCOL_FINGERPRINT:
        raise ValueError("GazeBase protocol declares an unexpected fingerprint")
    protocol = loaded.get("protocol")
    if not isinstance(protocol, Mapping):
        raise ValueError("GazeBase protocol document is missing the protocol object")
    protocol = dict(protocol)
    if fingerprint(protocol) != GAZEBASE_PROTOCOL_FINGERPRINT:
        raise ValueError("GazeBase protocol content does not match its frozen fingerprint")

    dataset = protocol.get("dataset", {})
    detector_space = protocol.get("detector_space", {})
    completeness = protocol.get("completeness_gate", {})
    rule = protocol.get("conclusion_rule", {})
    expected_checks = {
        "case_study_id": protocol.get("case_study_id") == GAZEBASE_CASE_STUDY_ID,
        "round": dataset.get("round") == 1,
        "session": dataset.get("session") == 1,
        "tasks": tuple(dataset.get("tasks", ())) == GAZEBASE_TASKS,
        "detectors": tuple(detector_space.get("algorithms", ())) == GAZEBASE_DETECTORS,
        "coverage": completeness.get("minimum_finite_participant_fraction_per_detector")
        == 0.95,
        "relative_tolerance": rule.get("relative_tolerance") == 0.20,
        "minimum_recovery_fraction": rule.get("minimum_recovery_fraction") == 6 / 7,
        "minimum_recovered_detectors": rule.get("minimum_recovered_detectors") == 6,
        "uses_p_values": rule.get("uses_p_values") is False,
        "no_retuning": detector_space.get("post_hoc_retuning_allowed") is False,
        "no_removal": detector_space.get("post_hoc_detector_removal_allowed") is False,
    }
    failed = [name for name, passed in expected_checks.items() if not passed]
    if failed:
        raise ValueError(f"GazeBase protocol failed frozen guardrails: {failed}")
    return protocol


def prepare_gazebase_pymovements_dataset(dataset: Any) -> PreparedGazeBaseData:
    """Prepare the already-loaded frozen GazeBase subset from pymovements.

    The caller must load only Round 1 / Session 1 / FXS and TEX, for example::

        dataset.load(
            subset={"round_id": 1, "session_id": 1, "task_name": ["FXS", "TEX"]}
        )

    Pixel coordinates are generated with ``Dataset.deg2pix`` only when absent.
    EyeLink parser labels are retained separately as the external reference.
    """

    protocol = verify_gazebase_protocol()
    recordings = list(getattr(dataset, "gaze", ()) or ())
    if not recordings:
        raise ValueError("dataset.gaze must contain the loaded GazeBase subset")

    fileinfo = _to_pandas_frame(getattr(dataset, "fileinfo", None), "dataset.fileinfo")
    required_fileinfo = {"round_id", "subject_id", "session_id", "task_name"}
    missing = sorted(required_fileinfo.difference(fileinfo.columns))
    if missing:
        raise ValueError(f"GazeBase fileinfo is missing required columns: {missing}")
    if len(fileinfo) != len(recordings):
        raise ValueError("GazeBase fileinfo rows must align one-to-one with dataset.gaze")

    rounds = set(pd.to_numeric(fileinfo["round_id"], errors="coerce").dropna().astype(int))
    sessions = set(pd.to_numeric(fileinfo["session_id"], errors="coerce").dropna().astype(int))
    tasks = set(fileinfo["task_name"].astype(str))
    if rounds != {1} or sessions != {1} or not tasks or not tasks.issubset(set(GAZEBASE_TASKS)):
        raise ValueError(
            "loaded GazeBase data must contain only Round 1 / Session 1 / FXS and TEX"
        )
    if not set(GAZEBASE_TASKS).issubset(tasks):
        raise ValueError("loaded GazeBase subset must contain both FXS and TEX recordings")

    if any("pixel" not in _sample_columns(recording) for recording in recordings):
        deg2pix = getattr(dataset, "deg2pix", None)
        if not callable(deg2pix):
            raise TypeError("dataset must expose deg2pix() when pixel coordinates are absent")
        deg2pix(
            pixel_origin="upper left",
            position_column="position",
            pixel_column="pixel",
            verbose=False,
        )
        recordings = list(getattr(dataset, "gaze", ()) or ())
    if any("pixel" not in _sample_columns(recording) for recording in recordings):
        raise ValueError("pymovements deg2pix did not produce the required 'pixel' coordinate")

    frames: list[pd.DataFrame] = []
    source_files: list[dict[str, Any]] = []
    for index, (recording, info) in enumerate(
        zip(recordings, fileinfo.to_dict(orient="records"), strict=True)
    ):
        participant = _python_scalar(info["subject_id"])
        task = str(info["task_name"])
        canonical = PymovementsGazeAdapter(
            coordinate="pixel",
            component="auto",
            participant_id=participant,
            trial_columns=(),
            numeric_time_unit="ms",
        ).to_study(recording)
        raw = _to_pandas_frame(getattr(recording, "samples", None), "recording.samples")
        if "lab" not in raw.columns:
            raise ValueError("GazeBase source samples must contain EyeLink parser column 'lab'")
        if len(raw) != len(canonical.data):
            raise ValueError("reference labels must align one-to-one with canonical gaze samples")

        frame = canonical.data.copy()
        frame["trial"] = task
        frame[GAZEBASE_REFERENCE_LABEL_COLUMN] = raw["lab"].map(_reference_label).to_numpy()
        frames.append(frame)

        filename = _portable_basename(info.get("filepath", info.get("filename", f"recording_{index}")))
        source_files.append(
            {
                "subject_id": participant,
                "task": task,
                "filename": filename,
            }
        )

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(
        ["participant", "trial", "timestamp"],
        kind="stable",
    ).reset_index(drop=True)
    study = GazeStudy(combined)

    ordered_files = sorted(
        source_files,
        key=lambda item: (str(item["subject_id"]), item["task"], item["filename"]),
    )
    source_identity = {
        "dataset": "GazeBase",
        "dataset_version": protocol["dataset"]["version"],
        "paper_doi": protocol["dataset"]["paper_doi"],
        "data_doi": protocol["dataset"]["data_doi"],
        "catalog_archive_md5": GAZEBASE_ARCHIVE_MD5,
        "round": 1,
        "session": 1,
        "tasks": list(GAZEBASE_TASKS),
        "selected_file_count": len(ordered_files),
        "selected_files_fingerprint": fingerprint(ordered_files),
    }
    return PreparedGazeBaseData(study=study, source_identity=source_identity)


def verify_gazebase_software_versions(
    version_getter: Callable[[str], str] | None = None,
) -> dict[str, str]:
    """Require the exact frozen interoperability versions before execution."""

    getter = package_version if version_getter is None else version_getter
    names = {"pymovements": "pymovements", "peyes": "pEYES", "gazeaudit": "gazeaudit"}
    found: dict[str, str] = {}
    for key, distribution in names.items():
        try:
            found[key] = str(getter(distribution))
        except PackageNotFoundError as exc:
            raise RuntimeError(f"required execution dependency is not installed: {distribution}") from exc

    if found["pymovements"] != "0.28.0":
        raise RuntimeError("frozen GazeBase execution requires pymovements==0.28.0")
    if found["peyes"] != "0.2.2":
        raise RuntimeError("frozen GazeBase execution requires pEYES==0.2.2")
    try:
        if Version(found["gazeaudit"]) < Version("0.1.0.dev7"):
            raise RuntimeError("frozen GazeBase execution requires GazeAudit>=0.1.0.dev7")
    except InvalidVersion as exc:
        raise RuntimeError("installed GazeAudit version is not PEP 440 compatible") from exc
    return found


def run_gazebase_multidetector_execution(
    prepared: PreparedGazeBaseData,
    *,
    gazeaudit_commit: str,
    protocol_document: Mapping[str, Any] | None = None,
    detector_factory: Callable[..., Any] = make_peyes_detector,
    detector_runner: Callable[..., Any] = run_peyes_detector,
    version_getter: Callable[[str], str] | None = None,
) -> GazeBaseExecution:
    """Execute the frozen seven-detector GazeBase robustness protocol.

    Protocol, source, commit, and software checks all occur before a detector is
    constructed. The EyeLink reference cohort and reference effect are also
    computed before alternative-detector construction, ensuring that a zero
    reference effect fails before detector-output inspection.
    """

    if not isinstance(prepared, PreparedGazeBaseData):
        raise TypeError("prepared must be PreparedGazeBaseData")
    protocol = verify_gazebase_protocol(protocol_document)
    _validate_commit(gazeaudit_commit)
    source_identity = _validate_source_identity(prepared.source_identity, protocol)
    software_versions = verify_gazebase_software_versions(version_getter)
    _validate_execution_study(prepared.study)

    reference_samples = prepared.study.data[
        ["participant", "trial", "timestamp", GAZEBASE_REFERENCE_LABEL_COLUMN]
    ].rename(
        columns={
            "trial": "task",
            GAZEBASE_REFERENCE_LABEL_COLUMN: "event_label",
        }
    )
    fixed_cohort, _, _, reference_effect = fixed_reference_cohort(
        reference_samples,
        task_a=GAZEBASE_TASKS[0],
        task_b=GAZEBASE_TASKS[1],
    )
    if reference_effect == 0.0:
        raise ValueError(
            "reference effect is exactly zero; frozen relative-error protocol must stop "
            "before alternative-detector execution"
        )

    detector_space = protocol["detector_space"]
    shared = detector_space["shared_parameters"]
    detector_parameters: dict[str, dict[str, Any]] = {}
    detector_samples: dict[str, pd.DataFrame] = {}

    for algorithm in GAZEBASE_DETECTORS:
        detector = detector_factory(
            algorithm,
            missing_value=np.nan,
            min_event_duration=float(shared["min_event_duration_ms"]),
            pad_blinks_time=float(shared["pad_blinks_time_ms"]),
            name=algorithm,
        )
        defaults_getter = getattr(detector, "get_default_params", None)
        if not callable(defaults_getter):
            raise TypeError(
                f"detector {algorithm!r} must expose get_default_params() for frozen provenance"
            )
        defaults = defaults_getter()
        if not isinstance(defaults, Mapping):
            raise TypeError(f"detector {algorithm!r} defaults must be a mapping")
        detector_parameters[algorithm] = {
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
                protocol["coordinate_conversion"]["peyes_viewer_distance_cm"]
            ),
            pixel_size_cm=float(protocol["coordinate_conversion"]["peyes_pixel_size_cm"]),
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
        detector_samples[algorithm] = samples[
            ["participant", "trial", "timestamp", "event_label"]
        ].rename(columns={"trial": "task"})

    frozen_rule = _conclusion_rule(protocol)
    audit = audit_detector_robustness(
        reference_samples,
        detector_samples,
        expected_detectors=GAZEBASE_DETECTORS,
        task_a=GAZEBASE_TASKS[0],
        task_b=GAZEBASE_TASKS[1],
        rule=frozen_rule,
        minimum_coverage_fraction=float(
            protocol["completeness_gate"]["minimum_finite_participant_fraction_per_detector"]
        ),
    )
    if tuple(audit.fixed_cohort) != tuple(fixed_cohort):
        raise RuntimeError("detector audit changed the frozen reference-defined cohort")
    if audit.reference_effect != reference_effect:
        raise RuntimeError("detector audit changed the frozen external-reference effect")

    cohort_fingerprint = fingerprint(list(audit.fixed_cohort))
    metadata = {
        "case_study_id": GAZEBASE_CASE_STUDY_ID,
        "protocol_fingerprint": GAZEBASE_PROTOCOL_FINGERPRINT,
        "gazeaudit_commit": gazeaudit_commit,
        "software_versions": software_versions,
        "source_identity": source_identity,
        "cohort_size": len(audit.fixed_cohort),
        "cohort_fingerprint": cohort_fingerprint,
        "detector_parameters": detector_parameters,
        "coordinate_conversion": protocol["coordinate_conversion"],
        "missingness": protocol["missingness"],
        "coverage_fingerprint": fingerprint(_frame_records(audit.coverage)),
    }

    publication_bundle: PublicationAuditBundle | None = None
    if bool(audit.summary["completeness_passed"]):
        publication_bundle = build_conclusion_audit_bundle(
            audit.effects,
            audit.reference_effect,
            frozen_rule,
            title="GazeBase multi-detector inferential-robustness audit",
            endpoint=str(protocol["endpoint"]["name"]),
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
        "gazeaudit_commit": gazeaudit_commit,
        "software_versions": software_versions,
        "source_identity": source_identity,
        "coordinate_conversion": protocol["coordinate_conversion"],
        "missingness": protocol["missingness"],
        "endpoint": protocol["endpoint"],
        "detector_parameters": detector_parameters,
        "fixed_cohort_size": len(audit.fixed_cohort),
        "fixed_cohort_fingerprint": cohort_fingerprint,
        "reference_effect": audit.reference_effect,
        "coverage": _frame_records(audit.coverage),
        "effects": _frame_records(audit.effects),
        "recovery": None if audit.recovery is None else _frame_records(audit.recovery),
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
        protocol=protocol,
        protocol_fingerprint=GAZEBASE_PROTOCOL_FINGERPRINT,
        audit=audit,
        detector_parameters=detector_parameters,
        software_versions=software_versions,
        cohort_fingerprint=cohort_fingerprint,
        source_identity=source_identity,
        publication_bundle=publication_bundle,
        execution_manifest=execution_manifest,
    )


def _conclusion_rule(protocol: Mapping[str, Any]) -> ConclusionRule:
    rule = protocol["conclusion_rule"]
    return ConclusionRule(
        relative_tolerance=float(rule["relative_tolerance"]),
        absolute_tolerance=rule["absolute_tolerance"],
        require_sign=bool(rule["require_sign"]),
        minimum_recovery_fraction=float(rule["minimum_recovery_fraction"]),
    )


def _validate_commit(value: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ValueError("gazeaudit_commit must be an exact 40-character lowercase Git SHA")


def _validate_source_identity(
    source: Mapping[str, Any],
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(source, Mapping) or not source:
        raise ValueError("source_identity must be a non-empty mapping")
    normalized = _safe_mapping(source)
    dataset = protocol["dataset"]
    required = {
        "dataset": "GazeBase",
        "data_doi": dataset["data_doi"],
        "round": 1,
        "session": 1,
        "tasks": list(GAZEBASE_TASKS),
    }
    mismatched = [key for key, expected in required.items() if normalized.get(key) != expected]
    if mismatched:
        raise ValueError(f"source_identity does not match frozen GazeBase protocol: {mismatched}")
    archive = normalized.get("catalog_archive_md5")
    if archive is not None and archive != GAZEBASE_ARCHIVE_MD5:
        raise ValueError("source_identity contains an unexpected GazeBase archive MD5")
    return normalized


def _validate_execution_study(study: GazeStudy) -> None:
    if not isinstance(study, GazeStudy):
        raise TypeError("prepared.study must be a GazeStudy")
    study.require_columns([GAZEBASE_REFERENCE_LABEL_COLUMN])
    tasks = set(study.data[study.trial].astype(str))
    if tasks != set(GAZEBASE_TASKS):
        raise ValueError("execution study must contain exactly the frozen FXS and TEX tasks")


def _reference_label(value: Any) -> str:
    if pd.isna(value):
        return "undefined"
    try:
        numeric = int(value)
    except (TypeError, ValueError):
        return "undefined"
    return {1: "fixation", 2: "saccade", -1: "blink"}.get(numeric, "undefined")


def _sample_columns(recording: Any) -> set[str]:
    samples = getattr(recording, "samples", None)
    if isinstance(samples, pd.DataFrame):
        return {str(column) for column in samples.columns}
    columns = getattr(samples, "columns", None)
    if columns is None:
        return set()
    return {str(column) for column in columns}


def _to_pandas_frame(value: Any, name: str) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value.copy()
    to_pandas = getattr(value, "to_pandas", None)
    if not callable(to_pandas):
        raise TypeError(f"{name} must be a pandas DataFrame or expose to_pandas()")
    frame = to_pandas()
    if not isinstance(frame, pd.DataFrame):
        raise TypeError(f"{name}.to_pandas() must return a pandas DataFrame")
    return frame


def _portable_basename(value: Any) -> str:
    text = str(value)
    return text.replace("\\", "/").rsplit("/", 1)[-1]


def _python_scalar(value: Any) -> Any:
    return value.item() if isinstance(value, np.generic) else value


def _frame_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [_safe_mapping(record) for record in frame.to_dict(orient="records")]


def _safe_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): _safe_value(item) for key, item in value.items()}


def _safe_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, np.generic):
        return _safe_value(value.item())
    if isinstance(value, float):
        return value if np.isfinite(value) else None
    if isinstance(value, Mapping):
        return _safe_mapping(value)
    if isinstance(value, (list, tuple)):
        return [_safe_value(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_safe_value(item) for item in value.tolist()]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if pd.isna(value):
        return None
    raise TypeError(f"unsupported GazeBase provenance type: {type(value).__name__}")
