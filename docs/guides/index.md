---
title: Guides
description: Task-oriented GazeAudit guides for project setup, researcher decisions, data onboarding, uncertainty, robustness design, troubleshooting, result interpretation, reporting, publication, and interoperability.
kicker: Guides
---

# Guides

The guides explain **how to design, govern, interpret, troubleshoot, and report** GazeAudit analyses. For copy-paste runnable demonstrations, use the [examples](../examples/).

## Choose by task

<div class="card-grid">
  <article class="card">
    <div class="card-icon" aria-hidden="true">1</div>
    <h3>Set up the research record</h3>
    <p>Separate source data, researcher-owned decisions, analysis code, generated evidence, and exact software identity before the project becomes difficult to audit.</p>
    <p><a href="project-starter/">Project starter →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">2</div>
    <h3>Govern researcher decisions</h3>
    <p>Use a before/during/after checklist and a copy-ready decision log so thresholds, exclusions, specifications, deviations, and reporting boundaries stay visible.</p>
    <p><a href="researcher-audit-checklist/">Researcher checklist →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">3</div>
    <h3>Interpret the completed audit</h3>
    <p>Check execution completeness first, then separate direction stability, magnitude sensitivity, descriptive factor alignment, and unresolved uncertainty before choosing manuscript wording.</p>
    <p><a href="interpret-audit-result/">Interpret an audit result →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">4</div>
    <h3>Prepare publication evidence</h3>
    <p>Bind the complete audit bundle, provenance, fingerprints, methods wording, results wording, and unresolved limitations into a durable record.</p>
    <p><a href="publication-audits/">Publication audits →</a></p>
  </article>
</div>

## Start with your own data

### [Start a reproducible GazeAudit project](project-starter/)

Set up a compact study directory that separates the canonical input table, analysis code, researcher decisions, software record, and generated evidence. Use this when you want a clean project scaffold before adapting the practical first-audit example.

### [Researcher audit checklist](researcher-audit-checklist/)

Use a before/during/after checklist for source binding, endpoint declaration, QC policy, exclusions, specification design, failure handling, robustness interpretation, reporting language, and archive handoff. This is the practical governance layer between reproducible code and defensible scientific judgement.

### [Audit decision log template](audit-decision-log-template/)

Copy a structured Markdown record into the project repository to preserve source identity, endpoints, QC decisions, exclusions, declared specification factors, perturbations, deviations, software identity, generated evidence, and reporting boundaries.

### [First real audit with your own data](first-real-audit/)

Take one canonical eye-tracking CSV through `GazeStudy`, structural preflight, researcher-owned decisions, a declared specification space, robustness summaries, and saved evidence. This is the recommended practical entry point when you have a study file and want to understand how the package pieces connect.

### [Audit record map](audit-record-map/)

Follow the research record from source data and researcher-owned decisions through structural QC, declared specification execution, robustness and sensitivity summaries, provenance, fingerprints, and publication claims. Use this when you need to understand **how one artifact supports the next stage of the audit** rather than only what each file contains.

### [Understanding the audit output bundle](audit-output-bundle/)

Read the files produced by the practical workflow as one evidence bundle: structural QC and fingerprints, every declared specification, the specification curve, effect-stability summaries, and marginal and pairwise sensitivity outputs. The guide separates what each artifact describes from conclusions it cannot establish.

## Data onboarding

### [Data onboarding and structural preflight](data-onboarding/)

Map vendor or analysis tables into `GazeStudy`, inspect structural QC, and separate import/ordering problems from scientific quality decisions before running uncertainty or robustness analyses.

### [Analysis-readiness governance](analysis-readiness/)

Declare structural-QC policies, preview cohort impact, separate repairable structural conditions from scientific exclusions, and bind the resulting readiness record to provenance.

## Measurement uncertainty

### [AOI uncertainty](aoi-uncertainty/)

Fit global or grouped gaze-error models, propagate spatial uncertainty into AOI membership, compare hard and probabilistic assignments, and identify boundary-sensitive observations.

## Analytical robustness

### [Specification spaces](specification-space/)

Turn defensible analytical decisions into an explicit `PipelineSpace`, reject invalid combinations before execution, and summarise endpoint stability without selecting a preferred specification after the fact.

### [Interpret an audit result](interpret-audit-result/)

Move from completed robustness outputs to bounded scientific interpretation. The guide starts with the declared execution denominator, then separates direction stability from magnitude sensitivity, treats marginal/pairwise summaries as descriptive rather than causal, records untested uncertainty dimensions, and maps each evidence pattern to an appropriate next action.

For a side-by-side worked comparison, use the [result-pattern reporting example](../examples/result-patterns/).

### [Reporting robustness](reporting-robustness/)

Translate specification curves, sign fractions, marginal sensitivity, and pairwise sensitivity into precise Methods and Results language without treating descriptive diagnostics as confidence intervals, posterior probabilities, or causal decompositions.

For a complete worked interpretation exercise, use the [decision-to-report example](../examples/decision-to-report/).

## Troubleshooting the research record

### [Common audit mistakes and repairs](common-audit-mistakes/)

Diagnose nine recurring failure patterns: outcome-informed specification design, silent branch deletion, endpoint drift, QC/exclusion confusion, hidden interpolation or missingness repair, inferential over-reading of robustness summaries, rewritten decision history, incomplete archives, and transfer of protocol-bound case labels to new data. Each failure is paired with a concrete repair and the evidence that should be preserved.

Use this guide when an analysis runs successfully but the **decision trail, completeness, or reporting boundary** is still difficult to defend.

## Reproducibility

### [Publication audits](publication-audits/)

Use a predeclared conclusion rule, deterministic manifests, methods/report generation, and scientific/bundle fingerprints to make robustness evidence auditable.

### [Publication and archive handoff example](../examples/publication-archive-handoff/)

See one illustrative end state that brings together decision history, complete branch accountability, manuscript Methods/Results wording, limitations, source/software provenance, fingerprints, and a reviewer-friendly archive manifest. All effect values in the worked handoff are synthetic teaching material.

## Ecosystem integration

### [Interoperability](interoperability/)

Understand the division of responsibility between GazeAudit and Eye-Tracking-BIDS, pymovements, pEYES, and custom study/detector adapters.

## A practical sequence

1. [Project starter](project-starter/) — create the study structure.
2. [Researcher audit checklist](researcher-audit-checklist/) — declare and govern decisions.
3. [Decision log template](audit-decision-log-template/) — preserve those decisions and amendments.
4. [First real audit](first-real-audit/) — run the practical CSV-to-evidence path.
5. [Audit output bundle](audit-output-bundle/) — understand what each artifact establishes.
6. [Common audit mistakes](common-audit-mistakes/) — diagnose record and execution failures before interpretation.
7. [Interpret an audit result](interpret-audit-result/) — separate completeness, direction, magnitude, and unresolved uncertainty.
8. [Result-pattern example](../examples/result-patterns/) — compare four synthetic evidence patterns and bounded wording.
9. [Decision-to-report example](../examples/decision-to-report/) — practice bounded interpretation on the deterministic 12-branch exercise.
10. [Publication/archive handoff](../examples/publication-archive-handoff/) — assemble a reviewable end state.
11. [Publication audits](publication-audits/) — build and verify the durable research record.

## What a guide is not

Guides describe GazeAudit's scientific contracts and recommended use. They do not replace study-specific justification. Researchers remain responsible for deciding which AOIs, error models, detectors, preprocessing choices, QC thresholds, perturbations, and scientific endpoints are defensible for their design.