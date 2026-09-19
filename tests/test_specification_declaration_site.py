import json
import re
from pathlib import Path

import pandas as pd
import pytest

from gazeaudit import GazeStudy, PipelineSpace, run_specs

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "specification_declaration_fields.yml"
JSON_SOURCE = ROOT / "assets" / "specification-declaration-reference.json"
CENTER = ROOT / "docs" / "specification-declaration.md"
GUIDE = ROOT / "docs" / "guides" / "specification-declaration.md"
EXAMPLE = ROOT / "docs" / "examples" / "specification-denominator-audit.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "specification-declaration.css"
JS = ROOT / "assets" / "js" / "specification-declaration.js"
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
    "space_name",
    "scientific_question",
    "endpoint_reference",
    "decision_timing",
    "validity_mode",
    "validity_rule",
    "reference_specification",
    "failure_policy",
    "interpretation_boundary",
}

REQUIRED_FIELDS = {
    "space_name",
    "scientific_question",
    "endpoint_reference",
    "decision_timing",
    "validity_mode",
    "failure_policy",
    "interpretation_boundary",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def _space() -> PipelineSpace:
    return (
        PipelineSpace()
        .add_choice("detector", ["ivt", "idt"])
        .add_choice("qc_policy", ["moderate", "strict"])
        .add_choice("aoi_mode", ["hard", "probabilistic"])
    )


def _valid_spec(spec: dict[str, object]) -> bool:
    return not (
        spec["detector"] == "idt"
        and spec["qc_policy"] == "strict"
    )


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


def test_specification_declaration_catalog_has_exact_fields() -> None:
    blocks = _catalog_blocks()
    names = {_field(block, "name") for block in blocks}
    required = {
        _field(block, "name")
        for block in blocks
        if _field(block, "required") == "true"
    }

    assert len(blocks) == 9
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


def test_pipeline_space_cartesian_size_and_order_are_deterministic() -> None:
    space = _space()

    assert space.size == 8

    first = space.enumerate_specs()
    second = space.enumerate_specs()
    assert first == second
    assert len(first) == 8

    assert first[0] == {
        "detector": "ivt",
        "qc_policy": "moderate",
        "aoi_mode": "hard",
    }
    assert first[-1] == {
        "detector": "idt",
        "qc_policy": "strict",
        "aoi_mode": "probabilistic",
    }


def test_validity_rule_yields_six_valid_from_eight_declared() -> None:
    space = _space()
    valid = space.enumerate_specs(valid_if=_valid_spec)

    assert space.size == 8
    assert len(valid) == 6
    assert all(_valid_spec(spec) for spec in valid)

    invalid = [
        spec
        for spec in space.enumerate_specs()
        if not _valid_spec(spec)
    ]
    assert len(invalid) == 2
    assert {
        spec["aoi_mode"]
        for spec in invalid
    } == {"hard", "probabilistic"}


def test_duplicate_factor_name_overwrites_in_runtime_mapping() -> None:
    space = (
        PipelineSpace()
        .add_choice("detector", ["ivt", "idt"])
        .add_choice("detector", ["custom"])
    )

    assert space.choices == {"detector": ("custom",)}
    assert space.size == 1

    builder = _text(JS)
    assert "Factor name ${name} is duplicated." in builder


def test_run_specs_propagates_one_valid_branch_failure() -> None:
    study = _study()
    space = _space()

    def processor(current: GazeStudy, spec: dict[str, object]) -> GazeStudy:
        if (
            spec["detector"] == "ivt"
            and spec["qc_policy"] == "strict"
            and spec["aoi_mode"] == "probabilistic"
        ):
            raise RuntimeError("synthetic backend failure")
        return current

    def endpoint(processed: GazeStudy, spec: dict[str, object]) -> float:
        del processed, spec
        return 1.0

    with pytest.raises(RuntimeError, match="synthetic backend failure"):
        run_specs(
            study,
            space,
            endpoint=endpoint,
            processor=processor,
            valid_if=_valid_spec,
        )


def test_all_valid_space_runs_six_rows_after_explicit_filter() -> None:
    study = _study()
    space = _space()

    results = run_specs(
        study,
        space,
        endpoint=lambda processed, spec: 1.0,
        valid_if=_valid_spec,
    )

    assert len(results) == 6
    assert results["spec_id"].tolist() == list(range(6))


def test_builder_calculates_only_declared_count_without_guessing_validity() -> None:
    center = _text(CENTER)
    js = _text(JS)

    assert "never invents a valid-specification count" in center
    assert "valid count remains unknown" in js
    assert "declared_combination_count" in js
    assert "valid_combination_count" in js
    assert "raise NotImplementedError" in js
    assert "implement the declared pre-execution validity rule" in js


def test_builder_enforces_unique_names_typed_levels_and_rationale() -> None:
    js = _text(JS)
    css = _text(CSS)

    for contract in (
        "factorNames.has(name)",
        "contains duplicate levels",
        "number levels must all be finite numeric values",
        "boolean levels must be true or false",
        "needs a rationale",
        "data-spec-add-factor",
        "data-spec-remove-factor",
        "validityRule.disabled = !needsPredicate",
        "validityRule.required = needsPredicate",
        "aria-invalid",
        "errors.focus()",
    ):
        assert contract in js

    for contract in (
        ".spec-declaration-field-grid",
        ".spec-factor-card",
        ".spec-factor-grid",
        ".spec-validity-mode",
        ".spec-builder-errors",
        ".spec-output-grid",
        ":focus-visible",
        "@media (max-width: 860px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_methodology_guide_covers_validity_timing_and_failure_denominators() -> None:
    text = _text(GUIDE)

    for heading in (
        "Fix the common endpoint first",
        "State the robustness question",
        "Include factors because they are scientifically defensible",
        "Give every level a rationale",
        "Keep factor names unique",
        "Preserve typed levels",
        "Calculate the declared denominator before execution",
        "Separate declared from valid",
        "Validity rules must be independent of the endpoint result",
        "Invalid-before-execution is not technical failure",
        "A non-finite endpoint is not predeclared invalidity",
        "Declare the execution-failure policy before running the space",
        "Record declaration timing",
        "Keep reviewer-requested additions separate when timing differs",
        "Avoid specification explosion",
        "Consider dependencies among factors",
        "Reporting the declaration",
        "Specification declaration checklist",
    ):
        assert heading in text


def test_worked_example_preserves_eight_six_five_denominators() -> None:
    text = _text(EXAMPLE)

    assert 'example_data: "Synthetic"' in text
    assert 'example_focus: "Robustness & sensitivity"' in text

    for contract in (
        "8 declared",
        "6 valid",
        "5 successful",
        "1 valid technical failure",
        "2 invalid before execution",
        "5 successful / 6 valid",
        "Not:",
        "5 / 5",
        "A repaired rerun does not erase the original failure",
        "Reuse boundary",
    ):
        assert contract in text


def test_specification_api_links_exist() -> None:
    api = json.loads(_text(API_REFERENCE))
    anchors = {item["anchor"] for item in api["symbols"]}

    expected = {
        "api-pipelinespace",
        "api-run-specs",
        "api-specification-curve",
        "api-effect-stability",
    }
    assert expected.issubset(anchors)

    center = _text(CENTER)
    for anchor in expected:
        assert f"#{anchor}" in center


def test_specification_declaration_routes_are_discoverable() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    faq = _text(FAQ)
    readme = _text(README)

    assert layout.count("/docs/specification-declaration/") >= 3
    assert "/docs/guides/specification-declaration/" in layout
    assert "/docs/examples/specification-denominator-audit/" in layout

    assert "[Specification Space Declaration Center]" in docs
    assert "[Specification-space declaration and validity]" in guides
    assert "Declared → valid → successful →</a>" in examples
    assert "/assets/specification-declaration-reference.json" in reference
    assert "/docs/specification-declaration/" in compass
    assert "/docs/specification-declaration/" in faq
    assert "/docs/specification-declaration/" in readme


def test_specification_reference_and_site_verifier_are_governed() -> None:
    source = _text(JSON_SOURCE)
    checker = _text(SITE_CHECK)

    assert "permalink: /assets/specification-declaration-reference.json" in source
    assert "{{ site.data.specification_declaration_fields | jsonify }}" in source

    for contract in (
        "def _verify_specification_declaration_reference",
        "unexpected specification declaration catalog",
        "specification declaration field names mismatch",
        "_verify_specification_declaration_reference(site_root",
        '"docs/specification-declaration/index.html"',
        '"docs/guides/specification-declaration/index.html"',
        '"docs/examples/specification-denominator-audit/index.html"',
        '"assets/specification-declaration-reference.json"',
        '"assets/css/specification-declaration.css"',
        '"assets/js/specification-declaration.js"',
    ):
        assert contract in checker
