import json

import numpy as np
import pandas as pd
import pytest

from gazeaudit.bids_adapter import (
    BIDSEyeTrackingAdapter,
    parse_bids_entities,
    read_bids_eyetrack,
    read_bids_eyetrack_many,
)


def _metadata(**overrides):
    metadata = {
        "SamplingFrequency": 1000.0,
        "StartTime": -0.25,
        "Columns": ["timestamp", "x_coordinate", "y_coordinate", "pupil_size"],
        "PhysioType": "eyetrack",
        "RecordedEye": "right",
        "SampleCoordinateSystem": "gaze-on-screen",
        "timestamp": {"Units": "ms", "Origin": "System startup"},
        "x_coordinate": {"Units": "pixel"},
        "y_coordinate": {"Units": "pixel"},
        "pupil_size": {"Units": "arbitrary"},
    }
    metadata.update(overrides)
    return metadata


def _write_record(tmp_path, name, rows=None, metadata=None):
    if rows is None:
        rows = [
            [1000.0, 100.0, 200.0, 3.1],
            [1010.0, 101.0, 201.0, 3.2],
            [1020.0, 102.0, 202.0, 3.3],
        ]
    path = tmp_path / name
    frame = pd.DataFrame(rows)
    compression = "gzip" if name.endswith(".gz") else None
    frame.to_csv(path, sep="\t", header=False, index=False, compression=compression)
    sidecar_name = name.replace(".tsv.gz", ".json").replace(".tsv", ".json")
    sidecar = tmp_path / sidecar_name
    sidecar.write_text(json.dumps(metadata or _metadata()), encoding="utf-8")
    return path, sidecar


def test_read_bids_eyetrack_maps_required_columns_and_metadata(tmp_path):
    path, _ = _write_record(
        tmp_path,
        "sub-01_task-demo_run-1_recording-eye1_physio.tsv.gz",
    )
    record = read_bids_eyetrack(path)

    np.testing.assert_allclose(record.study.data["x"], [100.0, 101.0, 102.0])
    np.testing.assert_allclose(record.study.data["y"], [200.0, 201.0, 202.0])
    np.testing.assert_allclose(record.study.data["timestamp"], [1000.0, 1010.0, 1020.0])
    assert set(record.study.data["participant"]) == {"sub-01"}
    assert set(record.study.data["trial"]) == {"task-demo|run-1|recording-eye1"}
    assert list(record.study.data["pupil_size"]) == [3.1, 3.2, 3.3]
    assert set(record.study.data["recorded_eye"]) == {"right"}
    assert set(record.study.data["bids_recording"]) == {"eye1"}
    assert record.coordinate_unit == "pixel"
    assert record.timestamp_unit == "ms"
    assert record.entities["sub"] == "01"
    assert record.entities["recording"] == "eye1"


def test_read_bids_eyetrack_converts_seconds_to_ms_and_can_drop_extra_columns(tmp_path):
    metadata = _metadata(timestamp={"Units": "s"})
    path, _ = _write_record(
        tmp_path,
        "sub-02_task-demo_recording-eye1_physio.tsv",
        rows=[[1.0, 5.0, 6.0, 2.0], [1.01, 7.0, 8.0, 2.1]],
        metadata=metadata,
    )
    record = read_bids_eyetrack(path, preserve_columns=False)
    np.testing.assert_allclose(record.study.data["timestamp"], [1000.0, 1010.0])
    assert list(record.study.data.columns) == [
        "x",
        "y",
        "timestamp",
        "participant",
        "trial",
    ]


def test_bids_adapter_and_explicit_identifiers(tmp_path):
    path, sidecar = _write_record(
        tmp_path,
        "sub-01_task-demo_recording-eye1_physio.tsv.gz",
    )
    adapter = BIDSEyeTrackingAdapter(
        sidecar_path=sidecar,
        participant_id="custom-participant",
        trial_id="custom-trial",
    )
    study = adapter.to_study(path)
    assert set(study.data["participant"]) == {"custom-participant"}
    assert set(study.data["trial"]) == {"custom-trial"}


def test_read_bids_many_keeps_eye_recordings_as_distinct_streams(tmp_path):
    right_path, _ = _write_record(
        tmp_path,
        "sub-01_task-demo_recording-eye1_physio.tsv.gz",
        metadata=_metadata(RecordedEye="right"),
    )
    left_path, _ = _write_record(
        tmp_path,
        "sub-01_task-demo_recording-eye2_physio.tsv.gz",
        metadata=_metadata(RecordedEye="left"),
    )

    study, records = read_bids_eyetrack_many([right_path, left_path])
    assert len(records) == 2
    assert len(study.data) == 6
    assert study.n_participants == 1
    assert study.n_trials == 2
    assert set(study.data["recorded_eye"]) == {"left", "right"}
    assert set(study.data["trial"]) == {
        "task-demo|recording-eye1",
        "task-demo|recording-eye2",
    }


