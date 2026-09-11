import numpy as np
import pandas as pd
import pytest

from gazeaudit.aoi import CircleAOI, RectangleAOI
from gazeaudit.aoi_propagation import audit_aoi_effect_uncertainty
from gazeaudit.scientific_benchmark import condition_dwell_effect
from gazeaudit.uncertainty import (
    GaussianGazeErrorModel,
    GroupedGaussianGazeErrorModel,
    aoi_probabilities,
)


def _effect_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "participant": ["p1", "p1", "p2", "p2"],
            "condition": ["control", "treatment", "control", "treatment"],
            "duration": [100.0, 100.0, 200.0, 200.0],
            "observed_x": [-5.0, 5.0, -5.0, 5.0],
            "observed_y": [0.0, 0.0, 0.0, 0.0],
            "validation_block": ["v1", "v1", "v1", "v1"],
        }
    )


def test_mean_radial_error_conversion_uses_explicit_rayleigh_relation():
    model = GaussianGazeErrorModel.from_mean_radial_error(
        2.0,
        n_validation=9,
        bias=(0.25, -0.5),
    )
    sigma = 2.0 / np.sqrt(np.pi / 2.0)

    np.testing.assert_allclose(model.mean_error, [0.25, -0.5])
    np.testing.assert_allclose(model.covariance, np.eye(2) * sigma**2)
    assert model.n_validation == 9

    zero = GaussianGazeErrorModel.from_mean_radial_error(0.0, n_validation=9)
    np.testing.assert_array_equal(zero.covariance, np.zeros((2, 2)))

    with pytest.raises(ValueError, match="non-negative"):
        GaussianGazeErrorModel.from_mean_radial_error(-0.1, n_validation=9)
    with pytest.raises(ValueError, match="finite"):
        GaussianGazeErrorModel.from_mean_radial_error(np.nan, n_validation=9)
    with pytest.raises(ValueError, match="bias"):
        GaussianGazeErrorModel.from_mean_radial_error(1.0, n_validation=9, bias=(0.0,))


def test_grouped_radial_constructor_supports_group_specific_validation_counts_and_biases():
    grouped = GroupedGaussianGazeErrorModel.from_mean_radial_errors(
        {"p1-v1": 0.5, "p2-v1": 1.0},
        n_validation={"p1-v1": 9, "p2-v1": 18},
        bias={"p1-v1": (0.0, 0.0), "p2-v1": (0.1, -0.2)},
    )

    assert set(grouped.models) == {"p1-v1", "p2-v1"}
    assert grouped.model_for("p1-v1").n_validation == 9
    assert grouped.model_for("p2-v1").n_validation == 18
    np.testing.assert_allclose(grouped.model_for("p2-v1").mean_error, [0.1, -0.2])

    with pytest.raises(ValueError, match="missing group"):
        GroupedGaussianGazeErrorModel.from_mean_radial_errors(
            {"a": 0.5, "b": 1.0},
            n_validation={"a": 9},
        )


def test_one_group_aoi_probabilities_are_exactly_equivalent_to_global_model():
    points = np.array([[-1.0, 0.0], [0.1, 0.0], [1.2, 0.0], [3.0, 0.0]])
    aoi = CircleAOI("target", 0.0, 0.0, 1.0)
    global_model = GaussianGazeErrorModel(
        mean_error=np.array([0.1, -0.2]),
        covariance=np.array([[1.5, 0.2], [0.2, 0.8]]),
        n_validation=20,
    )
    grouped_model = GroupedGaussianGazeErrorModel({"v1": global_model})

    global_result = aoi_probabilities(points, [aoi], global_model, draws=128, rng=912)
    grouped_result = aoi_probabilities(
        points,
        [aoi],
        grouped_model,
        groups=["v1"] * len(points),
        draws=128,
        rng=912,
    )
    pd.testing.assert_frame_equal(global_result, grouped_result)


