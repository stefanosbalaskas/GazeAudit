"""Frozen sampling/missingness scientific execution for the Pedrotti case study.

The public-data entry points are source-lock gated.  The scientific core remains
usable with synthetic fixtures so the already-frozen endpoint and perturbation
semantics can be qualified without inspecting the real-data outcome.
"""

from __future__ import annotations

import hashlib
import json
import platform
import re
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .pedrotti_source import (
    PEDROTTI_CASE_STUDY_ID,
    PEDROTTI_PROTOCOL_FINGERPRINT,
    PedrottiSourceIntake,
    _numeric_condition,
    inspect_pedrotti_source,
    load_pedrotti_protocol,
)
from .pedrotti_source_lock import (
    PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT,
    PEDROTTI_SOURCE_LOCK_FINGERPRINT,
    verify_pedrotti_locked_intake,
    verify_pedrotti_source_lock,
)
from .provenance import canonical_json, fingerprint

PEDROTTI_EXECUTION_SCHEMA = "gazeaudit-pedrotti-scientific-execution-v1"
PEDROTTI_EXECUTION_ARTIFACT_SCHEMA = "gazeaudit-pedrotti-scientific-artifacts-v1"
PEDROTTI_EXECUTION_WORKFLOW = ".github/workflows/pedrotti-scientific-execution.yml"
_PEDROTTI_CLASSIFICATIONS = {
    "robust",
    "materially_fragile",
    "mixed",
    "incomplete",
    "indeterminate_reference_zero",
}
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class PedrottiTrial:
    """One numeric trial on the published dominant-eye sample timeline."""

    participant_id: str
    trial_index: int
    condition: str
    timestamp_ms: np.ndarray
    x: np.ndarray
    y: np.ndarray
    duration_seconds: float
    finite_mask: np.ndarray
    finite_positions: np.ndarray
    native_pair_finite: np.ndarray
    edge_distance: np.ndarray


@dataclass(frozen=True)
class PreparedPedrottiData:
    """Source-identified numeric trials ready for the frozen execution."""

    source_identity: dict[str, Any]
    trials: tuple[PedrottiTrial, ...]
    participant_ids: tuple[str, ...]


@dataclass(frozen=True)
class PedrottiScientificExecution:
    """Outcome-bearing execution held in memory until checksummed archival."""

    protocol: dict[str, Any]
    prepared: PreparedPedrottiData
    reference: dict[str, Any]
    sampling_results: tuple[dict[str, Any], ...]
    missingness_results: tuple[dict[str, Any], ...]
    family_recovery: tuple[dict[str, Any], ...]
    classification: str
    execution_manifest: dict[str, Any]

    @property
    def execution_fingerprint(self) -> str:
        return str(self.execution_manifest["execution_fingerprint"])


def make_pedrotti_trial(
    participant_id: str,
    trial_index: int,
    condition: str,
    timestamp_ms: Sequence[float],
    x: Sequence[float],
    y: Sequence[float],
) -> PedrottiTrial:
    """Validate and freeze one numeric trial representation."""

    if not isinstance(participant_id, str) or not participant_id:
        raise ValueError("participant_id must be a non-empty string")
    if not isinstance(trial_index, int) or isinstance(trial_index, bool) or trial_index < 1:
        raise ValueError("trial_index must be a positive integer")
    if condition not in {"short", "long"}:
        raise ValueError("condition must be 'short' or 'long'")

    times = np.asarray(timestamp_ms, dtype=float).copy()
    x_values = np.asarray(x, dtype=float).copy()
    y_values = np.asarray(y, dtype=float).copy()
    if times.ndim != 1 or x_values.ndim != 1 or y_values.ndim != 1:
        raise ValueError("trial arrays must be one-dimensional")
    if not (len(times) == len(x_values) == len(y_values)) or len(times) < 2:
        raise ValueError("trial arrays must have equal length of at least two samples")
    if not np.isfinite(times).all() or not np.all(np.diff(times) > 0):
        raise ValueError("trial timestamps must be finite and strictly increasing")

    duration = float((times[-1] - times[0]) / 1000.0)
    if not np.isfinite(duration) or duration <= 0:
        raise ValueError("trial source duration must be finite and positive")

    finite = np.isfinite(x_values) & np.isfinite(y_values)
    finite_positions = np.flatnonzero(finite)
    pair = finite[:-1] & finite[1:]
    distances = np.zeros(len(times) - 1, dtype=float)
    if bool(pair.any()):
        dx = x_values[1:][pair] - x_values[:-1][pair]
        dy = y_values[1:][pair] - y_values[:-1][pair]
        distances[pair] = np.hypot(dx, dy)

    for values in (times, x_values, y_values, finite, finite_positions, pair, distances):
        values.setflags(write=False)
    return PedrottiTrial(
        participant_id=participant_id,
        trial_index=trial_index,
        condition=condition,
        timestamp_ms=times,
        x=x_values,
        y=y_values,
        duration_seconds=duration,
        finite_mask=finite,
        finite_positions=finite_positions,
        native_pair_finite=pair,
        edge_distance=distances,
    )


