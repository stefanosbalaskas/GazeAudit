"""pEYES detector interoperability for GazeAudit.

This module targets the pEYES 0.2 public detector contract. Imports are lazy so
GazeAudit remains usable on Python versions where pEYES is unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .adapters import DetectionResult
from .study import GazeStudy


@dataclass(frozen=True)
class PeyesDetectorAdapter:
    """Run a pEYES-compatible detector on each participant-by-trial stream.

    The wrapped detector must expose ``detect(t, x, y, viewer_distance_cm,
    pixel_size_cm)`` and return ``(labels, metadata)``. This is the public
    ``BaseDetector.detect`` contract in pEYES 0.2.x.
    """

    detector: Any
    viewer_distance_cm: float
    pixel_size_cm: float
    timestamp_unit: str = "ms"
    coordinate_unit: str = "px"
    label_column: str = "event_label"
    code_column: str = "event_code"
    name: str = "peyes"

    def __post_init__(self) -> None:
        if not callable(getattr(self.detector, "detect", None)):
            raise TypeError("detector must expose a callable detect() method")
        if not np.isfinite(self.viewer_distance_cm) or self.viewer_distance_cm <= 0:
            raise ValueError("viewer_distance_cm must be finite and positive")
        if not np.isfinite(self.pixel_size_cm) or self.pixel_size_cm <= 0:
            raise ValueError("pixel_size_cm must be finite and positive")
        if self.coordinate_unit != "px":
            raise ValueError("pEYES detector interoperability currently requires pixel coordinates")
        _time_factor(self.timestamp_unit)
        if not self.label_column:
            raise ValueError("label_column must be non-empty")
        if not self.code_column:
            raise ValueError("code_column must be non-empty")

    def detect(self, study: GazeStudy) -> DetectionResult:
        """Run the detector groupwise and normalize labels plus metadata."""

        study.validate_time_order()
        output = study.data.copy()
        output[self.label_column] = pd.Series(pd.NA, index=output.index, dtype="object")
        output[self.code_column] = pd.Series(pd.NA, index=output.index, dtype="Int64")

        metadata_rows: list[dict[str, Any]] = []
        grouped = output.groupby([study.participant, study.trial], sort=False, dropna=False)
        for key, frame in grouped:
            participant_value, trial_value = _group_key(key)
            timestamps = pd.to_numeric(frame[study.timestamp], errors="coerce").to_numpy(dtype=float)
            if np.any(~np.isfinite(timestamps)):
                raise ValueError("pEYES detector timestamps must be finite")
            timestamps_ms = timestamps * _time_factor(self.timestamp_unit)
            if timestamps_ms.size > 1 and np.any(np.diff(timestamps_ms) <= 0):
                raise ValueError(
                    "pEYES requires strictly increasing timestamps within each participant-by-trial stream"
                )

            x = pd.to_numeric(frame[study.x], errors="coerce").to_numpy(dtype=float)
            y = pd.to_numeric(frame[study.y], errors="coerce").to_numpy(dtype=float)
            labels, detector_metadata = self.detector.detect(
                timestamps_ms,
                x,
                y,
                self.viewer_distance_cm,
                self.pixel_size_cm,
            )
            labels = list(labels)
            if len(labels) != len(frame):
                raise ValueError(
                    "pEYES detector returned a label sequence whose length does not match the input stream"
                )

            normalized_labels = [_label_name(label) for label in labels]
            codes = [_label_code(label) for label in labels]
            output.loc[frame.index, self.label_column] = normalized_labels
            output.loc[frame.index, self.code_column] = pd.array(codes, dtype="Int64")

            metadata_rows.append(
                {
                    study.participant: participant_value,
                    study.trial: trial_value,
                    "backend": self.name,
                    "detector": _detector_name(self.detector),
                    "algorithm": _detector_algorithm(self.detector),
                    "viewer_distance_cm": float(self.viewer_distance_cm),
                    "pixel_size_cm": float(self.pixel_size_cm),
                    "metadata": _metadata_mapping(detector_metadata),
                }
            )

        normalized = output.rename(columns={self.label_column: "event_label"})
        if self.code_column != "event_code":
            normalized = normalized.rename(columns={self.code_column: "event_code"})
        metadata = pd.DataFrame(metadata_rows)
        return DetectionResult(
            samples=normalized.reset_index(drop=True),
            metadata=metadata.reset_index(drop=True),
            backend=self.name,
            detector=_detector_name(self.detector),
        )


def make_peyes_detector(
    algorithm: str,
    *,
    missing_value: float = np.nan,
    min_event_duration: float,
    pad_blinks_time: float = 0.0,
    name: str | None = None,
    **kwargs: Any,
) -> Any:
    """Create a pEYES detector through its public ``create_detector`` factory.

    Raises an informative ImportError when pEYES is not installed. pEYES 0.2.x
    currently requires Python 3.12 or newer.
    """

    try:
        import peyes
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise ImportError(
            "pEYES interoperability requires the optional dependency; install "
            "GazeAudit with the 'peyes' extra on Python 3.12+"
        ) from exc

    return peyes.create_detector(
        algorithm=algorithm,
        missing_value=missing_value,
        min_event_duration=min_event_duration,
        pad_blinks_time=pad_blinks_time,
        name=name,
        **kwargs,
    )


def run_peyes_detector(
    study: GazeStudy,
    detector: Any,
    *,
    viewer_distance_cm: float,
    pixel_size_cm: float,
    timestamp_unit: str = "ms",
    coordinate_unit: str = "px",
) -> DetectionResult:
    """Convenience wrapper around :class:`PeyesDetectorAdapter`."""

    adapter = PeyesDetectorAdapter(
        detector=detector,
        viewer_distance_cm=viewer_distance_cm,
        pixel_size_cm=pixel_size_cm,
        timestamp_unit=timestamp_unit,
        coordinate_unit=coordinate_unit,
    )
    return adapter.detect(study)


def _time_factor(unit: str) -> float:
    factors = {"ms": 1.0, "s": 1000.0, "us": 0.001}
    try:
        return factors[unit]
    except KeyError as exc:
        raise ValueError("timestamp_unit must be 'ms', 's', or 'us'") from exc


def _group_key(key: Any) -> tuple[Any, Any]:
    if isinstance(key, tuple) and len(key) == 2:
        return key[0], key[1]
    return key, None


def _label_name(label: Any) -> str:
    name = getattr(label, "name", None)
    if isinstance(name, str) and name:
        return name.lower()
    return str(label).strip().lower()


def _label_code(label: Any) -> int | None:
    try:
        return int(label)
    except (TypeError, ValueError):
        return None


def _detector_name(detector: Any) -> str:
    name = getattr(detector, "name", None)
    if isinstance(name, str) and name:
        return name
    return detector.__class__.__name__


def _detector_algorithm(detector: Any) -> str:
    algorithm = getattr(detector, "algorithm_name", None)
    if isinstance(algorithm, str) and algorithm:
        return algorithm
    return detector.__class__.__name__.removesuffix("Detector").lower()


def _metadata_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise TypeError("pEYES detector metadata must be a dictionary")
    return dict(value)
