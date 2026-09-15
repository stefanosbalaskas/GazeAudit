---
title: Documentation hub
description: Choose the GazeAudit documentation path that matches your research task.
kicker: Documentation
---

# Documentation hub

GazeAudit documentation is organised around **research tasks**, not only modules. Start with the smallest runnable example, build a transparent audit route from study conditions, then move into structural preflight, measurement uncertainty, specification-space design, sensitivity analysis, frozen real-data case studies, and reproducible publication.

<div class="callout info">
<strong>Current release</strong>
The public release is <code>0.1.0</code>. Install it with <code>pip install gazeaudit==0.1.0</code>. The documentation also describes post-release development on <code>main</code>; when reproducibility matters, record the exact version or commit used.
</div>

<div class="callout tip">
<strong>Have your own gaze CSV already?</strong>
Open <a href="guides/first-real-audit/">First real audit with your own data</a> for the practical CSV → <code>GazeStudy</code> → structural preflight → declared robustness → saved evidence route. The companion <a href="examples/first-real-audit/">executable example</a> can be run first on deterministic demo data and then on your canonical table.
</div>

Use **Ctrl/Cmd + K** anywhere on the site to search methods, workflows, examples, evidence pages, and reference material. The search catalog is generated from documentation metadata at build time, so new documented routes do not require a second hand-maintained index.

## Start here

| Goal | Recommended page |
|---|---|
| Apply GazeAudit to my own canonical CSV | [First real audit guide](guides/first-real-audit/) |
| See the whole project-level path from planning to publication | [Researcher workspace](workspace/) |
| Install and run the smallest example | [Getting started](getting-started/) |
| Build and export a transparent audit route from study conditions | [Audit planner](planner/) |
| Map a research question to methods, public functions, examples, plots, and evidence | [Method explorer](methods/) |
| Map a vendor table and inspect structural QC | [Data onboarding and structural preflight](guides/data-onboarding/) |
| Declare participant/trial readiness policies and preview cohort impact | [Analysis-readiness governance](guides/analysis-readiness/) |
| Browse reproducible code-generated figures | [Plot gallery](plots/) |
| Run one complete robustness audit | [End-to-end robustness example](examples/end-to-end-robustness/) |
| Understand uncertainty at AOI boundaries | [AOI uncertainty guide](guides/aoi-uncertainty/) |
| Build a multiverse/specification analysis | [Specification-space guide](guides/specification-space/) |
| Report robustness precisely | [Reporting robustness](guides/reporting-robustness/) |
| Inspect real validation outcomes | [Case studies](case-studies/) |
| Create deterministic publication evidence | [Publication audits](guides/publication-audits/) |
| Connect BIDS, pymovements, pEYES, or custom backends | [Interoperability](guides/interoperability/) |
| Find the right public function | [API map](reference/api-map/) |

## Researcher workspace

The [Researcher workspace](workspace/) is the project-level route when you want to connect several documentation layers without losing their scientific boundaries. It links six stages: scope the audit, inspect the governed method route, run the smallest relevant workflow, inspect visuals in context, check the evidence boundary, and preserve the publication record.

Use it as an orientation layer rather than a new source of scientific rules. The workspace does not choose thresholds, exclusions, perturbation levels, specifications, or validity claims.

## Plan an audit from study conditions

The [Audit planner](planner/) is the shortest route when you know which study conditions or methodological risks are relevant but do not yet know which parts of GazeAudit to combine. Select only the conditions that genuinely apply; the planner deduplicates the corresponding governed method families, explains why each method entered the route, and links directly to its guide, runnable example, diagnostic plot, and evidence boundary.

The planner is deliberately **non-diagnostic**. It does not choose thresholds, infer unselected risks, exclude participants, or decide whether a result is scientifically valid. A shared planner URL records navigation choices, not a scientific conclusion.

When the route is useful, preserve it as a **shareable URL**, a **Markdown audit brief**, or a deterministic **JSON navigation manifest**. The JSON record includes a stable schema version, selected conditions, ordered methods, API sequences, workflow handoffs, the GazeAudit release identity, and the documentation revision; it intentionally does not insert a volatile timestamp.

## Explore methods by research question

The [method explorer](methods/) connects ten methodological questions to a compact public API route, a guide or runnable example, a diagnostic figure, and an explicit evidence boundary. Use it when you know **what decision you need to defend** but do not yet know which GazeAudit functions or workflow page to open.

