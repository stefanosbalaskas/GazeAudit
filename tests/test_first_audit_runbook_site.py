from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_project_starter_is_a_searchable_governed_guide() -> None:
    starter = _text("docs/guides/project-starter.md")
    guide_index = _text("docs/guides/index.md")
    first_audit = _text("docs/guides/first-real-audit.md")

    assert "permalink: /docs/guides/project-starter/" in starter
    assert "search_category: Guides" in starter
    assert "project-starter/" in guide_index
    assert "'/docs/guides/project-starter/' | relative_url" in first_audit


def test_first_audit_runbook_exposes_prepare_run_verify_before_long_form_steps() -> None:
    guide = _text("docs/guides/first-real-audit.md")

    runbook = guide.index("## Runbook: prepare, run, verify")
    numbered_steps = guide.index("## 1. Install the release you intend to report")
    assert runbook < numbered_steps

    for label in ("01 · Prepare", "02 · Run", "03 · Verify"):
        assert label in guide

    for column in (
        "participant",
        "trial",
        "timestamp",
        "x",
        "y",
        "condition",
        "quality",
    ):
        assert f"<code>{column}</code>" in guide


def test_project_starter_preserves_complete_evidence_bundle_and_scientific_boundary() -> None:
    starter = _text("docs/guides/project-starter.md")

    for artifact in (
        "study-qc/",
        "specifications.csv",
        "specification-curve.csv",
        "effect-stability.csv",
        "marginal-sensitivity.csv",
        "pairwise-sensitivity.csv",
    ):
        assert artifact in starter

    for contract in (
        "Project structure is not a scientific protocol.",
        "Do not inherit demo defaults by convenience.",
        "Empirical specification quantiles are not confidence intervals",
        "do not make the analysis scientifically appropriate by itself",
    ):
        assert contract in starter


def test_first_real_audit_keeps_existing_scientific_guardrails() -> None:
    guide = _text("docs/guides/first-real-audit.md")

    for contract in (
        "not recommended universal cutoffs",
        "Structural QC is not scientific validity",
        "Do not expand the space after seeing",
        "Empirical specification quantiles are **not confidence intervals**",
    ):
        assert contract in guide


def test_runbook_visuals_have_responsive_contracts() -> None:
    css = _text("assets/css/practical-workspace.css")

    for selector in (
        ".first-audit-runbook",
        ".runbook-step",
        ".schema-chip-grid",
        ".artifact-grid",
    ):
        assert selector in css

    assert "grid-template-columns: repeat(3, minmax(0, 1fr));" in css
    assert "@media (max-width: 720px)" in css
    assert ".first-audit-runbook," in css
    assert ".artifact-grid" in css
