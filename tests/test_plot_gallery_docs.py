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
    assert "data-gallery-search" in page
    assert "tools/generate_plot_gallery.py" in page
    assert "src/gazeaudit/plotting.py" in page
    assert "deterministic synthetic demonstration data" in page
    for filename in EXPECTED:
        assert filename in page


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
