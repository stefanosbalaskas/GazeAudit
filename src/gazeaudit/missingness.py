"""Structured missingness perturbation and sensitivity analysis."""

from __future__ import annotations

from collections.abc import Callable, Iterable

import numpy as np
import pandas as pd

from .study import GazeStudy


def missingness_mask(study: GazeStudy) -> np.ndarray:
    """Return rows where either gaze coordinate is missing."""

    x = pd.to_numeric(study.data[study.x], errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(study.data[study.y], errors="coerce").to_numpy(dtype=float)
    return ~(np.isfinite(x) & np.isfinite(y))


def summarize_missingness(study: GazeStudy) -> pd.Series:
    """Summarize observed gaze-coordinate missingness."""

    mask = missingness_mask(study)
    return pd.Series(
        {
            "n_rows": int(mask.size),
            "n_missing": int(mask.sum()),
            "missing_fraction": float(mask.mean()),
            "n_complete": int((~mask).sum()),
        }
    )


def inject_missingness(
    study: GazeStudy,
    fraction: float,
    *,
    mechanism: str = "mcar",
    rng: np.random.Generator | int | None = None,
    reason: str | None = None,
    reason_col: str = "missing_reason",
) -> GazeStudy:
    """Inject controlled missing gaze while preserving the original study.

    ``mechanism='mcar'`` masks randomly selected complete rows across the study.
    ``mechanism='block'`` masks approximately the requested fraction as
    contiguous blocks within participant-by-trial streams. These are benchmark
    perturbations, not claims that real eye-tracking loss is MCAR or blockwise.
    """

    if not np.isfinite(fraction) or not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be finite and between 0 and 1")
    if mechanism not in {"mcar", "block"}:
        raise ValueError("mechanism must be 'mcar' or 'block'")

    data = study.data.reset_index(drop=True).copy()
    working = study.copy_with(data)
    complete = np.flatnonzero(~missingness_mask(working))
    n_mask = int(round(fraction * complete.size))
    if n_mask == 0:
        return working

    generator = _as_rng(rng)
    if mechanism == "mcar":
        selected = np.sort(generator.choice(complete, size=n_mask, replace=False))
    else:
        selected = _block_positions(working, n_mask, generator)

    data.loc[selected, [study.x, study.y]] = np.nan
    if reason is not None:
        if reason_col not in data.columns:
            data[reason_col] = pd.Series(pd.NA, index=data.index, dtype="object")
        data.loc[selected, reason_col] = reason
    return study.copy_with(data)


def missingness_sensitivity_curve(
    study: GazeStudy,
    fractions: Iterable[float],
    endpoint: Callable[[GazeStudy], float],
    *,
    mechanism: str = "mcar",
    rng: np.random.Generator | int | None = None,
) -> pd.DataFrame:
    """Evaluate one endpoint as controlled gaze missingness increases."""

    values = tuple(float(value) for value in fractions)
    if not values:
        raise ValueError("fractions must contain at least one value")
    generator = _as_rng(rng)
    rows: list[dict[str, float | int | str]] = []
    for fraction in values:
        child_seed = int(generator.integers(0, np.iinfo(np.uint32).max, dtype=np.uint32))
        perturbed = inject_missingness(
            study,
            fraction,
            mechanism=mechanism,
            rng=child_seed,
            reason=f"injected_{mechanism}",
        )
        estimate = float(endpoint(perturbed))
        if not np.isfinite(estimate):
            raise ValueError("endpoint must return a finite scalar")
        summary = summarize_missingness(perturbed)
        rows.append(
            {
                "requested_fraction": fraction,
                "mechanism": mechanism,
                "observed_missing_fraction": float(summary["missing_fraction"]),
                "n_missing": int(summary["n_missing"]),
                "estimate": estimate,
            }
        )
    return pd.DataFrame(rows)


def _block_positions(
    study: GazeStudy,
    n_mask: int,
    generator: np.random.Generator,
) -> np.ndarray:
    complete_mask = ~missingness_mask(study)
    candidates: list[np.ndarray] = []
    grouped = study.data.groupby([study.participant, study.trial], sort=False, dropna=False)
    for _, frame in grouped:
        positions = np.asarray(frame.index, dtype=int)
        positions = positions[complete_mask[positions]]
        if positions.size:
            candidates.append(positions)
    if not candidates:
        return np.array([], dtype=int)

    selected: set[int] = set()
    attempts = 0
    while len(selected) < n_mask and attempts < max(20, n_mask * 5):
        group = candidates[int(generator.integers(0, len(candidates)))]
        remaining = n_mask - len(selected)
        max_block = min(group.size, max(1, remaining))
        block_len = int(generator.integers(1, max_block + 1))
        start_max = group.size - block_len
        start = int(generator.integers(0, start_max + 1)) if start_max > 0 else 0
        selected.update(int(value) for value in group[start : start + block_len])
        attempts += 1

    if len(selected) < n_mask:
        all_complete = np.concatenate(candidates)
        already = np.fromiter(selected, dtype=int)
        remaining = np.setdiff1d(all_complete, already, assume_unique=False)
        need = min(n_mask - len(selected), remaining.size)
        if need:
            selected.update(
                int(value) for value in generator.choice(remaining, size=need, replace=False)
            )
    return np.array(sorted(selected), dtype=int)


def _as_rng(rng: np.random.Generator | int | None) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)
