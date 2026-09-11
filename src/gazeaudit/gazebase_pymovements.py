"""Compatibility preparation for the pymovements 0.28 GazeBase dataset contract.

pymovements 0.28 stores dataset file information as a mapping keyed by content
kind (for GazeBase, ``dataset.fileinfo['gaze']``), whereas the lower-level
GazeAudit frozen preparation routine consumes the gaze file-information table
directly. This module provides the public bridge without changing any frozen
scientific rule or source-data value.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gazebase_execution import PreparedGazeBaseData
from .gazebase_execution import prepare_gazebase_pymovements_dataset as _prepare_table_contract


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


def prepare_gazebase_pymovements_dataset(dataset: Any) -> PreparedGazeBaseData:
    """Prepare a loaded pymovements 0.28 GazeBase subset for frozen execution.

    Both the native pymovements 0.28 ``fileinfo`` mapping and the direct table
    form used by lightweight adapters/tests are accepted. If a mapping is
    supplied it must contain exactly the gaze metadata under the ``'gaze'`` key;
    no other content metadata can substitute for it.
    """

    fileinfo = getattr(dataset, "fileinfo", None)
    if isinstance(fileinfo, Mapping):
        if "gaze" not in fileinfo:
            raise ValueError("pymovements dataset.fileinfo is missing the 'gaze' table")
        dataset = _GazeFileinfoDatasetView(dataset, fileinfo["gaze"])
    return _prepare_table_contract(dataset)
