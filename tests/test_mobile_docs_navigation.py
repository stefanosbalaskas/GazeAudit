from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_mobile_docs_navigation_is_progressive_enhancement() -> None:
    script = _text("assets/js/site.js")
    style = _text("assets/css/enhancements.css")
    assert "body.classList.add('site-js')" in script
    assert "data-mobile-doc-dock" in script
    assert "data-mobile-doc-dialog" in script
    assert "cloneNode(true)" in script
    assert ".site-js .docs-sidebar" in style
    assert "@media (max-width: 820px)" in style


def test_mobile_docs_dialog_exposes_browse_toc_and_search_routes() -> None:
    script = _text("assets/js/site.js")
    for label in ("Browse docs", "On this page", "Search"):
        assert label in script
    assert "Browse documentation" in script
    assert "On this page" in script
    assert "aria-labelledby" in script
    assert "data-search-open" in script


def test_mobile_toc_reuses_generated_heading_navigation() -> None:
    script = _text("assets/js/site.js")
    assert "toc.cloneNode(true)" in script
    assert "docsNav.cloneNode(true)" in script
    assert "mobileDocContent" in script
    assert "mobileDocDialog.close()" in script


def test_mobile_navigation_keeps_no_js_sidebar_fallback() -> None:
    style = _text("assets/css/enhancements.css")
    assert ".mobile-doc-dock {" in style
    assert "display: none;" in style
    assert ".site-js .mobile-doc-dock" in style
    assert ".site-js .docs-sidebar" in style
