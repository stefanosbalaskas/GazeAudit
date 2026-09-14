---
title: API map
description: Task-oriented map of the public GazeAudit API for study representation, structural QC, uncertainty, robustness, sensitivity, interoperability, and publication evidence.
kicker: Reference
permalink: /docs/reference/api-map/
---

# API map

This page is a task-oriented map of the public API exposed by `gazeaudit`. Function docstrings remain the source-level reference; the map helps you find the right entry point without scanning the package source.

## Canonical study representation and structural QC

| API | Purpose |
|---|---|
| `GazeStudy` | Vendor-neutral tabular gaze/fixation representation with semantic column mapping. |
| `audit_study_qc` | Conservative structural preflight for non-finite coordinates/timestamps, identifier gaps, duplicate timestamps, and decreasing within-trial time. |
| `StudyQCReport` | Frozen machine-readable preflight result with counts, `status`, issue codes, and tabular export. |
| `study_qc_diagnostics` | Deterministic row/group diagnostics with stable IDs and issue/detail codes. |
| `StudyQCDecision` | Explicit researcher decision and rationale attached to a flagged QC issue family. |
| `build_study_qc_audit` | Bind mapped study identity, report, diagnostics, decisions, and software provenance. |
| `StudyQCAudit` | Deterministic structural-QC record with study, audit, and manifest fingerprints. |
| `verify_study_qc_audit` | Detect mutation of the in-memory QC record or its manifest. |
| `verify_study_qc_manifest` | Verify a standalone QC manifest and its nested fingerprints. |
| `write_study_qc_artifacts` | Write deterministic QC JSON/CSV evidence and byte-level integrity metadata. |
| `verify_study_qc_artifacts` | Verify the written QC evidence directory byte-for-byte. |
| `study_qc_publication_metadata` | Create a compact substantive QC descriptor for publication-bundle metadata. |
| `adapt_study` | Adapt an external study object through the `StudyAdapter` contract. |
| `StudyAdapter` | Runtime-checkable protocol for custom study integrations. |
| `DetectionResult` | Normalised event-detection output contract. |
| `DetectorBackend` | Runtime-checkable protocol for external detector backends. |
| `run_detector_backend` | Execute a detector backend against a canonical study. |

The study preflight is descriptive. It does not assign a universal data-quality score or replace calibration, event-detection, missingness, or scientific-validity assessment.

### Structural-QC provenance constants

`STUDY_QC_SCHEMA`, `STUDY_QC_ARTIFACT_SCHEMA`, `STUDY_QC_PUBLICATION_LINK_SCHEMA`, and `STUDY_QC_ISSUE_CODES` expose the stable machine-readable contracts used by the QC provenance layer.

## AOIs and measurement uncertainty

| API | Purpose |
|---|---|
| `RectangleAOI`, `CircleAOI` | Lightweight AOI geometry primitives. |
| `GaussianGazeErrorModel` | Global bivariate Gaussian gaze-position error model. |
| `GroupedGaussianGazeErrorModel` | Declared group-specific collection of Gaussian error models. |
| `aoi_probabilities` | Monte Carlo marginal AOI-membership probabilities. |
| `hard_aoi_membership` | Deterministic AOI membership of observed points. |
| `compare_hard_probabilistic` | Long-form hard/probabilistic membership comparison with flip probability and boundary risk. |
| `summarize_aoi_risk` | AOI-level summary of assignment fragility. |
| `expected_dwell` | Probability-weighted dwell endpoint. |
| `expected_fixation_count` | Probability-weighted fixation-count endpoint. |

## AOI protocol and propagation tooling

| API | Purpose |
|---|---|
| `build_aoi_uncertainty_protocol` | Build a deterministic AOI-uncertainty protocol record. |
| `verify_aoi_uncertainty_protocol` | Verify the protocol record. |
| `audit_aoi_effect_uncertainty` | Propagate AOI uncertainty into an effect audit. |
| `write_aoi_uncertainty_artifacts` | Write bound AOI uncertainty evidence. |
| `verify_aoi_uncertainty_artifacts` | Verify written AOI evidence. |

## Specification spaces and robustness

| API | Purpose |
|---|---|
| `PipelineSpace` | Declare named analytical choices and enumerate combinations deterministically. |
| `run_specs` | Execute valid specifications against one common scalar endpoint. |
| `specification_curve` | Order complete specification results by endpoint estimate. |
| `effect_stability` | Descriptive range, quantiles, sign fractions, and sign stability. |
| `marginal_sensitivity` | Screen factor-level sensitivity using descriptive between-level variation. |
| `pairwise_interaction_sensitivity` | Screen pairwise non-additive sensitivity across specification factors. |

## Controlled sensitivity analyses

| API | Purpose |
|---|---|
| `scale_error_model` | Scale the declared gaze-error model for controlled spatial sensitivity. |
| `spatial_sensitivity_curve` | Evaluate one endpoint over declared error scales. |
| `downsample_gaze` | Retain existing samples nearest a regular target grid; no coordinate interpolation. |
| `sampling_sensitivity_curve` | Evaluate one endpoint across controlled target sampling rates. |
| `missingness_mask` | Construct a missingness mask under the declared mechanism. |
| `inject_missingness` | Apply controlled missingness to a study. |
| `missingness_sensitivity_curve` | Evaluate one endpoint across declared missingness levels/mechanisms. |
| `summarize_missingness` | Summarise missingness in the perturbed record. |

