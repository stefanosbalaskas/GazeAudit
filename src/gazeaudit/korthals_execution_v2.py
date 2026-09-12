"""Protocol-v2 scientific execution and archive layer for the Korthals case study.

This module implements the already-frozen AOI measurement-uncertainty endpoint for
protocol v2. The only scientific difference from v1 is upstream: protocol v2 removes
an entire matched moving/jumping cell when one of its trials has zero finite gaze
samples on the fixed 50-Hz grid. The endpoint, AOI, error model, Monte Carlo settings,
and interpretation rule remain unchanged.

Real-data execution is admitted only through ``run_korthals_locked_aoi_execution_v2``,
which requires the independently archived public-source lock before evaluating AOI
membership or any scientific effect.
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
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
from .korthals_execution import (
    KORTHALS_COMPANION_COMMIT,
    KORTHALS_TARGET_TYPES,
    PreparedKorthalsData,
    _classify_korthals_result,
    _endpoint_weights,
    _parse_checksums,
    _recursive_file_records,
    _sha256_file,
    _validate_membership,
    _write_json,
)
from .korthals_freeze import KORTHALS_COMPANION_REPOSITORY
from .korthals_source_lock import (
    KORTHALS_SOURCE_LOCK_FINGERPRINT,
    verify_korthals_locked_prepared,
    verify_korthals_source_lock,
)
from .korthals_v2 import (
    KORTHALS_V2_CASE_STUDY_ID,
    KORTHALS_V2_MISSINGNESS_POLICY,
    KORTHALS_V2_PROTOCOL_FINGERPRINT,
    verify_korthals_protocol_v2,
)
from .provenance import canonical_json, fingerprint
from .uncertainty import GroupedGaussianGazeErrorModel

KORTHALS_V2_EXECUTION_ARTIFACT_SCHEMA = "gazeaudit-korthals-aoi-execution-artifacts-v2"
KORTHALS_V2_EXECUTION_WORKFLOW = ".github/workflows/korthals-scientific-execution.yml"
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class KorthalsAOIExecutionV2:
    """One protocol-v2 Korthals measurement-uncertainty execution."""

    protocol: dict[str, Any]
    prepared: PreparedKorthalsData
    audit: AOIEffectUncertaintyAudit
    classification: str
    execution_manifest: dict[str, Any]

    @property
    def execution_fingerprint(self) -> str:
        return str(self.execution_manifest["execution_fingerprint"])


def run_korthals_aoi_execution_v2(
    prepared: PreparedKorthalsData,
    *,
    protocol_document: Mapping[str, Any] | None = None,
) -> KorthalsAOIExecutionV2:
    """Execute frozen protocol v2 on already-prepared data.

    This function is intentionally usable with synthetic fixtures for qualification.
    Real public-data execution must call ``run_korthals_locked_aoi_execution_v2`` so
    the source lock is checked before AOI membership is evaluated.
    """

    if not isinstance(prepared, PreparedKorthalsData):
        raise TypeError("prepared must be PreparedKorthalsData")
    protocol = verify_korthals_protocol_v2(protocol_document)
    _validate_prepared_identity_v2(prepared, protocol)

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
        "case_study_id": KORTHALS_V2_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "source_identity": prepared.source_identity,
        "n_rows": len(prepared.data),
        "n_validation_groups": len(prepared.validation_groups),
        "classification": classification,
        "summary": json.loads(canonical_json(audit.summary.to_dict())),
    }
    execution_manifest = dict(manifest_core)
    execution_manifest["execution_fingerprint"] = fingerprint(manifest_core)
    return KorthalsAOIExecutionV2(
        protocol=protocol,
        prepared=prepared,
        audit=audit,
        classification=classification,
        execution_manifest=execution_manifest,
    )


def run_korthals_locked_aoi_execution_v2(
    prepared: PreparedKorthalsData,
    *,
    protocol_document: Mapping[str, Any] | None = None,
    lock_document: Mapping[str, Any] | None = None,
) -> KorthalsAOIExecutionV2:
    """Execute real-data protocol v2 only after the archived source lock passes."""

    verify_korthals_locked_prepared(prepared, lock_document=lock_document)
    return run_korthals_aoi_execution_v2(
        prepared,
        protocol_document=protocol_document,
    )


def write_korthals_execution_artifacts_v2(
    execution: KorthalsAOIExecutionV2,
    output_dir: str | Path,
    *,
    execution_context: Mapping[str, Any],
    environment_text: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write a checksummed, source-lock-bound protocol-v2 scientific archive."""

    if not isinstance(execution, KorthalsAOIExecutionV2):
        raise TypeError("execution must be KorthalsAOIExecutionV2")
    _validate_prepared_identity_v2(execution.prepared, execution.protocol)
    context = _validated_execution_context_v2(execution_context, execution.prepared)
    _validate_environment_snapshot(environment_text)

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
    _write_json(destination / "execution_context.json", context)
    (destination / "pip_freeze.txt").write_text(
        environment_text.rstrip("\n") + "\n",
        encoding="utf-8",
    )

    manifest_core = {
        "schema": KORTHALS_V2_EXECUTION_ARTIFACT_SCHEMA,
        "case_study_id": KORTHALS_V2_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "source_lock_fingerprint": KORTHALS_SOURCE_LOCK_FINGERPRINT,
        "source_manifest_fingerprint": execution.prepared.source_identity[
            "source_manifest_fingerprint"
        ],
        "execution_commit": context["execution_commit"],
        "workflow_ref": context["workflow_ref"],
        "github_run_id": context["github_run_id"],
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
    if not verify_korthals_execution_artifacts_v2(destination):
        raise RuntimeError("newly written Korthals protocol-v2 archive failed verification")
    return manifest


def verify_korthals_execution_artifacts_v2(output_dir: str | Path) -> bool:
    """Return whether a source-lock-bound protocol-v2 scientific archive is intact."""

    root = Path(output_dir)
    try:
        required = {
            "audit",
            "source_identity.json",
            "execution_manifest.json",
            "execution_context.json",
            "pip_freeze.txt",
            "artifact_manifest.json",
            "SHA256SUMS",
        }
        if not root.is_dir() or {path.name for path in root.iterdir()} != required:
            return False
        if not verify_aoi_uncertainty_artifacts(root / "audit"):
            return False

        lock = verify_korthals_source_lock()
        manifest = json.loads((root / "artifact_manifest.json").read_text(encoding="utf-8"))
        source_identity = json.loads(
            (root / "source_identity.json").read_text(encoding="utf-8")
        )
        execution_manifest = json.loads(
            (root / "execution_manifest.json").read_text(encoding="utf-8")
        )
        context = _validated_execution_context_v2(
            json.loads((root / "execution_context.json").read_text(encoding="utf-8")),
            _prepared_identity_proxy(source_identity, execution_manifest),
        )
        environment_text = (root / "pip_freeze.txt").read_text(encoding="utf-8")
        _validate_environment_snapshot(environment_text)

        if manifest.get("schema") != KORTHALS_V2_EXECUTION_ARTIFACT_SCHEMA:
            return False
        stored = manifest.get("artifact_manifest_fingerprint")
        core = dict(manifest)
        core.pop("artifact_manifest_fingerprint", None)
        if stored != fingerprint(core):
            return False
        if manifest.get("case_study_id") != KORTHALS_V2_CASE_STUDY_ID:
            return False
        if manifest.get("protocol_fingerprint") != KORTHALS_V2_PROTOCOL_FINGERPRINT:
            return False
        if manifest.get("source_lock_fingerprint") != KORTHALS_SOURCE_LOCK_FINGERPRINT:
            return False
        if manifest.get("source_lock_fingerprint") != lock["lock_fingerprint"]:
            return False
        if manifest.get("source_manifest_fingerprint") != source_identity.get(
            "source_manifest_fingerprint"
        ):
            return False
        if source_identity.get("source_manifest_fingerprint") != lock["source"][
            "source_manifest_fingerprint"
        ]:
            return False
        if source_identity.get("protocol_fingerprint") != KORTHALS_V2_PROTOCOL_FINGERPRINT:
            return False
        if source_identity.get("companion_commit") != KORTHALS_COMPANION_COMMIT:
            return False
        if source_identity.get("missingness_policy") != KORTHALS_V2_MISSINGNESS_POLICY:
            return False

        execution_core = dict(execution_manifest)
        execution_fingerprint = execution_core.pop("execution_fingerprint", None)
        if execution_fingerprint != fingerprint(execution_core):
            return False
        if execution_manifest.get("source_identity") != source_identity:
            return False
        if manifest.get("execution_fingerprint") != execution_fingerprint:
            return False
        if manifest.get("classification") != execution_manifest.get("classification"):
            return False
        if manifest.get("execution_commit") != context["execution_commit"]:
            return False
        if manifest.get("workflow_ref") != context["workflow_ref"]:
            return False
        if str(manifest.get("github_run_id")) != str(context["github_run_id"]):
            return False

        audit_manifest = json.loads(
            (root / "audit" / "artifact_manifest.json").read_text(encoding="utf-8")
        )
        if manifest.get("audit_scientific_fingerprint") != audit_manifest.get(
            "scientific_fingerprint"
        ):
            return False
        declared = manifest.get("files")
        actual = _recursive_file_records(
            root,
            exclude={"artifact_manifest.json", "SHA256SUMS"},
        )
        if declared != actual:
            return False

        checksums = _parse_checksums(root / "SHA256SUMS")
        expected_paths = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and path.relative_to(root).as_posix() != "SHA256SUMS"
        }
        if set(checksums) != expected_paths:
            return False
        return all(_sha256_file(root / name) == digest for name, digest in checksums.items())
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError):
        return False


