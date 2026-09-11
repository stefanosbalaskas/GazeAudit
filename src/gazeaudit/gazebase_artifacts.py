"""Immutable artifact sets for frozen GazeBase real-data executions.

The writer in this module serializes every publication-relevant endpoint table,
provenance object, and publication bundle produced by the frozen GazeBase runner.
It deliberately excludes sample-level raw gaze data so that an artifact set can
be shared without redistributing the source dataset. Every emitted file is
SHA-256 bound into a machine-readable artifact manifest and ``SHA256SUMS``.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pandas as pd

from .gazebase_execution import GazeBaseExecution
from .provenance import canonical_json, fingerprint

ARTIFACT_SCHEMA = "gazeaudit-gazebase-artifacts-v1"


def write_gazebase_execution_artifacts(
    execution: GazeBaseExecution,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write a deterministic, checksummed artifact set for one execution.

    The output directory must be absent or empty unless ``overwrite=True``. An
    incomplete execution is still serialized, but publication-bundle files are
    emitted only when the runner produced a verified publication bundle.
    """

    if not isinstance(execution, GazeBaseExecution):
        raise TypeError("execution must be a GazeBaseExecution")
    destination = Path(output_dir)
    _prepare_output_directory(destination, overwrite=overwrite)

    protocol_document = {
        "fingerprint_definition": (
            "sha256(GazeAudit canonical JSON of the protocol object: sorted keys, "
            "compact separators, UTF-8, no NaN/Infinity)"
        ),
        "protocol_fingerprint": execution.protocol_fingerprint,
        "protocol": execution.protocol,
    }
    _write_json(destination / "protocol.json", protocol_document)
    _write_json(destination / "execution_manifest.json", execution.execution_manifest)
    _write_json(destination / "detector_parameters.json", execution.detector_parameters)
    _write_json(destination / "source_identity.json", execution.source_identity)
    _write_json(destination / "fixed_cohort.json", list(execution.audit.fixed_cohort))
    _write_json(destination / "summary.json", _series_mapping(execution.audit.summary))

    tables = {
        "reference_participant_tasks.csv": execution.audit.reference_participant_tasks,
        "reference_contrasts.csv": execution.audit.reference_contrasts,
        "detector_participant_tasks.csv": execution.audit.detector_participant_tasks,
        "detector_contrasts.csv": execution.audit.detector_contrasts,
        "coverage.csv": execution.audit.coverage,
        "effects.csv": execution.audit.effects,
    }
    if execution.audit.recovery is not None:
        tables["recovery.csv"] = execution.audit.recovery
    for filename, frame in tables.items():
        _write_csv(destination / filename, frame)

    bundle = execution.publication_bundle
    if bundle is not None:
        _write_json(destination / "publication_manifest.json", bundle.manifest)
        _write_csv(destination / "publication_specifications.csv", bundle.specifications)
        _write_csv(destination / "publication_recovery.csv", bundle.recovery)
        _write_text(destination / "publication_report.md", bundle.markdown)
        _write_text(destination / "publication_methods.txt", bundle.methods_text + "\n")

    scientific_files = sorted(path for path in destination.iterdir() if path.is_file())
    file_records = [_file_record(path) for path in scientific_files]
    artifact_manifest: dict[str, Any] = {
        "schema": ARTIFACT_SCHEMA,
        "execution_fingerprint": execution.execution_fingerprint,
        "protocol_fingerprint": execution.protocol_fingerprint,
        "classification": str(execution.audit.summary["classification"]),
        "completeness_passed": bool(execution.audit.summary["completeness_passed"]),
        "publication_scientific_fingerprint": (
            None if bundle is None else bundle.scientific_fingerprint
        ),
        "publication_bundle_fingerprint": None if bundle is None else bundle.bundle_fingerprint,
        "files": file_records,
    }
    artifact_manifest["artifact_manifest_fingerprint"] = fingerprint(artifact_manifest)
    _write_json(destination / "artifact_manifest.json", artifact_manifest)

    checksum_targets = sorted(path for path in destination.iterdir() if path.is_file())
    checksum_lines = [f"{_sha256_file(path)}  {path.name}" for path in checksum_targets]
    _write_text(destination / "SHA256SUMS", "\n".join(checksum_lines) + "\n")

    if not verify_gazebase_execution_artifacts(destination):
        raise RuntimeError("newly written GazeBase artifact set failed verification")
    return artifact_manifest


