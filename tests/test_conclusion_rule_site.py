import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    ConclusionRule,
    conclusion_recovery_table,
    summarize_conclusion_recovery,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "conclusion_rule_fields.yml"
JSON_SOURCE = ROOT / "assets" / "conclusion-rule-reference.json"
CENTER = ROOT / "docs" / "conclusion-rule.md"
GUIDE = ROOT / "docs" / "guides" / "conclusion-rule-design.md"
EXAMPLE = ROOT / "docs" / "examples" / "conclusion-rule-edge-cases.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "conclusion-rule.css"
JS = ROOT / "assets" / "js" / "conclusion-rule.js"
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
    "rule_name",
    "reference_type",
    "reference_effect",
    "reference_rationale",
    "relative_tolerance",
    "absolute_tolerance",
    "tolerance_rationale",
    "require_sign",
    "minimum_recovery_fraction",
    "decision_timing",
    "interpretation_boundary",
}

REQUIRED_FIELDS = EXPECTED_FIELDS - {
    "relative_tolerance",
    "absolute_tolerance",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _blocks() -> list[str]:
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


def test_conclusion_rule_catalog_has_exact_fields() -> None:
    blocks = _blocks()
    names = {_field(block, "name") for block in blocks}
    required = {
        _field(block, "name")
        for block in blocks
        if _field(block, "required") == "true"
    }

    assert len(blocks) == 11
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


def test_conclusion_rule_requires_at_least_one_tolerance() -> None:
    with pytest.raises(ValueError, match="at least one"):
        ConclusionRule()


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("absolute_tolerance", -1.0),
        ("relative_tolerance", -0.1),
        ("absolute_tolerance", float("inf")),
        ("relative_tolerance", float("nan")),
    ],
)
def test_conclusion_rule_rejects_invalid_tolerances(
    name: str,
    value: float,
) -> None:
    with pytest.raises(ValueError, match=name):
        ConclusionRule(**{name: value})


@pytest.mark.parametrize("value", [-0.01, 1.01, float("inf"), float("nan")])
def test_conclusion_rule_rejects_invalid_recovery_fraction(value: float) -> None:
    with pytest.raises(ValueError, match="minimum_recovery_fraction"):
        ConclusionRule(
            absolute_tolerance=1.0,
            minimum_recovery_fraction=value,
        )


def test_dual_tolerances_are_conjunctive() -> None:
    rule = ConclusionRule(
        absolute_tolerance=3.0,
        relative_tolerance=0.10,
        require_sign=True,
        minimum_recovery_fraction=1.0,
    )
    recovery = conclusion_recovery_table(
        pd.DataFrame({"estimate": [12.0]}),
        true_effect=10.0,
        rule=rule,
    )

    assert bool(recovery.loc[0, "absolute_tolerance_recovered"])
    assert not bool(recovery.loc[0, "relative_tolerance_recovered"])
    assert not bool(recovery.loc[0, "tolerance_recovered"])
    assert not bool(recovery.loc[0, "conclusion_recovered"])


def test_require_sign_is_separate_from_tolerance_recovery() -> None:
    results = pd.DataFrame({"estimate": [-10.0]})

    strict_rule = ConclusionRule(
        absolute_tolerance=25.0,
        require_sign=True,
        minimum_recovery_fraction=1.0,
    )
    strict = conclusion_recovery_table(
        results,
        true_effect=10.0,
        rule=strict_rule,
    )
    assert bool(strict.loc[0, "tolerance_recovered"])
    assert not bool(strict.loc[0, "sign_recovered"])
    assert not bool(strict.loc[0, "conclusion_recovered"])

    tolerance_only_rule = ConclusionRule(
        absolute_tolerance=25.0,
        require_sign=False,
        minimum_recovery_fraction=1.0,
    )
    relaxed = conclusion_recovery_table(
        results,
        true_effect=10.0,
        rule=tolerance_only_rule,
    )
    assert bool(relaxed.loc[0, "tolerance_recovered"])
    assert bool(relaxed.loc[0, "conclusion_recovered"])


def test_zero_reference_rejects_relative_tolerance() -> None:
    rule = ConclusionRule(
        relative_tolerance=0.10,
        require_sign=True,
        minimum_recovery_fraction=1.0,
    )
    with pytest.raises(ValueError, match="true_effect is zero"):
        conclusion_recovery_table(
            pd.DataFrame({"estimate": [0.0]}),
            true_effect=0.0,
            rule=rule,
        )


def test_zero_reference_absolute_tolerance_contract() -> None:
    rule = ConclusionRule(
        absolute_tolerance=0.5,
        require_sign=True,
        minimum_recovery_fraction=1.0,
    )
    recovery = conclusion_recovery_table(
        pd.DataFrame({"estimate": [0.2]}),
        true_effect=0.0,
        rule=rule,
    )

    assert np.isnan(recovery.loc[0, "relative_error"])
    assert np.isnan(recovery.loc[0, "effect_ratio"])
    assert bool(recovery.loc[0, "sign_recovered"])
    assert bool(recovery.loc[0, "tolerance_recovered"])
    assert bool(recovery.loc[0, "conclusion_recovered"])


