"""Measurement-error models and probabilistic AOI assignment."""

from __future__ import annotations

from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

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
    ) -> GaussianGazeErrorModel:
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

    @classmethod
    def from_mean_radial_error(
        cls,
        mean_radial_error: float,
        *,
        n_validation: int,
        bias: Sequence[float] = (0.0, 0.0),
    ) -> GaussianGazeErrorModel:
        """Construct an isotropic Gaussian model from mean radial validation error.

        This constructor is for validation summaries that report a mean Euclidean
        position error but not pointwise x/y residuals. It makes an explicit modelling
        assumption: after the supplied systematic ``bias`` is removed, x and y errors
        are independent zero-mean Gaussians with a common standard deviation ``sigma``.
        The radial magnitude then follows a Rayleigh distribution with
        ``E[R] = sigma * sqrt(pi / 2)``. Therefore
        ``sigma = mean_radial_error / sqrt(pi / 2)``.

        The conversion is an assumption-driven approximation; it does not recover
        anisotropy, spatial non-stationarity, or uncertainty in the reported validation
        summary itself.
        """

        try:
            radial = float(mean_radial_error)
        except (TypeError, ValueError) as exc:
            raise TypeError("mean_radial_error must be a numeric scalar") from exc
        if not np.isfinite(radial) or radial < 0.0:
            raise ValueError("mean_radial_error must be finite and non-negative")
        bias_arr = np.asarray(bias, dtype=float)
        if bias_arr.shape != (2,) or not np.all(np.isfinite(bias_arr)):
            raise ValueError("bias must contain two finite values")

        sigma = radial / np.sqrt(np.pi / 2.0)
        covariance = np.eye(2, dtype=float) * sigma**2
        return cls(
            mean_error=bias_arr,
            covariance=covariance,
            n_validation=n_validation,
        )

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


@dataclass(frozen=True)
class GroupedGaussianGazeErrorModel:
    """Collection of Gaussian gaze-error models indexed by scientific group.

    Grouping allows measurement uncertainty to differ across participants,
    calibration/validation blocks, sessions, devices, or any predeclared combination
    of those factors. Every observation supplied to a grouped audit must map to exactly
    one declared model; missing or unknown groups fail closed rather than falling back
    to a pooled model.
    """

    models: Mapping[Hashable, GaussianGazeErrorModel]

    def __post_init__(self) -> None:
        if not isinstance(self.models, Mapping):
            raise TypeError("models must be a mapping")
        copied = dict(self.models)
        if not copied:
            raise ValueError("models must contain at least one group")
        for key, model in copied.items():
            if not isinstance(key, Hashable):
                raise TypeError("error-model group keys must be hashable")
            if _is_missing_group(key):
                raise ValueError("error-model group keys must not be missing")
            if not isinstance(model, GaussianGazeErrorModel):
                raise TypeError("every grouped error model must be GaussianGazeErrorModel")
        object.__setattr__(self, "models", MappingProxyType(copied))

    @classmethod
    def from_mean_radial_errors(
        cls,
        mean_radial_errors: Mapping[Hashable, float],
        *,
        n_validation: int | Mapping[Hashable, int],
        bias: Sequence[float] | Mapping[Hashable, Sequence[float]] = (0.0, 0.0),
    ) -> GroupedGaussianGazeErrorModel:
        """Build grouped isotropic models from mean radial validation summaries.

        ``n_validation`` and ``bias`` may be common to every group or supplied as
        mappings keyed identically to ``mean_radial_errors``. The same Rayleigh-to-
        Gaussian assumption documented by ``GaussianGazeErrorModel`` applies
        independently to every group.
        """

        if not isinstance(mean_radial_errors, Mapping) or not mean_radial_errors:
            raise ValueError("mean_radial_errors must be a non-empty mapping")

        models: dict[Hashable, GaussianGazeErrorModel] = {}
        for key, radial in mean_radial_errors.items():
            group_n = _group_parameter(n_validation, key, "n_validation")
            if isinstance(bias, Mapping):
                group_bias = _group_parameter(bias, key, "bias")
            else:
                group_bias = bias
            models[key] = GaussianGazeErrorModel.from_mean_radial_error(
                radial,
                n_validation=int(group_n),
                bias=group_bias,
            )
        return cls(models)

    def model_for(self, group: Hashable) -> GaussianGazeErrorModel:
        """Return the declared model for ``group`` or fail closed."""

        if _is_missing_group(group):
            raise ValueError("error-model groups must not contain missing values")
        try:
            return self.models[group]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"unmapped error-model group: {group!r}") from exc

    def validate_groups(self, groups: Sequence[Any], *, n_observations: int) -> np.ndarray:
        """Validate and return one object-valued group key per observation."""

        raw = list(groups)
        values = np.empty(len(raw), dtype=object)
        values[:] = raw
        if len(values) != n_observations:
            raise ValueError("groups must be one-dimensional and match observations")
        for value in values:
            self.model_for(value)
        return values