def verify_gazebase_execution_artifacts(output_dir: str | Path) -> bool:
    """Return whether a serialized GazeBase artifact set is internally intact."""

    destination = Path(output_dir)
    try:
        manifest_path = destination / "artifact_manifest.json"
        checksums_path = destination / "SHA256SUMS"
        if not manifest_path.is_file() or not checksums_path.is_file():
            return False
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("schema") != ARTIFACT_SCHEMA:
            return False

        stored_manifest_fingerprint = manifest.get("artifact_manifest_fingerprint")
        manifest_core = dict(manifest)
        manifest_core.pop("artifact_manifest_fingerprint", None)
        if stored_manifest_fingerprint != fingerprint(manifest_core):
            return False

        file_records = manifest.get("files")
        if not isinstance(file_records, list) or not file_records:
            return False
        declared_names: set[str] = set()
        for record in file_records:
            if not isinstance(record, Mapping):
                return False
            name = record.get("path")
            if not isinstance(name, str) or not name or Path(name).name != name:
                return False
            if name in declared_names:
                return False
            declared_names.add(name)
            path = destination / name
            if not path.is_file():
                return False
            if int(record.get("size_bytes", -1)) != path.stat().st_size:
                return False
            if record.get("sha256") != _sha256_file(path):
                return False

        actual_names = {path.name for path in destination.iterdir() if path.is_file()}
        expected_names = declared_names | {"artifact_manifest.json", "SHA256SUMS"}
        if actual_names != expected_names:
            return False

        if not _verify_execution_manifest(destination / "execution_manifest.json"):
            return False
        if not _verify_protocol_document(destination / "protocol.json"):
            return False
        if "publication_manifest.json" in declared_names:
            if not _verify_publication_manifest(destination / "publication_manifest.json"):
                return False

        expected_checksum_names = declared_names | {"artifact_manifest.json"}
        checksum_map = _parse_checksums(checksums_path)
        if set(checksum_map) != expected_checksum_names:
            return False
        for name, digest in checksum_map.items():
            if digest != _sha256_file(destination / name):
                return False
        return True
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def _prepare_output_directory(destination: Path, *, overwrite: bool) -> None:
    if destination.exists() and not destination.is_dir():
        raise ValueError("output_dir must be a directory path")
    destination.mkdir(parents=True, exist_ok=True)
    existing = list(destination.iterdir())
    if existing and not overwrite:
        raise FileExistsError("output_dir is not empty; pass overwrite=True to replace artifacts")
    if overwrite:
        for path in existing:
            if path.is_dir():
                raise ValueError("overwrite=True refuses to remove nested directories")
            path.unlink()


def _write_json(path: Path, value: Any) -> None:
    _write_text(path, canonical_json(value) + "\n")


def _write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("artifact tables must be pandas DataFrames")
    frame.to_csv(
        path,
        index=False,
        lineterminator="\n",
        na_rep="NA",
        float_format="%.17g",
    )


def _file_record(path: Path) -> dict[str, Any]:
    return {
        "path": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _series_mapping(series: pd.Series) -> dict[str, Any]:
    if not isinstance(series, pd.Series):
        raise TypeError("summary must be a pandas Series")
    return {str(key): _json_scalar(value) for key, value in series.items()}


def _json_scalar(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    item = getattr(value, "item", None)
    if callable(item):
        return _json_scalar(item())
    return value


def _verify_execution_manifest(path: Path) -> bool:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        return False
    stored = document.get("execution_fingerprint")
    core = dict(document)
    core.pop("execution_fingerprint", None)
    return stored == fingerprint(core)


def _verify_protocol_document(path: Path) -> bool:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        return False
    protocol = document.get("protocol")
    stored = document.get("protocol_fingerprint")
    return isinstance(protocol, dict) and stored == fingerprint(protocol)


def _verify_publication_manifest(path: Path) -> bool:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        return False
    stored = document.get("bundle_fingerprint")
    core = dict(document)
    core.pop("bundle_fingerprint", None)
    return stored == fingerprint(core)


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
