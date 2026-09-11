"""Publication-oriented audit bundles for conclusion robustness analyses.

This module packages a predeclared conclusion-recovery analysis into deterministic
scientific and execution fingerprints plus reusable methods/report wording. It
does not choose specifications, optimize statistical significance, or interpret
an effect beyond the rule supplied by the researcher.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .conclusion import (
    ConclusionRule,
    conclusion_recovery_table,
    summarize_conclusion_recovery,
)
from .provenance import canonical_json, fingerprint, software_environment


@dataclass(frozen=True)
class PublicationAuditBundle:
    """Deterministic publication artifact for one conclusion-robustness audit.

    DataFrames are copied when the bundle is built. The manifest fingerprints
    bind the declared rule, reference effect, specification table, recovery
    table, summary, source description, and optional researcher metadata.
    """

    title: str
    endpoint: str
    source_description: str
    reference_effect: float
    rule: ConclusionRule
    specifications: pd.DataFrame
    recovery: pd.DataFrame
    summary: pd.Series
    metadata: dict[str, Any]
    methods_text: str
    manifest: dict[str, Any]
    markdown: str

    @property
    def scientific_fingerprint(self) -> str:
        """Stable identity of the scientific inputs and recovery outputs."""

        return str(self.manifest["scientific_fingerprint"])

    @property
    def bundle_fingerprint(self) -> str:
        """Stable identity of the complete manifest including software provenance."""

        return str(self.manifest["bundle_fingerprint"])

    def manifest_json(self) -> str:
        """Return the machine-readable manifest as canonical JSON."""

        return canonical_json(self.manifest)


def build_conclusion_audit_bundle(
    results: pd.DataFrame,
    reference_effect: float,
    rule: ConclusionRule,
    *,
    title: str,
    endpoint: str,
    source_description: str,
    estimate_col: str = "estimate",
    metadata: Mapping[str, Any] | None = None,
) -> PublicationAuditBundle:
    """Build an auditable publication bundle from a declared specification table.

    ``reference_effect`` may be known truth in simulation or a researcher-defined
    reference effect in a real-data robustness study. Its meaning should be made
    explicit in ``source_description`` or ``metadata``. GazeAudit does not infer
    or select a reference effect from the supplied results.
    """

    normalized_title = _nonempty_text(title, "title")
    normalized_endpoint = _nonempty_text(endpoint, "endpoint")
    normalized_source = _nonempty_text(source_description, "source_description")
    if not isinstance(rule, ConclusionRule):
        raise TypeError("rule must be a ConclusionRule")
    if not np.isfinite(reference_effect):
        raise ValueError("reference_effect must be finite")

    specifications = results.copy(deep=True)
    recovery = conclusion_recovery_table(
        specifications,
        float(reference_effect),
        rule,
        estimate_col=estimate_col,
    )
    summary = summarize_conclusion_recovery(recovery, rule)
    safe_metadata = _safe_mapping({} if metadata is None else metadata)

    methods_text = render_publication_methods(
        summary,
        rule,
        endpoint=normalized_endpoint,
        reference_effect=float(reference_effect),
    )
    manifest = _build_manifest(
        title=normalized_title,
        endpoint=normalized_endpoint,
        source_description=normalized_source,
        reference_effect=float(reference_effect),
        rule=rule,
        specifications=specifications,
        recovery=recovery,
        summary=summary,
        metadata=safe_metadata,
        methods_text=methods_text,
        estimate_col=estimate_col,
        software=software_environment(),
    )
    markdown = _render_markdown(
        title=normalized_title,
        endpoint=normalized_endpoint,
        source_description=normalized_source,
        reference_effect=float(reference_effect),
        rule=rule,
        summary=summary,
        methods_text=methods_text,
        manifest=manifest,
    )
    return PublicationAuditBundle(
        title=normalized_title,
        endpoint=normalized_endpoint,
        source_description=normalized_source,
        reference_effect=float(reference_effect),
        rule=rule,
        specifications=specifications,
        recovery=recovery,
        summary=summary.copy(),
        metadata=safe_metadata,
        methods_text=methods_text,
        manifest=manifest,
        markdown=markdown,
    )


def render_publication_methods(
    summary: pd.Series,
    rule: ConclusionRule,
    *,
    endpoint: str,
    reference_effect: float,
) -> str:
    """Render deterministic methods wording for a conclusion-recovery analysis."""

    normalized_endpoint = _nonempty_text(endpoint, "endpoint")
    if not isinstance(rule, ConclusionRule):
        raise TypeError("rule must be a ConclusionRule")
    if not np.isfinite(reference_effect):
        raise ValueError("reference_effect must be finite")
    summary_map = _summary_mapping(summary)

    tolerance_parts: list[str] = []
    if rule.absolute_tolerance is not None:
        tolerance_parts.append(
            f"an absolute-error tolerance of {rule.absolute_tolerance:.6g}"
        )
    if rule.relative_tolerance is not None:
        tolerance_parts.append(
            f"a relative-error tolerance of {rule.relative_tolerance:.1%}"
        )
    tolerance_text = " and ".join(tolerance_parts)
    sign_text = (
        "and required recovery of the reference-effect direction"
        if rule.require_sign
        else "without requiring recovery of the reference-effect direction"
    )
    return (
        f"GazeAudit evaluated {int(summary_map['n_specifications'])} predeclared "
        f"specifications for the endpoint '{normalized_endpoint}' against a reference "
        f"effect of {reference_effect:.6g}. Conclusion recovery was defined before "
        f"inspection of the robustness outputs using {tolerance_text}, {sign_text}. "
        f"The analysis was classified as robust only when at least "
        f"{rule.minimum_recovery_fraction:.1%} of supplied specifications recovered the "
        f"conclusion. The observed recovery fraction was "
        f"{float(summary_map['conclusion_recovery_fraction']):.1%}, yielding the "
        f"predeclared classification '{summary_map['classification']}'. Statistical "
        "significance and p-value optimization were not used to select specifications or "
        "define conclusion recovery. The classification applies only to the declared "
        "specification space."
    )


def render_publication_markdown(bundle: PublicationAuditBundle) -> str:
    """Re-render the deterministic Markdown report carried by a bundle."""

    if not isinstance(bundle, PublicationAuditBundle):
        raise TypeError("bundle must be a PublicationAuditBundle")
    return _render_markdown(
        title=bundle.title,
        endpoint=bundle.endpoint,
        source_description=bundle.source_description,
        reference_effect=bundle.reference_effect,
        rule=bundle.rule,
        summary=bundle.summary,
        methods_text=bundle.methods_text,
        manifest=bundle.manifest,
    )


def verify_publication_audit_bundle(bundle: PublicationAuditBundle) -> bool:
    """Return whether a bundle still matches its stored deterministic manifest.

    Verification recomputes recovery and fingerprints from the current bundle
    fields while preserving the software environment recorded at build time. A
    mutated specification table, recovery table, summary, rule, methods paragraph,
    or report therefore fails verification rather than retaining a stale identity.
    """

    if not isinstance(bundle, PublicationAuditBundle):
        raise TypeError("bundle must be a PublicationAuditBundle")
    try:
        recovered = conclusion_recovery_table(
            bundle.specifications,
            bundle.reference_effect,
            bundle.rule,
            estimate_col=str(bundle.manifest["estimate_column"]),
        )
        summary = summarize_conclusion_recovery(recovered, bundle.rule)
        if _table_descriptor(recovered) != _table_descriptor(bundle.recovery):
            return False
        if _summary_mapping(summary) != _summary_mapping(bundle.summary):
            return False
        methods_text = render_publication_methods(
            summary,
            bundle.rule,
            endpoint=bundle.endpoint,
            reference_effect=bundle.reference_effect,
        )
        stored_software = bundle.manifest.get("software")
        if not isinstance(stored_software, Mapping):
            return False
        expected_manifest = _build_manifest(
            title=bundle.title,
            endpoint=bundle.endpoint,
            source_description=bundle.source_description,
            reference_effect=bundle.reference_effect,
            rule=bundle.rule,
            specifications=bundle.specifications,
            recovery=recovered,
            summary=summary,
            metadata=bundle.metadata,
            methods_text=methods_text,
            estimate_col=str(bundle.manifest["estimate_column"]),
            software=_safe_mapping(stored_software),
        )
        if canonical_json(expected_manifest) != canonical_json(bundle.manifest):
            return False
        if methods_text != bundle.methods_text:
            return False
        expected_markdown = _render_markdown(
            title=bundle.title,
            endpoint=bundle.endpoint,
            source_description=bundle.source_description,
            reference_effect=bundle.reference_effect,
            rule=bundle.rule,
            summary=summary,
            methods_text=methods_text,
            manifest=expected_manifest,
        )
        return expected_markdown == bundle.markdown
    except (KeyError, TypeError, ValueError):
        return False


def _build_manifest(
    *,
    title: str,
    endpoint: str,
    source_description: str,
    reference_effect: float,
    rule: ConclusionRule,
    specifications: pd.DataFrame,
    recovery: pd.DataFrame,
    summary: pd.Series,
    metadata: Mapping[str, Any],
    methods_text: str,
    estimate_col: str,
    software: Mapping[str, Any],
) -> dict[str, Any]:
    scientific_core: dict[str, Any] = {
        "schema": "gazeaudit-publication-audit-v1",
        "title": title,
        "endpoint": endpoint,
        "source_description": source_description,
        "reference_effect": float(reference_effect),
        "rule": _rule_mapping(rule),
        "estimate_column": str(estimate_col),
        "metadata": _safe_mapping(metadata),
        "specifications": _table_descriptor(specifications),
        "recovery": _table_descriptor(recovery),
        "summary": _summary_mapping(summary),
        "methods_text_fingerprint": fingerprint(methods_text),
    }
    scientific_fingerprint = fingerprint(scientific_core)
    manifest = dict(scientific_core)
    manifest["scientific_fingerprint"] = scientific_fingerprint
    manifest["software"] = _safe_mapping(software)
    manifest["bundle_fingerprint"] = fingerprint(manifest)
    return manifest


def _rule_mapping(rule: ConclusionRule) -> dict[str, Any]:
    return {
        "relative_tolerance": rule.relative_tolerance,
        "absolute_tolerance": rule.absolute_tolerance,
        "require_sign": bool(rule.require_sign),
        "minimum_recovery_fraction": float(rule.minimum_recovery_fraction),
    }


def _table_descriptor(frame: pd.DataFrame) -> dict[str, Any]:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("audit tables must be pandas DataFrames")
    if frame.empty:
        raise ValueError("audit tables must contain at least one row")
    records = [_safe_mapping(record) for record in frame.to_dict(orient="records")]
    return {
        "columns": [str(column) for column in frame.columns],
        "n_rows": int(len(frame)),
        "records_fingerprint": fingerprint(records),
    }


def _summary_mapping(summary: pd.Series) -> dict[str, Any]:
    if not isinstance(summary, pd.Series):
        raise TypeError("summary must be a pandas Series")
    required = {
        "n_specifications",
        "conclusion_recovery_fraction",
        "sign_recovery_fraction",
        "sign_flip_fraction",
        "tolerance_recovery_fraction",
        "median_absolute_error",
        "max_absolute_error",
        "median_relative_error",
        "max_relative_error",
        "minimum_recovery_fraction",
        "classification",
    }
    missing = required.difference(summary.index)
    if missing:
        raise ValueError(f"summary is missing required values: {sorted(missing)}")
    return _safe_mapping({str(key): value for key, value in summary.items()})


def _safe_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): _safe_value(item) for key, item in value.items()}


def _safe_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, np.generic):
        return _safe_value(value.item())
    if isinstance(value, float):
        if np.isnan(value):
            return None
        if not np.isfinite(value):
            raise ValueError("publication provenance values must not be infinite")
        return value
    if isinstance(value, Mapping):
        return _safe_mapping(value)
    if isinstance(value, (list, tuple)):
        return [_safe_value(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_safe_value(item) for item in value.tolist()]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if pd.isna(value):
        return None
    raise TypeError(f"unsupported publication provenance type: {type(value).__name__}")


def _nonempty_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _render_markdown(
    *,
    title: str,
    endpoint: str,
    source_description: str,
    reference_effect: float,
    rule: ConclusionRule,
    summary: pd.Series,
    methods_text: str,
    manifest: Mapping[str, Any],
) -> str:
    summary_map = _summary_mapping(summary)
    relative = (
        "not used"
        if rule.relative_tolerance is None
        else f"{rule.relative_tolerance:.1%}"
    )
    absolute = (
        "not used"
        if rule.absolute_tolerance is None
        else f"{rule.absolute_tolerance:.6g}"
    )
    lines = [
        f"# {title}",
        "",
        "## Study provenance",
        "",
        f"- Endpoint: {endpoint}",
        f"- Source: {source_description}",
        f"- Reference effect: {reference_effect:.6g}",
        f"- Specifications evaluated: {int(summary_map['n_specifications'])}",
        "",
        "## Predeclared conclusion rule",
        "",
        f"- Relative-error tolerance: {relative}",
        f"- Absolute-error tolerance: {absolute}",
        f"- Require reference-effect direction: {'yes' if rule.require_sign else 'no'}",
        f"- Minimum recovery fraction: {rule.minimum_recovery_fraction:.1%}",
        "",
        "## Recovery summary",
        "",
        f"- Classification: **{summary_map['classification']}**",
        "- Conclusion recovery: "
        f"{float(summary_map['conclusion_recovery_fraction']):.1%}",
        f"- Sign recovery: {float(summary_map['sign_recovery_fraction']):.1%}",
        f"- Sign flips: {float(summary_map['sign_flip_fraction']):.1%}",
        "- Tolerance recovery: "
        f"{float(summary_map['tolerance_recovery_fraction']):.1%}",
        f"- Median absolute error: {float(summary_map['median_absolute_error']):.6g}",
        f"- Maximum absolute error: {float(summary_map['max_absolute_error']):.6g}",
        "",
        "## Methods wording",
        "",
        methods_text,
        "",
        "## Audit identity",
        "",
        f"- Scientific fingerprint: `{manifest['scientific_fingerprint']}`",
        f"- Bundle fingerprint: `{manifest['bundle_fingerprint']}`",
        "",
        "## Interpretation guardrail",
        "",
        "Specifications must be declared as scientifically defensible before robustness "
        "outputs are inspected. The robust/fragile classification applies only to the "
        "declared rule and supplied specification space. It is not a statistical-"
        "significance decision and does not establish that omitted analysis choices are "
        "irrelevant.",
        "",
    ]
    return "\n".join(lines)