def reveal_korthals_execution_v2(output_dir: str | Path) -> dict[str, Any]:
    """Return the archived scientific result only after archive verification."""

    root = Path(output_dir)
    if not verify_korthals_execution_artifacts_v2(root):
        raise ValueError("Korthals protocol-v2 scientific archive failed verification")
    manifest = json.loads((root / "artifact_manifest.json").read_text(encoding="utf-8"))
    execution = json.loads((root / "execution_manifest.json").read_text(encoding="utf-8"))
    return {
        "artifact_manifest_fingerprint": manifest["artifact_manifest_fingerprint"],
        "audit_scientific_fingerprint": manifest["audit_scientific_fingerprint"],
        "classification": execution["classification"],
        "execution_fingerprint": execution["execution_fingerprint"],
        "protocol_fingerprint": KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "source_lock_fingerprint": KORTHALS_SOURCE_LOCK_FINGERPRINT,
        "source_manifest_fingerprint": manifest["source_manifest_fingerprint"],
        "summary": execution["summary"],
    }


def _validate_prepared_identity_v2(
    prepared: PreparedKorthalsData,
    protocol: Mapping[str, Any],
) -> None:
    identity = prepared.source_identity
    if identity.get("case_study_id") != KORTHALS_V2_CASE_STUDY_ID:
        raise ValueError("prepared source identity does not match protocol-v2 case study")
    if identity.get("protocol_fingerprint") != KORTHALS_V2_PROTOCOL_FINGERPRINT:
        raise ValueError("prepared source identity does not match protocol v2")
    if identity.get("companion_commit") != KORTHALS_COMPANION_COMMIT:
        raise ValueError("prepared source identity does not match frozen companion commit")
    if identity.get("missingness_policy") != KORTHALS_V2_MISSINGNESS_POLICY:
        raise ValueError("prepared source identity does not match protocol-v2 missingness policy")
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
        raise ValueError(f"prepared Korthals protocol-v2 data is missing columns: {missing}")
    if set(prepared.data["target_type"].unique()) != set(KORTHALS_TARGET_TYPES):
        raise ValueError("prepared Korthals protocol-v2 data has unexpected target types")
    if int(protocol["validation"]["n_validation_points"]) != 9:
        raise ValueError("frozen Korthals validation model requires nine points")
    _endpoint_weights(prepared.data)


