"""Adapters from pymovements objects to GazeAudit's canonical study model.

The implementation targets the public pymovements 0.28 ``Gaze.samples``
contract: a Polars DataFrame with ``time`` and nested coordinate columns such
as ``pixel`` or ``position``. The adapter uses duck typing so importing
GazeAudit never requires pymovements to be installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
import pandas as pd

from .study import GazeStudy


@dataclass(frozen=True)
class PymovementsGazeAdapter:
    """Convert one pymovements ``Gaze`` object into a :class:`GazeStudy`.

    Parameters
    ----------
    coordinate:
        Nested pymovements coordinate column, usually ``"pixel"`` or
        ``"position"``.
    component:
        ``"auto"`` accepts only two-component monocular/cyclopian data.
        For binocular nested vectors, specify ``"left"``, ``"right"``, or
        ``"cyclopian"`` explicitly. This fail-closed behavior avoids silently
        averaging or selecting an eye.
    participant_id:
        Identifier assigned when no ``participant_column`` is supplied.
    participant_column:
        Existing sample column to use as participant identifier.
    trial_columns:
        Columns defining a trial. If omitted, ``gaze.trial_columns`` is used.
        Multiple trial columns are preserved as tuples rather than collapsed.
    numeric_time_unit:
        Unit used only when the pymovements ``time`` column arrives as numeric.
        pymovements normally stores ``time`` as a Polars duration; those values
        are converted to milliseconds automatically.
    """

    coordinate: str = "pixel"
    component: str = "auto"
    participant_id: Any = "recording_1"
    participant_column: str | None = None
    trial_columns: tuple[str, ...] | None = None
    numeric_time_unit: str = "ms"
    name: str = "pymovements-gaze"

    def to_study(self, source: Any) -> GazeStudy:
        frame = _samples_to_pandas(source)
        if self.coordinate not in frame.columns:
            raise ValueError(
                f"pymovements samples do not contain coordinate column {self.coordinate!r}"
            )
        if "time" not in frame.columns:
            raise ValueError("pymovements samples do not contain the canonical 'time' column")

        x, y = _extract_coordinate_components(frame[self.coordinate], self.component)
        timestamp = _time_to_milliseconds(frame["time"], self.numeric_time_unit)

        if self.participant_column is None:
            participant = pd.Series(
                [self.participant_id] * len(frame),
                index=frame.index,
                dtype="object",
            )
        else:
            if self.participant_column not in frame.columns:
                raise ValueError(
                    f"participant column {self.participant_column!r} is not present in samples"
                )
            participant = frame[self.participant_column].copy()

        trial_columns = self.trial_columns
        if trial_columns is None:
            raw = getattr(source, "trial_columns", None)
            if raw is None:
                trial_columns = ()
            elif isinstance(raw, str):
                trial_columns = (raw,)
            else:
                trial_columns = tuple(raw)
        trial = _trial_identifier(frame, trial_columns)

        output = pd.DataFrame(
            {
                "x": x,
                "y": y,
                "timestamp": timestamp,
                "participant": participant.to_numpy(copy=False),
                "trial": trial,
            }
        )
        study = GazeStudy(output)
        study.validate_time_order()
        return study


def from_pymovements_gaze(
    gaze: Any,
    *,
    coordinate: str = "pixel",
    component: str = "auto",
    participant_id: Any = "recording_1",
    participant_column: str | None = None,
    trial_columns: Sequence[str] | None = None,
    numeric_time_unit: str = "ms",
) -> GazeStudy:
    """Convenience wrapper for :class:`PymovementsGazeAdapter`."""

    adapter = PymovementsGazeAdapter(
        coordinate=coordinate,
        component=component,
        participant_id=participant_id,
        participant_column=participant_column,
        trial_columns=None if trial_columns is None else tuple(trial_columns),
        numeric_time_unit=numeric_time_unit,
    )
    return adapter.to_study(gaze)


def from_pymovements_dataset(
    dataset: Any,
    *,
    coordinate: str = "pixel",
    component: str = "auto",
    participant_ids: Sequence[Any] | None = None,
    participant_column: str | None = None,
    trial_columns: Sequence[str] | None = None,
    numeric_time_unit: str = "ms",
) -> GazeStudy:
    """Convert all loaded ``Dataset.gaze`` recordings into one ``GazeStudy``.

    When ``participant_ids`` is omitted, neutral recording identifiers
    (``recording_1``, ``recording_2``, ...) are generated. They are explicitly
    recording IDs and must not be interpreted as recovered participant identity.
    """

    recordings = getattr(dataset, "gaze", None)
    if recordings is None:
        raise TypeError("dataset must expose a 'gaze' sequence")
    recordings = list(recordings)
    if not recordings:
        raise ValueError("dataset.gaze must contain at least one loaded recording")

    if participant_ids is None:
        ids = [f"recording_{index + 1}" for index in range(len(recordings))]
    else:
        ids = list(participant_ids)
        if len(ids) != len(recordings):
            raise ValueError("participant_ids must match the number of dataset.gaze recordings")

    studies: list[pd.DataFrame] = []
    for recording, participant_id in zip(recordings, ids, strict=True):
        adapter = PymovementsGazeAdapter(
            coordinate=coordinate,
            component=component,
            participant_id=participant_id,
            participant_column=participant_column,
            trial_columns=None if trial_columns is None else tuple(trial_columns),
            numeric_time_unit=numeric_time_unit,
        )
        studies.append(adapter.to_study(recording).data)

    return GazeStudy(pd.concat(studies, ignore_index=True))


def _samples_to_pandas(source: Any) -> pd.DataFrame:
    samples = getattr(source, "samples", None)
    if samples is None:
        raise TypeError("source must expose a pymovements-like 'samples' attribute")
    if isinstance(samples, pd.DataFrame):
        return samples.copy()
    to_pandas = getattr(samples, "to_pandas", None)
    if not callable(to_pandas):
        raise TypeError("source.samples must be a pandas DataFrame or expose to_pandas()")
    frame = to_pandas()
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("source.samples.to_pandas() must return a pandas DataFrame")
    return frame


def _extract_coordinate_components(
    values: pd.Series,
    component: str,
) -> tuple[np.ndarray, np.ndarray]:
    parsed: list[np.ndarray | None] = []
    widths: set[int] = set()
    for value in values:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            parsed.append(None)
            continue
        array = np.asarray(value, dtype=float).reshape(-1)
        parsed.append(array)
        widths.add(int(array.size))

    if not widths:
        raise ValueError("coordinate column contains no usable coordinate vectors")
    if len(widths) != 1:
        raise ValueError(f"coordinate vector width is inconsistent across samples: {sorted(widths)}")
    width = next(iter(widths))

    component_key = component.lower().strip()
    if component_key == "auto":
        if width != 2:
            raise ValueError(
                "component='auto' is only valid for two-component coordinates; "
                "select 'left', 'right', or 'cyclopian' explicitly for binocular data"
            )
        indices = (0, 1)
    else:
        mapping = {
            "mono": (0, 1),
            "left": (0, 1),
            "right": (2, 3),
            "cyclopian": (4, 5),
        }
        if component_key not in mapping:
            raise ValueError("component must be 'auto', 'mono', 'left', 'right', or 'cyclopian'")
        indices = mapping[component_key]
        if max(indices) >= width:
            raise ValueError(
                f"component {component_key!r} requires at least {max(indices) + 1} values, "
                f"but coordinate width is {width}"
            )

    x = np.full(len(parsed), np.nan, dtype=float)
    y = np.full(len(parsed), np.nan, dtype=float)
    for index, array in enumerate(parsed):
        if array is not None:
            x[index] = array[indices[0]]
            y[index] = array[indices[1]]
    return x, y


def _time_to_milliseconds(values: pd.Series, numeric_time_unit: str) -> np.ndarray:
    if pd.api.types.is_timedelta64_dtype(values.dtype):
        return values.dt.total_seconds().to_numpy(dtype=float) * 1000.0

    if pd.api.types.is_numeric_dtype(values.dtype):
        numeric = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
        factor = _time_factor(numeric_time_unit)
        output = numeric * factor
    else:
        try:
            delta = pd.to_timedelta(values)
        except (TypeError, ValueError) as exc:
            raise TypeError("pymovements time values must be duration-like or numeric") from exc
        output = delta.dt.total_seconds().to_numpy(dtype=float) * 1000.0

    if np.any(~np.isfinite(output)):
        raise ValueError("pymovements time values must be finite")
    return output


def _time_factor(unit: str) -> float:
    factors = {"ms": 1.0, "s": 1000.0, "us": 0.001}
    try:
        return factors[unit]
    except KeyError as exc:
        raise ValueError("numeric_time_unit must be 'ms', 's', or 'us'") from exc


def _trial_identifier(frame: pd.DataFrame, columns: tuple[str, ...]) -> np.ndarray:
    if not columns:
        return np.zeros(len(frame), dtype=int)
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"trial columns are not present in samples: {missing}")
    if len(columns) == 1:
        return frame[columns[0]].to_numpy(copy=False)
    tuples = list(frame[list(columns)].itertuples(index=False, name=None))
    output = np.empty(len(tuples), dtype=object)
    output[:] = tuples
    return output
