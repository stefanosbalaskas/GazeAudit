---
title: Core public API inventory
description: Generated-style inventory contract for the user-facing GazeAudit API families that are protected against documentation drift.
kicker: Reference
permalink: /docs/reference/core-api-inventory/
---

# Core public API inventory

This page is the documentation-side contract for the core user-facing exports in `gazeaudit.__all__`. CI compares these names with the package initializer so that adding or removing a public analysis API cannot silently drift away from the site.

The inventory deliberately focuses on normal research workflows. Frozen validation-programme internals remain documented through the validation matrix and their protocol-specific pages.

## Study representation and structural QC

`GazeStudy`, `StudyQCReport`, `StudyQCDecision`, `StudyQCAudit`, `audit_study_qc`, `study_qc_diagnostics`, `build_study_qc_audit`, `verify_study_qc_audit`, `verify_study_qc_manifest`, `write_study_qc_artifacts`, `verify_study_qc_artifacts`, `study_qc_publication_metadata`.

## Analysis-readiness governance

`ReadinessThresholds`, `AnalysisReadinessReport`, `RepairComparison`, `trial_qc_summary`, `participant_qc_summary`, `evaluate_analysis_readiness`, `cohort_impact_preview`, `filter_study_by_readiness`, `readiness_policy_table`, `readiness_pipeline_processor`, `compare_qc_states`, `analysis_readiness_publication_metadata`, `write_analysis_readiness_artifacts`, `verify_analysis_readiness_artifacts`, `verify_analysis_readiness_report`, `verify_analysis_readiness_manifest`, `verify_repair_comparison`, `verify_repair_comparison_manifest`.

## AOIs and uncertainty

`RectangleAOI`, `CircleAOI`, `GazeErrorModel`, `GaussianGazeErrorModel`, `GroupedGaussianGazeErrorModel`, `aoi_probabilities`, `hard_aoi_membership`, `compare_hard_probabilistic`, `summarize_aoi_risk`, `expected_dwell`, `expected_fixation_count`.

## Robustness and controlled sensitivity

`PipelineSpace`, `run_specs`, `specification_curve`, `effect_stability`, `marginal_sensitivity`, `pairwise_interaction_sensitivity`, `downsample_gaze`, `sampling_sensitivity_curve`, `scale_error_model`, `spatial_sensitivity_curve`.

## Plotting

`plot_qc_issue_profile`, `plot_trial_readiness`, `plot_participant_readiness`, `plot_cohort_impact`, `plot_repair_comparison`, `plot_policy_tradeoffs`, `plot_threshold_sweep`, `plot_specification_curve`, `plot_factor_sensitivity`, `plot_sensitivity_curve`, `plot_gaze_trajectory`, `plot_aoi_probability_profile`, `plot_recovery_matrix`.

For task-oriented descriptions, use the [API map]({{ '/docs/reference/api-map/' | relative_url }}). For visual examples, use the [plot gallery]({{ '/docs/plots/' | relative_url }}).