def test_threshold_equality_is_robust_and_higher_cutoff_is_fragile() -> None:
    results = pd.DataFrame(
        {"estimate": [10.0, 10.5, 9.5, 11.0, 12.0]}
    )

    rule_080 = ConclusionRule(
        absolute_tolerance=1.0,
        require_sign=True,
        minimum_recovery_fraction=0.80,
    )
    recovery_080 = conclusion_recovery_table(
        results,
        true_effect=10.0,
        rule=rule_080,
    )
    summary_080 = summarize_conclusion_recovery(recovery_080, rule_080)

    assert summary_080["conclusion_recovery_fraction"] == pytest.approx(0.80)
    assert summary_080["classification"] == "robust"

    rule_081 = ConclusionRule(
        absolute_tolerance=1.0,
        require_sign=True,
        minimum_recovery_fraction=0.81,
    )
    recovery_081 = conclusion_recovery_table(
        results,
        true_effect=10.0,
        rule=rule_081,
    )
    summary_081 = summarize_conclusion_recovery(recovery_081, rule_081)

    assert summary_081["conclusion_recovery_fraction"] == pytest.approx(0.80)
    assert summary_081["classification"] == "fragile"


def test_center_has_no_hidden_scientific_defaults() -> None:
    center = _text(CENTER)
    js = _text(JS)

    assert "supplies no scientific defaults" in center
    assert '<option value="">Choose explicitly…</option>' in center
    assert "reference effect and tolerances must be justified independently" in center
    assert "relative_tolerance cannot be used when reference_effect is zero" in js

    assert "require_sign=\${pythonValue(values.require_sign)}" in js
    assert "minimum_recovery_fraction=" in js

    assert 'value="0.9"' not in center
    assert 'value="true"' not in center


def test_builder_is_accessible_and_validates_rule_contract() -> None:
    center = _text(CENTER)
    js = _text(JS)
    css = _text(CSS)

    for contract in (
        "data-conclusion-builder",
        "data-conclusion-errors",
        'role="alert"',
        'tabindex="-1"',
        "data-conclusion-status",
        'aria-live="polite"',
        "data-conclusion-copy",
    ):
        assert contract in center

    for contract in (
        "At least one of relative_tolerance or absolute_tolerance is required.",
        "must be non-negative",
        "minimum_recovery_fraction must be between 0 and 1",
        "aria-invalid",
        "errors.focus()",
        "navigator.clipboard.writeText",
    ):
        assert contract in js

    for contract in (
        ".conclusion-rule-grid",
        ".conclusion-rule-field",
        ".conclusion-errors",
        ".conclusion-output-grid",
        ":focus-visible",
        "@media (max-width: 820px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_guide_and_example_cover_scientific_boundaries() -> None:
    guide = _text(GUIDE)
    example = _text(EXAMPLE)

    for heading in (
        "Start with the reference effect, not the tolerance",
        "When both tolerances exist, both must pass",
        "Zero reference effects require absolute tolerance",
        "Sign recovery is separate from tolerance recovery",
        "Explicitly declare the across-specification threshold",
        "Do not confuse Python defaults with scientific recommendations",
        "Execution completeness still matters",
        "Classification is conditional, not universal",
        "Keep frozen validation labels separate",
        "Reviewer-requested conclusion rules need temporal provenance",
        "Reporting examples",
        "Common mistakes",
    ):
        assert heading in guide

    for phrase in (
        "Case 1 · A rule needs at least one tolerance",
        "Case 3 · Both tolerances mean AND, not OR",
        "Case 5 · Zero reference effects cannot use relative tolerance",
        "Case 6 · Equality at the recovery threshold passes",
        "Case 7 · Python defaults are not scientific defaults",
        "Case 8 · A circular real-data reference invalidates the interpretation",
        "Case 9 · Incomplete execution comes before classification",
        "Reuse boundary",
    ):
        assert phrase in example


def test_conclusion_rule_api_anchors_exist() -> None:
    api = json.loads(_text(API_REFERENCE))
    anchors = {item["anchor"] for item in api["symbols"]}

    expected = {
        "api-conclusionrule",
        "api-summarize-conclusion-recovery",
        "api-build-conclusion-audit-bundle",
        "api-verify-publication-audit-bundle",
    }
    assert expected.issubset(anchors)


def test_conclusion_rule_routes_are_discoverable() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    faq = _text(FAQ)
    readme = _text(README)

    assert layout.count("/docs/conclusion-rule/") >= 3
    assert "/docs/guides/conclusion-rule-design/" in layout
    assert "/docs/examples/conclusion-rule-edge-cases/" in layout
    assert "[Conclusion Rule Design Center]" in docs
    assert "[Design conclusion-recovery rules]" in guides
    assert "Conclusion-rule edge cases →</a>" in examples
    assert "/assets/conclusion-rule-reference.json" in reference
    assert "/docs/conclusion-rule/" in compass
    assert "/docs/conclusion-rule/" in faq
    assert "/docs/conclusion-rule/" in readme


def test_conclusion_reference_and_site_verifier_are_governed() -> None:
    source = _text(JSON_SOURCE)
    checker = _text(SITE_CHECK)

    assert "permalink: /assets/conclusion-rule-reference.json" in source
    assert "{{ site.data.conclusion_rule_fields | jsonify }}" in source

    for contract in (
        "def _verify_conclusion_rule_reference",
        "unexpected conclusion rule field catalog",
        "conclusion rule field names mismatch",
        "_verify_conclusion_rule_reference(site_root",
        '"docs/conclusion-rule/index.html"',
        '"docs/guides/conclusion-rule-design/index.html"',
        '"docs/examples/conclusion-rule-edge-cases/index.html"',
        '"assets/conclusion-rule-reference.json"',
        '"assets/css/conclusion-rule.css"',
        '"assets/js/conclusion-rule.js"',
    ):
        assert contract in checker
