import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    effect_stability,
    marginal_sensitivity,
    pairwise_interaction_sensitivity,
    specification_curve,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "robustness_diagnostics.yml"
JSON_SOURCE = ROOT / "assets" / "robustness-diagnostic-reference.json"
CENTER = ROOT / "docs" / "robustness-diagnostics.md"
GUIDE = ROOT / "docs" / "guides" / "robustness-diagnostics.md"
EXAMPLE = ROOT / "docs" / "examples" / "robustness-diagnostic-walkthrough.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "robustness-diagnostics.css"
JS = ROOT / "assets" / "js" / "robustness-diagnostics.js"
DOCS = ROOT / "docs" / "index.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
EXAMPLES = ROOT / "docs" / "examples" / "index.md"
REFERENCE = ROOT / "docs" / "reference" / "index.md"
COMPASS = ROOT / "docs" / "documentation-map.md"
FAQ = ROOT / "docs" / "faq.md"
README = ROOT / "README.md"
API_REFERENCE = ROOT / "assets" / "api-symbol-reference.json"
PLOTS = ROOT / "_data" / "plots.yml"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"

EXPECTED_IDS = {
    "execution-completeness",
    "specification-curve",
    "effect-stability",
    "marginal-sensitivity",
    "pairwise-sensitivity",
    "controlled-sensitivity",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _blocks() -> list[str]:
    text = _text(CATALOG)
    return ["- id: " + block for block in text.split("- id: ")[1:]]


def _field(block: str, name: str) -> str:
    match = re.search(
        rf"^  {re.escape(name)}: (.*)$",
        block,
        flags=re.MULTILINE,
    )
    assert match is not None, f"missing field {name}"
    return match.group(1).strip().strip('"')


def _results() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "spec_id": 0,
                "detector": "ivt",
                "qc_policy": "moderate",
                "aoi_mode": "hard",
                "estimate": -0.01,
            },
            {
                "spec_id": 1,
                "detector": "ivt",
                "qc_policy": "moderate",
                "aoi_mode": "probabilistic",
                "estimate": 0.02,
            },
            {
                "spec_id": 2,
                "detector": "ivt",
                "qc_policy": "strict",
                "aoi_mode": "hard",
                "estimate": 0.00,
            },
            {
                "spec_id": 3,
                "detector": "ivt",
                "qc_policy": "strict",
                "aoi_mode": "probabilistic",
                "estimate": 0.03,
            },
            {
                "spec_id": 4,
                "detector": "idt",
                "qc_policy": "moderate",
                "aoi_mode": "hard",
                "estimate": 0.01,
            },
            {
                "spec_id": 5,
                "detector": "idt",
                "qc_policy": "moderate",
                "aoi_mode": "probabilistic",
                "estimate": 0.05,
            },
            {
                "spec_id": 6,
                "detector": "idt",
                "qc_policy": "strict",
                "aoi_mode": "hard",
                "estimate": 0.02,
            },
            {
                "spec_id": 7,
                "detector": "idt",
                "qc_policy": "strict",
                "aoi_mode": "probabilistic",
                "estimate": 0.06,
            },
        ]
    )


def test_diagnostic_catalog_has_exact_governed_ids() -> None:
    blocks = _blocks()
    assert len(blocks) == 6
    assert {_field(block, "id") for block in blocks} == EXPECTED_IDS

    for block in blocks:
        for field in (
            "title:",
            "question:",
            "source:",
            "output_kind:",
            "key_fields:",
            "plot_id:",
            "api_anchor:",
            "can_answer:",
            "cannot_answer:",
            "next_path:",
            "reporting:",
        ):
            assert field in block


def test_runtime_specification_curve_matches_documented_order() -> None:
    curve = specification_curve(_results())
    assert curve["estimate"].tolist() == [
        -0.01,
        0.00,
        0.01,
        0.02,
        0.02,
        0.03,
        0.05,
        0.06,
    ]


