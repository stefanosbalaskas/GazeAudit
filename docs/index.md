---
title: Documentation hub
description: Choose the GazeAudit documentation path that matches your research task.
kicker: Documentation
---

# Documentation hub

GazeAudit documentation is organised around **research tasks**, not only modules. Start with the smallest runnable example, then move into measurement uncertainty, specification-space design, sensitivity analysis, and reproducible publication.

<div class="callout info">
<strong>Current release</strong>
The public release is <code>0.1.0</code>. Install it with <code>pip install gazeaudit==0.1.0</code>. The documentation also describes post-release development on <code>main</code>; when reproducibility matters, record the exact version or commit used.
</div>

## Start here

| Goal | Recommended page |
|---|---|
| Install and run the smallest example | [Getting started](getting-started/) |
| Understand uncertainty at AOI boundaries | [AOI uncertainty guide](guides/aoi-uncertainty/) |
| Build a multiverse/specification analysis | [Specification-space guide](guides/specification-space/) |
| Create deterministic publication evidence | [Publication audits](guides/publication-audits/) |
| Connect BIDS, pymovements, pEYES, or custom backends | [Interoperability](guides/interoperability/) |
| Find the right public function | [API map](reference/api-map/) |

## Runnable examples

The examples use synthetic data unless a page explicitly points to a frozen real-data validation record. This keeps the examples runnable without private participant data while separating demonstration values from empirical claims.

- [AOI boundary uncertainty](examples/aoi-boundary/) — fit a gaze-error model and convert a hard boundary decision into probabilistic membership.
- [Specification curve](examples/specification-curve/) — summarise an explicit analytical decision space.
- [Sampling sensitivity](examples/sampling-sensitivity/) — perturb sampling rate and inspect endpoint stability.

## Research workflows

Use the workflow pages when you are designing a study or analysis rather than learning one function.

- [Workflow map](workflows/) — choose the right workflow family.
- [Measurement audit](workflows/measurement-audit/) — validation information → error model → AOI uncertainty → endpoint propagation.
- [Robustness audit](workflows/robustness-audit/) — defensible choices → common endpoint → specification curve → sensitivity diagnostics.
- [Reproducible publication](workflows/reproducible-publication/) — declared rule → audit bundle → fingerprints → methods/report output.

## Conceptual articles

The articles explain why the package is structured the way it is and where its scientific boundaries sit.

- [Measurement uncertainty is a modelling problem](articles/measurement-uncertainty-is-a-modeling-problem/)
- [From one pipeline to a robustness audit](articles/from-one-pipeline-to-a-robustness-audit/)
- [How to read a fragile result](articles/how-to-read-a-fragile-result/)

## Frozen validation evidence

GazeAudit's validation programme deliberately preserves different scientific outcomes. The authoritative index is the [validation matrix](VALIDATION_MATRIX.html).

| Case | Canonical outcome | What the outcome means |
|---|---|---|
| GazeBase multi-detector audit | `incomplete` | The predeclared completeness gate was not satisfied. |
| Korthals target-tracking AOI | `robust_negative` | The negative paired AOI effect survived the frozen uncertainty model. |
| Pedrotti/de Chambrier sampling + missingness | `materially_fragile` | The endpoint changed materially under the frozen perturbation protocol. |

These labels are **protocol-bound records**, not universal properties of the source datasets.

## Scientific and release reference

For deeper provenance or publication operations, use the existing authoritative records:

- [Scientific methods](SCIENTIFIC_METHODS.html)
- [Validation matrix](VALIDATION_MATRIX.html)
- [Citation and reuse](CITATION_AND_REUSE.html)
- [Release notes 0.1.0](RELEASE_NOTES_0.1.0.html)
- [External publication record](EXTERNAL_PUBLICATION_0.1.0.html)

## Need a quick answer?

Open the [FAQ](faq/) for installation, interpretation, versioning, and scope questions.
