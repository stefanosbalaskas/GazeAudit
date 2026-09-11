"""Frozen-protocol execution support for the Korthals et al. AOI case study.

The adapter starts after the companion repository's canonical ``OriginalPreprocessor``
gaze/target preprocessing and alignment. It binds aligned tables to the predeclared
50-Hz representation, validation-block mapping, paired endpoint, grouped measurement
error model, and interpretation rule.

No public-data download or endpoint execution happens at import time. The protocol
implementation can therefore be certified on synthetic fixtures before any target
scientific result is inspected.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .aoi import CircleAOI
from .aoi_artifacts import (
    verify_aoi_uncertainty_artifacts,
    write_aoi_uncertainty_artifacts,
)
from .aoi_propagation import AOIEffectUncertaintyAudit, audit_aoi_effect_uncertainty
from .aoi_protocol import verify_aoi_uncertainty_protocol
from .provenance import canonical_json, fingerprint
from .uncertainty import GroupedGaussianGazeErrorModel

KORTHALS_PROTOCOL_FINGERPRINT = (
    "2b8e8da84182316d08ab173ad7d71a2ff09fc45bd84f875ae548832a288ba291"
)
KORTHALS_CASE_STUDY_ID = "korthals2026-target-tracking-aoi-v1"
KORTHALS_COMPANION_COMMIT = "1d7ebec23e3fe20f6db952eefda1a0dd58ae09da"
KORTHALS_TARGET_TYPES = ("moving_circle", "jumping_circle")
KORTHALS_ARTIFACT_SCHEMA = "gazeaudit-korthals-aoi-execution-artifacts-v1"


@dataclass(frozen=True)
class PreparedKorthalsData:
    """Protocol-bound 50-Hz Korthals samples and validation summaries."""

    data: pd.DataFrame
    validation_groups: pd.DataFrame
    source_identity: dict[str, Any]


@dataclass(frozen=True)
class KorthalsAOIExecution:
    """One frozen Korthals measurement-uncertainty execution."""

    protocol: dict[str, Any]
    prepared: PreparedKorthalsData
    audit: AOIEffectUncertaintyAudit
    classification: str
    execution_manifest: dict[str, Any]

    @property
    def execution_fingerprint(self) -> str:
        return str(self.execution_manifest["execution_fingerprint"])


def load_korthals_protocol() -> dict[str, Any]:
    """Load the immutable Korthals protocol shipped inside the package."""

    text = (
        resources.files("gazeaudit.data")
        .joinpath("korthals2026_target_tracking_aoi_v1.json")
        .read_text(encoding="utf-8")
    )
    document = json.loads(text)
    if not isinstance(document, dict):
        raise ValueError("packaged Korthals protocol must be a JSON object")
    return document


def verify_korthals_protocol(
    document: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify the frozen Korthals identity and scientific guardrails."""

    protocol = load_korthals_protocol() if document is None else dict(document)
    if not verify_aoi_uncertainty_protocol(protocol):
        raise ValueError("Korthals protocol failed generic protocol verification")
    checks = {
        "fingerprint": protocol.get("protocol_fingerprint") == KORTHALS_PROTOCOL_FINGERPRINT,
        "case_study": protocol.get("case_study_id") == KORTHALS_CASE_STUDY_ID,
        "companion_commit": (
            protocol["dataset"].get("companion_commit") == KORTHALS_COMPANION_COMMIT
        ),
        "target_types": (
            tuple(protocol["dataset"].get("trial_types", ())) == KORTHALS_TARGET_TYPES
        ),
        "sampling_hz": (
            float(protocol["dataset"]["sampling"].get("target_hz", -1.0)) == 50.0
        ),
        "validation_group": (
            tuple(protocol["validation"].get("grouping", ()))
            == ("participant_id", "validation_nr")
        ),
        "validation_metric": protocol["validation"].get("metric") == "error_avg",
        "aoi_geometry": protocol["aoi"].get("geometry") == "circle",
        "aoi_radius": float(protocol["aoi"].get("radius", -1.0)) == 1.0,
        "draws": int(protocol["monte_carlo"].get("draws", -1)) == 2000,
        "batch_size": int(protocol["monte_carlo"].get("batch_size", -1)) == 8,
        "seed": int(protocol["monte_carlo"].get("rng_seed", -1)) == 20260316,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"Korthals protocol failed frozen guardrails: {failed}")
    return protocol