def test_parse_bids_entities_reads_only_key_value_tokens():
    entities = parse_bids_entities(
        "sub-09_ses-2_task-search_run-03_recording-eye2_physio.tsv.gz"
    )
    assert entities == {
        "sub": "09",
        "ses": "2",
        "task": "search",
        "run": "03",
        "recording": "eye2",
    }


def test_bids_reader_requires_recording_entity(tmp_path):
    path, _ = _write_record(tmp_path, "sub-01_task-demo_physio.tsv.gz")
    with pytest.raises(ValueError, match="recording-<label>"):
        read_bids_eyetrack(path)


def test_bids_reader_validates_sidecar_and_column_order(tmp_path):
    wrong_type = _metadata(PhysioType="cardiac")
    path, _ = _write_record(
        tmp_path,
        "sub-01_task-demo_recording-eye1_physio.tsv.gz",
        metadata=wrong_type,
    )
    with pytest.raises(ValueError, match="PhysioType"):
        read_bids_eyetrack(path)

    missing_field = _metadata()
    del missing_field["RecordedEye"]
    path2, _ = _write_record(
        tmp_path,
        "sub-02_task-demo_recording-eye1_physio.tsv.gz",
        metadata=missing_field,
    )
    with pytest.raises(ValueError, match="missing required fields"):
        read_bids_eyetrack(path2)

    wrong_order = _metadata(
        Columns=["x_coordinate", "timestamp", "y_coordinate", "pupil_size"]
    )
    path3, _ = _write_record(
        tmp_path,
        "sub-03_task-demo_recording-eye1_physio.tsv.gz",
        metadata=wrong_order,
    )
    with pytest.raises(ValueError, match="first columns"):
        read_bids_eyetrack(path3)


def test_bids_reader_validates_units_and_data_shape(tmp_path):
    missing_timestamp_units = _metadata(timestamp={"Origin": "device"})
    path, _ = _write_record(
        tmp_path,
        "sub-01_task-demo_recording-eye1_physio.tsv.gz",
        metadata=missing_timestamp_units,
    )
    with pytest.raises(ValueError, match="timestamp.*Units"):
        read_bids_eyetrack(path)

    mismatch = _metadata(y_coordinate={"Units": "degree"})
    path2, _ = _write_record(
        tmp_path,
        "sub-02_task-demo_recording-eye1_physio.tsv.gz",
        metadata=mismatch,
    )
    with pytest.raises(ValueError, match="same units"):
        read_bids_eyetrack(path2)

    unsupported = _metadata(timestamp={"Units": "ticks"})
    path3, _ = _write_record(
        tmp_path,
        "sub-03_task-demo_recording-eye1_physio.tsv.gz",
        metadata=unsupported,
    )
    with pytest.raises(ValueError, match="unsupported.*timestamp unit"):
        read_bids_eyetrack(path3)

    short_rows = [[1000.0, 10.0, 20.0], [1010.0, 11.0, 21.0]]
    path4, _ = _write_record(
        tmp_path,
        "sub-04_task-demo_recording-eye1_physio.tsv.gz",
        rows=short_rows,
        metadata=_metadata(),
    )
    with pytest.raises(ValueError, match="sidecar declares"):
        read_bids_eyetrack(path4)


def test_bids_reader_rejects_nonfinite_timestamps_and_bad_paths(tmp_path):
    path, _ = _write_record(
        tmp_path,
        "sub-01_task-demo_recording-eye1_physio.tsv.gz",
        rows=[["n/a", 10.0, 20.0, 2.0]],
    )
    with pytest.raises(ValueError, match="timestamps must be finite"):
        read_bids_eyetrack(path)

    missing = tmp_path / "sub-99_task-demo_recording-eye1_physio.tsv.gz"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        read_bids_eyetrack(missing)

    bad_name = tmp_path / "sub-01_task-demo_recording-eye1_gaze.tsv"
    bad_name.write_text("1\t2\t3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="physio_path"):
        read_bids_eyetrack(bad_name)


def test_bids_many_validates_sequence_lengths(tmp_path):
    path, _ = _write_record(
        tmp_path,
        "sub-01_task-demo_recording-eye1_physio.tsv.gz",
    )
    with pytest.raises(ValueError, match="at least one file"):
        read_bids_eyetrack_many([])
    with pytest.raises(ValueError, match="participant_ids"):
        read_bids_eyetrack_many([path], participant_ids=["p1", "p2"])
    with pytest.raises(ValueError, match="trial_ids"):
        read_bids_eyetrack_many([path], trial_ids=[1, 2])
