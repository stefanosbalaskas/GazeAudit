"""Outcome-blind protocol-v2 intake for the Korthals et al. case study.

Protocol v1 remains immutable. Version 2 changes only the missingness rule discovered
by source-readiness testing before any scientific AOI endpoint was executed: when a
task trial has zero finite gaze samples on the already-frozen 50-Hz grid, its whole
moving/jumping matched cell is removed symmetrically. No gaze sample is substituted,
interpolated, phase-shifted, or otherwise recovered.
"""

from __future__ import annotations

import importlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .aoi_protocol import verify_aoi_uncertainty_protocol
from .korthals_execution import (
    KORTHALS_CASE_STUDY_ID as KORTHALS_V1_CASE_STUDY_ID,
    KORTHALS_COMPANION_COMMIT,
    KORTHALS_PROTOCOL_FINGERPRINT as KORTHALS_V1_PROTOCOL_FINGERPRINT,
    KORTHALS_TARGET_TYPES,
    PreparedKorthalsData,
    _downsample_trial_50hz,
    _normalize_aligned_data,
    _normalize_validations,
    _require_complete_trial_pairing,
    _validation_trial_mapping,
    prepare_korthals_aligned_data as _prepare_korthals_aligned_data_v1,
)
from .korthals_source import (
    KORTHALS_SOURCE_SCHEMA,
    _align_companion_preprocessed_participant,
    _canonicalize_companion_participant_identity,
    _file_record,
    _parse_checksums,
    _require_clean_tables,
    _scope_authoritative_task_trials,
    _sha256_file,
    _validated_data_root,
    _working_directory,
    _write_json,
    build_korthals_source_manifest as _build_korthals_source_manifest_v1,
    verify_korthals_source_manifest as _verify_korthals_source_manifest_v1,
)
from .provenance import canonical_json, fingerprint

KORTHALS_V2_CASE_STUDY_ID = "korthals2026-target-tracking-aoi-v2"
KORTHALS_V2_PROTOCOL_FINGERPRINT = (
    "1cd4150c9341db145b8f6aee544f9634c67c46116e61e7e675ae3c50282d2d55"
)
KORTHALS_V2_SOURCE_INTAKE_SCHEMA = "gazeaudit-korthals-source-intake-artifacts-v2"
KORTHALS_V2_PROTOCOL_FILE = "korthals2026_target_tracking_aoi_v2.json"
KORTHALS_V2_MISSINGNESS_POLICY = "drop_entire_zero-finite_matched_cell_without_replacement"


@dataclass(frozen=True)
class KorthalsSourceIntakeV2:
    """Source inventory plus protocol-v2 prepared rows, without endpoint execution."""

    prepared: PreparedKorthalsData
    source_manifest: dict[str, Any]
    participant_splits: tuple[tuple[str, str], ...]


def load_korthals_protocol_v2() -> dict[str, Any]:
    """Load the packaged outcome-blind protocol-v2 amendment."""

    text = (
        resources.files("gazeaudit.data")
        .joinpath(KORTHALS_V2_PROTOCOL_FILE)
        .read_text(encoding="utf-8")
    )
    document = json.loads(text)
    if not isinstance(document, dict):
        raise ValueError("packaged Korthals protocol v2 must be a JSON object")
    return document