def prepare_korthals_aligned_data(
    aligned_data: pd.DataFrame,
    validations: pd.DataFrame,
    *,
    source_identity: Mapping[str, Any] | None = None,
    protocol_document: Mapping[str, Any] | None = None,
) -> PreparedKorthalsData:
    """Bind canonical companion-preprocessed gaze/target data to protocol v1.

    ``aligned_data`` must contain canonical target-aligned companion output with
    participant/trial identifiers, trial-relative time, gaze and target coordinates,
    target type, actual target speed (or normalized ``target_speed``), and trajectory.
    ``validations`` must concatenate ``Participant.validation_check()`` outputs.

    The operation order is frozen: author exclusion -> target-type filter -> validation
    mapping -> 50-Hz nearest-row sampling with earlier-sample tie breaking -> removal of
    non-finite gaze. Missing mappings and retained trials with zero finite scheduled
    samples fail closed.
    """

    protocol = verify_korthals_protocol(protocol_document)
    if not isinstance(aligned_data, pd.DataFrame):
        raise TypeError("aligned_data must be a pandas DataFrame")
    if not isinstance(validations, pd.DataFrame):
        raise TypeError("validations must be a pandas DataFrame")
    if aligned_data.empty:
        raise ValueError("aligned_data must not be empty")

    data = _normalize_aligned_data(aligned_data)
    validation_table = _normalize_validations(validations)
    exclusion = protocol["dataset"]["author_directed_exclusion"]
    excluded = (
        (data["participant_id"] == str(exclusion["participant_id"]))
        & data["trial_number"].between(
            int(exclusion["trial_number_start"]),
            int(exclusion["trial_number_end"]),
            inclusive="both",
        )
    )
    data = data.loc[~excluded].copy()
    data = data[data["target_type"].isin(KORTHALS_TARGET_TYPES)].copy()
    if data.empty:
        raise ValueError("no frozen moving/jumping-circle rows remain after filtering")
    if set(data["target_type"].unique()) != set(KORTHALS_TARGET_TYPES):
        raise ValueError("prepared data must contain both frozen target types")

    trial_mapping = _validation_trial_mapping(data, validation_table)
    keys = zip(data["participant_id"], data["trial_number"], strict=True)
    mapped = [trial_mapping[(participant, int(trial))] for participant, trial in keys]
    data["validation_nr"] = [value[0] for value in mapped]
    data["error_avg"] = [value[1] for value in mapped]

    sampled_parts = [
        _downsample_trial_50hz(trial)
        for _, trial in data.groupby(["participant_id", "trial_number"], sort=True)
    ]
    sampled = pd.concat(sampled_parts, ignore_index=True)
    target_points = sampled[["target_x", "target_y"]].to_numpy(dtype=float)
    if np.any(~np.isfinite(target_points)):
        raise ValueError("target coordinates must remain finite on the scheduled grid")

    gaze = sampled[["gaze_x", "gaze_y"]].to_numpy(dtype=float)
    sampled = sampled.loc[np.isfinite(gaze).all(axis=1)].copy()
    if sampled.empty:
        raise ValueError("no finite gaze rows remain after frozen 50-Hz sampling")

    expected_trials = set(
        zip(data["participant_id"], data["trial_number"].astype(int), strict=True)
    )
    observed_trials = set(
        zip(sampled["participant_id"], sampled["trial_number"].astype(int), strict=True)
    )
    missing_trials = sorted(expected_trials.difference(observed_trials))
    if missing_trials:
        raise ValueError(
            "retained trials with zero finite scheduled samples fail closed: "
            f"{missing_trials[:5]}"
        )

    sampled["observed_x"] = sampled["gaze_x"] - sampled["target_x"]
    sampled["observed_y"] = sampled["gaze_y"] - sampled["target_y"]
    sampled["repetition"] = np.where(sampled["trial_number"] <= 72, 1, 2).astype(int)
    sampled["error_group"] = list(
        zip(sampled["participant_id"], sampled["validation_nr"].astype(int), strict=True)
    )
    sampled = sampled.sort_values(
        ["participant_id", "trial_number", "scheduled_trial_time", "trial_time"],
        kind="stable",
    ).reset_index(drop=True)
    _endpoint_weights(sampled)

    used_groups = set(sampled["error_group"])
    validation_groups = validation_table.copy()
    validation_groups["error_group"] = list(
        zip(
            validation_groups["participant_id"],
            validation_groups["validation_nr"].astype(int),
            strict=True,
        )
    )
    validation_groups = validation_groups[
        validation_groups["error_group"].isin(used_groups)
    ].copy()
    if set(validation_groups["error_group"]) != used_groups:
        raise ValueError("every retained error group must have one validation summary")
    if validation_groups["error_group"].duplicated().any():
        raise ValueError("validation groups must be unique")
    validation_groups["n_validation"] = int(protocol["validation"]["n_validation_points"])
    validation_groups = validation_groups[
        ["participant_id", "validation_nr", "error_avg", "n_validation", "error_group"]
    ]
    validation_groups = validation_groups.sort_values(
        ["participant_id", "validation_nr"], kind="stable"
    ).reset_index(drop=True)

    participant_ids = sorted(sampled["participant_id"].unique().tolist())
    retained_trials = (
        sampled[["participant_id", "trial_number"]]
        .drop_duplicates()
        .sort_values(["participant_id", "trial_number"], kind="stable")
        .to_dict(orient="records")
    )
    supplied_identity = (
        {} if source_identity is None else json.loads(canonical_json(source_identity))
    )
    if not isinstance(supplied_identity, dict):
        raise TypeError("source_identity must normalize to an object")
    protected = {
        "case_study_id",
        "companion_commit",
        "protocol_fingerprint",
        "participant_count",
        "participant_fingerprint",
        "retained_trial_count",
        "retained_trial_fingerprint",
    }
    forbidden = protected.intersection(supplied_identity)
    if forbidden:
        names = sorted(forbidden)
        raise ValueError(
            f"source_identity may not override frozen identity fields: {names}"
        )
    identity = {
        **supplied_identity,
        "case_study_id": KORTHALS_CASE_STUDY_ID,
        "companion_commit": KORTHALS_COMPANION_COMMIT,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "participant_count": len(participant_ids),
        "participant_fingerprint": fingerprint(participant_ids),
        "retained_trial_count": len(retained_trials),
        "retained_trial_fingerprint": fingerprint(retained_trials),
    }
    return PreparedKorthalsData(sampled, validation_groups, identity)