def test_runtime_effect_stability_matches_documented_values() -> None:
    stability = effect_stability(_results())

    assert stability["n_specifications"] == 8
    assert stability["mean_estimate"] == pytest.approx(0.0225)
    assert stability["median_estimate"] == pytest.approx(0.02)
    assert stability["min_estimate"] == pytest.approx(-0.01)
    assert stability["max_estimate"] == pytest.approx(0.06)
    assert stability["q025"] == pytest.approx(-0.00825)
    assert stability["q975"] == pytest.approx(0.05825)
    assert stability["positive_fraction"] == pytest.approx(0.75)
    assert stability["negative_fraction"] == pytest.approx(0.125)
    assert stability["exact_null_fraction"] == pytest.approx(0.125)
    assert stability["sign_stability"] == pytest.approx(0.75)


def test_runtime_marginal_sensitivity_matches_documented_ranking() -> None:
    marginal = marginal_sensitivity(
        _results(),
        factors=["detector", "qc_policy", "aoi_mode"],
    )

    assert marginal["factor"].tolist() == [
        "aoi_mode",
        "detector",
        "qc_policy",
    ]
    values = dict(zip(marginal["factor"], marginal["marginal_eta2"], strict=True))
    ranges = dict(zip(marginal["factor"], marginal["level_mean_range"], strict=True))

    assert values["aoi_mode"] == pytest.approx(0.6202531645569621)
    assert values["detector"] == pytest.approx(0.3164556962025317)
    assert values["qc_policy"] == pytest.approx(0.05063291139240505)
    assert ranges["aoi_mode"] == pytest.approx(0.035)
    assert ranges["detector"] == pytest.approx(0.025)
    assert ranges["qc_policy"] == pytest.approx(0.01)


def test_runtime_pairwise_sensitivity_matches_documented_pattern() -> None:
    pairwise = pairwise_interaction_sensitivity(
        _results(),
        factors=["detector", "qc_policy", "aoi_mode"],
    )

    first = pairwise.iloc[0]
    assert first["factor_a"] == "detector"
    assert first["factor_b"] == "aoi_mode"
    assert first["interaction_ratio"] == pytest.approx(
        0.012658227848101255
    )
    assert first["max_abs_interaction"] == pytest.approx(0.0025)


def test_robustness_summaries_fail_closed_on_nonfinite_estimates() -> None:
    bad = _results()
    bad.loc[3, "estimate"] = np.nan

    with pytest.raises(ValueError, match="endpoint estimates must be finite"):
        effect_stability(bad)
    with pytest.raises(ValueError, match="endpoint estimates must be finite"):
        specification_curve(bad)
    with pytest.raises(ValueError, match="endpoint estimates must be finite"):
        marginal_sensitivity(bad, factors=["detector"])
    with pytest.raises(ValueError, match="endpoint estimates must be finite"):
        pairwise_interaction_sensitivity(
            bad,
            factors=["detector", "aoi_mode"],
        )


def test_center_preserves_descriptive_and_inferential_boundaries() -> None:
    text = _text(CENTER)

    for contract in (
        "page_type: robustness-diagnostics",
        "site.data.robustness_diagnostics",
        "data-robustness-controls",
        "data-robustness-search",
        "data-robustness-kind",
        "data-robustness-status",
        'role="status"',
        'aria-live="polite"',
        "Execution completeness",
        "Specification curve",
        "Effect stability",
        "Marginal sensitivity",
        "Pairwise sensitivity",
        "Controlled sensitivity curves",
        "Finite endpoint prerequisite",
        "Read the plot as a visual summary, not new evidence",
        "When not to use a robustness diagnostic",
    ):
        assert contract in text

    assert "not confidence intervals or credible intervals" in text
    assert "not an inferential winner" not in text


