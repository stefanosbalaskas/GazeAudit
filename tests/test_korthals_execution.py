import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit.korthals_execution import (
    KORTHALS_COMPANION_COMMIT,
    KORTHALS_PROTOCOL_FINGERPRINT,
    korthals_paired_occupancy_effect,
    load_korthals_protocol,
    prepare_korthals_aligned_data,
    run_korthals_aoi_execution,
    verify_korthals_execution_artifacts,
    verify_korthals_protocol,
    write_korthals_execution_artifacts,
)


def _aligned_fixture(*, participants=("p1", "p2")) -> pd.DataFrame:
    rows = []
    trial_specs = [
        (1, "moving_circle", 4.0, "east", 2.0),
        (2, "jumping_circle", 4.0, "east", 0.0),
        (73, "moving_circle", 6.0, "north", 2.0),
        (74, "jumping_circle", 6.0, "north", 0.0),
    ]
    # 0.020 is exactly between 0.019 and 0.021. The frozen rule must choose 0.019.
    times = [0.0, 0.019, 0.021, 0.04]
    for participant in participants:
        for trial_number, target_type, speed, trajectory, relative_gaze_x in trial_specs:
            for trial_time in times:
                gaze_x = relative_gaze_x
                if trial_time == 0.021:
                    gaze_x = 99.0  # would expose wrong tie-breaking at the 20-ms grid point
                if trial_time == 0.04:
                    gaze_x = np.nan  # selected on-grid, then removed after downsampling
                # Keep actual_speed deliberately different across target types. If the
                # adapter ever aliases it to the frozen target_speed design factor,
                # moving/jumping pairing will fail and these fixtures expose the drift.
                actual_speed = speed + (0.01 if target_type == "moving_circle" else 0.02)
                rows.append(
                    {
                        "participant_id": participant,
                        "trial_number": trial_number,
                        "trial_time": trial_time,
                        "gaze_x": gaze_x,
                        "gaze_y": 0.0,
                        "target_x": 0.0,
                        "target_y": 0.0,
                        "target_type": target_type,
                        "target_speed": speed,
                        "actual_speed": actual_speed,
                        "target_trajectory": trajectory,
                    }
                )
    return pd.DataFrame(rows)


def _validation_fixture(*, participants=("p1", "p2"), error_avg=0.0) -> pd.DataFrame:
    rows = []
    for participant in participants:
        rows.extend(
            [
                {
                    "participant_id": participant,
                    "validation_nr": 1,
                    "error_avg": error_avg,
                    "first_trial": 1,
                    "last_trial": 72,
                },
                {
                    "participant_id": participant,
                    "validation_nr": 2,
                    "error_avg": error_avg,
                    "first_trial": 73,
                    "last_trial": 144,
                },
            ]
        )
    return pd.DataFrame(rows)


def test_packaged_korthals_protocol_is_the_merged_frozen_document():
    packaged = load_korthals_protocol()
    committed = json.loads(
        Path("docs/protocols/korthals2026_target_tracking_aoi_v1.json").read_text(
            encoding="utf-8"
        )
    )
    assert packaged == committed
    assert packaged["protocol_fingerprint"] == KORTHALS_PROTOCOL_FINGERPRINT
    assert packaged["dataset"]["companion_commit"] == KORTHALS_COMPANION_COMMIT
    assert verify_korthals_protocol(packaged) == packaged


def test_prepare_applies_frozen_grid_tie_break_validation_mapping_and_gaze_ordering():
    prepared = prepare_korthals_aligned_data(
        _aligned_fixture(),
        _validation_fixture(error_avg=0.4),
        source_identity={"fixture": "synthetic-contract-only"},
    )

    # Three scheduled rows (0, .02, .04) exist per trial before finite-gaze filtering;
    # the on-grid .04 row is then removed because gaze is NaN.
    assert len(prepared.data) == 2 * 4 * 2
    assert set(prepared.data["scheduled_trial_time"].unique()) == {0.0, 0.02}
    assert set(prepared.data.loc[prepared.data["scheduled_trial_time"] == 0.02, "trial_time"]) == {
        0.019
    }
    assert 99.0 not in set(prepared.data["gaze_x"])
    assert set(prepared.data["target_speed"]) == {4.0, 6.0}
    assert set(prepared.data["actual_speed"]) == {4.01, 4.02, 6.01, 6.02}

    first = prepared.data[prepared.data["trial_number"].isin([1, 2])]
    second = prepared.data[prepared.data["trial_number"].isin([73, 74])]
    assert set(first["validation_nr"]) == {1}
    assert set(second["validation_nr"]) == {2}
    assert set(first["repetition"]) == {1}
    assert set(second["repetition"]) == {2}
    assert set(prepared.validation_groups["n_validation"]) == {9}
    assert prepared.source_identity["protocol_fingerprint"] == KORTHALS_PROTOCOL_FINGERPRINT


def test_prepare_requires_frozen_target_speed_even_when_actual_speed_exists():
    aligned = _aligned_fixture(participants=("p1",)).drop(columns="target_speed")
    with pytest.raises(ValueError, match="target_speed"):
        prepare_korthals_aligned_data(
            aligned,
            _validation_fixture(participants=("p1",)),
        )


