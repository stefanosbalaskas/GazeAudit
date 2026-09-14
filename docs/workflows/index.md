---
title: Research workflows
description: End-to-end GazeAudit workflows for measurement uncertainty, analytical robustness, and reproducible publication.
kicker: Workflows
---

# Research workflows

Use these pages when you already understand the basic functions and need to structure a complete analysis.

<figure class="plot-card">
  <img src="{{ '/assets/images/workflow-overview.svg' | relative_url }}" alt="GazeAudit end-to-end workflow">
  <figcaption>GazeAudit separates measurement uncertainty, analytical decision uncertainty, endpoint definition, robustness diagnostics, and publication provenance.</figcaption>
</figure>

## [Measurement audit](measurement-audit/)

**Question:** could plausible gaze-position error change AOI membership or the scientific endpoint?

Typical sequence:

1. preserve validation information;
2. fit global or grouped error models;
3. propagate uncertainty into AOI membership;
4. compare hard and probabilistic assignment;
5. calculate uncertainty-weighted endpoints;
6. stress-test the error model.

## [Robustness audit](robustness-audit/)

**Question:** does the scientific endpoint remain stable across defensible analytical decisions?

Typical sequence:

1. define the common endpoint;
2. declare a `PipelineSpace`;
3. remove scientifically invalid combinations before execution;
4. execute all remaining specifications;
5. inspect specification curve and sign/magnitude stability;
6. screen marginal and pairwise sensitivity;
7. interpret instability without post-hoc optimisation.

## [Reproducible publication](reproducible-publication/)

**Question:** can another researcher reconstruct what was declared, executed, and reported?

Typical sequence:

1. freeze software and source identity;
2. freeze the scientific decision rule where appropriate;
3. execute the analysis;
4. build a deterministic audit bundle;
5. preserve scientific and execution fingerprints;
6. archive report, methods, manifests, and complete results;
7. cite the exact release or commit.

## Combine workflows deliberately

The three workflows can be nested. For example, a `PipelineSpace` may contain hard versus probabilistic AOI branches, while each probabilistic branch is generated under a declared error model. The publication workflow can then bind the complete decision space and outputs.

The important constraint is **semantic clarity**: measurement assumptions, analytical choices, perturbation analyses, and publication rules should remain distinguishable in the provenance record.
