---
title: Researcher workspace
description: Move from study conditions to governed methods, runnable workflows, evidence boundaries, and a publication-ready audit record.
kicker: Researcher workspace
page_type: workspace
permalink: /docs/workspace/
search_category: Start
search_keywords: workspace project plan audit planner methods examples workflows evidence publication markdown json own data csv first audit
---

# Researcher workspace

Use this page as the **project-level map** for GazeAudit. It connects the planner, method catalog, runnable documentation, visual diagnostics, empirical evidence, and publication tooling without turning any of them into an automatic scientific decision system.

<div class="callout info">
<strong>Keep navigation and judgement separate.</strong>
GazeAudit can help you make a decision trail explicit. It does not decide which thresholds, exclusions, perturbation levels, specifications, or validity claims are scientifically justified for your study.
</div>

<div class="callout tip">
<strong>Already have a gaze file?</strong>
Use the <a href="{{ '/docs/guides/first-real-audit/' | relative_url }}">first real audit guide</a> for the practical CSV → preflight → robustness → saved evidence path, or run the <a href="{{ '/docs/examples/first-real-audit/' | relative_url }}">companion executable example</a> first.
</div>

## 1. Scope the audit

Start with the [Audit planner]({{ '/docs/planner/' | relative_url }}) when you know the study conditions that matter but have not yet assembled a method route. Select only conditions that genuinely apply. The planner deduplicates the corresponding governed method families and explains why each one entered the route.

When the route is useful, preserve it in one of three forms:

- **shareable URL** — retains the selected planner conditions;
- **Markdown audit brief** — a human-readable handoff for collaborators, protocols, or manuscript notes;
- **JSON navigation manifest** — a deterministic machine-readable record with `schema_version`, selected conditions, ordered methods, API sequences, workflow handoffs, release identity, and documentation revision.

The export contains **no inferred diagnosis and no timestamp-derived nondeterminism**. Researcher-owned thresholds, exclusions, assumptions, and validity judgements remain outside the navigation artifact.

## 2. Inspect the governed method route

Use the [Method explorer]({{ '/docs/methods/' | relative_url }}) when the methodological question is clear. Each of the ten method families connects the research question to:

- a compact public API sequence;
- a task-oriented guide;
- a runnable example or workflow;
- a governed diagnostic plot;
- an explicit evidence boundary.

This is the best place to check whether a frozen real-data case is genuinely relevant or whether the available evidence is instead synthetic, interoperability-focused, or descriptive.

## 3. Run the smallest relevant workflow

Prefer the smallest executable path that answers the methodological question before combining multiple audit layers.

| Need | Start here | Continue with |
|---|---|---|
| Apply GazeAudit to your own canonical CSV | [First real audit]({{ '/docs/examples/first-real-audit/' | relative_url }}) | [First-study workflow]({{ '/docs/workflows/first-study-audit/' | relative_url }}) |
| Structural preflight | [Study preflight]({{ '/docs/examples/study-preflight/' | relative_url }}) | [Data onboarding]({{ '/docs/guides/data-onboarding/' | relative_url }}) |
| Readiness governance | [Analysis-readiness example]({{ '/docs/examples/analysis-readiness/' | relative_url }}) | [Readiness guide]({{ '/docs/guides/analysis-readiness/' | relative_url }}) |
| AOI measurement uncertainty | [AOI boundary example]({{ '/docs/examples/aoi-boundary/' | relative_url }}) | [Measurement audit]({{ '/docs/workflows/measurement-audit/' | relative_url }}) |
| Alternative analytical choices | [End-to-end robustness audit]({{ '/docs/examples/end-to-end-robustness/' | relative_url }}) | [Robustness workflow]({{ '/docs/workflows/robustness-audit/' | relative_url }}) |
| Sampling sensitivity | [Sampling example]({{ '/docs/examples/sampling-sensitivity/' | relative_url }}) | [Specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }}) |
| Publication evidence | [Publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) | [Publication-audit guide]({{ '/docs/guides/publication-audits/' | relative_url }}) |

## 4. Inspect visuals in context

The [Plot gallery]({{ '/docs/plots/' | relative_url }}) contains fourteen deterministic code-generated figures. Plot cards now link back to the method families they support, so a figure can be read in methodological context instead of as an isolated visual.

Synthetic gallery figures demonstrate APIs and reporting patterns. They are **not additional validation evidence**. Use the case-study layer for empirical validation records.

## 5. Check the evidence boundary

The [Case studies]({{ '/docs/case-studies/' | relative_url }}) expose three deliberately different frozen outcomes:

| Case | Frozen outcome | Boundary |
|---|---|---|
| GazeBase multi-detector audit | `incomplete` | A predeclared completeness gate was not satisfied. |
| Korthals target-tracking AOI | `robust_negative` | The negative paired effect survived the frozen uncertainty model. |
| Pedrotti/de Chambrier sampling + missingness | `materially_fragile` | Magnitude recovery changed materially under the frozen perturbation protocol. |

These are protocol-bound records. Do not transfer a case-study label to a new dataset simply because the same method family is used.

## 6. Preserve the publication record

Before writing the final methods or results text, record:

1. the GazeAudit release or exact commit;
2. the planner route or rationale for the selected method families;
3. researcher-declared thresholds, perturbation levels, and specifications;
4. generated outputs and fingerprints;
5. the interpretation boundary used in reporting.

Then use the [reproducible-publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) and [reporting guide]({{ '/docs/guides/reporting-robustness/' | relative_url }}) to keep robustness summaries distinct from confidence intervals, causal claims, or automated validity decisions.

## Fast routes

- **I already have a gaze CSV:** [first real audit →]({{ '/docs/guides/first-real-audit/' | relative_url }})
- **I have new gaze data:** [data onboarding →]({{ '/docs/guides/data-onboarding/' | relative_url }})
- **I know the study risks:** [audit planner →]({{ '/docs/planner/' | relative_url }})
- **I know the methodological question:** [method explorer →]({{ '/docs/methods/' | relative_url }})
- **I want runnable code:** [examples →]({{ '/docs/examples/' | relative_url }})
- **I want end-to-end analysis design:** [workflows →]({{ '/docs/workflows/' | relative_url }})
- **I need evidence provenance:** [validation matrix →]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }})
- **I am preparing a manuscript/archive:** [publication audits →]({{ '/docs/guides/publication-audits/' | relative_url }})
