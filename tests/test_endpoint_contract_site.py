import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit import GazeStudy, PipelineSpace, run_specs

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "endpoint_contract_fields.yml"
JSON_SOURCE = ROOT / "assets" / "endpoint-contract-reference.json"
CENTER = ROOT / "docs" / "endpoint-contract.md"
GUIDE = ROOT / "docs" / "guides" / "endpoint-definition.md"
EXAMPLE = ROOT / "docs" / "examples" / "endpoint-drift-audit.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "endpoint-contract.css"
JS = ROOT / "assets" / "js" / "endpoint-contract.js"
DOCS = ROOT / "docs" / "index.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
EXAMPLES = ROOT / "docs" / "examples" / "index.md"
REFERENCE = ROOT / "docs" / "reference" / "index.md"
COMPASS = ROOT / "docs" / "documentation-map.md"
FAQ = ROOT / "docs" / "faq.md"
README = ROOT / "README.md"
API_REFERENCE = ROOT / "assets" / "api-symbol-reference.json"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"

EXPECTED_FIELDS = {
    "endpoint_name",
    "scientific_quantity",
    "unit",
    "contrast_direction",
    "analysis_unit",
    "population_denominator",
    "missingness_policy",
    "nonfinite_policy",
    "transformation",
    "scientific_null",
    "required_inputs",
    "interpretation_boundary",
}