Its evidence column is deliberately conservative: frozen real-data cases are linked only where they are substantively relevant, while synthetic known-truth benchmarks and live interoperability checks remain labelled as different evidence types.

## Data onboarding

Before applying measurement or robustness methods to a new table, map its semantic columns explicitly with `GazeStudy` and run the structural preflight. The [data onboarding guide](guides/data-onboarding/) explains how `audit_study_qc()` reports non-finite coordinates/timestamps, missing identifiers, duplicate within-trial timestamps, and decreasing time order without turning those diagnostics into universal exclusion rules.

For a single practical path that continues beyond preflight into robustness outputs and saved evidence, use [First real audit with your own data](guides/first-real-audit/).

## Runnable examples

The examples use synthetic data unless a page explicitly points to a frozen real-data validation record. This keeps demonstrations runnable without private participant data while separating demonstration values from empirical claims.

- [First real audit](examples/first-real-audit/) — CSV-oriented project template with structural-QC provenance, complete specification execution, and saved robustness tables.
- `python examples/study_preflight.py` — inspect a deliberately flagged canonical study before downstream analysis.
- [End-to-end robustness audit](examples/end-to-end-robustness/) — canonical study → declared specification space → complete execution → stability and sensitivity diagnostics.
- [AOI boundary uncertainty](examples/aoi-boundary/) — fit a gaze-error model and convert a hard boundary decision into probabilistic membership.
- [Specification curve](examples/specification-curve/) — summarise an explicit analytical decision space.
- [Sampling sensitivity](examples/sampling-sensitivity/) — perturb sampling rate and inspect endpoint stability.

## Research workflows

Use the workflow pages when you are designing a study or analysis rather than learning one function.

- [Workflow map](workflows/) — choose the right workflow family.
- [First-study audit](workflows/first-study-audit/) — canonical data → preflight → optional readiness/measurement layers → robustness → publication provenance.
- [Measurement audit](workflows/measurement-audit/) — validation information → error model → AOI uncertainty → endpoint propagation.
- [Robustness audit](workflows/robustness-audit/) — defensible choices → common endpoint → specification curve → sensitivity diagnostics.
- [Reproducible publication](workflows/reproducible-publication/) — declared rule → audit bundle → fingerprints → methods/report output.

## Real-data case studies

The case-study layer turns the frozen validation records into readable methodological walkthroughs while leaving the underlying scientific records untouched.

<div class="evidence-grid">
  <article class="evidence-card evidence-incomplete">
    <span class="evidence-state">Incomplete</span>
    <h3>GazeBase</h3>
    <p>See why a seven-detector analysis stopped when two frozen specifications failed the completeness gate.</p>
    <p><a href="{{ '/docs/case-studies/gazebase-incomplete/' | relative_url }}">Open case →</a></p>
  </article>
  <article class="evidence-card evidence-robust">
    <span class="evidence-state">Robust negative</span>
    <h3>Korthals</h3>
    <p>Compare hard AOI membership with the uncertainty-propagated target-tracking effect.</p>
    <p><a href="{{ '/docs/case-studies/korthals-target-tracking/' | relative_url }}">Open case →</a></p>
  </article>
  <article class="evidence-card evidence-fragile">
    <span class="evidence-state">Materially fragile</span>
    <h3>Pedrotti/de Chambrier</h3>
    <p>See how sampling resolution and controlled missingness changed magnitude recovery.</p>
    <p><a href="{{ '/docs/case-studies/pedrotti-sensitivity/' | relative_url }}">Open case →</a></p>
  </article>
</div>

## Conceptual articles

The articles explain why the package is structured the way it is and where its scientific boundaries sit.

- [Measurement uncertainty is a modelling problem](articles/measurement-uncertainty-is-a-modeling-problem/)
- [From one pipeline to a robustness audit](articles/from-one-pipeline-to-a-robustness-audit/)
- [How to read a fragile result](articles/how-to-read-a-fragile-result/)

## Reporting layer

After running an audit, use [Reporting robustness without overclaiming](guides/reporting-robustness/) to distinguish descriptive specification quantiles from confidence intervals, sign fractions from probabilities, and sensitivity screening from causal variance decomposition.

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

## Code-generated visual reference

The [plot gallery](plots/) contains 14 deterministic Matplotlib SVGs tied to executable source, including readiness, cohort-impact, repair, specification, sensitivity, AOI, and recovery diagnostics.
