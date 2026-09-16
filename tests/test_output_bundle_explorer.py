from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_bundle_guide_loads_dedicated_assets() -> None:
    guide = _text("docs/guides/audit-output-bundle.md")

    assert "/assets/css/output-bundle.css" in guide
    assert "/assets/js/output-bundle.js" in guide
    assert "data-bundle-explorer" in guide


def test_bundle_explorer_governs_all_six_documented_artifacts() -> None:
    guide = _text("docs/guides/audit-output-bundle.md")

    artifacts = (
        "study-qc/",
        "specifications.csv",
        "specification-curve.csv",
        "effect-stability.csv",
        "marginal-sensitivity.csv",
        "pairwise-sensitivity.csv",
    )
    for artifact in artifacts:
        assert f'data-bundle-name="{artifact}"' in guide

    assert guide.count("data-bundle-item") == 6
    assert guide.count('role="tab"') == 6
    assert 'role="tabpanel"' in guide


def test_bundle_explorer_keeps_scientific_boundaries_explicit() -> None:
    guide = _text("docs/guides/audit-output-bundle.md")

    boundary_phrases = (
        "does not define universal exclusion rules",
        "does not identify a preferred specification",
        "Empirical quantiles are not confidence intervals",
        "not posterior probabilities, confidence statements, or causal evidence",
        "not causal variance decompositions",
        "does not by itself establish a generalisable interaction",
        "does not rank artifacts by scientific importance",
    )
    for phrase in boundary_phrases:
        assert phrase in guide


def test_bundle_explorer_keyboard_contract_is_accessible() -> None:
    script = _text("assets/js/output-bundle.js")

    for contract in (
        "aria-selected",
        "tabIndex",
        "ArrowDown",
        "ArrowRight",
        "ArrowUp",
        "ArrowLeft",
        "Home",
        "End",
        "aria-labelledby",
    ):
        assert contract in script


def test_bundle_copy_supports_clipboard_and_fallback() -> None:
    script = _text("assets/js/output-bundle.js")

    assert "navigator.clipboard?.writeText" in script
    assert "document.execCommand('copy')" in script
    assert "data-bundle-status" in script
    assert "copyButton.dataset.copyValue" in script


def test_bundle_explorer_styles_are_responsive_and_accessible() -> None:
    css = _text("assets/css/output-bundle.css")

    for selector in (
        ".bundle-explorer",
        ".bundle-item",
        '.bundle-item[aria-selected="true"]',
        ".bundle-explorer-panel",
        ".bundle-panel-grid",
        ".bundle-panel-block-boundary",
    ):
        assert selector in css

    assert "@media (max-width: 780px)" in css
    assert "@media (max-width: 560px)" in css
    assert "@media (forced-colors: active)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
