from __future__ import annotations

import json
import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLOTS = ROOT / "assets" / "plots"
EXPECTED = {
    "qc-issue-profile.svg",
    "trial-readiness.svg",
    "participant-readiness.svg",
    "cohort-impact.svg",
    "repair-comparison.svg",
    "policy-tradeoffs.svg",
    "threshold-sweep.svg",
    "specification-curve-code.svg",
    "factor-sensitivity.svg",
    "missingness-sensitivity-code.svg",
    "sampling-sensitivity-code.svg",
    "gaze-trajectory-aoi.svg",
    "aoi-probability-profile.svg",
    "recovery-matrix.svg",
}


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_gallery_assets_are_generated_svg_with_accessibility_metadata() -> None:
    assert PLOTS.is_dir()
    actual = {path.name for path in PLOTS.glob("*.svg")}
    assert actual == EXPECTED
    for path in sorted(PLOTS.glob("*.svg")):
        text = path.read_text(encoding="utf-8")
        assert "<svg" in text
        assert "<title>" in text
        assert "<desc>" in text
        assert "matplotlib" in text.lower()


def test_gallery_manifest_matches_committed_assets() -> None:
    manifest = json.loads((PLOTS / "gallery-manifest.json").read_text(encoding="utf-8"))
    assert len(manifest) == 14
    assert {item["filename"] for item in manifest} == EXPECTED
    assert all(item["source"] == "tools/generate_plot_gallery.py" for item in manifest)
    assert {item["category"] for item in manifest} == {
        "readiness",
        "robustness",
        "sensitivity",
        "measurement",
    }


def test_governed_plot_catalog_matches_committed_assets() -> None:
    catalog = _text("_data/plots.yml")
    filenames = set(re.findall(r"^  filename: (.+\.svg)$", catalog, flags=re.MULTILINE))
    plot_ids = re.findall(r"^- id: ([a-z0-9-]+)$", catalog, flags=re.MULTILINE)
    next_paths = re.findall(r"^  next_path: (.+)$", catalog, flags=re.MULTILINE)
    assert filenames == EXPECTED
    assert len(plot_ids) == 14
    assert len(plot_ids) == len(set(plot_ids))
    assert len(next_paths) == 14
    assert all(path.startswith("/docs/") and path.endswith("/") for path in next_paths)
    assert catalog.count("  next_label:") == 14
    assert catalog.count("  method_ids:") == 14
    assert catalog.count("  function: plot_") == 14


def test_gallery_page_is_driven_by_governed_catalog() -> None:
    page = _text("docs/plots/index.md")
    assert "data-plot-gallery" in page
    assert "data-plot-gallery-toolbar" in page
    assert "data-gallery-search" in page
    assert "data-gallery-count" in page
    assert "data-gallery-share-status" in page
    assert "site.data.plots" in page
    assert "data-plot-index" in page
    assert 'id="plot-{{ plot.id }}"' in page
    assert "plot.method_ids" in page
    assert "plot.next_path" in page
    assert "plot.next_label" in page
    assert "data-copy-plot-link" in page
    assert "method-" in page
    assert "tools/generate_plot_gallery.py" in page
    assert "src/gazeaudit/plotting.py" in page
    assert "deterministic synthetic demonstration data" in page
    assert "assign plots =" not in page


def test_plot_index_is_generated_from_governed_catalog() -> None:
    index = _text("assets/plot-index.json")
    assert "layout: null" in index
    assert "site.data.plots | jsonify" in index


def test_gallery_exposes_public_plotting_functions_and_questions() -> None:
    catalog = _text("_data/plots.yml")
    for function in (
        "plot_qc_issue_profile",
        "plot_trial_readiness",
        "plot_participant_readiness",
        "plot_cohort_impact",
        "plot_repair_comparison",
        "plot_policy_tradeoffs",
        "plot_threshold_sweep",
        "plot_specification_curve",
        "plot_factor_sensitivity",
        "plot_sensitivity_curve",
        "plot_gaze_trajectory",
        "plot_aoi_probability_profile",
        "plot_recovery_matrix",
    ):
        assert function in catalog
    assert catalog.count("  question:") == 14


def test_gallery_controls_target_toolbar_and_grid_separately() -> None:
    script = _text("assets/js/gallery.js")
    assert "document.querySelector('[data-plot-gallery]')" in script
    assert "document.querySelector('[data-plot-gallery-toolbar]')" in script
    assert "toolbar.querySelector('[data-gallery-search]')" in script
    assert "toolbar.querySelectorAll('[data-gallery-filter]')" in script
    assert "data-gallery-count" in script
    assert "plots`" in script


def test_gallery_state_and_plot_links_are_shareable() -> None:
    script = _text("assets/js/gallery.js")
    for contract in (
        "new URLSearchParams(window.location.search)",
        "url.searchParams.set('category', category)",
        "url.searchParams.set('q', query)",
        "window.history.replaceState",
        "data-copy-plot-link",
        "navigator.clipboard?.writeText",
        "plot-${plotId}",
        "fallbackCopy",
    ):
        assert contract in script


def test_visual_navigation_styles_are_loaded_and_responsive() -> None:
    gallery_css = _text("assets/css/gallery.css")
    visual_css = _text("assets/css/visual-navigation.css")
    assert '@import url("./visual-navigation.css");' in gallery_css
    for selector in (
        ".landing-jump-nav",
        ".plot-next-step",
        ".plot-card-actions button",
        ".gallery-share-status",
        ".featured-plot-links",
    ):
        assert selector in visual_css
    assert "@media (max-width: 620px)" in visual_css
    assert "@media (prefers-reduced-motion: reduce)" in visual_css


def test_gallery_workflow_regenerates_and_checks_byte_drift() -> None:
    workflow = _text(".github/workflows/plot-gallery.yml")
    assert '"matplotlib==3.10.8"' in workflow
    assert "python tools/generate_plot_gallery.py" in workflow
    assert "git diff --exit-code -- assets/plots" in workflow


def test_gallery_generator_runs_and_declares_fourteen_outputs() -> None:
    namespace = runpy.run_path(str(ROOT / "tools" / "generate_plot_gallery.py"))
    entries = namespace["generate"]()
    assert len(entries) == 14
    assert {entry["filename"] for entry in entries} == EXPECTED
