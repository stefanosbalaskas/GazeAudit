---
title: Examples
description: Runnable synthetic and project-oriented examples for GazeAudit data preflight, researcher decisions, measurement uncertainty, robustness analysis, sensitivity, and bounded reporting.
kicker: Examples
---

# Examples

These examples are intentionally small. Demonstration datasets are **synthetic unless stated otherwise**; project-oriented examples are explicit about which parts must be replaced with study-specific decisions.

## Choose by task

<div class="card-grid">
  <article class="card">
    <div class="card-icon" aria-hidden="true">1</div>
    <h3>Bring your own gaze table</h3>
    <p>Start from a canonical CSV, inspect structural QC, declare alternatives, and write the complete audit bundle.</p>
    <p><a href="first-real-audit/">First real audit →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">2</div>
    <h3>Learn the robustness API</h3>
    <p>Run a deterministic 12-specification synthetic audit and inspect the specification curve, effect stability, and sensitivity summaries.</p>
    <p><a href="end-to-end-robustness/">End-to-end robustness →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">3</div>
    <h3>Practice interpretation</h3>
    <p>Use the same 12 synthetic branches to move from a decision record to complete robustness evidence and bounded manuscript wording.</p>
    <p><a href="decision-to-report/">Decision-to-report example →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">4</div>
    <h3>Stress a measurement assumption</h3>
    <p>Work through AOI uncertainty or sampling sensitivity when measurement geometry or temporal resolution is part of the scientific question.</p>
    <p><a href="aoi-boundary/">AOI boundary example →</a></p>
  </article>
</div>

<div class="callout info">
<strong>Starting with your own data?</strong>
Use the <a href="first-real-audit/">first real audit example</a> for a CSV-oriented command-line path that writes structural-QC provenance and robustness tables. Use the <a href="study-preflight/">study preflight example</a> when you want to focus only on canonical mapping and structural diagnostics. Use the <a href="../guides/researcher-audit-checklist/">researcher audit checklist</a> before treating any demonstration value as a study-specific decision.
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

## [Decision-to-report worked example](decision-to-report/)

Use the deterministic 12-branch robustness demo to practise recording analytical choices before outcome inspection, reading the complete positive/negative/zero pattern, separating direction from magnitude, and translating the result into bounded Methods and Results language.

**Use this when:** you understand the code path but want to learn what a defensible interpretation and manuscript handoff look like.

## [Analysis readiness](analysis-readiness/)

Work through executable policy, cohort-impact, repair, and specification-space decisions while keeping structural diagnostics separate from scientific exclusions.

**Use this when:** readiness policy and its effect on the analyzable cohort are part of the audit question.

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
2. Use the [researcher audit checklist](../guides/researcher-audit-checklist/) and [decision-log template](../guides/audit-decision-log-template/) to replace demonstration choices with documented study-specific decisions.
3. Use the [study preflight](study-preflight/) when structural onboarding itself needs closer inspection.
4. Run the [end-to-end robustness audit](end-to-end-robustness/) to study the specification API in isolation.
5. Work through [decision-to-report](decision-to-report/) to practise interpreting the complete pattern without selecting a preferred branch after the fact.
6. Run the [AOI boundary example](aoi-boundary/) if spatial measurement uncertainty is part of the question.
7. Use [sampling sensitivity](sampling-sensitivity/) when temporal resolution is part of the scientific question.
8. Move to the [first-study workflow](../workflows/first-study-audit/) when assembling the full research process.

## Visual convention

Plots in these example pages are explanatory figures. When they display synthetic values, the page and figure say so explicitly. Frozen empirical validation results remain in the [validation matrix](../VALIDATION_MATRIX.html) and case-specific result records.

- [Plot gallery]({{ '/docs/plots/' | relative_url }}) — 14 deterministic code-generated figures with source links.
