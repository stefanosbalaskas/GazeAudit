"""Frozen protocols for sampling-rate and missingness sensitivity studies.

Real-data sensitivity analyses create a particular researcher degree of freedom:
perturbation grids, missingness mechanisms, seeds, recovery tolerances, and
classification thresholds can all be changed after an outcome is visible.  This
module provides a small deterministic contract that binds those choices before
real-data endpoint inspection.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from typing import Any

from .provenance import canonical_json, fingerprint

SENSITIVITY_PROTOCOL_SCHEMA = "gazeaudit-sampling-missingness-protocol-v1"


def build_sampling_missingness_protocol(
    *,
    case_study_id: str,
    dataset: Mapping[str, Any],
    representation: Mapping[str, Any],
    endpoint: Mapping[str, Any],
    sampling: Mapping[str, Any],
    missingness: Mapping[str, Any],
    interpretation: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic pre-analysis sampling/missingness protocol.

    The returned document is canonicalized and fingerprinted.  Scientific
    choices remain transparent mappings so that the committed protocol can be
    inspected without reconstructing hidden Python objects.
    """

    identifier = str(case_study_id).strip()
    if not identifier:
        raise ValueError("case_study_id must be non-empty")

    fields = {
        "dataset": _canonical_mapping(dataset, name="dataset"),
        "representation": _canonical_mapping(representation, name="representation"),
        "endpoint": _canonical_mapping(endpoint, name="endpoint"),
        "sampling": _canonical_mapping(sampling, name="sampling"),
        "missingness": _canonical_mapping(missingness, name="missingness"),
        "interpretation": _canonical_mapping(interpretation, name="interpretation"),
    }
    _validate_fields(fields)

    core = {
        "schema": SENSITIVITY_PROTOCOL_SCHEMA,
        "case_study_id": identifier,
        **fields,
    }
    document = dict(core)
    document["protocol_fingerprint"] = fingerprint(core)
    return document


def verify_sampling_missingness_protocol(protocol: Mapping[str, Any]) -> bool:
    """Return whether a protocol is structurally valid and fingerprint-intact."""

    try:
        if not isinstance(protocol, Mapping):
            return False
        document = _canonical_mapping(protocol, name="protocol")
        if document.get("schema") != SENSITIVITY_PROTOCOL_SCHEMA:
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

        fields: dict[str, dict[str, Any]] = {}
        for name in (
            "dataset",
            "representation",
            "endpoint",
            "sampling",
            "missingness",
            "interpretation",
        ):
            value = core.get(name)
            if not isinstance(value, dict) or not value:
                return False
            fields[name] = value
        _validate_fields(fields)
        return True
    except (TypeError, ValueError, json.JSONDecodeError):
        return False


def _validate_fields(fields: Mapping[str, Mapping[str, Any]]) -> None:
    for name in (
        "dataset",
        "representation",
        "endpoint",
        "sampling",
        "missingness",
        "interpretation",
    ):
        _require_name(fields[name], name=name)
    _validate_sampling(fields["sampling"])
    _validate_missingness(fields["missingness"])
    _validate_interpretation(fields["interpretation"])


def _validate_sampling(value: Mapping[str, Any]) -> None:
    if "baseline_hz" not in value:
        raise ValueError("sampling must declare baseline_hz")
    if "target_hz" not in value:
        raise ValueError("sampling must declare target_hz")

    baseline = _positive_float(value["baseline_hz"], name="sampling baseline_hz")
    targets = _numeric_sequence(value["target_hz"], name="sampling target_hz")
    if not targets:
        raise ValueError("sampling target_hz must contain at least one value")
    if len(set(targets)) != len(targets):
        raise ValueError("sampling target_hz values must be unique")
    if any(rate <= 0.0 for rate in targets):
        raise ValueError("sampling target_hz values must be positive")
    if any(rate >= baseline for rate in targets):
        raise ValueError("sampling target_hz values must be below baseline_hz")


def _validate_missingness(value: Mapping[str, Any]) -> None:
    required = {"mechanisms", "fractions", "replicates", "rng_seed"}
    missing = required.difference(value)
    if missing:
        raise ValueError(f"missingness is missing required fields: {sorted(missing)}")

    mechanisms = value["mechanisms"]
    if isinstance(mechanisms, (str, bytes)) or not isinstance(mechanisms, Sequence):
        raise TypeError("missingness mechanisms must be a sequence")
    normalized_mechanisms = [str(item).strip() for item in mechanisms]
    if not normalized_mechanisms or any(not item for item in normalized_mechanisms):
        raise ValueError("missingness mechanisms must contain non-empty names")
    if len(set(normalized_mechanisms)) != len(normalized_mechanisms):
        raise ValueError("missingness mechanisms must be unique")

    fractions = _numeric_sequence(value["fractions"], name="missingness fractions")
    if not fractions:
        raise ValueError("missingness fractions must contain at least one value")
    if len(set(fractions)) != len(fractions):
        raise ValueError("missingness fractions must be unique")
    if any(not 0.0 < fraction < 1.0 for fraction in fractions):
        raise ValueError("missingness fractions must be strictly between 0 and 1")

    replicates = value["replicates"]
    if isinstance(replicates, bool) or not isinstance(replicates, int) or replicates < 2:
        raise ValueError("missingness replicates must be an integer >= 2")
    seed = value["rng_seed"]
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("missingness rng_seed must be an integer")


def _validate_interpretation(value: Mapping[str, Any]) -> None:
    required = {
        "relative_tolerance",
        "minimum_family_recovery",
        "material_fragility_ceiling",
    }
    missing = required.difference(value)
    if missing:
        raise ValueError(f"interpretation is missing required fields: {sorted(missing)}")

    tolerance = _finite_float(
        value["relative_tolerance"], name="interpretation relative_tolerance"
    )
    if tolerance < 0.0:
        raise ValueError("interpretation relative_tolerance must be non-negative")

    minimum = _probability(
        value["minimum_family_recovery"], name="interpretation minimum_family_recovery"
    )
    ceiling = _probability(
        value["material_fragility_ceiling"],
        name="interpretation material_fragility_ceiling",
    )
    if ceiling > minimum:
        raise ValueError(
            "interpretation material_fragility_ceiling must not exceed "
            "minimum_family_recovery"
        )


def _canonical_mapping(value: Mapping[str, Any], *, name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    if not value:
        raise ValueError(f"{name} must be non-empty")
    normalized = json.loads(canonical_json(dict(value)))
    if not isinstance(normalized, dict):
        raise TypeError(f"{name} must normalize to an object")
    return normalized


def _require_name(value: Mapping[str, Any], *, name: str) -> None:
    label = value.get("name")
    if not isinstance(label, str) or not label.strip():
        raise ValueError(f"{name} must declare a non-empty 'name'")


def _numeric_sequence(value: Any, *, name: str) -> list[float]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(f"{name} must be a sequence")
    return [_finite_float(item, name=name) for item in value]


def _positive_float(value: Any, *, name: str) -> float:
    result = _finite_float(value, name=name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _probability(value: Any, *, name: str) -> float:
    result = _finite_float(value, name=name)
    if not 0.0 <= result <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return result


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
