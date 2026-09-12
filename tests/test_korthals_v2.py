from __future__ import annotations

import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit.korthals_execution import (
    KORTHALS_COMPANION_COMMIT,
    KORTHALS_PROTOCOL_FINGERPRINT,
)
from gazeaudit.korthals_freeze import (
    KORTHALS_COMPANION_REPOSITORY,
    KORTHALS_FREEZE_WORKFLOW,
)
from gazeaudit.korthals_freeze_v2 import (
    verify_korthals_source_freeze_artifacts_v2,
    write_korthals_source_freeze_artifacts_v2,
)
from gazeaudit.korthals_v2 import (
    KORTHALS_V2_CASE_STUDY_ID,
    KORTHALS_V2_MISSINGNESS_POLICY,
    KORTHALS_V2_PROTOCOL_FINGERPRINT,
    KorthalsSourceIntakeV2,
    build_korthals_source_manifest_v2,
    load_korthals_protocol_v2,
    prepare_korthals_aligned_data_v2,
    verify_korthals_protocol_v2,
    verify_korthals_source_intake_artifacts_v2,
    verify_korthals_source_manifest_v2,
    write_korthals_source_intake_artifacts_v2,
)
from gazeaudit.provenance import fingerprint


def _aligned_fixture(*, participants=("p1", "p2")) -> pd.DataFrame:
    rows = []
    trial_specs = [
        (1, "moving_circle", 4.0, "east"),
        (2, "jumping_circle", 4.0, "east"),
        (73, "moving_circle", 6.0, "north"),
        (74, "jumping_circle", 6.0, "north"),
    ]
    for participant in participants:
        for trial_number, target_type, speed, trajectory in trial_specs:
            relative_x = 2.0 if target_type == "moving_circle" else 0.0
            for trial_time in (0.0, 0.02, 0.04):
                rows.append(
                    {
                        "participant_id": participant,
                        "trial_number": trial_number,
                        "trial_time": trial_time,
                        "gaze_x": relative_x,
                        "gaze_y": 0.0,
                        "target_x": 0.0,
                        "target_y": 0.0,
                        "target_type": target_type,
                        "target_speed": speed,
                        "target_trajectory": trajectory,
                    }
                )
    return pd.DataFrame(rows)


def _validation_fixture(*, participants=("p1", "p2")) -> pd.DataFrame:
    rows = []
    for participant in participants:
        rows.extend(
            [
                {
                    "participant_id": participant,
                    "validation_nr": 1,
                    "error_avg": 0.4,
                    "first_trial": 1,
                    "last_trial": 72,
                },
                {
                    "participant_id": participant,
                    "validation_nr": 2,
                    "error_avg": 0.6,
                    "first_trial": 73,
                    "last_trial": 144,
                },
            ]
        )
    return pd.DataFrame(rows)


def _source_tree(tmp_path: Path, participant: str = "p1") -> Path:
    root = tmp_path / "data"
    clean = root / "clean" / "train" / participant
    raw = root / "raw" / "train" / participant
    clean.mkdir(parents=True)
    raw.mkdir(parents=True)
    (clean / f"{participant}_gaze.csv").write_text(
        f"participant_id,marker\n{participant},gaze\n",
        encoding="utf-8",
    )
    (raw / f"{participant}.asc").write_text("raw fixture\n", encoding="utf-8")
    return root


def _source_identity(manifest: dict, participant: str = "p1") -> dict:
    split_records = [{"participant_id": participant, "split": "train"}]
    return {
        "source_manifest_fingerprint": manifest["source_manifest_fingerprint"],
        "source_file_count": manifest["file_count"],
        "download_contract": manifest["download_contract"],
        "participant_split_fingerprint": fingerprint(split_records),
        "participant_splits": split_records,
    }


def test_protocol_v2_is_versioned_and_v1_remains_its_explicit_predecessor():
    protocol = load_korthals_protocol_v2()
    committed = json.loads(
        Path("docs/protocols/korthals2026_target_tracking_aoi_v2.json").read_text(
            encoding="utf-8"
        )
    )

    assert protocol == committed
    assert verify_korthals_protocol_v2(protocol) == protocol
    assert protocol["case_study_id"] == KORTHALS_V2_CASE_STUDY_ID
    assert protocol["protocol_fingerprint"] == KORTHALS_V2_PROTOCOL_FINGERPRINT
    assert protocol["amendment"]["supersedes_protocol_fingerprint"] == (
        KORTHALS_PROTOCOL_FINGERPRINT
    )
    assert protocol["amendment"]["scientific_endpoint_executed_before_amendment"] is False


def test_zero_finite_trial_removes_its_entire_matched_cell_without_recovery():
    aligned = _aligned_fixture(participants=("p1",))
    aligned.loc[aligned["trial_number"] == 2, ["gaze_x", "gaze_y"]] = np.nan

    prepared = prepare_korthals_aligned_data_v2(
        aligned,
        _validation_fixture(participants=("p1",)),
    )

    assert set(prepared.data["trial_number"]) == {73, 74}
    assert prepared.source_identity["missingness_policy"] == KORTHALS_V2_MISSINGNESS_POLICY
    assert prepared.source_identity["zero_finite_scheduled_trials"] == [
        {"participant_id": "p1", "trial_number": 2}
    ]
    assert prepared.source_identity["sampling_incomplete_matched_cells"] == [
        {
            "participant_id": "p1",
            "repetition": 1,
            "target_speed": 4.0,
            "target_trajectory": "east",
            "trial_numbers": [1, 2],
        }
    ]
    assert prepared.source_identity["retained_trial_count"] == 2


