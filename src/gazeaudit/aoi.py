"""Area-of-interest geometry primitives used by GazeAudit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class AOI(Protocol):
    """Structural protocol implemented by supported AOI geometries."""

    name: str

    def contains_points(self, points: np.ndarray) -> np.ndarray:
        """Return a boolean mask indicating whether points belong to the AOI."""


@dataclass(frozen=True)
class RectangleAOI:
    """Axis-aligned rectangular AOI."""

    name: str
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def __post_init__(self) -> None:
        if self.xmax < self.xmin:
            raise ValueError("xmax must be greater than or equal to xmin")
        if self.ymax < self.ymin:
            raise ValueError("ymax must be greater than or equal to ymin")

    def contains_points(self, points: np.ndarray) -> np.ndarray:
        arr = _as_points(points)
        return (
            (arr[:, 0] >= self.xmin)
            & (arr[:, 0] <= self.xmax)
            & (arr[:, 1] >= self.ymin)
            & (arr[:, 1] <= self.ymax)
        )


@dataclass(frozen=True)
class CircleAOI:
    """Circular AOI."""

    name: str
    cx: float
    cy: float
    radius: float

    def __post_init__(self) -> None:
        if self.radius < 0:
            raise ValueError("radius must be non-negative")

    def contains_points(self, points: np.ndarray) -> np.ndarray:
        arr = _as_points(points)
        squared_distance = (arr[:, 0] - self.cx) ** 2 + (arr[:, 1] - self.cy) ** 2
        return squared_distance <= self.radius**2


def _as_points(points: np.ndarray) -> np.ndarray:
    arr = np.asarray(points, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError("points must have shape (n, 2)")
    return arr
