---
title: Examples
description: Runnable synthetic and project-oriented examples for GazeAudit data preflight, measurement uncertainty, specification spaces, complete robustness audits, and sensitivity analysis.
kicker: Examples
---

# Examples

These examples are intentionally small. Demonstration datasets are **synthetic unless stated otherwise**; project-oriented examples are explicit about which parts must be replaced with study-specific decisions.

<div class="callout info">
<strong>Starting with your own data?</strong>
Use the <a href="first-real-audit/">first real audit example</a> for a CSV-oriented command-line path that writes structural-QC provenance and robustness tables. Use the <a href="study-preflight/">study preflight example</a> when you want to focus only on canonical mapping and structural diagnostics.
</div>

## [First real audit](first-real-audit/)

Run one practical script on deterministic demo data or a canonical eye-tracking CSV. The script combines `GazeStudy`, structural-QC fingerprints, a declared 12-specification robustness space, stability/sensitivity summaries, and output writing.

**Use this when:** you have a project file and want a concrete operational template to adapt before moving into study-specific methods.

## [Study preflight](study-preflight/)

Create a canonical `GazeStudy`, run `audit_study_qc()`, inspect stable issue codes, and export a compact QC table. The synthetic example deliberately contains one missing coordinate and a repeated timestamp.

**Use this when:** you are onboarding a new table and want a transparent structural check before measurement or robustness analysis.

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

1. Start with the [first real audit](first-real-audit/) when you want to adapt GazeAudit to your own canonical CSV.
2. Use the [study preflight](study-preflight/) when structural onboarding itself needs closer inspection.
3. Run the [AOI boundary example](aoi-boundary/) if spatial measurement uncertainty is new to you.
4. Run the [end-to-end robustness audit](end-to-end-robustness/) to study the specification API in isolation.
5. Use [sampling sensitivity](sampling-sensitivity/) when temporal resolution is part of the scientific question.
6. Move to the [first-study workflow](../workflows/first-study-audit/) when assembling the full research process.

## Visual convention

Plots in these example pages are explanatory figures. When they display synthetic values, the page and figure say so explicitly. Frozen empirical validation results remain in the [validation matrix](../VALIDATION_MATRIX.html) and case-specific result records.

- [Analysis-readiness example]({{ '/docs/examples/analysis-readiness/' | relative_url }}) — executable policy, cohort-impact, repair, and specification-space workflow.
- [Plot gallery]({{ '/docs/plots/' | relative_url }}) — 14 deterministic code-generated figures with source links.
