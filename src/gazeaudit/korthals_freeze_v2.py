"""Archive-bound source freeze for the Korthals protocol-v2 source intake.

The envelope is endpoint-blind. It records source, environment, execution commit, and
the source-readiness missingness diagnostics introduced by protocol v2, but never
computes or stores AOI effects, Monte Carlo draws, or classifications.
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Mapping
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .korthals_execution import KORTHALS_COMPANION_COMMIT
from .korthals_freeze import (
    KORTHALS_COMPANION_REPOSITORY,
    KORTHALS_FREEZE_WORKFLOW,
    _parse_checksums,
    _prepare_destination,
    _read_json,
    _records_for_freeze_payload,
    _sha256_file,
    _write_json,
)
from .korthals_v2 import (
    KORTHALS_V2_CASE_STUDY_ID,
    KORTHALS_V2_PROTOCOL_FINGERPRINT,
    verify_korthals_source_intake_artifacts_v2,
)
from .provenance import canonical_json, fingerprint

KORTHALS_V2_SOURCE_FREEZE_SCHEMA = "gazeaudit-korthals-source-freeze-v2"

_FORBIDDEN_SCIENTIFIC_TOKENS = (
    "hard_effect",
    "mc_mean",
    "mc_median",
    "mc_interval",
    "classification",
    "probability_above_reference",
    "probability_below_reference",
    "draw_effects",
)
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def write_korthals_source_freeze_artifacts_v2(
    intake_dir: str | Path,
    output_dir: str | Path,
    *,
    execution_context: Mapping[str, Any],
    environment_text: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write a checksummed protocol-v2 source freeze envelope."""

    intake = Path(intake_dir)
    if not verify_korthals_source_intake_artifacts_v2(intake):
        raise ValueError("intake_dir is not a valid Korthals protocol-v2 source intake")
    context = _validated_execution_context_v2(execution_context, intake)
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
    file_records = _records_for_freeze_payload(destination)
    core = {
        "schema": KORTHALS_V2_SOURCE_FREEZE_SCHEMA,
        "case_study_id": KORTHALS_V2_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": source["source_manifest_fingerprint"],
        "intake_artifact_manifest_fingerprint": intake_manifest[
            "artifact_manifest_fingerprint"
        ],
        "execution_commit": context["execution_commit"],
        "workflow_ref": context["workflow_ref"],
        "github_run_id": context["github_run_id"],
        "files": file_records,
    }
    manifest = dict(core)
    manifest["freeze_manifest_fingerprint"] = fingerprint(core)
    _write_json(destination / "freeze_manifest.json", manifest)

    checksum_targets = sorted(
        path
        for path in destination.rglob("*")
        if path.is_file() and path != destination / "SHA256SUMS"
    )
    lines = [
        f"{_sha256_file(path)}  {path.relative_to(destination).as_posix()}"
        for path in checksum_targets
    ]
    (destination / "SHA256SUMS").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    if not verify_korthals_source_freeze_artifacts_v2(destination):
        raise RuntimeError(
            "newly written Korthals protocol-v2 source freeze failed verification"
        )
    return manifest


def verify_korthals_source_freeze_artifacts_v2(output_dir: str | Path) -> bool:
    """Return whether a protocol-v2 source freeze is complete and unmodified."""

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
        if not verify_korthals_source_intake_artifacts_v2(root / "intake"):
            return False

        source = _read_json(root / "intake" / "source_manifest.json")
        intake_manifest = _read_json(root / "intake" / "artifact_manifest.json")
        context = _validated_execution_context_v2(
            _read_json(root / "execution_context.json"), root / "intake"
        )
        environment_text = (root / "pip_freeze.txt").read_text(encoding="utf-8")
        if not environment_text.strip():
            return False

        manifest = _read_json(root / "freeze_manifest.json")
        if manifest.get("schema") != KORTHALS_V2_SOURCE_FREEZE_SCHEMA:
            return False
        stored = manifest.get("freeze_manifest_fingerprint")
        core = dict(manifest)
        core.pop("freeze_manifest_fingerprint", None)
        if stored != fingerprint(core):
            return False
        if manifest.get("case_study_id") != KORTHALS_V2_CASE_STUDY_ID:
            return False
        if manifest.get("protocol_fingerprint") != KORTHALS_V2_PROTOCOL_FINGERPRINT:
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
        if not all(
            _sha256_file(root / name) == digest for name, digest in checksums.items()
        ):
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


def _validated_execution_context_v2(
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
        "companion_repository",
        "companion_commit",
        "protocol_fingerprint",
        "source_manifest_fingerprint",
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
    if normalized["workflow_ref"] != KORTHALS_FREEZE_WORKFLOW:
        raise ValueError("unexpected source-freeze workflow identity")
    run_id = str(normalized["github_run_id"])
    if not run_id.isdigit() or int(run_id) <= 0:
        raise ValueError("github_run_id must be a positive integer")
    if normalized["companion_repository"] != KORTHALS_COMPANION_REPOSITORY:
        raise ValueError("unexpected companion repository")
    if normalized["companion_commit"] != KORTHALS_COMPANION_COMMIT:
        raise ValueError("unexpected companion commit")
    if normalized["protocol_fingerprint"] != KORTHALS_V2_PROTOCOL_FINGERPRINT:
        raise ValueError("unexpected protocol-v2 fingerprint")
    if normalized["source_manifest_fingerprint"] != source.get(
        "source_manifest_fingerprint"
    ):
        raise ValueError("source fingerprint differs from the archived intake")
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
