"""Deterministic end-to-end GazeAudit robustness example.

The data are synthetic and are designed only to exercise the public API. They
are not empirical validation evidence and must not be interpreted as a claim
about any real eye-tracking dataset.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from gazeaudit import (
    GazeStudy,
    PipelineSpace,
    effect_stability,
    marginal_sensitivity,
    pairwise_interaction_sensitivity,
    run_specs,
    specification_curve,
)


def build_synthetic_study() -> GazeStudy:
    """Create a deterministic gaze-like table with two synthetic conditions."""

    rows: list[dict[str, object]] = []
    for participant in range(1, 13):
        for trial in range(1, 5):
            condition = "treatment" if trial % 2 == 0 else "control"
            shift = 0.035 if condition == "treatment" else 0.0
            for sample in range(60):
                phase = sample + participant * 3 + trial
                rows.append(
                    {
                        "participant": f"P{participant:02d}",
                        "trial": trial,
                        "timestamp": sample / 60.0,
                        "x": 0.50 + shift + 0.16 * np.sin(phase / 7.0),
                        "y": 0.50
                        + 0.14 * np.cos((sample + participant + trial * 2) / 9.0),
                        "condition": condition,
                        "quality": 0.65
                        + 0.35
                        * (((sample * 17 + participant * 13 + trial * 7) % 101) / 100.0),
                    }
                )

    return GazeStudy(pd.DataFrame(rows))


def process_specification(study: GazeStudy, spec: dict[str, object]) -> GazeStudy:
    """Apply declared QC and sample-retention choices without mutating the input."""

    frame = study.data.copy()
    frame["sample_rank"] = frame.groupby(
        [study.participant, study.trial], sort=False
    ).cumcount()
    keep = (frame["quality"] >= float(spec["min_quality"])) & (
        frame["sample_rank"] % int(spec["sample_stride"]) == 0
    )
    return study.copy_with(frame.loc[keep].drop(columns="sample_rank"))


def condition_aoi_occupancy_effect(
    processed: GazeStudy, spec: dict[str, object]
) -> float:
    """Return treatment minus control AOI occupancy for one specification."""

    radius = float(spec["aoi_radius"])
    frame = processed.data
    squared_distance = (frame[processed.x] - 0.50) ** 2 + (
        frame[processed.y] - 0.50
    ) ** 2
    inside = squared_distance <= radius**2
    by_condition = (
        frame.assign(in_aoi=inside)
        .groupby("condition", sort=False)["in_aoi"]
        .mean()
    )
    return float(by_condition["treatment"] - by_condition["control"])


def run_demo() -> dict[str, object]:
    """Run the complete synthetic robustness audit and return all core outputs."""

    study = build_synthetic_study()
    study.validate_time_order()

    space = (
        PipelineSpace()
        .add_choice("min_quality", [0.70, 0.80])
        .add_choice("sample_stride", [1, 2])
        .add_choice("aoi_radius", [0.16, 0.20, 0.24])
    )

    results = run_specs(
        study,
        space,
        endpoint=condition_aoi_occupancy_effect,
        processor=process_specification,
    )
    factors = ["min_quality", "sample_stride", "aoi_radius"]

    return {
        "study": study,
        "space": space,
        "results": results,
        "curve": specification_curve(results),
        "stability": effect_stability(results),
        "marginal": marginal_sensitivity(results, factors=factors),
        "pairwise": pairwise_interaction_sensitivity(results, factors=factors),
    }


if __name__ == "__main__":
    audit = run_demo()
    print("\nSpecification results")
    print(audit["results"].to_string(index=False))
    print("\nEffect stability")
    print(audit["stability"].to_string())
    print("\nMarginal sensitivity")
    print(audit["marginal"].to_string(index=False))
    print("\nPairwise interaction sensitivity")
    print(audit["pairwise"].to_string(index=False))
