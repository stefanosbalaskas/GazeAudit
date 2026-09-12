from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from gazeaudit.korthals_streaming import combine_korthals_prepared_participants_v2
from gazeaudit.korthals_v2 import prepare_korthals_aligned_data_v2
from gazeaudit.provenance import fingerprint


def _aligned_fixture() -> pd.DataFrame:
    rows = []
    trial_specs = [
        (1, "moving_circle", 4.0, "east"),
        (2, "jumping_circle", 4.0, "east"),
        (73, "moving_circle", 6.0, "north"),
        (74, "jumping_circle", 6.0, "north"),
    ]
    for participant in ("p1", "p2"):
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
    frame = pd.DataFrame(rows)
    frame.loc[
        (frame["participant_id"] == "p1") & (frame["trial_number"] == 2),
        ["gaze_x", "gaze_y"],
    ] = np.nan
    return frame


def _validation_fixture() -> pd.DataFrame:
    rows = []
    for participant in ("p1", "p2"):
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


def _source_identity() -> dict:
    split_records = [
        {"participant_id": "p1", "split": "train"},
        {"participant_id": "p2", "split": "test"},
    ]
    return {
        "source_manifest_fingerprint": "a" * 64,
        "source_file_count": 112,
        "download_contract": {
            "raw_clean": "both",
            "train_test": "both",
            "participants": "all",
        },
        "participant_split_fingerprint": fingerprint(split_records),
        "participant_splits": split_records,
    }


def test_participant_streaming_combination_is_exactly_monolithic_v2_equivalent():
    aligned = _aligned_fixture()
    validations = _validation_fixture()
    source_identity = _source_identity()

    monolithic = prepare_korthals_aligned_data_v2(
        aligned,
        validations,
        source_identity=source_identity,
    )
    parts = []
    for participant_id in ("p1", "p2"):
        parts.append(
            prepare_korthals_aligned_data_v2(
                aligned[aligned["participant_id"] == participant_id].copy(),
                validations[validations["participant_id"] == participant_id].copy(),
            )
        )

    streamed = combine_korthals_prepared_participants_v2(
        parts,
        expected_participants=["p1", "p2"],
        source_identity=source_identity,
    )

    pd.testing.assert_frame_equal(streamed.data, monolithic.data)
    pd.testing.assert_frame_equal(streamed.validation_groups, monolithic.validation_groups)
    assert streamed.source_identity == monolithic.source_identity


def test_streaming_combiner_fails_closed_on_duplicate_or_missing_participants():
    aligned = _aligned_fixture()
    validations = _validation_fixture()
    p1 = prepare_korthals_aligned_data_v2(
        aligned[aligned["participant_id"] == "p1"].copy(),
        validations[validations["participant_id"] == "p1"].copy(),
    )

    with pytest.raises(ValueError, match="expected cohort"):
        combine_korthals_prepared_participants_v2(
            [p1],
            expected_participants=["p1", "p2"],
            source_identity=_source_identity(),
        )

    with pytest.raises(ValueError, match="cover the expected cohort exactly"):
        combine_korthals_prepared_participants_v2(
            [p1, p1],
            expected_participants=["p1", "p2"],
            source_identity=_source_identity(),
        )