def test_filter_ui_is_progressive_and_accessible() -> None:
    js = _text(JS)
    css = _text(CSS)

    for contract in (
        "data-robustness-controls",
        "data-robustness-card",
        "card.hidden = !show",
        "Showing all",
        "search.focus()",
        "empty.hidden = visible !== 0",
    ):
        assert contract in js

    for contract in (
        ".robustness-diagnostic-controls",
        ".robustness-diagnostic-grid",
        ".robustness-diagnostic-card",
        ".robustness-claim-grid",
        ".robustness-diagnostic-routes",
        ":focus-visible",
        "@media (max-width: 780px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_guide_covers_core_diagnostic_boundaries() -> None:
    text = _text(GUIDE)

    for heading in (
        "Start with the denominator",
        "Know the finite-estimate contract",
        "Read a specification curve as an ordered evidence display",
        "Separate sign stability from magnitude stability",
        "Interpret the empirical quantiles correctly",
        "Interpret sign fractions as branch proportions",
        "Read marginal sensitivity as descriptive factor alignment",
        "Read pairwise sensitivity as non-additive pattern screening",
        "Controlled sensitivity is a different design",
        "Sampling sensitivity is not another hardware experiment",
        "Missingness sensitivity is not a causal missing-data effect",
        "Spatial-error sensitivity is conditional on the error model",
        "Plot examples are evidence displays, not validation evidence",
        "Reporting language",
        "Diagnostic checklist",
    ):
        assert heading in text


def test_worked_example_matches_governed_contract() -> None:
    text = _text(EXAMPLE)

    assert 'example_data: "Synthetic"' in text
    assert 'example_focus: "Interpretation & reporting"' in text

    for contract in (
        "8 declared",
        "8 valid",
        "8 successful finite endpoints",
        "q025",
        "-0.00825",
        "q975",
        "0.05825",
        "0.620253",
        "0.316456",
        "0.050633",
        "interaction_ratio ≈ 0.012658",
        "Seven of eight valid specifications",
        "Methods example",
        "Results example",
        "Limitation example",
        "Reuse boundary",
    ):
        assert contract in text


def test_diagnostic_api_and_plot_routes_exist() -> None:
    api = json.loads(_text(API_REFERENCE))
    anchors = {item["anchor"] for item in api["symbols"]}
    expected_anchors = {
        "api-specification-curve",
        "api-effect-stability",
        "api-spatial-sensitivity-curve",
        "api-sampling-sensitivity-curve",
        "api-missingness-sensitivity-curve",
    }
    assert expected_anchors.issubset(anchors)

    plots = _text(PLOTS)
    assert "- id: specification-curve" in plots
    assert "- id: factor-sensitivity" in plots


def test_diagnostic_routes_are_discoverable_across_site() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    faq = _text(FAQ)
    readme = _text(README)

    assert layout.count("/docs/robustness-diagnostics/") >= 3
    assert "/docs/guides/robustness-diagnostics/" in layout
    assert "/docs/examples/robustness-diagnostic-walkthrough/" in layout
    assert "[Robustness Diagnostics & Sensitivity Interpretation Center]" in docs
    assert "[Read robustness diagnostics]" in guides
    assert "Diagnostic interpretation →</a>" in examples
    assert "/assets/robustness-diagnostic-reference.json" in reference
    assert "/docs/robustness-diagnostics/" in compass
    assert "/docs/robustness-diagnostics/" in faq
    assert "/docs/robustness-diagnostics/" in readme


def test_reference_and_site_verifier_are_governed() -> None:
    source = _text(JSON_SOURCE)
    checker = _text(SITE_CHECK)

    assert "permalink: /assets/robustness-diagnostic-reference.json" in source
    assert "{{ site.data.robustness_diagnostics | jsonify }}" in source

    for contract in (
        "def _verify_robustness_diagnostic_reference",
        "unexpected robustness diagnostic catalog",
        "robustness diagnostic ids mismatch",
        "_verify_robustness_diagnostic_reference(site_root",
        '"docs/robustness-diagnostics/index.html"',
        '"docs/guides/robustness-diagnostics/index.html"',
        '"docs/examples/robustness-diagnostic-walkthrough/index.html"',
        '"assets/robustness-diagnostic-reference.json"',
        '"assets/css/robustness-diagnostics.css"',
        '"assets/js/robustness-diagnostics.js"',
    ):
        assert contract in checker