def prepare_pedrotti_execution_data(
    source_dir: str | Path,
    intake: PedrottiSourceIntake,
) -> PreparedPedrottiData:
    """Prepare numeric trials after endpoint-blind source intake has completed."""

    if not isinstance(intake, PedrottiSourceIntake):
        raise TypeError("intake must be PedrottiSourceIntake")
    root = Path(source_dir)
    if not root.is_dir():
        raise FileNotFoundError("source_dir must exist")

    records = intake.intake_summary["participants"]
    trials: list[PedrottiTrial] = []
    participant_ids: list[str] = []
    for record in records:
        participant_id = str(record["participant_id"])
        eye = str(record["eye"])
        participant_ids.append(participant_id)
        prefix = "LEFT" if eye == "left" else "RIGHT"
        columns = [
            "TRIAL_INDEX",
            f"{prefix}_GAZE_X",
            f"{prefix}_GAZE_Y",
            "TIMESTAMP",
            "TrialTextShown",
        ]
        frame = pd.read_csv(
            root / f"{participant_id}.txt",
            usecols=columns,
            na_values=["."],
            dtype={"TrialTextShown": "string"},
            low_memory=False,
        )
        frame["TRIAL_INDEX"] = pd.to_numeric(frame["TRIAL_INDEX"], errors="raise").astype(int)
        frame["TIMESTAMP"] = pd.to_numeric(frame["TIMESTAMP"], errors="raise").astype(float)
        frame[f"{prefix}_GAZE_X"] = pd.to_numeric(
            frame[f"{prefix}_GAZE_X"], errors="coerce"
        )
        frame[f"{prefix}_GAZE_Y"] = pd.to_numeric(
            frame[f"{prefix}_GAZE_Y"], errors="coerce"
        )

        short_count = 0
        long_count = 0
        for trial_index, trial_frame in frame.groupby("TRIAL_INDEX", sort=True):
            stimulus_values = trial_frame["TrialTextShown"].drop_duplicates()
            if len(stimulus_values) != 1:
                raise ValueError(
                    f"participant {participant_id} trial {trial_index} has unstable stimulus"
                )
            condition = _numeric_condition(stimulus_values.iloc[0])
            if condition is None:
                continue
            short_count += int(condition == "short")
            long_count += int(condition == "long")
            trials.append(
                make_pedrotti_trial(
                    participant_id,
                    int(trial_index),
                    condition,
                    trial_frame["TIMESTAMP"].to_numpy(dtype=float),
                    trial_frame[f"{prefix}_GAZE_X"].to_numpy(dtype=float),
                    trial_frame[f"{prefix}_GAZE_Y"].to_numpy(dtype=float),
                )
            )
        if short_count != int(record["short_numeric_trial_count"]):
            raise ValueError(f"participant {participant_id} short-numeric trial count drifted")
        if long_count != int(record["long_numeric_trial_count"]):
            raise ValueError(f"participant {participant_id} long-numeric trial count drifted")

    source_identity = {
        "case_study_id": PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": intake.source_manifest[
            "source_manifest_fingerprint"
        ],
        "participant_count": int(intake.intake_summary["participant_count"]),
        "source_file_count": int(intake.intake_summary["source_file_count"]),
        "total_row_count": int(intake.intake_summary["total_row_count"]),
        "total_trial_count": int(intake.intake_summary["total_trial_count"]),
        "short_numeric_trial_count": int(
            intake.intake_summary["short_numeric_trial_count"]
        ),
        "long_numeric_trial_count": int(
            intake.intake_summary["long_numeric_trial_count"]
        ),
        "numeric_trial_count": len(trials),
        "eye_counts": dict(intake.intake_summary["eye_counts"]),
        "scientific_endpoint_evaluated_before_preparation": False,
    }
    prepared = PreparedPedrottiData(
        source_identity=source_identity,
        trials=tuple(trials),
        participant_ids=tuple(participant_ids),
    )
    _validate_prepared(prepared)
    return prepared


def prepare_pedrotti_locked_execution_data(
    source_dir: str | Path,
    *,
    lock_document: Mapping[str, Any] | None = None,
) -> PreparedPedrottiData:
    """Prepare the real published source only after its endpoint-blind lock passes."""

    intake = inspect_pedrotti_source(source_dir)
    verify_pedrotti_locked_intake(intake, lock_document=lock_document)
    prepared = prepare_pedrotti_execution_data(source_dir, intake)
    _verify_locked_prepared(prepared, lock_document=lock_document)
    return prepared


