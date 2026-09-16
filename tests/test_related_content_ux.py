from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_related_content_reuses_governed_search_index() -> None:
    script = _text("assets/js/search-tools.js")

    for contract in (
        "const relatedKindOrder",
        "const relatedHubPaths",
        "const relatedStopWords",
        "const renderRelated",
        "loadIndex().then(renderRelated)",
        "document.querySelector('.doc-article')",
        "article?.querySelector('[data-page-pagination]')",
    ):
        assert contract in script


def test_related_content_is_deterministic_and_excludes_current_page() -> None:
    script = _text("assets/js/search-tools.js")

    assert "normalisePath(window.location.pathname)" in script
    assert "normalisePath(item.url) !== currentPath" in script
    assert (
        ".sort((a, b) => b.score - a.score || "
        "a.item.title.localeCompare(b.item.title))"
    ) in script
    assert ".slice(0, 4)" in script
    assert "relatedHubPaths.has(currentPath)" in script


def test_related_navigation_does_not_present_scientific_recommendations() -> None:
    script = _text("assets/js/search-tools.js")

    assert "This is navigation support, not a scientific recommendation." in script
    assert "Related documentation for this topic" in script
    assert "Continue exploring" in script


def test_related_content_escapes_index_strings_before_rendering() -> None:
    script = _text("assets/js/search-tools.js")

    for field in (
        "item.kind || 'Documentation'",
        "item.category",
        "item.title",
        "item.description",
    ):
        assert f"escapeHtml({field})" in script


def test_related_content_has_accessible_section_and_card_contracts() -> None:
    script = _text("assets/js/search-tools.js")

    for contract in (
        "data.relatedContent = ''",
        "aria-labelledby",
        "aria-describedby",
        "related-content-grid",
        "related-content-card",
        "related-content-kind",
        "related-content-cta",
    ):
        assert contract in script


def test_related_content_styles_cover_responsive_and_accessibility_modes() -> None:
    css = _text("assets/css/search-tools.css")

    for selector in (
        ".related-content",
        ".related-content-head",
        ".related-content-grid",
        ".related-content-card",
        ".related-content-kind",
        ".related-content-cta",
    ):
        assert selector in css

    assert "@media (max-width: 760px)" in css
    assert "grid-template-columns: 1fr" in css
    assert "@media (forced-colors: active)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
