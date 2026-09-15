from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_accessibility_checker_covers_core_generated_html_contracts() -> None:
    checker = _text("tools/check_accessibility.py")
    for contract in (
        "duplicate ids",
        "aria-controls",
        "aria-labelledby",
        "aria-describedby",
        "image missing alt attribute",
        "dialog(s) missing accessible name",
        "button(s) have no accessible name",
        "html element has no lang",
        "expected exactly one main landmark",
        "skip link does not target #main-content",
        "ACCESSIBILITY VERIFY: PASS",
    ):
        assert contract in checker


def test_docs_site_workflow_runs_accessibility_after_generated_site_verification() -> None:
    workflow = _text(".github/workflows/docs-site.yml")
    structural = workflow.index("python tools/check_docs_site.py _site --baseurl /GazeAudit")
    accessibility = workflow.index("python tools/check_accessibility.py _site")
    assert structural < accessibility
    assert '"tools/check_accessibility.py"' in workflow
    assert '"tests/test_accessibility_contracts.py"' in workflow


def test_homepage_planner_enhancement_is_progressive_and_governed() -> None:
    script = _text("assets/js/landing.js")
    style = _text("assets/css/landing-planner.css")
    assert "fetch(plannerIndexUrl)" in script
    assert "Homepage preset references unknown planner ids" in script
    assert "router.parentNode.insertBefore(section, router)" in script
    assert "data-planner-preset" in script
    assert "?plan=" in script
    assert "They do not diagnose your data" in script
    assert "planner URL records navigation choices, not a scientific conclusion" in script
    assert "prefers-reduced-motion" in style
    assert ":focus-visible" in style


def test_homepage_presets_reference_only_governed_planner_choices() -> None:
    script = _text("assets/js/landing.js")
    planner = _text("_data/planner.yml")
    for choice in (
        "incoming-data",
        "aoi-boundary",
        "analysis-choices",
        "sampling-risk",
        "missingness-risk",
        "publication-record",
    ):
        assert choice in script
        assert f"- id: {choice}" in planner
