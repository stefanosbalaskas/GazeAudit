import json
import re
from dataclasses import fields
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    GazeStudy,
    ReadinessThresholds,
    evaluate_analysis_readiness,
    readiness_policy_table,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "readiness_thresholds.yml"
JSON_SOURCE = ROOT / "assets" / "readiness-threshold-reference.json"
CENTER = ROOT / "docs" / "readiness-policy.md"
GUIDE = ROOT / "docs" / "guides" / "readiness-policy-design.md"
EXAMPLE = ROOT / "docs" / "examples" / "readiness-policy-design.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "readiness-policy.css"
JS = ROOT / "assets" / "js" / "readiness-policy.js"
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
    "max_coordinate_issue_fraction",
    "max_timestamp_issue_fraction",
    "max_identifier_issue_fraction",
    "max_duplicate_timestamp_fraction",
    "max_flagged_trial_fraction",
    "min_rows_per_trial",
    "min_trials_per_participant",
    "require_monotonic_time",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _study() -> GazeStudy:
    rows: list[dict[str, object]] = []
    for participant_index, participant in enumerate(("P01", "P02", "P03")):
        for trial in (1, 2):
            for sample in range(24):
                rows.append(
                    {
                        "participant": participant,
                        "trial": trial,
                        "timestamp": sample * (1000.0 / 60.0),
                        "x": 0.25 + 0.045 * sample + 0.04 * participant_index,
                        "y": 0.55 + 0.12 * np.sin(sample / 4.0 + trial),
                    }
                )

    data = pd.DataFrame(rows)
    mask = (
        (data["participant"] == "P02")
        & (data["trial"] == 2)
        & (data.index % 11 == 0)
    )
    data.loc[mask, "x"] = np.nan

    duplicate_mask = (data["participant"] == "P03") & (data["trial"] == 1)
    duplicate_rows = data.loc[duplicate_mask].index[:2]
    data.loc[duplicate_rows[1], "timestamp"] = data.loc[
        duplicate_rows[0], "timestamp"
    ]

    disorder = data.index[
        (data["participant"] == "P01") & (data["trial"] == 2)
    ][10:12]
    data.loc[disorder, "timestamp"] = data.loc[
        disorder[::-1], "timestamp"
    ].to_numpy()
    return GazeStudy(data)


def _primary_policy() -> ReadinessThresholds:
    return ReadinessThresholds(
        max_coordinate_issue_fraction=0.05,
        max_duplicate_timestamp_fraction=0.05,
        max_flagged_trial_fraction=0.50,
        min_rows_per_trial=20,
        require_monotonic_time=True,
    )


def _alternative_policy() -> ReadinessThresholds:
    return ReadinessThresholds(
        max_coordinate_issue_fraction=0.10,
        max_duplicate_timestamp_fraction=0.10,
        max_flagged_trial_fraction=0.75,
        min_rows_per_trial=20,
        require_monotonic_time=True,
    )


def test_threshold_catalog_matches_public_dataclass_fields() -> None:
    text = _text(CATALOG)
    catalog_names = set(
        re.findall(r"^- name: ([a-z_]+)$", text, flags=re.MULTILINE)
    )
    runtime_names = {field.name for field in fields(ReadinessThresholds)}

    assert runtime_names == EXPECTED_FIELDS
    assert catalog_names == EXPECTED_FIELDS
    assert text.count("  value_type: fraction") == 5
    assert text.count("  value_type: integer") == 2
    assert text.count("  value_type: boolean") == 1

    for field in (
        "scope:",
        "comparator:",
        "metric:",
        "description:",
        "interpretation:",
        "boundary:",
    ):
        assert text.count(field) >= 8


def test_runtime_defaults_and_validation_match_builder_contract() -> None:
    empty = ReadinessThresholds()

    assert empty.active_rules == ()
    assert all(getattr(empty, name) is None for name in EXPECTED_FIELDS)
    assert ReadinessThresholds(require_monotonic_time=False).active_rules == ()
    assert ReadinessThresholds(require_monotonic_time=True).active_rules == (
        "require_monotonic_time",
    )

    with pytest.raises(ValueError):
        ReadinessThresholds(max_coordinate_issue_fraction=-0.01)
    with pytest.raises(ValueError):
        ReadinessThresholds(max_coordinate_issue_fraction=1.01)
    with pytest.raises(ValueError):
        ReadinessThresholds(min_rows_per_trial=0)
    with pytest.raises(ValueError):
        ReadinessThresholds(min_trials_per_participant=1.5)
    with pytest.raises(TypeError):
        ReadinessThresholds(require_monotonic_time="yes")  # type: ignore[arg-type]


def test_primary_worked_policy_reproduces_documented_cohort_impact() -> None:
    report = evaluate_analysis_readiness(
        _study(),
        _primary_policy(),
        policy_name="synthetic_primary",
    )
    impact = report.cohort_impact.set_index("scope")

    assert report.status == "review_under_policy"

    trial = impact.loc["trial"]
    assert int(trial["baseline_rows"]) == 144
    assert int(trial["retained_rows"]) == 72
    assert int(trial["retained_trial_units"]) == 3
    assert int(trial["retained_participant_units"]) == 3

    participant = impact.loc["participant"]
    assert int(participant["retained_rows"]) == 96
    assert int(participant["retained_trial_units"]) == 4
    assert int(participant["retained_participant_units"]) == 2


def test_alternative_worked_policy_changes_trial_but_not_participant_scope() -> None:
    report = evaluate_analysis_readiness(
        _study(),
        _alternative_policy(),
        policy_name="synthetic_alternative",
    )
    impact = report.cohort_impact.set_index("scope")

    assert report.status == "review_under_policy"

    trial = impact.loc["trial"]
    assert int(trial["retained_rows"]) == 120
    assert int(trial["retained_trial_units"]) == 5
    assert int(trial["retained_participant_units"]) == 3

    participant = impact.loc["participant"]
    assert int(participant["retained_rows"]) == 96
    assert int(participant["retained_trial_units"]) == 4
    assert int(participant["retained_participant_units"]) == 2


