"""Deterministic provenance for GazeAudit specifications and audit results."""

from __future__ import annotations

import hashlib
import json
import platform
from collections.abc import Mapping
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import numpy as np
import pandas as pd


def canonical_json(value: Any) -> str:
    """Serialize supported scientific metadata deterministically as JSON."""

    normalized = _normalize(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def fingerprint(value: Any, *, algorithm: str = "sha256") -> str:
    """Return a stable hexadecimal fingerprint for canonical metadata."""

    try:
        digest = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(f"unsupported hash algorithm: {algorithm}") from exc
    digest.update(canonical_json(value).encode("utf-8"))
    return digest.hexdigest()


def specification_manifest(
    specification: Mapping[str, Any],
    *,
    endpoint: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a machine-readable manifest for one declared specification."""

    spec = _normalize(dict(specification))
    manifest: dict[str, Any] = {
        "schema": "gazeaudit-specification-v1",
        "specification": spec,
        "specification_fingerprint": fingerprint(spec),
    }
    if endpoint is not None:
        manifest["endpoint"] = str(endpoint)
    if metadata is not None:
        manifest["metadata"] = _normalize(dict(metadata))
    manifest["manifest_fingerprint"] = fingerprint(manifest)
    return manifest


def results_manifest(
    results: pd.DataFrame,
    *,
    estimate_col: str = "estimate",
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create deterministic provenance for a specification-results table.

    Row order is preserved because specification order can itself be part of the
    audit trail. DataFrame index labels are intentionally excluded.
    """

    if estimate_col not in results.columns:
        raise ValueError(f"column {estimate_col!r} is not present in results")
    if results.empty:
        raise ValueError("results must contain at least one row")

    records = [_normalize(record) for record in results.to_dict(orient="records")]
    manifest: dict[str, Any] = {
        "schema": "gazeaudit-results-v1",
        "estimate_column": estimate_col,
        "columns": [str(column) for column in results.columns],
        "n_rows": int(len(results)),
        "records_fingerprint": fingerprint(records),
        "software": software_environment(),
    }
    if metadata is not None:
        manifest["metadata"] = _normalize(dict(metadata))
    manifest["manifest_fingerprint"] = fingerprint(manifest)
    return manifest


def software_environment() -> dict[str, str]:
    """Return a compact, auditable software-environment record."""

    try:
        gazeaudit_version = version("gazeaudit")
    except PackageNotFoundError:
        gazeaudit_version = "uninstalled"
    return {
        "gazeaudit": gazeaudit_version,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "platform": platform.platform(),
    }


def _normalize(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not np.isfinite(value):
            raise ValueError("provenance values must be finite")
        return value
    if isinstance(value, np.generic):
        return _normalize(value.item())
    if isinstance(value, Mapping):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if isinstance(value, np.ndarray):
        return _normalize(value.tolist())
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if pd.isna(value):
        return None
    raise TypeError(f"unsupported provenance value type: {type(value).__name__}")
