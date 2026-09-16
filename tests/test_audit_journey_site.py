from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_homepage_audit_journey_exposes_six_traceable_stages() -> None:
    script = _text("assets/js/landing.js")

    assert "addAuditJourney" in script
    assert "data-audit-journey" in script
    assert "Six-stage practical audit journey" in script
    for stage in (
        "Map the study explicitly",
        "Inspect structural conditions",
        "Record researcher actions",
        "Define defensible alternatives",
        "Inspect robustness and sensitivity",
        "Save the whole evidence bundle",
    ):
        assert stage in script


def test_homepage_audit_journey_names_complete_demo_bundle() -> None:
    script = _text("assets/js/landing.js")

    for artifact in (
        "study-qc/",
        "specifications.csv",
        "specification-curve.csv",
        "effect-stability.csv",
        "marginal-sensitivity.csv",
        "pairwise-sensitivity.csv",
    ):
        assert artifact in script

    command = "python examples/first_real_audit.py --output-dir demo-audit"
    assert command in script
    assert "/docs/guides/audit-output-bundle/" in script
    assert "/docs/examples/first-real-audit/" in script


def test_audit_journey_preserves_scientific_boundary() -> None:
    script = _text("assets/js/landing.js")
    guide = _text("docs/guides/audit-output-bundle.md")

    assert "not universal cutoffs" in script
    assert "do not constitute validation evidence" in script
    assert "not an automatic verdict" in guide
    assert "not causal variance decompositions" in guide
    assert "not validation evidence for a real study" in guide


def test_output_bundle_guide_is_searchable_and_in_guide_taxonomy() -> None:
    guide = _text("docs/guides/audit-output-bundle.md")
    index = _text("docs/guides/index.md")

    for metadata in (
        "title: Understanding the audit output bundle",
        "permalink: /docs/guides/audit-output-bundle/",
        "search_category: Guides",
        "search_keywords:",
    ):
        assert metadata in guide

    assert "Understanding the audit output bundle" in index
    assert "audit-output-bundle/" in index


def test_audit_journey_has_responsive_visual_contracts() -> None:
    style = _text("assets/css/onboarding.css")

    for contract in (
        ".audit-journey-grid",
        ".audit-journey-step",
        ".audit-run-panel",
        ".audit-output-list",
        "@media (max-width: 980px)",
        "@media (max-width: 820px)",
        "@media (max-width: 520px)",
    ):
        assert contract in style
