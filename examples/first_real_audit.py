"""Practical GazeAudit workflow for a canonical CSV or deterministic demo data.

The demo mode uses synthetic data only. Supplying ``--csv`` is the intended
research workflow: map a study into the documented canonical columns, run
structural preflight, execute a declared robustness space, and save auditable
outputs without selecting a preferred specification after seeing the results.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from gazeaudit import (
    GazeStudy,
    PipelineSpace,
    build_study_qc_audit,
    effect_stability,
    marginal_sensitivity,
    pairwise_interaction_sensitivity,
    run_specs,
    specification_curve,
    write_study_qc_artifacts,
)

REQUIRED_COLUMNS = (
    "participant",
    "trial",
    "timestamp",
    "x",
    "y",
    "condition",
    "quality",
)


def build_demo_study() -> GazeStudy:
    """Return deterministic synthetic data that exercise the practical workflow."""

    rows: list[dict[str, object]] = []
    for participant in range(1, 9):
        for trial in range(1, 5):
            condition = "treatment" if trial % 2 == 0 else "control"
            shift = 0.03 if condition == "treatment" else 0.0
            for sample in range(48):
                phase = sample + participant * 2 + trial
                rows.append(
                    {
                        "participant": f"P{participant:02d}",
                        "trial": trial,
                        "timestamp": sample / 60.0,
                        "x": 0.50 + shift + 0.15 * np.sin(phase / 7.0),
                        "y": 0.50
                        + 0.13 * np.cos((sample + participant + trial) / 8.0),
                        "condition": condition,
                        "quality": 0.68
                        + 0.32
                        * (((sample * 13 + participant * 11 + trial * 5) % 101) / 100.0),
                    }
                )
    return GazeStudy(pd.DataFrame(rows))


def load_study(csv_path: str | Path) -> GazeStudy:
    """Load one canonical CSV and fail clearly when required columns are absent."""

    path = Path(csv_path)
    frame = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(
            "CSV is missing required canonical columns: " + ", ".join(missing)
        )
    return GazeStudy(frame)


def process_specification(study: GazeStudy, spec: dict[str, object]) -> GazeStudy:
    """Apply only the QC/sampling choices declared in the specification space."""

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
    """Return treatment minus control occupancy in a declared circular AOI."""

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
    required = {"control", "treatment"}
    if not required.issubset(by_condition.index):
        raise ValueError(
            "each specification must retain both 'control' and 'treatment' conditions"
        )
    return float(by_condition["treatment"] - by_condition["control"])


def run_audit(study: GazeStudy) -> dict[str, object]:
    """Run structural preflight plus a small declared robustness audit."""

    qc = build_study_qc_audit(study)
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
        "qc": qc,
        "space": space,
        "results": results,
        "curve": specification_curve(results),
        "stability": effect_stability(results),
        "marginal": marginal_sensitivity(results, factors=factors),
        "pairwise": pairwise_interaction_sensitivity(results, factors=factors),
    }


def write_outputs(audit: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    """Write QC provenance and robustness tables to one explicit output directory."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    qc_paths = write_study_qc_artifacts(audit["qc"], destination / "study-qc")
    table_paths = {
        "specifications": destination / "specifications.csv",
        "specification_curve": destination / "specification-curve.csv",
        "effect_stability": destination / "effect-stability.csv",
        "marginal_sensitivity": destination / "marginal-sensitivity.csv",
        "pairwise_sensitivity": destination / "pairwise-sensitivity.csv",
    }
    audit["results"].to_csv(table_paths["specifications"], index=False)
    audit["curve"].to_csv(table_paths["specification_curve"], index=False)
    audit["stability"].to_frame(name="value").to_csv(table_paths["effect_stability"])
    audit["marginal"].to_csv(table_paths["marginal_sensitivity"], index=False)
    audit["pairwise"].to_csv(table_paths["pairwise_sensitivity"], index=False)

    return {**{f"qc_{key}": value for key, value in qc_paths.items()}, **table_paths}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        type=Path,
        help=(
            "canonical gaze CSV with participant, trial, timestamp, x, y, "
            "condition, and quality columns; omit to run deterministic demo data"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("gazeaudit-output"),
        help="directory for QC provenance and robustness tables",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    study = load_study(args.csv) if args.csv is not None else build_demo_study()
    audit = run_audit(study)
    paths = write_outputs(audit, args.output_dir)

    print("study rows:", len(study.data))
    print("QC status:", audit["qc"].report.status)
    print("QC issue codes:", list(audit["qc"].report.issue_codes))
    print("specifications:", len(audit["results"]))
    print(audit["stability"].to_string())
    print("outputs:")
    for label, path in sorted(paths.items()):
        print(f"  {label}: {path}")


if __name__ == "__main__":
    main()
