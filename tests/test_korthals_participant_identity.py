from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from gazeaudit.korthals_source import (
    _canonicalize_companion_participant_identity,
    _participant_identity_value_matches,
)


def _write_identity_csv(
    clean_root: Path,
    participant_id: str,
    name: str,
    value: str,
    *,
    split: str = "train",
) -> Path:
    participant_root = clean_root / split / participant_id
    participant_root.mkdir(parents=True, exist_ok=True)
    path = participant_root / f"{participant_id}_{name}.csv"
    path.write_text(
        f"participant_id,trial_number,value\n{value},1,0.0\n",
        encoding="utf-8",
    )
    return path


def test_scientific_notation_like_id_accepts_published_numeric_coercion_and_restores_path_id(
    tmp_path: Path,
):
    participant_id = "68471e16"
    clean_root = tmp_path / "clean"
    _write_identity_csv(clean_root, participant_id, "gaze", participant_id)
    _write_identity_csv(clean_root, participant_id, "participant", "6.8471e+20")
    _write_identity_csv(
        clean_root,
        participant_id,
        "targets",
        "684710000000000000000",
    )

    inferred_numeric = float(participant_id)
    clean_data = {
        "gaze": pd.DataFrame(
            {"participant_id": [participant_id], "trial_number": [1], "gaze_x": [0.0]}
        ),
        "participant": pd.DataFrame({"participant_id": [inferred_numeric]}),
        "targets": pd.DataFrame(
            {"participant_id": [inferred_numeric], "trial_number": [1], "target_x": [0.0]}
        ),
    }

    _canonicalize_companion_participant_identity(clean_root, participant_id, clean_data)

    for frame in clean_data.values():
        assert frame["participant_id"].tolist() == [participant_id]


def test_numeric_equivalence_is_exact_not_approximate():
    participant_id = "68471e16"

    assert _participant_identity_value_matches(participant_id, "6.8471e+20")
    assert _participant_identity_value_matches(
        participant_id,
        "684710000000000000000",
    )
    assert not _participant_identity_value_matches(participant_id, "6.847100000000001e+20")
    assert not _participant_identity_value_matches(participant_id, "nan")
    assert not _participant_identity_value_matches(participant_id, "inf")
    assert not _participant_identity_value_matches(participant_id, " 6.8471e+20")


def test_non_scientific_path_id_does_not_accept_numeric_equivalence(tmp_path: Path):
    participant_id = "00012345"
    clean_root = tmp_path / "clean"
    _write_identity_csv(clean_root, participant_id, "gaze", "12345")
    clean_data = {
        "gaze": pd.DataFrame(
            {"participant_id": [12345], "trial_number": [1], "gaze_x": [0.0]}
        )
    }

    with pytest.raises(ValueError, match="incompatible with path identity '00012345'"):
        _canonicalize_companion_participant_identity(clean_root, participant_id, clean_data)


def test_participant_identity_canonicalization_fails_on_source_mismatch(tmp_path: Path):
    participant_id = "68471e16"
    clean_root = tmp_path / "clean"
    _write_identity_csv(clean_root, participant_id, "gaze", "6.8472e+20")
    clean_data = {
        "gaze": pd.DataFrame(
            {"participant_id": [float(participant_id)], "trial_number": [1], "gaze_x": [0.0]}
        )
    }

    with pytest.raises(ValueError, match="incompatible with path identity '68471e16'"):
        _canonicalize_companion_participant_identity(clean_root, participant_id, clean_data)


def test_participant_identity_canonicalization_fails_on_companion_memory_mismatch(
    tmp_path: Path,
):
    participant_id = "68471e16"
    clean_root = tmp_path / "clean"
    _write_identity_csv(clean_root, participant_id, "gaze", "6.8471e+20")
    clean_data = {
        "gaze": pd.DataFrame(
            {"participant_id": ["different-id"], "trial_number": [1], "gaze_x": [0.0]}
        )
    }

    with pytest.raises(ValueError, match="companion clean table 'gaze'.*incompatible"):
        _canonicalize_companion_participant_identity(clean_root, participant_id, clean_data)


def test_participant_identity_canonicalization_rejects_mixed_source_values(tmp_path: Path):
    participant_id = "68471e16"
    clean_root = tmp_path / "clean"
    participant_root = clean_root / "train" / participant_id
    participant_root.mkdir(parents=True)
    (participant_root / f"{participant_id}_gaze.csv").write_text(
        "participant_id,trial_number,gaze_x\n"
        "68471e16,1,0.0\n"
        "6.8472e+20,2,0.0\n",
        encoding="utf-8",
    )
    clean_data = {
        "gaze": pd.DataFrame(
            {"participant_id": [float(participant_id)], "trial_number": [1], "gaze_x": [0.0]}
        )
    }

    with pytest.raises(ValueError, match="incompatible with path identity '68471e16'"):
        _canonicalize_companion_participant_identity(clean_root, participant_id, clean_data)


def test_participant_identity_canonicalization_requires_published_identity_column(
    tmp_path: Path,
):
    participant_id = "68471e16"
    clean_root = tmp_path / "clean"
    participant_root = clean_root / "train" / participant_id
    participant_root.mkdir(parents=True)
    (participant_root / f"{participant_id}_gaze.csv").write_text(
        "trial_number,gaze_x\n1,0.0\n",
        encoding="utf-8",
    )
    clean_data = {"gaze": pd.DataFrame({"trial_number": [1], "gaze_x": [0.0]})}

    with pytest.raises(ValueError, match="no participant_id source column"):
        _canonicalize_companion_participant_identity(clean_root, participant_id, clean_data)


def test_participant_identity_canonicalization_requires_authoritative_path_layout(
    tmp_path: Path,
):
    participant_id = "68471e16"
    clean_root = tmp_path / "clean"
    wrong_root = clean_root / "misc" / participant_id
    wrong_root.mkdir(parents=True)
    (wrong_root / f"{participant_id}_gaze.csv").write_text(
        "participant_id,trial_number,gaze_x\n6.8471e+20,1,0.0\n",
        encoding="utf-8",
    )
    clean_data = {
        "gaze": pd.DataFrame(
            {"participant_id": [float(participant_id)], "trial_number": [1], "gaze_x": [0.0]}
        )
    }

    with pytest.raises(ValueError, match="no matching published clean CSV files"):
        _canonicalize_companion_participant_identity(clean_root, participant_id, clean_data)


def test_participant_identity_canonicalization_rejects_cross_split_duplicate(tmp_path: Path):
    participant_id = "68471e16"
    clean_root = tmp_path / "clean"
    _write_identity_csv(clean_root, participant_id, "gaze", participant_id, split="train")
    _write_identity_csv(clean_root, participant_id, "gaze", participant_id, split="test")
    clean_data = {
        "gaze": pd.DataFrame(
            {"participant_id": [participant_id], "trial_number": [1], "gaze_x": [0.0]}
        )
    }

    with pytest.raises(ValueError, match="represented in multiple clean-data splits"):
        _canonicalize_companion_participant_identity(clean_root, participant_id, clean_data)
