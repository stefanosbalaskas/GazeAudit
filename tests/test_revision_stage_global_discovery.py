from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAVIGATION = ROOT / "assets" / "js" / "navigation.js"
STYLES = ROOT / "assets" / "css" / "revision-discovery.css"
GUIDE = ROOT / "docs" / "guides" / "revision-route-map.md"
EXAMPLE = ROOT / "docs" / "examples" / "revision-round-scenarios.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_project_stage_router_exposes_five_research_stages_and_revision_route() -> None:
    text = _read(NAVIGATION)
    for stage in (
        "Plan the study",
        "Audit the data",
        "Interpret results",
        "Revise after review",
        "Finalize handoff",
    ):
        assert stage in text

    assert "data-project-stage-tab" in text
    assert "data-project-stage-panel" in text
    assert "new URLSearchParams(window.location.search).get('stage')" in text
    assert "['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End']" in text


def test_revision_navigation_is_promoted_across_desktop_mobile_and_docs_sidebar() -> None:
    text = _read(NAVIGATION)
    assert "Peer-review revision toolkit" in text
    assert "Peer-review revision" in text
    assert "Revision route map" in text
    assert "Revision-package quickstart" in text
    assert "data-primary-nav" in text
    assert "mobile-nav-priority" in text
    assert "data-docs-nav" in text
    assert "Peer review" in text


def test_project_stage_router_keeps_scientific_judgement_researcher_owned() -> None:
    text = _read(NAVIGATION)
    boundary = (
        "It does not decide whether a reviewer request, threshold, endpoint, analysis, "
        "or interpretation is scientifically justified."
    )
    assert boundary in text


def test_revision_route_map_preserves_temporal_denominators_and_failures() -> None:
    text = _read(GUIDE)
    for category in (
        "`documentation_clarification`",
        "`correction`",
        "`sensitivity_amendment`",
        "`analytical_amendment`",
        "`endpoint_amendment`",
        "`measurement_amendment`",
    ):
        assert category in text

    assert "8 / 8 submitted + 4 / 4 post-review" in text
    assert "3 successful / 4 valid" in text
    assert "<code>3 / 4</code>, not <code>3 / 3</code>" in text
    assert "structural provenance only" in text


def test_revision_round_scenarios_cover_clarification_amendment_failure_and_endpoint() -> None:
    text = _read(EXAMPLE)
    for scenario in (
        "Scenario A — clarification, no rerun",
        "Scenario B — reviewer-requested sensitivity amendment",
        "Scenario C — one valid post-review branch fails",
        "Scenario D — different endpoint",
        "Scenario E — correction rather than amendment",
    ):
        assert scenario in text

    assert "E1 submitted: 8 / 8" in text
    assert "E1 post-review sensitivity amendment: 4 / 4" in text
    assert "amendment execution: 3 / 4" in text
    assert "E2 post-review endpoint amendment: separate endpoint record" in text
    assert "gazeaudit-revision-package validate --root revision-package" in text


def test_new_revision_material_is_synthetic_and_preserves_frozen_outcomes() -> None:
    guide = _read(GUIDE)
    example = _read(EXAMPLE)
    for text in (guide, example):
        assert "synthetic teaching material" in text
        assert "GazeBase `incomplete`" in text
        assert "Korthals `robust_negative`" in text
        assert "Pedrotti/de Chambrier `materially_fragile`" in text


def test_revision_discovery_styles_cover_focus_mobile_and_reduced_motion() -> None:
    text = _read(STYLES)
    assert ".project-stage-tab:focus-visible" in text
    assert "@media (max-width: 840px)" in text
    assert "@media (max-width: 560px)" in text
    assert "@media (prefers-reduced-motion: reduce)" in text
