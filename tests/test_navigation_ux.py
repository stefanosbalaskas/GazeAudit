from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_primary_navigation_exposes_current_page_state_contract() -> None:
    layout = _text("_layouts/default.html")
    script = _text("assets/js/site.js")
    style = _text("assets/css/onboarding.css")

    assert "data-primary-nav" in layout
    assert "data-mobile-primary-nav" in layout
    assert "markCurrentNavigation" in script
    assert "currentPath.startsWith(target)" in script
    assert "aria-current" in script
    assert '.top-nav a[aria-current="page"]' in style
    assert '.mobile-menu a[aria-current="page"]' in style


def test_mobile_header_navigation_closes_cleanly() -> None:
    script = _text("assets/js/site.js")
    assert "closeMobileMenu" in script
    assert "event.target.closest('a')" in script
    assert "event.key === 'Escape'" in script
    assert "menuToggle?.focus()" in script


def test_documentation_pages_expose_copy_link_and_exact_source_route() -> None:
    layout = _text("_layouts/default.html")
    script = _text("assets/js/site.js")
    style = _text("assets/css/onboarding.css")

    for contract in (
        "docs_source_ref",
        "doc-tools",
        "data-copy-page-link",
        "Copy page link",
        "View source",
        "GazeAudit/blob/{{ docs_source_ref }}/{{ page.path }}",
    ):
        assert contract in layout

    assert "window.location.href.split('#')[0]" in script
    assert "navigator.clipboard.writeText(pageUrl)" in script
    assert ".site-js .doc-tool-copy" in style


def test_onboarding_styles_are_loaded_globally_through_existing_gallery_bundle() -> None:
    gallery = _text("assets/css/gallery.css")
    onboarding = ROOT / "assets" / "css" / "onboarding.css"
    assert onboarding.is_file()
    assert '@import url("./onboarding.css");' in gallery


def test_homepage_practical_start_routes_are_explicit_and_non_diagnostic() -> None:
    script = _text("assets/js/landing.js")
    style = _text("assets/css/onboarding.css")

    for contract in (
        "addPracticalStart",
        "/docs/guides/first-real-audit/",
        "/docs/getting-started/",
        "/docs/planner/",
        "I have gaze data",
        "I am learning the package",
        "I am designing an audit",
        "Thresholds, exclusions, AOIs, perturbations, endpoints, and validity judgements remain researcher-owned",
        "Audit your own data →",
    ):
        assert contract in script

    assert ".practical-start-grid" in style
    assert ".practical-start-card.is-primary" in style
    assert "@media (max-width: 820px)" in style