def verify_korthals_protocol_v2(
    document: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify protocol v2 and all scientific choices that were not amended."""

    protocol = load_korthals_protocol_v2() if document is None else dict(document)
    if not verify_aoi_uncertainty_protocol(protocol):
        raise ValueError("Korthals protocol v2 failed generic protocol verification")
    checks = {
        "fingerprint": (
            protocol.get("protocol_fingerprint") == KORTHALS_V2_PROTOCOL_FINGERPRINT
        ),
        "case_study": protocol.get("case_study_id") == KORTHALS_V2_CASE_STUDY_ID,
        "companion_commit": (
            protocol["dataset"].get("companion_commit") == KORTHALS_COMPANION_COMMIT
        ),
        "target_types": (
            tuple(protocol["dataset"].get("trial_types", ())) == KORTHALS_TARGET_TYPES
        ),
        "sampling_hz": (
            float(protocol["dataset"]["sampling"].get("target_hz", -1.0)) == 50.0
        ),
        "missingness_policy": (
            protocol["dataset"]["sampling"].get("zero_finite_trial_policy")
            == (
                "if a retained task trial has zero finite gaze samples after the fixed "
                "50-Hz scheduled-grid selection, remove its entire matched cell without "
                "imputation or replacement; every participant must retain at least one "
                "complete matched cell"
            )
        ),
        "validation_group": (
            tuple(protocol["validation"].get("grouping", ()))
            == ("participant_id", "validation_nr")
        ),
        "validation_metric": protocol["validation"].get("metric") == "error_avg",
        "aoi_geometry": protocol["aoi"].get("geometry") == "circle",
        "aoi_radius": float(protocol["aoi"].get("radius", -1.0)) == 1.0,
        "matched_cell": (
            tuple(protocol["endpoint"].get("matched_cell", ()))
            == ("participant_id", "repetition", "target_speed", "target_trajectory")
        ),
        "cell_contrast": (
            protocol["endpoint"].get("cell_contrast")
            == "jumping_circle occupancy minus moving_circle occupancy"
        ),
        "draws": int(protocol["monte_carlo"].get("draws", -1)) == 2000,
        "batch_size": int(protocol["monte_carlo"].get("batch_size", -1)) == 8,
        "seed": int(protocol["monte_carlo"].get("rng_seed", -1)) == 20260316,
        "supersedes_v1": (
            protocol.get("amendment", {}).get("supersedes_protocol_fingerprint")
            == KORTHALS_V1_PROTOCOL_FINGERPRINT
        ),
        "outcome_blind": (
            protocol.get("amendment", {}).get("outcome_blind") is True
            and protocol.get("amendment", {}).get(
                "scientific_endpoint_executed_before_amendment"
            )
            is False
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"Korthals protocol v2 failed frozen guardrails: {failed}")
    return protocol


def build_korthals_source_manifest_v2(
    data_root: str | Path = "data",
) -> dict[str, Any]:
    """Build the same byte inventory as v1, rebound to protocol v2."""

    base = _build_korthals_source_manifest_v1(data_root)
    core = dict(base)
    core.pop("source_manifest_fingerprint", None)
    core["case_study_id"] = KORTHALS_V2_CASE_STUDY_ID
    core["protocol_fingerprint"] = KORTHALS_V2_PROTOCOL_FINGERPRINT
    document = dict(core)
    document["source_manifest_fingerprint"] = fingerprint(core)
    if not verify_korthals_source_manifest_v2(document):
        raise RuntimeError("newly built Korthals v2 source manifest failed verification")
    return document


def verify_korthals_source_manifest_v2(document: Mapping[str, Any]) -> bool:
    """Verify a v2 source manifest while reusing the proven v1 byte-contract checks."""

    try:
        normalized = json.loads(canonical_json(document))
        if normalized.get("schema") != KORTHALS_SOURCE_SCHEMA:
            return False
        if normalized.get("case_study_id") != KORTHALS_V2_CASE_STUDY_ID:
            return False
        if normalized.get("protocol_fingerprint") != KORTHALS_V2_PROTOCOL_FINGERPRINT:
            return False
        stored = normalized.pop("source_manifest_fingerprint", None)
        if stored != fingerprint(normalized):
            return False

        compatibility = dict(normalized)
        compatibility["case_study_id"] = KORTHALS_V1_CASE_STUDY_ID
        compatibility["protocol_fingerprint"] = KORTHALS_V1_PROTOCOL_FINGERPRINT
        compatibility["source_manifest_fingerprint"] = fingerprint(compatibility)
        return _verify_korthals_source_manifest_v1(compatibility)
    except (TypeError, ValueError, KeyError, json.JSONDecodeError):
        return False


def prepare_korthals_aligned_data_v2(
    aligned_data: pd.DataFrame,
    validations: pd.DataFrame,
    *,
    source_identity: Mapping[str, Any] | None = None,
    protocol_document: Mapping[str, Any] | None = None,
) -> PreparedKorthalsData:
    """Prepare v2 data without changing the frozen grid or recovering missing gaze.

    The full source is first checked for the same pre-exclusion matched-cell completeness
    required by v1. After the declared author exclusion, every trial is sampled on the
    same fixed 50-Hz grid. A trial with zero finite selected gaze samples makes its
    entire matched cell structurally unestimable, so both target-type members are
    removed before the unchanged v1 preparation machinery is applied.
    """

    protocol = verify_korthals_protocol_v2(protocol_document)
    if not isinstance(aligned_data, pd.DataFrame) or aligned_data.empty:
        raise ValueError("aligned_data must be a non-empty pandas DataFrame")
    if not isinstance(validations, pd.DataFrame):
        raise TypeError("validations must be a pandas DataFrame")

    protected_v2 = {
        "case_study_id",
        "protocol_fingerprint",
        "protocol_amendment_from",
        "zero_finite_scheduled_trial_count",
        "zero_finite_scheduled_trials",
        "sampling_incomplete_matched_cell_count",
        "sampling_incomplete_matched_cells",
        "missingness_policy",
    }
    supplied_identity = (
        {} if source_identity is None else json.loads(canonical_json(source_identity))
    )
    if not isinstance(supplied_identity, dict):
        raise TypeError("source_identity must normalize to an object")
    forbidden = protected_v2.intersection(supplied_identity)
    if forbidden:
        raise ValueError(
            "source_identity may not override protocol-v2 identity fields: "
            f"{sorted(forbidden)}"
        )

    normalized = _normalize_aligned_data(aligned_data)

    pre_exclusion = normalized[
        normalized["target_type"].isin(KORTHALS_TARGET_TYPES)
    ].copy()
    if pre_exclusion.empty:
        raise ValueError("no frozen moving/jumping-circle rows are present")
    pre_exclusion["repetition"] = np.where(
        pre_exclusion["trial_number"] <= 72, 1, 2
    ).astype(int)
    _require_complete_trial_pairing(pre_exclusion)

    exclusion = protocol["dataset"]["author_directed_exclusion"]
    excluded = (
        (normalized["participant_id"] == str(exclusion["participant_id"]))
        & normalized["trial_number"].between(
            int(exclusion["trial_number_start"]),
            int(exclusion["trial_number_end"]),
            inclusive="both",
        )
    )
    eligible = normalized.loc[~excluded].copy()
    eligible = eligible[eligible["target_type"].isin(KORTHALS_TARGET_TYPES)].copy()
    if eligible.empty:
        raise ValueError("no frozen moving/jumping-circle rows remain after filtering")
    eligible["repetition"] = np.where(
        eligible["trial_number"] <= 72, 1, 2
    ).astype(int)

    # Preserve v1's fail-closed validation contract before any missingness-based
    # matched-cell removal. A zero-finite trial may not hide an unmapped validation.
    normalized_validations = _normalize_validations(validations)
    _validation_trial_mapping(eligible, normalized_validations)

    sampled_parts = [
        _downsample_trial_50hz(trial)
        for _, trial in eligible.groupby(["participant_id", "trial_number"], sort=True)
    ]
    sampled = pd.concat(sampled_parts, ignore_index=True)
    target = sampled[["target_x", "target_y"]].to_numpy(dtype=float)
    if np.any(~np.isfinite(target)):
        raise ValueError("target coordinates must remain finite on the scheduled grid")
    gaze = sampled[["gaze_x", "gaze_y"]].to_numpy(dtype=float)
    finite = np.isfinite(gaze).all(axis=1)

    expected_trials = set(
        zip(
            eligible["participant_id"].astype(str),
            eligible["trial_number"].astype(int),
            strict=True,
        )
    )
    finite_sampled = sampled.loc[finite]
    observed_trials = set(
        zip(
            finite_sampled["participant_id"].astype(str),
            finite_sampled["trial_number"].astype(int),
            strict=True,
        )
    )
    zero_trials = sorted(expected_trials.difference(observed_trials))

    trial_meta = (
        eligible[
            [
                "participant_id",
                "trial_number",
                "repetition",
                "target_speed",
                "target_trajectory",
                "target_type",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    if trial_meta.duplicated(["participant_id", "trial_number"]).any():
        raise ValueError("each participant trial must have one frozen metadata identity")

    incomplete_cells: list[dict[str, Any]] = []
    drop_trial_keys: set[tuple[str, int]] = set()

    for participant_id, trial_number in zero_trials:
        row = trial_meta[
            (trial_meta["participant_id"].astype(str) == str(participant_id))
            & (trial_meta["trial_number"].astype(int) == int(trial_number))
        ]
        if len(row) != 1:
            raise ValueError(
                f"zero-finite trial {(participant_id, trial_number)!r} has ambiguous metadata"
            )
        first = row.iloc[0]
        mask = (
            (trial_meta["participant_id"].astype(str) == str(participant_id))
            & (trial_meta["repetition"].astype(int) == int(first["repetition"]))
            & (trial_meta["target_speed"].astype(float) == float(first["target_speed"]))
            & (
                trial_meta["target_trajectory"].astype(str)
                == str(first["target_trajectory"])
            )
        )
        cell = trial_meta.loc[mask].copy()
        counts = cell["target_type"].value_counts()
        if any(int(counts.get(kind, 0)) != 1 for kind in KORTHALS_TARGET_TYPES):
            raise ValueError(
                "zero-finite trial does not belong to one complete frozen matched cell"
            )
        drop_trial_keys.update(
            (str(item.participant_id), int(item.trial_number))
            for item in cell.itertuples(index=False)
        )
        cell_record = {
            "participant_id": str(participant_id),
            "repetition": int(first["repetition"]),
            "target_speed": float(first["target_speed"]),
            "target_trajectory": str(first["target_trajectory"]),
            "trial_numbers": sorted(cell["trial_number"].astype(int).tolist()),
        }
        if cell_record not in incomplete_cells:
            incomplete_cells.append(cell_record)

    incomplete_cells = sorted(
        incomplete_cells,
        key=lambda item: (
            item["participant_id"],
            item["repetition"],
            item["target_speed"],
            item["target_trajectory"],
        ),
    )
    zero_trial_records = [
        {"participant_id": str(participant), "trial_number": int(trial)}
        for participant, trial in zero_trials
    ]

    if drop_trial_keys:
        keep = np.fromiter(
            (
                (str(participant), int(trial)) not in drop_trial_keys
                for participant, trial in zip(
                    normalized["participant_id"],
                    normalized["trial_number"],
                    strict=True,
                )
            ),
            dtype=bool,
            count=len(normalized),
        )
        analysis_source = normalized.loc[keep].copy()
    else:
        analysis_source = normalized.copy()

    base = _prepare_korthals_aligned_data_v1(
        analysis_source,
        validations,
        source_identity=supplied_identity,
    )

    expected_participants = sorted(eligible["participant_id"].astype(str).unique().tolist())
    retained_participants = sorted(base.data["participant_id"].astype(str).unique().tolist())
    if retained_participants != expected_participants:
        missing = sorted(set(expected_participants).difference(retained_participants))
        raise ValueError(
            "protocol v2 requires every participant to retain at least one complete "
            f"matched cell; lost participants: {missing}"
        )

    identity = dict(base.source_identity)
    identity["case_study_id"] = KORTHALS_V2_CASE_STUDY_ID
    identity["protocol_fingerprint"] = KORTHALS_V2_PROTOCOL_FINGERPRINT
    identity["protocol_amendment_from"] = KORTHALS_V1_PROTOCOL_FINGERPRINT
    identity["missingness_policy"] = KORTHALS_V2_MISSINGNESS_POLICY
    identity["zero_finite_scheduled_trial_count"] = len(zero_trial_records)
    identity["zero_finite_scheduled_trials"] = zero_trial_records
    identity["sampling_incomplete_matched_cell_count"] = len(incomplete_cells)
    identity["sampling_incomplete_matched_cells"] = incomplete_cells

    return PreparedKorthalsData(
        data=base.data,
        validation_groups=base.validation_groups,
        source_identity=identity,
    )


def prepare_korthals_from_companion_v2(
    data_root: str | Path = "data",
    *,
    participant_factory: Callable[..., Any] | None = None,
    preprocessor_factory: Callable[[], Any] | None = None,
) -> KorthalsSourceIntakeV2:
    """Run the exact companion preprocessing path and bind it to protocol v2."""

    root = _validated_data_root(data_root)
    if root.name != "data":
        raise ValueError("companion intake requires a source directory named exactly 'data'")
    source_manifest = build_korthals_source_manifest_v2(root)

    if participant_factory is None or preprocessor_factory is None:
        participant_module = importlib.import_module("eyemovement_data.participant")
        preprocessor_module = importlib.import_module("eyemovement_data.preprocessor")
        if participant_factory is None:
            participant_factory = participant_module.Participant
        if preprocessor_factory is None:
            preprocessor_factory = preprocessor_module.OriginalPreprocessor

    participants = list(source_manifest["participants"])
    aligned_parts: list[pd.DataFrame] = []
    validation_parts: list[pd.DataFrame] = []
    splits: list[tuple[str, str]] = []

    with _working_directory(root.parent):
        relative_root = Path("data")
        for participant_id in participants:
            participant = participant_factory(
                id=participant_id,
                preprocessor=preprocessor_factory(),
            )
            participant.set_clean_data(str(relative_root / "clean"))
            _require_clean_tables(participant_id, participant.clean_data)
            _canonicalize_companion_participant_identity(
                relative_root / "clean",
                participant_id,
                participant.clean_data,
            )
            participant.preprocess_clean_data(
                blink_offset=(50, 50),
                rolling_mean_window=1,
            )
            aligned_parts.append(
                _align_companion_preprocessed_participant(
                    participant_id,
                    participant.preprocessed_data,
                )
            )
            validation = participant.validation_check(str(relative_root / "raw"))
            if not isinstance(validation, pd.DataFrame) or validation.empty:
                raise ValueError(
                    f"participant {participant_id!r} produced no validation summaries"
                )
            validation_parts.append(validation.copy())
            split = str(getattr(participant, "subset", "unknown_subset"))
            if split not in {"train", "test"}:
                raise ValueError(
                    f"participant {participant_id!r} has unresolved train/test split"
                )
            splits.append((participant_id, split))

    aligned = pd.concat(aligned_parts, ignore_index=True)
    aligned = _scope_authoritative_task_trials(aligned)
    validations = pd.concat(validation_parts, ignore_index=True)
    ordered_splits = tuple(sorted(splits))
    split_records = [
        {"participant_id": participant_id, "split": split}
        for participant_id, split in ordered_splits
    ]
    source_identity = {
        "source_manifest_fingerprint": source_manifest["source_manifest_fingerprint"],
        "source_file_count": source_manifest["file_count"],
        "download_contract": source_manifest["download_contract"],
        "participant_split_fingerprint": fingerprint(split_records),
        "participant_splits": split_records,
    }
    prepared = prepare_korthals_aligned_data_v2(
        aligned,
        validations,
        source_identity=source_identity,
    )
    if prepared.source_identity["participant_count"] != len(participants):
        raise ValueError("prepared participant count differs from source-manifest cohort")
    return KorthalsSourceIntakeV2(
        prepared=prepared,
        source_manifest=source_manifest,
        participant_splits=ordered_splits,
    )


def write_korthals_source_intake_artifacts_v2(
    intake: KorthalsSourceIntakeV2,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Archive protocol-v2 source identity and readiness diagnostics, no outcomes."""

    if not isinstance(intake, KorthalsSourceIntakeV2):
        raise TypeError("intake must be KorthalsSourceIntakeV2")
    if not verify_korthals_source_manifest_v2(intake.source_manifest):
        raise ValueError("intake source manifest is invalid")

    destination = Path(output_dir)
    if destination.exists() and not destination.is_dir():
        raise ValueError("output_dir must be a directory path")
    destination.mkdir(parents=True, exist_ok=True)
    existing = list(destination.iterdir())
    if existing and not overwrite:
        raise FileExistsError("output_dir is not empty; pass overwrite=True to replace")
    if overwrite:
        for path in existing:
            if path.is_dir():
                raise ValueError("overwrite=True refuses nested directories")
            path.unlink()

    prepared = intake.prepared
    trial_count = int(
        len(prepared.data[["participant_id", "trial_number"]].drop_duplicates())
    )
    summary = {
        "case_study_id": KORTHALS_V2_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "protocol_amendment_from": KORTHALS_V1_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": intake.source_manifest[
            "source_manifest_fingerprint"
        ],
        "participant_count": int(prepared.source_identity["participant_count"]),
        "prepared_row_count": int(len(prepared.data)),
        "retained_trial_count": trial_count,
        "validation_group_count": int(len(prepared.validation_groups)),
        "target_types": sorted(prepared.data["target_type"].unique().tolist()),
        "participant_split_fingerprint": prepared.source_identity[
            "participant_split_fingerprint"
        ],
        "missingness_policy": prepared.source_identity["missingness_policy"],
        "zero_finite_scheduled_trial_count": prepared.source_identity[
            "zero_finite_scheduled_trial_count"
        ],
        "zero_finite_scheduled_trials": prepared.source_identity[
            "zero_finite_scheduled_trials"
        ],
        "sampling_incomplete_matched_cell_count": prepared.source_identity[
            "sampling_incomplete_matched_cell_count"
        ],
        "sampling_incomplete_matched_cells": prepared.source_identity[
            "sampling_incomplete_matched_cells"
        ],
    }
    _write_json(destination / "source_manifest.json", intake.source_manifest)
    _write_json(destination / "intake_summary.json", summary)

    file_records = [
        _file_record(destination / "intake_summary.json", destination),
        _file_record(destination / "source_manifest.json", destination),
    ]
    core = {
        "schema": KORTHALS_V2_SOURCE_INTAKE_SCHEMA,
        "case_study_id": KORTHALS_V2_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": intake.source_manifest[
            "source_manifest_fingerprint"
        ],
        "files": file_records,
    }
    manifest = dict(core)
    manifest["artifact_manifest_fingerprint"] = fingerprint(core)
    _write_json(destination / "artifact_manifest.json", manifest)

    checksum_targets = sorted(path for path in destination.iterdir() if path.is_file())
    lines = [f"{_sha256_file(path)}  {path.name}" for path in checksum_targets]
    (destination / "SHA256SUMS").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    if not verify_korthals_source_intake_artifacts_v2(destination):
        raise RuntimeError("newly written Korthals v2 source intake failed verification")
    return manifest


