"""Immutable public-source lock for the Korthals protocol-v2 case study.

The source lock binds the first successful endpoint-blind source freeze to the exact
OSF byte-manifest fingerprint, protocol/companion identities, endpoint-blind intake
shape, and archived freeze artifact. It contains no scientific AOI endpoint result.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from importlib import resources
from typing import Any

from .korthals_execution import KORTHALS_COMPANION_COMMIT, PreparedKorthalsData
from .korthals_v2 import (
    KORTHALS_V2_CASE_STUDY_ID,
    KORTHALS_V2_MISSINGNESS_POLICY,
    KORTHALS_V2_PROTOCOL_FINGERPRINT,
    verify_korthals_source_manifest_v2,
)
from .provenance import canonical_json, fingerprint

KORTHALS_SOURCE_LOCK_SCHEMA = "gazeaudit-korthals-source-lock-v2"
KORTHALS_SOURCE_LOCK_FILE = "korthals2026_source_lock_v2.json"
KORTHALS_SOURCE_LOCK_FINGERPRINT = (
    "8bcd9e1dfc8d6ca07c6222a20f563bf8b3bd67aed0de0d3b0e97628799de3a08"
)


def load_korthals_source_lock() -> dict[str, Any]:
    """Load the packaged immutable source lock."""

    text = resources.files("gazeaudit.data").joinpath(KORTHALS_SOURCE_LOCK_FILE).read_text(
        encoding="utf-8"
    )
    document = json.loads(text)
    if not isinstance(document, dict):
        raise ValueError("packaged Korthals source lock must be a JSON object")
    return document


def verify_korthals_source_lock(
    document: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify the frozen source-lock fingerprint and hard provenance guardrails."""

    lock = load_korthals_source_lock() if document is None else json.loads(canonical_json(document))
    if not isinstance(lock, dict):
        raise TypeError("Korthals source lock must normalize to an object")

    stored = lock.get("lock_fingerprint")
    if stored != KORTHALS_SOURCE_LOCK_FINGERPRINT:
        raise ValueError("Korthals source lock has the wrong immutable fingerprint")
    core = dict(lock)
    core.pop("lock_fingerprint", None)
    if fingerprint(core) != KORTHALS_SOURCE_LOCK_FINGERPRINT:
        raise ValueError("Korthals source lock content does not match its fingerprint")

    checks = {
        "schema": lock.get("schema") == KORTHALS_SOURCE_LOCK_SCHEMA,
        "case_study": lock.get("case_study_id") == KORTHALS_V2_CASE_STUDY_ID,
        "protocol": lock.get("protocol_fingerprint") == KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "companion": lock.get("companion", {}).get("commit") == KORTHALS_COMPANION_COMMIT,
        "outcome_blind": lock.get("scientific_endpoint_executed_before_lock") is False,
        "missingness": (
            lock.get("intake", {}).get("missingness_policy") == KORTHALS_V2_MISSINGNESS_POLICY
        ),
        "artifact_digest": (
            lock.get("source_freeze", {}).get("github_artifact_digest")
            == "sha256:" + lock.get("source_freeze", {}).get("artifact_zip_sha256", "")
        ),
        "source_count": int(lock.get("source", {}).get("file_count", -1)) == 110,
        "participant_count": int(lock.get("source", {}).get("participant_count", -1)) == 10,
        "pandas": lock.get("environment", {}).get("pandas") == "2.3.3",
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"Korthals source lock failed guardrails: {failed}")
    return lock


def verify_korthals_locked_source_manifest(
    document: Mapping[str, Any],
    *,
    lock_document: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Fail closed unless a current OSF manifest has the exact locked byte identity."""

    lock = verify_korthals_source_lock(lock_document)
    manifest = json.loads(canonical_json(document))
    if not verify_korthals_source_manifest_v2(manifest):
        raise ValueError("current Korthals source manifest failed protocol-v2 verification")

    source = lock["source"]
    checks = {
        "fingerprint": (
            manifest.get("source_manifest_fingerprint") == source["source_manifest_fingerprint"]
        ),
        "file_count": int(manifest.get("file_count", -1)) == int(source["file_count"]),
        "participant_count": (
            int(manifest.get("participant_count", -1)) == int(source["participant_count"])
        ),
        "participants": list(manifest.get("participants", [])) == list(source["participants"]),
        "download_contract": manifest.get("download_contract") == lock["osf"]["download_contract"],
        "osf_doi": manifest.get("osf_doi") == lock["osf"]["doi"],
        "osf_project": manifest.get("osf_project") == lock["osf"]["project"],
        "companion": manifest.get("companion_commit") == lock["companion"]["commit"],
        "protocol": manifest.get("protocol_fingerprint") == lock["protocol_fingerprint"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"current Korthals source differs from locked source: {failed}")
    return manifest


def verify_korthals_locked_prepared(
    prepared: PreparedKorthalsData,
    *,
    lock_document: Mapping[str, Any] | None = None,
) -> PreparedKorthalsData:
    """Fail closed unless endpoint-blind preparation reproduces the locked intake facts."""

    if not isinstance(prepared, PreparedKorthalsData):
        raise TypeError("prepared must be PreparedKorthalsData")
    lock = verify_korthals_source_lock(lock_document)
    source = lock["source"]
    intake = lock["intake"]
    identity = prepared.source_identity

    target_types = sorted(prepared.data["target_type"].astype(str).unique().tolist())
    checks = {
        "source_fingerprint": (
            identity.get("source_manifest_fingerprint") == source["source_manifest_fingerprint"]
        ),
        "source_file_count": int(identity.get("source_file_count", -1)) == source["file_count"],
        "participant_count": (
            int(identity.get("participant_count", -1)) == source["participant_count"]
        ),
        "split_fingerprint": (
            identity.get("participant_split_fingerprint")
            == intake["participant_split_fingerprint"]
        ),
        "prepared_rows": len(prepared.data) == intake["prepared_row_count"],
        "retained_trials": int(identity.get("retained_trial_count", -1))
        == intake["retained_trial_count"],
        "validation_groups": len(prepared.validation_groups) == intake["validation_group_count"],
        "target_types": target_types == sorted(intake["target_types"]),
        "missingness_policy": identity.get("missingness_policy") == intake["missingness_policy"],
        "zero_finite_count": int(identity.get("zero_finite_scheduled_trial_count", -1))
        == intake["zero_finite_scheduled_trial_count"],
        "zero_finite_trials": identity.get("zero_finite_scheduled_trials")
        == intake["zero_finite_scheduled_trials"],
        "incomplete_cell_count": int(identity.get("sampling_incomplete_matched_cell_count", -1))
        == intake["sampling_incomplete_matched_cell_count"],
        "incomplete_cells": identity.get("sampling_incomplete_matched_cells")
        == intake["sampling_incomplete_matched_cells"],
        "case_study": identity.get("case_study_id") == KORTHALS_V2_CASE_STUDY_ID,
        "protocol": identity.get("protocol_fingerprint") == KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "companion": identity.get("companion_commit") == KORTHALS_COMPANION_COMMIT,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"prepared Korthals intake differs from locked source freeze: {failed}")
    return prepared
