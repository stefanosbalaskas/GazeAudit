---
title: First-study audit workflow
description: A study-level GazeAudit workflow from canonical data and structural preflight through declared robustness analysis, evidence review, and publication provenance.
kicker: Workflow · Start here
permalink: /docs/workflows/first-study-audit/
search_category: Workflows
search_keywords: first study workflow own data csv preflight readiness measurement robustness publication provenance
---

# First-study audit workflow

Use this workflow when you are applying GazeAudit to a study for the first time and want a **research-process sequence**, not only isolated function documentation.

It connects the main layers without pretending they are interchangeable:

**scope → canonical data → structural preflight → researcher decisions → optional readiness/measurement layers → declared robustness → evidence review → publication record**.

<div class="callout info">
<strong>The workflow governs traceability, not scientific judgement.</strong>
GazeAudit can preserve what you declared and what happened under those declarations. It does not decide which thresholds, AOIs, exclusions, perturbations, or conclusion rules are justified for your study.
</div>

## Stage 0 — define the scientific question before opening the result tables

Write down:

- the scientific endpoint;
- the analysis unit;
- the conditions or contrasts required by that endpoint;
- plausible measurement uncertainties;
- defensible preprocessing/QC alternatives;
- the evidence that would count as stable, fragile, or unresolved for the specific study.

If you are unsure which GazeAudit families apply, use the [Audit planner]({{ '/docs/planner/' | relative_url }}) and save its Markdown brief or JSON navigation manifest as a project handoff.

## Stage 1 — create one canonical study representation

Map the table explicitly with `GazeStudy`. Preserve raw/source data separately; the canonical table is the representation you are choosing to audit.

For a copy-ready path, start with the [first real audit guide]({{ '/docs/guides/first-real-audit/' | relative_url }}) and [first real audit example]({{ '/docs/examples/first-real-audit/' | relative_url }}).

**Gate:** you can explain what each mapped coordinate, timestamp, participant, and trial column means, including units and coordinate system.

## Stage 2 — run structural preflight

Build a `StudyQCAudit` before substantive modelling.

Inspect:

- non-finite coordinates or timestamps;
- missing participant/trial identifiers;
- duplicate participant × trial timestamps;
- decreasing finite time order;
- deterministic study and audit fingerprints.

**Gate:** every structural flag has either been corrected with provenance or retained with a documented rationale. A flag is not an automatic exclusion rule.

## Stage 3 — decide whether readiness governance is needed

If participant/trial retention is itself an analytical policy, move into [analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}).

Use this layer when you need to compare declared threshold policies or preview cohort consequences. Do not use it to manufacture a universal “good/bad participant” score.

**Gate:** retention rules are declared before inspecting preferred scientific results, and their cohort impact is preserved.

## Stage 4 — decide whether a measurement audit is needed

If AOI membership or another endpoint could change under plausible gaze-position error, use the [measurement audit]({{ '/docs/workflows/measurement-audit/' | relative_url }}).

This layer is distinct from general robustness. It asks what happens when the measurement itself is uncertain, not merely when analysts choose different preprocessing branches.

**Gate:** the error model and AOI geometry have study-specific justification.

## Stage 5 — declare the analytical decision space

Build a finite `PipelineSpace` containing only defensible alternatives.

Typical factors can include:

- QC policy;
- detector or preprocessing family;
- missing-data handling;
- sample-retention or downsampling rule;
- AOI definition or uncertainty branch;
- model specification where a common scalar endpoint can still be compared meaningfully.

Do not add levels because they move the estimate toward a preferred direction.

**Gate:** every specification answers the same scientific question and invalid combinations are removed for scientific reasons before result interpretation.

## Stage 6 — execute the full space and inspect robustness

Run `run_specs()` and preserve every evaluated row.

Then inspect:

1. `specification_curve()`;
2. `effect_stability()`;
3. `marginal_sensitivity()`;
4. `pairwise_interaction_sensitivity()` where appropriate;
5. targeted sampling, missingness, or spatial-error sensitivity when those perturbations are scientifically relevant.

Use the [plot gallery]({{ '/docs/plots/' | relative_url }}) to identify the corresponding governed diagnostics.

**Gate:** reporting distinguishes empirical specification summaries from sampling uncertainty, posterior uncertainty, or causal decomposition.

## Stage 7 — check the evidence boundary before interpreting the result

The frozen GazeAudit case studies illustrate three different protocol-bound outcomes:

- GazeBase: `incomplete`;
- Korthals: `robust_negative`;
- Pedrotti/de Chambrier: `materially_fragile`.

These labels are not templates to transfer automatically to a new study. Use the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) and relevant case page only to understand how evidence boundaries are recorded.

**Gate:** your study's interpretation is derived from its own declared protocol and outputs, not borrowed from a package case label.

## Stage 8 — preserve publication provenance

Before manuscript writing or archive deposit, preserve:

- exact GazeAudit version/commit;
- canonical data mapping;
- structural-QC audit and decisions;
- readiness policy where used;
- measurement model where used;
- complete specification table;
- robustness/sensitivity summaries;
- figures and generated tables;
- scientific and execution fingerprints where supported;
- the reporting rule used to interpret stability or fragility.

Continue with the [reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) and [publication-audit guide]({{ '/docs/guides/publication-audits/' | relative_url }}).

## Minimal project directory

A transparent project can be as simple as:

```text
project/
├── data/
│   ├── raw/                  # immutable source exports
│   └── canonical/            # explicit GazeStudy input table
├── analysis/
│   └── run_audit.py          # adapted from first_real_audit.py
├── audit-output/
│   ├── study-qc/
│   ├── specifications.csv
│   ├── specification-curve.csv
│   ├── effect-stability.csv
│   ├── marginal-sensitivity.csv
│   └── pairwise-sensitivity.csv
└── README.md                 # study-specific decisions and exact software identity
```

The package does not require this directory layout; it is a practical separation of source data, executable analysis, and generated evidence.

## Fast handoff

- **Need code now:** [First real audit example →]({{ '/docs/examples/first-real-audit/' | relative_url }})
- **Need explanation:** [First real audit guide →]({{ '/docs/guides/first-real-audit/' | relative_url }})
- **Need to choose methods:** [Method explorer →]({{ '/docs/methods/' | relative_url }})
- **Need the broader project map:** [Researcher workspace →]({{ '/docs/workspace/' | relative_url }})
