"""GazeAudit: uncertainty-aware robustness analysis for eye-tracking research."""

from .aoi import CircleAOI, RectangleAOI
from .endpoints import expected_dwell, expected_fixation_count
from .multiverse import PipelineSpace, run_specs
from .robustness import effect_stability, marginal_sensitivity
from .study import GazeStudy
from .uncertainty import GaussianGazeErrorModel, aoi_probabilities

__all__ = [
    "CircleAOI",
    "RectangleAOI",
    "GazeStudy",
    "GaussianGazeErrorModel",
    "PipelineSpace",
    "aoi_probabilities",
    "effect_stability",
    "expected_dwell",
    "expected_fixation_count",
    "marginal_sensitivity",
    "run_specs",
]

__version__ = "0.1.0.dev0"
