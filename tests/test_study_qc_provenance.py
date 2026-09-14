from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    ConclusionRule,
    GazeStudy,
    STUDY_QC_ARTIFACT_SCHEMA,
    STUDY_QC_PUBLICATION_LINK_SCHEMA,
    STUDY_QC_SCHEMA,
    StudyQCAudit,
    StudyQCDecision,
    build_conclusion_audit_bundle,
    build_study_qc_audit,
    study_qc_diagnostics,
    study_qc_publication_metadata,
    verify_publication_audit_bundle,
    verify_study_qc_artifacts,
    verify_study_qc_audit,
    verify_study_qc_manifest,
    write_study_qc_artifacts,
)


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "pid": ["p1", "p1", "p1", "p2", "p2", "p2"],
            "trial": ["a", "a", "a", "b", "b", "b"],
            "time": [0.0, 1.0, 1.0, 0.0, 2.0, 1.0],
            "gx": [100.0, np.nan, np.inf, 200.0, 201.0, 202.0],
            "gy": [50.0, 51.0, 52.0, 60.0, np.nan, 62.0],
            "condition": ["A", "A", "A", "B", "B", "B"],
        }
    )


def _study(frame: pd.DataFrame | None = None) -> GazeStudy:
    return GazeStudy(
        _frame() if frame is None else frame,
        x="gx",
        y="gy",
        timestamp="time",
        participant="pid",
        trial="trial",
    )


def _decisions() -> tuple[StudyQCDecision, ...]:
    return (
        StudyQCDecision(
            issue_code="coordinate_nonfinite",
            action="retain with explicit missingness handling",
            rationale="Coordinate non-finiteness is preserved for planned sensitivity analysis.",
            diagnostic_ids=("D000001", "D000003", "D000005"),
        ),
        StudyQCDecision(
            issue_code="timestamp_duplicate",
            action="retain",
            rationale="The duplicated time points are documented and retained for this fixture.",
            diagnostic_ids=("D000002", "D000004"),
        ),
        StudyQCDecision(
            issue_code="timestamp_decreasing",
            action="review ordering before time-dependent analysis",
            rationale="The affected trial requires an explicit ordering decision downstream.",
            diagnostic_ids=("D000006",),
        ),
    )


def test_diagnostics_expose_row_and_group_level_evidence() -> None:
    diagnostics = study_qc_diagnostics(_study())

    assert list(diagnostics.columns) == [
        "diagnostic_id",
        "scope",
        "issue_code",
        "detail_code",
        "row_position",
        "participant",
        "trial",
        "timestamp",
        "message",
    ]
    assert diagnostics["diagnostic_id"].tolist() == [
        "D000001",
        "D000002",
        "D000003",
        "D000004",
        "D000005",
        "D000006",
    ]
    assert diagnostics["detail_code"].tolist() == [
        "x_missing",
        "timestamp_duplicate",
        "x_infinite",
        "timestamp_duplicate",
        "y_missing",
        "timestamp_decreasing",
    ]
    group_row = diagnostics.iloc[-1]
    assert group_row["scope"] == "group"
    assert group_row["participant"] == "p2"
    assert group_row["trial"] == "b"
    assert pd.isna(group_row["row_position"])


def test_qc_audit_is_deterministic_and_verifiable() -> None:
    first = build_study_qc_audit(_study(), decisions=_decisions())
    second = build_study_qc_audit(_study(), decisions=_decisions())

    assert isinstance(first, StudyQCAudit)
    assert first.manifest["schema"] == STUDY_QC_SCHEMA
    assert first.study_fingerprint == second.study_fingerprint
    assert first.audit_fingerprint == second.audit_fingerprint
    assert first.manifest_fingerprint == second.manifest_fingerprint
    assert first.manifest_json() == second.manifest_json()
    assert verify_study_qc_manifest(first.manifest)
    assert verify_study_qc_audit(first)
    assert len(first.study_fingerprint) == 64
    assert len(first.audit_fingerprint) == 64


def test_study_fingerprint_ignores_unmapped_covariates_but_binds_qc_columns() -> None:
    original = build_study_qc_audit(_study())

    changed_covariate = _frame()
    changed_covariate.loc[0, "condition"] = "changed"
    covariate_audit = build_study_qc_audit(_study(changed_covariate))
    assert covariate_audit.study_fingerprint == original.study_fingerprint

    changed_gaze = _frame()
    changed_gaze.loc[0, "gx"] = 999.0
    gaze_audit = build_study_qc_audit(_study(changed_gaze))
    assert gaze_audit.study_fingerprint != original.study_fingerprint


def test_nonfinite_values_are_fingerprintable_without_being_silently_coerced() -> None:
    audit = build_study_qc_audit(_study())
    parsed = json.loads(audit.manifest_json())

    assert audit.report.infinite_x_rows == 1
    assert parsed["study"]["records_fingerprint"]
    assert parsed["report"]["infinite_x_rows"] == 1
    assert verify_study_qc_manifest(parsed)


def test_decisions_are_bound_into_audit_identity() -> None:
    original = build_study_qc_audit(_study(), decisions=_decisions())
    revised_decisions = list(_decisions())
    revised_decisions[0] = StudyQCDecision(
        issue_code="coordinate_nonfinite",
        action="exclude flagged rows",
        rationale="Alternative documented decision for provenance testing.",
        diagnostic_ids=("D000001", "D000003", "D000005"),
    )
    revised = build_study_qc_audit(_study(), decisions=revised_decisions)

    assert revised.study_fingerprint == original.study_fingerprint
    assert revised.audit_fingerprint != original.audit_fingerprint
    assert revised.decisions_frame().iloc[0]["decision_id"] == "Q000001"


