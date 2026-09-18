---
title: Claim-boundary reporting
description: A cross-method guide for translating GazeAudit structural-QC, readiness, robustness, sensitivity, and frozen validation evidence into denominator-aware Methods, Results, and limitations language without inferential upgrades or status misuse.
kicker: Guide · Interpretation & reporting
permalink: /docs/guides/claim-boundary-reporting/
search_category: Guide
search_keywords: claim boundary reporting methods results limitations status denominator runtime interpretation robustness readiness qc sensitivity frozen labels overclaim
---

# Claim-boundary reporting

Use this guide when the analysis outputs already exist and the remaining task is **turning evidence into prose without making the evidence stronger than it is**.

The corresponding [Results Interpretation & Reporting Center]({{ '/docs/reporting-center/' | relative_url }}) provides searchable, copyable contracts. This guide explains the reasoning sequence behind them.

## 1. Identify the evidence object before the adjective

Before writing “clean”, “ready”, “robust”, “sensitive”, “fragile”, or “incomplete”, identify the exact object that supports the statement.

Examples:

- `StudyQCReport.status`;
- `AnalysisReadinessReport.status`;
- trial/participant cohort-impact tables;
- specification-level endpoint estimates;
- `effect_stability()` summaries;
- marginal/pairwise sensitivity diagnostics;
- a declared/valid/successful execution ledger;
- a frozen case-specific validation record.

Do not start from the adjective and search backward for a justification.

## 2. Distinguish three kinds of labels

### Runtime status

A value returned by software under an explicit contract.

Examples:

- `pass`;
- `review`;
- `unassessed`;
- `ready_under_policy`;
- `review_under_policy`.

These values can be reported directly when the corresponding object and denominator are named.

### Interpretation pattern

A researcher description of the complete evidence pattern.

Examples:

- direction stable but magnitude variable;
- estimates cross the scientific null;
- declared execution incomplete;
- one factor aligns most strongly with descriptive specification variation.

These are not package enums.

They require the researcher to inspect the complete declared evidence set.

### Protocol-bound evidence label

A canonical outcome attached to a frozen GazeAudit validation programme.

Examples:

- `incomplete` for the frozen GazeBase protocol;
- `robust_negative` for the frozen Korthals protocol;
- `materially_fragile` for the frozen Pedrotti/de Chambrier protocol.

These labels must not be assigned to unrelated studies or synthetic examples.

## 3. Preserve the denominator before writing the result

A claim without its denominator is often impossible to reconstruct.

### Structural QC

Keep separate:

- total rows;
- affected rows;
- participant × trial groups;
- affected groups.

Do not add row and group counts together.

### Readiness

Keep separate:

- baseline and retained rows;
- baseline and retained trial units;
- baseline and retained participant units;
- trial-scope versus participant-scope consequences.

### Robustness

Keep separate:

- declared combinations;
- predeclared-invalid combinations;
- valid specifications;
- successfully executed valid specifications;
- technical failures;
- not-run branches;
- post-review amendments.

Do not redefine the denominator by deleting inconvenient branches.

## 4. Use a claim ladder

For each result, move through four levels.

### Level 1 — observation

What exactly happened?

> Three of six trial units failed the declared synthetic readiness policy.

### Level 2 — bounded interpretation

What does that observation imply under the declared contract?

> Readiness was review-under-policy at the declared thresholds.

### Level 3 — scientific interpretation

What does it mean for the study's substantive question?

This requires study-specific judgement about endpoint dependence, magnitude, design, and uncertainty.

### Level 4 — generalisation

How far does the conclusion extend beyond the observed data, specification space, measurement model, or frozen protocol?

GazeAudit does not determine this step automatically.

A common reporting error is jumping directly from Level 1 to Level 4.

## 5. Keep Methods and Results roles distinct

### Methods should say

- what was declared;
- what was evaluated;
- what denominator was governed;
- what functions or workflow were used;
- what rule translated evidence into any categorical decision;
- when the decision was fixed.

### Results should say

- what evidence state occurred;
- what counts/fractions/ranges were observed;
- what branches or units were missing or failed;
- what descriptive sensitivity pattern appeared;
- how the result maps to the predeclared rule, if one exists.

Do not hide post-result decisions in Methods wording that makes them look prespecified.

## 6. Add the limitation next to the claim

A limitation should identify **the boundary of the evidence object**, not just a generic caveat.

Examples:

### Structural QC

> Structural preflight did not assess calibration accuracy, event-detection validity, or inferential robustness.

### Readiness

> Readiness was conditional on the declared structural policy and application scope.

### Robustness

> The observed stability applies to the declared decision space and does not cover untested analytical or measurement choices.

### Sensitivity

> Marginal and pairwise diagnostics are descriptive and do not provide causal variance decomposition.

### Frozen validation

> The label applies only to the fixed source/protocol/endpoints in the canonical validation record.

## 7. Do not upgrade descriptive quantities into inference

### Empirical specification quantiles are not confidence intervals

`effect_stability()` quantiles describe the realised specification estimates.

They do not have repeated-sampling coverage merely because they use 2.5% and 97.5% cut points.

### Sign fractions are not posterior probabilities

A 90% positive-specification fraction means 90% of the represented specification estimates were positive.

It does not mean there is a 90% probability that the true effect is positive.

### Sensitivity ratios are not causal variance shares

A large marginal sensitivity value says that estimate variation differs across declared levels.

It does not prove that factor caused that percentage of scientific uncertainty.

### Pairwise sensitivity is not an inferential interaction test