def run_pedrotti_scientific_execution(
    prepared: PreparedPedrottiData,
    *,
    protocol_document: Mapping[str, Any] | None = None,
) -> PedrottiScientificExecution:
    """Execute the frozen endpoint and perturbation grid on prepared data."""

    _validate_prepared(prepared)
    protocol = _verified_protocol(protocol_document)
    reference_estimate, participant_reference = _study_estimate(
        prepared,
        lambda trial: _trial_rate_native(trial),
    )
    reference = {
        "study_estimate": reference_estimate,
        "participant_contrasts": participant_reference,
        "unit": protocol["endpoint"]["unit"],
    }

    sampling_results: list[dict[str, Any]] = []
    for target_hz in protocol["sampling"]["target_hz"]:
        estimate, _ = _study_estimate(
            prepared,
            lambda trial, hz=float(target_hz): _trial_rate_sampled(trial, hz),
        )
        diagnostic = _recovery_diagnostic(reference_estimate, estimate, protocol)
        sampling_results.append(
            {
                "target_hz": float(target_hz),
                "estimate": estimate,
                **diagnostic,
            }
        )

    missingness_results: list[dict[str, Any]] = []
    missingness = protocol["missingness"]
    root_seed = int(missingness["rng_seed"])
    for mechanism in missingness["mechanisms"]:
        for fraction in missingness["fractions"]:
            for replicate in range(1, int(missingness["replicates"]) + 1):
                estimate, _ = _study_estimate(
                    prepared,
                    lambda trial, mech=str(mechanism), frac=float(fraction), rep=replicate: (
                        _trial_rate_missingness(
                            trial,
                            mechanism=mech,
                            fraction=frac,
                            replicate=rep,
                            root_seed=root_seed,
                        )
                    ),
                )
                diagnostic = _recovery_diagnostic(reference_estimate, estimate, protocol)
                missingness_results.append(
                    {
                        "mechanism": str(mechanism),
                        "fraction": float(fraction),
                        "replicate": replicate,
                        "estimate": estimate,
                        **diagnostic,
                    }
                )

    family_recovery = _family_recovery_rows(
        reference_estimate,
        sampling_results,
        missingness_results,
    )
    classification = _classify_execution(
        reference_estimate,
        sampling_results,
        missingness_results,
        family_recovery,
        protocol,
    )
    results_core = {
        "reference": reference,
        "sampling_results": sampling_results,
        "missingness_results": missingness_results,
        "family_recovery": family_recovery,
        "classification": classification,
    }
    manifest_core = {
        "schema": PEDROTTI_EXECUTION_SCHEMA,
        "case_study_id": PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_lock_fingerprint": PEDROTTI_SOURCE_LOCK_FINGERPRINT,
        "source_manifest_fingerprint": prepared.source_identity[
            "source_manifest_fingerprint"
        ],
        "participant_count": len(prepared.participant_ids),
        "numeric_trial_count": len(prepared.trials),
        "sampling_result_count": len(sampling_results),
        "missingness_result_count": len(missingness_results),
        "family_recovery_count": len(family_recovery),
        "results_fingerprint": fingerprint(results_core),
        "classification": classification,
    }
    execution_manifest = dict(manifest_core)
    execution_manifest["execution_fingerprint"] = fingerprint(manifest_core)
    return PedrottiScientificExecution(
        protocol=protocol,
        prepared=prepared,
        reference=reference,
        sampling_results=tuple(sampling_results),
        missingness_results=tuple(missingness_results),
        family_recovery=tuple(family_recovery),
        classification=classification,
        execution_manifest=execution_manifest,
    )


def run_pedrotti_locked_scientific_execution(
    prepared: PreparedPedrottiData,
    *,
    protocol_document: Mapping[str, Any] | None = None,
    lock_document: Mapping[str, Any] | None = None,
) -> PedrottiScientificExecution:
    """Execute real public data only after the archived source lock passes."""

    _verify_locked_prepared(prepared, lock_document=lock_document)
    return run_pedrotti_scientific_execution(
        prepared,
        protocol_document=protocol_document,
    )


