from enum import IntEnum

import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    DetectionResult,
    GazeStudy,
    PeyesDetectorAdapter,
    PymovementsGazeAdapter,
    adapt_study,
    from_pymovements_dataset,
    from_pymovements_gaze,
    run_detector_backend,
    run_peyes_detector,
)


class _Samples:
    def __init__(self, frame):
        self._frame = frame

    def to_pandas(self):
        return self._frame.copy()


class _Gaze:
    def __init__(self, frame, trial_columns=None):
        self.samples = _Samples(frame)
        self.trial_columns = trial_columns


class _Dataset:
    def __init__(self, gaze):
        self.gaze = gaze


class _Label(IntEnum):
    UNDEFINED = 0
    FIXATION = 1
    SACCADE = 2


class _Detector:
    name = "fake-detector"
    algorithm_name = "fake"

    def __init__(self):
        self.calls = []

    def detect(self, t, x, y, viewer_distance_cm, pixel_size_cm):
        self.calls.append(
            {
                "t": np.asarray(t).copy(),
                "x": np.asarray(x).copy(),
                "y": np.asarray(y).copy(),
                "viewer_distance_cm": viewer_distance_cm,
                "pixel_size_cm": pixel_size_cm,
            }
        )
        labels = [_Label.FIXATION if index % 2 == 0 else _Label.SACCADE for index in range(len(t))]
        return labels, {"sampling_rate": 100.0}


def _study():
    return GazeStudy(
        pd.DataFrame(
            {
                "participant": ["p1", "p1", "p2", "p2"],
                "trial": [1, 1, 1, 1],
                "timestamp": [0.0, 10.0, 0.0, 10.0],
                "x": [100.0, 101.0, 200.0, 201.0],
                "y": [50.0, 51.0, 60.0, 61.0],
            }
        )
    )


def test_user_study_adapter_protocol_is_enforced():
    class Adapter:
        name = "demo"

        def to_study(self, source):
            return source

    study = _study()
    assert adapt_study(study, Adapter()) is study

    class BadAdapter:
        name = "bad"

    with pytest.raises(TypeError, match="StudyAdapter"):
        adapt_study(study, BadAdapter())


def test_user_detector_backend_protocol_is_enforced():
    class Backend:
        name = "demo"

        def detect(self, study):
            samples = study.data.copy()
            samples["event_label"] = "fixation"
            return DetectionResult(
                samples=samples,
                metadata=pd.DataFrame([{"backend": "demo"}]),
                backend="demo",
                detector="constant",
            )

    result = run_detector_backend(_study(), Backend())
    assert result.backend == "demo"
    assert set(result.samples["event_label"]) == {"fixation"}

    class BadBackend:
        name = "bad"

    with pytest.raises(TypeError, match="DetectorBackend"):
        run_detector_backend(_study(), BadBackend())


def test_detection_result_validates_normalized_contract():
    with pytest.raises(ValueError, match="event_label"):
        DetectionResult(
            samples=pd.DataFrame({"x": [1.0]}),
            metadata=pd.DataFrame(),
            backend="x",
            detector="y",
        )
    with pytest.raises(ValueError, match="at least one row"):
        DetectionResult(
            samples=pd.DataFrame({"event_label": []}),
            metadata=pd.DataFrame(),
            backend="x",
            detector="y",
        )


def test_pymovements_gaze_adapter_converts_duration_and_nested_pixel_coordinates():
    frame = pd.DataFrame(
        {
            "time": pd.to_timedelta([0, 10, 20], unit="ms"),
            "pixel": [[100.0, 50.0], [101.0, 51.0], [102.0, 52.0]],
            "condition": ["a", "a", "b"],
            "trial_id": [1, 1, 2],
        }
    )
    gaze = _Gaze(frame, trial_columns=["condition", "trial_id"])
    study = from_pymovements_gaze(gaze, participant_id="p1")

    np.testing.assert_allclose(study.data["x"], [100.0, 101.0, 102.0])
    np.testing.assert_allclose(study.data["y"], [50.0, 51.0, 52.0])
    np.testing.assert_allclose(study.data["timestamp"], [0.0, 10.0, 20.0])
    assert list(study.data["participant"]) == ["p1", "p1", "p1"]
    assert list(study.data["trial"]) == [("a", 1), ("a", 1), ("b", 2)]


def test_pymovements_adapter_requires_explicit_eye_for_binocular_vectors():
    frame = pd.DataFrame(
        {
            "time": [0.0, 10.0],
            "pixel": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]],
        }
    )
    gaze = _Gaze(frame)
    with pytest.raises(ValueError, match="select 'left', 'right', or 'cyclopian'"):
        from_pymovements_gaze(gaze)

    right = from_pymovements_gaze(gaze, component="right")
    np.testing.assert_allclose(right.data["x"], [3.0, 7.0])
    np.testing.assert_allclose(right.data["y"], [4.0, 8.0])


