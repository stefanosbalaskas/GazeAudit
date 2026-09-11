import numpy as np
import pandas as pd
import pytest

from gazeaudit import RectangleAOI, fit_error_model_from_known_truth
from gazeaudit.conclusion import (
    ConclusionRule,
    aoi_conclusion_specifications,
    conclusion_recovery_table,
    run_canonical_conclusion_benchmark,
    run_paired_conclusion_benchmark,
    summarize_conclusion_recovery,
)
from gazeaudit.scientific_benchmark import simulate_known_aoi_effect


def test_conclusion_rule_requires_predeclared_numerical_tolerance():
    with pytest.raises(ValueError, match="at least one"):
        ConclusionRule()
    with pytest.raises(ValueError, match="relative_tolerance"):
        ConclusionRule(relative_tolerance=-0.1)
    with pytest.raises(ValueError, match="absolute_tolerance"):
        ConclusionRule(absolute_tolerance=np.inf)
    with pytest.raises(ValueError, match="minimum_recovery_fraction"):
        ConclusionRule(relative_tolerance=0.2, minimum_recovery_fraction=1.1)


def test_conclusion_recovery_table_is_direction_and_tolerance_based_not_p_value_based():
    results = pd.DataFrame(
        {
            "specification": ["baseline", "attenuated", "reversed"],
            "estimate": [10.0, 7.0, -10.0],
            "p_value": [0.90, 0.001, 0.001],
        }
    )
    rule = ConclusionRule(relative_tolerance=0.25, require_sign=True)
    recovery = conclusion_recovery_table(results, 10.0, rule)

    assert list(recovery["relative_error"]) == pytest.approx([0.0, 0.3, 2.0])
    assert list(recovery["conclusion_recovered"]) == [True, False, False]
    assert list(recovery["p_value"]) == [0.90, 0.001, 0.001]


def test_conclusion_recovery_combines_absolute_and_relative_tolerances():
    results = pd.DataFrame({"estimate": [9.0, 8.0, 11.5]})
    rule = ConclusionRule(
        relative_tolerance=0.20,
        absolute_tolerance=1.5,
        require_sign=True,
    )
    recovery = conclusion_recovery_table(results, 10.0, rule)
    assert list(recovery["absolute_tolerance_recovered"]) == [True, False, True]
    assert list(recovery["relative_tolerance_recovered"]) == [True, True, True]
    assert list(recovery["conclusion_recovered"]) == [True, False, True]


def test_zero_true_effect_requires_absolute_tolerance_when_relative_requested():
    results = pd.DataFrame({"estimate": [0.1, -0.2]})
    with pytest.raises(ValueError, match="true_effect is zero"):
        conclusion_recovery_table(
            results,
            0.0,
            ConclusionRule(relative_tolerance=0.2),
        )

    recovery = conclusion_recovery_table(
        results,
        0.0,
        ConclusionRule(absolute_tolerance=0.15),
    )
    assert recovery["relative_error"].isna().all()
    assert list(recovery["conclusion_recovered"]) == [True, False]


def test_conclusion_summary_classification_uses_predeclared_recovery_fraction():
    results = pd.DataFrame({"estimate": [10.0, 9.0, 8.0, 5.0]})
    rule = ConclusionRule(
        relative_tolerance=0.20,
        minimum_recovery_fraction=0.75,
    )
    recovery = conclusion_recovery_table(results, 10.0, rule)
    summary = summarize_conclusion_recovery(recovery, rule)

    assert summary["conclusion_recovery_fraction"] == pytest.approx(0.75)
    assert summary["classification"] == "robust"

    stricter = ConclusionRule(
        relative_tolerance=0.20,
        minimum_recovery_fraction=0.80,
    )
    strict_summary = summarize_conclusion_recovery(recovery, stricter)
    assert strict_summary["classification"] == "fragile"


