"""Live-contract tests for optional upstream interoperability dependencies."""

import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    GAZEBASE_DETECTORS,
    GazeStudy,
    from_pymovements_gaze,
    make_peyes_detector,
    run_peyes_detector,
    verify_gazebase_software_versions,
)


def test_live_pymovements_028_contract():
    pm = pytest.importorskip("pymovements")
    samples = np.array(
        [
            [0.0, 100.0, 200.0],
            [10.0, 101.0, 201.0],
            [20.0, 102.0, 202.0],
        ]
    )
    gaze = pm.gaze.from_numpy(
        samples=samples,
        schema=["t", "x", "y"],
        time_column="t",
        time_unit="ms",
        pixel_columns=["x", "y"],
        orient="row",
    )

    study = from_pymovements_gaze(gaze, participant_id="p-live")
    assert isinstance(study, GazeStudy)
    np.testing.assert_allclose(study.data["timestamp"], [0.0, 10.0, 20.0])
    np.testing.assert_allclose(study.data["x"], [100.0, 101.0, 102.0])
    np.testing.assert_allclose(study.data["y"], [200.0, 201.0, 202.0])


def test_live_peyes_02_detector_contract():
    peyes = pytest.importorskip("peyes")
    assert tuple(int(part) for part in peyes.__version__.split(".")[:2]) >= (0, 2)

    n = 30
    study = GazeStudy(
        pd.DataFrame(
            {
                "x": np.linspace(500.0, 502.0, n),
                "y": np.linspace(400.0, 402.0, n),
                "timestamp": np.arange(n, dtype=float) * 10.0,
                "participant": ["p-live"] * n,
                "trial": np.ones(n, dtype=int),
            }
        )
    )
    detector = make_peyes_detector(
        "ivt",
        min_event_duration=20.0,
        pad_blinks_time=0.0,
        saccade_velocity_threshold=30.0,
    )
    result = run_peyes_detector(
        study,
        detector,
        viewer_distance_cm=60.0,
        pixel_size_cm=0.03,
    )

    assert len(result.samples) == n
    assert result.samples["event_label"].notna().all()
    assert len(result.metadata) == 1
    assert result.metadata.loc[0, "algorithm"] == "ivt"


def test_live_gazebase_frozen_detector_contract():
    pytest.importorskip("pymovements")
    pytest.importorskip("peyes")

    versions = verify_gazebase_software_versions()
    assert versions["pymovements"] == "0.28.0"
    assert versions["peyes"] == "0.2.2"

    resolved = {}
    for algorithm in GAZEBASE_DETECTORS:
        detector = make_peyes_detector(
            algorithm,
            missing_value=np.nan,
            min_event_duration=40.0,
            pad_blinks_time=0.0,
            name=algorithm,
        )
        defaults = detector.get_default_params()
        assert isinstance(defaults, dict)
        resolved[algorithm] = defaults

    assert tuple(resolved) == GAZEBASE_DETECTORS
    assert all(isinstance(parameters, dict) for parameters in resolved.values())
