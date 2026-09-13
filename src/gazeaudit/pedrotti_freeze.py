"""Archive-bound source freeze for the Pedrotti public-data case study.

The envelope is endpoint-blind. It binds exact Zenodo source identity, the frozen
protocol, execution commit, workflow identity, and dependency environment before any
gaze-path effect or perturbation sensitivity result is computed.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections.abc import Mapping
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .pedrotti_source import (
    PEDROTTI_CASE_STUDY_ID,
    PEDROTTI_PROTOCOL_FINGERPRINT,
    PEDROTTI_ZENODO_DOI,
    PEDROTTI_ZENODO_RECORD,
    verify_pedrotti_source_intake_artifacts,
)
from .provenance import canonical_json, fingerprint

PEDROTTI_SOURCE_FREEZE_SCHEMA = "gazeaudit-pedrotti-source-freeze-v1"
PEDROTTI_FREEZE_WORKFLOW = ".github/workflows/pedrotti-source-freeze.yml"

_FORBIDDEN_SCIENTIFIC_TOKENS = (
    '"reference_estimate"',
    '"study_estimate"',
    '"participant_contrast"',
    '"sampling_estimates"',
    '"missingness_estimates"',
    '"perturbed_estimate"',
    '"relative_deviation"',
    '"recovery_fraction"',
    '"family_recovery"',
    '"classification"',
)
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def write_pedrotti_source_freeze_artifacts(
    intake_dir: str | Path,
    output_dir: str | Path,
    *,
    execution_context: Mapping[str, Any],
    environment_text: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write a checksummed outer freeze envelope around a verified source intake."""

    intake = Path(intake_dir)
    if not verify_pedrotti_source_intake_artifacts(intake):
        raise ValueError("intake_dir is not a valid Pedrotti source-intake artifact")
    context = _validated_execution_context(execution_context, intake)
    if not isinstance(environment_text, str) or not environment_text.strip():
        raise ValueError("environment_text must be a non-empty dependency snapshot")

    destination = Path(output_dir)
    _prepare_destination(destination, overwrite=overwrite)
    nested = destination / "intake"
    nested.mkdir()
    for name in (
        "source_manifest.json",
        "intake_summary.json",
        "artifact_manifest.json",
        "SHA256SUMS",
    ):
        shutil.copy2(intake / name, nested / name)

    _write_json(destination / "execution_context.json", context)
    (destination / "pip_freeze.txt").write_text(
        environment_text.rstrip("\n") + "\n", encoding="utf-8"
    )

    source = _read_json(nested / "source_manifest.json")
    intake_manifest = _read_json(nested / "artifact_manifest.json")
    core = {
        "schema": PEDROTTI_SOURCE_FREEZE_SCHEMA,
        "case_study_id": PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": source["source_manifest_fingerprint"],
        "intake_artifact_manifest_fingerprint": intake_manifest[
            "artifact_manifest_fingerprint"
        ],
        "execution_commit": context["execution_commit"],
        "workflow_ref": context["workflow_ref"],
        "github_run_id": context["github_run_id"],
        "zenodo_record": PEDROTTI_ZENODO_RECORD,
        "files": _records_for_freeze_payload(destination),
        "scientific_endpoint_evaluated": False,
    }
    manifest = dict(core)
    manifest["freeze_manifest_fingerprint"] = fingerprint(core)
    _write_json(destination / "freeze_manifest.json", manifest)

    checksum_targets = sorted(
        path
        for path in destination.rglob("*")
        if path.is_file() and path != destination / "SHA256SUMS"
    )
    (destination / "SHA256SUMS").write_text(
        "\n".join(
            f"{_sha256_file(path)}  {path.relative_to(destination).as_posix()}"
            for path in checksum_targets
        )
        + "\n",
        encoding="utf-8",
    )

    if not verify_pedrotti_source_freeze_artifacts(destination):
        raise RuntimeError("newly written Pedrotti source freeze failed verification")
    return manifest