def korthals_paired_occupancy_effect(data: pd.DataFrame, membership: np.ndarray) -> float:
    """Frozen unweighted jumping-minus-moving occupancy estimand."""

    values = _validate_membership(membership, len(data))
    return float(np.dot(_endpoint_weights(data), values))


def run_korthals_aoi_execution(
    prepared: PreparedKorthalsData,
    *,
    protocol_document: Mapping[str, Any] | None = None,
) -> KorthalsAOIExecution:
    """Execute the frozen measurement-uncertainty protocol on prepared data."""

    if not isinstance(prepared, PreparedKorthalsData):
        raise TypeError("prepared must be PreparedKorthalsData")
    protocol = verify_korthals_protocol(protocol_document)
    _validate_prepared_identity(prepared, protocol)

    radial_errors = {
        row.error_group: float(row.error_avg)
        for row in prepared.validation_groups.itertuples(index=False)
    }
    n_validation = {
        row.error_group: int(row.n_validation)
        for row in prepared.validation_groups.itertuples(index=False)
    }
    model = GroupedGaussianGazeErrorModel.from_mean_radial_errors(
        radial_errors,
        n_validation=n_validation,
        bias=(0.0, 0.0),
    )
    aoi = CircleAOI(
        str(protocol["aoi"]["name"]),
        float(protocol["aoi"]["cx"]),
        float(protocol["aoi"]["cy"]),
        float(protocol["aoi"]["radius"]),
    )
    weights = _endpoint_weights(prepared.data)

    def frozen_endpoint(_data: pd.DataFrame, membership: np.ndarray) -> float:
        values = _validate_membership(membership, len(weights))
        return float(np.dot(weights, values))

    monte_carlo = protocol["monte_carlo"]
    audit = audit_aoi_effect_uncertainty(
        prepared.data,
        aoi,
        model,
        frozen_endpoint,
        observed_x="observed_x",
        observed_y="observed_y",
        error_group=prepared.data["error_group"].tolist(),
        draws=int(monte_carlo["draws"]),
        batch_size=int(monte_carlo["batch_size"]),
        interval=float(monte_carlo["interval"]),
        reference=float(monte_carlo["reference"]),
        rng=int(monte_carlo["rng_seed"]),
    )
    classification = _classify_korthals_result(audit.summary)
    manifest_core = {
        "case_study_id": KORTHALS_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "source_identity": prepared.source_identity,
        "n_rows": len(prepared.data),
        "n_validation_groups": len(prepared.validation_groups),
        "classification": classification,
        "summary": json.loads(canonical_json(audit.summary.to_dict())),
    }
    execution_manifest = dict(manifest_core)
    execution_manifest["execution_fingerprint"] = fingerprint(manifest_core)
    return KorthalsAOIExecution(
        protocol=protocol,
        prepared=prepared,
        audit=audit,
        classification=classification,
        execution_manifest=execution_manifest,
    )


