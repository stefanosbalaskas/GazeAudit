from __future__ import annotations

from pathlib import Path

import pandas as pd

from gazeaudit.korthals_execution import KORTHALS_PROTOCOL_FINGERPRINT
from gazeaudit.korthals_source import (
    KORTHALS_COMPANION_COMMIT,
    KORTHALS_SOURCE_SCHEMA,
    _align_companion_preprocessed_participant,
    build_korthals_source_manifest,
    discover_korthals_participants,
    prepare_korthals_from_companion,
    verify_korthals_source_intake_artifacts,
    verify_korthals_source_manifest,
    write_korthals_source_intake_artifacts,
)


def _make_source_tree(tmp_path: Path) -> Path:
    root = tmp_path / "data"
    for split, participant in [("train", "p1"), ("test", "p2")]:
        clean = root / "clean" / split / participant
        raw = root / "raw" / split / participant
        clean.mkdir(parents=True)
        raw.mkdir(parents=True)
        for table in ["gaze", "targets", "trials", "blinks"]:
            (clean / f"{participant}_{table}.csv").write_text(
                f"participant_id,marker\n{participant},{table}\n",
                encoding="utf-8",
            )
        (raw / f"{participant}.asc").write_text(
            f"synthetic raw contract fixture for {participant}\n",
            encoding="utf-8",
        )
    return root


def _preprocessed_tables(participant_id: str) -> dict[str, pd.DataFrame]:
    trial_specs = [
        (1, "moving_circle", 4.0, "east"),
        (2, "jumping_circle", 4.0, "east"),
        (73, "moving_circle", 6.0, "north"),
        (74, "jumping_circle", 6.0, "north"),
    ]
    gaze_rows = []
    target_rows = []
    trial_rows = []
    for trial_number, target_type, speed, trajectory in trial_specs:
        trial_rows.append(
            {
                "participant_id": participant_id,
                "trial_number": trial_number,
                "target_type": target_type,
                "target_speed": speed,
                "actual_speed": speed + 0.01,
                "target_trajectory": trajectory,
            }
        )
        relative_x = 2.0 if target_type == "moving_circle" else 0.0
        for trial_time in [0.0, 0.02, 0.04]:
            gaze_rows.append(
                {
                    "participant_id": participant_id,
                    "trial_number": trial_number,
                    "trial_time": trial_time,
                    "gaze_x": relative_x,
                    "gaze_y": 0.0,
                    "velocity": 0.0,
                    "blink": False,
                }
            )
            target_rows.append(
                {
                    "participant_id": participant_id,
                    "trial_number": trial_number,
                    "trial_time": trial_time,
                    "target_x": 0.0,
                    "target_y": 0.0,
                }
            )
    return {
        "gaze": pd.DataFrame(gaze_rows),
        "targets": pd.DataFrame(target_rows),
        "trials": pd.DataFrame(trial_rows),
        "blinks": pd.DataFrame(
            {
                "participant_id": [participant_id],
                "trial_number": [1],
                "blink_start": [999.0],
                "blink_end": [1000.0],
            }
        ),
    }


class _FakeParticipant:
    tables_by_participant: dict[str, dict[str, pd.DataFrame]] = {}

    def __init__(self, id: str, preprocessor):
        self.id = id
        self.preprocessor = preprocessor
        self.subset = "train" if id == "p1" else "test"
        self.clean_data: dict[str, pd.DataFrame] = {}
        self.preprocessed_data: dict[str, pd.DataFrame] = {}

    def set_clean_data(self, data_path: str) -> None:
        assert data_path == "data/clean"
        tables = self.tables_by_participant[self.id]
        self.clean_data = {name: frame.copy() for name, frame in tables.items()}

    def preprocess_clean_data(self, **kwargs) -> None:
        assert kwargs == {"blink_offset": (50, 50), "rolling_mean_window": 1}
        self.preprocessed_data = {
            name: frame.copy() for name, frame in self.clean_data.items()
        }

    def validation_check(self, raw_data_path: str) -> pd.DataFrame:
        assert raw_data_path == "data/raw"
        return pd.DataFrame(
            {
                "participant_id": [self.id, self.id],
                "validation_nr": [1, 2],
                "error_avg": [0.4, 0.6],
                "first_trial": [1, 73],
                "last_trial": [72, 144],
            }
        )


class _FakePreprocessor:
    pass


def _configure_fakes() -> None:
    _FakeParticipant.tables_by_participant = {
        "p1": _preprocessed_tables("p1"),
        "p2": _preprocessed_tables("p2"),
    }


