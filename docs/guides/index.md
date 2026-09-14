---
title: Guides
description: Task-oriented GazeAudit guides for uncertainty, robustness, publication, and interoperability.
kicker: Guides
---

# Guides

The guides explain **how to design and interpret** GazeAudit analyses. For copy-paste runnable demonstrations, use the [examples](../examples/).

## Measurement uncertainty

### [AOI uncertainty](aoi-uncertainty/)

Fit global or grouped gaze-error models, propagate spatial uncertainty into AOI membership, compare hard and probabilistic assignments, and identify boundary-sensitive observations.

## Analytical robustness

### [Specification spaces](specification-space/)

Turn defensible analytical decisions into an explicit `PipelineSpace`, reject invalid combinations before execution, and summarise endpoint stability without selecting a preferred specification after the fact.

## Reproducibility

### [Publication audits](publication-audits/)

Use a predeclared conclusion rule, deterministic manifests, methods/report generation, and scientific/bundle fingerprints to make robustness evidence auditable.

## Ecosystem integration

### [Interoperability](interoperability/)

Understand the division of responsibility between GazeAudit and Eye-Tracking-BIDS, pymovements, pEYES, and custom study/detector adapters.

## What a guide is not

Guides describe GazeAudit's scientific contracts and recommended use. They do not replace study-specific justification. Researchers remain responsible for deciding which AOIs, error models, detectors, preprocessing choices, QC thresholds, perturbations, and scientific endpoints are defensible for their design.
