from __future__ import annotations

import copy

import pytest

import gazeaudit.pedrotti_source_lock as lock_module
from gazeaudit.pedrotti_source import (
    PEDROTTI_CASE_STUDY_ID,
    PEDROTTI_PROTOCOL_FINGERPRINT,
    PEDROTTI_SOURCE_INTAKE_SCHEMA,
    PedrottiSourceIntake,
)
from gazeaudit.pedrotti_source_lock import (
    PEDROTTI_LOCKED_INTAKE_SUMMARY_FINGERPRINT,
    PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT,
    PEDROTTI_SOURCE_FREEZE_ARTIFACT_ID,
    PEDROTTI_SOURCE_FREEZE_COMMIT,
    PEDROTTI_SOURCE_FREEZE_RUN_ID,
    PEDROTTI_SOURCE_FREEZE_ZIP_SHA256,
    PEDROTTI_SOURCE_LOCK_FINGERPRINT,
    load_pedrotti_source_lock,
    verify_pedrotti_locked_intake,
    verify_pedrotti_locked_source_manifest,
    verify_pedrotti_source_lock,
)


def _synthetic_locked_manifest() -> dict[str, object]:
    lock = load_pedrotti_source_lock()
    return {
        "source_manifest_fingerprint": PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT,
        "file_count": 37,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "zenodo_doi": lock["zenodo"]["doi"],
        "zenodo_record": lock["zenodo"]["record"],
        "zenodo_version": lock["zenodo"]["version"],
        "download_contract": lock["zenodo"]["download_contract"],
    }


def _synthetic_locked_summary() -> dict[str, object]:
    return {
        "schema": PEDROTTI_SOURCE_INTAKE_SCHEMA,
        "case_study_id": PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT,
        "participant_count": 36,
        "source_file_count": 37,
        "total_row_count": 13149347,
        "total_trial_count": 3456,
        "short_numeric_trial_count": 864,
        "long_numeric_trial_count": 864,
        "eye_counts": {"left": 20, "right": 16},
        "scientific_endpoint_evaluated": False,
    }


def test_packaged_pedrotti_source_lock_is_immutable_and_endpoint_blind() -> None:
    lock = verify_pedrotti_source_lock()

    assert lock["lock_fingerprint"] == PEDROTTI_SOURCE_LOCK_FINGERPRINT
    assert lock["scientific_endpoint_executed_before_lock"] is False
    assert lock["source_freeze"]["run_id"] == PEDROTTI_SOURCE_FREEZE_RUN_ID
    assert lock["source_freeze"]["artifact_id"] == PEDROTTI_SOURCE_FREEZE_ARTIFACT_ID
    assert lock["source_freeze"]["execution_commit"] == PEDROTTI_SOURCE_FREEZE_COMMIT
    assert lock["source_freeze"]["artifact_zip_sha256"] == PEDROTTI_SOURCE_FREEZE_ZIP_SHA256
    assert lock["source"]["source_manifest_fingerprint"] == (
        PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT
    )
    assert lock["intake"]["intake_summary_fingerprint"] == (
        PEDROTTI_LOCKED_INTAKE_SUMMARY_FINGERPRINT
    )


def test_source_lock_rejects_archive_provenance_tampering() -> None:
    lock = load_pedrotti_source_lock()
    tampered = copy.deepcopy(lock)
    tampered["source_freeze"]["artifact_id"] += 1

    with pytest.raises(ValueError, match="content does not match"):
        verify_pedrotti_source_lock(tampered)


def test_locked_source_manifest_requires_exact_archived_fingerprint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(lock_module, "verify_pedrotti_source_manifest", lambda _: True)
    manifest = _synthetic_locked_manifest()

    verified = verify_pedrotti_locked_source_manifest(manifest)
    assert verified["source_manifest_fingerprint"] == PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT

    changed = dict(manifest)
    changed["source_manifest_fingerprint"] = "0" * 64
    with pytest.raises(ValueError, match="differs from locked source"):
        verify_pedrotti_locked_source_manifest(changed)


def test_locked_source_manifest_still_requires_base_protocol_verifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(lock_module, "verify_pedrotti_source_manifest", lambda _: False)

    with pytest.raises(ValueError, match="frozen-protocol verification"):
        verify_pedrotti_locked_source_manifest(_synthetic_locked_manifest())


def test_locked_intake_requires_endpoint_blind_archived_facts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_fingerprint = lock_module.fingerprint

    def controlled_fingerprint(value: object) -> str:
        if isinstance(value, dict) and value.get("schema") == PEDROTTI_SOURCE_INTAKE_SCHEMA:
            return PEDROTTI_LOCKED_INTAKE_SUMMARY_FINGERPRINT
        return real_fingerprint(value)

    monkeypatch.setattr(lock_module, "fingerprint", controlled_fingerprint)
    monkeypatch.setattr(lock_module, "verify_pedrotti_source_manifest", lambda _: True)
    intake = PedrottiSourceIntake(
        source_manifest=_synthetic_locked_manifest(),
        intake_summary=_synthetic_locked_summary(),
    )

    assert verify_pedrotti_locked_intake(intake) is intake

    changed = copy.deepcopy(intake)
    changed.intake_summary["scientific_endpoint_evaluated"] = True
    with pytest.raises(ValueError, match="differs from locked source freeze"):
        verify_pedrotti_locked_intake(changed)


def test_locked_intake_rejects_wrong_type() -> None:
    with pytest.raises(TypeError, match="PedrottiSourceIntake"):
        verify_pedrotti_locked_intake(object())  # type: ignore[arg-type]
