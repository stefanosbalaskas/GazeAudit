import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit import GazeStudy, PipelineSpace, run_specs

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "execution_states.yml"
JSON_SOURCE = ROOT / "assets" / "execution-state-reference.json"
CENTER = ROOT / "docs" / "execution-ledger.md"
GUIDE = ROOT / "docs" / "guides" / "execution-ledger-recovery.md"
EXAMPLE = ROOT / "docs" / "examples" / "execution-ledger-reconciliation.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "execution-ledger.css"
JS = ROOT / "assets" / "js" / "execution-ledger.js"
DOCS = ROOT / "docs" / "index.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
EXAMPLES = ROOT / "docs" / "examples" / "index.md"
REFERENCE = ROOT / "docs" / "reference" / "index.md"
COMPASS = ROOT / "docs" / "documentation-map.md"
FAQ = ROOT / "docs" / "faq.md"
README = ROOT / "README.md"
VOCABULARY = ROOT / "docs" / "reference" / "evidence-vocabulary.md"
TROUBLESHOOTING = ROOT / "docs" / "guides" / "troubleshooting.md"
API_REFERENCE = ROOT / "assets" / "api-symbol-reference.json"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"

EXPECTED_SIGNALS = {
    "invalid_before_execution",
    "successful",
    "technical_failure",
    "non_finite_endpoint",
    "not_run",
    "repair_rerun_success",
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


def test_execution_state_catalog_has_exact_governed_signals() -> None:
    blocks = _catalog_blocks()
    signals = {_field(block, "signal") for block in blocks}
    ids = {_field(block, "id") for block in blocks}

    assert len(blocks) == 6
    assert signals == EXPECTED_SIGNALS
    assert len(ids) == 6

    for block in blocks:
        for field in (
            "label:",
            "phase:",
            "kind:",
            "valid_denominator:",
            "attempted:",
            "estimate_state:",
            "meaning:",
            "record:",
            "next_step:",
            "reporting_template:",
            "boundary:",
        ):
            assert field in block


def test_execution_states_are_documentation_vocabulary() -> None:
    blocks = _catalog_blocks()
    technical = next(
        block
        for block in blocks
        if _field(block, "signal") == "technical_failure"
    )
    nonfinite = next(
        block
        for block in blocks
        if _field(block, "signal") == "non_finite_endpoint"
    )

    assert "not a run_specs() enum" in technical
    assert "does not automatically classify this state" in nonfinite

    center = _text(CENTER)
    assert "These execution-state labels are documentation/audit vocabulary." in center
    assert "It does not create `technical_failure`" in center


def test_run_specs_success_rows_do_not_invent_status_fields() -> None:
    results = run_specs(
        _study(),
        PipelineSpace().add_choice("branch", ["a", "b"]),
        endpoint=lambda processed, spec: 1.0,
    )

    assert results["spec_id"].tolist() == [0, 1]
    assert results["estimate"].tolist() == [1.0, 1.0]
    assert "status" not in results.columns
    assert "error" not in results.columns
    assert "technical_failure" not in results.columns


def test_run_specs_propagates_exceptions_instead_of_failure_rows() -> None:
    space = PipelineSpace().add_choice("branch", ["ok", "fail"])

    def endpoint(processed: GazeStudy, spec: dict[str, str]) -> float:
        del processed
        if spec["branch"] == "fail":
            raise RuntimeError("synthetic failure")
        return 1.0

    with pytest.raises(RuntimeError, match="synthetic failure"):
        run_specs(_study(), space, endpoint=endpoint)


def test_run_specs_preserves_nonfinite_float_values() -> None:
    results = run_specs(
        _study(),
        PipelineSpace().add_choice("branch", ["finite", "nan"]),
        endpoint=lambda processed, spec: (
            float("nan")
            if spec["branch"] == "nan"
            else 1.0
        ),
    )

    assert results["estimate"].iloc[0] == 1.0
    assert np.isnan(results["estimate"].iloc[1])


def test_execution_center_has_state_filter_and_attempt_builder() -> None:
    text = _text(CENTER)

    for contract in (
        "page_type: execution-ledger",
        "site.data.execution_states",
        "data-execution-state-controls",
        "data-execution-state-card",
        "data-execution-state-status",
        'role="status"',
        'aria-live="polite"',
        "All cards remain visible without JavaScript.",
        "data-execution-attempt-builder",
        "data-attempt-errors",
        'role="alert"',
        'tabindex="-1"',
        "data-attempt-json",
        "gazeaudit-execution-attempt-v1",
    ):
        assert contract in text

    assert "Attempt rows are not the specification denominator." in text


def test_attempt_builder_enforces_state_compatibility_without_execution() -> None:
    js = _text(JS)
    css = _text(CSS)

    for contract in (
        "Successful execution requires a finite numeric estimate.",
        "Technical failure requires an error type or error message.",
        "Technical failure must not contain a scientific estimate.",
        "Non-finite endpoint requires NaN, Infinity, +Infinity,",
        "Not-run state requires an explicit reason.",
        "Successful repair rerun requires the prior attempt ID.",
        "Successful repair rerun requires a repair record reference.",
        "Factor values must use one factor=value pair per line.",
        "aria-invalid",
        "errors.focus()",
        "navigator.clipboard.writeText",
    ):
        assert contract in js

    assert "fetch(" not in js
    assert "FileReader" not in js

    for contract in (
        ".execution-state-controls",
        ".execution-state-card",
        ".execution-state-meta",
        ".execution-attempt-builder",
        ".execution-attempt-grid",
        ".execution-attempt-errors",
        ".execution-attempt-output",
        ":focus-visible",
        "@media (max-width: 820px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_recovery_guide_covers_branch_attempt_lineage_and_reporting() -> None:
    text = _text(GUIDE)

    for heading in (
        "Keep branch identity separate from attempt identity",
        "Keep validity separate from execution state",
        "Do not invent package runtime statuses",
        "Preserve the failure before debugging",
        "Diagnose the causal layer",
        "Repair the causal defect, not the scientific result",
        "Rerun the same branch where possible",
        "Non-finite endpoints require their own evidence",
        "Not-run branches need an explicit reason",
        "Reconcile current branch state separately from attempt history",
        "Reconciliation equations",
        "Preserve outcome-inspection timing",
        "Keep repair scope minimal",
        "Build downstream summaries from reconciled current state",
        "Reporting a repaired execution",
        "Reporting unresolved execution",
        "Recovery checklist",
    ):
        assert heading in text

    assert "Attempt rows are not the specification denominator." in text
    assert "Do not convert `NaN` to zero." in text


def test_reconciliation_example_preserves_branch_and_attempt_denominators() -> None:
    text = _text(EXAMPLE)

    assert 'example_data: "Synthetic"' in text
    assert 'example_focus: "Robustness & sensitivity"' in text

    for contract in (
        "8 declared branches",
        "7 valid branches",
        "4 successful",
        "1 technical failure",
        "1 non-finite endpoint",
        "1 valid not-run branch",
        "6 successful / 7 valid",
        "S04 / A01 / technical_failure",
        "S04 / A02 / repair_rerun_success",
        "nine historical records/events associated with seven valid branches",
        "Reuse boundary",
    ):
        assert contract in text

    assert "6 successful out of 9" in text
    assert "would mix:" in text


def test_execution_api_links_exist_in_governed_reference() -> None:
    api = json.loads(_text(API_REFERENCE))
    anchors = {item["anchor"] for item in api["symbols"]}

    expected = {"api-run-specs", "api-pipelinespace"}
    assert expected.issubset(anchors)

    center = _text(CENTER)
    for anchor in expected:
        assert f"#{anchor}" in center


def test_execution_routes_are_discoverable_across_site() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    faq = _text(FAQ)
    readme = _text(README)
    vocabulary = _text(VOCABULARY)
    troubleshooting = _text(TROUBLESHOOTING)

    assert layout.count("/docs/execution-ledger/") >= 3
    assert "/docs/guides/execution-ledger-recovery/" in layout
    assert "/docs/examples/execution-ledger-reconciliation/" in layout

    assert "[Execution Ledger & Recovery Center](execution-ledger/)" in docs
    assert "[Execution ledger and recovery]" in guides
    assert "Failure → repair → reconciliation →</a>" in examples
    assert "/assets/execution-state-reference.json" in reference
    assert "/docs/execution-ledger/" in compass
    assert "/docs/execution-ledger/" in faq
    assert "/docs/execution-ledger/" in readme
    assert "/docs/execution-ledger/" in vocabulary
    assert "/docs/execution-ledger/" in troubleshooting


def test_execution_reference_and_site_verifier_are_governed() -> None:
    source = _text(JSON_SOURCE)
    checker = _text(SITE_CHECK)

    assert "permalink: /assets/execution-state-reference.json" in source
    assert "{{ site.data.execution_states | jsonify }}" in source

    for contract in (
        "def _verify_execution_state_reference",
        "unexpected execution state catalog",
        "execution state signals mismatch",
        "_verify_execution_state_reference(site_root",
        '"docs/execution-ledger/index.html"',
        '"docs/guides/execution-ledger-recovery/index.html"',
        '"docs/examples/execution-ledger-reconciliation/index.html"',
        '"assets/execution-state-reference.json"',
        '"assets/css/execution-ledger.css"',
        '"assets/js/execution-ledger.js"',
    ):
        assert contract in checker
