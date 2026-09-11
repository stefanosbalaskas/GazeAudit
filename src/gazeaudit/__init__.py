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
from .aoi_propagation import AOIEffectUncertaintyAudit, audit_aoi_effect_uncertainty
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
from .conclusion import (
    ConclusionBenchmark,
    ConclusionRule,
    aoi_conclusion_specifications,
    conclusion_recovery_table,
    run_canonical_conclusion_benchmark,
    run_paired_conclusion_benchmark,
    summarize_conclusion_recovery,
)
from .endpoints import expected_dwell, expected_fixation_count
from .gazebase_artifacts import (
    ARTIFACT_SCHEMA,
    verify_gazebase_execution_artifacts,
    write_gazebase_execution_artifacts,
)
from .gazebase_execution import (
    GAZEBASE_ARCHIVE_MD5,
    GAZEBASE_CASE_STUDY_ID,
    GAZEBASE_DETECTORS,
    GAZEBASE_PROTOCOL_FINGERPRINT,
    GAZEBASE_TASKS,
    GazeBaseExecution,
    PreparedGazeBaseData,
    load_gazebase_protocol,
    run_gazebase_multidetector_execution,
    verify_gazebase_protocol,
    verify_gazebase_software_versions,
)
from .gazebase_failure import run_gazebase_detector_partition_fail_closed
from .gazebase_partitioned import (
    PARTITION_SCHEMA,
    GazeBaseDetectorPartition,
    GazeBaseExecutionContext,
    assemble_gazebase_partitioned_execution,
    detector_partition_document,
    prepare_gazebase_execution_context,
    read_gazebase_detector_partition,
    run_gazebase_detector_partition,
    write_gazebase_detector_partition,
)
from .gazebase_pymovements import prepare_gazebase_pymovements_dataset
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
from .publication import (
    PublicationAuditBundle,
    build_conclusion_audit_bundle,
    render_publication_markdown,
    render_publication_methods,
    verify_publication_audit_bundle,
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
from .task_contrast import (
    DetectorRobustnessAudit,
    audit_detector_robustness,
    detector_task_contrast,
    fixation_event_durations,
    fixed_reference_cohort,
    participant_task_fixation_summary,
)
from .uncertainty import GaussianGazeErrorModel, aoi_probabilities

__all__ = [
    "AOIEffectUncertaintyAudit",
    "ARTIFACT_SCHEMA",
    "BIDSEyeTrackingAdapter",
    "BIDSEyeTrackingRecord",
    "CircleAOI",
    "ConclusionBenchmark",
    "ConclusionRule",
    "DetectionResult",
    "DetectorBackend",
    "DetectorRobustnessAudit",
    "GAZEBASE_ARCHIVE_MD5",
    "GAZEBASE_CASE_STUDY_ID",
    "GAZEBASE_DETECTORS",
    "GAZEBASE_PROTOCOL_FINGERPRINT",
    "GAZEBASE_TASKS",
    "GazeBaseDetectorPartition",
    "GazeBaseExecution",
    "GazeBaseExecutionContext",
    "GazeStudy",
    "GaussianGazeErrorModel",
    "PARTITION_SCHEMA",
    "PeyesDetectorAdapter",
    "PipelineSpace",
    "PreparedGazeBaseData",
    "PublicationAuditBundle",
    "PymovementsGazeAdapter",
    "RectangleAOI",
    "StudyAdapter",
    "adapt_study",
    "aoi_conclusion_specifications",
    "aoi_probabilities",
    "assemble_gazebase_partitioned_execution",
    "audit_aoi_effect_uncertainty",
    "audit_detector_robustness",
    "benchmark_known_aoi_effect",
    "build_conclusion_audit_bundle",
    "canonical_json",
    "compare_hard_probabilistic",
    "conclusion_recovery_table",
    "condition_dwell_effect",
    "detector_partition_document",
    "detector_task_contrast",
    "downsample_gaze",
    "effect_stability",
    "evaluate_aoi_recovery",
    "expected_dwell",
    "expected_fixation_count",
    "fingerprint",
    "fit_error_model_from_known_truth",
    "fixation_event_durations",
    "fixed_reference_cohort",
    "from_pymovements_dataset",
    "from_pymovements_gaze",
    "hard_aoi_membership",
    "inject_missingness",
    "load_gazebase_protocol",
    "make_peyes_detector",
    "marginal_sensitivity",
    "missingness_mask",
    "missingness_sensitivity_curve",
    "pairwise_interaction_sensitivity",
    "parse_bids_entities",
    "participant_task_fixation_summary",
    "prepare_gazebase_execution_context",
    "prepare_gazebase_pymovements_dataset",
    "read_bids_eyetrack",
    "read_bids_eyetrack_many",
    "read_gazebase_detector_partition",
    "render_publication_markdown",
    "render_publication_methods",
    "results_manifest",
    "run_canonical_conclusion_benchmark",
    "run_detector_backend",
    "run_gazebase_detector_partition",
    "run_gazebase_detector_partition_fail_closed",
    "run_gazebase_multidetector_execution",
    "run_paired_conclusion_benchmark",
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
    "summarize_conclusion_recovery",
    "summarize_missingness",
    "verify_gazebase_execution_artifacts",
    "verify_gazebase_protocol",
    "verify_gazebase_software_versions",
    "verify_publication_audit_bundle",
    "write_gazebase_detector_partition",
    "write_gazebase_execution_artifacts",
]

__version__ = "0.1.0.dev13"
