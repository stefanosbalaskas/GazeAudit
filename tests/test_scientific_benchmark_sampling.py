import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    GazeStudy,
    RectangleAOI,
    benchmark_known_aoi_effect,
    condition_dwell_effect,
    downsample_gaze,
    fit_error_model_from_known_truth,
    sampling_sensitivity_curve,
    simulate_known_aoi_effect,
)


def _sampled_study() -> GazeStudy:
    data = pd.DataFrame(
        {
            "participant": ["p1"] * 10,
            "trial": [1] * 10,
            "timestamp": np.arange(0.0, 100.0, 10.0),
            "x": np.arange(10, dtype=float),
            "y": np.zeros(10),
        }
    )
    return GazeStudy(data)


def test_known_effect_simulation_is_reproducible_and_balanced():
    first = simulate_known_aoi_effect(
        n_participants=8,
        trials_per_condition=5,
        control_probability=0.2,
        treatment_probability=0.8,
        rng=42,
    )
    second = simulate_known_aoi_effect(
        n_participants=8,
        trials_per_condition=5,
        control_probability=0.2,
        treatment_probability=0.8,
        rng=42,
    )
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 8 * 5 * 2
    counts = first.groupby(["participant", "condition"]).size()
    assert (counts == 5).all()


def test_condition_dwell_effect_recovers_simple_within_participant_difference():
    data = pd.DataFrame(
        {
            "participant": ["p1", "p1", "p2", "p2"],
            "condition": ["control", "treatment", "control", "treatment"],
            "duration": [100.0, 100.0, 200.0, 200.0],
        }
    )
    membership = np.array([0.0, 1.0, 0.5, 1.0])
    effect = condition_dwell_effect(data, membership)
    assert effect == pytest.approx(100.0)


def test_known_effect_benchmark_compares_scientific_endpoint_against_truth():
    data = simulate_known_aoi_effect(
        n_participants=100,
        trials_per_condition=30,
        control_probability=0.25,
        treatment_probability=0.75,
        measurement_sd=10.0,
        rng=123,
    )
    model = fit_error_model_from_known_truth(data)
    right = RectangleAOI("right", 0.0, -100.0, 100.0, 100.0)
    result = benchmark_known_aoi_effect(data, right, model, draws=3000, rng=99)

    assert result["true_effect"] > 0
    assert np.isfinite(result["hard_effect"])
    assert np.isfinite(result["probabilistic_effect"])
    assert result["hard_absolute_error"] >= 0
    assert result["probabilistic_absolute_error"] >= 0
    assert bool(result["hard_sign_recovered"])
    assert bool(result["probabilistic_sign_recovered"])


def test_known_effect_input_validation():
    with pytest.raises(ValueError, match="n_participants"):
        simulate_known_aoi_effect(n_participants=1)
    with pytest.raises(ValueError, match="trials_per_condition"):
        simulate_known_aoi_effect(trials_per_condition=0)
    with pytest.raises(ValueError, match="control_probability"):
        simulate_known_aoi_effect(control_probability=1.1)
    with pytest.raises(ValueError, match="center_sd"):
        simulate_known_aoi_effect(center_sd=-1)
    with pytest.raises(ValueError, match="duration_mean"):
        simulate_known_aoi_effect(duration_mean=-1)

    data = pd.DataFrame(
        {
            "participant": ["p1", "p1"],
            "condition": ["control", "treatment"],
            "duration": [100.0, 100.0],
        }
    )
    with pytest.raises(ValueError, match="match data rows"):
        condition_dwell_effect(data, np.array([1.0]))
    with pytest.raises(ValueError, match="between 0 and 1"):
        condition_dwell_effect(data, np.array([0.0, 1.5]))
    bad_duration = data.copy()
    bad_duration.loc[0, "duration"] = -1.0
    with pytest.raises(ValueError, match="durations"):
        condition_dwell_effect(bad_duration, np.ones(2))
    with pytest.raises(ValueError, match="both control and treatment"):
        condition_dwell_effect(
            data.loc[data["condition"] == "control"],
            np.ones(1),
        )


def test_downsample_gaze_retains_nearest_samples_on_regular_grid():
    study = _sampled_study()
    down50 = downsample_gaze(study, 50.0)
    down100 = downsample_gaze(study, 100.0)

    assert len(down50.data) == 5
    assert list(down50.data["timestamp"]) == [0.0, 20.0, 40.0, 60.0, 80.0]
    assert len(down100.data) == 10
    assert study.data.equals(_sampled_study().data)


def test_downsample_supports_seconds_and_single_sample_trials():
    data = pd.DataFrame(
        {
            "participant": ["p1", "p1", "p1", "p2"],
            "trial": [1, 1, 1, 1],
            "timestamp": [0.0, 0.01, 0.02, 0.0],
            "x": [0.0, 1.0, 2.0, 3.0],
            "y": [0.0, 0.0, 0.0, 0.0],
        }
    )
    down = downsample_gaze(GazeStudy(data), 50.0, timestamp_unit="s")
    assert len(down.data) == 3
    assert "p2" in set(down.data["participant"])


def test_sampling_sensitivity_curve_reports_retention_and_endpoint():
    study = _sampled_study()
    curve = sampling_sensitivity_curve(
        study,
        [100.0, 50.0],
        endpoint=lambda s: float(s.data["x"].mean()),
    )
    assert list(curve["target_hz"]) == [100.0, 50.0]
    assert list(curve["n_rows"]) == [10, 5]
    assert curve.loc[0, "retained_fraction"] == pytest.approx(1.0)
    assert curve.loc[1, "retained_fraction"] == pytest.approx(0.5)
    assert np.isfinite(curve["estimate"]).all()


def test_sampling_input_validation():
    study = _sampled_study()
    with pytest.raises(ValueError, match="positive"):
        downsample_gaze(study, 0)
    with pytest.raises(ValueError, match="timestamp_unit"):
        downsample_gaze(study, 60, timestamp_unit="ticks")
    with pytest.raises(ValueError, match="at least one value"):
        sampling_sensitivity_curve(study, [], lambda _s: 1.0)
    with pytest.raises(ValueError, match="finite scalar"):
        sampling_sensitivity_curve(study, [60], lambda _s: np.inf)

    bad = study.data.copy()
    bad.loc[0, "timestamp"] = np.nan
    with pytest.raises(ValueError, match="finite"):
        downsample_gaze(GazeStudy(bad), 60)

    descending = study.data.copy()
    descending.loc[2, "timestamp"] = -5.0
    with pytest.raises(ValueError, match="timestamps decrease"):
        downsample_gaze(GazeStudy(descending), 60)
