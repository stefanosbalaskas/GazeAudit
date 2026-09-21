from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

import gazeaudit.publication as publication
from gazeaudit.conclusion import ConclusionRule


def _results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "specification": ["a", "b", "c"],
            "estimate": [10.0, 11.0, 9.0],
        }
    )


def _relative_rule() -> ConclusionRule:
    return ConclusionRule(
        relative_tolerance=0.20,
        require_sign=True,
        minimum_recovery_fraction=2 / 3,
    )


def _absolute_rule() -> ConclusionRule:
    return ConclusionRule(
        absolute_tolerance=2.0,
        require_sign=False,
        minimum_recovery_fraction=2 / 3,
    )


def _bundle(
    *,
    metadata: dict[str, object] | None = None,
) -> publication.PublicationAuditBundle:
    return publication.build_conclusion_audit_bundle(
        _results(),
        10.0,
        _relative_rule(),
        title="  Publication audit  ",
        endpoint="  median fixation contrast  ",
        source_description="  Synthetic declared specification space  ",
        metadata=metadata,
    )


def test_build_bundle_is_deterministic_and_copies_inputs() -> None:
    results = _results()

    metadata = {
        "integer": 2,
        "numpy_integer": np.int64(3),
        "finite": 1.5,
        "numpy_float": np.float64(2.5),
        "missing": np.nan,
        "pd_missing": pd.NA,
        "timestamp": pd.Timestamp("2026-09-21T00:00:00"),
        "array": np.array([1, 2, 3]),
        "tuple": ("a", 2),
        "list": [True, None, 4],
        "nested": {
            "value": np.float32(5.5),
        },
    }

    bundle = publication.build_conclusion_audit_bundle(
        results,
        10.0,
        _relative_rule(),
        title="  Publication audit  ",
        endpoint="  median fixation contrast  ",
        source_description="  Synthetic declared specification space  ",
        metadata=metadata,
    )

    assert bundle.title == "Publication audit"
    assert bundle.endpoint == "median fixation contrast"
    assert bundle.source_description == "Synthetic declared specification space"

    assert len(bundle.scientific_fingerprint) == 64
    assert len(bundle.bundle_fingerprint) == 64

    assert bundle.manifest["schema"] == "gazeaudit-publication-audit-v1"
    assert bundle.manifest["metadata"]["integer"] == 2
    assert bundle.manifest["metadata"]["numpy_integer"] == 3
    assert bundle.manifest["metadata"]["finite"] == 1.5
    assert bundle.manifest["metadata"]["numpy_float"] == 2.5
    assert bundle.manifest["metadata"]["missing"] is None
    assert bundle.manifest["metadata"]["pd_missing"] is None
    assert bundle.manifest["metadata"]["array"] == [1, 2, 3]
    assert bundle.manifest["metadata"]["tuple"] == ["a", 2]
    assert bundle.manifest["metadata"]["timestamp"] == "2026-09-21T00:00:00"

    assert "Conclusion recovery" in bundle.markdown
    assert "Interpretation guardrail" in bundle.markdown
    assert "relative-error tolerance" in bundle.methods_text
    assert "required recovery of the reference-effect direction" in bundle.methods_text

    assert publication.verify_publication_audit_bundle(bundle)
    assert publication.render_publication_markdown(bundle) == bundle.markdown

    manifest_json = bundle.manifest_json()
    assert bundle.scientific_fingerprint in manifest_json
    assert bundle.bundle_fingerprint in manifest_json

    # The builder must hold a deep copy of the specification table.
    results.loc[0, "estimate"] = 999.0
    assert bundle.specifications.loc[0, "estimate"] == 10.0


def test_build_bundle_supports_none_metadata() -> None:
    bundle = _bundle(metadata=None)

    assert bundle.metadata == {}
    assert publication.verify_publication_audit_bundle(bundle)


@pytest.mark.parametrize(
    ("field", "kwargs"),
    [
        (
            "title",
            {
                "title": "",
                "endpoint": "endpoint",
                "source_description": "source",
            },
        ),
        (
            "endpoint",
            {
                "title": "title",
                "endpoint": "   ",
                "source_description": "source",
            },
        ),
        (
            "source_description",
            {
                "title": "title",
                "endpoint": "endpoint",
                "source_description": "",
            },
        ),
    ],
)
def test_bundle_requires_nonempty_text(
    field: str,
    kwargs: dict[str, str],
) -> None:
    with pytest.raises(
        ValueError,
        match=field,
    ):
        publication.build_conclusion_audit_bundle(
            _results(),
            10.0,
            _relative_rule(),
            **kwargs,
        )


def test_nonempty_text_rejects_non_string() -> None:
    with pytest.raises(
        ValueError,
        match="demo",
    ):
        publication._nonempty_text(  # type: ignore[arg-type]
            123,
            "demo",
        )

    assert publication._nonempty_text(
        "  value  ",
        "demo",
    ) == "value"