def verify_korthals_source_intake_artifacts_v2(output_dir: str | Path) -> bool:
    """Return whether the endpoint-blind protocol-v2 intake is intact."""

    destination = Path(output_dir)
    try:
        expected = {
            "source_manifest.json",
            "intake_summary.json",
            "artifact_manifest.json",
            "SHA256SUMS",
        }
        actual = {path.name for path in destination.iterdir() if path.is_file()}
        if actual != expected:
            return False
        source = json.loads(
            (destination / "source_manifest.json").read_text(encoding="utf-8")
        )
        if not verify_korthals_source_manifest_v2(source):
            return False
        summary = json.loads(
            (destination / "intake_summary.json").read_text(encoding="utf-8")
        )
        manifest = json.loads(
            (destination / "artifact_manifest.json").read_text(encoding="utf-8")
        )
        if manifest.get("schema") != KORTHALS_V2_SOURCE_INTAKE_SCHEMA:
            return False
        if manifest.get("case_study_id") != KORTHALS_V2_CASE_STUDY_ID:
            return False
        if manifest.get("protocol_fingerprint") != KORTHALS_V2_PROTOCOL_FINGERPRINT:
            return False
        if summary.get("case_study_id") != KORTHALS_V2_CASE_STUDY_ID:
            return False
        if summary.get("protocol_fingerprint") != KORTHALS_V2_PROTOCOL_FINGERPRINT:
            return False
        stored = manifest.get("artifact_manifest_fingerprint")
        core = dict(manifest)
        core.pop("artifact_manifest_fingerprint", None)
        if stored != fingerprint(core):
            return False
        source_fingerprint = source.get("source_manifest_fingerprint")
        if manifest.get("source_manifest_fingerprint") != source_fingerprint:
            return False
        if summary.get("source_manifest_fingerprint") != source_fingerprint:
            return False
        declared = manifest.get("files")
        expected_records = [
            _file_record(destination / "intake_summary.json", destination),
            _file_record(destination / "source_manifest.json", destination),
        ]
        if declared != expected_records:
            return False
        checksums = _parse_checksums(destination / "SHA256SUMS")
        if set(checksums) != {
            "artifact_manifest.json",
            "intake_summary.json",
            "source_manifest.json",
        }:
            return False
        return all(
            digest == _sha256_file(destination / name)
            for name, digest in checksums.items()
        )
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError):
        return False
