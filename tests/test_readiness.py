from __future__ import annotations

import json
import runpy
from pathlib import Path

import pandas as pd
import pytest

from gazeaudit import (
    ReadinessThresholds,
    analysis_readiness_publication_metadata,
    cohort_impact_preview,
    evaluate_analysis_readiness,
    filter_study_by_readiness,
    readiness_policy_table,
    verify_analysis_readiness_artifacts,
    verify_analysis_readiness_manifest,
    verify_analysis_readiness_report,
    verify_repair_comparison,
    verify_repair_comparison_manifest,
    write_analysis_readiness_artifacts,
)

ROOT = Path(__file__).resolve().parents[1]


def _demo() -> dict[str, object]:
    namespace = runpy.run_path(str(ROOT / "examples" / "analysis_readiness.py"))
    return namespace["run_demo"]()


def test_thresholds_have_no_universal_defaults_and_are_fingerprinted() -> None:
    empty = ReadinessThresholds()
    assert empty.active_rules == ()
    assert len(empty.policy_fingerprint) == 64
    strict = ReadinessThresholds(max_coordinate_issue_fraction=0.01)
    assert strict.policy_fingerprint != empty.policy_fingerprint
    with pytest.raises(ValueError):
        ReadinessThresholds(max_coordinate_issue_fraction=1.1)
    with pytest.raises(ValueError):
        ReadinessThresholds(min_rows_per_trial=0)


def test_readiness_aggregates_trials_participants_and_previews_without_mutation() -> None:
    demo = _demo()
    study = demo["study"]
    readiness = demo["readiness"]
    before = study.data.copy(deep=True)

    assert len(readiness.trial_summary) == 6
    assert len(readiness.participant_summary) == 3
    assert set(readiness.cohort_impact["scope"]) == {"trial", "participant"}
    assert readiness.status in {"ready_under_policy", "review_under_policy"}
    assert verify_analysis_readiness_report(readiness)
    assert verify_analysis_readiness_manifest(readiness.manifest)
    pd.testing.assert_frame_equal(study.data, before)

    trial = cohort_impact_preview(readiness, scope="trial")
    assert len(trial) == 1
    assert 0.0 <= float(trial.iloc[0]["retained_row_fraction"]) <= 1.0


def test_filtering_is_explicit_and_preserves_original_study() -> None:
    demo = _demo()
    study = demo["study"]
    readiness = demo["readiness"]
    before = study.data.copy(deep=True)
    filtered = filter_study_by_readiness(study, readiness, scope="trial")

    assert 0 < len(filtered.data) <= len(study.data)
    pd.testing.assert_frame_equal(study.data, before)
    unassessed = evaluate_analysis_readiness(study, ReadinessThresholds())
    assert unassessed.status == "unassessed"
    with pytest.raises(ValueError):
        filter_study_by_readiness(study, unassessed)


def test_policy_table_and_pipeline_make_qc_choice_visible() -> None:
    demo = _demo()
    table = demo["policy_table"]
    results = demo["specification_results"]
    assert set(table["policy"]) == {"lenient", "primary", "strict"}
    assert table["policy_fingerprint"].str.len().eq(64).all()
    assert len(results) == 9
    assert set(results["readiness_policy"]) == {"lenient", "primary", "strict"}
    assert results["estimate"].notna().all()


def test_repair_comparison_is_provenance_bound_without_claiming_validity() -> None:
    demo = _demo()
    comparison = demo["repair_comparison"]
    assert verify_repair_comparison(comparison)
    assert verify_repair_comparison_manifest(comparison.manifest)
    assert comparison.before_audit.study_fingerprint != comparison.after_audit.study_fingerprint
    assert "delta" in comparison.metrics.columns


def test_readiness_artifacts_detect_tampering_and_bind_publication_metadata(tmp_path) -> None:
    demo = _demo()
    readiness = demo["readiness"]
    comparison = demo["repair_comparison"]
    paths = write_analysis_readiness_artifacts(
        readiness,
        tmp_path,
        repair_comparison=comparison,
    )
    assert verify_analysis_readiness_artifacts(tmp_path)
    metadata = analysis_readiness_publication_metadata(readiness)
    assert metadata["readiness_fingerprint"] == readiness.readiness_fingerprint
    assert metadata["policy_fingerprint"] == readiness.policy_fingerprint

    manifest = json.loads(paths["analysis_readiness_artifacts.json"].read_text())
    assert manifest["schema"].startswith("gazeaudit-analysis-readiness")
    target = paths["trial_readiness.csv"]
    target.write_text(target.read_text() + "tampered\n", encoding="utf-8")
    assert not verify_analysis_readiness_artifacts(tmp_path)


def test_policy_comparison_is_deterministic() -> None:
    demo = _demo()
    study = demo["study"]
    policies = demo["policies"]
    first = readiness_policy_table(study, policies)
    second = readiness_policy_table(study, policies)
    pd.testing.assert_frame_equal(first, second)