## Known-truth and conclusion recovery

| API | Purpose |
|---|---|
| `simulate_boundary_data` | Synthetic boundary-focused AOI benchmark data. |
| `fit_error_model_from_known_truth` | Fit an error model from known-truth benchmark information. |
| `evaluate_aoi_recovery` | Evaluate AOI recovery in a known-truth setting. |
| `simulate_known_aoi_effect` | Generate known AOI effect data for scientific recovery benchmarking. |
| `benchmark_known_aoi_effect` | Benchmark recovery of the known effect. |
| `condition_dwell_effect` | Compute the benchmark condition dwell contrast. |
| `ConclusionRule` | Predeclared effect-error/direction/recovery criterion. |
| `conclusion_recovery_table` | Evaluate specifications under a conclusion rule. |
| `summarize_conclusion_recovery` | Summarise recovery results. |
| `run_canonical_conclusion_benchmark` | Run the canonical known-truth conclusion benchmark. |
| `run_paired_conclusion_benchmark` | Paired benchmark comparing alternative analysis families. |

## Publication and provenance

| API | Purpose |
|---|---|
| `build_conclusion_audit_bundle` | Bind results, conclusion rule, source description, methods/report, metadata, and provenance. |
| `PublicationAuditBundle` | Deterministic bundle object containing scientific and execution evidence. |
| `verify_publication_audit_bundle` | Detect mutation of bound publication evidence. |
| `study_qc_publication_metadata` | Bind structural-QC scientific identity through the existing publication metadata channel. |
| `render_publication_methods` | Deterministic methods text for the audit. |
| `render_publication_markdown` | Deterministic Markdown report. |
| `canonical_json` | Canonical serialisation used by provenance fingerprints. |
| `fingerprint` | Deterministic content fingerprint helper. |
| `specification_manifest` | Manifest of the declared specification. |
| `results_manifest` | Manifest of bound results. |
| `software_environment` | Capture relevant execution-environment metadata. |

## Eye-Tracking-BIDS

| API | Purpose |
|---|---|
| `read_bids_eyetrack` | Read one eye-tracking `physio.tsv[.gz]` record into canonical form. |
| `read_bids_eyetrack_many` | Read multiple BIDS eye-tracking records. |
| `parse_bids_entities` | Parse BIDS entities from a supported source path. |
| `BIDSEyeTrackingRecord` | Record wrapper containing canonical study and source metadata. |
| `BIDSEyeTrackingAdapter` | BIDS adapter contract. |

GazeAudit is not a replacement for the official BIDS Validator.

## pymovements

| API | Purpose |
|---|---|
| `from_pymovements_gaze` | Convert a `pymovements.Gaze` object into `GazeStudy`. |
| `from_pymovements_dataset` | Convert supported dataset-level input. |
| `PymovementsGazeAdapter` | Adapter implementation for pymovements gaze data. |

Install the optional extra with:

```bash
python -m pip install "gazeaudit[pymovements]==0.1.0"
```

## pEYES

| API | Purpose |
|---|---|
| `make_peyes_detector` | Construct a supported pEYES detector adapter. |
| `run_peyes_detector` | Execute the detector and return a normalised `DetectionResult`. |
| `PeyesDetectorAdapter` | Adapter implementation for pEYES. |

The current pEYES optional dependency is available on Python 3.12+.

## Frozen scientific-validation tooling

The public package also exposes source-lock, protocol, execution, partitioning, artifact-writing, and verification functions for the GazeBase and Korthals validation programmes. These functions support the package's own auditable validation workflows and are more specialised than the normal user-facing analysis path.

Start with the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) before reusing validation-specific functions, because their scientific meaning is tied to frozen protocol/source contracts.

## Recommended entry points by task

- **I have a vendor or analysis table:** `GazeStudy` → `audit_study_qc` → `study_qc_diagnostics` → explicit `StudyQCDecision` values → `build_study_qc_audit`.
- **I need portable QC evidence:** `write_study_qc_artifacts` → archive → `verify_study_qc_artifacts`.
- **I have validation data and AOIs:** `GaussianGazeErrorModel` → `aoi_probabilities` → `compare_hard_probabilistic` → uncertainty-weighted endpoint.
- **I have multiple defensible analysis choices:** `PipelineSpace` → `run_specs` → `specification_curve` → `effect_stability` → sensitivity diagnostics.
- **I need sampling/missingness stress tests:** `sampling_sensitivity_curve` / `missingness_sensitivity_curve`.
- **I need a reproducible conclusion record:** `ConclusionRule` + optional `study_qc_publication_metadata` → `build_conclusion_audit_bundle` → `verify_publication_audit_bundle`.
- **I have external data/detectors:** use BIDS/pymovements/pEYES adapters or implement the study/detector protocols.

For conceptual guidance, return to the [documentation hub]({{ '/docs/' | relative_url }}).
