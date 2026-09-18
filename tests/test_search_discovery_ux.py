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


def test_search_discovery_supports_facets_and_reference_shortcuts() -> None:
    script = _text("assets/js/search-tools.js")

    for contract in (
        "data-search-facets",
        "aria-pressed",
        "data-search-kind",
        "activeKind = 'All'",
        "first real audit",
        "robustness",
        "AOI uncertainty",
        "CLI command",
        "declared valid successful",
        "publication",
    ):
        assert contract in script


def test_search_results_are_grouped_by_documentation_kind() -> None:
    script = _text("assets/js/search-tools.js")

    for contract in (
        "const groupedItems = (items, maxResults = 12, perGroup = 4)",
        "const groups = new Map()",
        "search-result-group",
        "search-result-group-head",
        "search-result-group-items",
        'aria-labelledby="${groupId}"',
        "group.total",
        "visibleCount",
    ):
        assert contract in script

    assert "escapeHtml(group.kind)" in script
    assert "group.items.map((item)" in script


def test_search_status_is_separate_from_interactive_results() -> None:
    layout = _text("_layouts/default.html")
    script = _text("assets/js/search-tools.js")
    core = _text("assets/js/site.js")

    assert 'data-search-status role="status"' in layout
    assert 'aria-live="polite"' in layout
    assert 'aria-atomic="true"' in layout
    assert 'data-search-results aria-label="Search results"' in layout
    assert "data-search-results aria-live" not in layout
    assert "document.querySelector('[data-search-status]')" in script
    assert "document.querySelector('[data-search-status]')" in core


def test_search_overlay_preserves_keyboard_result_contract() -> None:
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
    assert "Selected ${selectedResult + 1} of ${results.length}" in core


def test_zero_result_state_offers_recovery_without_scientific_inference() -> None:
    script = _text("assets/js/search-tools.js")
    css = _text("assets/css/search-tools.css")

    for contract in (
        'data-search-reset="kind"',
        'data-search-reset="query"',
        "Search all documentation types",
        "Clear query",
        "Browse Guides",
        "Browse Examples",
        "Browse Reference",
        "results.addEventListener('click'",
    ):
        assert contract in script

    assert ".search-empty-recovery" in css
    assert ".search-recovery-actions" in css


def test_search_result_strings_are_escaped_before_rendering() -> None:
    script = _text("assets/js/search-tools.js")

    assert "const escapeHtml" in script
    for field in (
        "group.kind",
        "item.category",
        "item.title",
        "item.description",
    ):
        assert f"escapeHtml({field})" in script


def test_search_styles_cover_grouping_mobile_and_accessibility_modes() -> None:
    css = _text("assets/css/search-tools.css")

    for selector in (
        ".search-facets",
        ".search-query-chip",
        ".search-result-status",
        ".search-result-group",
        ".search-result-group-head",
        ".search-result-group-items",
        '.search-facet[aria-pressed="true"]',
    ):
        assert selector in css

    assert "@media (max-width: 620px)" in css
    assert "overflow-x: auto" in css
    assert "@media (forced-colors: active)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
