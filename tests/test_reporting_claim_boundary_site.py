import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from gazeaudit import (
    GazeStudy,
    ReadinessThresholds,
    audit_study_qc,
    evaluate_analysis_readiness,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "reporting_contracts.yml"
JSON_SOURCE = ROOT / "assets" / "reporting-contract-reference.json"
CENTER = ROOT / "docs" / "reporting-center.md"
GUIDE = ROOT / "docs" / "guides" / "claim-boundary-reporting.md"
EXAMPLE = ROOT / "docs" / "examples" / "reporting-language-rewrite.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "reporting-center.css"
JS = ROOT / "assets" / "js" / "reporting-center.js"
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
    "structural-pass",
    "structural-review",
    "readiness-unassessed",
    "readiness-ready",
    "readiness-review",
    "robustness-complete-stable",
    "robustness-magnitude-sensitive",
    "robustness-sign-sensitive",
    "robustness-incomplete",
    "sensitivity-descriptive",
    "frozen-validation-labels",
}

EXPECTED_RUNTIME_SIGNALS = {
    "pass",
    "review",
    "unassessed",
    "ready_under_policy",
    "review_under_policy",
}

FROZEN_LABELS = {
    "incomplete",
    "robust_negative",
    "materially_fragile",
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


def _clean_study() -> GazeStudy:
    return GazeStudy(
        pd.DataFrame(
            {
                "participant": ["P01", "P01", "P01"],
                "trial": [1, 1, 1],
                "timestamp": [0.0, 16.7, 33.4],
                "x": [100.0, 101.0, 102.0],
                "y": [50.0, 51.0, 52.0],
            }
        )
    )


def _review_study() -> GazeStudy:
    data = _clean_study().data.copy()
    data.loc[1, "x"] = np.nan
    return GazeStudy(data)


def test_catalog_has_governed_layers_kinds_and_ids() -> None:
    blocks = _catalog_blocks()
    ids = {_field(block, "id") for block in blocks}
    kinds = [_field(block, "kind") for block in blocks]
    layers = [_field(block, "layer") for block in blocks]

    assert len(blocks) == 11
    assert ids == EXPECTED_IDS
    assert kinds.count("Runtime status") == 5
    assert kinds.count("Interpretation pattern") == 5
    assert kinds.count("Protocol-bound evidence label") == 1

    assert layers.count("Structural QC") == 2
    assert layers.count("Readiness") == 3
    assert layers.count("Robustness") == 4
    assert layers.count("Sensitivity") == 1
    assert layers.count("Frozen evidence") == 1


def test_runtime_status_cards_match_actual_runtime_statuses() -> None:
    clean = _clean_study()
    review = _review_study()

    observed = {
        audit_study_qc(clean).status,
        audit_study_qc(review).status,
        evaluate_analysis_readiness(
            clean,
            ReadinessThresholds(),
        ).status,
        evaluate_analysis_readiness(
            clean,
            ReadinessThresholds(max_coordinate_issue_fraction=0.0),
        ).status,
        evaluate_analysis_readiness(
            review,
            ReadinessThresholds(max_coordinate_issue_fraction=0.0),
        ).status,
    }
    assert observed == EXPECTED_RUNTIME_SIGNALS

    runtime_signals = {
        _field(block, "signal")
        for block in _catalog_blocks()
        if _field(block, "kind") == "Runtime status"
    }
    assert runtime_signals == EXPECTED_RUNTIME_SIGNALS


def test_interpretation_patterns_are_not_runtime_statuses() -> None:
    blocks = _catalog_blocks()
    pattern_signals = {
        _field(block, "signal")
        for block in blocks
        if _field(block, "kind") == "Interpretation pattern"
    }

    assert pattern_signals.isdisjoint(EXPECTED_RUNTIME_SIGNALS)
    assert len(pattern_signals) == 5

    for block in blocks:
        if _field(block, "kind") == "Interpretation pattern":
            assert "runtime_source:" in block
            assert "denominator:" in block
            assert "cannot_say:" in block


def test_frozen_labels_are_confined_to_protocol_bound_contract() -> None:
    frozen_blocks = [
        block
        for block in _catalog_blocks()
        if _field(block, "kind") == "Protocol-bound evidence label"
    ]
    assert len(frozen_blocks) == 1

    signal = _field(frozen_blocks[0], "signal")
    for label in FROZEN_LABELS:
        assert label in signal

    assert "not generic runtime statuses" in frozen_blocks[0]


def test_every_reporting_contract_has_claim_and_template_boundaries() -> None:
    required = (
        "runtime_source:",
        "meaning:",
        "denominator:",
        "can_say:",
        "cannot_say:",
        "methods_template:",
        "results_template:",
        "limitation_template:",
        "guide_url:",
        "example_url:",
        "api_anchor:",
    )

    for block in _catalog_blocks():
        for field in required:
            assert field in block


def test_reporting_center_is_progressive_accessible_and_filterable() -> None:
    text = _text(CENTER)

    for contract in (
        "page_type: reporting-center",
        "site.data.reporting_contracts",
        "data-reporting-controls",
        "data-reporting-search",
        "data-reporting-layer",
        "data-reporting-kind",
        "data-reporting-status",
        'role="status"',
        'aria-live="polite"',
        "data-reporting-contract",
        "data-reporting-template",
        "data-reporting-copy",
        "All remain visible when JavaScript is unavailable.",
        "Runtime status ≠ interpretation pattern ≠ frozen label",
    ):
        assert contract in text

    assert "A card can show what a given evidence state licenses you to report" in text
    assert "This center constrains claims; it does not make" in text


def test_reporting_center_filters_and_copy_actions_are_progressive() -> None:
    js = _text(JS)
    css = _text(CSS)

    for contract in (
        "data-reporting-contracts",
        "data-reporting-contract",
        "card.hidden = !show",
        "Showing ${visible} of ${total} reporting contracts.",
        "navigator.clipboard.writeText",
        "Copy was unavailable.",
        "search.focus()",
    ):
        assert contract in js

    for contract in (
        ".reporting-center-controls",
        ".reporting-contract-grid",
        ".reporting-contract-card",
        ".reporting-claim-grid",
        ".reporting-claim-boundary",
        ".reporting-contract-routes",
        ":focus-visible",
        "@media (max-width: 760px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_claim_boundary_guide_covers_denominator_inference_and_timing() -> None:
    text = _text(GUIDE)

    for heading in (
        "Identify the evidence object before the adjective",
        "Distinguish three kinds of labels",
        "Preserve the denominator before writing the result",
        "Use a claim ladder",
        "Keep Methods and Results roles distinct",
        "Add the limitation next to the claim",
        "Do not upgrade descriptive quantities into inference",
        "Report incomplete execution before reporting robustness",
        "Preserve temporal evidence layers",
        "Treat “no issue” and “no evidence” differently",
        "Reporting structural-QC evidence",
        "Reporting readiness evidence",
        "Reporting specification robustness",
        "Reporting sensitivity",
        "Reporting frozen validation evidence",
        "Final claim-boundary checklist",
    ):
        assert heading in text

    assert "Sign fractions are not posterior probabilities" in text
    assert "Sensitivity ratios are not causal variance shares" in text
    assert "Pairwise sensitivity is not an inferential interaction test" in text


def test_reporting_rewrite_example_repairs_seven_overclaims() -> None:
    text = _text(EXAMPLE)

    assert 'example_data: "Synthetic"' in text
    assert 'example_focus: "Interpretation & reporting"' in text
    assert "seven **synthetic over-claims**" in text
    assert text.count("### Too strong") == 7
    assert text.count("### Bounded rewrite") == 7
    assert text.count("### Limitation") == 7

    for phrase in (
        "Structural §review§ is not “bad data”",
        "§ready_under_policy§ is not universal quality",
        "§unassessed§ is not “all included”",
        "Stable direction can coexist with unstable magnitude",
        "Six successful branches do not become a six-branch denominator",
        "Sensitivity is descriptive, not causal attribution",
        "Frozen validation labels do not transfer",
    ):
        assert phrase.replace("§", chr(96)) in text


def test_catalog_api_anchors_exist_in_governed_api_reference() -> None:
    api = json.loads(_text(API_REFERENCE))
    anchors = {item["anchor"] for item in api["symbols"]}

    catalog_anchors = {
        _field(block, "api_anchor")
        for block in _catalog_blocks()
        if _field(block, "api_anchor")
    }
    assert catalog_anchors
    assert catalog_anchors.issubset(anchors)


def test_reporting_routes_are_discoverable_across_site() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    faq = _text(FAQ)
    readme = _text(README)

    assert layout.count("/docs/reporting-center/") >= 3
    assert "/docs/guides/claim-boundary-reporting/" in layout
    assert "/docs/examples/reporting-language-rewrite/" in layout

    assert "[Results Interpretation & Reporting Center](reporting-center/)" in docs
    assert "[Claim-boundary reporting]" in guides
    assert (
        'href="reporting-language-rewrite/">Reporting-language rewrite →</a>'
        in examples
    )
    assert "/assets/reporting-contract-reference.json" in reference
    assert "/docs/reporting-center/" in compass
    assert "/docs/reporting-center/" in faq
    assert "/docs/reporting-center/" in readme


def test_reporting_reference_and_site_verifier_are_governed() -> None:
    source = _text(JSON_SOURCE)
    checker = _text(SITE_CHECK)

    assert "permalink: /assets/reporting-contract-reference.json" in source
    assert "{{ site.data.reporting_contracts | jsonify }}" in source

    for contract in (
        "def _verify_reporting_contract_reference",
        "unexpected reporting contract catalog",
        "reporting runtime signals mismatch",
        "_verify_reporting_contract_reference(site_root",
        '"docs/reporting-center/index.html"',
        '"docs/guides/claim-boundary-reporting/index.html"',
        '"docs/examples/reporting-language-rewrite/index.html"',
        '"assets/reporting-contract-reference.json"',
        '"assets/css/reporting-center.css"',
        '"assets/js/reporting-center.js"',
    ):
        assert contract in checker