def write_pedrotti_locked_execution_artifacts(
    execution: PedrottiScientificExecution,
    output_dir: str | Path,
    *,
    execution_context: Mapping[str, Any],
    environment_text: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write the outcome-bearing archive without revealing it to stdout."""

    if not isinstance(execution, PedrottiScientificExecution):
        raise TypeError("execution must be PedrottiScientificExecution")
    _verify_locked_prepared(execution.prepared)
    context = _validated_execution_context(execution_context)
    _validate_environment_snapshot(environment_text)

    destination = Path(output_dir)
    if destination.exists() and not destination.is_dir():
        raise ValueError("output_dir must be a directory path")
    if destination.exists() and any(destination.iterdir()):
        if not overwrite:
            raise FileExistsError("output_dir is not empty")
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    _write_json(destination / "source_identity.json", execution.prepared.source_identity)
    _write_json(destination / "reference.json", execution.reference)
    _write_json(destination / "sampling_results.json", list(execution.sampling_results))
    _write_json(
        destination / "missingness_results.json",
        list(execution.missingness_results),
    )
    _write_json(destination / "family_recovery.json", list(execution.family_recovery))
    _write_json(destination / "execution_manifest.json", execution.execution_manifest)
    _write_json(destination / "execution_context.json", context)
    (destination / "pip_freeze.txt").write_text(
        environment_text.rstrip("\n") + "\n",
        encoding="utf-8",
    )

    manifest_core = {
        "schema": PEDROTTI_EXECUTION_ARTIFACT_SCHEMA,
        "case_study_id": PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_lock_fingerprint": PEDROTTI_SOURCE_LOCK_FINGERPRINT,
        "source_manifest_fingerprint": execution.prepared.source_identity[
            "source_manifest_fingerprint"
        ],
        "execution_commit": context["execution_commit"],
        "workflow_ref": context["workflow_ref"],
        "github_run_id": context["github_run_id"],
        "execution_fingerprint": execution.execution_fingerprint,
        "classification": execution.classification,
        "files": _flat_file_records(destination),
    }
    artifact_manifest = dict(manifest_core)
    artifact_manifest["artifact_manifest_fingerprint"] = fingerprint(manifest_core)
    _write_json(destination / "artifact_manifest.json", artifact_manifest)
    _write_sha256sums(destination)

    if not verify_pedrotti_locked_execution_artifacts(destination):
        raise RuntimeError("newly written Pedrotti scientific archive failed verification")
    return artifact_manifest


def verify_pedrotti_locked_execution_artifacts(output_dir: str | Path) -> bool:
    """Verify checksums, source lock, protocol and frozen result semantics."""

    root = Path(output_dir)
    try:
        expected_names = {
            "SHA256SUMS",
            "artifact_manifest.json",
            "execution_context.json",
            "execution_manifest.json",
            "family_recovery.json",
            "missingness_results.json",
            "pip_freeze.txt",
            "reference.json",
            "sampling_results.json",
            "source_identity.json",
        }
        if not root.is_dir() or {path.name for path in root.iterdir()} != expected_names:
            return False
        checksums = _parse_checksums(root / "SHA256SUMS")
        if set(checksums) != expected_names - {"SHA256SUMS"}:
            return False
        if not all(_sha256_file(root / name) == digest for name, digest in checksums.items()):
            return False

        lock = verify_pedrotti_source_lock()
        source_identity = _read_json(root / "source_identity.json")
        reference = _read_json(root / "reference.json")
        sampling = _read_json_list(root / "sampling_results.json")
        missingness = _read_json_list(root / "missingness_results.json")
        families = _read_json_list(root / "family_recovery.json")
        execution = _read_json(root / "execution_manifest.json")
        context = _read_json(root / "execution_context.json")
        artifact = _read_json(root / "artifact_manifest.json")
        environment_text = (root / "pip_freeze.txt").read_text(encoding="utf-8")
        _validate_environment_snapshot(environment_text)
        _validated_execution_context(context)

        if source_identity.get("source_manifest_fingerprint") != (
            lock["source"]["source_manifest_fingerprint"]
        ):
            return False
        if source_identity.get("protocol_fingerprint") != PEDROTTI_PROTOCOL_FINGERPRINT:
            return False
        if int(source_identity.get("participant_count", -1)) != 36:
            return False
        if int(source_identity.get("numeric_trial_count", -1)) != 1728:
            return False

        protocol = _verified_protocol(None)
        _validate_archived_result_rows(reference, sampling, missingness, protocol)
        reference_estimate = float(reference["study_estimate"])
        expected_families = _family_recovery_rows(
            reference_estimate,
            sampling,
            missingness,
        )
        if json.loads(canonical_json(families)) != json.loads(
            canonical_json(expected_families)
        ):
            return False
        expected_classification = _classify_execution(
            reference_estimate,
            sampling,
            missingness,
            families,
            protocol,
        )
        results_core = {
            "reference": reference,
            "sampling_results": sampling,
            "missingness_results": missingness,
            "family_recovery": families,
            "classification": expected_classification,
        }
        execution_core = dict(execution)
        stored_execution_fingerprint = execution_core.pop("execution_fingerprint")
        if stored_execution_fingerprint != fingerprint(execution_core):
            return False
        if execution.get("schema") != PEDROTTI_EXECUTION_SCHEMA:
            return False
        if execution.get("case_study_id") != PEDROTTI_CASE_STUDY_ID:
            return False
        if execution.get("results_fingerprint") != fingerprint(results_core):
            return False
        if execution.get("classification") != expected_classification:
            return False
        if execution.get("protocol_fingerprint") != PEDROTTI_PROTOCOL_FINGERPRINT:
            return False
        if execution.get("source_lock_fingerprint") != PEDROTTI_SOURCE_LOCK_FINGERPRINT:
            return False
        if int(execution.get("participant_count", -1)) != 36:
            return False
        if int(execution.get("numeric_trial_count", -1)) != 1728:
            return False
        if execution.get("source_manifest_fingerprint") != (
            PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT
        ):
            return False
        if int(execution.get("sampling_result_count", -1)) != 5:
            return False
        if int(execution.get("missingness_result_count", -1)) != 160:
            return False
        if int(execution.get("family_recovery_count", -1)) != 9:
            return False

        artifact_core = dict(artifact)
        stored_artifact_fingerprint = artifact_core.pop(
            "artifact_manifest_fingerprint"
        )
        if stored_artifact_fingerprint != fingerprint(artifact_core):
            return False
        if artifact.get("schema") != PEDROTTI_EXECUTION_ARTIFACT_SCHEMA:
            return False
        if artifact.get("source_lock_fingerprint") != PEDROTTI_SOURCE_LOCK_FINGERPRINT:
            return False
        if artifact.get("source_manifest_fingerprint") != (
            PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT
        ):
            return False
        if artifact.get("execution_fingerprint") != stored_execution_fingerprint:
            return False
        if artifact.get("classification") != expected_classification:
            return False
        if artifact.get("execution_commit") != context["execution_commit"]:
            return False
        if artifact.get("github_run_id") != context["github_run_id"]:
            return False
        if artifact.get("workflow_ref") != PEDROTTI_EXECUTION_WORKFLOW:
            return False

        expected_records = _flat_file_records(
            root,
            excluded={"artifact_manifest.json", "SHA256SUMS"},
        )
        return artifact.get("files") == expected_records
    except (
        KeyError,
        OSError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        OverflowError,
    ):
        return False


def reveal_pedrotti_locked_execution(output_dir: str | Path) -> dict[str, Any]:
    """Reveal only a scientific result that already exists in a verified archive."""

    root = Path(output_dir)
    if not verify_pedrotti_locked_execution_artifacts(root):
        raise ValueError("Pedrotti scientific archive failed locked verification")
    return {
        "status": "archived_scientific_result",
        "reference": _read_json(root / "reference.json"),
        "sampling_results": _read_json_list(root / "sampling_results.json"),
        "missingness_results": _read_json_list(root / "missingness_results.json"),
        "family_recovery": _read_json_list(root / "family_recovery.json"),
        "execution_manifest": _read_json(root / "execution_manifest.json"),
    }


def _verified_protocol(
    document: Mapping[str, Any] | None,
) -> dict[str, Any]:
    packaged = load_pedrotti_protocol()
    candidate = packaged if document is None else json.loads(canonical_json(document))
    if not isinstance(candidate, dict):
        raise TypeError("Pedrotti protocol must normalize to an object")
    if candidate.get("protocol_fingerprint") != PEDROTTI_PROTOCOL_FINGERPRINT:
        raise ValueError("Pedrotti protocol fingerprint differs from frozen identity")
    if canonical_json(candidate) != canonical_json(packaged):
        raise ValueError("Pedrotti protocol content differs from packaged frozen protocol")
    return candidate


def _validate_prepared(prepared: PreparedPedrottiData) -> None:
    if not isinstance(prepared, PreparedPedrottiData):
        raise TypeError("prepared must be PreparedPedrottiData")
    if not prepared.trials or not prepared.participant_ids:
        raise ValueError("prepared data must contain participants and numeric trials")
    if len(set(prepared.participant_ids)) != len(prepared.participant_ids):
        raise ValueError("participant identities must be unique")
    participant_set = set(prepared.participant_ids)
    condition_counts = {
        participant: {"short": 0, "long": 0} for participant in prepared.participant_ids
    }
    keys: set[tuple[str, int]] = set()
    for trial in prepared.trials:
        if not isinstance(trial, PedrottiTrial):
            raise TypeError("prepared trials must be PedrottiTrial instances")
        if trial.participant_id not in participant_set:
            raise ValueError("trial participant is absent from participant_ids")
        key = (trial.participant_id, trial.trial_index)
        if key in keys:
            raise ValueError("duplicate participant-by-trial identity")
        keys.add(key)
        condition_counts[trial.participant_id][trial.condition] += 1
    if any(
        counts["short"] < 1 or counts["long"] < 1
        for counts in condition_counts.values()
    ):
        raise ValueError("every participant must contribute both frozen numeric conditions")


def _verify_locked_prepared(
    prepared: PreparedPedrottiData,
    *,
    lock_document: Mapping[str, Any] | None = None,
) -> PreparedPedrottiData:
    _validate_prepared(prepared)
    lock = verify_pedrotti_source_lock(lock_document)
    identity = prepared.source_identity
    checks = {
        "case_study": identity.get("case_study_id") == PEDROTTI_CASE_STUDY_ID,
        "protocol": identity.get("protocol_fingerprint") == PEDROTTI_PROTOCOL_FINGERPRINT,
        "source": (
            identity.get("source_manifest_fingerprint")
            == lock["source"]["source_manifest_fingerprint"]
        ),
        "participant_count": (
            int(identity.get("participant_count", -1))
            == int(lock["intake"]["participant_count"])
            == len(prepared.participant_ids)
        ),
        "source_file_count": (
            int(identity.get("source_file_count", -1))
            == int(lock["source"]["file_count"])
        ),
        "total_rows": (
            int(identity.get("total_row_count", -1))
            == int(lock["intake"]["total_row_count"])
        ),
        "total_trials": (
            int(identity.get("total_trial_count", -1))
            == int(lock["intake"]["total_trial_count"])
        ),
        "short_trials": (
            int(identity.get("short_numeric_trial_count", -1))
            == int(lock["intake"]["short_numeric_trial_count"])
        ),
        "long_trials": (
            int(identity.get("long_numeric_trial_count", -1))
            == int(lock["intake"]["long_numeric_trial_count"])
        ),
        "numeric_trials": (
            int(identity.get("numeric_trial_count", -1))
            == int(lock["intake"]["short_numeric_trial_count"])
            + int(lock["intake"]["long_numeric_trial_count"])
            == len(prepared.trials)
        ),
        "eyes": identity.get("eye_counts") == lock["intake"]["eye_counts"],
        "endpoint_blind": (
            identity.get("scientific_endpoint_evaluated_before_preparation") is False
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"prepared Pedrotti data differs from source lock: {failed}")
    return prepared


def _trial_rate_native(trial: PedrottiTrial) -> float:
    return float(trial.edge_distance.sum() / trial.duration_seconds)


def _trial_rate_sampled(trial: PedrottiTrial, target_hz: float) -> float:
    if not np.isfinite(target_hz) or target_hz <= 0:
        raise ValueError("target_hz must be finite and positive")
    interval = 1000.0 / target_hz
    start = float(trial.timestamp_ms[0])
    stop = float(trial.timestamp_ms[-1])
    grid = np.arange(start, stop + interval * 0.5, interval)
    positions = _nearest_unique_positions(trial.timestamp_ms, grid)
    x_values = trial.x[positions]
    y_values = trial.y[positions]
    finite = np.isfinite(x_values) & np.isfinite(y_values)
    pair = finite[:-1] & finite[1:]
    numerator = 0.0
    if bool(pair.any()):
        numerator = float(
            np.hypot(
                x_values[1:][pair] - x_values[:-1][pair],
                y_values[1:][pair] - y_values[:-1][pair],
            ).sum()
        )
    return numerator / trial.duration_seconds


def _trial_rate_missingness(
    trial: PedrottiTrial,
    *,
    mechanism: str,
    fraction: float,
    replicate: int,
    root_seed: int,
) -> float:
    selected = _added_missingness_positions(
        trial,
        mechanism=mechanism,
        fraction=fraction,
        replicate=replicate,
        root_seed=root_seed,
    )
    if selected.size == 0:
        return _trial_rate_native(trial)
    adjacent = np.concatenate((selected - 1, selected))
    adjacent = adjacent[(adjacent >= 0) & (adjacent < len(trial.edge_distance))]
    removed_edges = np.unique(adjacent)
    numerator = float(
        trial.edge_distance.sum() - trial.edge_distance[removed_edges].sum()
    )
    if numerator < 0 and abs(numerator) < 1e-10:
        numerator = 0.0
    if numerator < 0:
        raise RuntimeError("added missingness produced a negative path numerator")
    return numerator / trial.duration_seconds


def _added_missingness_positions(
    trial: PedrottiTrial,
    *,
    mechanism: str,
    fraction: float,
    replicate: int,
    root_seed: int,
) -> np.ndarray:
    if mechanism not in {"mcar_within_trial", "single_block_within_trial"}:
        raise ValueError("unexpected frozen missingness mechanism")
    if not np.isfinite(fraction) or not 0 <= fraction <= 1:
        raise ValueError("fraction must be finite and between zero and one")
    if not isinstance(replicate, int) or isinstance(replicate, bool) or replicate < 1:
        raise ValueError("replicate must be a positive integer")

    finite_positions = trial.finite_positions
    n_mask = int(round(float(fraction) * finite_positions.size))
    if n_mask == 0:
        return np.array([], dtype=int)
    if n_mask > finite_positions.size:
        raise ValueError("requested added missingness exceeds finite trial rows")
    generator = np.random.default_rng(
        _child_seed(
            root_seed,
            trial.participant_id,
            trial.trial_index,
            mechanism,
            fraction,
            replicate,
        )
    )
    if mechanism == "mcar_within_trial":
        selected = generator.choice(finite_positions, size=n_mask, replace=False)
        return np.sort(np.asarray(selected, dtype=int))

    last_admissible_start = int(finite_positions[finite_positions.size - n_mask])
    start = int(generator.integers(0, last_admissible_start + 1))
    first_finite = int(np.searchsorted(finite_positions, start, side="left"))
    selected = finite_positions[first_finite : first_finite + n_mask]
    if selected.size != n_mask:
        raise RuntimeError("single-block missingness failed exact finite-sample target")
    return selected


def _child_seed(
    root_seed: int,
    participant_id: str,
    trial_index: int,
    mechanism: str,
    fraction: float,
    replicate: int,
) -> int:
    key = (
        f"{int(root_seed)}|{participant_id}|{int(trial_index):03d}|"
        f"{mechanism}|{float(fraction):.8f}|{int(replicate):03d}"
    )
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _study_estimate(
    prepared: PreparedPedrottiData,
    trial_estimator: Any,
) -> tuple[float, list[dict[str, Any]]]:
    values = {
        participant: {"short": [], "long": []}
        for participant in prepared.participant_ids
    }
    for trial in prepared.trials:
        estimate = float(trial_estimator(trial))
        if not np.isfinite(estimate):
            raise ValueError("trial endpoint produced a non-finite estimate")
        values[trial.participant_id][trial.condition].append(estimate)

    participant_rows: list[dict[str, Any]] = []
    contrasts: list[float] = []
    for participant in prepared.participant_ids:
        short = values[participant]["short"]
        long = values[participant]["long"]
        if not short or not long:
            raise ValueError("participant lacks a frozen numeric condition")
        short_mean = float(np.mean(short))
        long_mean = float(np.mean(long))
        contrast = long_mean - short_mean
        if not np.isfinite(contrast):
            raise ValueError("participant contrast is non-finite")
        contrasts.append(contrast)
        participant_rows.append(
            {
                "participant_id": participant,
                "short_mean": short_mean,
                "long_mean": long_mean,
                "contrast": contrast,
                "short_trial_count": len(short),
                "long_trial_count": len(long),
            }
        )
    study = float(np.mean(contrasts))
    if not np.isfinite(study):
        raise ValueError("study endpoint is non-finite")
    return study, participant_rows


def _recovery_diagnostic(
    reference: float,
    estimate: float,
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    if not np.isfinite(reference) or not np.isfinite(estimate):
        raise ValueError("recovery diagnostics require finite estimates")
    if reference == 0.0:
        return {
            "relative_deviation": None,
            "same_strict_sign": None,
            "recovered": None,
        }
    tolerance = float(protocol["interpretation"]["relative_tolerance"])
    relative_deviation = abs(estimate - reference) / abs(reference)
    same_sign = bool(estimate * reference > 0)
    recovered = bool(same_sign and relative_deviation <= tolerance)
    return {
        "relative_deviation": float(relative_deviation),
        "same_strict_sign": same_sign,
        "recovered": recovered,
    }


def _validate_archived_result_rows(
    reference: Mapping[str, Any],
    sampling_results: Sequence[Mapping[str, Any]],
    missingness_results: Sequence[Mapping[str, Any]],
    protocol: Mapping[str, Any],
) -> None:
    if set(reference) != {"study_estimate", "participant_contrasts", "unit"}:
        raise ValueError("reference result has an unexpected field set")
    if reference["unit"] != protocol["endpoint"]["unit"]:
        raise ValueError("reference endpoint unit differs from frozen protocol")
    participants = reference["participant_contrasts"]
    if not isinstance(participants, list) or len(participants) != 36:
        raise ValueError("reference must contain 36 participant contrasts")
    expected_participant_fields = {
        "participant_id",
        "short_mean",
        "long_mean",
        "contrast",
        "short_trial_count",
        "long_trial_count",
    }
    if any(
        not isinstance(row, dict) or set(row) != expected_participant_fields
        for row in participants
    ):
        raise ValueError("reference participant rows have an unexpected field set")
    if [str(row["participant_id"]) for row in participants] != [
        f"{participant:02d}" for participant in range(1, 37)
    ]:
        raise ValueError("reference participant identities differ from 01 through 36")
    if any(
        not np.isfinite(float(row[field]))
        for row in participants
        for field in ("short_mean", "long_mean", "contrast")
    ):
        raise ValueError("reference participant result contains a non-finite estimate")

    target_rates = [float(value) for value in protocol["sampling"]["target_hz"]]
    if len(sampling_results) != len(target_rates):
        raise ValueError("sampling result count differs from frozen grid")
    sampling_fields = {
        "target_hz",
        "estimate",
        "relative_deviation",
        "same_strict_sign",
        "recovered",
    }
    reference_estimate = float(reference["study_estimate"])
    for row, target_hz in zip(sampling_results, target_rates, strict=True):
        if set(row) != sampling_fields or float(row["target_hz"]) != target_hz:
            raise ValueError("sampling result differs from frozen grid")
        expected = _recovery_diagnostic(
            reference_estimate,
            float(row["estimate"]),
            protocol,
        )
        observed = {key: row[key] for key in expected}
        if canonical_json(observed) != canonical_json(expected):
            raise ValueError("sampling recovery diagnostic is inconsistent")

    expected_keys = [
        (str(mechanism), float(fraction), replicate)
        for mechanism in protocol["missingness"]["mechanisms"]
        for fraction in protocol["missingness"]["fractions"]
        for replicate in range(1, int(protocol["missingness"]["replicates"]) + 1)
    ]
    if len(missingness_results) != len(expected_keys):
        raise ValueError("missingness result count differs from frozen grid")
    missingness_fields = {
        "mechanism",
        "fraction",
        "replicate",
        "estimate",
        "relative_deviation",
        "same_strict_sign",
        "recovered",
    }
    for row, expected_key in zip(missingness_results, expected_keys, strict=True):
        key = (str(row["mechanism"]), float(row["fraction"]), int(row["replicate"]))
        if set(row) != missingness_fields or key != expected_key:
            raise ValueError("missingness result differs from frozen grid")
        expected = _recovery_diagnostic(
            reference_estimate,
            float(row["estimate"]),
            protocol,
        )
        observed = {name: row[name] for name in expected}
        if canonical_json(observed) != canonical_json(expected):
            raise ValueError("missingness recovery diagnostic is inconsistent")


def _family_recovery_rows(
    reference: float,
    sampling_results: Sequence[Mapping[str, Any]],
    missingness_results: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if reference == 0.0:
        sampling_recovery = None
    else:
        sampling_recovery = float(
            np.mean([bool(row["recovered"]) for row in sampling_results])
        )
    rows: list[dict[str, Any]] = [
        {
            "family": "sampling",
            "mechanism": None,
            "fraction": None,
            "n_estimates": len(sampling_results),
            "recovery_fraction": sampling_recovery,
        }
    ]
    grouped: dict[tuple[str, float], list[Mapping[str, Any]]] = {}
    for row in missingness_results:
        key = (str(row["mechanism"]), float(row["fraction"]))
        grouped.setdefault(key, []).append(row)
    for mechanism, fraction in sorted(grouped):
        members = grouped[(mechanism, fraction)]
        recovery = None
        if reference != 0.0:
            recovery = float(np.mean([bool(row["recovered"]) for row in members]))
        rows.append(
            {
                "family": "missingness",
                "mechanism": mechanism,
                "fraction": fraction,
                "n_estimates": len(members),
                "recovery_fraction": recovery,
            }
        )
    return rows


def _classify_execution(
    reference: float,
    sampling_results: Sequence[Mapping[str, Any]],
    missingness_results: Sequence[Mapping[str, Any]],
    family_recovery: Sequence[Mapping[str, Any]],
    protocol: Mapping[str, Any],
) -> str:
    if not np.isfinite(reference):
        return "incomplete"
    if reference == 0.0:
        return "indeterminate_reference_zero"
    if len(sampling_results) != 5 or len(missingness_results) != 160:
        return "incomplete"
    if len(family_recovery) != 9:
        return "incomplete"
    for row in [*sampling_results, *missingness_results]:
        try:
            estimate = float(row["estimate"])
            deviation = float(row["relative_deviation"])
        except (KeyError, TypeError, ValueError):
            return "incomplete"
        if not np.isfinite(estimate) or not np.isfinite(deviation):
            return "incomplete"
        if not isinstance(row.get("same_strict_sign"), bool):
            return "incomplete"
        if not isinstance(row.get("recovered"), bool):
            return "incomplete"

    recoveries: list[float] = []
    for row in family_recovery:
        value = row.get("recovery_fraction")
        if value is None:
            return "incomplete"
        recovery = float(value)
        if not np.isfinite(recovery) or not 0 <= recovery <= 1:
            return "incomplete"
        recoveries.append(recovery)
    minimum = float(protocol["interpretation"]["minimum_family_recovery"])
    fragile = float(protocol["interpretation"]["material_fragility_ceiling"])
    if all(value >= minimum for value in recoveries):
        return "robust"
    if any(value <= fragile for value in recoveries):
        return "materially_fragile"
    return "mixed"


def _nearest_unique_positions(times: np.ndarray, grid: np.ndarray) -> np.ndarray:
    insertion = np.searchsorted(times, grid, side="left")
    right = np.clip(insertion, 0, len(times) - 1)
    left = np.clip(insertion - 1, 0, len(times) - 1)
    left_distance = np.abs(times[left] - grid)
    right_distance = np.abs(times[right] - grid)
    chosen = np.where(right_distance < left_distance, right, left)
    return np.unique(chosen)


def _validated_execution_context(
    document: Mapping[str, Any],
) -> dict[str, Any]:
    context = json.loads(canonical_json(document))
    if not isinstance(context, dict):
        raise TypeError("execution_context must normalize to an object")
    required = {
        "schema",
        "execution_commit",
        "workflow_ref",
        "github_run_id",
        "runner_os",
        "runner_arch",
        "python",
    }
    if set(context) != required:
        raise ValueError("execution_context has an unexpected field set")
    if context["schema"] != "gazeaudit-pedrotti-execution-context-v1":
        raise ValueError("unexpected Pedrotti execution-context schema")
    if not _SHA40.fullmatch(str(context["execution_commit"])):
        raise ValueError("execution_commit must be a lowercase 40-hex SHA")
    if context["workflow_ref"] != PEDROTTI_EXECUTION_WORKFLOW:
        raise ValueError("unexpected Pedrotti execution workflow")
    if (
        not isinstance(context["github_run_id"], int)
        or isinstance(context["github_run_id"], bool)
        or context["github_run_id"] < 1
    ):
        raise ValueError("github_run_id must be a positive integer")
    if not isinstance(context["runner_os"], str) or not context["runner_os"]:
        raise ValueError("runner_os must be non-empty")
    if not isinstance(context["runner_arch"], str) or not context["runner_arch"]:
        raise ValueError("runner_arch must be non-empty")
    if context["python"] != "3.12.14":
        raise ValueError("scientific execution requires Python 3.12.14")
    return context


def _validate_environment_snapshot(environment_text: str) -> None:
    if not isinstance(environment_text, str) or not environment_text.strip():
        raise ValueError("environment snapshot must be non-empty")
    lines = set(environment_text.splitlines())
    required = {"numpy==2.5.3", "pandas==2.3.3"}
    if not required.issubset(lines):
        raise ValueError("environment snapshot differs from frozen execution stack")


def execution_context(
    *,
    execution_commit: str,
    github_run_id: int,
    runner_os: str,
    runner_arch: str,
) -> dict[str, Any]:
    """Build a validated workflow execution-context record."""

    return _validated_execution_context(
        {
            "schema": "gazeaudit-pedrotti-execution-context-v1",
            "execution_commit": execution_commit,
            "workflow_ref": PEDROTTI_EXECUTION_WORKFLOW,
            "github_run_id": github_run_id,
            "runner_os": runner_os,
            "runner_arch": runner_arch,
            "python": platform.python_version(),
        }
    )


def _flat_file_records(
    root: Path,
    *,
    excluded: set[str] | None = None,
) -> list[dict[str, Any]]:
    excluded = set() if excluded is None else excluded
    records = []
    for path in sorted(root.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name not in excluded:
            records.append(
                {
                    "path": path.name,
                    "size_bytes": int(path.stat().st_size),
                    "sha256": _sha256_file(path),
                }
            )
    return records


def _write_sha256sums(root: Path) -> None:
    targets = sorted(
        (path for path in root.iterdir() if path.is_file() and path.name != "SHA256SUMS"),
        key=lambda item: item.name,
    )
    (root / "SHA256SUMS").write_text(
        "\n".join(f"{_sha256_file(path)}  {path.name}" for path in targets) + "\n",
        encoding="utf-8",
    )


def _parse_checksums(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, separator, name = line.partition("  ")
        if (
            not separator
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            or not name
            or Path(name).is_absolute()
            or ".." in Path(name).parts
            or name in values
        ):
            raise ValueError("invalid SHA256SUMS entry")
        values[name] = digest
    return values


def _write_json(path: Path, value: Any) -> None:
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise ValueError(f"{path.name} must contain a JSON array of objects")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
