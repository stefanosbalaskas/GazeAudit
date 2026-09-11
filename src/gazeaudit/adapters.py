"""Interoperability protocols and normalized detector outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

import pandas as pd

from .study import GazeStudy


@runtime_checkable
class StudyAdapter(Protocol):
    """Protocol for adapters that convert external objects into :class:`GazeStudy`."""

    name: str

    def to_study(self, source: Any) -> GazeStudy:
        """Convert an external object into the canonical GazeAudit study representation."""


@runtime_checkable
class DetectorBackend(Protocol):
    """Protocol for detector backends used in analytical multiverses."""

    name: str

    def detect(self, study: GazeStudy) -> DetectionResult:
        """Run one detector backend on a canonical gaze study."""


@dataclass(frozen=True)
class DetectionResult:
    """Normalized sample labels and per-trial detector metadata.

    ``samples`` must retain the canonical participant, trial, and timestamp
    columns and add an ``event_label`` column. ``metadata`` is intentionally a
    separate table so detector-level provenance is not silently duplicated on
    every gaze sample.
    """

    samples: pd.DataFrame
    metadata: pd.DataFrame
    backend: str
    detector: str

    def __post_init__(self) -> None:
        if not isinstance(self.samples, pd.DataFrame):
            raise TypeError("samples must be a pandas DataFrame")
        if not isinstance(self.metadata, pd.DataFrame):
            raise TypeError("metadata must be a pandas DataFrame")
        if self.samples.empty:
            raise ValueError("samples must contain at least one row")
        if "event_label" not in self.samples.columns:
            raise ValueError("samples must contain an 'event_label' column")
        if not self.backend:
            raise ValueError("backend must be a non-empty string")
        if not self.detector:
            raise ValueError("detector must be a non-empty string")


def adapt_study(source: Any, adapter: StudyAdapter) -> GazeStudy:
    """Convert ``source`` through a user-supplied or built-in study adapter."""

    if not isinstance(adapter, StudyAdapter):
        raise TypeError("adapter must implement the StudyAdapter protocol")
    study = adapter.to_study(source)
    if not isinstance(study, GazeStudy):
        raise TypeError("study adapters must return a GazeStudy")
    return study


def run_detector_backend(study: GazeStudy, backend: DetectorBackend) -> DetectionResult:
    """Run a detector backend while enforcing the normalized result contract."""

    if not isinstance(study, GazeStudy):
        raise TypeError("study must be a GazeStudy")
    if not isinstance(backend, DetectorBackend):
        raise TypeError("backend must implement the DetectorBackend protocol")
    result = backend.detect(study)
    if not isinstance(result, DetectionResult):
        raise TypeError("detector backends must return a DetectionResult")
    return result