GazeErrorModel = GaussianGazeErrorModel | GroupedGaussianGazeErrorModel


def aoi_probabilities(
    points: np.ndarray,
    aois: Sequence[AOI],
    error_model: GazeErrorModel,
    *,
    groups: Sequence[Any] | None = None,
    draws: int = 2000,
    rng: np.random.Generator | int | None = None,
    include_outside: bool = True,
) -> pd.DataFrame:
    """Estimate probabilistic AOI membership by Monte Carlo propagation.

    AOIs are allowed to overlap. Therefore AOI probabilities are marginal
    membership probabilities and need not sum to one. ``outside`` is the
    probability of belonging to none of the supplied AOIs.

    For :class:`GroupedGaussianGazeErrorModel`, ``groups`` must provide one declared
    model key per observation. A global :class:`GaussianGazeErrorModel` ignores
    ``groups`` and preserves the original global-model sampling path.
    """

    if not aois:
        raise ValueError("at least one AOI is required")
    names = [aoi.name for aoi in aois]
    if len(names) != len(set(names)):
        raise ValueError("AOI names must be unique")

    arr = _as_points(points)
    if isinstance(error_model, GaussianGazeErrorModel):
        latent = error_model.sample_true_points(arr, draws=draws, rng=rng)
    elif isinstance(error_model, GroupedGaussianGazeErrorModel):
        if groups is None:
            raise ValueError("groups are required for a grouped error model")
        latent = _sample_grouped_true_points(
            arr,
            error_model,
            groups=groups,
            draws=draws,
            rng=rng,
        )
    else:
        raise TypeError(
            "error_model must be GaussianGazeErrorModel or GroupedGaussianGazeErrorModel"
        )

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


def sample_grouped_errors_draw_major(
    error_model: GroupedGaussianGazeErrorModel,
    groups: Sequence[Any],
    *,
    n_observations: int,
    draws: int,
    rng: np.random.Generator | int | None = None,
) -> np.ndarray:
    """Sample grouped measurement errors with shape ``(draws, observations, 2)``.

    This helper is public so higher-level uncertainty propagators can share the exact
    grouped sampling contract without duplicating group validation or fallback logic.
    """

    if draws < 1:
        raise ValueError("draws must be at least 1")
    group_values = error_model.validate_groups(groups, n_observations=n_observations)
    generator = _as_rng(rng)
    errors = np.empty((draws, n_observations, 2), dtype=float)

    # Preserve first-observation group order instead of sorting heterogeneous keys.
    ordered_groups = list(dict.fromkeys(group_values.tolist()))
    for group in ordered_groups:
        mask = np.fromiter((value == group for value in group_values), dtype=bool)
        model = error_model.model_for(group)
        errors[:, mask, :] = generator.multivariate_normal(
            mean=model.mean_error,
            cov=model.covariance,
            size=(draws, int(mask.sum())),
            check_valid="raise",
        )
    return errors


def _sample_grouped_true_points(
    points: np.ndarray,
    error_model: GroupedGaussianGazeErrorModel,
    *,
    groups: Sequence[Any],
    draws: int,
    rng: np.random.Generator | int | None,
) -> np.ndarray:
    if draws < 1:
        raise ValueError("draws must be at least 1")
    group_values = error_model.validate_groups(groups, n_observations=len(points))
    generator = _as_rng(rng)
    latent = np.empty((len(points), draws, 2), dtype=float)
    ordered_groups = list(dict.fromkeys(group_values.tolist()))
    for group in ordered_groups:
        mask = np.fromiter((value == group for value in group_values), dtype=bool)
        model = error_model.model_for(group)
        latent[mask] = model.sample_true_points(points[mask], draws=draws, rng=generator)
    return latent


def _group_parameter(parameter: Any, key: Hashable, label: str) -> Any:
    if isinstance(parameter, Mapping):
        if key not in parameter:
            raise ValueError(f"{label} is missing group {key!r}")
        return parameter[key]
    return parameter


def _is_missing_group(value: Any) -> bool:
    if isinstance(value, tuple):
        return any(_is_missing_group(item) for item in value)
    try:
        missing = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if isinstance(missing, (bool, np.bool_)):
        return bool(missing)
    return False


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
