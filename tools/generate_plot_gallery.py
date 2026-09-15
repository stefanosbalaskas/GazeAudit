"""Generate the committed GazeAudit plot gallery deterministically."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from gazeaudit import (
    RectangleAOI,
    ReadinessThresholds,
    evaluate_analysis_readiness,
    marginal_sensitivity,
    missingness_sensitivity_curve,
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
    readiness_policy_table,
    sampling_sensitivity_curve,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "plots"
MANIFEST = OUTPUT / "gallery-manifest.json"
matplotlib.rcParams["svg.hashsalt"] = "gazeaudit-gallery-v1"
matplotlib.rcParams["svg.fonttype"] = "none"


def _demo() -> dict[str, object]:
    namespace = runpy.run_path(str(ROOT / "examples" / "analysis_readiness.py"))
    return namespace["run_demo"]()


def _endpoint(study) -> float:
    values = pd.to_numeric(study.data[study.x], errors="coerce").to_numpy(float)
    return float(np.nanmean(values) - 0.75)


def _save(fig, filename: str, title: str, description: str, category: str) -> dict[str, str]:
    path = OUTPUT / filename
    fig.savefig(
        path,
        format="svg",
        bbox_inches="tight",
        metadata={"Title": title, "Description": description, "Creator": "GazeAudit", "Date": None},
    )
    plt.close(fig)
    text = path.read_text(encoding="utf-8")
    if "<title>" not in text or "<desc>" not in text:
        raise RuntimeError(f"SVG accessibility metadata missing from {filename}")
    return {
        "filename": filename,
        "title": title,
        "description": description,
        "category": category,
        "source": "tools/generate_plot_gallery.py",
    }


def generate() -> list[dict[str, str]]:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    demo = _demo()
    study = demo["study"]
    readiness = demo["readiness"]
    policy_table = demo["policy_table"]
    repair = demo["repair_comparison"]
    spec_results = demo["specification_results"]

    entries: list[dict[str, str]] = []
    entries.append(_save(
        plot_qc_issue_profile(readiness.qc_audit.report),
        "qc-issue-profile.svg",
        "Structural QC issue profile",
        "Synthetic example showing counts across the five structural QC issue families.",
        "readiness",
    ))
    entries.append(_save(
        plot_trial_readiness(readiness.trial_summary),
        "trial-readiness.svg",
        "Trial-level readiness preview",
        "Synthetic participant-by-trial units showing structural issue burden and policy-relative pass or review status.",
        "readiness",
    ))
    entries.append(_save(
        plot_participant_readiness(readiness.participant_summary),
        "participant-readiness.svg",
        "Participant readiness profile",
        "Synthetic participant-level fraction of trials failing the declared structural policy.",
        "readiness",
    ))
    entries.append(_save(
        plot_cohort_impact(readiness.cohort_impact, metric="rows"),
        "cohort-impact.svg",
        "Cohort impact preview",
        "Synthetic baseline-versus-retained row counts under explicit trial- and participant-scope filtering previews.",
        "readiness",
    ))
    entries.append(_save(
        plot_repair_comparison(repair.metrics),
        "repair-comparison.svg",
        "Before and after structural QC",
        "Synthetic comparison of structural QC counts before and after an explicitly performed repair operation.",
        "readiness",
    ))
    entries.append(_save(
        plot_policy_tradeoffs(policy_table),
        "policy-tradeoffs.svg",
        "Readiness-policy cohort trade-offs",
        "Synthetic comparison of trial-scope and participant-scope retained rows across declared policies.",
        "readiness",
    ))

    sweep_rows = []
    for threshold in (0.00, 0.02, 0.05, 0.10, 0.20):
        report = evaluate_analysis_readiness(
            study,
            ReadinessThresholds(max_coordinate_issue_fraction=threshold),
            policy_name=f"coordinate_{threshold:.2f}",
        )
        trial_row = report.cohort_impact.loc[report.cohort_impact["scope"] == "trial"].iloc[0]
        sweep_rows.append({"threshold": threshold, "retained_fraction": float(trial_row["retained_row_fraction"])})
    sweep = pd.DataFrame(sweep_rows)
    entries.append(_save(
        plot_threshold_sweep(sweep),
        "threshold-sweep.svg",
        "Threshold sensitivity of cohort retention",
        "Synthetic sensitivity curve showing how retained rows change as a user-declared coordinate-issue threshold changes.",
        "readiness",
    ))

    entries.append(_save(
        plot_specification_curve(spec_results),
        "specification-curve-code.svg",
        "Specification curve",
        "Code-generated synthetic estimates ordered across readiness-policy and endpoint-offset specifications.",
        "robustness",
    ))
    factors = marginal_sensitivity(spec_results, ["readiness_policy", "offset"])
    entries.append(_save(
        plot_factor_sensitivity(factors),
        "factor-sensitivity.svg",
        "Specification-factor sensitivity",
        "Synthetic marginal sensitivity diagnostic ranking the declared specification factors.",
        "robustness",
    ))

    cleaned = demo["repaired"]
    missingness = missingness_sensitivity_curve(
        cleaned,
        (0.0, 0.05, 0.10, 0.20, 0.30),
        _endpoint,
        mechanism="mcar",
        rng=20260915,
    )
    entries.append(_save(
        plot_sensitivity_curve(
            missingness,
            x_col="observed_missing_fraction",
            title="Missingness sensitivity",
            x_label="Observed missing fraction",
        ),
        "missingness-sensitivity-code.svg",
        "Missingness sensitivity",
        "Synthetic controlled-MCAR perturbation showing the scientific endpoint across increasing observed missingness.",
        "sensitivity",
    ))

    sampling = sampling_sensitivity_curve(
        cleaned,
        (60.0, 40.0, 30.0, 20.0, 15.0),
        _endpoint,
        timestamp_unit="ms",
    )
    entries.append(_save(
        plot_sensitivity_curve(
            sampling,
            x_col="target_hz",
            title="Sampling-rate sensitivity",
            x_label="Target sampling rate (Hz)",
        ),
        "sampling-sensitivity-code.svg",
        "Sampling-rate sensitivity",
        "Synthetic controlled downsampling analysis showing the endpoint across declared target sampling rates.",
        "sensitivity",
    ))

    trajectory = cleaned.data.loc[
        (cleaned.data["participant"] == "P01") & (cleaned.data["trial"] == 1)
    ].reset_index(drop=True)
    entries.append(_save(
        plot_gaze_trajectory(
            trajectory,
            aoi=RectangleAOI("target", xmin=0.55, ymin=0.35, xmax=1.05, ymax=0.75),
        ),
        "gaze-trajectory-aoi.svg",
        "Gaze trajectory and AOI geometry",
        "Synthetic gaze trajectory overlaid with an explicitly declared rectangular AOI.",
        "measurement",
    ))

    distances = np.linspace(-0.30, 0.30, 13)
    probabilities = 1.0 / (1.0 + np.exp(18.0 * distances))
    profile = pd.DataFrame(
        {"boundary_distance": distances, "membership_probability": probabilities}
    )
    entries.append(_save(
        plot_aoi_probability_profile(profile),
        "aoi-probability-profile.svg",
        "Probabilistic AOI boundary profile",
        "Synthetic probability profile illustrating gradual AOI membership around a signed boundary distance.",
        "measurement",
    ))

    recovery = pd.DataFrame(
        [
            {"missingness": m, "sampling_hz": hz, "recovery": 1.0 - 0.65 * m - 0.004 * (60 - hz)}
            for m in (0.0, 0.10, 0.20, 0.30)
            for hz in (60, 40, 20)
        ]
    )
    entries.append(_save(
        plot_recovery_matrix(
            recovery,
            row_col="missingness",
            column_col="sampling_hz",
            value_col="recovery",
            title="Synthetic recovery surface",
        ),
        "recovery-matrix.svg",
        "Synthetic recovery matrix",
        "Illustrative matrix of deterministic recovery values across missingness and sampling-rate conditions.",
        "robustness",
    ))

    MANIFEST.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return entries


if __name__ == "__main__":
    generated = generate()
    print(f"generated {len(generated)} plot-gallery SVGs in {OUTPUT}")