def test_decisions_fail_closed_on_stale_or_mismatched_references() -> None:
    with pytest.raises(ValueError, match="unflagged issue code"):
        build_study_qc_audit(
            _study(),
            decisions=(
                StudyQCDecision(
                    issue_code="timestamp_nonfinite",
                    action="retain",
                    rationale="No such issue is present in this fixture.",
                ),
            ),
        )

    with pytest.raises(ValueError, match="unknown diagnostic_id"):
        build_study_qc_audit(
            _study(),
            decisions=(
                StudyQCDecision(
                    issue_code="coordinate_nonfinite",
                    action="review",
                    rationale="References a stale diagnostic identifier.",
                    diagnostic_ids=("D999999",),
                ),
            ),
        )

    with pytest.raises(ValueError, match="same issue_code"):
        build_study_qc_audit(
            _study(),
            decisions=(
                StudyQCDecision(
                    issue_code="coordinate_nonfinite",
                    action="review",
                    rationale="References a diagnostic from another issue family.",
                    diagnostic_ids=("D000002",),
                ),
            ),
        )


def test_invalid_decision_values_are_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported study QC issue code"):
        StudyQCDecision("not-a-code", "retain", "reason")
    with pytest.raises(ValueError, match="action"):
        StudyQCDecision("coordinate_nonfinite", " ", "reason")
    with pytest.raises(ValueError, match="rationale"):
        StudyQCDecision("coordinate_nonfinite", "retain", " ")
    with pytest.raises(ValueError, match="duplicates"):
        StudyQCDecision(
            "coordinate_nonfinite",
            "retain",
            "reason",
            ("D000001", "D000001"),
        )


def test_verification_detects_mutated_diagnostics_or_manifest() -> None:
    audit = build_study_qc_audit(_study(), decisions=_decisions())
    audit.diagnostics.loc[0, "message"] = "mutated"
    assert not verify_study_qc_audit(audit)

    clean = build_study_qc_audit(_study(), decisions=_decisions())
    clean.manifest["report"]["coordinate_issue_rows"] = 999
    assert not verify_study_qc_audit(clean)


def test_qc_artifacts_round_trip_and_detect_tampering(tmp_path) -> None:
    audit = build_study_qc_audit(_study(), decisions=_decisions())
    paths = write_study_qc_artifacts(audit, tmp_path)

    assert set(paths) == {
        "study_qc_report.json",
        "study_qc_diagnostics.csv",
        "study_qc_decisions.csv",
        "study_qc_audit.json",
        "study_qc_artifacts.json",
    }
    artifact_manifest = json.loads(paths["study_qc_artifacts.json"].read_text())
    assert artifact_manifest["schema"] == STUDY_QC_ARTIFACT_SCHEMA
    assert artifact_manifest["audit_fingerprint"] == audit.audit_fingerprint
    assert verify_study_qc_artifacts(tmp_path)

    paths["study_qc_diagnostics.csv"].write_text("tampered\n", encoding="utf-8")
    assert not verify_study_qc_artifacts(tmp_path)


def test_clean_audit_exports_empty_diagnostics_and_decision_tables(tmp_path) -> None:
    frame = pd.DataFrame(
        {
            "pid": ["p1", "p1"],
            "trial": ["a", "a"],
            "time": [0.0, 1.0],
            "gx": [100.0, 101.0],
            "gy": [50.0, 51.0],
        }
    )
    audit = build_study_qc_audit(_study(frame))

    assert audit.report.status == "pass"
    assert audit.diagnostics.empty
    assert audit.decisions_frame().empty
    write_study_qc_artifacts(audit, tmp_path)
    assert verify_study_qc_artifacts(tmp_path)


def test_publication_metadata_binds_qc_identity_without_schema_change() -> None:
    audit = build_study_qc_audit(_study(), decisions=_decisions())
    qc_metadata = study_qc_publication_metadata(audit)

    assert qc_metadata["schema"] == STUDY_QC_PUBLICATION_LINK_SCHEMA
    assert qc_metadata["status"] == "review"
    assert qc_metadata["audit_fingerprint"] == audit.audit_fingerprint

    results = pd.DataFrame(
        {
            "method": ["hard", "probabilistic"],
            "estimate": [9.5, 10.2],
        }
    )
    rule = ConclusionRule(
        relative_tolerance=0.20,
        require_sign=True,
        minimum_recovery_fraction=0.50,
    )
    unbound = build_conclusion_audit_bundle(
        results,
        10.0,
        rule,
        title="QC provenance fixture",
        endpoint="dwell contrast",
        source_description="synthetic fixture",
    )
    bound = build_conclusion_audit_bundle(
        results,
        10.0,
        rule,
        title="QC provenance fixture",
        endpoint="dwell contrast",
        source_description="synthetic fixture",
        metadata={"study_qc": qc_metadata},
    )

    assert bound.manifest["schema"] == "gazeaudit-publication-audit-v1"
    assert bound.scientific_fingerprint != unbound.scientific_fingerprint
    assert bound.manifest["metadata"]["study_qc"] == qc_metadata
    assert verify_publication_audit_bundle(bound)


def test_publication_metadata_rejects_mutated_qc_audit() -> None:
    audit = build_study_qc_audit(_study(), decisions=_decisions())
    audit.diagnostics.loc[0, "message"] = "mutated"

    with pytest.raises(ValueError, match="does not match its manifest"):
        study_qc_publication_metadata(audit)
