"""Immutable public-source lock for the Pedrotti/de Chambrier sensitivity case study.

The lock binds the first successful endpoint-blind source freeze to the exact Zenodo
byte-manifest fingerprint, endpoint-blind intake facts, frozen protocol, and archived
GitHub Actions artifact. It contains no gaze-path endpoint, perturbation estimate,
recovery fraction, or robustness classification.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from importlib import resources
from typing import Any

from .pedrotti_source import (
    PEDROTTI_CASE_STUDY_ID,
    PEDROTTI_PROTOCOL_FINGERPRINT,
    PEDROTTI_SOURCE_INTAKE_SCHEMA,
    PEDROTTI_ZENODO_DOI,
    PEDROTTI_ZENODO_RECORD,
    PEDROTTI_ZENODO_VERSION,
    PedrottiSourceIntake,
    verify_pedrotti_source_manifest,
)
from .provenance import canonical_json, fingerprint

PEDROTTI_SOURCE_LOCK_SCHEMA = "gazeaudit-pedrotti-source-lock-v1"
PEDROTTI_SOURCE_LOCK_FILE = "pedrotti2023_source_lock_v1.json"
PEDROTTI_SOURCE_LOCK_FINGERPRINT = (
    "d71949f035ecdf14b9e225b8ca441d291625767dc4a07fa4854882ff2dcae898"
)
PEDROTTI_SOURCE_FREEZE_RUN_ID = 34786624831
PEDROTTI_SOURCE_FREEZE_JOB_ID = 103803177169
PEDROTTI_SOURCE_FREEZE_ARTIFACT_ID = 10326523152
PEDROTTI_SOURCE_FREEZE_COMMIT = "63c4dabc47d716d8616f0df422a4d6115d19cb77"
PEDROTTI_SOURCE_FREEZE_ZIP_SHA256 = (
    "e90a7e196df951cbd9c4b2a544beed69cbf2c289a2fd945c3755762dc1c6c667"
)
PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT = (
    "ca676426a01c1d57dda93b62709d4e9040369e4193c0b44353be78d644a33b1f"
)
PEDROTTI_LOCKED_INTAKE_SUMMARY_FINGERPRINT = (
    "24ecbf9b267b56d1e3750e9ed562af972bbec3093196f2ad2cd2a0b567fc48a1"
)


def load_pedrotti_source_lock() -> dict[str, Any]:
    """Load the packaged immutable Pedrotti source lock."""

    text = (
        resources.files("gazeaudit.data")
        .joinpath(PEDROTTI_SOURCE_LOCK_FILE)
        .read_text(encoding="utf-8")
    )
    document = json.loads(text)
    if not isinstance(document, dict):
        raise ValueError("packaged Pedrotti source lock must be a JSON object")
    return document


def verify_pedrotti_source_lock(
    document: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify the immutable lock fingerprint and archive/source guardrails."""

    if document is None:
        lock = load_pedrotti_source_lock()
    else:
        lock = json.loads(canonical_json(document))
    if not isinstance(lock, dict):
        raise TypeError("Pedrotti source lock must normalize to an object")

    stored = lock.get("lock_fingerprint")
    if stored != PEDROTTI_SOURCE_LOCK_FINGERPRINT:
        raise ValueError("Pedrotti source lock has the wrong immutable fingerprint")
    core = dict(lock)
    core.pop("lock_fingerprint", None)
    if fingerprint(core) != PEDROTTI_SOURCE_LOCK_FINGERPRINT:
        raise ValueError("Pedrotti source lock content does not match its fingerprint")

    source = lock.get("source", {})
    intake = lock.get("intake", {})
    freeze = lock.get("source_freeze", {})
    zenodo = lock.get("zenodo", {})
    environment = lock.get("environment", {})
    checks = {
        "schema": lock.get("schema") == PEDROTTI_SOURCE_LOCK_SCHEMA,
        "case_study": lock.get("case_study_id") == PEDROTTI_CASE_STUDY_ID,
        "protocol": lock.get("protocol_fingerprint") == PEDROTTI_PROTOCOL_FINGERPRINT,
        "outcome_blind": lock.get("scientific_endpoint_executed_before_lock") is False,
        "zenodo_doi": zenodo.get("doi") == PEDROTTI_ZENODO_DOI,
        "zenodo_record": zenodo.get("record") == PEDROTTI_ZENODO_RECORD,
        "zenodo_version": zenodo.get("version") == PEDROTTI_ZENODO_VERSION,
        "source_fingerprint": (
            source.get("source_manifest_fingerprint")
            == PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT
        ),
        "source_file_count": int(source.get("file_count", -1)) == 37,
        "participant_file_count": int(source.get("participant_file_count", -1)) == 36,
        "source_total_bytes": int(source.get("source_total_bytes", -1)) == 638488099,
        "participant_count": int(intake.get("participant_count", -1)) == 36,
        "total_rows": int(intake.get("total_row_count", -1)) == 13149347,
        "total_trials": int(intake.get("total_trial_count", -1)) == 3456,
        "short_numeric_trials": int(intake.get("short_numeric_trial_count", -1)) == 864,
        "long_numeric_trials": int(intake.get("long_numeric_trial_count", -1)) == 864,
        "eyes": intake.get("eye_counts") == {"left": 20, "right": 16},
        "intake_fingerprint": (
            intake.get("intake_summary_fingerprint")
            == PEDROTTI_LOCKED_INTAKE_SUMMARY_FINGERPRINT
        ),
        "run_id": freeze.get("run_id") == PEDROTTI_SOURCE_FREEZE_RUN_ID,
        "job_id": freeze.get("job_id") == PEDROTTI_SOURCE_FREEZE_JOB_ID,
        "artifact_id": freeze.get("artifact_id") == PEDROTTI_SOURCE_FREEZE_ARTIFACT_ID,
        "execution_commit": freeze.get("execution_commit") == PEDROTTI_SOURCE_FREEZE_COMMIT,
        "artifact_digest": (
            freeze.get("artifact_zip_sha256") == PEDROTTI_SOURCE_FREEZE_ZIP_SHA256
            and freeze.get("github_artifact_digest")
            == "sha256:" + PEDROTTI_SOURCE_FREEZE_ZIP_SHA256
        ),
        "python": environment.get("python") == "3.12.14",
        "numpy": environment.get("numpy") == "2.5.3",
        "pandas": environment.get("pandas") == "2.3.3",
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"Pedrotti source lock failed guardrails: {failed}")
    return lock