def test_bundle_requires_conclusion_rule() -> None:
    with pytest.raises(
        TypeError,
        match="ConclusionRule",
    ):
        publication.build_conclusion_audit_bundle(
            _results(),
            10.0,
            object(),  # type: ignore[arg-type]
            title="title",
            endpoint="endpoint",
            source_description="source",
        )


@pytest.mark.parametrize(
    "value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_bundle_requires_finite_reference_effect(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="reference_effect",
    ):
        publication.build_conclusion_audit_bundle(
            _results(),
            value,
            _relative_rule(),
            title="title",
            endpoint="endpoint",
            source_description="source",
        )


def test_methods_support_absolute_only_rule_without_sign_requirement() -> None:
    rule = _absolute_rule()

    bundle = publication.build_conclusion_audit_bundle(
        _results(),
        10.0,
        rule,
        title="Absolute audit",
        endpoint="effect",
        source_description="synthetic",
    )

    assert "absolute-error tolerance of 2" in bundle.methods_text
    assert "without requiring recovery" in bundle.methods_text

    assert "- Relative-error tolerance: not used" in bundle.markdown
    assert "- Absolute-error tolerance: 2" in bundle.markdown
    assert "- Require reference-effect direction: no" in bundle.markdown

    assert publication.verify_publication_audit_bundle(bundle)


def test_methods_support_both_tolerances() -> None:
    rule = ConclusionRule(
        absolute_tolerance=2.0,
        relative_tolerance=0.20,
        require_sign=True,
        minimum_recovery_fraction=0.5,
    )

    bundle = publication.build_conclusion_audit_bundle(
        _results(),
        10.0,
        rule,
        title="Combined",
        endpoint="effect",
        source_description="synthetic",
    )

    assert "absolute-error tolerance of 2" in bundle.methods_text
    assert "relative-error tolerance of 20.0%" in bundle.methods_text

    assert publication.verify_publication_audit_bundle(bundle)


def test_render_methods_validates_inputs() -> None:
    bundle = _bundle()

    with pytest.raises(
        ValueError,
        match="endpoint",
    ):
        publication.render_publication_methods(
            bundle.summary,
            bundle.rule,
            endpoint=" ",
            reference_effect=10.0,
        )

    with pytest.raises(
        TypeError,
        match="ConclusionRule",
    ):
        publication.render_publication_methods(
            bundle.summary,
            object(),  # type: ignore[arg-type]
            endpoint="effect",
            reference_effect=10.0,
        )

    with pytest.raises(
        ValueError,
        match="reference_effect",
    ):
        publication.render_publication_methods(
            bundle.summary,
            bundle.rule,
            endpoint="effect",
            reference_effect=np.inf,
        )


def test_render_markdown_requires_bundle() -> None:
    with pytest.raises(
        TypeError,
        match="PublicationAuditBundle",
    ):
        publication.render_publication_markdown(
            object()  # type: ignore[arg-type]
        )


def test_verify_requires_bundle() -> None:
    with pytest.raises(
        TypeError,
        match="PublicationAuditBundle",
    ):
        publication.verify_publication_audit_bundle(
            object()  # type: ignore[arg-type]
        )


def test_verification_detects_recovery_tampering() -> None:
    bundle = _bundle()

    recovery = bundle.recovery.copy(deep=True)
    recovery.loc[0, "absolute_error"] = 999.0

    tampered = replace(
        bundle,
        recovery=recovery,
    )

    assert not publication.verify_publication_audit_bundle(tampered)


def test_verification_detects_summary_tampering() -> None:
    bundle = _bundle()

    summary = bundle.summary.copy()
    summary["classification"] = "tampered"

    tampered = replace(
        bundle,
        summary=summary,
    )

    assert not publication.verify_publication_audit_bundle(tampered)


def test_verification_rejects_non_mapping_software_record() -> None:
    bundle = _bundle()

    manifest = dict(bundle.manifest)
    manifest["software"] = "invalid"

    tampered = replace(
        bundle,
        manifest=manifest,
    )

    assert not publication.verify_publication_audit_bundle(tampered)


def test_verification_detects_manifest_tampering() -> None:
    bundle = _bundle()

    manifest = dict(bundle.manifest)
    manifest["title"] = "different"

    tampered = replace(
        bundle,
        manifest=manifest,
    )

    assert not publication.verify_publication_audit_bundle(tampered)


def test_verification_detects_methods_tampering() -> None:
    bundle = _bundle()

    tampered = replace(
        bundle,
        methods_text=bundle.methods_text + " tampered",
    )

    assert not publication.verify_publication_audit_bundle(tampered)


