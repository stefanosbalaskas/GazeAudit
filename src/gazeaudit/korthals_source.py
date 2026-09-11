"""Public-source intake for the frozen Korthals et al. AOI case study.

This module stops deliberately *before* the scientific AOI endpoint. It inventories the
published OSF raw/clean files, executes the companion repository's canonical
``Participant`` + ``OriginalPreprocessor`` path, extracts the raw EyeLink validation
summaries through ``Participant.validation_check()``, and hands the resulting aligned
rows to :func:`prepare_korthals_aligned_data`.

The separation is intentional: a source fingerprint can be archived and frozen before
the first public-data scientific endpoint is ever evaluated.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
from collections.abc import Callable, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .korthals_execution import (
    KORTHALS_CASE_STUDY_ID,
    KORTHALS_COMPANION_COMMIT,
    KORTHALS_PROTOCOL_FINGERPRINT,
    PreparedKorthalsData,
    prepare_korthals_aligned_data,
)
from .provenance import canonical_json, fingerprint

KORTHALS_SOURCE_SCHEMA = "gazeaudit-korthals-source-manifest-v1"
KORTHALS_SOURCE_INTAKE_SCHEMA = "gazeaudit-korthals-source-intake-artifacts-v1"
KORTHALS_OSF_PROJECT = "zx7hc"
KORTHALS_OSF_DOI = "10.17605/OSF.IO/ZX7HC"


@dataclass(frozen=True)
class KorthalsSourceIntake:
    """Source inventory plus protocol-prepared rows, without endpoint execution."""

    prepared: PreparedKorthalsData
    source_manifest: dict[str, Any]
    participant_splits: tuple[tuple[str, str], ...]


def discover_korthals_participants(data_root: str | Path = "data") -> list[str]:
    """Return sorted participant IDs represented in the published clean CSV tree."""

    root = _validated_data_root(data_root)
    clean_root = root / "clean"
    if not clean_root.is_dir():
        raise FileNotFoundError("Korthals source intake requires data/clean")
    participant_ids = {
        path.name.split("_", 1)[0]
        for path in clean_root.rglob("*.csv")
        if "_" in path.name and path.is_file()
    }
    values = sorted(value for value in participant_ids if value)
    if not values:
        raise ValueError("no participant IDs were discovered in data/clean")
    return values


def build_korthals_source_manifest(data_root: str | Path = "data") -> dict[str, Any]:
    """Build a deterministic raw+clean OSF source inventory before preprocessing."""

    root = _validated_data_root(data_root)
    raw_root = root / "raw"
    clean_root = root / "clean"
    if not raw_root.is_dir() or not clean_root.is_dir():
        raise FileNotFoundError("Korthals source intake requires both data/raw and data/clean")

    participant_ids = discover_korthals_participants(root)
    files: list[dict[str, Any]] = []
    for source_dir in (raw_root, clean_root):
        for path in sorted(candidate for candidate in source_dir.rglob("*") if candidate.is_file()):
            files.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "size_bytes": int(path.stat().st_size),
                    "sha256": _sha256_file(path),
                }
            )
    if not files:
        raise ValueError("Korthals source tree contains no raw/clean files")

    core = {
        "schema": KORTHALS_SOURCE_SCHEMA,
        "case_study_id": KORTHALS_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "osf_project": KORTHALS_OSF_PROJECT,
        "osf_doi": KORTHALS_OSF_DOI,
        "companion_commit": KORTHALS_COMPANION_COMMIT,
        "download_contract": {
            "raw_clean": "both",
            "train_test": "both",
            "participants": "all",
        },
        "participants": participant_ids,
        "participant_count": len(participant_ids),
        "files": files,
        "file_count": len(files),
    }
    document = dict(core)
    document["source_manifest_fingerprint"] = fingerprint(core)
    return document


def verify_korthals_source_manifest(document: Mapping[str, Any]) -> bool:
    """Return whether a source manifest is internally complete and fingerprint-valid."""

    try:
        normalized = json.loads(canonical_json(document))
        if normalized.get("schema") != KORTHALS_SOURCE_SCHEMA:
            return False
        if normalized.get("case_study_id") != KORTHALS_CASE_STUDY_ID:
            return False
        if normalized.get("protocol_fingerprint") != KORTHALS_PROTOCOL_FINGERPRINT:
            return False
        if normalized.get("companion_commit") != KORTHALS_COMPANION_COMMIT:
            return False
        if normalized.get("osf_project") != KORTHALS_OSF_PROJECT:
            return False
        if normalized.get("osf_doi") != KORTHALS_OSF_DOI:
            return False
        stored = normalized.pop("source_manifest_fingerprint", None)
        if stored != fingerprint(normalized):
            return False
        participants = normalized.get("participants")
        files = normalized.get("files")
        if not isinstance(participants, list) or participants != sorted(set(participants)):
            return False
        if int(normalized.get("participant_count", -1)) != len(participants):
            return False
        if not isinstance(files, list) or not files:
            return False
        if int(normalized.get("file_count", -1)) != len(files):
            return False
        paths: set[str] = set()
        for record in files:
            if not isinstance(record, dict):
                return False
            path = str(record.get("path", ""))
            candidate = Path(path)
            if (
                not path
                or candidate.is_absolute()
                or ".." in candidate.parts
                or path in paths
                or not (path.startswith("raw/") or path.startswith("clean/"))
            ):
                return False
            paths.add(path)
            digest = record.get("sha256")
            if not isinstance(digest, str) or len(digest) != 64:
                return False
            if int(record.get("size_bytes", -1)) < 0:
                return False
        return True
    except (TypeError, ValueError, KeyError, json.JSONDecodeError):
        return False


def prepare_korthals_from_companion(
    data_root: str | Path = "data",
    *,
    participant_factory: Callable[..., Any] | None = None,
    preprocessor_factory: Callable[[], Any] | None = None,
) -> KorthalsSourceIntake:
    """Run the authors' canonical preprocessing/validation path without an endpoint.

    The real-data path requires the source directory to be named exactly ``data``
    because the companion ``Participant`` constructor itself discovers train/test split
    membership below that relative directory. Test doubles may be injected through the
    two factory parameters; the default path imports the companion package lazily.
    """

    root = _validated_data_root(data_root)
    if root.name != "data":
        raise ValueError("companion intake requires a source directory named exactly 'data'")
    source_manifest = build_korthals_source_manifest(root)
    if not verify_korthals_source_manifest(source_manifest):
        raise RuntimeError("newly built Korthals source manifest failed verification")

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
    prepared = prepare_korthals_aligned_data(
        aligned,
        validations,
        source_identity=source_identity,
    )
    if prepared.source_identity["participant_count"] != len(participants):
        raise ValueError("prepared participant count differs from source-manifest cohort")
    return KorthalsSourceIntake(
        prepared=prepared,
        source_manifest=source_manifest,
        participant_splits=ordered_splits,
    )


def write_korthals_source_intake_artifacts(
    intake: KorthalsSourceIntake,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Archive source identity and preprocessing counts without scientific outcomes."""

    if not isinstance(intake, KorthalsSourceIntake):
        raise TypeError("intake must be KorthalsSourceIntake")
    if not verify_korthals_source_manifest(intake.source_manifest):
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
        "case_study_id": KORTHALS_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": intake.source_manifest["source_manifest_fingerprint"],
        "participant_count": int(prepared.source_identity["participant_count"]),
        "prepared_row_count": int(len(prepared.data)),
        "retained_trial_count": trial_count,
        "validation_group_count": int(len(prepared.validation_groups)),
        "target_types": sorted(prepared.data["target_type"].unique().tolist()),
        "participant_split_fingerprint": prepared.source_identity[
            "participant_split_fingerprint"
        ],
    }
    _write_json(destination / "source_manifest.json", intake.source_manifest)
    _write_json(destination / "intake_summary.json", summary)

    file_records = [
        _file_record(destination / "intake_summary.json", destination),
        _file_record(destination / "source_manifest.json", destination),
    ]
    core = {
        "schema": KORTHALS_SOURCE_INTAKE_SCHEMA,
        "case_study_id": KORTHALS_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": intake.source_manifest["source_manifest_fingerprint"],
        "files": file_records,
    }
    manifest = dict(core)
    manifest["artifact_manifest_fingerprint"] = fingerprint(core)
    _write_json(destination / "artifact_manifest.json", manifest)

    checksum_targets = sorted(path for path in destination.iterdir() if path.is_file())
    lines = [f"{_sha256_file(path)}  {path.name}" for path in checksum_targets]
    (destination / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not verify_korthals_source_intake_artifacts(destination):
        raise RuntimeError("newly written Korthals source intake failed verification")
    return manifest


def verify_korthals_source_intake_artifacts(output_dir: str | Path) -> bool:
    """Return whether a source-intake artifact set is complete and unmodified."""

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
        source = json.loads((destination / "source_manifest.json").read_text(encoding="utf-8"))
        if not verify_korthals_source_manifest(source):
            return False
        summary = json.loads((destination / "intake_summary.json").read_text(encoding="utf-8"))
        manifest = json.loads((destination / "artifact_manifest.json").read_text(encoding="utf-8"))
        if manifest.get("schema") != KORTHALS_SOURCE_INTAKE_SCHEMA:
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


def _align_companion_preprocessed_participant(
    participant_id: str,
    preprocessed: Mapping[str, Any],
) -> pd.DataFrame:
    required = {"gaze", "targets", "trials"}
    missing = sorted(required.difference(preprocessed))
    if missing:
        raise ValueError(
            f"participant {participant_id!r} preprocessed data is missing: {missing}"
        )
    gaze = _participant_frame(preprocessed["gaze"], participant_id, "gaze")
    targets = _participant_frame(preprocessed["targets"], participant_id, "targets")
    trials = _participant_frame(preprocessed["trials"], participant_id, "trials")

    key = ["participant_id", "trial_number", "trial_time"]
    _require_columns(gaze, key + ["gaze_x", "gaze_y"], "preprocessed gaze")
    _require_columns(targets, key + ["target_x", "target_y"], "preprocessed targets")
    if gaze.duplicated(key).any():
        raise ValueError(f"participant {participant_id!r} gaze alignment keys are duplicated")
    if targets.duplicated(key).any():
        raise ValueError(f"participant {participant_id!r} target alignment keys are duplicated")

    aligned = gaze.merge(
        targets[key + ["target_x", "target_y"]],
        on=key,
        how="left",
        validate="one_to_one",
    )
    if aligned[["target_x", "target_y"]].isna().any().any():
        raise ValueError(
            f"participant {participant_id!r} has gaze rows without exact canonical target alignment"
        )

    trial_columns = [
        "participant_id",
        "trial_number",
        "target_type",
        "target_speed",
        "target_trajectory",
    ]
    optional = [column for column in ["actual_speed"] if column in trials.columns]
    _require_columns(trials, trial_columns, "preprocessed trials")
    trial_meta = trials[trial_columns + optional].drop_duplicates()
    if trial_meta.duplicated(["participant_id", "trial_number"]).any():
        raise ValueError(f"participant {participant_id!r} trial metadata is not one-to-one")
    aligned = aligned.merge(
        trial_meta,
        on=["participant_id", "trial_number"],
        how="left",
        validate="many_to_one",
    )
    if aligned[["target_type", "target_speed", "target_trajectory"]].isna().any().any():
        raise ValueError(f"participant {participant_id!r} has gaze rows without trial metadata")
    return aligned


def _require_clean_tables(participant_id: str, clean_data: Mapping[str, Any]) -> None:
    required = {"gaze", "targets", "trials", "blinks"}
    missing = sorted(required.difference(clean_data))
    if missing:
        raise ValueError(f"participant {participant_id!r} clean data is missing: {missing}")
    for name in required:
        if not isinstance(clean_data[name], pd.DataFrame) or clean_data[name].empty:
            raise ValueError(f"participant {participant_id!r} clean table {name!r} is empty")


def _participant_frame(value: Any, participant_id: str, label: str) -> pd.DataFrame:
    if not isinstance(value, pd.DataFrame) or value.empty:
        raise ValueError(f"participant {participant_id!r} {label} table must be non-empty")
    frame = value.copy()
    if "participant_id" not in frame.columns:
        frame["participant_id"] = participant_id
    frame["participant_id"] = frame["participant_id"].astype(str)
    if set(frame["participant_id"].unique()) != {participant_id}:
        raise ValueError(f"{label} table contains rows for a different participant")
    return frame


def _validated_data_root(data_root: str | Path) -> Path:
    root = Path(data_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Korthals data root does not exist: {root}")
    return root


def _require_columns(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


@contextmanager
def _working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _file_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "size_bytes": int(path.stat().st_size),
        "sha256": _sha256_file(path),
    }


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
        digest, name = parts
        if name in values or Path(name).name != name:
            raise ValueError("invalid or duplicate SHA256SUMS path")
        values[name] = digest
    return values