def write_korthals_execution_artifacts(
    execution: KorthalsAOIExecution,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write and verify a checksummed envelope around the generic AOI audit."""

    if not isinstance(execution, KorthalsAOIExecution):
        raise TypeError("execution must be KorthalsAOIExecution")
    destination = Path(output_dir)
    if destination.exists() and not destination.is_dir():
        raise ValueError("output_dir must be a directory path")
    if destination.exists() and any(destination.iterdir()):
        if not overwrite:
            raise FileExistsError(
                "output_dir is not empty; pass overwrite=True to replace artifacts"
            )
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    audit_manifest = write_aoi_uncertainty_artifacts(
        execution.audit,
        execution.protocol,
        destination / "audit",
    )
    _write_json(destination / "source_identity.json", execution.prepared.source_identity)
    _write_json(destination / "execution_manifest.json", execution.execution_manifest)

    manifest_core = {
        "schema": KORTHALS_ARTIFACT_SCHEMA,
        "case_study_id": KORTHALS_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "execution_fingerprint": execution.execution_fingerprint,
        "classification": execution.classification,
        "audit_scientific_fingerprint": audit_manifest["scientific_fingerprint"],
        "files": _recursive_file_records(destination),
    }
    manifest = dict(manifest_core)
    manifest["artifact_manifest_fingerprint"] = fingerprint(manifest_core)
    _write_json(destination / "artifact_manifest.json", manifest)

    checksum_targets = sorted(
        path
        for path in destination.rglob("*")
        if path.is_file() and path.relative_to(destination).as_posix() != "SHA256SUMS"
    )
    lines = [
        f"{_sha256_file(path)}  {path.relative_to(destination).as_posix()}"
        for path in checksum_targets
    ]
    (destination / "SHA256SUMS").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )
    if not verify_korthals_execution_artifacts(destination):
        raise RuntimeError("newly written Korthals artifact set failed verification")
    return manifest


def verify_korthals_execution_artifacts(output_dir: str | Path) -> bool:
    """Return whether a Korthals execution envelope is complete and intact."""

    destination = Path(output_dir)
    try:
        manifest_path = destination / "artifact_manifest.json"
        checksums_path = destination / "SHA256SUMS"
        source_path = destination / "source_identity.json"
        execution_path = destination / "execution_manifest.json"
        audit_dir = destination / "audit"
        required = [manifest_path, checksums_path, source_path, execution_path]
        if not all(path.is_file() for path in required) or not audit_dir.is_dir():
            return False
        if not verify_aoi_uncertainty_artifacts(audit_dir):
            return False

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("schema") != KORTHALS_ARTIFACT_SCHEMA:
            return False
        stored = manifest.get("artifact_manifest_fingerprint")
        core = dict(manifest)
        core.pop("artifact_manifest_fingerprint", None)
        if stored != fingerprint(core):
            return False
        if manifest.get("protocol_fingerprint") != KORTHALS_PROTOCOL_FINGERPRINT:
            return False

        execution_manifest = json.loads(execution_path.read_text(encoding="utf-8"))
        execution_core = dict(execution_manifest)
        execution_fingerprint = execution_core.pop("execution_fingerprint", None)
        if execution_fingerprint != fingerprint(execution_core):
            return False
        if manifest.get("execution_fingerprint") != execution_fingerprint:
            return False
        if manifest.get("classification") != execution_manifest.get("classification"):
            return False

        source_identity = json.loads(source_path.read_text(encoding="utf-8"))
        if source_identity != execution_manifest.get("source_identity"):
            return False
        if source_identity.get("protocol_fingerprint") != KORTHALS_PROTOCOL_FINGERPRINT:
            return False
        if source_identity.get("companion_commit") != KORTHALS_COMPANION_COMMIT:
            return False

        declared = manifest.get("files")
        if not isinstance(declared, list):
            return False
        actual = _recursive_file_records(
            destination,
            exclude={"artifact_manifest.json", "SHA256SUMS"},
        )
        if declared != actual:
            return False

        checksum_map = _parse_checksums(checksums_path)
        expected_paths = {
            path.relative_to(destination).as_posix()
            for path in destination.rglob("*")
            if path.is_file() and path.relative_to(destination).as_posix() != "SHA256SUMS"
        }
        if set(checksum_map) != expected_paths:
            return False
        for relative, digest in checksum_map.items():
            if digest != _sha256_file(destination / relative):
                return False
        return True
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError):
        return False


def _normalize_aligned_data(data: pd.DataFrame) -> pd.DataFrame:
    required = {
        "participant_id",
        "trial_number",
        "trial_time",
        "gaze_x",
        "gaze_y",
        "target_x",
        "target_y",
        "target_type",
        "target_trajectory",
    }
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"aligned_data is missing required columns: {missing}")
    speed_column = "actual_speed" if "actual_speed" in data.columns else "target_speed"
    if speed_column not in data.columns:
        raise ValueError("aligned_data must contain actual_speed or target_speed")

    frame = data.copy()
    frame["participant_id"] = frame["participant_id"].astype(str)
    if frame["participant_id"].str.strip().eq("").any():
        raise ValueError("participant_id must be non-empty")
    numeric = [
        "trial_number",
        "trial_time",
        "gaze_x",
        "gaze_y",
        "target_x",
        "target_y",
        speed_column,
    ]
    for column in numeric:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if frame["trial_number"].isna().any() or frame["trial_time"].isna().any():
        raise ValueError("trial_number and trial_time must be finite")
    trial_values = frame["trial_number"].to_numpy(dtype=float)
    if np.any(trial_values != np.floor(trial_values)):
        raise ValueError("trial_number must be integer-valued")
    frame["trial_number"] = frame["trial_number"].astype(int)
    if not frame["trial_number"].between(1, 144, inclusive="both").all():
        raise ValueError("frozen repetition rule requires trial_number in 1..144")
    if np.any(~np.isfinite(frame["trial_time"].to_numpy(dtype=float))):
        raise ValueError("trial_time must be finite")
    if (frame["trial_time"] < 0.0).any():
        raise ValueError("canonical trial_time must be non-negative")
    target_numeric = frame[["target_x", "target_y", speed_column]].to_numpy(dtype=float)
    if np.any(~np.isfinite(target_numeric)):
        raise ValueError("target coordinates and speed must be finite")
    frame["target_type"] = frame["target_type"].astype(str)
    frame["target_trajectory"] = frame["target_trajectory"].astype(str)
    frame["target_speed"] = frame[speed_column].astype(float)

    keys = ["participant_id", "trial_number"]
    for column in ["target_type", "target_speed", "target_trajectory"]:
        counts = frame.groupby(keys, sort=False)[column].nunique(dropna=False)
        if (counts != 1).any():
            raise ValueError(f"{column} must be constant within participant trial")
    return frame


def _normalize_validations(validations: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "participant_id",
        "validation_nr",
        "error_avg",
        "first_trial",
        "last_trial",
    ]
    missing = sorted(set(columns).difference(validations.columns))
    if missing:
        raise ValueError(f"validations is missing required columns: {missing}")
    frame = validations[columns].copy()
    frame["participant_id"] = frame["participant_id"].astype(str)
    for column in columns[1:]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    one_bound_missing = frame["first_trial"].isna() ^ frame["last_trial"].isna()
    if one_bound_missing.any():
        raise ValueError("validation trial ranges must have both first_trial and last_trial")
    frame = frame.dropna(subset=["first_trial", "last_trial"]).copy()
    if frame.empty:
        raise ValueError("no validation rows map to trial ranges")
    if frame[["validation_nr", "error_avg"]].isna().any().any():
        raise ValueError("mapped validation rows require validation_nr and error_avg")
    if (frame["error_avg"] < 0.0).any() or np.any(~np.isfinite(frame["error_avg"])):
        raise ValueError("error_avg must be finite and non-negative")
    for column in ["validation_nr", "first_trial", "last_trial"]:
        values = frame[column].to_numpy(dtype=float)
        if np.any(values != np.floor(values)):
            raise ValueError(f"{column} must be integer-valued")
        frame[column] = frame[column].astype(int)
    if (frame["first_trial"] > frame["last_trial"]).any():
        raise ValueError("validation first_trial must not exceed last_trial")
    if frame.duplicated(["participant_id", "validation_nr"]).any():
        raise ValueError("participant validation_nr values must be unique")
    return frame.sort_values(
        ["participant_id", "validation_nr"], kind="stable"
    ).reset_index(drop=True)


def _validation_trial_mapping(
    data: pd.DataFrame,
    validations: pd.DataFrame,
) -> dict[tuple[str, int], tuple[int, float]]:
    mapping: dict[tuple[str, int], tuple[int, float]] = {}
    unique_trials = data[["participant_id", "trial_number"]].drop_duplicates()
    grouped = {
        participant: group
        for participant, group in validations.groupby("participant_id", sort=False)
    }
    for row in unique_trials.itertuples(index=False):
        participant = str(row.participant_id)
        trial = int(row.trial_number)
        candidate = grouped.get(participant)
        if candidate is None:
            raise ValueError(f"participant {participant!r} has no validation summaries")
        matches = candidate[
            (candidate["first_trial"] <= trial) & (candidate["last_trial"] >= trial)
        ]
        if len(matches) != 1:
            raise ValueError(
                f"trial {(participant, trial)!r} must map to exactly one validation block"
            )
        match = matches.iloc[0]
        mapping[(participant, trial)] = (
            int(match["validation_nr"]),
            float(match["error_avg"]),
        )
    return mapping


def _downsample_trial_50hz(trial: pd.DataFrame) -> pd.DataFrame:
    ordered = trial.sort_values("trial_time", kind="stable").reset_index(drop=True)
    times = ordered["trial_time"].to_numpy(dtype=float)
    if np.any(np.diff(times) <= 0.0):
        raise ValueError("canonical aligned trial_time must be strictly increasing within trial")
    step = 1.0 / 50.0
    max_time = float(times[-1])
    final = np.floor(max_time / step + 1e-12) * step
    scheduled = np.arange(0.0, final + step / 2.0, step)
    if scheduled.size == 0:
        scheduled = np.array([0.0])

    chosen: list[int] = []
    for target in scheduled:
        right = int(np.searchsorted(times, target, side="left"))
        if right == 0:
            index = 0
        elif right >= len(times):
            index = len(times) - 1
        else:
            left = right - 1
            left_distance = abs(target - times[left])
            right_distance = abs(times[right] - target)
            index = left if left_distance <= right_distance else right
        chosen.append(index)
    if len(set(chosen)) != len(chosen):
        raise ValueError(
            "50-Hz grid selected duplicate source samples; aligned sampling is too sparse"
        )
    sampled = ordered.iloc[chosen].copy().reset_index(drop=True)
    sampled["scheduled_trial_time"] = scheduled
    return sampled


def _endpoint_weights(data: pd.DataFrame) -> np.ndarray:
    required = {
        "participant_id",
        "trial_number",
        "repetition",
        "target_speed",
        "target_trajectory",
        "target_type",
    }
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Korthals endpoint data is missing columns: {missing}")
    if data.empty:
        raise ValueError("Korthals endpoint data must not be empty")

    frame = data.reset_index(drop=True)
    trial_meta = frame[list(required)].drop_duplicates()
    if trial_meta.duplicated(["participant_id", "trial_number"]).any():
        raise ValueError("each participant trial must have one frozen metadata identity")

    cell_keys = ["participant_id", "repetition", "target_speed", "target_trajectory"]
    cells: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {}
    for key, cell in trial_meta.groupby(cell_keys, sort=True, dropna=False):
        counts = cell["target_type"].value_counts()
        if any(int(counts.get(kind, 0)) > 1 for kind in KORTHALS_TARGET_TYPES):
            raise ValueError("matched cells may contain at most one trial per frozen target type")
        if not all(int(counts.get(kind, 0)) == 1 for kind in KORTHALS_TARGET_TYPES):
            continue
        participant = str(key[0])
        moving_trial = int(
            cell.loc[cell["target_type"] == "moving_circle", "trial_number"].iloc[0]
        )
        jumping_trial = int(
            cell.loc[cell["target_type"] == "jumping_circle", "trial_number"].iloc[0]
        )
        participant_values = frame["participant_id"].astype(str).to_numpy()
        trial_values = frame["trial_number"].to_numpy(dtype=int)
        moving_rows = np.flatnonzero(
            (participant_values == participant) & (trial_values == moving_trial)
        )
        jumping_rows = np.flatnonzero(
            (participant_values == participant) & (trial_values == jumping_trial)
        )
        if len(moving_rows) == 0 or len(jumping_rows) == 0:
            raise ValueError("complete matched-cell trials must contain retained samples")
        cells.setdefault(participant, []).append((moving_rows, jumping_rows))

    participants = sorted(set(frame["participant_id"].astype(str)))
    if set(cells) != set(participants):
        missing_participants = sorted(set(participants).difference(cells))
        raise ValueError(
            "participants without complete matched cells fail closed: "
            f"{missing_participants}"
        )

    weights = np.zeros(len(frame), dtype=float)
    study_scale = 1.0 / len(participants)
    for participant in participants:
        pairs = cells[participant]
        cell_scale = study_scale / len(pairs)
        for moving_rows, jumping_rows in pairs:
            weights[moving_rows] -= cell_scale / len(moving_rows)
            weights[jumping_rows] += cell_scale / len(jumping_rows)
    return weights


def _validate_membership(membership: np.ndarray, n_rows: int) -> np.ndarray:
    values = np.asarray(membership, dtype=float)
    if values.ndim != 1 or len(values) != n_rows:
        raise ValueError("membership must be one-dimensional and match data rows")
    if np.any(~np.isfinite(values)) or np.any((values < 0.0) | (values > 1.0)):
        raise ValueError("membership must contain finite values between 0 and 1")
    return values


def _validate_prepared_identity(
    prepared: PreparedKorthalsData,
    protocol: Mapping[str, Any],
) -> None:
    identity = prepared.source_identity
    if identity.get("protocol_fingerprint") != KORTHALS_PROTOCOL_FINGERPRINT:
        raise ValueError("prepared source identity does not match the frozen protocol")
    if identity.get("companion_commit") != KORTHALS_COMPANION_COMMIT:
        raise ValueError("prepared source identity does not match the frozen companion commit")
    required = {
        "participant_id",
        "trial_number",
        "repetition",
        "target_speed",
        "target_trajectory",
        "target_type",
        "observed_x",
        "observed_y",
        "error_group",
    }
    missing = sorted(required.difference(prepared.data.columns))
    if missing:
        raise ValueError(f"prepared Korthals data is missing columns: {missing}")
    if set(prepared.data["target_type"].unique()) != set(KORTHALS_TARGET_TYPES):
        raise ValueError("prepared Korthals data has unexpected target types")
    if int(protocol["validation"]["n_validation_points"]) != 9:
        raise ValueError("frozen Korthals validation model requires nine points")
    _endpoint_weights(prepared.data)


def _classify_korthals_result(summary: pd.Series) -> str:
    hard = float(summary["hard_effect"])
    above = float(summary["probability_above_reference"])
    below = float(summary["probability_below_reference"])
    if hard > 0.0 and above >= 0.95:
        return "robust_positive"
    if hard < 0.0 and below >= 0.95:
        return "robust_negative"
    return "measurement_sensitive"


def _recursive_file_records(
    destination: Path,
    *,
    exclude: set[str] | None = None,
) -> list[dict[str, Any]]:
    excluded = set() if exclude is None else exclude
    records: list[dict[str, Any]] = []
    for path in sorted(path for path in destination.rglob("*") if path.is_file()):
        relative = path.relative_to(destination).as_posix()
        if relative in excluded:
            continue
        records.append(
            {
                "path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    return records


def _write_json(path: Path, value: Any) -> None:
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_checksums(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise ValueError("invalid SHA256SUMS entry")
        digest, relative = parts
        candidate = Path(relative)
        if candidate.is_absolute() or ".." in candidate.parts or relative in values:
            raise ValueError("invalid or duplicate SHA256SUMS path")
        values[relative] = digest
    return values
