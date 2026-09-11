import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    GaussianGazeErrorModel,
    GazeStudy,
    PipelineSpace,
    RectangleAOI,
    aoi_probabilities,
    effect_stability,
    expected_dwell,
    expected_fixation_count,
    marginal_sensitivity,
    run_specs,
)
from gazeaudit.report import render_markdown_audit
from gazeaudit.robustness import specification_curve


def _study() -> GazeStudy:
    data = pd.DataFrame(
        {
            "participant": ["p1", "p1", "p2", "p2"],
            "trial": [1, 1, 1, 1],
            "timestamp": [0.0, 10.0, 0.0, 10.0],
            "x": [10.0, 20.0, 11.0, 21.0],
            "y": [5.0, 5.0, 6.0, 6.0],
        }
    )
    return GazeStudy(data)


def test_gaze_study_validates_and_counts_units():
    study = _study()
    study.validate_time_order()
    assert study.n_participants == 2
    assert study.n_trials == 2


def test_error_model_recovers_known_bias():
    validation = pd.DataFrame(
        {
            "observed_x": [11.0, 21.0, 31.0, 41.0],
            "observed_y": [8.0, 18.0, 28.0, 38.0],
            "target_x": [10.0, 20.0, 30.0, 40.0],
            "target_y": [10.0, 20.0, 30.0, 40.0],
        }
    )
    model = GaussianGazeErrorModel.fit(validation)
    assert model.bias_x == pytest.approx(1.0)
    assert model.bias_y == pytest.approx(-2.0)
    corrected = model.corrected_points(np.array([[51.0, 48.0]]))
    np.testing.assert_allclose(corrected, [[50.0, 50.0]])


def test_probabilistic_aoi_assignment_is_reproducible_and_bounded():
    model = GaussianGazeErrorModel(
        mean_error=np.array([0.0, 0.0]),
        covariance=np.array([[4.0, 0.0], [0.0, 4.0]]),
        n_validation=20,
    )
    left = RectangleAOI("left", -100.0, -100.0, 0.0, 100.0)
    right = RectangleAOI("right", 0.0, -100.0, 100.0, 100.0)
    points = np.array([[0.0, 0.0]])

    first = aoi_probabilities(points, [left, right], model, draws=20_000, rng=42)
    second = aoi_probabilities(points, [left, right], model, draws=20_000, rng=42)

    pd.testing.assert_frame_equal(first, second)
    assert first.loc[0, "left"] == pytest.approx(0.5, abs=0.02)
    assert first.loc[0, "right"] == pytest.approx(0.5, abs=0.02)
    assert first.loc[0, "outside"] == pytest.approx(0.0, abs=0.001)


def test_expected_endpoints_weight_membership_probability():
    probabilities = pd.DataFrame({"target": [1.0, 0.5, 0.0]})
    durations = np.array([100.0, 200.0, 300.0])
    assert expected_dwell(probabilities, durations, "target") == pytest.approx(200.0)
    assert expected_fixation_count(probabilities, "target") == pytest.approx(1.5)


def test_pipeline_space_enumerates_and_runs_all_defensible_specs():
    space = PipelineSpace()
    space.add_choice("detector", ["ivt", "idt"])
    space.add_choice("qc", [0.10, 0.20])

    results = run_specs(
        _study(),
        space,
        endpoint=lambda _study_object, spec: (1.0 if spec["detector"] == "ivt" else 2.0)
        + spec["qc"],
    )

    assert space.size == 4
    assert len(results) == 4
    assert set(results.columns) == {"spec_id", "detector", "qc", "estimate"}


def test_robustness_summaries_identify_stable_direction_and_factor_sensitivity():
    results = pd.DataFrame(
        {
            "detector": ["a", "a", "b", "b"],
            "qc": [0.1, 0.2, 0.1, 0.2],
            "estimate": [1.0, 1.1, 2.0, 2.1],
        }
    )
    stability = effect_stability(results)
    sensitivity = marginal_sensitivity(results, ["detector", "qc"])
    curve = specification_curve(results)

    assert stability["positive_fraction"] == pytest.approx(1.0)
    assert stability["sign_stability"] == pytest.approx(1.0)
    assert sensitivity.iloc[0]["factor"] == "detector"
    assert list(curve["estimate"]) == sorted(results["estimate"])


def test_markdown_report_contains_guardrail_and_factor_diagnostics():
    results = pd.DataFrame(
        {
            "detector": ["a", "a", "b", "b"],
            "estimate": [0.2, 0.3, 0.4, 0.5],
        }
    )
    report = render_markdown_audit(results, factors=["detector"])
    assert "GazeAudit robustness report" in report
    assert "Marginal specification sensitivity" in report
    assert "does not automate substantive interpretation" in report
