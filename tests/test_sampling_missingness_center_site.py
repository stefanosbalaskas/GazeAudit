import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    GazeStudy,
    downsample_gaze,
    inject_missingness,
    missingness_sensitivity_curve,
    sampling_sensitivity_curve,
    summarize_missingness,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "sampling_missingness_contracts.yml"
JSON_SOURCE = ROOT / "assets" / "sampling-missingness-reference.json"
CENTER = ROOT / "docs" / "sampling-missingness.md"
GUIDE = ROOT / "docs" / "guides" / "sampling-missingness-sensitivity.md"
EXAMPLE = ROOT / "docs" / "examples" / "sampling-missingness-design-audit.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "sampling-missingness.css"
JS = ROOT / "assets" / "js" / "sampling-missingness.js"
DOCS = ROOT / "docs" / "index.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
EXAMPLES = ROOT / "docs" / "examples" / "index.md"
REFERENCE = ROOT / "docs" / "reference" / "index.md"
COMPASS = ROOT / "docs" / "documentation-map.md"
FAQ = ROOT / "docs" / "faq.md"
README = ROOT / "README.md"
API_REFERENCE = ROOT / "assets" / "api-symbol-reference.json"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"

EXPECTED_IDS = {
    "missingness-mask",
    "summarize-missingness",
    "downsample-gaze",
    "sampling-sensitivity-curve",
    "inject-missingness",
    "missingness-sensitivity-curve",
}

