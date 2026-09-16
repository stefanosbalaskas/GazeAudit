from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_search_tools_load_after_core_search_and_before_gallery() -> None:
    layout = _text("_layouts/default.html")

    core = layout.index("/assets/js/site.js")
    search = layout.index("/assets/js/search-tools.js")
    gallery = layout.index("/assets/js/gallery.js")

    assert core < search < gallery
    assert "/assets/css/search-tools.css" in layout


def test_search_index_derives_content_kind_from_governed_urls() -> None:
    template = _text("assets/search-index.json")

    expected = {
        "/docs/guides/": "Guide",
        "/docs/examples/": "Example",
        "/docs/workflows/": "Workflow",
        "/docs/methods/": "Method",
        "/docs/plots/": "Plot",
        "/docs/case-studies/": "Case study",
        "/docs/articles/": "Article",
        "/docs/reference/": "Reference",
    }
    for route, kind in expected.items():
        assert route in template
        assert f"'{kind}'" in template

    for evidence_route in (
        "/docs/results/",
        "/docs/validation/",
        "/docs/protocols/",
        "/docs/case_studies/",
    ):
        assert evidence_route in template

    assert '"kind":{{ search_kind | jsonify }}' in template
    assert "{{ search_kind }} {{ item.url }}" in template


def test_search_discovery_supports_facets_counts_and_research_shortcuts() -> None:
    script = _text("assets/js/search-tools.js")

    for contract in (
        "data-search-facets",
        "aria-pressed",
        "data-search-kind",
        "data-search-result-summary",
        "activeKind = 'All'",
        "matched.slice(0, 12)",
        "first real audit",
        "robustness",
        "AOI",
        "publication",
    ):
        assert contract in script


def test_search_overlay_preserves_core_result_and_keyboard_contract() -> None:
    script = _text("assets/js/search-tools.js")
    core = _text("assets/js/site.js")

    for contract in (
        "data-search-result",
        "is-selected",
        "data-index",
        "input.dispatchEvent(new Event('input', { bubbles: true }))",
        "input.addEventListener('focus', refresh)",
        "input.addEventListener('input', refresh)",
    ):
        assert contract in script

    assert "[data-search-result]" in core
    assert "ArrowDown" in core
    assert "ArrowUp" in core
    assert "event.key === 'Enter'" in core


def test_search_result_strings_are_escaped_before_rendering() -> None:
    script = _text("assets/js/search-tools.js")

    assert "const escapeHtml" in script
    for field in (
        "item.kind || 'Documentation'",
        "item.category",
        "item.title",
        "item.description",
    ):
        assert f"escapeHtml({field})" in script


def test_search_styles_cover_mobile_forced_colours_and_result_context() -> None:
    css = _text("assets/css/search-tools.css")

    for selector in (
        ".search-facets",
        ".search-query-chip",
        ".search-result-kind",
        '.search-facet[aria-pressed="true"]',
    ):
        assert selector in css

    assert "@media (max-width: 620px)" in css
    assert "overflow-x: auto" in css
    assert "@media (forced-colors: active)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
