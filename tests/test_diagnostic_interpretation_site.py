import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    GaussianGazeErrorModel,
    GazeStudy,
    RectangleAOI,
    effect_stability,
    marginal_sensitivity,
    missingness_sensitivity_curve,
    pairwise_interaction_sensitivity,
    sampling_sensitivity_curve,
    spatial_sensitivity_curve,
    specification_curve,
    summarize_missingness,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "diagnostic_contracts.yml"
JSON_SOURCE = ROOT / "assets" / "diagnostic-contract-reference.json"
CENTER = ROOT / "docs" / "diagnostics.md"
GUIDE = ROOT / "docs" / "guides" / "diagnostic-interpretation.md"
EXAMPLE = ROOT / "docs" / "examples" / "diagnostic-interpretation.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "diagnostics.css"
JS = ROOT / "assets" / "js" / "diagnostics.js"
DOCS = ROOT / "docs" / "index.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
EXAMPLES = ROOT / "docs" / "examples" / "index.md"
REFERENCE = ROOT / "docs" / "reference" / "index.md"
COMPASS = ROOT / "docs" / "documentation-map.md"
FAQ = ROOT / "docs" / "faq.md"
README = ROOT / "README.md"
API_REFERENCE = ROOT / "assets" / "api-symbol-reference.json"
METHODS = ROOT / "_data" / "methods.yml"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"

EXPECTED_FUNCTIONS = {
    "specification_curve",
    "effect_stability",
    "marginal_sensitivity",
    "pairwise_interaction_sensitivity",
    "spatial_sensitivity_curve",
    "sampling_sensitivity_curve",
    "missingness_sensitivity_curve",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _catalog_blocks() -> list[str]:
    text = _text(CATALOG)
    return ["- id: " + block for block in text.split("- id: ")[1:]]


def _field(block: str, name: str) -> str:
    match = re.search(
        rf"^  {re.escape(name)}: (.+)$",
        block,
        flags=re.MULTILINE,
    )
    assert match is not None, f"missing field {name}"
    return match.group(1).strip().strip('"')


def _results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "factor_a": ["low", "low", "high", "high"],
            "factor_b": ["x", "y", "x", "y"],
            "estimate": [1.0, 3.0, 5.0, 9.0],
        }
    )


def _study() -> GazeStudy:
    return GazeStudy(
        pd.DataFrame(
            {
                "participant": ["P01"] * 6,
                "trial": [1] * 6,
                "timestamp": [0, 10, 20, 30, 40, 50],
                "x": [100, 101, 102, 103, 104, 105],
                "y": [200, 201, 202, 203, 204, 205],
            }
        )
    )


def test_diagnostic_catalog_has_exact_families_and_functions() -> None:
    blocks = _catalog_blocks()
    functions = {_field(block, "function") for block in blocks}
    families = [_field(block, "family") for block in blocks]

    assert len(blocks) == 7
    assert functions == EXPECTED_FUNCTIONS
    assert families.count("Specification results") == 4
    assert families.count("Controlled perturbation") == 3

    for block in blocks:
        for field in (
            "question:",
            "input_contract:",
            "output_fields:",
            "interpretation:",
            "do_not_infer:",
            "reporting_template:",
            "limitation_template:",
            "api_anchor:",
            "guide_url:",
            "example_url:",
            "plot_url:",
        ):
            assert field in block


def test_api_reference_now_governs_38_symbols_and_both_sensitivity_helpers() -> None:
    metadata = json.loads(_text(API_REFERENCE))
    symbols = {item["name"]: item for item in metadata["symbols"]}

    assert metadata["symbol_count"] == 38
    assert len(symbols) == 38

    marginal = symbols["marginal_sensitivity"]
    assert marginal["anchor"] == "api-marginal-sensitivity"
    assert marginal["source_line"] == 46
    assert marginal["minimal_call"] == "marginal_sensitivity(results, factors)"
    assert marginal["method_ids"] == ["specification-robustness"]

    pairwise = symbols["pairwise_interaction_sensitivity"]
    assert pairwise["anchor"] == "api-pairwise-interaction-sensitivity"
    assert pairwise["source_line"] == 91
    assert (
        pairwise["minimal_call"]
        == "pairwise_interaction_sensitivity(results, factors)"
    )
    assert pairwise["method_ids"] == ["specification-robustness"]

    methods = _text(METHODS)
    assert "    - marginal_sensitivity" in methods
    assert "    - pairwise_interaction_sensitivity" in methods


def test_specification_curve_orders_estimates_stably() -> None:
    results = _results().iloc[[3, 1, 0, 2]].reset_index(drop=True)
    ordered = specification_curve(results)

    assert ordered["estimate"].tolist() == [1.0, 3.0, 5.0, 9.0]
    assert ordered["factor_a"].tolist() == ["low", "low", "high", "high"]


