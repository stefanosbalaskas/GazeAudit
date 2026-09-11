import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    GaussianGazeErrorModel,
    RectangleAOI,
    compare_hard_probabilistic,
    evaluate_aoi_recovery,
    fit_error_model_from_known_truth,
    hard_aoi_membership,
    pairwise_interaction_sensitivity,
    scale_error_model,
    simulate_boundary_data,
    spatial_sensitivity_curve,
    summarize_aoi_risk,
)


def _binary_aois():
    return [
        RectangleAOI("left", -100.0, -100.0, 0.0, 100.0),
        RectangleAOI("right", 0.0, -100.0, 100.0, 100.0),
    ]


def _error_model(sd=2.0):
    return GaussianGazeErrorModel(
        mean_error=np.array([0.0, 0.0]),
        covariance=np.diag([sd**2, sd**2]),
        n_validation=50,
    )


def test_hard_membership_reports_each_aoi_and_outside():
    points = np.array([[-5.0, 0.0], [5.0, 0.0], [200.0, 0.0]])
    membership = hard_aoi_membership(points, _binary_aois())

    assert list(membership.columns) == ["left", "right", "outside"]
    assert membership.loc[0, "left"]
    assert membership.loc[1, "right"]
    assert membership.loc[2, "outside"]


def test_hard_membership_validates_inputs():
    with pytest.raises(ValueError, match="at least one AOI"):
        hard_aoi_membership(np.array([[0.0, 0.0]]), [])
    with pytest.raises(ValueError, match="unique"):
        hard_aoi_membership(
            np.array([[0.0, 0.0]]),
            [
                RectangleAOI("same", -1, -1, 1, 1),
                RectangleAOI("same", -2, -2, 2, 2),
            ],
        )
    with pytest.raises(ValueError, match="shape"):
        hard_aoi_membership(np.array([1.0, 2.0]), _binary_aois())
    with pytest.raises(ValueError, match="finite"):
        hard_aoi_membership(np.array([[np.nan, 0.0]]), _binary_aois())


def test_compare_hard_probabilistic_identifies_boundary_fragility():
    points = np.array([[-20.0, 0.0], [0.2, 0.0], [20.0, 0.0]])
    comparison = compare_hard_probabilistic(
        points,
        _binary_aois(),
        _error_model(sd=2.0),
        draws=20_000,
        rng=123,
    )

    assert set(comparison.columns) == {
        "observation",
        "aoi",
        "observed_in_aoi",
        "membership_probability",
        "flip_probability",
        "boundary_risk",
    }
    near_right = comparison.query("observation == 1 and aoi == 'right'").iloc[0]
    far_right = comparison.query("observation == 2 and aoi == 'right'").iloc[0]
    assert near_right["membership_probability"] == pytest.approx(0.54, abs=0.03)
    assert near_right["boundary_risk"] > 0.85
    assert far_right["flip_probability"] < 0.01


def test_summarize_aoi_risk_reports_high_risk_fraction():
    comparison = pd.DataFrame(
        {
            "aoi": ["a", "a", "b", "b"],
            "flip_probability": [0.1, 0.4, 0.0, 0.2],
            "boundary_risk": [0.2, 0.8, 0.0, 0.4],
        }
    )
    summary = summarize_aoi_risk(comparison, high_risk_threshold=0.25)
    a = summary.loc[summary["aoi"] == "a"].iloc[0]
    assert a["mean_flip_probability"] == pytest.approx(0.25)
    assert a["max_flip_probability"] == pytest.approx(0.4)
    assert a["high_risk_fraction"] == pytest.approx(0.5)

    with pytest.raises(ValueError, match="between 0 and 1"):
        summarize_aoi_risk(comparison, high_risk_threshold=1.1)
    with pytest.raises(ValueError, match="at least one row"):
        summarize_aoi_risk(comparison.iloc[0:0])
    with pytest.raises(ValueError, match="required columns"):
        summarize_aoi_risk(pd.DataFrame({"aoi": ["a"]}))
    bad = comparison.copy()
    bad.loc[0, "flip_probability"] = "bad"
    with pytest.raises(ValueError, match="numeric and complete"):
        summarize_aoi_risk(bad)


def test_scale_error_model_scales_bias_and_standard_deviation():
    model = GaussianGazeErrorModel(
        mean_error=np.array([2.0, -4.0]),
        covariance=np.array([[4.0, 1.0], [1.0, 9.0]]),
        n_validation=10,
    )
    scaled = scale_error_model(model, sd_scale=2.0, bias_scale=0.5)
    np.testing.assert_allclose(scaled.mean_error, [1.0, -2.0])
    np.testing.assert_allclose(scaled.covariance, model.covariance * 4.0)
    assert scaled.n_validation == model.n_validation

    with pytest.raises(ValueError, match="sd_scale"):
        scale_error_model(model, sd_scale=-1)
    with pytest.raises(ValueError, match="bias_scale"):
        scale_error_model(model, bias_scale=-1)


def test_spatial_sensitivity_curve_detects_increasing_boundary_uncertainty():
    points = np.array([[-10.0, 0.0], [0.2, 0.0], [10.0, 0.0]])
    durations = np.array([100.0, 200.0, 300.0])
    curve = spatial_sensitivity_curve(
        points,
        _binary_aois(),
        _error_model(sd=1.0),
        [0.0, 1.0, 3.0],
        durations=durations,
        draws=10_000,
        rng=7,
    )

    assert len(curve) == 6
    assert "expected_dwell" in curve.columns
    right = curve.loc[curve["aoi"] == "right"].sort_values("sd_scale")
    assert right.iloc[0]["mean_flip_probability"] == pytest.approx(0.0)
    assert right.iloc[-1]["mean_flip_probability"] > right.iloc[0]["mean_flip_probability"]

    repeat = spatial_sensitivity_curve(
        points,
        _binary_aois(),
        _error_model(sd=1.0),
        [1.0],
        draws=1000,
        rng=99,
    )
    repeat2 = spatial_sensitivity_curve(
        points,
        _binary_aois(),
        _error_model(sd=1.0),
        [1.0],
        draws=1000,
        rng=99,
    )
    pd.testing.assert_frame_equal(repeat, repeat2)


