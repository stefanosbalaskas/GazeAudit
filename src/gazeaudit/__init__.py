"""GazeAudit: uncertainty-aware robustness analysis for eye-tracking research."""

from .adapters import (
    DetectionResult,
    DetectorBackend,
    StudyAdapter,
    adapt_study,
    run_detector_backend,
)
from .aoi import CircleAOI, RectangleAOI
from .aoi_audit import (
    compare_hard_probabilistic,
    hard_aoi_membership,
    summarize_aoi_risk,
)
from .benchmark import (
    evaluate_aoi_recovery,
    fit_error_model_from_known_truth,
    simulate_boundary_data,
)
from .bids_adapter import (
    BIDSEyeTrackingAdapter,
    BIDSEyeTrackingRecord,
    parse_bids_entities,
    read_bids_eyetrack,
    read_bids_eyetrack_many,
)
from .endpoints import expected_dwell, expected_fixation_count
from .missingness import (
    inject_missingness,
    missingness_mask,
    missingness_sensitivity_curve,
    summarize_missingness,
)
from .multiverse import PipelineSpace, run_specs
from .peyes_adapter import PeyesDetectorAdapter, make_peyes_detector, run_peyes_detector
from .provenance import (
    canonical_json,
    fingerprint,
    results_manifest,
    software_environment,
    specification_manifest,
)
from .pymovements_adapter import (
    PymovementsGazeAdapter,
    from_pymovements_dataset,
    from_pymovements_gaze,
)
from .robustness import (
    effect_stability,
    marginal_sensitivity,
    pairwise_interaction_sensitivity,
    specification_curve,
)
from .sampling import downsample_gaze, sampling_sensitivity_curve
from .scientific_benchmark import (
    benchmark_known_aoi_effect,
    condition_dwell_effect,
    simulate_known_aoi_effect,
)
from .sensitivity import scale_error_model, spatial_sensitivity_curve
from .study import GazeStudy
from .uncertainty import GaussianGazeErrorModel, aoi_probabilities

__all__ = [
    "BIDSEyeTrackingAdapter",
    "BIDSEyeTrackingRecord",
    "CircleAOI",
    "DetectionResult",
    "DetectorBackend",
    "GazeStudy",
    "GaussianGazeErrorModel",
    "PeyesDetectorAdapter",
    "PipelineSpace",
    "PymovementsGazeAdapter",
    "RectangleAOI",
    "StudyAdapter",
    "adapt_study",
    "aoi_probabilities",
    "benchmark_known_aoi_effect",
    "canonical_json",
    "compare_hard_probabilistic",
    "condition_dwell_effect",
    "downsample_gaze",
    "effect_stability",
    "evaluate_aoi_recovery",
    "expected_dwell",
    "expected_fixation_count",
    "fingerprint",
    "fit_error_model_from_known_truth",
    "from_pymovements_dataset",
    "from_pymovements_gaze",
    "hard_aoi_membership",
    "inject_missingness",
    "make_peyes_detector",
    "marginal_sensitivity",
    "missingness_mask",
    "missingness_sensitivity_curve",
    "pairwise_interaction_sensitivity",
    "parse_bids_entities",
    "read_bids_eyetrack",
    "read_bids_eyetrack_many",
    "results_manifest",
    "run_detector_backend",
    "run_peyes_detector",
    "run_specs",
    "sampling_sensitivity_curve",
    "scale_error_model",
    "simulate_boundary_data",
    "simulate_known_aoi_effect",
    "software_environment",
    "spatial_sensitivity_curve",
    "specification_curve",
    "specification_manifest",
    "summarize_aoi_risk",
    "summarize_missingness",
]

__version__ = "0.1.0.dev5"
