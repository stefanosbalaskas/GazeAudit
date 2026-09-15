"""Executable analysis-readiness governance example."""

from __future__ import annotations

import numpy as np
import pandas as pd

from gazeaudit import (
    GazeStudy,
    PipelineSpace,
    ReadinessThresholds,
    compare_qc_states,
    evaluate_analysis_readiness,
    readiness_pipeline_processor,
    readiness_policy_table,
    run_specs,
)


def build_demo_study() -> GazeStudy:
    rows: list[dict[str, object]] = []
    for participant_index, participant in enumerate(("P01", "P02", "P03")):
        for trial in (1, 2):
            for sample in range(24):
                rows.append(
                    {
                        "participant": participant,
                        "trial": trial,
                        "timestamp": sample * (1000.0 / 60.0),
                        "x": 0.25 + 0.045 * sample + 0.04 * participant_index,
                        "y": 0.55 + 0.12 * np.sin(sample / 4.0 + trial),
                    }
                )
    data = pd.DataFrame(rows)
    data.loc[(data["participant"] == "P02") & (data["trial"] == 2) & (data.index % 11 == 0), "x"] = np.nan
    duplicate_mask = (data["participant"] == "P03") & (data["trial"] == 1)
    duplicate_rows = data.loc[duplicate_mask].index[:2]
    data.loc[duplicate_rows[1], "timestamp"] = data.loc[duplicate_rows[0], "timestamp"]
    disorder = data.index[(data["participant"] == "P01") & (data["trial"] == 2)][10:12]
    data.loc[disorder, "timestamp"] = data.loc[disorder[::-1], "timestamp"].to_numpy()
    return GazeStudy(data)


def repaired_study(study: GazeStudy) -> GazeStudy:
    data = study.data.copy()
    data["x"] = data.groupby(["participant", "trial"], dropna=False)["x"].transform(
        lambda values: values.fillna(values.median())
    )
    data = data.drop_duplicates(["participant", "trial", "timestamp"], keep="first")
    data = data.sort_values(["participant", "trial", "timestamp"], kind="mergesort")
    return study.copy_with(data.reset_index(drop=True))


def run_demo() -> dict[str, object]:
    study = build_demo_study()
    policies = {
        "lenient": ReadinessThresholds(
            max_coordinate_issue_fraction=0.15,
            max_duplicate_timestamp_fraction=0.10,
            max_flagged_trial_fraction=0.75,
            min_rows_per_trial=20,
            require_monotonic_time=True,
        ),
        "primary": ReadinessThresholds(
            max_coordinate_issue_fraction=0.05,
            max_duplicate_timestamp_fraction=0.05,
            max_flagged_trial_fraction=0.50,
            min_rows_per_trial=20,
            require_monotonic_time=True,
        ),
        "strict": ReadinessThresholds(
            max_coordinate_issue_fraction=0.01,
            max_duplicate_timestamp_fraction=0.01,
            max_flagged_trial_fraction=0.25,
            min_rows_per_trial=24,
            require_monotonic_time=True,
        ),
    }
    readiness = evaluate_analysis_readiness(study, policies["primary"], policy_name="primary")
    policy_table = readiness_policy_table(study, policies)
    repaired = repaired_study(study)
    repair_comparison = compare_qc_states(study, repaired)

    space = PipelineSpace().add_choice("readiness_policy", policies).add_choice(
        "offset", (-0.10, 0.0, 0.10)
    )
    processor = readiness_pipeline_processor(policies, scope="trial")

    def endpoint(processed: GazeStudy, spec: dict[str, object]) -> float:
        values = pd.to_numeric(processed.data[processed.x], errors="coerce").to_numpy(float)
        return float(np.nanmean(values) - 0.75 + float(spec["offset"]))

    specification_results = run_specs(study, space, endpoint, processor=processor)
    return {
        "study": study,
        "policies": policies,
        "readiness": readiness,
        "policy_table": policy_table,
        "repaired": repaired,
        "repair_comparison": repair_comparison,
        "specification_results": specification_results,
    }


if __name__ == "__main__":
    demo = run_demo()
    readiness = demo["readiness"]
    print("status:", readiness.status)
    print(readiness.cohort_impact.to_string(index=False))
    print(demo["policy_table"].to_string(index=False))
    print(demo["repair_comparison"].metrics.to_string(index=False))