REQUIRED_FIELDS = EXPECTED_FIELDS - {
    "transformation",
    "scientific_null",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _study() -> GazeStudy:
    return GazeStudy(
        pd.DataFrame(
            {
                "participant": ["P01", "P01"],
                "trial": [1, 1],
                "timestamp": [0.0, 16.7],
                "x": [100.0, 101.0],
                "y": [50.0, 51.0],
            }
        )
    )


def _catalog_blocks() -> list[str]:
    text = _text(CATALOG)
    return ["- name: " + block for block in text.split("- name: ")[1:]]


def _field(block: str, name: str) -> str:
    match = re.search(
        rf"^  {re.escape(name)}: (.+)$",
        block,
        flags=re.MULTILINE,
    )
    assert match is not None, f"missing field {name}"
    return match.group(1).strip().strip('"')


def test_endpoint_catalog_has_exact_governed_fields() -> None:
    blocks = _catalog_blocks()
    names = {_field(block, "name") for block in blocks}
    required = {
        _field(block, "name")
        for block in blocks
        if _field(block, "required") == "true"
    }

    assert len(blocks) == 12
    assert names == EXPECTED_FIELDS
    assert required == REQUIRED_FIELDS

    for block in blocks:
        for field in (
            "label:",
            "value_type:",
            "required:",
            "purpose:",
            "boundary:",
        ):
            assert field in block


def test_run_specs_returns_one_float_coerced_row_per_valid_spec() -> None:
    study = _study()
    space = (
        PipelineSpace()
        .add_choice("a", [1, 2])
        .add_choice("b", [10, 20])
    )

    results = run_specs(
        study,
        space,
        endpoint=lambda processed, spec: np.float64(spec["a"] + spec["b"]),
        valid_if=lambda spec: not (spec["a"] == 2 and spec["b"] == 20),
    )

    assert len(results) == 3
    assert results["spec_id"].tolist() == [0, 1, 2]
    assert results["estimate"].tolist() == [11.0, 21.0, 12.0]
    assert np.issubdtype(results["estimate"].dtype, np.floating)


def test_run_specs_preserves_nan_endpoint_without_automatic_rejection() -> None:
    study = _study()
    space = PipelineSpace().add_choice("branch", ["finite", "nonfinite"])

    def endpoint(processed: GazeStudy, spec: dict[str, str]) -> float:
        del processed
        if spec["branch"] == "nonfinite":
            return float("nan")
        return 1.0

    results = run_specs(study, space, endpoint=endpoint)

    assert results["estimate"].iloc[0] == 1.0
    assert np.isnan(results["estimate"].iloc[1])


def test_run_specs_propagates_endpoint_exceptions() -> None:
    study = _study()
    space = PipelineSpace().add_choice("branch", ["ok", "fail"])

    def endpoint(processed: GazeStudy, spec: dict[str, str]) -> float:
        del processed
        if spec["branch"] == "fail":
            raise ValueError("declared endpoint unavailable")
        return 1.0

    with pytest.raises(ValueError, match="declared endpoint unavailable"):
        run_specs(study, space, endpoint=endpoint)


def test_endpoint_center_has_no_prefilled_scientific_values() -> None:
    text = _text(CENTER)

    assert "This builder does not invent an endpoint." in text
    assert "No contrast, unit, aggregation, missingness rule" in text
    assert "That coercion does **not** itself reject `NaN` or infinity." in text

    value_controls = re.findall(
        r"<(?:input|textarea)(?:(?!<(?:input|textarea)).)*?"
        r"data-endpoint-value(?:(?!<(?:input|textarea)).)*?>",
        text,
        flags=re.DOTALL,
    )
    assert len(value_controls) == 12
    assert all(" value=" not in control for control in value_controls)


def test_endpoint_builder_is_accessible_and_refuses_to_fabricate_code() -> None:
    text = _text(CENTER)
    js = _text(JS)
    css = _text(CSS)

    for contract in (
        "data-endpoint-builder",
        "data-endpoint-field",
        "data-endpoint-errors",
        'role="alert"',
        'tabindex="-1"',
        "data-endpoint-status",
        'role="status"',
        'aria-live="polite"',
        "data-endpoint-finite-guard",
        "data-endpoint-copy",
    ):
        assert contract in text

    for contract in (
        "raise NotImplementedError",
        "endpoint estimate must be finite under the declared contract",
        "aria-invalid",
        "errors.focus()",
        "navigator.clipboard.writeText",
        "The Python calculation remains intentionally unimplemented.",
    ):
        assert contract in js

    for contract in (
        ".endpoint-field-grid",
        ".endpoint-field-card",
        ".endpoint-finite-guard",
        ".endpoint-builder-errors",
        ".endpoint-output-grid",
        ":focus-visible",
        "@media (max-width: 820px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_endpoint_methodology_covers_invariance_failure_and_reporting() -> None:
    text = _text(GUIDE)

    for heading in (
        "Write the endpoint in words before code",
        "Fix the sign / contrast convention",
        "Fix the unit or scale",
        "Fix the analysis unit and aggregation target",
        "Fix the eligible population / denominator",
        "Separate processor choices from endpoint meaning",
        "Do not hide undeclared specification choices inside the endpoint",
        "Treat endpoint transformations as part of the contract",
        "Define missing-input behavior",
        "Define the non-finite endpoint policy",
        "Keep `valid_if` separate from endpoint failure",
        "Keep endpoint and conclusion rule separate",
        "Test endpoint invariance before the full audit",
        "Endpoint change during peer review",
        "Reporting endpoint identity",
        "Endpoint handoff checklist",
    ):
        assert heading.replace("`", chr(96)) in text

    assert "Do not convert a non-finite endpoint to zero." in text


def test_endpoint_drift_example_covers_nine_compatibility_scenarios() -> None:
    text = _text(EXAMPLE)

    assert 'example_data: "Synthetic"' in text
    assert 'example_focus: "Robustness & sensitivity"' in text
    assert text.count("## Scenario ") == 9

    for phrase in (
        "QC varies, endpoint stays the same",
        "AOI radius varies, dwell contrast stays the same",
        "Contrast silently reverses",
        "Seconds appear in one branch",
        "Dwell changes to fixation count",
        "Participant weighting changes to observation weighting",
        "Missing pair silently becomes zero",
        "Endpoint returns `NaN`",
        "Reviewer requests latency instead of dwell",
        "Compatibility matrix",
        "Reuse boundary",
    ):
        assert phrase.replace("`", chr(96)) in text


def test_endpoint_api_links_exist_in_governed_reference() -> None:
    api = json.loads(_text(API_REFERENCE))
    anchors = {item["anchor"] for item in api["symbols"]}

    expected = {
        "api-run-specs",
        "api-pipelinespace",
        "api-expected-dwell",
    }
    assert expected.issubset(anchors)

    center = _text(CENTER)
    for anchor in expected:
        assert f"#{anchor}" in center


def test_endpoint_routes_are_discoverable_across_site() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    faq = _text(FAQ)
    readme = _text(README)

    assert layout.count("/docs/endpoint-contract/") >= 3
    assert "/docs/guides/endpoint-definition/" in layout
    assert "/docs/examples/endpoint-drift-audit/" in layout
    assert "[Endpoint Definition & Handoff Center](endpoint-contract/)" in docs
    assert "[Endpoint definition and invariance]" in guides
    assert 'href="endpoint-drift-audit/">Endpoint drift audit →</a>' in examples
    assert "/assets/endpoint-contract-reference.json" in reference
    assert "/docs/endpoint-contract/" in compass
    assert "/docs/endpoint-contract/" in faq
    assert "/docs/endpoint-contract/" in readme


def test_endpoint_reference_and_site_verifier_are_governed() -> None:
    source = _text(JSON_SOURCE)
    checker = _text(SITE_CHECK)

    assert "permalink: /assets/endpoint-contract-reference.json" in source
    assert "{{ site.data.endpoint_contract_fields | jsonify }}" in source

    for contract in (
        "def _verify_endpoint_contract_reference",
        "unexpected endpoint field catalog",
        "endpoint field names mismatch",
        "_verify_endpoint_contract_reference(site_root",
        '"docs/endpoint-contract/index.html"',
        '"docs/guides/endpoint-definition/index.html"',
        '"docs/examples/endpoint-drift-audit/index.html"',
        '"assets/endpoint-contract-reference.json"',
        '"assets/css/endpoint-contract.css"',
        '"assets/js/endpoint-contract.js"',
    ):
        assert contract in checker
