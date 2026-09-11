import numpy as np
import pandas as pd
import pytest

from gazeaudit.aoi import RectangleAOI
from gazeaudit.aoi_propagation import audit_aoi_effect_uncertainty
from gazeaudit.scientific_benchmark import condition_dwell_effect, simulate_known_aoi_effect
from gazeaudit.uncertainty import GaussianGazeErrorModel


def _zero_error_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "participant": ["p1", "p1", "p2", "p2"],
            "condition": ["control", "treatment", "control", "treatment"],
            "duration": [100.0, 100.0, 200.0, 200.0],
            "observed_x": [-5.0, 5.0, -5.0, 5.0],
            "observed_y": [0.0, 0.0, 0.0, 0.0],
        }
    )


def test_zero_measurement_error_collapses_to_hard_effect():
    data = _zero_error_data()
    aoi = RectangleAOI("right", 0.0, -10.0, 10.0, 10.0)
    model = GaussianGazeErrorModel(
        mean_error=np.zeros(2),
        covariance=np.zeros((2, 2)),
        n_validation=20,
    )

    audit = audit_aoi_effect_uncertainty(
        data,
        aoi,
        model,
        condition_dwell_effect,
        draws=32,
        batch_size=7,
        rng=123,
    )

    assert audit.aoi == "right"
    assert audit.summary["hard_effect"] == pytest.approx(150.0)
    assert audit.summary["expected_membership_effect"] == pytest.approx(150.0)
    assert audit.summary["monte_carlo_mean"] == pytest.approx(150.0)
    assert audit.summary["monte_carlo_sd"] == pytest.approx(0.0)
    assert audit.summary["interval_lower"] == pytest.approx(150.0)
    assert audit.summary["interval_upper"] == pytest.approx(150.0)
    assert (audit.draw_effects["estimate"] == pytest.approx(150.0)).all()
    assert list(audit.membership_probabilities["membership_probability"]) == [
        0.0,
        1.0,
        0.0,
        1.0,
    ]


def test_uncertainty_audit_is_reproducible_and_probability_accounting_is_complete():
    data = simulate_known_aoi_effect(
        n_participants=8,
        trials_per_condition=5,
        control_probability=0.25,
        treatment_probability=0.75,
        measurement_sd=9.0,
        rng=44,
    )
    errors = np.column_stack(
        [
            data["observed_x"].to_numpy() - data["true_x"].to_numpy(),
            data["observed_y"].to_numpy() - data["true_y"].to_numpy(),
        ]
    )
    model = GaussianGazeErrorModel(
        mean_error=errors.mean(axis=0),
        covariance=np.cov(errors, rowvar=False, ddof=1),
        n_validation=len(errors),
    )
    aoi = RectangleAOI("right", 0.0, -100.0, 100.0, 100.0)

    first = audit_aoi_effect_uncertainty(
        data,
        aoi,
        model,
        condition_dwell_effect,
        draws=64,
        batch_size=16,
        interval=0.90,
        rng=991,
    )
    second = audit_aoi_effect_uncertainty(
        data,
        aoi,
        model,
        condition_dwell_effect,
        draws=64,
        batch_size=16,
        interval=0.90,
        rng=991,
    )

    pd.testing.assert_frame_equal(first.draw_effects, second.draw_effects)
    pd.testing.assert_frame_equal(
        first.membership_probabilities,
        second.membership_probabilities,
    )
    pd.testing.assert_series_equal(first.summary, second.summary)
    assert first.summary["interval_level"] == pytest.approx(0.90)
    assert first.summary["interval_lower"] <= first.summary["interval_upper"]
    assert np.isfinite(first.draw_effects["estimate"]).all()
    probabilities = first.membership_probabilities["membership_probability"].to_numpy()
    assert np.all((probabilities >= 0.0) & (probabilities <= 1.0))
    reference_mass = (
        first.summary["probability_above_reference"]
        + first.summary["probability_below_reference"]
        + first.summary["probability_equal_reference"]
    )
    assert reference_mass == pytest.approx(1.0)


def test_endpoint_is_evaluated_on_complete_latent_realizations():
    data = _zero_error_data()
    aoi = RectangleAOI("right", 0.0, -10.0, 10.0, 10.0)
    model = GaussianGazeErrorModel(
        mean_error=np.zeros(2),
        covariance=np.eye(2) * 16.0,
        n_validation=20,
    )
    observed_lengths: list[int] = []

    def endpoint(frame: pd.DataFrame, membership: np.ndarray) -> float:
        observed_lengths.append(len(membership))
        return float(np.mean(membership))

    audit = audit_aoi_effect_uncertainty(
        data,
        aoi,
        model,
        endpoint,
        draws=12,
        batch_size=5,
        rng=3,
    )

    # One hard endpoint, one endpoint on marginal probabilities, and one per draw.
    assert observed_lengths == [len(data)] * 14
    assert len(audit.draw_effects) == 12


def test_aoi_effect_uncertainty_input_validation_and_endpoint_guardrails():
    data = _zero_error_data()
    aoi = RectangleAOI("right", 0.0, -10.0, 10.0, 10.0)
    model = GaussianGazeErrorModel(
        mean_error=np.zeros(2),
        covariance=np.eye(2),
        n_validation=20,
    )

    with pytest.raises(ValueError, match="draws"):
        audit_aoi_effect_uncertainty(data, aoi, model, condition_dwell_effect, draws=1)
    with pytest.raises(ValueError, match="batch_size"):
        audit_aoi_effect_uncertainty(
            data,
            aoi,
            model,
            condition_dwell_effect,
            batch_size=0,
        )
    with pytest.raises(ValueError, match="interval"):
        audit_aoi_effect_uncertainty(
            data,
            aoi,
            model,
            condition_dwell_effect,
            interval=1.0,
        )
    with pytest.raises(ValueError, match="reference"):
        audit_aoi_effect_uncertainty(
            data,
            aoi,
            model,
            condition_dwell_effect,
            reference=np.inf,
        )
    with pytest.raises(ValueError, match="observed gaze columns"):
        audit_aoi_effect_uncertainty(
            data.drop(columns=["observed_y"]),
            aoi,
            model,
            condition_dwell_effect,
        )

    bad = data.copy()
    bad.loc[0, "observed_x"] = np.nan
    with pytest.raises(ValueError, match="finite and complete"):
        audit_aoi_effect_uncertainty(bad, aoi, model, condition_dwell_effect)

    with pytest.raises(TypeError, match="scalar"):
        audit_aoi_effect_uncertainty(
            data,
            aoi,
            model,
            lambda _frame, _membership: np.array([1.0, 2.0]),
            draws=2,
        )
    with pytest.raises(ValueError, match="finite scalar"):
        audit_aoi_effect_uncertainty(
            data,
            aoi,
            model,
            lambda _frame, _membership: np.nan,
            draws=2,
        )