def test_policy_table_preserves_two_named_policies_and_fingerprints() -> None:
    table = readiness_policy_table(
        _study(),
        {
            "synthetic_primary": _primary_policy(),
            "synthetic_alternative": _alternative_policy(),
        },
    )

    assert table["policy"].tolist() == [
        "synthetic_primary",
        "synthetic_alternative",
    ]
    assert table["policy_fingerprint"].str.len().eq(64).all()
    assert table["policy_fingerprint"].nunique() == 2


def test_policy_center_has_no_prefilled_scientific_thresholds() -> None:
    text = _text(CENTER)

    assert "No scientific threshold is pre-filled." in text
    assert "Every readiness criterion starts inactive." in text
    assert "does not call" in text
    assert "filter_study_by_readiness()" in text
    assert "scope above is intentionally not selected by this builder" in text

    value_inputs = re.findall(
        r"<input(?:(?!<input).)*?data-readiness-value(?:(?!<input).)*?>",
        text,
        flags=re.DOTALL,
    )
    assert len(value_inputs) == 2
    assert all(" value=" not in block for block in value_inputs)


def test_policy_center_uses_accessible_native_form_contracts() -> None:
    text = _text(CENTER)

    for contract in (
        "data-readiness-builder",
        "<fieldset",
        "<legend>",
        "required",
        "data-readiness-errors",
        'role="alert"',
        "data-readiness-status",
        'role="status"',
        'aria-live="polite"',
        "data-readiness-active",
        "data-readiness-value",
        "data-readiness-copy",
    ):
        assert contract in text


def test_policy_builder_is_progressive_and_never_filters_data() -> None:
    js = _text(JS)
    css = _text(CSS)

    for contract in (
        "value.disabled = !active.checked",
        "value.required = active.checked",
        "schema: 'gazeaudit-readiness-policy-draft-v1'",
        "ReadinessThresholds,",
        "cohort_impact_preview,",
        "evaluate_analysis_readiness,",
        "No filtering was applied.",
        "navigator.clipboard.writeText",
    ):
        assert contract in js

    assert "filter_study_by_readiness" not in js

    for contract in (
        ".readiness-builder",
        ".readiness-rule-grid",
        ".readiness-rule-card",
        ".readiness-builder-errors",
        ".readiness-output-grid",
        ":focus-visible",
        "@media (max-width: 820px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_methodology_guide_covers_timing_scope_sensitivity_reporting_limits() -> None:
    text = _text(GUIDE)

    for heading in (
        "Separate observation from decision",
        "Give every active threshold a rationale source",
        "Understand which unit each rule evaluates",
        "Treat `max_flagged_trial_fraction` as a second-order rule",
        "Declare timing",
        "Preview cohort impact before filtering",
        "Keep filter scope as a separate decision",
        "Compare nearby defensible alternatives",
        "Read `active_rules` correctly",
        "Interpret the three readiness statuses",
        "Preserve provenance",
        "Interpretation checklist",
        "Reporting examples",
        "Reporting mistakes to avoid",
        "Limitations of readiness governance",
    ):
        assert heading.replace("`", chr(96)) in text

    assert "GazeAudit deliberately supplies no scientific defaults." in text
    assert "Do not relabel a later sensitivity threshold" in text
    assert "Do not add arbitrary threshold levels" in text


def test_worked_example_is_synthetic_bounded_and_runtime_consistent() -> None:
    text = _text(EXAMPLE)

    for contract in (
        'example_data: "Synthetic"',
        'example_focus: "Data & QC"',
        "Do not copy the thresholds.",
        "**72 / 144 rows**",
        "**3 / 6 trial units**",
        "**96 / 144 rows**",
        "**2 / 3 participants**",
        "**120 / 144 rows**",
        "**5 / 6 trial units**",
        "These numbers belong only to this deterministic teaching fixture.",
        "Reuse boundary",
    ):
        assert contract in text


def test_readiness_api_links_resolve_to_governed_api_anchors() -> None:
    center = _text(CENTER)
    api = json.loads(_text(API_REFERENCE))
    anchors = {item["anchor"] for item in api["symbols"]}

    expected = {
        "api-readinessthresholds",
        "api-evaluate-analysis-readiness",
        "api-cohort-impact-preview",
        "api-readiness-policy-table",
    }
    assert expected.issubset(anchors)
    for anchor in expected:
        assert f"#{anchor}" in center


def test_readiness_policy_routes_are_discoverable() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    faq = _text(FAQ)
    readme = _text(README)

    assert layout.count("/docs/readiness-policy/") >= 3
    assert "/docs/guides/readiness-policy-design/" in layout
    assert "/docs/examples/readiness-policy-design/" in layout
    assert "[Readiness Policy Design Center](readiness-policy/)" in docs
    assert "[Design and audit readiness policies]" in guides
    assert 'href="readiness-policy-design/">Readiness policy design →</a>' in examples
    assert "/assets/readiness-threshold-reference.json" in reference
    assert "/docs/readiness-policy/" in compass
    assert "/docs/readiness-policy/" in faq
    assert "/docs/readiness-policy/" in readme


def test_threshold_reference_is_generated_from_single_catalog() -> None:
    text = _text(JSON_SOURCE)
    checker = _text(SITE_CHECK)

    assert "permalink: /assets/readiness-threshold-reference.json" in text
    assert "{{ site.data.readiness_thresholds | jsonify }}" in text
    assert '"assets/readiness-threshold-reference.json"' in checker
