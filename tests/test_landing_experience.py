from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_landing_exposes_five_accessible_research_tasks() -> None:
    page = _text("index.md")
    tasks = ("qc", "readiness", "uncertainty", "robustness", "publish")

    assert page.count("data-router-tab=") == 5
    assert page.count("data-router-panel=") == 5
    for task in tasks:
        assert f'id="router-tab-{task}"' in page
        assert f'aria-controls="router-panel-{task}"' in page
        assert f'data-router-tab="{task}"' in page
        assert f'id="router-panel-{task}"' in page
        assert f'aria-labelledby="router-tab-{task}"' in page
        assert f'data-router-panel="{task}"' in page


def test_landing_keeps_synthetic_visuals_separate_from_frozen_evidence() -> None:
    page = _text("index.md")

    for asset in (
        "/assets/plots/specification-curve-code.svg",
        "/assets/plots/trial-readiness.svg",
        "/assets/plots/cohort-impact.svg",
        "/assets/plots/aoi-probability-profile.svg",
        "/assets/plots/threshold-sweep.svg",
        "/assets/plots/factor-sensitivity.svg",
    ):
        assert asset in page

    assert "deterministic synthetic demonstration data" in page
    assert "synthetic demo" in page

    for asset in (
        "/assets/images/gazebase-completeness.svg",
        "/assets/images/korthals-effect.svg",
        "/assets/images/pedrotti-sampling-sensitivity.svg",
    ):
        assert asset in page

    for label in ("Incomplete", "Robust negative", "Materially fragile"):
        assert label in page
    assert "protocol-bound scientific records" in page


def test_landing_states_scientific_product_boundaries() -> None:
    page = _text("index.md")
    for contract in (
        "GazeAudit does not",
        "universal QC cutoffs",
        "automatically exclude participants",
        "favourable specification",
        "causal evidence",
    ):
        assert contract in page


def test_landing_assets_are_wired_only_for_landing_pages() -> None:
    layout = _text("_layouts/default.html")
    assert "page.page_type == 'landing'" in layout
    assert "/assets/css/landing.css" in layout
    assert "/assets/js/landing.js" in layout

    assert (ROOT / "assets/css/landing.css").is_file()
    assert (ROOT / "assets/css/landing-planner.css").is_file()
    assert (ROOT / "assets/js/landing.js").is_file()


def test_research_router_supports_keyboard_navigation_and_aria_state() -> None:
    script = _text("assets/js/landing.js")
    for contract in (
        "ArrowLeft",
        "ArrowRight",
        "ArrowUp",
        "ArrowDown",
        "Home",
        "End",
        "aria-selected",
        "tabIndex",
        "panel.hidden",
    ):
        assert contract in script


def test_landing_planner_presets_are_governed_and_non_diagnostic() -> None:
    script = _text("assets/js/landing.js")
    for preset in ("new-study", "aoi-study", "robustness-study", "publication-study"):
        assert f"id: '{preset}'" in script
    for choice in (
        "incoming-data",
        "aoi-boundary",
        "analysis-choices",
        "sampling-risk",
        "missingness-risk",
        "publication-record",
    ):
        assert choice in script
    assert "fetch(plannerIndexUrl)" in script
    assert "Plan an audit" in script
    assert "They do not diagnose your data" in script
    assert "planner URL records navigation choices, not a scientific conclusion" in script


def test_landing_has_compact_section_navigation() -> None:
    page = _text("index.md")
    assert 'class="landing-jump-nav"' in page
    assert 'aria-label="Explore the GazeAudit homepage"' in page
    for anchor in (
        "research-tasks",
        "visual-methods",
        "evidence",
        "workflow",
        "scientific-boundary",
    ):
        assert f'href="#{anchor}"' in page
        assert f'id="{anchor}"' in page


def test_featured_visuals_deep_link_to_plot_and_method_routes() -> None:
    page = _text("index.md")
    for plot_id in (
        "specification-curve",
        "trial-readiness",
        "cohort-impact",
        "aoi-probability-profile",
        "threshold-sweep",
        "factor-sensitivity",
    ):
        assert f"#plot-{plot_id}" in page
    for route in (
        "/docs/guides/analysis-readiness/",
        "/docs/guides/aoi-uncertainty/",
        "/docs/guides/specification-space/",
    ):
        assert route in page
    assert page.count('class="featured-plot-links"') == 5


def test_landing_is_task_first_not_duplicate_legacy_sections() -> None:
    page = _text("index.md")
    for heading in (
        "Choose your research task",
        "Scientific boundary",
        "Executable visual methods",
        "Frozen validation programme",
        "One auditable workflow",
    ):
        assert heading in page

    assert page.count("Frozen validation programme") == 1
    assert page.count("Code-generated plot gallery") == 0