def test_v2_does_not_drop_any_cell_when_every_trial_has_finite_grid_samples():
    prepared = prepare_korthals_aligned_data_v2(
        _aligned_fixture(participants=("p1",)),
        _validation_fixture(participants=("p1",)),
    )

    assert set(prepared.data["trial_number"]) == {1, 2, 73, 74}
    assert prepared.source_identity["zero_finite_scheduled_trial_count"] == 0
    assert prepared.source_identity["sampling_incomplete_matched_cell_count"] == 0


def test_v2_still_fails_closed_for_unrelated_source_pairing_gap():
    aligned = _aligned_fixture(participants=("p1",))
    aligned = aligned[aligned["trial_number"] != 2].copy()

    with pytest.raises(ValueError, match="incomplete or duplicated frozen matched cell"):
        prepare_korthals_aligned_data_v2(
            aligned,
            _validation_fixture(participants=("p1",)),
        )


def test_zero_finite_trial_cannot_hide_an_unmapped_validation():
    aligned = _aligned_fixture(participants=("p1",))
    aligned.loc[aligned["trial_number"] == 2, ["gaze_x", "gaze_y"]] = np.nan
    validation = _validation_fixture(participants=("p1",))
    validation = validation[validation["validation_nr"] == 2].copy()

    with pytest.raises(ValueError, match="exactly one validation block"):
        prepare_korthals_aligned_data_v2(aligned, validation)


def test_participant_cannot_disappear_because_all_of_their_cells_are_zero_finite():
    aligned = _aligned_fixture(participants=("p1", "p2"))
    aligned.loc[
        (aligned["participant_id"] == "p1")
        & aligned["trial_number"].isin([2, 74]),
        ["gaze_x", "gaze_y"],
    ] = np.nan

    with pytest.raises(ValueError, match="every participant"):
        prepare_korthals_aligned_data_v2(
            aligned,
            _validation_fixture(participants=("p1", "p2")),
        )


def test_source_manifest_v2_reuses_exact_source_bytes_but_has_new_protocol_identity(tmp_path):
    root = _source_tree(tmp_path)
    manifest = build_korthals_source_manifest_v2(root)

    assert verify_korthals_source_manifest_v2(manifest)
    assert manifest["case_study_id"] == KORTHALS_V2_CASE_STUDY_ID
    assert manifest["protocol_fingerprint"] == KORTHALS_V2_PROTOCOL_FINGERPRINT
    assert manifest["participants"] == ["p1"]
    assert manifest["file_count"] == 2


def test_v2_intake_and_freeze_artifacts_are_endpoint_blind_and_tamper_evident(tmp_path):
    root = _source_tree(tmp_path)
    source_manifest = build_korthals_source_manifest_v2(root)
    prepared = prepare_korthals_aligned_data_v2(
        _aligned_fixture(participants=("p1",)),
        _validation_fixture(participants=("p1",)),
        source_identity=_source_identity(source_manifest),
    )
    intake = KorthalsSourceIntakeV2(
        prepared=prepared,
        source_manifest=source_manifest,
        participant_splits=(("p1", "train"),),
    )
    intake_dir = tmp_path / "intake"
    write_korthals_source_intake_artifacts_v2(intake, intake_dir)
    assert verify_korthals_source_intake_artifacts_v2(intake_dir)

    summary_text = (intake_dir / "intake_summary.json").read_text(encoding="utf-8")
    for forbidden in (
        "hard_effect",
        "classification",
        "probability_above_reference",
        "draw_effects",
    ):
        assert forbidden not in summary_text

    context = {
        "repository": "stefanosbalaskas/GazeAudit",
        "execution_commit": "a" * 40,
        "workflow_ref": KORTHALS_FREEZE_WORKFLOW,
        "github_run_id": "123",
        "companion_repository": KORTHALS_COMPANION_REPOSITORY,
        "companion_commit": KORTHALS_COMPANION_COMMIT,
        "protocol_fingerprint": KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": source_manifest["source_manifest_fingerprint"],
        "package_version": version("gazeaudit"),
        "python_version": "3.12-test",
        "platform": "test-platform",
        "runner_os": "Linux",
        "runner_arch": "X64",
    }
    freeze_dir = tmp_path / "freeze"
    write_korthals_source_freeze_artifacts_v2(
        intake_dir,
        freeze_dir,
        execution_context=context,
        environment_text="gazeaudit==0.1.0.dev19\npandas==2.3.3\n",
    )
    assert verify_korthals_source_freeze_artifacts_v2(freeze_dir)

    manifest = freeze_dir / "freeze_manifest.json"
    manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert not verify_korthals_source_freeze_artifacts_v2(freeze_dir)
