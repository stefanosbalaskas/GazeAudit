"""Compatibility preparation for the pymovements 0.28 GazeBase dataset contract.

pymovements 0.28 stores dataset file information as a mapping keyed by content
kind (for GazeBase, ``dataset.fileinfo['gaze']``), whereas the lower-level
GazeAudit frozen preparation routine consumes the gaze file-information table
directly. This module provides the public bridge without changing any frozen
scientific rule or source-data value.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pandas as pd

from .gazebase_execution import PreparedGazeBaseData
from .gazebase_execution import prepare_gazebase_pymovements_dataset as _prepare_table_contract
from .provenance import fingerprint


class _GazeFileinfoDatasetView:
    """Narrow live view exposing the table contract expected by the frozen preparer."""

    def __init__(self, source: Any, gaze_fileinfo: Any) -> None:
        self._source = source
        self.fileinfo = gaze_fileinfo

    @property
    def gaze(self) -> Any:
        return self._source.gaze

    def deg2pix(self, **kwargs: Any) -> Any:
        converter = getattr(self._source, "deg2pix", None)
        if not callable(converter):
            raise TypeError("dataset must expose deg2pix() when pixel coordinates are absent")
        return converter(**kwargs)


def prepare_gazebase_pymovements_dataset(
    dataset: Any,
    *,
    require_content_hash: bool = False,
) -> PreparedGazeBaseData:
    """Prepare a loaded pymovements 0.28 GazeBase subset for frozen execution.

    Both the native pymovements 0.28 ``fileinfo`` mapping and the direct table
    form used by lightweight adapters/tests are accepted. If a mapping is
    supplied it must contain the gaze metadata under the ``'gaze'`` key.

    With ``require_content_hash=True``, every selected source CSV must resolve
    below ``dataset.paths.raw`` and is SHA-256 hashed before detector execution.
    The deterministic aggregate content fingerprint is then bound into the
    existing source identity and therefore into the execution/publication
    fingerprints. This is the mode used by the real-data CLI.
    """

    fileinfo = getattr(dataset, "fileinfo", None)
    native_mapping = isinstance(fileinfo, Mapping)
    gaze_fileinfo = fileinfo
    source_dataset = dataset
    if native_mapping:
        if "gaze" not in fileinfo:
            raise ValueError("pymovements dataset.fileinfo is missing the 'gaze' table")
        gaze_fileinfo = fileinfo["gaze"]
        dataset = _GazeFileinfoDatasetView(source_dataset, gaze_fileinfo)

    prepared = _prepare_table_contract(dataset)
    content_identity = _selected_file_content_identity(
        source_dataset,
        gaze_fileinfo,
        required=require_content_hash,
    )
    if not content_identity:
        return prepared
    return PreparedGazeBaseData(
        study=prepared.study,
        source_identity={**prepared.source_identity, **content_identity},
    )


def _selected_file_content_identity(
    dataset: Any,
    gaze_fileinfo: Any,
    *,
    required: bool,
) -> dict[str, Any]:
    paths = getattr(dataset, "paths", None)
    raw_root = getattr(paths, "raw", None)
    if raw_root is None:
        if required:
            raise ValueError(
                "content-bound GazeBase execution requires pymovements dataset.paths.raw"
            )
        return {}

    records = _fileinfo_records(gaze_fileinfo)
    if not records:
        if required:
            raise ValueError("content-bound GazeBase execution requires gaze fileinfo rows")
        return {}

    content_records: list[dict[str, Any]] = []
    total_bytes = 0
    for record in records:
        relative = record.get("filepath")
        if relative is None:
            if required:
                raise ValueError("GazeBase gaze fileinfo must contain filepath values")
            return {}
        relative_text = str(relative).replace("\\", "/")
        candidate = Path(relative_text)
        if not candidate.is_absolute():
            candidate = Path(raw_root) / candidate
        if not candidate.is_file():
            if required:
                raise FileNotFoundError(
                    f"selected GazeBase source file is not readable: {relative_text}"
                )
            return {}
        size = candidate.stat().st_size
        total_bytes += size
        content_records.append(
            {
                "filepath": relative_text,
                "size_bytes": size,
                "sha256": _sha256_file(candidate),
            }
        )

    content_records.sort(key=lambda item: item["filepath"])
    return {
        "selected_file_content_hash_algorithm": "sha256",
        "selected_file_content_count": len(content_records),
        "selected_file_content_bytes": total_bytes,
        "selected_file_content_fingerprint": fingerprint(content_records),
    }


def _fileinfo_records(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    to_dicts = getattr(value, "to_dicts", None)
    if callable(to_dicts):
        records = to_dicts()
        if isinstance(records, list):
            return [dict(record) for record in records]
    return []


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
