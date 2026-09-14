---
title: Examples
description: Runnable synthetic examples for GazeAudit measurement uncertainty, specification spaces, complete robustness audits, and sensitivity analysis.
kicker: Examples
---

# Examples

These examples are intentionally small and use **synthetic data** unless stated otherwise. Their purpose is to make GazeAudit's contracts runnable without private eye-tracking files.

<div class="callout info">
<strong>Want one complete workflow?</strong>
Start with the <a href="end-to-end-robustness/">end-to-end robustness audit</a>. It constructs a canonical study, declares a decision space, executes all specifications, and produces stability plus sensitivity diagnostics in one deterministic script.
</div>

## [End-to-end robustness audit](end-to-end-robustness/)

Run a complete 12-specification synthetic audit from `GazeStudy` construction through `PipelineSpace`, `run_specs()`, specification ordering, effect stability, marginal sensitivity, and pairwise interaction diagnostics.

**Use this when:** you want a copy-ready template showing how the main robustness pieces fit together in one executable analysis.

## [AOI boundary uncertainty](aoi-boundary/)

Fit `GaussianGazeErrorModel`, define adjacent AOIs, estimate probabilistic membership, and compare hard versus uncertainty-aware assignment.

**Use this when:** you want to understand the measurement-error layer before building a larger analysis.

## [Specification curve](specification-curve/)

Create a synthetic results table, order estimates with `specification_curve()`, calculate `effect_stability()`, and screen factor sensitivity.

**Use this when:** you already have one estimate per defensible analytical specification and want to understand the robustness summaries.

## [Sampling sensitivity](sampling-sensitivity/)

Create a canonical `GazeStudy`, downsample the same participant-by-trial stream to controlled target rates, and evaluate one endpoint with `sampling_sensitivity_curve()`.

**Use this when:** sampling rate is a plausible source of inferential sensitivity.

## Suggested learning path

1. Run the [AOI boundary example](aoi-boundary/) if spatial measurement uncertainty is new to you.
2. Run the [end-to-end robustness audit](end-to-end-robustness/) to see a full specification workflow.
3. Use [sampling sensitivity](sampling-sensitivity/) when temporal resolution is part of the scientific question.
4. Move to the [research workflows](../workflows/) when adapting these pieces to a real study.

## Visual convention

Plots in these example pages are explanatory figures. When they display synthetic values, the page and figure say so explicitly. Frozen empirical validation results remain in the [validation matrix](../VALIDATION_MATRIX.html) and case-specific result records.