def _validated_execution_context_v2(
    document: Mapping[str, Any],
    prepared: PreparedKorthalsData,
) -> dict[str, Any]:
    normalized = json.loads(canonical_json(document))
    required = {
        "repository",
        "execution_commit",
        "workflow_ref",
        "github_run_id",
        "companion_repository",
        "companion_commit",
        "protocol_fingerprint",
        "source_lock_fingerprint",
        "source_manifest_fingerprint",
        "package_version",
        "python_version",
        "platform",
        "runner_os",
        "runner_arch",
    }
    if set(normalized) != required:
        raise ValueError("execution_context does not have the exact required field set")
    lock = verify_korthals_source_lock()
    if normalized["repository"] != "stefanosbalaskas/GazeAudit":
        raise ValueError("unexpected repository identity")
    if not isinstance(normalized["execution_commit"], str) or not _SHA40.fullmatch(
        normalized["execution_commit"]
    ):
        raise ValueError("execution_commit must be a lowercase 40-character Git SHA")
    if normalized["workflow_ref"] != KORTHALS_V2_EXECUTION_WORKFLOW:
        raise ValueError("unexpected scientific-execution workflow identity")
    run_id = str(normalized["github_run_id"])
    if not run_id.isdigit() or int(run_id) <= 0:
        raise ValueError("github_run_id must be a positive integer")
    if normalized["companion_repository"] != KORTHALS_COMPANION_REPOSITORY:
        raise ValueError("unexpected companion repository")
    if normalized["companion_commit"] != KORTHALS_COMPANION_COMMIT:
        raise ValueError("unexpected companion commit")
    if normalized["protocol_fingerprint"] != KORTHALS_V2_PROTOCOL_FINGERPRINT:
        raise ValueError("unexpected protocol-v2 fingerprint")
    if normalized["source_lock_fingerprint"] != KORTHALS_SOURCE_LOCK_FINGERPRINT:
        raise ValueError("unexpected Korthals source-lock fingerprint")
    if normalized["source_lock_fingerprint"] != lock["lock_fingerprint"]:
        raise ValueError("execution context differs from packaged source lock")
    if normalized["source_manifest_fingerprint"] != prepared.source_identity.get(
        "source_manifest_fingerprint"
    ):
        raise ValueError("execution source fingerprint differs from prepared source")
    if normalized["source_manifest_fingerprint"] != lock["source"][
        "source_manifest_fingerprint"
    ]:
        raise ValueError("execution source fingerprint differs from source lock")
    try:
        installed_version = version("gazeaudit")
    except PackageNotFoundError as exc:  # pragma: no cover
        raise ValueError("gazeaudit package metadata is unavailable") from exc
    if normalized["package_version"] != installed_version:
        raise ValueError("execution package version differs from installed GazeAudit")
    if normalized["python_version"] != lock["environment"]["python"]:
        raise ValueError("execution Python version differs from source-freeze environment")
    for field in ("platform", "runner_os", "runner_arch"):
        if not isinstance(normalized[field], str) or not normalized[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
    return normalized


def _validate_environment_snapshot(environment_text: str) -> None:
    if not isinstance(environment_text, str) or not environment_text.strip():
        raise ValueError("environment_text must be a non-empty dependency snapshot")
    lock = verify_korthals_source_lock()
    lines = {line.strip().lower() for line in environment_text.splitlines() if line.strip()}
    critical = {
        f"numpy=={lock['environment']['numpy']}".lower(),
        f"pandas=={lock['environment']['pandas']}".lower(),
        f"scipy=={lock['environment']['scipy']}".lower(),
    }
    missing = sorted(critical.difference(lines))
    if missing:
        raise ValueError(f"dependency snapshot lacks locked critical versions: {missing}")


def _prepared_identity_proxy(
    source_identity: Mapping[str, Any],
    execution_manifest: Mapping[str, Any],
) -> PreparedKorthalsData:
    """Provide context validation with archived identity without reconstructing raw rows."""

    n_rows = int(execution_manifest.get("n_rows", 0))
    if n_rows <= 0:
        raise ValueError("archived execution must declare a positive row count")
    return PreparedKorthalsData(
        data=pd.DataFrame(index=range(n_rows)),
        validation_groups=pd.DataFrame(),
        source_identity=dict(source_identity),
    )
