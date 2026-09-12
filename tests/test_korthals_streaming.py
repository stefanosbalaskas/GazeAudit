from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit.korthals_streaming import (
    combine_korthals_prepared_participants_v2,
    prepare_korthals_from_companion_v2_streaming,
)
from gazeaudit.korthals_v2 import (
    build_korthals_source_manifest_v2,
    prepare_korthals_aligned_data_v2,
)
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


def _source_tree(tmp_path: Path) -> Path:
    root = tmp_path / "data"
    for participant_id, split in (("p1", "train"), ("p2", "test")):
        clean = root / "clean" / split / participant_id
        raw = root / "raw" / split / participant_id
        clean.mkdir(parents=True)
        raw.mkdir(parents=True)
        (clean / f"{participant_id}_participant.csv").write_text(
            f"participant_id,marker\n{participant_id},fixture\n",
            encoding="utf-8",
        )
        (raw / f"{participant_id}.asc").write_text("raw fixture\n", encoding="utf-8")
    return root


class _FakeParticipant:
    aligned = _aligned_fixture()
    validations = _validation_fixture()

    def __init__(self, *, id: str, preprocessor: object):
        self.id = id
        self.preprocessor = preprocessor
        self.subset = "train" if id == "p1" else "test"
        self.clean_data: dict[str, pd.DataFrame] = {}
        self.preprocessed_data: dict[str, pd.DataFrame] = {}

    def set_clean_data(self, _path: str) -> None:
        self.clean_data = {
            label: pd.DataFrame({"participant_id": [self.id], "fixture": [1]})
            for label in ("gaze", "targets", "trials", "blinks")
        }

    def preprocess_clean_data(
        self,
        *,
        blink_offset: tuple[int, int],
        rolling_mean_window: int,
    ) -> None:
        assert blink_offset == (50, 50)
        assert rolling_mean_window == 1
        frame = self.aligned[self.aligned["participant_id"] == self.id].copy()
        key = ["participant_id", "trial_number", "trial_time"]
        self.preprocessed_data = {
            "gaze": frame[key + ["gaze_x", "gaze_y"]].copy(),
            "targets": frame[key + ["target_x", "target_y"]].copy(),
            "trials": frame[
                [
                    "participant_id",
                    "trial_number",
                    "target_type",
                    "target_speed",
                    "target_trajectory",
                ]
            ]
            .drop_duplicates()
            .copy(),
        }

    def validation_check(self, _path: str) -> pd.DataFrame:
        return self.validations[self.validations["participant_id"] == self.id].copy()


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


def test_streamed_companion_intake_matches_monolithic_preparation(tmp_path):
    root = _source_tree(tmp_path)
    manifest = build_korthals_source_manifest_v2(root)
    split_records = [
        {"participant_id": "p1", "split": "train"},
        {"participant_id": "p2", "split": "test"},
    ]
    source_identity = {
        "source_manifest_fingerprint": manifest["source_manifest_fingerprint"],
        "source_file_count": manifest["file_count"],
        "download_contract": manifest["download_contract"],
        "participant_split_fingerprint": fingerprint(split_records),
        "participant_splits": split_records,
    }
    canonical_aligned = _aligned_fixture()[
        [
            "participant_id",
            "trial_number",
            "trial_time",
            "target_x",
            "target_y",
            "gaze_x",
            "gaze_y",
            "target_type",
            "target_speed",
            "target_trajectory",
        ]
    ].copy()
    monolithic = prepare_korthals_aligned_data_v2(
        canonical_aligned,
        _validation_fixture(),
        source_identity=source_identity,
    )

    intake = prepare_korthals_from_companion_v2_streaming(
        root,
        participant_factory=_FakeParticipant,
        preprocessor_factory=object,
    )

    pd.testing.assert_frame_equal(intake.prepared.data, monolithic.data)
    pd.testing.assert_frame_equal(
        intake.prepared.validation_groups,
        monolithic.validation_groups,
    )
    assert intake.prepared.source_identity == monolithic.source_identity
    assert intake.participant_splits == (("p1", "train"), ("p2", "test"))
    assert intake.source_manifest == manifest


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