EXPECTED_API_ANCHORS = {
    "api-missingness-mask",
    "api-summarize-missingness",
    "api-downsample-gaze",
    "api-sampling-sensitivity-curve",
    "api-inject-missingness",
    "api-missingness-sensitivity-curve",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sampling_study() -> GazeStudy:
    return GazeStudy(
        pd.DataFrame(
            {
                "participant": ["P01"] * 10,
                "trial": [1] * 10,
                "timestamp": np.arange(0.0, 100.0, 10.0),
                "x": np.arange(10, dtype=float),
                "y": np.zeros(10),
            }
        )
    )


def _missing_study(n: int = 20) -> GazeStudy:
    return GazeStudy(
        pd.DataFrame(
            {
                "participant": ["P01"] * (n // 2) + ["P02"] * (n - n // 2),
                "trial": [1] * n,
                "timestamp": np.arange(n, dtype=float),
                "x": np.arange(n, dtype=float),
                "y": np.arange(n, dtype=float) * 0.5,
            }
        )
    )


def test_governed_contract_catalog_has_exact_runtime_families() -> None:
    text = _text(CATALOG)

    ids = set(
        re.findall(r"^- id: ([a-z0-9-]+)$", text, flags=re.MULTILINE)
    )
    anchors = set(
        re.findall(r"^  api_anchor: ([a-z0-9-]+)$", text, flags=re.MULTILINE)
    )

    assert ids == EXPECTED_IDS
    assert anchors == EXPECTED_API_ANCHORS
    assert text.count("  family: Observed missingness") == 2
    assert text.count("  family: Sampling perturbation") == 1
    assert text.count("  family: Sampling sensitivity") == 1
    assert text.count("  family: Missingness perturbation") == 1
    assert text.count("  family: Missingness sensitivity") == 1

    for field in (
        "function_name:",
        "question:",
        "operation:",
        "input_contract:",
        "output_contract:",
        "randomness:",
        "preserves:",
        "when_use:",
        "when_not:",
        "boundary:",
    ):
        assert text.count(field) == 6


def test_downsample_runtime_matches_worked_exact_rows_and_preserves_source() -> None:
    study = _sampling_study()
    original = study.data.copy(deep=True)

    down50 = downsample_gaze(
        study,
        50.0,
        timestamp_unit="ms",
    )

    assert down50.data["timestamp"].tolist() == [
        0.0,
        20.0,
        40.0,
        60.0,
        80.0,
    ]
    assert down50.data["x"].tolist() == [0.0, 2.0, 4.0, 6.0, 8.0]
    pd.testing.assert_frame_equal(study.data, original)


def test_sampling_curve_matches_worked_retention_and_endpoint() -> None:
    curve = sampling_sensitivity_curve(
        _sampling_study(),
        target_rates=[100.0, 50.0],
        endpoint=lambda current: float(current.data["x"].mean()),
        timestamp_unit="ms",
    )

    assert curve["target_hz"].tolist() == [100.0, 50.0]
    assert curve["n_rows"].tolist() == [10, 5]
    assert curve["retained_fraction"].tolist() == pytest.approx([1.0, 0.5])
    assert curve["estimate"].tolist() == pytest.approx([4.5, 4.0])


def test_sampling_runtime_rejects_bad_contract_inputs() -> None:
    study = _sampling_study()

    with pytest.raises(ValueError, match="positive"):
        downsample_gaze(study, 0.0)
    with pytest.raises(ValueError, match="timestamp_unit"):
        downsample_gaze(study, 50.0, timestamp_unit="ticks")
    with pytest.raises(ValueError, match="at least one value"):
        sampling_sensitivity_curve(study, [], lambda current: 1.0)
    with pytest.raises(ValueError, match="finite scalar"):
        sampling_sensitivity_curve(
            study,
            [50.0],
            lambda current: np.inf,
        )


def test_mcar_and_block_injection_are_reproducible_and_preserve_source() -> None:
    study = _missing_study()
    original = study.data.copy(deep=True)

    first = inject_missingness(
        study,
        0.25,
        mechanism="mcar",
        rng=123,
        reason="synthetic_benchmark",
    )
    second = inject_missingness(
        study,
        0.25,
        mechanism="mcar",
        rng=123,
        reason="synthetic_benchmark",
    )
    pd.testing.assert_frame_equal(first.data, second.data)
    assert int(summarize_missingness(first)["n_missing"]) == 5

    block_a = inject_missingness(
        study,
        0.30,
        mechanism="block",
        rng=77,
    )
    block_b = inject_missingness(
        study,
        0.30,
        mechanism="block",
        rng=77,
    )
    pd.testing.assert_frame_equal(block_a.data, block_b.data)
    assert int(summarize_missingness(block_a)["n_missing"]) == 6

    pd.testing.assert_frame_equal(study.data, original)


def test_requested_added_fraction_uses_currently_complete_rows() -> None:
    study = _missing_study(10)
    data = study.data.copy()
    data.loc[0, ["x", "y"]] = np.nan
    native = study.copy_with(data)

    perturbed = inject_missingness(
        native,
        0.50,
        mechanism="mcar",
        rng=1,
    )
    summary = summarize_missingness(perturbed)

    assert int(summary["n_rows"]) == 10
    assert int(summary["n_missing"]) == 5
    assert int(summary["n_complete"]) == 5
    assert float(summary["missing_fraction"]) == pytest.approx(0.5)


def test_missingness_curve_is_seed_reproducible_one_row_per_fraction() -> None:
    study = _missing_study()

    def endpoint(current: GazeStudy) -> float:
        return float(current.data["x"].mean(skipna=True))

    first = missingness_sensitivity_curve(
        study,
        fractions=[0.0, 0.25, 0.50],
        endpoint=endpoint,
        mechanism="mcar",
        rng=11,
    )
    second = missingness_sensitivity_curve(
        study,
        fractions=[0.0, 0.25, 0.50],
        endpoint=endpoint,
        mechanism="mcar",
        rng=11,
    )

    pd.testing.assert_frame_equal(first, second)
    assert first["requested_fraction"].tolist() == [0.0, 0.25, 0.5]
    assert first["n_missing"].tolist() == [0, 5, 10]
    assert len(first) == 3
    assert np.isfinite(first["estimate"]).all()


def test_missingness_runtime_rejects_unsupported_or_nonfinite_contracts() -> None:
    study = _missing_study(10)

    with pytest.raises(ValueError, match="between 0 and 1"):
        inject_missingness(study, -0.1)
    with pytest.raises(ValueError, match="mechanism"):
        inject_missingness(study, 0.2, mechanism="informative")
    with pytest.raises(ValueError, match="at least one value"):
        missingness_sensitivity_curve(study, [], lambda current: 1.0)
    with pytest.raises(ValueError, match="finite scalar"):
        missingness_sensitivity_curve(
            study,
            [0.1],
            lambda current: np.inf,
        )


def test_center_has_no_hidden_perturbation_values_and_separates_families() -> None:
    center = _text(CENTER)
    js = _text(JS)

    assert "No target rate, missingness fraction, mechanism, seed" in center
    assert '<option value="">Choose explicitly…</option>' in center
    assert "Sampling and added missingness are generated as separate curves." in center

    for forbidden in (
        'value="500"',
        'value="250"',
        'value="0.01"',
        'value="0.05"',
        'value="20260913"',
    ):
        assert forbidden not in center

    for contract in (
        "samplingFieldset.disabled = !usesSampling()",
        "missingnessFieldset.disabled = !usesMissingness()",
        "Target rates",
        "Missingness fractions",
        "contains duplicate values",
        "Root seed must be a non-negative safe integer.",
        "sampling_sensitivity_curve",
        "missingness_sensitivity_curve",
        "No data were inspected or perturbed.",
    ):
        assert contract in js

    assert "fetch(" not in js
    assert "FileReader" not in js


def test_center_is_progressive_accessible_and_contract_driven() -> None:
    center = _text(CENTER)
    css = _text(CSS)

    for contract in (
        "site.data.sampling_missingness_contracts",
        "data-sampling-contract-controls",
        "data-sampling-contract-search",
        "data-sampling-contract-family",
        "data-sampling-contract-status",
        'role="status"',
        'aria-live="polite"',
        "All cards remain visible without JavaScript.",
        "data-sampling-plan-builder",
        "data-plan-errors",
        'role="alert"',
        'tabindex="-1"',
        "data-plan-copy",
    ):
        assert contract in center

    for contract in (
        ".sampling-contract-controls",
        ".sampling-contract-card",
        ".sampling-contract-use-grid",
        ".sampling-plan-builder",
        ".sampling-plan-family",
        ".sampling-plan-errors",
        ".sampling-plan-output-grid",
        ":focus-visible",
        "@media (max-width: 860px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_methodology_guide_covers_core_scientific_boundaries() -> None:
    guide = _text(GUIDE)

    for heading in (
        "Measure observed missingness before adding more",
        "Treat lower sampling rate as a representation perturbation",
        "Do not call downsampling a hardware simulation",
        "Report actual retention, not only the target rate",
        "Added missingness operates on currently complete rows",
        "Preserve native missingness",
        "Understand the MCAR benchmark",
        "Understand the block benchmark",
        "Preserve a deterministic seed",
        "A missingness curve is one draw per fraction per call",
        "Add outer replication explicitly when required",
        "Requested and observed missingness must both be reported",
        "Keep sampling and missingness families separate by default",
        "Do not treat row loss mechanisms as interchangeable",
        "Separate sensitivity from repair or imputation",
        "Use the frozen Pedrotti case correctly",
        "Reporting checklist",
        "Reporting examples",
    ):
        assert heading in guide

    for boundary in (
        "Do not infer:",
        "It does **not** interpolate gaze coordinates.",
        "It does not prove that empirical eye-tracking missingness is MCAR.",
        "It does not produce a distribution of outcomes at each fraction.",
        "Do not copy its rates, fractions, seed, 20% tolerance",
    ):
        assert boundary in guide


def test_worked_example_is_runtime_linked_synthetic_and_bounded() -> None:
    example = _text(EXAMPLE)

    for contract in (
        'example_data: "Synthetic"',
        'example_focus: "Robustness & sensitivity"',
        "Do not reuse the numerical settings.",
        "[0.0, 20.0, 40.0, 60.0, 80.0]",
        "| 100 | 10 | 1.00 | 4.5 |",
        "| 50 | 5 | 0.50 | 4.0 |",
        "round(0.25 × 20 complete rows) = 5 rows",
        "assert int(block_summary[\"n_missing\"]) == 6",
        "round(0.50 × 9) = 4 newly masked rows",
        "[0, 5, 10]",
        "one perturbation realization per call",
        "Reuse boundary",
    ):
        assert contract in example


def test_all_sampling_missingness_api_anchors_exist() -> None:
    api = json.loads(_text(API_REFERENCE))
    anchors = {item["anchor"] for item in api["symbols"]}

    assert EXPECTED_API_ANCHORS.issubset(anchors)

    center = _text(CENTER)
    for anchor in EXPECTED_API_ANCHORS:
        assert f"#{anchor}" in center


def test_sampling_missingness_routes_are_discoverable() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    faq = _text(FAQ)
    readme = _text(README)

    assert layout.count("/docs/sampling-missingness/") >= 3
    assert "/docs/guides/sampling-missingness-sensitivity/" in layout
    assert "/docs/examples/sampling-missingness-design-audit/" in layout

    assert "[Sampling & Missingness Sensitivity Center]" in docs
    assert "[Design sampling and missingness sensitivity]" in guides
    assert "[Sampling & missingness design audit]" in examples
    assert "/assets/sampling-missingness-reference.json" in reference
    assert "/docs/sampling-missingness/" in compass
    assert "/docs/sampling-missingness/" in faq
    assert "/docs/sampling-missingness/" in readme


def test_sampling_missingness_reference_and_site_verifier_are_governed() -> None:
    source = _text(JSON_SOURCE)
    checker = _text(SITE_CHECK)

    assert "permalink: /assets/sampling-missingness-reference.json" in source
    assert "{{ site.data.sampling_missingness_contracts | jsonify }}" in source

    for contract in (
        "def _verify_sampling_missingness_reference",
        "unexpected sampling/missingness contract catalog",
        "sampling/missingness contract IDs mismatch",
        "_verify_sampling_missingness_reference(site_root",
        '"docs/sampling-missingness/index.html"',
        '"docs/guides/sampling-missingness-sensitivity/index.html"',
        '"docs/examples/sampling-missingness-design-audit/index.html"',
        '"assets/sampling-missingness-reference.json"',
        '"assets/css/sampling-missingness.css"',
        '"assets/js/sampling-missingness.js"',
    ):
        assert contract in checker