def verify_pedrotti_source_freeze_artifacts(output_dir: str | Path) -> bool:
    """Return whether a Pedrotti source freeze is complete and unmodified."""

    root = Path(output_dir)
    try:
        if not root.is_dir():
            return False
        expected_top = {
            "intake",
            "execution_context.json",
            "pip_freeze.txt",
            "freeze_manifest.json",
            "SHA256SUMS",
        }
        if {path.name for path in root.iterdir()} != expected_top:
            return False
        if not verify_pedrotti_source_intake_artifacts(root / "intake"):
            return False

        source = _read_json(root / "intake" / "source_manifest.json")
        intake_manifest = _read_json(root / "intake" / "artifact_manifest.json")
        context = _validated_execution_context(
            _read_json(root / "execution_context.json"), root / "intake"
        )
        environment_text = (root / "pip_freeze.txt").read_text(encoding="utf-8")
        if not environment_text.strip():
            return False

        manifest = _read_json(root / "freeze_manifest.json")
        expected_manifest_keys = {
            "schema",
            "case_study_id",
            "protocol_fingerprint",
            "source_manifest_fingerprint",
            "intake_artifact_manifest_fingerprint",
            "execution_commit",
            "workflow_ref",
            "github_run_id",
            "zenodo_record",
            "files",
            "scientific_endpoint_evaluated",
            "freeze_manifest_fingerprint",
        }
        if set(manifest) != expected_manifest_keys:
            return False
        if manifest.get("schema") != PEDROTTI_SOURCE_FREEZE_SCHEMA:
            return False
        stored = manifest.pop("freeze_manifest_fingerprint")
        if stored != fingerprint(manifest):
            return False
        if manifest.get("case_study_id") != PEDROTTI_CASE_STUDY_ID:
            return False
        if manifest.get("protocol_fingerprint") != PEDROTTI_PROTOCOL_FINGERPRINT:
            return False
        if manifest.get("source_manifest_fingerprint") != source.get(
            "source_manifest_fingerprint"
        ):
            return False
        if manifest.get("intake_artifact_manifest_fingerprint") != intake_manifest.get(
            "artifact_manifest_fingerprint"
        ):
            return False
        if manifest.get("execution_commit") != context["execution_commit"]:
            return False
        if manifest.get("workflow_ref") != context["workflow_ref"]:
            return False
        if str(manifest.get("github_run_id")) != str(context["github_run_id"]):
            return False
        if manifest.get("zenodo_record") != PEDROTTI_ZENODO_RECORD:
            return False
        if manifest.get("scientific_endpoint_evaluated") is not False:
            return False
        if manifest.get("files") != _records_for_freeze_payload(root):
            return False

        checksums = _parse_checksums(root / "SHA256SUMS")
        expected_checksum_paths = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and path != root / "SHA256SUMS"
        }
        if set(checksums) != expected_checksum_paths:
            return False
        if not all(_sha256_file(root / name) == digest for name, digest in checksums.items()):
            return False

        searchable = "\n".join(
            canonical_json(value)
            for value in (
                context,
                manifest,
                _read_json(root / "intake" / "intake_summary.json"),
            )
        ).lower()
        if any(token in searchable for token in _FORBIDDEN_SCIENTIFIC_TOKENS):
            return False
        return True
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError):
        return False


def _validated_execution_context(
    document: Mapping[str, Any],
    intake_dir: Path,
) -> dict[str, Any]:
    normalized = json.loads(canonical_json(document))
    source = _read_json(intake_dir / "source_manifest.json")
    required = {
        "repository",
        "execution_commit",
        "workflow_ref",
        "github_run_id",
        "protocol_fingerprint",
        "source_manifest_fingerprint",
        "zenodo_doi",
        "zenodo_record",
        "package_version",
        "python_version",
        "platform",
        "runner_os",
        "runner_arch",
    }
    if set(normalized) != required:
        raise ValueError("execution_context does not have the exact required field set")
    if normalized["repository"] != "stefanosbalaskas/GazeAudit":
        raise ValueError("unexpected repository identity")
    if not isinstance(normalized["execution_commit"], str) or not _SHA40.fullmatch(
        normalized["execution_commit"]
    ):
        raise ValueError("execution_commit must be a lowercase 40-character Git SHA")
    if normalized["workflow_ref"] != PEDROTTI_FREEZE_WORKFLOW:
        raise ValueError("unexpected source-freeze workflow identity")
    run_id = str(normalized["github_run_id"])
    if not run_id.isdigit() or int(run_id) <= 0:
        raise ValueError("github_run_id must be a positive integer")
    if normalized["protocol_fingerprint"] != PEDROTTI_PROTOCOL_FINGERPRINT:
        raise ValueError("unexpected Pedrotti protocol fingerprint")
    if normalized["source_manifest_fingerprint"] != source.get(
        "source_manifest_fingerprint"
    ):
        raise ValueError("source fingerprint differs from the archived intake")
    if normalized["zenodo_doi"] != PEDROTTI_ZENODO_DOI:
        raise ValueError("unexpected Pedrotti Zenodo DOI")
    if normalized["zenodo_record"] != PEDROTTI_ZENODO_RECORD:
        raise ValueError("unexpected Pedrotti Zenodo record")
    try:
        installed_version = version("gazeaudit")
    except PackageNotFoundError as exc:  # pragma: no cover
        raise ValueError("gazeaudit package metadata is unavailable") from exc
    if normalized["package_version"] != installed_version:
        raise ValueError("execution package version differs from installed GazeAudit")
    for field in ("python_version", "platform", "runner_os", "runner_arch"):
        if not isinstance(normalized[field], str) or not normalized[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
    return normalized


def _prepare_destination(destination: Path, *, overwrite: bool) -> None:
    if destination.exists() and not destination.is_dir():
        raise ValueError("output_dir must be a directory path")
    destination.mkdir(parents=True, exist_ok=True)
    existing = list(destination.iterdir())
    if existing and not overwrite:
        raise FileExistsError("output_dir is not empty; pass overwrite=True to replace")
    if overwrite:
        for path in existing:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def _records_for_freeze_payload(root: Path) -> list[dict[str, Any]]:
    excluded = {root / "freeze_manifest.json", root / "SHA256SUMS"}
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size_bytes": int(path.stat().st_size),
            "sha256": _sha256_file(path),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and path not in excluded
    ]


def _write_json(path: Path, value: Any) -> None:
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


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
        digest, separator, name = line.partition("  ")
        candidate = Path(name)
        if not separator or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("invalid SHA256SUMS entry")
        if not name or candidate.is_absolute() or ".." in candidate.parts or name in values:
            raise ValueError("invalid or duplicate SHA256SUMS path")
        values[name] = digest
    return values
