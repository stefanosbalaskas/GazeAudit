import json

import numpy as np
import pandas as pd
import pytest

from gazeaudit import ConclusionRule
from gazeaudit.publication import (
    build_conclusion_audit_bundle,
    render_publication_markdown,
    verify_publication_audit_bundle,
)


def _results():
    return pd.DataFrame(
        {
            "method": ["hard", "probabilistic", "probabilistic", "hard"],
            "error_scale": [np.nan, 0.5, 1.5, np.nan],
            "missing_fraction": [0.0, 0.0, 0.1, 0.1],
            "estimate": [9.5, 10.2, 8.7, 8.4],
        }
    )


def _rule():
    return ConclusionRule(
        relative_tolerance=0.20,
        require_sign=True,
        minimum_recovery_fraction=0.75,
    )


def _bundle(results=None, rule=None):
    return build_conclusion_audit_bundle(
        _results() if results is None else results,
        10.0,
        _rule() if rule is None else rule,
        title="Example robustness audit",
        endpoint="treatment-minus-control dwell",
        source_description="Synthetic known-truth validation fixture",
        metadata={"design": "repeated-measures", "preregistered": True},
    )


def test_publication_bundle_is_deterministic_and_verifiable():
    first = _bundle()
    second = _bundle()

    assert first.scientific_fingerprint == second.scientific_fingerprint
    assert first.bundle_fingerprint == second.bundle_fingerprint
    assert first.manifest_json() == second.manifest_json()
    assert first.markdown == second.markdown
    assert verify_publication_audit_bundle(first)


def test_manifest_is_canonical_json_and_handles_not_applicable_nan():
    bundle = _bundle()
    parsed = json.loads(bundle.manifest_json())

    assert parsed["schema"] == "gazeaudit-publication-audit-v1"
    assert parsed["specifications"]["n_rows"] == 4
    assert len(parsed["specifications"]["records_fingerprint"]) == 64
    assert len(parsed["scientific_fingerprint"]) == 64
    assert len(parsed["bundle_fingerprint"]) == 64


def test_changed_result_changes_scientific_identity():
    original = _bundle()
    changed = _results()
    changed.loc[0, "estimate"] = 7.0
    revised = _bundle(changed)

    assert revised.scientific_fingerprint != original.scientific_fingerprint
    assert revised.bundle_fingerprint != original.bundle_fingerprint


def test_changed_rule_changes_scientific_identity():
    original = _bundle()
    stricter = ConclusionRule(
        relative_tolerance=0.10,
        require_sign=True,
        minimum_recovery_fraction=0.90,
    )
    revised = _bundle(rule=stricter)

    assert revised.scientific_fingerprint != original.scientific_fingerprint
    assert revised.manifest["rule"]["relative_tolerance"] == 0.10
    assert revised.manifest["rule"]["minimum_recovery_fraction"] == 0.90


def test_bundle_does_not_use_significance_as_recovery_rule():
    results = _results().assign(p_value=[0.001, 0.80, 0.04, 0.90])
    bundle = _bundle(results)

    assert bundle.summary["conclusion_recovery_fraction"] == pytest.approx(1.0)
    assert "Statistical significance and p-value optimization were not used" in bundle.methods_text
    assert "statistical-significance decision" in bundle.markdown


def test_methods_and_markdown_report_predeclared_rule_and_scope():
    bundle = _bundle()

    assert "4 predeclared specifications" in bundle.methods_text
    assert "relative-error tolerance of 20.0%" in bundle.methods_text
    assert "at least 75.0%" in bundle.methods_text
    assert "applies only to the declared specification space" in bundle.methods_text
    assert "Scientific fingerprint" in bundle.markdown
    assert bundle.scientific_fingerprint in bundle.markdown
    assert render_publication_markdown(bundle) == bundle.markdown


def test_absolute_and_relative_tolerances_are_both_reported():
    rule = ConclusionRule(
        relative_tolerance=0.20,
        absolute_tolerance=2.0,
        require_sign=False,
        minimum_recovery_fraction=0.50,
    )
    bundle = _bundle(rule=rule)

    assert "absolute-error tolerance of 2" in bundle.methods_text
    assert "relative-error tolerance of 20.0%" in bundle.methods_text
    assert "without requiring recovery" in bundle.methods_text
    assert "Absolute-error tolerance: 2" in bundle.markdown


def test_bundle_requires_explicit_publication_provenance_text():
    with pytest.raises(ValueError, match="title"):
        build_conclusion_audit_bundle(
            _results(),
            10.0,
            _rule(),
            title=" ",
            endpoint="dwell",
            source_description="fixture",
        )
    with pytest.raises(ValueError, match="endpoint"):
        build_conclusion_audit_bundle(
            _results(),
            10.0,
            _rule(),
            title="audit",
            endpoint="",
            source_description="fixture",
        )
    with pytest.raises(ValueError, match="source_description"):
        build_conclusion_audit_bundle(
            _results(),
            10.0,
            _rule(),
            title="audit",
            endpoint="dwell",
            source_description="",
        )


def test_bundle_rejects_nonfinite_reference_and_wrong_rule_type():
    with pytest.raises(ValueError, match="reference_effect"):
        build_conclusion_audit_bundle(
            _results(),
            np.inf,
            _rule(),
            title="audit",
            endpoint="dwell",
            source_description="fixture",
        )
    with pytest.raises(TypeError, match="ConclusionRule"):
        build_conclusion_audit_bundle(
            _results(),
            10.0,
            object(),
            title="audit",
            endpoint="dwell",
            source_description="fixture",
        )


def test_verification_detects_mutated_specification_table():
    bundle = _bundle()
    bundle.specifications.loc[0, "estimate"] = 3.0

    assert not verify_publication_audit_bundle(bundle)


def test_verification_detects_mutated_recovery_or_summary_table():
    recovery_bundle = _bundle()
    recovery_bundle.recovery.loc[0, "absolute_error"] = 999.0
    assert not verify_publication_audit_bundle(recovery_bundle)

    summary_bundle = _bundle()
    summary_bundle.summary.loc["classification"] = "fragile"
    assert not verify_publication_audit_bundle(summary_bundle)


def test_infinite_metadata_fails_closed():
    with pytest.raises(ValueError, match="must not be infinite"):
        build_conclusion_audit_bundle(
            _results(),
            10.0,
            _rule(),
            title="audit",
            endpoint="dwell",
            source_description="fixture",
            metadata={"bad_value": np.inf},
        )