def verify_pedrotti_locked_source_manifest(
    document: Mapping[str, Any],
    *,
    lock_document: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Fail closed unless a source manifest has the exact locked byte identity."""

    lock = verify_pedrotti_source_lock(lock_document)
    manifest = json.loads(canonical_json(document))
    if not verify_pedrotti_source_manifest(manifest):
        raise ValueError("current Pedrotti source manifest failed frozen-protocol verification")

    checks = {
        "fingerprint": (
            manifest.get("source_manifest_fingerprint")
            == lock["source"]["source_manifest_fingerprint"]
        ),
        "file_count": int(manifest.get("file_count", -1)) == lock["source"]["file_count"],
        "protocol": manifest.get("protocol_fingerprint") == lock["protocol_fingerprint"],
        "zenodo_doi": manifest.get("zenodo_doi") == lock["zenodo"]["doi"],
        "zenodo_record": manifest.get("zenodo_record") == lock["zenodo"]["record"],
        "zenodo_version": manifest.get("zenodo_version") == lock["zenodo"]["version"],
        "download_contract": (
            manifest.get("download_contract") == lock["zenodo"]["download_contract"]
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"current Pedrotti source differs from locked source: {failed}")
    return manifest


def verify_pedrotti_locked_intake(
    intake: PedrottiSourceIntake,
    *,
    lock_document: Mapping[str, Any] | None = None,
) -> PedrottiSourceIntake:
    """Fail closed unless endpoint-blind source intake reproduces locked archive facts."""

    if not isinstance(intake, PedrottiSourceIntake):
        raise TypeError("intake must be PedrottiSourceIntake")
    lock = verify_pedrotti_source_lock(lock_document)
    verify_pedrotti_locked_source_manifest(intake.source_manifest, lock_document=lock)
    summary = json.loads(canonical_json(intake.intake_summary))
    expected = lock["intake"]
    checks = {
        "schema": summary.get("schema") == PEDROTTI_SOURCE_INTAKE_SCHEMA,
        "case_study": summary.get("case_study_id") == PEDROTTI_CASE_STUDY_ID,
        "protocol": summary.get("protocol_fingerprint") == PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_fingerprint": (
            summary.get("source_manifest_fingerprint")
            == lock["source"]["source_manifest_fingerprint"]
        ),
        "endpoint_blind": summary.get("scientific_endpoint_evaluated") is False,
        "participant_count": (
            int(summary.get("participant_count", -1)) == expected["participant_count"]
        ),
        "source_file_count": (
            int(summary.get("source_file_count", -1)) == lock["source"]["file_count"]
        ),
        "total_row_count": (
            int(summary.get("total_row_count", -1)) == expected["total_row_count"]
        ),
        "total_trial_count": (
            int(summary.get("total_trial_count", -1)) == expected["total_trial_count"]
        ),
        "short_numeric_trials": (
            int(summary.get("short_numeric_trial_count", -1))
            == expected["short_numeric_trial_count"]
        ),
        "long_numeric_trials": (
            int(summary.get("long_numeric_trial_count", -1))
            == expected["long_numeric_trial_count"]
        ),
        "eye_counts": summary.get("eye_counts") == expected["eye_counts"],
        "summary_fingerprint": (
            fingerprint(summary) == expected["intake_summary_fingerprint"]
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"current Pedrotti intake differs from locked source freeze: {failed}")
    return intake
