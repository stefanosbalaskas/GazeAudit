from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_desktop_navigation_is_task_first_and_preserves_research_routes() -> None:
    layout = _text("_layouts/default.html")

    for label in ("Use data", "Workspace", "Planner", "Evidence", "Explore"):
        assert label in layout

    for route in (
        "/docs/",
        "/docs/workspace/",
        "/docs/planner/",
        "/docs/methods/",
        "/docs/guides/",
        "/docs/examples/",
        "/docs/plots/",
        "/docs/workflows/",
        "/docs/case-studies/",
        "/docs/articles/",
        "/docs/reference/api-map/",
        "/docs/reference/site-provenance/",
        "/docs/VALIDATION_MATRIX.html",
        "/docs/guides/audit-output-bundle/",
    ):
        assert route in layout

    assert 'details class="nav-explore" data-explore-menu' in layout
    assert '<span>Learn</span>' in layout
    assert '<span>Apply</span>' in layout
    assert '<span>Reference</span>' in layout


def test_mobile_navigation_groups_routes_without_breaking_current_page_contract() -> None:
    layout = _text("_layouts/default.html")
    site_script = _text("assets/js/site.js")

    for contract in (
        "data-mobile-primary-nav",
        "mobile-nav-priority",
        "mobile-nav-groups",
        "mobile-nav-group",
        "Use your own data",
        "Evidence & case studies",
    ):
        assert contract in layout

    assert "markCurrentNavigation(document.querySelector('[data-primary-nav]'))" in site_script
    mobile_current = "markCurrentNavigation(document.querySelector('[data-mobile-primary-nav]'))"
    assert mobile_current in site_script
    assert "event.target.closest('a')" in site_script


def test_explore_menu_closes_accessibly_and_surfaces_current_group() -> None:
    script = _text("assets/js/navigation.js")

    for contract in (
        "closeExplore",
        "syncCurrentState",
        "event.key !== 'Escape'",
        "!explore.contains(event.target)",
        "event.target.closest('a')",
        "a[aria-current=\"page\"]",
        "summary.setAttribute('aria-current', 'page')",
        "summary?.focus()",
    ):
        assert contract in script


def test_navigation_assets_have_responsive_and_accessibility_contracts() -> None:
    layout = _text("_layouts/default.html")
    style = _text("assets/css/navigation.css")

    assert layout.index("/assets/js/site.js") < layout.index("/assets/js/navigation.js")
    assert "/assets/css/navigation.css" in layout

    for contract in (
        ".nav-explore-menu",
        ".mobile-nav-groups",
        "@media (max-width: 760px)",
        "@media (forced-colors: active)",
        "@media (prefers-reduced-motion: reduce)",
        '.top-nav > a[aria-current="page"]',
        '.nav-explore > summary[aria-current="page"]',
    ):
        assert contract in style