def test_effect_stability_exact_synthetic_truth() -> None:
    observed = effect_stability(_results(), null=0.0)

    assert observed["n_specifications"] == 4
    assert observed["median_estimate"] == pytest.approx(4.0)
    assert observed["mean_estimate"] == pytest.approx(4.5)
    assert observed["min_estimate"] == pytest.approx(1.0)
    assert observed["max_estimate"] == pytest.approx(9.0)
    assert observed["q025"] == pytest.approx(1.15)
    assert observed["q975"] == pytest.approx(8.70)
    assert observed["positive_fraction"] == pytest.approx(1.0)
    assert observed["negative_fraction"] == pytest.approx(0.0)
    assert observed["exact_null_fraction"] == pytest.approx(0.0)
    assert observed["sign_stability"] == pytest.approx(1.0)


def test_marginal_sensitivity_exact_synthetic_truth() -> None:
    observed = marginal_sensitivity(
        _results(),
        ["factor_a", "factor_b"],
    )

    assert observed["factor"].tolist() == ["factor_a", "factor_b"]

    factor_a = observed.iloc[0]
    assert factor_a["n_levels"] == 2
    assert factor_a["marginal_eta2"] == pytest.approx(25.0 / 35.0)
    assert factor_a["level_mean_range"] == pytest.approx(5.0)

    factor_b = observed.iloc[1]
    assert factor_b["n_levels"] == 2
    assert factor_b["marginal_eta2"] == pytest.approx(9.0 / 35.0)
    assert factor_b["level_mean_range"] == pytest.approx(3.0)


def test_pairwise_sensitivity_exact_synthetic_truth() -> None:
    observed = pairwise_interaction_sensitivity(
        _results(),
        ["factor_a", "factor_b"],
    )

    assert len(observed) == 1
    row = observed.iloc[0]
    assert row["factor_a"] == "factor_a"
    assert row["factor_b"] == "factor_b"
    assert row["n_cells"] == 4
    assert row["interaction_ratio"] == pytest.approx(1.0 / 35.0)
    assert row["max_abs_interaction"] == pytest.approx(0.5)


def test_pairwise_one_factor_returns_empty_schema() -> None:
    observed = pairwise_interaction_sensitivity(
        _results(),
        ["factor_a"],
    )

    assert observed.empty
    assert observed.columns.tolist() == [
        "factor_a",
        "factor_b",
        "n_cells",
        "interaction_ratio",
        "max_abs_interaction",
    ]


@pytest.mark.parametrize(
    "runner",
    [
        lambda data: specification_curve(data),
        lambda data: effect_stability(data),
        lambda data: marginal_sensitivity(data, ["factor_a", "factor_b"]),
        lambda data: pairwise_interaction_sensitivity(
            data,
            ["factor_a", "factor_b"],
        ),
    ],
)
def test_specification_diagnostics_reject_nonfinite_endpoints(runner) -> None:
    data = _results()
    data.loc[0, "estimate"] = np.nan

    with pytest.raises(ValueError, match="endpoint estimates must be finite"):
        runner(data)


def test_sampling_sensitivity_exact_teaching_truth() -> None:
    observed = sampling_sensitivity_curve(
        _study(),
        [100, 50],
        endpoint=lambda current: float(len(current.data)),
        timestamp_unit="ms",
    )

    assert observed["target_hz"].tolist() == [100.0, 50.0]
    assert observed["n_rows"].tolist() == [6, 3]
    assert observed["retained_fraction"].tolist() == pytest.approx([1.0, 0.5])
    assert observed["estimate"].tolist() == pytest.approx([6.0, 3.0])


def test_missingness_sensitivity_exact_teaching_truth() -> None:
    observed = missingness_sensitivity_curve(
        _study(),
        [0.0, 0.5],
        endpoint=lambda current: float(
            summarize_missingness(current)["missing_fraction"]
        ),
        mechanism="mcar",
        rng=123,
    )

    assert observed["requested_fraction"].tolist() == pytest.approx([0.0, 0.5])
    assert observed["mechanism"].tolist() == ["mcar", "mcar"]
    assert observed["observed_missing_fraction"].tolist() == pytest.approx(
        [0.0, 0.5]
    )
    assert observed["n_missing"].tolist() == [0, 3]
    assert observed["estimate"].tolist() == pytest.approx([0.0, 0.5])


