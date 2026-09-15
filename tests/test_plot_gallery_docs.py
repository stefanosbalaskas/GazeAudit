from __future__ import annotations

import json
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


def test_gallery_page_links_every_code_generated_plot_and_source() -> None:
    page = _text("docs/plots/index.md")
    assert "data-plot-gallery" in page
    assert "data-plot-gallery-toolbar" in page
    assert "data-gallery-search" in page
    assert "data-gallery-count" in page
    assert "tools/generate_plot_gallery.py" in page
    assert "src/gazeaudit/plotting.py" in page
    assert "deterministic synthetic demonstration data" in page
    for filename in EXPECTED:
        assert filename in page


def test_gallery_exposes_public_plotting_functions_and_questions() -> None:
    page = _text("docs/plots/index.md")
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
        assert function in page
    assert "Question" in page


def test_gallery_controls_target_toolbar_and_grid_separately() -> None:
    script = _text("assets/js/gallery.js")
    assert "document.querySelector('[data-plot-gallery]')" in script
    assert "document.querySelector('[data-plot-gallery-toolbar]')" in script
    assert "toolbar.querySelector('[data-gallery-search]')" in script
    assert "toolbar.querySelectorAll('[data-gallery-filter]')" in script
    assert "data-gallery-count" in script
    assert "plots`" in script


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
