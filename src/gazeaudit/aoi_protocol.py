"""Frozen protocol contracts for AOI measurement-uncertainty case studies.

A real-data AOI uncertainty analysis should declare its scientific choices
before the uncertainty-adjusted endpoint distribution is inspected.  This
module provides a small, deterministic protocol document that binds dataset and
validation identities, AOI geometry, endpoint definition, error-model
specification, Monte Carlo settings, and the interpretation rule into one
fingerprinted object.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any

from .provenance import canonical_json, fingerprint

AOI_UNCERTAINTY_PROTOCOL_SCHEMA = "gazeaudit-aoi-uncertainty-protocol-v1"


def build_aoi_uncertainty_protocol(
    *,
    case_study_id: str,
    dataset: Mapping[str, Any],
    validation: Mapping[str, Any],
    aoi: Mapping[str, Any],
    endpoint: Mapping[str, Any],
    error_model: Mapping[str, Any],
    monte_carlo: Mapping[str, Any],
    interpretation: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic pre-analysis protocol for one AOI uncertainty study.

    The function intentionally accepts transparent mappings rather than hiding
    domain choices behind a large object hierarchy.  Every field is canonicalized
    and bound into ``protocol_fingerprint``.  The resulting document is suitable
    for committing before real-data endpoint inspection and later attaching to an
    archived uncertainty audit.

    ``monte_carlo`` must declare at least ``draws``, ``batch_size``, ``interval``,
    ``reference``, and ``rng_seed``.  A fixed seed is required because the first
    publication-oriented case study must be exactly reproducible.
    """

    identifier = str(case_study_id).strip()
    if not identifier:
        raise ValueError("case_study_id must be non-empty")

    fields = {
        "dataset": _canonical_mapping(dataset, name="dataset"),
        "validation": _canonical_mapping(validation, name="validation"),
        "aoi": _canonical_mapping(aoi, name="aoi"),
        "endpoint": _canonical_mapping(endpoint, name="endpoint"),
        "error_model": _canonical_mapping(error_model, name="error_model"),
        "monte_carlo": _canonical_mapping(monte_carlo, name="monte_carlo"),
        "interpretation": _canonical_mapping(interpretation, name="interpretation"),
    }
    _validate_required_identity(fields["dataset"], "dataset")
    _validate_required_identity(fields["validation"], "validation")
    _validate_required_identity(fields["aoi"], "aoi")
    _validate_required_identity(fields["endpoint"], "endpoint")
    _validate_monte_carlo(fields["monte_carlo"])

    core = {
        "schema": AOI_UNCERTAINTY_PROTOCOL_SCHEMA,
        "case_study_id": identifier,
        **fields,
    }
    document = dict(core)
    document["protocol_fingerprint"] = fingerprint(core)
    return document


def verify_aoi_uncertainty_protocol(protocol: Mapping[str, Any]) -> bool:
    """Return whether a protocol document is structurally valid and intact."""

    try:
        if not isinstance(protocol, Mapping):
            return False
        document = _canonical_mapping(protocol, name="protocol")
        if document.get("schema") != AOI_UNCERTAINTY_PROTOCOL_SCHEMA:
            return False
        stored = document.get("protocol_fingerprint")
        if not isinstance(stored, str) or len(stored) != 64:
            return False
        core = dict(document)
        core.pop("protocol_fingerprint", None)
        if stored != fingerprint(core):
            return False
        if not str(core.get("case_study_id", "")).strip():
            return False
        for name in (
            "dataset",
            "validation",
            "aoi",
            "endpoint",
            "error_model",
            "monte_carlo",
            "interpretation",
        ):
            if not isinstance(core.get(name), dict) or not core[name]:
                return False
        _validate_required_identity(core["dataset"], "dataset")
        _validate_required_identity(core["validation"], "validation")
        _validate_required_identity(core["aoi"], "aoi")
        _validate_required_identity(core["endpoint"], "endpoint")
        _validate_monte_carlo(core["monte_carlo"])
        return True
    except (TypeError, ValueError, json.JSONDecodeError):
        return False


def _canonical_mapping(value: Mapping[str, Any], *, name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    if not value:
        raise ValueError(f"{name} must be non-empty")
    # canonical_json already applies GazeAudit's finite-value and supported-type
    # guardrails.  Decoding yields a plain JSON-compatible object for storage.
    normalized = json.loads(canonical_json(dict(value)))
    if not isinstance(normalized, dict):
        raise TypeError(f"{name} must normalize to an object")
    return normalized


def _validate_required_identity(value: Mapping[str, Any], name: str) -> None:
    label = value.get("name")
    if not isinstance(label, str) or not label.strip():
        raise ValueError(f"{name} must declare a non-empty 'name'")


def _validate_monte_carlo(value: Mapping[str, Any]) -> None:
    required = {"draws", "batch_size", "interval", "reference", "rng_seed"}
    missing = required.difference(value)
    if missing:
        raise ValueError(f"monte_carlo is missing required fields: {sorted(missing)}")

    draws = value["draws"]
    batch_size = value["batch_size"]
    rng_seed = value["rng_seed"]
    if isinstance(draws, bool) or not isinstance(draws, int) or draws < 2:
        raise ValueError("monte_carlo draws must be an integer >= 2")
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size < 1:
        raise ValueError("monte_carlo batch_size must be an integer >= 1")
    if isinstance(rng_seed, bool) or not isinstance(rng_seed, int):
        raise ValueError("monte_carlo rng_seed must be an integer")

    interval = _finite_float(value["interval"], name="monte_carlo interval")
    if not 0.0 < interval < 1.0:
        raise ValueError("monte_carlo interval must be strictly between 0 and 1")
    _finite_float(value["reference"], name="monte_carlo reference")


def _finite_float(value: Any, *, name: str) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result