def test_spatial_sensitivity_is_seeded_and_schema_stable() -> None:
    points = np.array([[50.0, 50.0], [99.0, 50.0]])
    aoi = RectangleAOI("target", 0.0, 0.0, 100.0, 100.0)
    model = GaussianGazeErrorModel(
        mean_error=np.array([0.0, 0.0]),
        covariance=np.array([[25.0, 0.0], [0.0, 25.0]]),
        n_validation=20,
    )

    first = spatial_sensitivity_curve(
        points,
        [aoi],
        model,
        [0.0, 1.0],
        durations=np.array([100.0, 100.0]),
        draws=200,
        rng=42,
    )
    second = spatial_sensitivity_curve(
        points,
        [aoi],
        model,
        [0.0, 1.0],
        durations=np.array([100.0, 100.0]),
        draws=200,
        rng=42,
    )

    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 2
    assert first["sd_scale"].tolist() == [0.0, 1.0]
    assert first["aoi"].tolist() == ["target", "target"]
    assert first.columns.tolist() == [
        "sd_scale",
        "aoi",
        "expected_fixation_count",
        "mean_flip_probability",
        "mean_boundary_risk",
        "expected_dwell",
    ]
    numeric = first.drop(columns=["aoi"]).to_numpy(dtype=float)
    assert np.all(np.isfinite(numeric))


def test_diagnostic_center_is_progressive_and_accessible() -> None:
    center = _text(CENTER)
    js = _text(JS)
    css = _text(CSS)

    for contract in (
        "page_type: diagnostic-center",
        "site.data.diagnostic_contracts",
        "data-diagnostic-controls",
        "data-diagnostic-search",
        "data-diagnostic-family",
        "data-diagnostic-status",
        'role="status"',
        'aria-live="polite"',
        "All cards remain visible without JavaScript.",
        "data-diagnostic-card",
        "data-diagnostic-copy",
    ):
        assert contract in center

    for contract in (
        "card.hidden = !show",
        "Showing ${visible} of ${cards.length} diagnostics.",
        "navigator.clipboard.writeText",
        "search.focus()",
    ):
        assert contract in js

    for contract in (
        ".diagnostic-center-controls",
        ".diagnostic-contract-card",
        ".diagnostic-contract-meta",
        ".diagnostic-contract-boundary",
        ".diagnostic-contract-routes",
        ":focus-visible",
        "@media (max-width: 820px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_diagnostic_guide_and_example_preserve_interpretation_boundaries() -> None:
    guide = _text(GUIDE)
    example = _text(EXAMPLE)

    for phrase in (
        "Empirical quantiles are not inferential intervals",
        "Sign stability can be high while magnitude is unstable",
        "Marginal sensitivity is a screening diagnostic",
        "Why marginal ratios need not sum to one",
        "Pairwise sensitivity is not a factorial inferential model",
        "Sampling sensitivity retains existing samples",
        "Missingness sensitivity distinguishes requested and observed missingness",
        "Seeds are reproducibility controls, not scientific parameters",
        "Diagnostic interpretation checklist",
    ):
        assert phrase in guide

    for phrase in (
        "q025",
        "1.15",
        "q975",
        "8.70",
        "0.7142857143",
        "0.2571428571",
        "0.0285714286",
        "100 Hz",
        "50 Hz",
        "6 rows",
        "3 rows",
        "Do not infer that real missingness is MCAR.",
        "Reuse boundary",
    ):
        assert phrase in example


def test_diagnostic_contract_api_anchors_exist() -> None:
    metadata = json.loads(_text(API_REFERENCE))
    anchors = {item["anchor"] for item in metadata["symbols"]}

    catalog_anchors = {
        _field(block, "api_anchor")
        for block in _catalog_blocks()
    }
    assert catalog_anchors.issubset(anchors)


def test_diagnostic_routes_are_discoverable() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    faq = _text(FAQ)
    readme = _text(README)

    assert layout.count("/docs/diagnostics/") >= 3
    assert "/docs/guides/diagnostic-interpretation/" in layout
    assert "/docs/examples/diagnostic-interpretation/" in layout
    assert "[Robustness Diagnostics & Sensitivity Center](diagnostics/)" in docs
    assert "[Interpret robustness and sensitivity diagnostics]" in guides
    assert "Diagnostic interpretation →</a>" in examples
    assert "/assets/diagnostic-contract-reference.json" in reference
    assert "/docs/diagnostics/" in compass
    assert "/docs/diagnostics/" in faq
    assert "/docs/diagnostics/" in readme


def test_diagnostic_reference_and_site_verifier_are_governed() -> None:
    source = _text(JSON_SOURCE)
    checker = _text(SITE_CHECK)

    assert "permalink: /assets/diagnostic-contract-reference.json" in source
    assert "{{ site.data.diagnostic_contracts | jsonify }}" in source

    for contract in (
        "def _verify_diagnostic_contract_reference",
        "unexpected diagnostic contract catalog",
        "diagnostic functions mismatch",
        "_verify_diagnostic_contract_reference(site_root",
        '"docs/diagnostics/index.html"',
        '"docs/guides/diagnostic-interpretation/index.html"',
        '"docs/examples/diagnostic-interpretation/index.html"',
        '"assets/diagnostic-contract-reference.json"',
        '"assets/css/diagnostics.css"',
        '"assets/js/diagnostics.js"',
    ):
        assert contract in checker
