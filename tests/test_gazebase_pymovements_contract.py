from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from gazeaudit import prepare_gazebase_pymovements_dataset


class _Recording:
    def __init__(self, samples):
        self.samples = samples
        self.trial_columns = []


class _Dataset:
    def __init__(self, recordings, gaze_fileinfo):
        self.gaze = recordings
        self.fileinfo = {"gaze": gaze_fileinfo}
        self.deg2pix_calls = 0

    def deg2pix(self, **kwargs):
        self.deg2pix_calls += 1
        for recording in self.gaze:
            if "pixel" not in recording.samples:
                recording.samples["pixel"] = recording.samples["position"].copy()
        return self


def _native_contract_dataset(*, include_pixel=True):
    recordings = []
    rows = []
    for participant in (1, 2):
        for task in ("FXS", "TEX"):
            positions = [np.array([float(index), float(participant)]) for index in range(6)]
            data = {
                "time": np.arange(6, dtype=float) * 10.0,
                "position": positions,
                "lab": [1, 1, 1, 1, 2, -1] if task == "TEX" else [1] * 6,
            }
            if include_pixel:
                data["pixel"] = positions
            recordings.append(_Recording(pd.DataFrame(data)))
            rows.append(
                {
                    "round_id": 1,
                    "subject_id": participant,
                    "session_id": 1,
                    "task_name": task,
                    "filepath": f"R1/S1/S_1{participant}_S1_{task}.csv",
                }
            )
    return _Dataset(recordings, pd.DataFrame(rows))


def _materialize_selected_files(dataset, root):
    dataset.paths = SimpleNamespace(raw=root)
    for relative in dataset.fileinfo["gaze"]["filepath"]:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"synthetic source for {relative}\n", encoding="utf-8")


def test_public_preparer_accepts_native_pymovements_fileinfo_mapping():
    dataset = _native_contract_dataset()

    prepared = prepare_gazebase_pymovements_dataset(dataset)

    assert dataset.deg2pix_calls == 0
    assert prepared.study.n_participants == 2
    assert set(prepared.study.data["trial"]) == {"FXS", "TEX"}
    assert prepared.source_identity["selected_file_count"] == 4
    assert prepared.source_identity["selected_files_fingerprint"]


def test_native_fileinfo_bridge_preserves_live_deg2pix_conversion():
    dataset = _native_contract_dataset(include_pixel=False)

    prepared = prepare_gazebase_pymovements_dataset(dataset)

    assert dataset.deg2pix_calls == 1
    assert prepared.study.data[["x", "y"]].notna().all().all()


def test_content_bound_preparation_hashes_every_selected_source_file(tmp_path):
    dataset = _native_contract_dataset()
    _materialize_selected_files(dataset, tmp_path)

    first = prepare_gazebase_pymovements_dataset(dataset, require_content_hash=True)
    first_identity = first.source_identity

    assert first_identity["selected_file_content_hash_algorithm"] == "sha256"
    assert first_identity["selected_file_content_count"] == 4
    assert first_identity["selected_file_content_bytes"] > 0
    assert len(first_identity["selected_file_content_fingerprint"]) == 64

    changed = tmp_path / dataset.fileinfo["gaze"].iloc[0]["filepath"]
    changed.write_text("scientifically different source bytes\n", encoding="utf-8")
    second = prepare_gazebase_pymovements_dataset(dataset, require_content_hash=True)

    assert (
        second.source_identity["selected_file_content_fingerprint"]
        != first_identity["selected_file_content_fingerprint"]
    )


def test_content_bound_preparation_rejects_relative_path_escape(tmp_path):
    dataset = _native_contract_dataset()
    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    outside = tmp_path / "outside.csv"
    outside.write_text("outside the frozen dataset root\n", encoding="utf-8")
    dataset.paths = SimpleNamespace(raw=raw_root)
    dataset.fileinfo["gaze"].loc[0, "filepath"] = "../outside.csv"

    with pytest.raises(ValueError, match="escapes dataset.paths.raw"):
        prepare_gazebase_pymovements_dataset(dataset, require_content_hash=True)


def test_content_bound_preparation_rejects_symlink_escape(tmp_path):
    dataset = _native_contract_dataset()
    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    outside = tmp_path / "outside.csv"
    outside.write_text("outside the frozen dataset root\n", encoding="utf-8")
    link = raw_root / "escaped.csv"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation is unavailable on this platform")
    dataset.paths = SimpleNamespace(raw=raw_root)
    dataset.fileinfo["gaze"].loc[0, "filepath"] = "escaped.csv"

    with pytest.raises(ValueError, match="escapes dataset.paths.raw"):
        prepare_gazebase_pymovements_dataset(dataset, require_content_hash=True)


def test_content_bound_preparation_fails_without_raw_source_root():
    dataset = _native_contract_dataset()

    with pytest.raises(ValueError, match="dataset.paths.raw"):
        prepare_gazebase_pymovements_dataset(dataset, require_content_hash=True)


def test_native_fileinfo_mapping_without_gaze_table_fails_closed():
    dataset = _native_contract_dataset()
    dataset.fileinfo = {"participants": pd.DataFrame({"participant_id": [1, 2]})}

    with pytest.raises(ValueError, match="missing the 'gaze' table"):
        prepare_gazebase_pymovements_dataset(dataset)
