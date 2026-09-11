"""Declarative specification spaces for eye-tracking robustness analysis."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from itertools import product
from typing import Any

import pandas as pd

from .study import GazeStudy

Specification = dict[str, Any]
Processor = Callable[[GazeStudy, Specification], Any]
Endpoint = Callable[[Any, Specification], float]


@dataclass
class PipelineSpace:
    """A set of defensible analysis decisions to be evaluated jointly.

    The class is deliberately agnostic about the scientific meaning of each
    choice. Researchers can register detector families, missing-data rules,
    AOI definitions, QC thresholds, sampling variants, or any other auditable
    decision. Invalid combinations can be filtered before execution.
    """

    choices: dict[str, tuple[Any, ...]] = field(default_factory=dict)

    def add_choice(self, name: str, values: Iterable[Any]) -> PipelineSpace:
        values_tuple = tuple(values)
        if not name:
            raise ValueError("choice name must be non-empty")
        if not values_tuple:
            raise ValueError(f"choice {name!r} must contain at least one value")
        self.choices[name] = values_tuple
        return self

    @property
    def size(self) -> int:
        total = 1
        for values in self.choices.values():
            total *= len(values)
        return total

    def enumerate_specs(
        self,
        *,
        valid_if: Callable[[Mapping[str, Any]], bool] | None = None,
    ) -> list[Specification]:
        """Enumerate all valid specifications in deterministic order."""

        if not self.choices:
            return [{}]

        names = list(self.choices)
        combinations = product(*(self.choices[name] for name in names))
        specs = [dict(zip(names, combination, strict=True)) for combination in combinations]
        if valid_if is not None:
            specs = [spec for spec in specs if bool(valid_if(spec))]
        return specs


def run_specs(
    study: GazeStudy,
    space: PipelineSpace,
    endpoint: Endpoint,
    *,
    processor: Processor | None = None,
    valid_if: Callable[[Mapping[str, Any]], bool] | None = None,
) -> pd.DataFrame:
    """Execute each specification and collect a common scalar endpoint.

    Parameters
    ----------
    study:
        Canonical GazeAudit study.
    space:
        Declarative set of analysis decisions.
    endpoint:
        Callable receiving ``(processed_object, specification)`` and returning
        one scalar scientific estimate.
    processor:
        Optional callable receiving ``(study, specification)``. If omitted,
        the original study is passed directly to ``endpoint``.
    valid_if:
        Optional predicate used to reject scientifically invalid combinations.

    Returns
    -------
    pandas.DataFrame
        One row per evaluated specification plus the resulting ``estimate``.
    """

    specs = space.enumerate_specs(valid_if=valid_if)
    rows: list[dict[str, Any]] = []
    for index, spec in enumerate(specs):
        processed = processor(study, spec) if processor is not None else study
        estimate = float(endpoint(processed, spec))
        row = {"spec_id": index, **spec, "estimate": estimate}
        rows.append(row)

    return pd.DataFrame(rows)