def test_aoi_conclusion_specifications_are_reproducible_and_share_missingness_masks():
    data = simulate_known_aoi_effect(
        n_participants=20,
        trials_per_condition=8,
        control_probability=0.2,
        treatment_probability=0.8,
        left_center=-25,
        right_center=25,
        center_sd=4,
        measurement_sd=4,
        rng=99,
    )
    model = fit_error_model_from_known_truth(data)
    aoi = RectangleAOI("right", 0.0, -100.0, 100.0, 100.0)

    first_truth, first = aoi_conclusion_specifications(
        data,
        aoi,
        model,
        error_scales=[0.5, 1.0],
        missing_fractions=[0.0, 0.1],
        draws=300,
        rng=123,
    )
    second_truth, second = aoi_conclusion_specifications(
        data,
        aoi,
        model,
        error_scales=[0.5, 1.0],
        missing_fractions=[0.0, 0.1],
        draws=300,
        rng=123,
    )

    assert first_truth == pytest.approx(second_truth)
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 6
    assert set(first["method"]) == {"hard", "probabilistic"}
    row_counts = first.groupby("missing_fraction")["n_rows"].nunique()
    assert (row_counts == 1).all()


def test_aoi_conclusion_specification_validation():
    data = simulate_known_aoi_effect(n_participants=4, trials_per_condition=2, rng=1)
    model = fit_error_model_from_known_truth(data)
    aoi = RectangleAOI("right", 0.0, -100.0, 100.0, 100.0)

    with pytest.raises(ValueError, match="error_scales"):
        aoi_conclusion_specifications(data, aoi, model, error_scales=[])
    with pytest.raises(ValueError, match="non-negative"):
        aoi_conclusion_specifications(data, aoi, model, error_scales=[-1])
    with pytest.raises(ValueError, match="missing_fractions"):
        aoi_conclusion_specifications(data, aoi, model, missing_fractions=[])
    with pytest.raises(ValueError, match=r"\[0, 1\)"):
        aoi_conclusion_specifications(data, aoi, model, missing_fractions=[1.0])
    with pytest.raises(ValueError, match="draws"):
        aoi_conclusion_specifications(data, aoi, model, draws=0)


def test_canonical_robust_and_fragile_cases_separate_under_same_rule():
    rule = ConclusionRule(
        relative_tolerance=0.25,
        require_sign=True,
        minimum_recovery_fraction=0.90,
    )
    robust = run_canonical_conclusion_benchmark(
        "robust",
        rule=rule,
        n_participants=50,
        trials_per_condition=20,
        draws=300,
        rng=123,
    )
    fragile = run_canonical_conclusion_benchmark(
        "fragile",
        rule=rule,
        n_participants=50,
        trials_per_condition=20,
        draws=300,
        rng=123,
    )

    assert robust.true_effect > 0
    assert fragile.true_effect > 0
    assert robust.summary["classification"] == "robust"
    assert fragile.summary["classification"] == "fragile"
    assert (
        robust.summary["conclusion_recovery_fraction"]
        > fragile.summary["conclusion_recovery_fraction"]
    )


def test_paired_benchmark_is_reproducible_and_contains_both_challenge_cases():
    rule = ConclusionRule(
        relative_tolerance=0.25,
        require_sign=True,
        minimum_recovery_fraction=0.90,
    )
    first = run_paired_conclusion_benchmark(
        rule=rule,
        n_participants=30,
        trials_per_condition=12,
        draws=200,
        rng=44,
    )
    second = run_paired_conclusion_benchmark(
        rule=rule,
        n_participants=30,
        trials_per_condition=12,
        draws=200,
        rng=44,
    )
    assert set(first) == {"robust", "fragile"}
    pd.testing.assert_frame_equal(first["robust"].recovery, second["robust"].recovery)
    pd.testing.assert_frame_equal(first["fragile"].recovery, second["fragile"].recovery)


def test_recovery_validation_rejects_bad_results_and_unknown_case():
    rule = ConclusionRule(relative_tolerance=0.2)
    with pytest.raises(ValueError, match="not present"):
        conclusion_recovery_table(pd.DataFrame({"x": [1]}), 1.0, rule)
    with pytest.raises(ValueError, match="at least one specification"):
        conclusion_recovery_table(pd.DataFrame({"estimate": []}), 1.0, rule)
    with pytest.raises(ValueError, match="estimates must be finite"):
        conclusion_recovery_table(pd.DataFrame({"estimate": [np.nan]}), 1.0, rule)
    with pytest.raises(ValueError, match="true_effect"):
        conclusion_recovery_table(pd.DataFrame({"estimate": [1.0]}), np.inf, rule)
    with pytest.raises(ValueError, match="case"):
        run_canonical_conclusion_benchmark("unknown", rule=rule)