def test_pymovements_adapter_supports_participant_column_and_numeric_seconds():
    frame = pd.DataFrame(
        {
            "time": [0.0, 0.01, 0.02],
            "pixel": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
            "subject": ["p9", "p9", "p9"],
            "trial": [2, 2, 2],
        }
    )
    gaze = _Gaze(frame, trial_columns="trial")
    adapter = PymovementsGazeAdapter(
        participant_column="subject",
        numeric_time_unit="s",
    )
    study = adapter.to_study(gaze)
    np.testing.assert_allclose(study.data["timestamp"], [0.0, 10.0, 20.0])
    assert set(study.data["participant"]) == {"p9"}
    assert set(study.data["trial"]) == {2}


def test_pymovements_dataset_adapter_combines_loaded_recordings():
    first = _Gaze(
        pd.DataFrame(
            {
                "time": [0.0, 10.0],
                "pixel": [[1.0, 2.0], [2.0, 3.0]],
            }
        )
    )
    second = _Gaze(
        pd.DataFrame(
            {
                "time": [0.0, 10.0],
                "pixel": [[4.0, 5.0], [5.0, 6.0]],
            }
        )
    )
    study = from_pymovements_dataset(_Dataset([first, second]), participant_ids=["p1", "p2"])
    assert study.n_participants == 2
    assert list(study.data["participant"]) == ["p1", "p1", "p2", "p2"]

    generated = from_pymovements_dataset(_Dataset([first, second]))
    assert set(generated.data["participant"]) == {"recording_1", "recording_2"}


def test_pymovements_adapter_fails_closed_on_schema_ambiguity():
    with pytest.raises(TypeError, match="samples"):
        from_pymovements_gaze(object())

    missing_coordinate = _Gaze(pd.DataFrame({"time": [0.0]}))
    with pytest.raises(ValueError, match="coordinate column"):
        from_pymovements_gaze(missing_coordinate)

    inconsistent = _Gaze(
        pd.DataFrame(
            {
                "time": [0.0, 1.0],
                "pixel": [[1.0, 2.0], [1.0, 2.0, 3.0, 4.0]],
            }
        )
    )
    with pytest.raises(ValueError, match="inconsistent"):
        from_pymovements_gaze(inconsistent)

    bad_trial = _Gaze(
        pd.DataFrame({"time": [0.0], "pixel": [[1.0, 2.0]]}),
        trial_columns=["missing"],
    )
    with pytest.raises(ValueError, match="trial columns"):
        from_pymovements_gaze(bad_trial)

    bad_time = _Gaze(pd.DataFrame({"time": [0.0], "pixel": [[1.0, 2.0]]}))
    with pytest.raises(ValueError, match="numeric_time_unit"):
        from_pymovements_gaze(bad_time, numeric_time_unit="ticks")


def test_peyes_adapter_runs_groupwise_and_preserves_detector_metadata():
    detector = _Detector()
    result = run_peyes_detector(
        _study(),
        detector,
        viewer_distance_cm=60.0,
        pixel_size_cm=0.03,
    )

    assert result.backend == "peyes"
    assert result.detector == "fake-detector"
    assert list(result.samples["event_label"]) == [
        "fixation",
        "saccade",
        "fixation",
        "saccade",
    ]
    assert list(result.samples["event_code"]) == [1, 2, 1, 2]
    assert len(result.metadata) == 2
    assert set(result.metadata["algorithm"]) == {"fake"}
    assert result.metadata.iloc[0]["metadata"]["sampling_rate"] == 100.0
    assert len(detector.calls) == 2


def test_peyes_adapter_converts_seconds_to_milliseconds():
    detector = _Detector()
    data = _study().data.copy()
    data["timestamp"] = data["timestamp"] / 1000.0
    adapter = PeyesDetectorAdapter(
        detector=detector,
        viewer_distance_cm=60.0,
        pixel_size_cm=0.03,
        timestamp_unit="s",
    )
    adapter.detect(GazeStudy(data))
    np.testing.assert_allclose(detector.calls[0]["t"], [0.0, 10.0])


def test_peyes_adapter_validation_and_length_guardrails():
    detector = _Detector()
    with pytest.raises(ValueError, match="pixel coordinates"):
        PeyesDetectorAdapter(
            detector=detector,
            viewer_distance_cm=60.0,
            pixel_size_cm=0.03,
            coordinate_unit="dva",
        )
    with pytest.raises(ValueError, match="timestamp_unit"):
        PeyesDetectorAdapter(
            detector=detector,
            viewer_distance_cm=60.0,
            pixel_size_cm=0.03,
            timestamp_unit="ticks",
        )

    bad_time = _study().data.copy()
    bad_time.loc[1, "timestamp"] = 0.0
    with pytest.raises(ValueError, match="strictly increasing"):
        run_peyes_detector(
            GazeStudy(bad_time),
            detector,
            viewer_distance_cm=60.0,
            pixel_size_cm=0.03,
        )

    class WrongLengthDetector(_Detector):
        def detect(self, t, x, y, viewer_distance_cm, pixel_size_cm):
            return [_Label.FIXATION], {}

    with pytest.raises(ValueError, match="length does not match"):
        run_peyes_detector(
            _study(),
            WrongLengthDetector(),
            viewer_distance_cm=60.0,
            pixel_size_cm=0.03,
        )