def test_spatial_sensitivity_curve_validates_scales_points_and_durations():
    points = np.array([[0.0, 0.0]])
    with pytest.raises(ValueError, match="at least one value"):
        spatial_sensitivity_curve(points, _binary_aois(), _error_model(), [])
    with pytest.raises(ValueError, match="non-negative"):
        spatial_sensitivity_curve(points, _binary_aois(), _error_model(), [-1])
    with pytest.raises(ValueError, match="match points"):
        spatial_sensitivity_curve(
            points,
            _binary_aois(),
            _error_model(),
            [1],
            durations=np.array([1.0, 2.0]),
        )
    with pytest.raises(ValueError, match="finite and non-negative"):
        spatial_sensitivity_curve(
            points,
            _binary_aois(),
            _error_model(),
            [1],
            durations=np.array([-1.0]),
        )
    with pytest.raises(ValueError, match="shape"):
        spatial_sensitivity_curve(np.array([0.0, 0.0]), _binary_aois(), _error_model(), [1])
    with pytest.raises(ValueError, match="finite"):
        spatial_sensitivity_curve(
            np.array([[np.inf, 0.0]]), _binary_aois(), _error_model(), [1]
        )


def test_boundary_simulation_is_reproducible_and_error_model_recovers_parameters():
    first = simulate_boundary_data(
        n=20_000,
        measurement_sd=3.0,
        bias_x=1.5,
        bias_y=-2.0,
        rng=123,
    )
    second = simulate_boundary_data(
        n=20_000,
        measurement_sd=3.0,
        bias_x=1.5,
        bias_y=-2.0,
        rng=123,
    )
    pd.testing.assert_frame_equal(first, second)

    model = fit_error_model_from_known_truth(first)
    assert model.bias_x == pytest.approx(1.5, abs=0.08)
    assert model.bias_y == pytest.approx(-2.0, abs=0.08)
    assert np.sqrt(model.covariance[0, 0]) == pytest.approx(3.0, abs=0.08)

    with pytest.raises(ValueError, match="at least 2"):
        simulate_boundary_data(n=1)
    with pytest.raises(ValueError, match="measurement_sd"):
        simulate_boundary_data(measurement_sd=-1)


def test_aoi_recovery_benchmark_returns_bounded_metrics():
    data = simulate_boundary_data(n=3000, measurement_sd=4.0, rng=321)
    model = fit_error_model_from_known_truth(data)
    truth = data[["true_x", "true_y"]].to_numpy()
    observed = data[["observed_x", "observed_y"]].to_numpy()
    benchmark = evaluate_aoi_recovery(
        truth,
        observed,
        _binary_aois(),
        model,
        draws=3000,
        rng=777,
    )

    assert set(benchmark["aoi"]) == {"left", "right"}
    for column in [
        "hard_accuracy",
        "probabilistic_accuracy",
        "hard_brier",
        "probabilistic_brier",
    ]:
        assert benchmark[column].between(0.0, 1.0).all()
    np.testing.assert_allclose(
        benchmark["hard_brier"],
        1.0 - benchmark["hard_accuracy"],
    )

    with pytest.raises(ValueError, match="same shape"):
        evaluate_aoi_recovery(truth[:10], observed[:9], _binary_aois(), model)
    with pytest.raises(ValueError, match="at least one AOI"):
        evaluate_aoi_recovery(truth[:10], observed[:10], [], model)
    with pytest.raises(ValueError, match="shape"):
        evaluate_aoi_recovery(np.array([1.0, 2.0]), observed[:1], _binary_aois(), model)
    bad_truth = truth[:2].copy()
    bad_truth[0, 0] = np.nan
    with pytest.raises(ValueError, match="finite"):
        evaluate_aoi_recovery(bad_truth, observed[:2], _binary_aois(), model)


def test_pairwise_interaction_sensitivity_finds_pure_interaction():
    results = pd.DataFrame(
        {
            "detector-family": ["a", "a", "b", "b"],
            "qc": ["low", "high", "low", "high"],
            "estimate": [0.0, 1.0, 1.0, 0.0],
        }
    )
    interactions = pairwise_interaction_sensitivity(
        results, ["detector-family", "qc"]
    )
    assert len(interactions) == 1
    assert interactions.loc[0, "interaction_ratio"] == pytest.approx(1.0)
    assert interactions.loc[0, "max_abs_interaction"] == pytest.approx(0.5)

    empty = pairwise_interaction_sensitivity(results, ["qc"])
    assert empty.empty
    with pytest.raises(ValueError, match="not present"):
        pairwise_interaction_sensitivity(results, ["qc", "missing"])


def test_pairwise_interaction_sensitivity_zero_when_endpoint_constant():
    results = pd.DataFrame(
        {
            "a": [0, 0, 1, 1],
            "b": [0, 1, 0, 1],
            "estimate": [2.0, 2.0, 2.0, 2.0],
        }
    )
    interactions = pairwise_interaction_sensitivity(results, ["a", "b"])
    assert interactions.loc[0, "interaction_ratio"] == pytest.approx(0.0)
    assert interactions.loc[0, "max_abs_interaction"] == pytest.approx(0.0)
