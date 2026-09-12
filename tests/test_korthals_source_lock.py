from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import pytest

import gazeaudit.korthals_source_lock as source_lock
from gazeaudit.korthals_execution import PreparedKorthalsData
from gazeaudit.korthals_source_lock import (
    KORTHALS_SOURCE_LOCK_FINGERPRINT,
    load_korthals_source_lock,
    verify_korthals_locked_prepared,
    verify_korthals_locked_source_manifest,
    verify_korthals_source_lock,
)


def test_packaged_korthals_source_lock_is_immutable_and_outcome_blind():
    lock = verify_korthals_source_lock()

    assert lock == load_korthals_source_lock()
    assert lock["lock_fingerprint"] == KORTHALS_SOURCE_LOCK_FINGERPRINT
    assert lock["scientific_endpoint_executed_before_lock"] is False
    assert lock["source_freeze"]["run_id"] == 34719412734
    assert lock["source_freeze"]["artifact_id"] == 10305414874
    assert lock["source"]["source_manifest_fingerprint"] == (
        "04dd531fb5e0eaa8aa77cb3743d7dadfd4c218895f7edf8186cc3ff9362b7541"
    )


def test_source_lock_rejects_tampering_even_when_semantically_plausible():
    lock = load_korthals_source_lock()
    tampered = copy.deepcopy(lock)
    tampered["source_freeze"]["artifact_id"] += 1

    with pytest.raises(ValueError, match="content does not match"):
        verify_korthals_source_lock(tampered)


def _locked_manifest_identity() -> dict:
    lock = load_korthals_source_lock()
    return {
        "source_manifest_fingerprint": lock["source"]["source_manifest_fingerprint"],
        "file_count": lock["source"]["file_count"],
        "participant_count": lock["source"]["participant_count"],
        "participants": lock["source"]["participants"],
        "download_contract": lock["osf"]["download_contract"],
        "osf_doi": lock["osf"]["doi"],
        "osf_project": lock["osf"]["project"],
        "companion_commit": lock["companion"]["commit"],
        "protocol_fingerprint": lock["protocol_fingerprint"],
    }


def test_current_osf_manifest_must_match_every_locked_identity_field(monkeypatch):
    manifest = _locked_manifest_identity()
    monkeypatch.setattr(source_lock, "verify_korthals_source_manifest_v2", lambda _: True)

    verified = verify_korthals_locked_source_manifest(manifest)
    assert verified["source_manifest_fingerprint"] == manifest["source_manifest_fingerprint"]

    changed = copy.deepcopy(manifest)
    changed["source_manifest_fingerprint"] = "0" * 64
    with pytest.raises(ValueError, match="differs from locked source"):
        verify_korthals_locked_source_manifest(changed)


def _locked_prepared_fixture() -> PreparedKorthalsData:
    lock = load_korthals_source_lock()
    intake = lock["intake"]
    n_rows = int(intake["prepared_row_count"])
    target_type = pd.Categorical(
        np.resize(np.array(["jumping_circle", "moving_circle"], dtype=object), n_rows)
    )
    data = pd.DataFrame({"target_type": target_type})
    validation_groups = pd.DataFrame({"validation_nr": range(intake["validation_group_count"])})
    identity = {
        "source_manifest_fingerprint": lock["source"]["source_manifest_fingerprint"],
        "source_file_count": lock["source"]["file_count"],
        "participant_count": lock["source"]["participant_count"],
        "participant_split_fingerprint": intake["participant_split_fingerprint"],
        "retained_trial_count": intake["retained_trial_count"],
        "missingness_policy": intake["missingness_policy"],
        "zero_finite_scheduled_trial_count": intake["zero_finite_scheduled_trial_count"],
        "zero_finite_scheduled_trials": intake["zero_finite_scheduled_trials"],
        "sampling_incomplete_matched_cell_count": (
            intake["sampling_incomplete_matched_cell_count"]
        ),
        "sampling_incomplete_matched_cells": intake["sampling_incomplete_matched_cells"],
        "case_study_id": lock["case_study_id"],
        "protocol_fingerprint": lock["protocol_fingerprint"],
        "companion_commit": lock["companion"]["commit"],
    }
    return PreparedKorthalsData(data, validation_groups, identity)


def test_prepared_endpoint_blind_intake_must_reproduce_locked_freeze_facts():
    prepared = _locked_prepared_fixture()
    assert verify_korthals_locked_prepared(prepared) is prepared

    prepared.source_identity["retained_trial_count"] -= 1
    with pytest.raises(ValueError, match="differs from locked source freeze"):
        verify_korthals_locked_prepared(prepared)