def test_prepare_drops_only_cell_made_incomplete_by_author_directed_exclusion():
    base = _aligned_fixture(participants=("21db28aa",))
    # This remains a complete speed/trajectory pair before exclusion. Trial 82 is
    # excluded by protocol, making trial 81's repetition-2 cell incomplete afterwards.
    base.loc[base["trial_number"] == 73, "trial_number"] = 81
    base.loc[base["trial_number"] == 74, "trial_number"] = 82
    prepared = prepare_korthals_aligned_data(
        base,
        _validation_fixture(participants=("21db28aa",)),
    )
    assert set(prepared.data["trial_number"]) == {1, 2}
    assert prepared.source_identity["retained_trial_count"] == 2


def test_prepare_rejects_unrelated_pre_exclusion_pairing_gap():
    base = _aligned_fixture(participants=("p1",))
    base = base[base["trial_number"] != 74].copy()
    with pytest.raises(ValueError, match="incomplete or duplicated frozen matched cell"):
        prepare_korthals_aligned_data(
            base,
            _validation_fixture(participants=("p1",)),
        )


def test_prepare_fails_closed_for_unmapped_validation_or_zero_finite_trial():
    aligned = _aligned_fixture(participants=("p1",))
    validation = _validation_fixture(participants=("p1",))

    broken_mapping = validation[validation["validation_nr"] == 1].copy()
    with pytest.raises(ValueError, match="exactly one validation block"):
        prepare_korthals_aligned_data(aligned, broken_mapping)

    broken_gaze = aligned.copy()
    broken_gaze.loc[broken_gaze["trial_number"] == 2, ["gaze_x", "gaze_y"]] = np.nan
    with pytest.raises(ValueError, match="zero finite scheduled samples"):
        prepare_korthals_aligned_data(broken_gaze, validation)


def test_prepare_fails_closed_for_overlapping_validation_ranges_and_identity_override():
    aligned = _aligned_fixture(participants=("p1",))
    validation = _validation_fixture(participants=("p1",))
    validation.loc[validation["validation_nr"] == 2, "first_trial"] = 2
    with pytest.raises(ValueError, match="exactly one validation block"):
        prepare_korthals_aligned_data(aligned, validation)

    with pytest.raises(ValueError, match="may not override"):
        prepare_korthals_aligned_data(
            aligned,
            _validation_fixture(participants=("p1",)),
            source_identity={"companion_commit": "different"},
        )


def test_frozen_endpoint_is_unweighted_participant_then_study_contrast():
    data = pd.DataFrame(
        {
            "participant_id": ["p1"] * 4 + ["p2"] * 4,
            "trial_number": [1, 1, 2, 2, 1, 1, 2, 2],
            "repetition": [1] * 8,
            "target_speed": [4.0] * 8,
            "target_trajectory": ["east"] * 8,
            "target_type": ["moving_circle"] * 2
            + ["jumping_circle"] * 2
            + ["moving_circle"] * 2
            + ["jumping_circle"] * 2,
        }
    )
    # p1: moving=.25, jumping=.75 => +.50; p2: moving=.50, jumping=1 => +.50.
    membership = np.array([0.0, 0.5, 0.5, 1.0, 0.0, 1.0, 1.0, 1.0])
    assert korthals_paired_occupancy_effect(data, membership) == pytest.approx(0.5)


def test_frozen_endpoint_rejects_incomplete_arbitrary_cell():
    data = pd.DataFrame(
        {
            "participant_id": ["p1", "p1"],
            "trial_number": [1, 1],
            "repetition": [1, 1],
            "target_speed": [4.0, 4.0],
            "target_trajectory": ["east", "east"],
            "target_type": ["moving_circle", "moving_circle"],
        }
    )
    with pytest.raises(ValueError, match="complete frozen matched cell"):
        korthals_paired_occupancy_effect(data, np.array([0.0, 1.0]))


def test_synthetic_execution_uses_frozen_mc_and_classifies_sign_stability():
    prepared = prepare_korthals_aligned_data(
        _aligned_fixture(),
        _validation_fixture(error_avg=0.0),
        source_identity={"fixture": "known-zero-measurement-error"},
    )
    execution = run_korthals_aoi_execution(prepared)

    assert execution.classification == "robust_positive"
    assert execution.audit.summary["n_draws"] == 2000
    assert execution.audit.summary["hard_effect"] == pytest.approx(1.0)
    assert execution.audit.summary["probability_above_reference"] == pytest.approx(1.0)
    assert execution.execution_manifest["protocol_fingerprint"] == KORTHALS_PROTOCOL_FINGERPRINT
    assert len(execution.execution_fingerprint) == 64


def test_korthals_outer_artifact_envelope_verifies_and_detects_tampering(tmp_path):
    prepared = prepare_korthals_aligned_data(
        _aligned_fixture(participants=("p1",)),
        _validation_fixture(participants=("p1",), error_avg=0.0),
    )
    execution = run_korthals_aoi_execution(prepared)
    output = tmp_path / "korthals"
    manifest = write_korthals_execution_artifacts(execution, output)

    assert manifest["classification"] == "robust_positive"
    assert verify_korthals_execution_artifacts(output)

    source = output / "source_identity.json"
    source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert not verify_korthals_execution_artifacts(output)
