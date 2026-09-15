from __future__ import annotations

import runpy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("matplotlib")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from gazeaudit import (
    RectangleAOI,
    marginal_sensitivity,
    plot_aoi_probability_profile,
    plot_cohort_impact,
    plot_factor_sensitivity,
    plot_gaze_trajectory,
    plot_participant_readiness,
    plot_policy_tradeoffs,
    plot_qc_issue_profile,
    plot_recovery_matrix,
    plot_repair_comparison,
    plot_sensitivity_curve,
    plot_specification_curve,
    plot_threshold_sweep,
    plot_trial_readiness,
)

ROOT = Path(__file__).resolve().parents[1]


def _demo() -> dict[str, object]:
    namespace = runpy.run_path(str(ROOT / "examples" / "analysis_readiness.py"))
    return namespace["run_demo"]()


def _assert_figure(fig) -> None:
    assert hasattr(fig, "savefig")
    assert len(fig.axes) >= 1
    plt.close(fig)


def test_readiness_plot_family_returns_figures() -> None:
    demo = _demo()
    readiness = demo["readiness"]
    for fig in (
        plot_qc_issue_profile(readiness.qc_audit.report),
        plot_trial_readiness(readiness.trial_summary),
        plot_participant_readiness(readiness.participant_summary),
        plot_cohort_impact(readiness.cohort_impact),
        plot_repair_comparison(demo["repair_comparison"].metrics),
        plot_policy_tradeoffs(demo["policy_table"]),
    ):
        _assert_figure(fig)


def test_robustness_and_sensitivity_plot_family_returns_figures() -> None:
    demo = _demo()
    results = demo["specification_results"]
    factors = marginal_sensitivity(results, ["readiness_policy", "offset"])
    sweep = pd.DataFrame(
        {"threshold": [0.0, 0.05, 0.10], "retained_fraction": [0.5, 0.8, 1.0]}
    )
    curve = pd.DataFrame({"level": [0.0, 0.1, 0.2], "estimate": [0.4, 0.3, 0.2]})
    for fig in (
        plot_threshold_sweep(sweep),
        plot_specification_curve(results),
        plot_factor_sensitivity(factors),
        plot_sensitivity_curve(curve, x_col="level"),
    ):
        _assert_figure(fig)


def test_measurement_and_recovery_plots_return_figures() -> None:
    demo = _demo()
    study = demo["repaired"]
    trajectory = study.data.loc[
        (study.data["participant"] == "P01") & (study.data["trial"] == 1)
    ]
    profile = pd.DataFrame(
        {
            "boundary_distance": np.linspace(-0.2, 0.2, 5),
            "membership_probability": [0.95, 0.75, 0.5, 0.25, 0.05],
        }
    )
    recovery = pd.DataFrame(
        [
            {"missingness": m, "sampling_hz": hz, "recovery": 1.0 - m - hz / 1000}
            for m in (0.0, 0.1)
            for hz in (60, 30)
        ]
    )
    for fig in (
        plot_gaze_trajectory(
            trajectory,
            aoi=RectangleAOI("target", 0.5, 0.3, 1.1, 0.8),
        ),
        plot_aoi_probability_profile(profile),
        plot_recovery_matrix(
            recovery,
            row_col="missingness",
            column_col="sampling_hz",
            value_col="recovery",
        ),
    ):
        _assert_figure(fig)


def test_plotting_validates_required_columns() -> None:
    with pytest.raises(ValueError):
        plot_specification_curve(pd.DataFrame({"wrong": [1.0]}))
    with pytest.raises(ValueError):
        plot_trial_readiness(pd.DataFrame({"trial_unit_id": ["T1"]}))
