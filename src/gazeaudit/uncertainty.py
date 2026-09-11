"""Measurement-error models and probabilistic AOI assignment."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .aoi import AOI


@dataclass(frozen=True)
class GaussianGazeErrorModel:
    """Global bivariate Gaussian model for gaze-position measurement error.

    The model is intentionally simple and auditable. Let ``e = observed - true``.
    ``mean_error`` estimates systematic bias and ``covariance`` estimates residual
    spatial uncertainty. Given a new observed gaze position ``g_obs``, latent true
    positions are sampled as ``g_true = g_obs - e``.

    This model is a foundation for the MVP, not a claim that eye-tracker error is
    universally Gaussian or spatially stationary. Later versions can support local,
    participant-specific, anisotropic, robust, and time-varying models.
    """

    mean_error: np.ndarray
    covariance: np.ndarray
    n_validation: int

    def __post_init__(self) -> None:
        mean = np.asarray(self.mean_error, dtype=float)
        covariance = np.asarray(self.covariance, dtype=float)
        if mean.shape != (2,):
            raise ValueError("mean_error must have shape (2,)")
        if covariance.shape != (2, 2):
            raise ValueError("covariance must have shape (2, 2)")
        if self.n_validation < 2:
            raise ValueError("n_validation must be at least 2")
        if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(covariance)):
            raise ValueError("error-model parameters must be finite")
        eigenvalues = np.linalg.eigvalsh(covariance)
        if np.any(eigenvalues < -1e-12):
            raise ValueError("covariance must be positive semidefinite")
        object.__setattr__(self, "mean_error", mean)
        object.__setattr__(self, "covariance", covariance)

    @classmethod
    def fit(
        cls,
        validation: pd.DataFrame,
        *,
        observed_x: str = "observed_x",
        observed_y: str = "observed_y",
        target_x: str = "target_x",
        target_y: str = "target_y",
    ) -> "GaussianGazeErrorModel":
        """Estimate systematic bias and covariance from validation targets."""

        required = [observed_x, observed_y, target_x, target_y]
        missing = [column for column in required if column not in validation.columns]
        if missing:
            raise ValueError(f"missing validation columns: {missing}")

        frame = validation[required].apply(pd.to_numeric, errors="coerce").dropna()
        if len(frame) < 2:
            raise ValueError("at least two complete validation observations are required")

        errors = np.column_stack(
            [
                frame[observed_x].to_numpy() - frame[target_x].to_numpy(),
                frame[observed_y].to_numpy() - frame[target_y].to_numpy(),
            ]
        )
        mean_error = errors.mean(axis=0)
        covariance = np.cov(errors, rowvar=False, ddof=1)
        covariance = np.atleast_2d(covariance)
        return cls(mean_error=mean_error, covariance=covariance, n_validation=len(errors))

    @property
    def bias_x(self) -> float:
        return float(self.mean_error[0])

    @property
    def bias_y(self) -> float:
        return float(self.mean_error[1])

    def corrected_points(self, points: np.ndarray) -> np.ndarray:
        """Bias-correct observed points without discarding residual uncertainty."""

        arr = _as_points(points)
        return arr - self.mean_error

    def sample_true_points(
        self,
        points: np.ndarray,
        *,
        draws: int = 2000,
        rng: np.random.Generator | int | None = None,
    ) -> np.ndarray:
        """Sample latent true gaze positions conditional on observed positions.

        Returns
        -------
        ndarray
            Array with shape ``(n_observations, draws, 2)``.
        """

        if draws < 1:
            raise ValueError("draws must be at least 1")
        arr = _as_points(points)
        generator = _as_rng(rng)
        error_draws = generator.multivariate_normal(
            mean=self.mean_error,
            cov=self.covariance,
            size=(arr.shape[0], draws),
            check_valid="raise",
        )
        return arr[:, None, :] - error_draws


def aoi_probabilities(
    points: np.ndarray,
    aois: Sequence[AOI],
    error_model: GaussianGazeErrorModel,
    *,
    draws: int = 2000,
    rng: np.random.Generator | int | None = None,
    include_outside: bool = True,
) -> pd.DataFrame:
    """Estimate probabilistic AOI membership by Monte Carlo propagation.

    AOIs are allowed to overlap. Therefore AOI probabilities are marginal
    membership probabilities and need not sum to one. ``outside`` is the
    probability of belonging to none of the supplied AOIs.
    """

    if not aois:
        raise ValueError("at least one AOI is required")
    names = [aoi.name for aoi in aois]
    if len(names) != len(set(names)):
        raise ValueError("AOI names must be unique")

    latent = error_model.sample_true_points(points, draws=draws, rng=rng)
    n_observations = latent.shape[0]
    flattened = latent.reshape(-1, 2)

    output: dict[str, np.ndarray] = {}
    membership_stack: list[np.ndarray] = []
    for aoi in aois:
        membership = np.asarray(aoi.contains_points(flattened), dtype=bool).reshape(
            n_observations, draws
        )
        membership_stack.append(membership)
        output[aoi.name] = membership.mean(axis=1)

    if include_outside:
        in_any = np.logical_or.reduce(membership_stack)
        output["outside"] = (~in_any).mean(axis=1)

    return pd.DataFrame(output)


def _as_points(points: np.ndarray) -> np.ndarray:
    arr = np.asarray(points, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError("points must have shape (n, 2)")
    if not np.all(np.isfinite(arr)):
        raise ValueError("points must contain only finite values")
    return arr


def _as_rng(rng: np.random.Generator | int | None) -> np.random.Generator:
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)
