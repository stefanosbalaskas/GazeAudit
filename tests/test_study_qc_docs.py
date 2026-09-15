from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_study_preflight_example_executes_provenance_path() -> None:
    namespace = runpy.run_path(str(ROOT / "examples/study_preflight.py"))
    audit = namespace["build_demo_audit"]()
    summary = namespace["run_demo"]()

    assert audit.report.status == "review"
    assert audit.report.issue_codes == (
        "coordinate_nonfinite",
        "timestamp_duplicate",
    )
    assert len(audit.diagnostics) == 3
    assert len(audit.decisions) == 2
    assert audit.diagnostics["diagnostic_id"].tolist() == [
        "D000001",
        "D000002",
        "D000003",
    ]
    assert len(audit.study_fingerprint) == 64
    assert len(audit.audit_fingerprint) == 64
    assert summary["study_fingerprint"] == audit.study_fingerprint
    assert summary["audit_fingerprint"] == audit.audit_fingerprint


def test_data_onboarding_documents_qc_provenance_boundaries() -> None:
    guide = _text("docs/guides/data-onboarding.md")
    for contract in (
        "StudyQCDecision",
        "study fingerprint",
        "audit fingerprint",
        "manifest fingerprint",
        "write_study_qc_artifacts",
        "verify_study_qc_artifacts",
        "study_qc_publication_metadata",
        "Provenance is not automatic validity",
        "Only the five semantically mapped QC columns",
    ):
        assert contract in guide


def test_study_preflight_page_distinguishes_decision_from_default_rule() -> None:
    page = _text("docs/examples/study-preflight.md")
    for contract in (
        "These actions are illustrative, not recommended defaults",
        "D000001",
        "D000002",
        "D000003",
        "The publication schema itself does not change",
        "Editing one exported payload causes verification to fail",
    ):
        assert contract in page


def test_publication_guide_binds_qc_through_existing_metadata_schema() -> None:
    guide = _text("docs/guides/publication-audits.md")
    for contract in (
        "study_qc_publication_metadata",
        'metadata={"study_qc": qc_metadata}',
        "gazeaudit-publication-audit-v1",
        "backward-compatible",
        "changing the bound QC audit changes the publication scientific fingerprint",
    ):
        assert contract in guide


def test_api_map_exposes_study_qc_provenance_surface() -> None:
    page = _text("docs/reference/api-map.md")
    for name in (
        "study_qc_diagnostics",
        "StudyQCDecision",
        "build_study_qc_audit",
        "StudyQCAudit",
        "verify_study_qc_audit",
        "write_study_qc_artifacts",
        "verify_study_qc_artifacts",
        "study_qc_publication_metadata",
        "STUDY_QC_ARTIFACT_SCHEMA",
    ):
        assert f"`{name}`" in page


def test_generated_search_sources_qc_provenance_terms_from_page_metadata() -> None:
    onboarding = _text("docs/guides/data-onboarding.md")
    example = _text("docs/examples/study-preflight.md")
    publication = _text("docs/guides/publication-audits.md")
    search = _text("assets/search-index.json")

    assert "search_keywords:" in onboarding
    assert "fingerprint" in onboarding
    assert "decisions" in onboarding
    assert "search_keywords:" in example
    assert "StudyQCAudit" in example
    assert "search_keywords:" in publication
    assert "metadata" in publication
    assert "item.search_keywords" in search
    assert "search_keywords | strip | jsonify" in search
