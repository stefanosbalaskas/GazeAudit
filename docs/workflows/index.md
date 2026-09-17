---
title: Research workflows
description: End-to-end GazeAudit workflows for applying the package to a study, measurement uncertainty, analytical robustness, peer-review revision, and reproducible publication.
kicker: Workflows
---

# Research workflows

Use these pages when you already understand the basic functions and need to structure a complete analysis or revision record.

<figure class="plot-card">
  <img src="{{ '/assets/images/workflow-overview.svg' | relative_url }}" alt="GazeAudit end-to-end workflow">
  <figcaption>GazeAudit separates measurement uncertainty, analytical decision uncertainty, endpoint definition, robustness diagnostics, review-stage amendments, and publication provenance.</figcaption>
</figure>

## [First-study audit](first-study-audit/)

**Question:** how do I take one real project from canonical data through preflight, declared robustness, evidence review, and publication provenance?

Typical sequence:

1. define the scientific endpoint and study-specific assumptions;
2. map one canonical `GazeStudy`;
3. run structural preflight and record decisions;
4. add readiness or measurement layers only when scientifically relevant;
5. declare and execute the defensible specification space;
6. inspect robustness and targeted sensitivity diagnostics;
7. preserve the complete evidence and software identity.

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

## [Peer-review revision toolkit]({{ '/docs/workspace/revision-toolkit/' | relative_url }})

**Question:** how do I add reviewer-requested work without rewriting what existed at submission?

Typical sequence:

1. classify the reviewer request before changing the record;
2. preserve the submitted evidence and its original denominator;
3. record outcome-inspection timing for post-review analytical decisions;
4. execute reviewer-requested amendments under their own denominators;
5. bind each response item to manuscript and archive locations;
6. record material v1 → v2 changes in a version-change manifest;
7. scaffold and validate the structural revision package;
8. run the final resubmission consistency gate.

The toolkit routes to the amendment guide, response-letter guide, executable `gazeaudit-revision-package` workflow, worked failure/repair example, and final editor-handoff checks.

## [Reproducible publication](reproducible-publication/)

**Question:** can another researcher reconstruct what was declared, executed, revised, and reported?

Typical sequence:

1. freeze software and source identity;
2. freeze the scientific decision rule where appropriate;
3. execute the analysis;
4. build a deterministic audit bundle;
5. preserve scientific and execution fingerprints;
6. preserve review-stage amendments and their temporal provenance;
7. archive report, methods, manifests, complete results, and final evidence maps;
8. cite the exact release or commit.

## Combine workflows deliberately

The first-study workflow is the project-level spine. Measurement, robustness, revision, and publication workflows are governed layers that can be nested where the study requires them.

For example, a `PipelineSpace` may contain hard versus probabilistic AOI branches, while each probabilistic branch is generated under a declared error model. If peer review later requests a stricter threshold, that analysis belongs in a separately timed revision layer rather than being silently inserted into the submitted specification space. The publication workflow can then bind the submitted and post-review records without collapsing them.

The important constraint is **semantic and temporal clarity**: measurement assumptions, analytical choices, perturbation analyses, reviewer-requested extensions, corrections, and publication rules should remain distinguishable in the provenance record.
