"""Direct Eye-Tracking-BIDS ingestion for GazeAudit.

The reader follows the current BIDS eye-tracking rules for ``physio`` files:
``PhysioType='eyetrack'``, one recording per eye, required timestamp/x/y
columns, and required ``RecordedEye`` plus ``SampleCoordinateSystem`` metadata.
The implementation intentionally validates only the subset needed for robust
GazeAudit ingestion; it is not a replacement for the official BIDS Validator.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .study import GazeStudy


_REQUIRED_INITIAL_COLUMNS = ("timestamp", "x_coordinate", "y_coordinate")
_REQUIRED_SIDECAR_FIELDS = (
    "SamplingFrequency",
    "StartTime",
    "Columns",
    "RecordedEye",
    "SampleCoordinateSystem",
)


@dataclass(frozen=True)
class BIDSEyeTrackingRecord:
    """One validated eye-tracking BIDS recording plus its canonical study."""

    study: GazeStudy
    metadata: dict[str, Any]
    entities: dict[str, str]
    source_path: Path
    sidecar_path: Path
    recorded_eye: str
    coordinate_unit: str
    timestamp_unit: str


@dataclass(frozen=True)
class BIDSEyeTrackingAdapter:
    """Study-adapter wrapper for one Eye-Tracking-BIDS ``physio`` file."""

    sidecar_path: str | Path | None = None
    participant_id: Any | None = None
    trial_id: Any | None = None
    preserve_columns: bool = True
    name: str = "bids-eyetrack"

    def to_study(self, source: Any) -> GazeStudy:
        record = read_bids_eyetrack(
            source,
            sidecar_path=self.sidecar_path,
            participant_id=self.participant_id,
            trial_id=self.trial_id,
            preserve_columns=self.preserve_columns,
        )
        return record.study


def read_bids_eyetrack(
    physio_path: str | Path,
    *,
    sidecar_path: str | Path | None = None,
    participant_id: Any | None = None,
    trial_id: Any | None = None,
    preserve_columns: bool = True,
) -> BIDSEyeTrackingRecord:
    """Read one BIDS eye-tracking ``physio.tsv[.gz]`` recording.

    Timestamps are converted to milliseconds for GazeAudit's canonical study.
    The original BIDS timestamp is retained as ``bids_timestamp`` when
    ``preserve_columns=True``.
    """

    source = Path(physio_path)
    if not source.exists():
        raise FileNotFoundError(f"eye-tracking physio file does not exist: {source}")
    if not _is_physio_tsv(source):
        raise ValueError("physio_path must end with '_physio.tsv' or '_physio.tsv.gz'")

    sidecar = (
        Path(sidecar_path)
        if sidecar_path is not None
        else _infer_sidecar_path(source)
    )
    if not sidecar.exists():
        raise FileNotFoundError(f"eye-tracking sidecar does not exist: {sidecar}")

    metadata = _load_sidecar(sidecar)
    _validate_sidecar(metadata)
    columns = tuple(metadata["Columns"])
    if tuple(columns[:3]) != _REQUIRED_INITIAL_COLUMNS:
        raise ValueError(
            "Eye-Tracking-BIDS requires the first columns to be "
            "timestamp, x_coordinate, y_coordinate"
        )

    frame = pd.read_csv(
        source,
        sep="\t",
        header=None,
        na_values=["n/a", "N/A"],
        compression="infer",
    )
    if frame.shape[1] != len(columns):
        raise ValueError(
            f"physio data has {frame.shape[1]} columns but sidecar declares "
            f"{len(columns)}"
        )
    frame.columns = list(columns)
    if frame.empty:
        raise ValueError("eye-tracking physio file must contain at least one row")

    timestamp_unit = _column_units(metadata, "timestamp", required=True)
    x_unit = _column_units(metadata, "x_coordinate", required=True)
    y_unit = _column_units(metadata, "y_coordinate", required=True)
    if x_unit != y_unit:
        raise ValueError(
            "x_coordinate and y_coordinate must use the same units for canonical ingestion"
        )

    timestamp = pd.to_numeric(
        frame["timestamp"], errors="coerce"
    ).to_numpy(dtype=float)
    x = pd.to_numeric(frame["x_coordinate"], errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(frame["y_coordinate"], errors="coerce").to_numpy(dtype=float)
    if np.any(~np.isfinite(timestamp)):
        raise ValueError("BIDS eye-tracking timestamps must be finite")
    timestamp_ms = timestamp * _time_factor_to_ms(timestamp_unit)

    entities = parse_bids_entities(source.name)
    if "recording" not in entities:
        raise ValueError(
            "Eye-Tracking-BIDS requires a recording-<label> entity for each eye recording"
        )

    participant = participant_id
    if participant is None:
        subject = entities.get("sub")
        if subject is None:
            raise ValueError(
                "could not infer participant from BIDS filename; provide "
                "participant_id explicitly"
            )
        participant = f"sub-{subject}"

    canonical_trial = (
        trial_id
        if trial_id is not None
        else _default_trial_id(source, entities)
    )
    output = pd.DataFrame(
        {
            "x": x,
            "y": y,
            "timestamp": timestamp_ms,
            "participant": [participant] * len(frame),
            "trial": [canonical_trial] * len(frame),
        }
    )

    if preserve_columns:
        output["bids_timestamp"] = timestamp
        output["recorded_eye"] = str(metadata["RecordedEye"])
        output["sample_coordinate_system"] = str(metadata["SampleCoordinateSystem"])
        output["bids_recording"] = entities["recording"]
        for column in frame.columns:
            if column in _REQUIRED_INITIAL_COLUMNS:
                continue
            target = column if column not in output.columns else f"bids_{column}"
            output[target] = frame[column].to_numpy(copy=False)

    study = GazeStudy(output)
    study.validate_time_order()
    return BIDSEyeTrackingRecord(
        study=study,
        metadata=metadata,
        entities=entities,
        source_path=source,
        sidecar_path=sidecar,
        recorded_eye=str(metadata["RecordedEye"]),
        coordinate_unit=x_unit,
        timestamp_unit=timestamp_unit,
    )


def read_bids_eyetrack_many(
    physio_paths: Sequence[str | Path],
    *,
    participant_ids: Sequence[Any] | None = None,
    trial_ids: Sequence[Any] | None = None,
    preserve_columns: bool = True,
) -> tuple[GazeStudy, list[BIDSEyeTrackingRecord]]:
    """Read multiple BIDS eye recordings and combine them into one study.

    Separate eye recordings remain distinct participant-by-trial streams because
    the default trial identifier contains the BIDS ``recording`` entity. This
    prevents left/right/cyclopean samples from being interleaved accidentally.
    """

    paths = [Path(path) for path in physio_paths]
    if not paths:
        raise ValueError("physio_paths must contain at least one file")
    participant_values = _optional_sequence(
        participant_ids, len(paths), "participant_ids"
    )
    trial_values = _optional_sequence(trial_ids, len(paths), "trial_ids")

    records: list[BIDSEyeTrackingRecord] = []
    frames: list[pd.DataFrame] = []
    for index, path in enumerate(paths):
        record = read_bids_eyetrack(
            path,
            participant_id=(
                None if participant_values is None else participant_values[index]
            ),
            trial_id=None if trial_values is None else trial_values[index],
            preserve_columns=preserve_columns,
        )
        records.append(record)
        frames.append(record.study.data)

    combined = GazeStudy(pd.concat(frames, ignore_index=True))
    combined.validate_time_order()
    return combined, records


def parse_bids_entities(filename: str) -> dict[str, str]:
    """Parse BIDS ``key-value`` entities without guessing their semantics."""

    name = Path(filename).name
    if name.endswith(".tsv.gz"):
        stem = name[: -len(".tsv.gz")]
    else:
        stem = Path(name).stem
    entities: dict[str, str] = {}
    for token in stem.split("_"):
        match = re.fullmatch(r"([A-Za-z0-9]+)-([A-Za-z0-9+]+)", token)
        if match:
            entities[match.group(1)] = match.group(2)
    return entities


def _load_sidecar(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON sidecar: {path}") from exc
    if not isinstance(value, dict):
        raise TypeError("BIDS sidecar must contain a JSON object")
    return value


def _validate_sidecar(metadata: Mapping[str, Any]) -> None:
    if metadata.get("PhysioType") != "eyetrack":
        raise ValueError("BIDS sidecar PhysioType must be 'eyetrack'")
    missing = [field for field in _REQUIRED_SIDECAR_FIELDS if field not in metadata]
    if missing:
        raise ValueError(
            f"BIDS eye-tracking sidecar is missing required fields: {missing}"
        )

    columns = metadata.get("Columns")
    if not isinstance(columns, list) or not columns or not all(
        isinstance(column, str) and column for column in columns
    ):
        raise TypeError("BIDS sidecar Columns must be a non-empty list of strings")

    sampling_frequency = metadata.get("SamplingFrequency")
    if not isinstance(sampling_frequency, (int, float)) or not np.isfinite(
        sampling_frequency
    ):
        raise TypeError("SamplingFrequency must be a finite number")
    if sampling_frequency <= 0:
        raise ValueError("SamplingFrequency must be positive")

    start_time = metadata.get("StartTime")
    if not isinstance(start_time, (int, float)) or not np.isfinite(start_time):
        raise TypeError("StartTime must be a finite number")

    for field in ("RecordedEye", "SampleCoordinateSystem"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            raise TypeError(f"{field} must be a non-empty string")


def _column_units(
    metadata: Mapping[str, Any],
    column: str,
    *,
    required: bool,
) -> str:
    column_metadata = metadata.get(column)
    if not isinstance(column_metadata, Mapping):
        if required:
            raise ValueError(
                f"BIDS sidecar must define metadata for column {column!r}"
            )
        return ""
    units = column_metadata.get("Units")
    if not isinstance(units, str) or not units.strip():
        if required:
            raise ValueError(
                f"BIDS column {column!r} must define non-empty Units"
            )
        return ""
    return units.strip()


def _time_factor_to_ms(unit: str) -> float:
    normalized = unit.strip().lower().replace("μ", "µ")
    factors = {
        "s": 1000.0,
        "sec": 1000.0,
        "second": 1000.0,
        "seconds": 1000.0,
        "ms": 1.0,
        "millisecond": 1.0,
        "milliseconds": 1.0,
        "us": 0.001,
        "µs": 0.001,
        "microsecond": 0.001,
        "microseconds": 0.001,
    }
    try:
        return factors[normalized]
    except KeyError as exc:
        raise ValueError(
            f"unsupported BIDS eye-tracking timestamp unit {unit!r}; "
            "use s, ms, or us/µs"
        ) from exc


def _infer_sidecar_path(source: Path) -> Path:
    name = source.name
    if name.endswith(".tsv.gz"):
        sidecar_name = name[: -len(".tsv.gz")] + ".json"
    elif name.endswith(".tsv"):
        sidecar_name = name[: -len(".tsv")] + ".json"
    else:  # guarded by _is_physio_tsv
        raise ValueError("unsupported physio file extension")
    return source.with_name(sidecar_name)


def _is_physio_tsv(path: Path) -> bool:
    return path.name.endswith("_physio.tsv") or path.name.endswith("_physio.tsv.gz")


def _default_trial_id(source: Path, entities: Mapping[str, str]) -> str:
    pieces: list[str] = []
    for key in ("ses", "task", "acq", "run", "recording"):
        if key in entities:
            pieces.append(f"{key}-{entities[key]}")
    if pieces:
        return "|".join(pieces)
    name = source.name
    if name.endswith(".tsv.gz"):
        return name[: -len(".tsv.gz")]
    return name[: -len(".tsv")]


def _optional_sequence(
    values: Sequence[Any] | None,
    expected: int,
    name: str,
) -> list[Any] | None:
    if values is None:
        return None
    output = list(values)
    if len(output) != expected:
        raise ValueError(f"{name} must match the number of physio files")
    return output
