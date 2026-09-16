from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _page() -> str:
    return (ROOT / "docs/case-studies/index.md").read_text(encoding="utf-8")


def test_evidence_map_preserves_three_frozen_statuses_and_boundaries() -> None:
    page = _page()

    for status in ("incomplete", "robust_negative", "materially_fragile"):
        assert f"`{status}`" in page

    for boundary in (
        "not dataset scores",
        "Does not establish:",
        "population confidence interval",
        "Does not establish:</strong> a sign reversal",
        "did not satisfy its predeclared completeness prerequisite",
    ):
        assert boundary in page


def test_evidence_map_reuses_only_governed_observed_figures() -> None:
    page = _page()

    figures = (
        "/assets/images/gazebase-completeness.svg",
        "/assets/images/korthals-effect.svg",
        "/assets/images/pedrotti-sampling-sensitivity.svg",
    )
    for figure in figures:
        assert figure in page

    assert page.count('<figure class="plot-card evidence-figure">') == 3
    assert page.count('loading="lazy"') == 3


def test_evidence_map_exposes_protocol_perturbation_endpoint_and_rule() -> None:
    page = _page()

    for heading in (
        "Compare the audits before comparing the labels",
        "Audit axis",
        "Frozen target",
        "Declared variation",
        "Frozen decision rule",
        "Choose a case by methodological question",
        "Read the programme in three layers",
    ):
        assert heading in page

    for scientific_contract in (
        "fixed cohort of 322 participants",
        "2,000 prespecified Monte Carlo draws",
        "20% relative magnitude deviation",
        "125, 100, and 50 Hz",
        "Every sampling-rate estimate remained negative",
    ):
        assert scientific_contract in page


def test_evidence_map_keeps_authoritative_routes_visible() -> None:
    page = _page()

    for route in (
        "/docs/VALIDATION_MATRIX.html",
        "/docs/SCIENTIFIC_METHODS.html",
        "/docs/case_studies/GAZEBASE_MULTIDETECTOR_PROTOCOL.html",
        "/docs/results/korthals2026_target_tracking_aoi_v2.html",
        "/docs/results/pedrotti_sampling_missingness_v1.html",
        "/docs/case-studies/gazebase-incomplete/",
        "/docs/case-studies/korthals-target-tracking/",
        "/docs/case-studies/pedrotti-sensitivity/",
    ):
        assert route in page