def test_verification_detects_markdown_tampering() -> None:
    bundle = _bundle()

    tampered = replace(
        bundle,
        markdown=bundle.markdown + "\ntampered\n",
    )

    assert not publication.verify_publication_audit_bundle(tampered)


def test_verification_fails_closed_for_missing_manifest_key() -> None:
    bundle = _bundle()

    manifest = dict(bundle.manifest)
    manifest.pop("estimate_column")

    tampered = replace(
        bundle,
        manifest=manifest,
    )

    assert not publication.verify_publication_audit_bundle(tampered)


def test_table_descriptor_validation_and_identity() -> None:
    frame = pd.DataFrame(
        {
            "x": [1, 2],
            "y": ["a", "b"],
        }
    )

    first = publication._table_descriptor(frame)
    second = publication._table_descriptor(frame.copy())

    assert first == second
    assert first["n_rows"] == 2
    assert first["columns"] == ["x", "y"]
    assert len(first["records_fingerprint"]) == 64

    with pytest.raises(
        TypeError,
        match="pandas DataFrames",
    ):
        publication._table_descriptor(
            []  # type: ignore[arg-type]
        )

    with pytest.raises(
        ValueError,
        match="at least one row",
    ):
        publication._table_descriptor(
            pd.DataFrame()
        )


def test_summary_mapping_validation() -> None:
    bundle = _bundle()

    mapping = publication._summary_mapping(
        bundle.summary
    )

    assert mapping["classification"] in {
        "robust",
        "fragile",
    }

    with pytest.raises(
        TypeError,
        match="pandas Series",
    ):
        publication._summary_mapping(
            {}  # type: ignore[arg-type]
        )

    incomplete = bundle.summary.drop(
        labels=["classification"]
    )

    with pytest.raises(
        ValueError,
        match="missing required values",
    ):
        publication._summary_mapping(
            incomplete
        )


def test_rule_mapping_is_json_safe() -> None:
    rule = ConclusionRule(
        relative_tolerance=0.20,
        absolute_tolerance=2.0,
        require_sign=False,
        minimum_recovery_fraction=0.75,
    )

    assert publication._rule_mapping(rule) == {
        "relative_tolerance": 0.20,
        "absolute_tolerance": 2.0,
        "require_sign": False,
        "minimum_recovery_fraction": 0.75,
    }


def test_safe_mapping_and_safe_value_cover_supported_types() -> None:
    timestamp = pd.Timestamp(
        "2026-09-21T12:34:56"
    )

    result = publication._safe_mapping(
        {
            "none": None,
            "string": "x",
            "bool": True,
            "integer": 1,
            "numpy_integer": np.int64(2),
            "finite_float": 1.25,
            "numpy_float": np.float64(2.5),
            "nan": np.nan,
            "pd_na": pd.NA,
            "mapping": {
                5: np.int32(6),
            },
            "list": [1, np.float32(2.5)],
            "tuple": ("x", False),
            "array": np.array(
                [
                    1,
                    2,
                ]
            ),
            "timestamp": timestamp,
        }
    )

    assert result == {
        "none": None,
        "string": "x",
        "bool": True,
        "integer": 1,
        "numpy_integer": 2,
        "finite_float": 1.25,
        "numpy_float": 2.5,
        "nan": None,
        "pd_na": None,
        "mapping": {
            "5": 6,
        },
        "list": [
            1,
            pytest.approx(2.5),
        ],
        "tuple": [
            "x",
            False,
        ],
        "array": [
            1,
            2,
        ],
        "timestamp": timestamp.isoformat(),
    }


@pytest.mark.parametrize(
    "value",
    [
        np.inf,
        -np.inf,
    ],
)
def test_safe_value_rejects_infinity(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="must not be infinite",
    ):
        publication._safe_value(value)


def test_safe_value_rejects_unsupported_object() -> None:
    class Unsupported:
        pass

    with pytest.raises(
        TypeError,
        match="unsupported publication provenance type",
    ):
        publication._safe_value(
            Unsupported()
        )


def test_build_manifest_is_deterministic() -> None:
    bundle = _bundle()

    rebuilt = publication._build_manifest(
        title=bundle.title,
        endpoint=bundle.endpoint,
        source_description=bundle.source_description,
        reference_effect=bundle.reference_effect,
        rule=bundle.rule,
        specifications=bundle.specifications,
        recovery=bundle.recovery,
        summary=bundle.summary,
        metadata=bundle.metadata,
        methods_text=bundle.methods_text,
        estimate_col="estimate",
        software=bundle.manifest["software"],
    )

    assert rebuilt == bundle.manifest


def test_markdown_explicitly_reports_unused_absolute_tolerance() -> None:
    bundle = _bundle()

    assert "- Absolute-error tolerance: not used" in bundle.markdown
    assert "- Require reference-effect direction: yes" in bundle.markdown