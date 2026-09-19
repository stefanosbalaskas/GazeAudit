---
title: Interpret an audit result
description: A decision-oriented guide for moving from completed GazeAudit outputs to bounded scientific interpretation by checking execution completeness, direction stability, magnitude stability, sensitivity, and unresolved uncertainty.
kicker: Guide · Interpretation
permalink: /docs/guides/interpret-audit-result/
search_category: Guide
search_keywords: interpret audit result robustness direction sign magnitude stability incomplete execution failed branches reporting next step decision guide
---

# Interpret an audit result

A completed robustness run does not automatically imply a completed scientific interpretation. Before writing a conclusion, separate five questions that are often collapsed into one:

1. **Was the declared analysis space actually represented?**
2. **Does the direction of the endpoint change across valid executed specifications?**
3. **Does the magnitude change enough to matter scientifically even when the sign does not?**
4. **Which declared factors align with the observed variation, descriptively?**
5. **What uncertainty remains outside the executed audit?**

This guide provides a practical route through those questions. It does **not** assign a universal robustness label, decide whether an effect is scientifically important, or transfer a frozen GazeAudit case-study classification to a new dataset.

<div class="callout warning">
<strong>Interpretation starts with completeness, not with the most attractive estimate.</strong>
If declared branches are missing, technically failed, invalidated after result inspection, or silently absent from the denominator, resolve and document that status before summarising direction or magnitude.
</div>

## Step 1 · Verify the execution denominator

Start from the **declared** specification space, not from the rows that happened to return estimates.

For every declared branch, preserve one accountable status such as:

| Status | Meaning | Interpretation consequence |
|---|---|---|
| `executed` | Valid declared branch completed | Include it in the declared summary denominator. |
| `invalid_predeclared` | Excluded by a rule fixed before execution | Preserve the rule and branch identity; do not treat it as a technical failure. |
| `technical_failure` | A valid branch failed computationally | Report the failure; do not silently remove it. |
| `data_unavailable` | Required source content was absent | Preserve the missing-source reason. |
| `not_run` | A declared branch was never executed | Interpretation remains incomplete until this is explained. |

The vocabulary can differ by project. The important property is **accountability**: a declared branch should not disappear because it complicates the result.

### Stop here when

- the declared denominator cannot be reconstructed;
- failure status is missing;
- an exclusion rule was created after outcome inspection but recorded as if it were predeclared;
- different branches estimate different scientific endpoints.

Use [common audit mistakes and repairs]({{ '/docs/guides/common-audit-mistakes/' | relative_url }}) before continuing.

## Step 2 · Separate direction from magnitude

A sign summary and a magnitude summary answer different questions.

### Direction

Ask whether valid executed estimates remain on one side of the scientific null, cross it, or include exact/near-zero values. A stable sign can be descriptively important, but it is **not** by itself proof that the result is scientifically robust.

### Magnitude

Ask whether the spread in estimates changes the substantive interpretation. A result can keep the same sign while moving from practically negligible to consequential, or from a small effect to a much larger one.

For that reason, avoid reducing the result to a single percentage such as “90% of specifications were positive.” Preserve the estimate distribution, ordering, branch metadata, and scientific scale.

## Step 3 · Describe the pattern before explaining it

A useful description normally reports:

- number of declared specifications;
- number and status of represented branches;
- estimate range;
- median or another clearly justified descriptive centre;
- positive / negative / zero counts when direction is relevant;
- whether scientifically meaningful thresholds are crossed, if those thresholds were justified independently of the observed result.

Only after describing the complete pattern should you inspect factor-level diagnostics.

<div class="callout info">
<strong>Descriptive sensitivity is not causal attribution.</strong>
If one analytical factor aligns with larger estimate shifts in marginal or pairwise summaries, report that association as a property of the declared specification set. The audit does not by itself establish that the factor caused the change.
</div>

## Step 4 · Use a four-path interpretation map

The map below is deliberately **descriptive rather than classificatory**. It helps choose the next analysis or reporting action without inventing a package-level verdict.