def test_source_manifest_is_deterministic_and_bound_to_public_identity(tmp_path):
    root = _make_source_tree(tmp_path)
    assert discover_korthals_participants(root) == ["p1", "p2"]

    first = build_korthals_source_manifest(root)
    second = build_korthals_source_manifest(root)
    assert first == second
    assert first["schema"] == KORTHALS_SOURCE_SCHEMA
    assert first["protocol_fingerprint"] == KORTHALS_PROTOCOL_FINGERPRINT
    assert first["companion_commit"] == KORTHALS_COMPANION_COMMIT
    assert first["participant_count"] == 2
    assert first["download_contract"] == {
        "raw_clean": "both",
        "train_test": "both",
        "participants": "all",
    }
    assert verify_korthals_source_manifest(first)

    altered = dict(first)
    altered["participant_count"] = 3
    assert not verify_korthals_source_manifest(altered)


def test_source_manifest_changes_when_any_published_file_changes(tmp_path):
    root = _make_source_tree(tmp_path)
    before = build_korthals_source_manifest(root)
    file_path = root / "raw" / "train" / "p1" / "p1.asc"
    file_path.write_text("changed bytes\n", encoding="utf-8")
    after = build_korthals_source_manifest(root)
    assert before["source_manifest_fingerprint"] != after["source_manifest_fingerprint"]


def test_companion_intake_runs_full_cohort_without_endpoint(tmp_path):
    root = _make_source_tree(tmp_path)
    _configure_fakes()
    intake = prepare_korthals_from_companion(
        root,
        participant_factory=_FakeParticipant,
        preprocessor_factory=_FakePreprocessor,
    )

    assert intake.source_manifest["participants"] == ["p1", "p2"]
    assert intake.participant_splits == (("p1", "train"), ("p2", "test"))
    assert intake.prepared.source_identity["participant_count"] == 2
    assert intake.prepared.source_identity["source_manifest_fingerprint"] == intake.source_manifest[
        "source_manifest_fingerprint"
    ]
    assert set(intake.prepared.data["target_speed"]) == {4.0, 6.0}
    assert len(intake.prepared.validation_groups) == 4


def test_companion_alignment_uses_preprocessed_target_timeline_as_master():
    tables = _preprocessed_tables("p1")
    target_only = pd.DataFrame(
        [
            {
                "participant_id": "p1",
                "trial_number": 1,
                "trial_time": 0.06,
                "target_x": 0.25,
                "target_y": -0.25,
            }
        ]
    )
    gaze_only = pd.DataFrame(
        [
            {
                "participant_id": "p1",
                "trial_number": 1,
                "trial_time": 0.01,
                "gaze_x": 99.0,
                "gaze_y": 99.0,
                "velocity": 0.0,
                "blink": False,
            }
        ]
    )
    tables["targets"] = pd.concat([tables["targets"], target_only], ignore_index=True)
    tables["gaze"] = pd.concat([tables["gaze"], gaze_only], ignore_index=True)

    aligned = _align_companion_preprocessed_participant("p1", tables)
    trial_one = aligned[aligned["trial_number"] == 1].sort_values("trial_time")

    assert 0.06 in trial_one["trial_time"].tolist()
    assert 0.01 not in trial_one["trial_time"].tolist()
    target_only_row = trial_one.loc[trial_one["trial_time"] == 0.06].iloc[0]
    assert target_only_row["target_x"] == 0.25
    assert target_only_row["target_y"] == -0.25
    assert pd.isna(target_only_row["gaze_x"])
    assert pd.isna(target_only_row["gaze_y"])


def test_source_intake_artifact_contains_no_scientific_effect_and_detects_tampering(tmp_path):
    root = _make_source_tree(tmp_path)
    _configure_fakes()
    intake = prepare_korthals_from_companion(
        root,
        participant_factory=_FakeParticipant,
        preprocessor_factory=_FakePreprocessor,
    )
    output = tmp_path / "intake"
    manifest = write_korthals_source_intake_artifacts(intake, output)

    assert manifest["source_manifest_fingerprint"] == intake.source_manifest[
        "source_manifest_fingerprint"
    ]
    assert verify_korthals_source_intake_artifacts(output)
    summary_text = (output / "intake_summary.json").read_text(encoding="utf-8")
    assert "hard_effect" not in summary_text
    assert "classification" not in summary_text
    assert "probability_above_reference" not in summary_text

    source = output / "source_manifest.json"
    source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert not verify_korthals_source_intake_artifacts(output)
