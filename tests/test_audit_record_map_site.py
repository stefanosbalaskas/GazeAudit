from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "guides" / "audit-record-map.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
WORKSPACE = ROOT / "docs" / "workspace" / "index.md"
PUBLICATION = ROOT / "docs" / "workflows" / "reproducible-publication.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_audit_record_map_has_searchable_guide_identity() -> None:
    page = _text(PAGE)

    assert "title: Audit record map" in page
    assert "permalink: /docs/guides/audit-record-map/" in page
    assert "search_category: Guide" in page
    assert "search_keywords:" in page


def test_audit_record_map_covers_full_research_lineage() -> None:
    page = _text(PAGE)

    for stage in (
        "1 · Bind the study source",
        "2 · Record researcher decisions",
        "3 · Inspect structural QC",
        "4 · Execute the declared space",
        "5 · Summarise robustness",
        "6 · Bind provenance and fingerprints",
        "7 · Write the scoped claim",
    ):
        assert stage in page

    for artifact in (
        "study-qc/",
        "specifications.csv",
        "specification-curve.csv",
        "effect-stability.csv",
        "marginal-sensitivity.csv",
        "pairwise-sensitivity.csv",
    ):
        assert artifact in page


def test_audit_record_map_preserves_scientific_boundaries() -> None:
    page = _text(PAGE)

    for boundary in (
        "navigation, not scientific authority",
        "does not decide which thresholds",
        "not a universal exclusion rule",
        "does not identify one preferred specification",
        "not confidence intervals, posterior probabilities, or causal evidence",
        "Descriptive sensitivity is not causal variance decomposition",
        "No preferred-result shortcut",
    ):
        assert boundary in page


def test_audit_record_map_routes_to_existing_research_surfaces() -> None:
    page = _text(PAGE)

    for route in (
        "/docs/workspace/",
        "/docs/planner/",
        "/docs/guides/first-real-audit/",
        "/docs/guides/data-onboarding/",
        "/docs/guides/audit-output-bundle/",
        "/docs/workflows/reproducible-publication/",
        "/docs/case-studies/",
    ):
        assert route in page


def test_existing_hubs_link_back_to_audit_record_map() -> None:
    route = "/docs/guides/audit-record-map/"

    assert "Audit record map" in _text(GUIDES)
    assert route in _text(WORKSPACE)
    assert route in _text(PUBLICATION)


def test_audit_record_map_reuses_governed_site_components() -> None:
    page = _text(PAGE)

    for component in (
        'class="workflow-steps"',
        'class="workflow-step"',
        'class="audit-output-preview"',
        'class="audit-output-panel"',
        'class="audit-file-tree"',
        'class="card-grid"',
        'class="card"',
        'class="callout callout-info"',
        'class="callout callout-warning"',
    ):
        assert component in page