| Observed audit pattern | What the evidence supports | What to do next |
|---|---|---|
| Complete execution; direction and magnitude both relatively stable across the declared space | The conclusion varies little within the executed specification set | Report the full range and denominator; still state what was not varied. |
| Complete execution; direction stable but magnitude materially variable | Direction is less sensitive than effect size | Report the sign stability and the magnitude sensitivity separately; identify which declared factors align with the spread. |
| Complete execution; direction changes across defensible specifications | The directional conclusion is specification-sensitive | Avoid a single-direction headline; localise the sensitivity and narrow the claim. |
| Execution incomplete or denominator uncertain | The robustness pattern cannot yet be interpreted as a complete declared-space result | Resolve failures/missing branches or explicitly report the incompleteness before stronger interpretation. |

These paths are not named outcome classes and should not be used to relabel the frozen GazeAudit case studies.

Before factor-level interpretation, use the [Robustness Diagnostics & Sensitivity Center]({{ '/docs/diagnostics/' | relative_url }}) to verify the exact summary contract, empirical-quantile boundary, and controlled-perturbation distinction.

## Step 5 · Inspect marginal and pairwise sensitivity conservatively

Use marginal summaries to ask whether estimate distributions differ across levels of one declared analytical factor. Use pairwise summaries to inspect whether combinations of factors align with additional variation.

Do **not** convert these summaries into:

- causal effects of preprocessing choices;
- posterior probabilities that one pipeline is correct;
- evidence that the largest estimate is the best estimate;
- permission to prune specifications after inspecting outcomes.

If a factor appears important, the appropriate follow-up may be scientific justification, additional measurement validation, a targeted sensitivity analysis, or narrower reporting—not retrospective optimisation.

## Step 6 · Check what the audit did not vary

A complete executed specification space can still leave important uncertainty untouched. Record dimensions that were fixed or absent, such as:

- AOI geometry;
- detector choice;
- sampling rate;
- missingness handling;
- participant inclusion policy;
- trial aggregation;
- endpoint construction;
- uncertainty model;
- external source version.

A robustness claim should be scoped to the dimensions actually examined.

## Step 7 · Choose bounded reporting language

Prefer language that states the empirical pattern and its scope.

### Direction and magnitude both stable

> Across the declared and successfully executed specifications, estimates remained similar in direction and magnitude. The observed range therefore showed limited sensitivity to the analytical choices represented in this audit. This statement is restricted to the declared specification space and does not address untested measurement or preprocessing choices.

### Direction stable, magnitude variable

> Estimates retained the same direction across the declared specifications, but their magnitude varied materially. The audit therefore supports a more stable directional than quantitative conclusion within the executed specification space.

### Direction changes

> The sign of the estimate changed across defensible specifications. The directional conclusion is therefore sensitive to analytical choices represented in the declared space, and a single-direction summary would obscure that variation.

### Incomplete execution

> The declared specification space was not fully represented because one or more valid branches were not successfully executed. The available estimates are reported descriptively, but the robustness audit is incomplete with respect to the original declaration.

Adapt wording to the study and preserve the branch-level evidence that supports it.

## Step 8 · Preserve the reasoning trail

Before publication, archive:

- the original decision log;
- any dated amendments;
- the declared specification space;
- execution status for every branch;
- complete estimates and metadata;
- robustness and sensitivity summaries;
- the exact software identity;
- limitations and untested uncertainty dimensions;
- the wording rule used to translate the pattern into manuscript claims.

Then continue with the [reporting robustness guide]({{ '/docs/guides/reporting-robustness/' | relative_url }}) and [publication/archive handoff example]({{ '/docs/examples/publication-archive-handoff/' | relative_url }}).

## Worked comparison

For four synthetic patterns that make the differences between complete/stable, magnitude-sensitive, sign-sensitive, and incomplete evidence concrete, use the [result-pattern reporting example]({{ '/docs/examples/result-patterns/' | relative_url }}).

## Interpretation boundary

GazeAudit exposes evidence about the consequences of declared analytical and measurement choices. The researcher remains responsible for deciding which choices are scientifically defensible, what magnitude is substantively meaningful, whether additional uncertainty must be tested, and how strongly the result can be generalised.