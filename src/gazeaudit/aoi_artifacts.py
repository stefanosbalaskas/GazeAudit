"""Deterministic artifacts for AOI measurement-uncertainty audits."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pandas as pd

from .aoi_propagation import AOIEffectUncertaintyAudit
from .aoi_protocol import verify_aoi_uncertainty_protocol
from .provenance import canonical_json, fingerprint

AOI_UNCERTAINTY_ARTIFACT_SCHEMA = "gazeaudit-aoi-uncertainty-artifacts-v1"


def write_aoi_uncertainty_artifacts(
    audit: AOIEffectUncertaintyAudit,
    protocol: Mapping[str, Any],
    output_dir: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write a checksummed AOI uncertainty audit bound to a frozen protocol.

    The writer refuses protocol/audit mismatches for AOI identity, draw count,
    interval level, and reference value.  This makes the archived result an
    execution of a declared protocol rather than an unbound table of Monte Carlo
    draws.
    """

    if not isinstance(audit, AOIEffectUncertaintyAudit):
        raise TypeError("audit must be an AOIEffectUncertaintyAudit")
    if not verify_aoi_uncertainty_protocol(protocol):
        raise ValueError("protocol must be a verified AOI uncertainty protocol")
    protocol_document = json.loads(canonical_json(dict(protocol)))
    _verify_audit_matches_protocol(audit, protocol_document)

    destination = Path(output_dir)
    _prepare_output_directory(destination, overwrite=overwrite)

    _write_json(destination / "protocol.json", protocol_document)
    _write_json(destination / "summary.json", audit.summary.to_dict())
    _write_csv(destination / "draw_effects.csv", audit.draw_effects)
    _write_csv(
        destination / "membership_probabilities.csv",
        audit.membership_probabilities,
    )

    result_files = {
        "summary.json": _sha256_file(destination / "summary.json"),
        "draw_effects.csv": _sha256_file(destination / "draw_effects.csv"),
        "membership_probabilities.csv": _sha256_file(
            destination / "membership_probabilities.csv"
        ),
    }
    scientific_identity = {
        "protocol_fingerprint": protocol_document["protocol_fingerprint"],
        "aoi": audit.aoi,
        "result_files": result_files,
    }
    scientific_fingerprint = fingerprint(scientific_identity)

    files_before_manifest = sorted(path for path in destination.iterdir() if path.is_file())
    file_records = [_file_record(path) for path in files_before_manifest]
    manifest: dict[str, Any] = {
        "schema": AOI_UNCERTAINTY_ARTIFACT_SCHEMA,
        "protocol_fingerprint": protocol_document["protocol_fingerprint"],
        "scientific_fingerprint": scientific_fingerprint,
        "aoi": audit.aoi,
        "n_observations": int(audit.summary["n_observations"]),
        "n_draws": int(audit.summary["n_draws"]),
        "files": file_records,
    }
    manifest["artifact_manifest_fingerprint"] = fingerprint(manifest)
    _write_json(destination / "artifact_manifest.json", manifest)

    checksum_targets = sorted(path for path in destination.iterdir() if path.is_file())
    checksum_lines = [f"{_sha256_file(path)}  {path.name}" for path in checksum_targets]
    _write_text(destination / "SHA256SUMS", "\n".join(checksum_lines) + "\n")

    if not verify_aoi_uncertainty_artifacts(destination):
        raise RuntimeError("newly written AOI uncertainty artifact set failed verification")
    return manifest


def verify_aoi_uncertainty_artifacts(output_dir: str | Path) -> bool:
    """Return whether an AOI uncertainty artifact directory is intact."""

    destination = Path(output_dir)
    try:
        manifest_path = destination / "artifact_manifest.json"
        checksums_path = destination / "SHA256SUMS"
        if not manifest_path.is_file() or not checksums_path.is_file():
            return False

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            return False
        if manifest.get("schema") != AOI_UNCERTAINTY_ARTIFACT_SCHEMA:
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

        required = {
            "protocol.json",
            "summary.json",
            "draw_effects.csv",
            "membership_probabilities.csv",
        }
        if declared_names != required:
            return False

        actual_names = {path.name for path in destination.iterdir() if path.is_file()}
        expected_names = declared_names | {"artifact_manifest.json", "SHA256SUMS"}
        if actual_names != expected_names:
            return False

        protocol = json.loads((destination / "protocol.json").read_text(encoding="utf-8"))
        if not verify_aoi_uncertainty_protocol(protocol):
            return False
        if manifest.get("protocol_fingerprint") != protocol.get("protocol_fingerprint"):
            return False

        summary = json.loads((destination / "summary.json").read_text(encoding="utf-8"))
        if not isinstance(summary, dict) or not _summary_matches_protocol(summary, protocol):
            return False
        if manifest.get("aoi") != summary.get("aoi"):
            return False
        if int(manifest.get("n_observations", -1)) != int(summary["n_observations"]):
            return False
        if int(manifest.get("n_draws", -1)) != int(summary["n_draws"]):
            return False

        draws = pd.read_csv(destination / "draw_effects.csv")
        memberships = pd.read_csv(destination / "membership_probabilities.csv")
        if list(draws.columns) != ["draw", "estimate"]:
            return False
        if list(memberships.columns) != ["observation", "membership_probability"]:
            return False
        if len(draws) != int(summary["n_draws"]):
            return False
        if len(memberships) != int(summary["n_observations"]):
            return False

        result_files = {
            "summary.json": _sha256_file(destination / "summary.json"),
            "draw_effects.csv": _sha256_file(destination / "draw_effects.csv"),
            "membership_probabilities.csv": _sha256_file(
                destination / "membership_probabilities.csv"
            ),
        }
        scientific_identity = {
            "protocol_fingerprint": protocol["protocol_fingerprint"],
            "aoi": summary["aoi"],
            "result_files": result_files,
        }
        if manifest.get("scientific_fingerprint") != fingerprint(scientific_identity):
            return False

        checksum_map = _parse_checksums(checksums_path)
        expected_checksum_names = declared_names | {"artifact_manifest.json"}
        if set(checksum_map) != expected_checksum_names:
            return False
        for name, digest in checksum_map.items():
            if digest != _sha256_file(destination / name):
                return False
        return True
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError):
        return False


def _verify_audit_matches_protocol(
    audit: AOIEffectUncertaintyAudit,
    protocol: Mapping[str, Any],
) -> None:
    summary = audit.summary.to_dict()
    if not _summary_matches_protocol(summary, protocol):
        raise ValueError("audit summary does not match the frozen protocol")
    if audit.aoi != protocol["aoi"]["name"]:
        raise ValueError("audit AOI does not match the frozen protocol")
    if len(audit.draw_effects) != int(summary["n_draws"]):
        raise ValueError("audit draw table does not match its declared draw count")
    if len(audit.membership_probabilities) != int(summary["n_observations"]):
        raise ValueError("audit membership table does not match its observation count")


def _summary_matches_protocol(
    summary: Mapping[str, Any],
    protocol: Mapping[str, Any],
) -> bool:
    try:
        monte_carlo = protocol["monte_carlo"]
        return (
            str(summary["aoi"]) == str(protocol["aoi"]["name"])
            and int(summary["n_draws"]) == int(monte_carlo["draws"])
            and float(summary["interval_level"]) == float(monte_carlo["interval"])
            and float(summary["reference"]) == float(monte_carlo["reference"])
        )
    except (KeyError, TypeError, ValueError):
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