Use it to locate non-additive descriptive specification patterns, not to substitute for a fitted factorial model.

## 8. Report incomplete execution before reporting robustness

If a declared valid branch failed or was not run, say so before summarising the observed estimate spread.

Preferred structure:

> Six of seven valid specifications produced endpoint estimates; one valid branch failed technically. The six available estimates were all positive and ranged from A to B, but the declared audit remained incomplete.

Avoid:

> All analyses were positive.

The second sentence silently changes the denominator from seven valid branches to six successful ones.

## 9. Preserve temporal evidence layers

A post-review sensitivity analysis is not part of the originally submitted evidence merely because it appears in the same final manuscript.

Report separately:

- submitted evidence;
- reviewer-requested amendment;
- correction;
- separate-endpoint amendment;
- superseded evidence.

Do not rewrite post-review analysis as if it had been prespecified.

## 10. Treat “no issue” and “no evidence” differently

Examples:

- structural `pass` means no implemented structural condition was detected;
- readiness `unassessed` means no active rule participated;
- a technical failure means no endpoint estimate was obtained for that valid branch;
- a not-run branch means the endpoint was not attempted;
- a non-finite endpoint is not a zero/null effect.

Absence of a flag, rule, estimate, or execution is not interchangeable.

## 11. Reporting structural-QC evidence

### Methods

> Structural preflight evaluated non-finite coordinates and timestamps, missing canonical identifiers, duplicate participant × trial timestamps, and decreasing within-unit time. Flagged diagnostics were inspected against source and preprocessing provenance before any repair, retention, or exclusion decision.

### Results — pass

> Structural preflight returned `pass`; none of the implemented structural conditions was detected in the canonical representation.

### Results — review

> Structural preflight returned `review` because [issue families] affected [row/group denominator]. The corresponding diagnostics were inspected before the recorded study-specific decisions were applied.

### Boundary

Do not write “the dataset passed validation”.

## 12. Reporting readiness evidence

### Methods

> Analysis readiness was evaluated under the declared [policy] policy. Trial- and participant-level summaries and cohort-impact previews were generated before the [trial/participant] application scope was fixed/applied.

### Results

> Readiness status was [status]. Trial-scope preview retained [rows/trials/participants], while participant-scope preview retained [rows/trials/participants].

### Boundary

Do not write “GazeAudit recommended excluding [x]%”.

Thresholds and scope are researcher-owned.

## 13. Reporting specification robustness

A compact result should normally include:

- valid represented branch count;
- range;
- median;
- empirical specification quantiles;
- positive / negative / exact-null pattern where relevant;
- descriptive factor-level sensitivity;
- execution completeness.

Example:

> Across 12 valid represented specifications, estimates ranged from -0.040 to +0.021. Four estimates were positive, four negative, and four exactly zero. The directional conclusion therefore depended on analytical choices represented in the declared specification space.

The conclusion is about the declared space, not all conceivable analyses.

## 14. Reporting sensitivity

Preferred:

> Descriptive marginal sensitivity was largest for AOI definition, while the strongest pairwise non-additive pattern involved detector × AOI definition.

Avoid:

> AOI definition explained 40% of the uncertainty.

Unless a separate statistical model justifies that interpretation, the GazeAudit descriptive diagnostic does not.

## 15. Reporting frozen validation evidence

Always include:

- case name;
- frozen protocol;
- canonical outcome label;
- scope boundary.

Example:

> Under the frozen Korthals target-tracking AOI protocol, the canonical outcome was `robust_negative`.

Do not write:

> GazeAudit proves negative AOI effects are robust.

## 16. Use bracketed templates as placeholders, not generated truth

The reporting center includes bracketed wording such as:

> [successful] of [valid] specifications produced endpoint estimates.

Replace every bracketed field from the actual evidence record.

If the required value is unavailable, do not delete the placeholder and retain the claim. Resolve the evidence gap or report it as unresolved.

## 17. Final claim-boundary checklist

Before approving manuscript wording:

- [ ] evidence object identified;
- [ ] runtime status distinguished from interpretation pattern;
- [ ] frozen labels kept case-specific;
- [ ] denominator explicitly reconstructable;
- [ ] endpoint unchanged across compared branches;
- [ ] execution failures/not-run branches retained;
- [ ] direction separated from magnitude;
- [ ] descriptive diagnostics not upgraded to inference;
- [ ] post-review evidence timing visible;
- [ ] limitation matches the evidence object;
- [ ] exact software/evidence identity archived;
- [ ] sentence can be traced to a stored artifact or table.

## API and reference routes

- [Structural-QC API pathway]({{ '/docs/reference/api-pathways/#path-structural-qc' | relative_url }})
- [Readiness API pathway]({{ '/docs/reference/api-pathways/#path-readiness-governance' | relative_url }})
- [Specification-robustness API pathway]({{ '/docs/reference/api-pathways/#path-specification-robustness' | relative_url }})
- [`effect_stability()`]({{ '/docs/reference/api-pathways/#api-effect-stability' | relative_url }})
- [`run_specs()`]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [Evidence and denominator vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }})
- [Validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }})
- [Results Interpretation & Reporting Center]({{ '/docs/reporting-center/' | relative_url }})
- [Machine-readable reporting contracts]({{ '/assets/reporting-contract-reference.json' | relative_url }})

## Worked exercise

Continue to [Reporting-language rewrite]({{ '/docs/examples/reporting-language-rewrite/' | relative_url }}) to repair over-strong synthetic manuscript statements across structural QC, readiness, robustness, sensitivity, execution completeness, and frozen evidence.
