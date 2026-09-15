---
title: Guides
description: Task-oriented GazeAudit guides for data onboarding, uncertainty, robustness design and reporting, publication, and interoperability.
kicker: Guides
---

# Guides

The guides explain **how to design, interpret, and report** GazeAudit analyses. For copy-paste runnable demonstrations, use the [examples](../examples/).

## Data onboarding

### [Data onboarding and structural preflight](data-onboarding/)

Map vendor or analysis tables into `GazeStudy`, inspect structural QC, and separate import/ordering problems from scientific quality decisions before running uncertainty or robustness analyses.

## Measurement uncertainty

### [AOI uncertainty](aoi-uncertainty/)

Fit global or grouped gaze-error models, propagate spatial uncertainty into AOI membership, compare hard and probabilistic assignments, and identify boundary-sensitive observations.

## Analytical robustness

### [Specification spaces](specification-space/)

Turn defensible analytical decisions into an explicit `PipelineSpace`, reject invalid combinations before execution, and summarise endpoint stability without selecting a preferred specification after the fact.

### [Reporting robustness](reporting-robustness/)

Translate specification curves, sign fractions, marginal sensitivity, and pairwise sensitivity into precise Methods and Results language without treating descriptive diagnostics as confidence intervals, posterior probabilities, or causal decompositions.

## Reproducibility

### [Publication audits](publication-audits/)

Use a predeclared conclusion rule, deterministic manifests, methods/report generation, and scientific/bundle fingerprints to make robustness evidence auditable.

## Ecosystem integration

### [Interoperability](interoperability/)

Understand the division of responsibility between GazeAudit and Eye-Tracking-BIDS, pymovements, pEYES, and custom study/detector adapters.

## What a guide is not

Guides describe GazeAudit's scientific contracts and recommended use. They do not replace study-specific justification. Researchers remain responsible for deciding which AOIs, error models, detectors, preprocessing choices, QC thresholds, perturbations, and scientific endpoints are defensible for their design.

- [Analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}) — declare structural-QC policies, preview cohort impact, and bind provenance.
