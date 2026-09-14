from __future__ import annotations

import json
import runpy
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


def test_site_shell_exposes_navigation_search_and_accessibility_controls() -> None:
    layout = _text("_layouts/default.html")
    for contract in (
        "Skip to content",
        "data-theme-toggle",
        "data-menu-toggle",
        "data-nav-filter",
        "data-toc",
        "data-search-open",
        "data-search-dialog",
        "data-site-search",
        "data-breadcrumbs",
        "data-page-pagination",
        "data-reading-progress",
        'role="status"',
        'aria-describedby="site-search-help"',
        "/assets/css/site.css",
        "/assets/css/enhancements.css",
        "/assets/js/site.js",
        "/assets/search-index.json",
        "/docs/guides/",
        "/docs/guides/reporting-robustness/",
        "/docs/examples/",
        "/docs/examples/end-to-end-robustness/",
        "/docs/workflows/",
        "/docs/case-studies/",
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
        "docs/guides/reporting-robustness.md",
        "docs/guides/publication-audits.md",
        "docs/guides/interoperability.md",
        "docs/examples/index.md",
        "docs/examples/end-to-end-robustness.md",
        "docs/examples/aoi-boundary.md",
        "docs/examples/specification-curve.md",
        "docs/examples/sampling-sensitivity.md",
        "examples/end_to_end_robustness.py",
        "docs/workflows/index.md",
        "docs/workflows/measurement-audit.md",
        "docs/workflows/robustness-audit.md",
        "docs/workflows/reproducible-publication.md",
        "docs/case-studies/index.md",
        "docs/case-studies/gazebase-incomplete.md",
        "docs/case-studies/korthals-target-tracking.md",
        "docs/case-studies/pedrotti-sensitivity.md",
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
        "assets/images/end-to-end-robustness.svg",
    ]
    for path in visual_paths:
        text = _text(path)
        assert "<svg" in text
        assert "<title" in text
        assert "<desc" in text

    assert "Synthetic" in _text("assets/images/aoi-boundary-uncertainty.svg")
    assert "Synthetic" in _text("assets/images/specification-curve.svg")
    assert "Synthetic" in _text("assets/images/sensitivity-curves.svg")
    assert "Synthetic" in _text("assets/images/end-to-end-robustness.svg")


def test_observed_evidence_visuals_are_bound_to_frozen_case_values() -> None:
    gazebase = _text("assets/images/gazebase-completeness.svg")
    assert "322/322" in gazebase
    assert "0/322" in gazebase
    assert "95% gate" in gazebase

    korthals = _text("assets/images/korthals-effect.svg")
    assert "−0.09864" in korthals
    assert "−0.07401" in korthals
    assert "2,000" in korthals

    sampling = _text("assets/images/pedrotti-sampling-sensitivity.svg")
    assert "Reference −75.38" in sampling
    for rate in ("500 Hz", "250 Hz", "125 Hz", "100 Hz", "50 Hz"):
        assert rate in sampling

    missingness = _text("assets/images/pedrotti-missingness-recovery.svg")
    assert "MCAR within trial" in missingness
    assert "single block" in missingness

    for text in (gazebase, korthals, sampling, missingness):
        assert "<title" in text
        assert "<desc" in text
        assert "Synthetic" not in text


def test_case_studies_preserve_authoritative_interpretation_boundaries() -> None:
    gazebase = _text("docs/case-studies/gazebase-incomplete.md")
    assert "`incomplete`" in gazebase
    assert "NH" in gazebase and "REMoDNaV" in gazebase
    assert "95%" in gazebase

    korthals = _text("docs/case-studies/korthals-target-tracking.md")
    assert "`robust_negative`" in korthals
    assert "not a population confidence interval" in korthals
    assert "All 2,000 draws were below zero" in korthals

    pedrotti = _text("docs/case-studies/pedrotti-sensitivity.md")
    assert "`materially_fragile`" in pedrotti
    assert "Do not paraphrase this as sign reversal" in pedrotti
    assert "−75.3781404722" in pedrotti


def test_end_to_end_example_executes_full_public_robustness_path() -> None:
    namespace = runpy.run_path(str(ROOT / "examples/end_to_end_robustness.py"))
    audit = namespace["run_demo"]()

    results = audit["results"]
    assert audit["space"].size == 12
    assert len(results) == 12
    assert list(results.columns) == [
        "spec_id",
        "min_quality",
        "sample_stride",
        "aoi_radius",
        "estimate",
    ]
    assert results["estimate"].notna().all()
    assert (results["estimate"] > 0).any()
    assert (results["estimate"] < 0).any()
    assert (results["estimate"] == 0).any()
    assert len(audit["curve"]) == 12
    assert int(audit["stability"]["n_specifications"]) == 12
    assert set(audit["marginal"]["factor"]) == {
        "min_quality",
        "sample_stride",
        "aoi_radius",
    }
    assert len(audit["pairwise"]) == 3


def test_reporting_guide_preserves_descriptive_boundaries() -> None:
    guide = _text("docs/guides/reporting-robustness.md")
    for contract in (
        "empirical specification quantiles",
        "not confidence intervals",
        "not causal",
        "not a replacement for a fitted factorial model",
        "protocol-bound",
    ):
        assert contract in guide


def test_accessibility_enhancements_cover_focus_and_motion_preferences() -> None:
    css = _text("assets/css/enhancements.css")
    assert ":focus-visible" in css
    assert "scroll-margin-top" in css
    assert "prefers-reduced-motion: reduce" in css
    assert "forced-colors: active" in css


def test_search_index_is_structured_and_points_to_core_documentation() -> None:
    index = json.loads(_text("assets/search-index.json"))
    assert isinstance(index, list)
    assert len(index) >= 27
    urls = {item["url"] for item in index}
    for item in index:
        assert {"title", "category", "url", "description", "keywords"} <= item.keys()
        assert item["title"].strip()
        assert item["url"].startswith("/docs/")
    for url in (
        "/docs/getting-started/",
        "/docs/examples/end-to-end-robustness/",
        "/docs/guides/reporting-robustness/",
        "/docs/case-studies/",
        "/docs/case-studies/gazebase-incomplete/",
        "/docs/case-studies/korthals-target-tracking/",
        "/docs/case-studies/pedrotti-sensitivity/",
        "/docs/reference/api-map/",
    ):
        assert url in urls


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
    assert "search index target failures" in verifier