def test_grouped_models_produce_group_specific_membership_uncertainty():
    points = np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 0.0], [2.0, 0.0]])
    aoi = CircleAOI("target", 0.0, 0.0, 1.0)
    zero = GaussianGazeErrorModel(np.zeros(2), np.zeros((2, 2)), 9)
    noisy = GaussianGazeErrorModel(np.zeros(2), np.eye(2) * 2.0, 9)
    grouped = GroupedGaussianGazeErrorModel({"zero": zero, "noisy": noisy})

    result = aoi_probabilities(
        points,
        [aoi],
        grouped,
        groups=["zero", "zero", "noisy", "noisy"],
        draws=2000,
        rng=22,
    )

    assert result.loc[0, "target"] == pytest.approx(1.0)
    assert result.loc[1, "target"] == pytest.approx(0.0)
    assert 0.0 < result.loc[2, "target"] < 1.0
    assert 0.0 < result.loc[3, "target"] < 1.0


def test_grouped_endpoint_propagation_matches_global_model_for_one_group():
    data = _effect_data()
    aoi = RectangleAOI("right", 0.0, -10.0, 10.0, 10.0)
    model = GaussianGazeErrorModel(np.zeros(2), np.eye(2) * 4.0, 20)
    grouped = GroupedGaussianGazeErrorModel({"v1": model})

    global_audit = audit_aoi_effect_uncertainty(
        data,
        aoi,
        model,
        condition_dwell_effect,
        draws=64,
        batch_size=11,
        rng=991,
    )
    grouped_audit = audit_aoi_effect_uncertainty(
        data,
        aoi,
        grouped,
        condition_dwell_effect,
        error_group="validation_block",
        draws=64,
        batch_size=11,
        rng=991,
    )

    pd.testing.assert_frame_equal(global_audit.draw_effects, grouped_audit.draw_effects)
    pd.testing.assert_frame_equal(
        global_audit.membership_probabilities,
        grouped_audit.membership_probabilities,
    )
    pd.testing.assert_series_equal(global_audit.summary, grouped_audit.summary)


def test_grouped_models_fail_closed_for_missing_unknown_or_misaligned_groups():
    model = GaussianGazeErrorModel(np.zeros(2), np.eye(2), 9)
    grouped = GroupedGaussianGazeErrorModel({"known": model})
    points = np.array([[0.0, 0.0], [1.0, 0.0]])
    aoi = CircleAOI("target", 0.0, 0.0, 1.0)

    with pytest.raises(ValueError, match="groups are required"):
        aoi_probabilities(points, [aoi], grouped, draws=8, rng=1)
    with pytest.raises(ValueError, match="unmapped"):
        aoi_probabilities(
            points,
            [aoi],
            grouped,
            groups=["known", "unknown"],
            draws=8,
            rng=1,
        )
    with pytest.raises(ValueError, match="missing"):
        aoi_probabilities(
            points,
            [aoi],
            grouped,
            groups=["known", None],
            draws=8,
            rng=1,
        )
    with pytest.raises(ValueError, match="match observations"):
        aoi_probabilities(
            points,
            [aoi],
            grouped,
            groups=["known"],
            draws=8,
            rng=1,
        )

    data = _effect_data()
    data["validation_block"] = ["known", "known", "unknown", "known"]
    with pytest.raises(ValueError, match="unmapped"):
        audit_aoi_effect_uncertainty(
            data,
            RectangleAOI("right", 0.0, -10.0, 10.0, 10.0),
            grouped,
            condition_dwell_effect,
            error_group="validation_block",
            draws=8,
            rng=1,
        )
    with pytest.raises(ValueError, match="not present"):
        audit_aoi_effect_uncertainty(
            data,
            RectangleAOI("right", 0.0, -10.0, 10.0, 10.0),
            grouped,
            condition_dwell_effect,
            error_group="missing_column",
            draws=8,
            rng=1,
        )


def test_tuple_group_keys_are_supported_for_participant_by_validation_blocks():
    model = GaussianGazeErrorModel(np.zeros(2), np.zeros((2, 2)), 9)
    grouped = GroupedGaussianGazeErrorModel({("p1", 1): model, ("p2", 1): model})
    points = np.array([[0.0, 0.0], [2.0, 0.0]])
    result = aoi_probabilities(
        points,
        [CircleAOI("target", 0.0, 0.0, 1.0)],
        grouped,
        groups=[("p1", 1), ("p2", 1)],
        draws=8,
        rng=5,
    )
    assert list(result["target"]) == [1.0, 0.0]
