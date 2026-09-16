from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_code_tools_are_loaded_after_core_site_javascript() -> None:
    layout = _text("_layouts/default.html")

    site_script = layout.index("/assets/js/site.js")
    code_tools_script = layout.index("/assets/js/code-tools.js")
    gallery_script = layout.index("/assets/js/gallery.js")

    assert site_script < code_tools_script < gallery_script
    assert "/assets/css/code-tools.css" in layout


def test_project_starter_is_in_persistent_docs_navigation() -> None:
    layout = _text("_layouts/default.html")

    assert "'/docs/guides/project-starter/' | relative_url" in layout
    assert ">Project starter</a>" in layout


def test_code_copy_uses_clipboard_api_with_selection_preserving_fallback() -> None:
    script = _text("assets/js/code-tools.js")

    for contract in (
        "navigator.clipboard?.writeText",
        "document.execCommand('copy')",
        "selection.rangeCount",
        "cloneRange()",
        "selection.removeAllRanges()",
        "activeElement.focus({ preventScroll: true })",
    ):
        assert contract in script


def test_code_copy_announces_state_and_derives_only_known_language_labels() -> None:
    script = _text("assets/js/code-tools.js")

    for contract in (
        "role', 'status'",
        "aria-live', 'polite'",
        "aria-describedby",
        "Code copied to clipboard.",
        "Automatic copy failed. Select the code and copy it manually.",
    ):
        assert contract in script

    for label in ("Python", "Shell", "JSON", "YAML", "R"):
        assert f"'{label}'" in script

    assert "startsWith('language-')" in script


def test_code_tool_styles_cover_mobile_forced_colours_and_reduced_motion() -> None:
    css = _text("assets/css/code-tools.css")

    for selector in (
        ".has-code-tools",
        ".code-language",
        '[data-copy-state="success"]',
        '[data-copy-state="error"]',
    ):
        assert selector in css

    assert "@media (max-width: 520px)" in css
    assert "@media (forced-colors: active)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
