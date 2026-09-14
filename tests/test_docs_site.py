from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_pages_configuration_is_explicit_and_excludes_repository_internals() -> None:
    config = _text("_config.yml")
    assert "baseurl: /GazeAudit" in config
    assert "theme: jekyll-theme-primer" in config
    for path in ("src", "tests", "tools", "release", "pyproject.toml", "README.md"):
        assert f"  - {path}\n" in config


def test_site_shell_exposes_core_navigation_and_accessibility_controls() -> None:
    layout = _text("_layouts/default.html")
    for contract in (
        "Skip to content",
        "data-theme-toggle",
        "data-menu-toggle",
        "data-nav-filter",
        "data-toc",
        "/assets/css/site.css",
        "/assets/js/site.js",
        "/docs/guides/",
        "/docs/examples/",
        "/docs/workflows/",
        "/docs/articles/",
    ):
        assert contract in layout


def test_required_documentation_pages_exist() -> None:
    required = [
        "index.md",
        "docs/index.md",
        "docs/getting-started.md",
        "docs/faq.md",
        "docs/guides/index.md",
        "docs/guides/aoi-uncertainty.md",
        "docs/guides/specification-space.md",
        "docs/guides/publication-audits.md",
        "docs/guides/interoperability.md",
        "docs/examples/index.md",
        "docs/examples/aoi-boundary.md",
        "docs/examples/specification-curve.md",
        "docs/examples/sampling-sensitivity.md",
        "docs/workflows/index.md",
        "docs/workflows/measurement-audit.md",
        "docs/workflows/robustness-audit.md",
        "docs/workflows/reproducible-publication.md",
        "docs/articles/index.md",
        "docs/articles/measurement-uncertainty-is-a-modeling-problem.md",
        "docs/articles/from-one-pipeline-to-a-robustness-audit.md",
        "docs/articles/how-to-read-a-fragile-result.md",
        "docs/reference/api-map.md",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    assert not missing


def test_explanatory_visuals_are_present_and_labelled_as_illustrative() -> None:
    visual_paths = [
        "assets/images/aoi-boundary-uncertainty.svg",
        "assets/images/specification-curve.svg",
        "assets/images/sensitivity-curves.svg",
        "assets/images/workflow-overview.svg",
    ]
    for path in visual_paths:
        text = _text(path)
        assert "<svg" in text
        assert "<title" in text
        assert "<desc" in text

    assert "Synthetic" in _text("assets/images/aoi-boundary-uncertainty.svg")
    assert "Synthetic" in _text("assets/images/specification-curve.svg")
    assert "Synthetic" in _text("assets/images/sensitivity-curves.svg")


def test_readme_is_a_gateway_to_public_documentation() -> None:
    readme = _text("README.md")
    assert "https://stefanosbalaskas.github.io/GazeAudit/" in readme
    assert "docs/getting-started/" in readme
    assert "docs/examples/" in readme
    assert "docs/workflows/" in readme
    assert "docs/reference/api-map/" in readme
    assert "10.5281/zenodo.22757340" in readme


def test_documentation_preserves_frozen_validation_outcomes() -> None:
    landing = _text("index.md")
    docs_hub = _text("docs/index.md")
    faq = _text("docs/faq.md")
    for text in (landing, docs_hub, faq):
        assert "incomplete" in text
        assert "robust_negative" in text or "Robust negative" in text
        assert "materially_fragile" in text or "Materially fragile" in text


def test_docs_site_verifier_is_wired_into_pr_workflow() -> None:
    workflow = _text(".github/workflows/docs-site.yml")
    assert "actions/jekyll-build-pages@v1" in workflow
    assert "python tools/check_docs_site.py _site --baseurl /GazeAudit" in workflow
    verifier = _text("tools/check_docs_site.py")
    assert "repository internals leaked into generated Pages site" in verifier
    assert "broken generated-site references" in verifier
