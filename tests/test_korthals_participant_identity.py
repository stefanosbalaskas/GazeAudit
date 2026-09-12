from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from gazeaudit.korthals_source import _canonicalize_companion_participant_identity


def test_scientific_notation_like_participant_id_is_restored_only_after_lexical_check(
    tmp_path: Path,
):
    participant_id = "68471e16"
    clean_root = tmp_path / "clean"
    participant_root = clean_root / "train" / participant_id
    participant_root.mkdir(parents=True)
    (participant_root / f"{participant_id}_gaze.csv").write_text(
        "participant_id,trial_number,gaze_x\n68471e16,1,0.0\n",
        encoding="utf-8",
    )
    (participant_root / f"{participant_id}_targets.csv").write_text(
        "participant_id,trial_number,target_x\n68471e16,1,0.0\n",
        encoding="utf-8",
    )

    inferred_numeric = float(participant_id)
    clean_data = {
        "gaze": pd.DataFrame(
            {"participant_id": [inferred_numeric], "trial_number": [1], "gaze_x": [0.0]}
        ),
        "targets": pd.DataFrame(
            {"participant_id": [inferred_numeric], "trial_number": [1], "target_x": [0.0]}
        ),
    }

    _canonicalize_companion_participant_identity(clean_root, participant_id, clean_data)

    assert clean_data["gaze"]["participant_id"].tolist() == [participant_id]
    assert clean_data["targets"]["participant_id"].tolist() == [participant_id]


def test_participant_identity_canonicalization_fails_on_lexical_source_mismatch(
    tmp_path: Path,
):
    participant_id = "68471e16"
    clean_root = tmp_path / "clean"
    participant_root = clean_root / "train" / participant_id
    participant_root.mkdir(parents=True)
    (participant_root / f"{participant_id}_gaze.csv").write_text(
        "participant_id,trial_number,gaze_x\nwrong-id,1,0.0\n",
        encoding="utf-8",
    )
    clean_data = {
        "gaze": pd.DataFrame(
            {"participant_id": [float(participant_id)], "trial_number": [1], "gaze_x": [0.0]}
        )
    }

    with pytest.raises(ValueError, match="expected exactly '68471e16'"):
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

    with pytest.raises(ValueError, match="no lexical participant_id source column"):
        _canonicalize_companion_participant_identity(clean_root, participant_id, clean_data)
