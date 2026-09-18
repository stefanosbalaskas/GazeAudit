---
title: Reporting-language rewrite
description: A fully synthetic worked exercise that rewrites over-strong GazeAudit manuscript claims into evidence-bounded Methods, Results, and limitation language while preserving runtime status, denominator, execution completeness, and protocol scope.
kicker: Example · Interpretation & reporting
page_type: example
permalink: /docs/examples/reporting-language-rewrite/
search_category: Example
search_keywords: reporting rewrite overclaim methods results limitations qc readiness robustness sensitivity incomplete execution frozen validation synthetic
example_data: "Synthetic"
example_focus: "Interpretation & reporting"
example_reuse: "Evidence object → denominator → claim boundary → bounded rewrite pattern"
example_output: "Seven repaired manuscript claims with explicit evidence and limitation boundaries"
example_boundary: "The sentences are synthetic teaching material; they are not manuscript claims about any real study."
---

# Reporting-language rewrite

This exercise starts with seven **synthetic over-claims** and repairs each one by identifying:

1. the actual evidence object;
2. the denominator that must remain visible;
3. what the evidence can support;
4. what it cannot support;
5. a bounded rewrite;
6. the limitation that belongs next to the claim.

<div class="callout warning">
<strong>Teaching language only.</strong>
The values and scenarios below are synthetic. Use the rewrite structure, not the numerical content or scientific conclusion.
</div>

## Rewrite 1 · Structural `review` is not “bad data”

### Evidence

Assume structural preflight reports:

```text
status = review
issue_codes = ("coordinate_nonfinite", "timestamp_duplicate")
coordinate_issue_rows = 4
duplicate_timestamp_rows = 6
```

### Too strong

> GazeAudit identified 10 bad observations that were removed.

### Why it fails

- `review` is an inspection state, not an invalid-data classification.
- coordinate and duplicate counts can overlap;
- the denominator is not stated;
- removal is a researcher decision, not a package action;
- duplicate timestamps can be a valid representation feature.

### Bounded rewrite

> Structural preflight returned `review` because non-finite coordinates and duplicate participant × trial timestamps were observed. The corresponding row-level diagnostics were inspected against source and preprocessing provenance before any study-specific retention, repair, or exclusion decision.

### Limitation

> Structural review identifies representation-level conditions and does not establish their cause or scientific invalidity.

---

## Rewrite 2 · `ready_under_policy` is not universal quality

### Evidence

Assume:

```text
policy_name = preregistered_primary
status = ready_under_policy
trial-scope retained = 96 / 100 trials
participant-scope retained = 48 / 50 participants
```

### Too strong

> The dataset passed GazeAudit quality control and was validated for analysis.

### Why it fails

`ready_under_policy` means the observed units satisfy **the declared active structural policy**.

It does not test:

- calibration quality;
- event detection;
- AOI validity;
- missingness assumptions;
- endpoint validity;
- inferential model assumptions.

### Bounded rewrite

> Under the preregistered primary structural-readiness policy, the study returned `ready_under_policy`. Trial-scope preview retained 96/100 trial units, while participant-scope preview retained 48/50 participants. The primary application scope was fixed separately in the analysis protocol.

### Limitation

> Readiness status is policy-relative and does not establish broader measurement or inferential validity.

---

## Rewrite 3 · `unassessed` is not “all included”

### Evidence

Assume:

```python
policy = ReadinessThresholds()
readiness.status == "unassessed"
```

### Too strong

> All participants met the readiness criteria.

### Why it fails

There were no active criteria.

No readiness decision was made.

### Bounded rewrite

> The readiness report returned `unassessed` because the declared policy contained no active structural-readiness criteria.

### Limitation

> This state provides no evidence that participants would satisfy a different declared readiness policy.

---

## Rewrite 4 · Stable direction can coexist with unstable magnitude

### Evidence

Synthetic eight-branch estimates:

```text
+0.006, +0.011, +0.019, +0.028,
+0.041, +0.057, +0.073, +0.091
```

All estimates are positive, but the magnitude varies substantially.

### Too strong

> The effect was robust across all analytical choices.

### Why it fails

The sign is stable, but the magnitude changes by more than an order of magnitude.

A single “robust” adjective hides that distinction.

### Bounded rewrite

> All eight declared synthetic specifications produced positive estimates, but magnitude ranged from +0.006 to +0.091. Direction was therefore less sensitive than quantitative magnitude within the declared specification space.

### Limitation

> Whether that magnitude spread is scientifically material requires an independently justified substantive scale and does not follow from sign stability alone.

---

## Rewrite 5 · Six successful branches do not become a six-branch denominator

### Evidence

```text
8 declared
7 valid
6 successful
1 valid technical failure
1 invalid before execution
```

The six successful estimates are positive and tightly grouped.

### Too strong

> All valid analyses produced consistent positive effects.

### Why it fails

One valid branch did not produce an estimate.

The correct execution denominator is **6 successful / 7 valid**, not 6/6.

### Bounded rewrite

> Six of seven valid specifications produced endpoint estimates and all six available estimates were positive; one valid branch failed technically. The available estimates were directionally consistent, but the declared valid audit remained incomplete.

### Limitation

> The unobserved branch estimate is unknown and cannot be treated as positive, null, or irrelevant.

---

## Rewrite 6 · Sensitivity is descriptive, not causal attribution

### Evidence

Assume `marginal_sensitivity()` returns its largest ratio for AOI definition and the largest pairwise non-additive pattern for detector × AOI definition.

### Too strong

> AOI definition caused most of the uncertainty, and detector choice interacted significantly with AOI definition.

### Why it fails

The GazeAudit diagnostics are descriptive properties of the realised specification set.

They are not:

- causal variance decompositions;
- shares that must sum to one;
- inferential interaction tests;
- p-values or significance tests.

### Bounded rewrite

> Descriptive marginal sensitivity was greatest across AOI-definition levels, while the strongest pairwise non-additive specification pattern involved detector × AOI definition.

### Limitation

> These diagnostics localise variation within the declared specification set and do not establish causal attribution or inferential interaction effects.

---

## Rewrite 7 · Frozen validation labels do not transfer

### Evidence

The frozen Korthals protocol has canonical outcome:

```text
robust_negative
```

### Too strong

> Negative AOI effects are robust in GazeAudit, so our negative effect can be classified as robust_negative.

### Why it fails

`robust_negative` is a **protocol-bound label** for one frozen validation record.

It is not a reusable result category.

### Bounded rewrite

> Under the frozen Korthals target-tracking AOI protocol, the canonical validation outcome was `robust_negative`. That record provides protocol-specific validation context and is not used as a classification rule for the present study.

### Limitation

> A new study requires its own declared endpoint, uncertainty model, decision space, and conclusion rule.

---

## Compare the seven repairs

| Problem | Evidence mistake | Repair principle |
|---|---|---|
| structural review → “bad data” | runtime status converted into invalidity | report issue family + inspection + decision provenance |
| ready-under-policy → “validated” | policy-relative status universalised | name policy, scope, denominator, boundary |
| unassessed → “all passed” | absence of active rules treated as success | state that readiness was not assessed |
| sign stable → “robust” | direction and magnitude collapsed | report sign and magnitude separately |
| 6/7 valid → “all valid” | successful denominator substituted for valid denominator | preserve technical failure |
| sensitivity → causal claim | descriptive diagnostic upgraded to inference | use “descriptive alignment/pattern” |
| frozen label → new study | case-specific evidence universalised | keep case/protocol identity attached |

## A reusable rewrite sequence

When a sentence feels too strong:

### Step 1 · Find the noun

What evidence object supports it?

Examples:

- structural report;
- readiness report;
- branch ledger;
- stability summary;
- sensitivity table;
- validation case.

### Step 2 · Find the denominator

Write the numerator and denominator explicitly before writing the adjective.

### Step 3 · Find the strongest literal statement

What can be said without interpretation?

Example:

> Six of seven valid branches produced estimates.

### Step 4 · Add bounded interpretation

Example:

> All six available estimates were positive.

### Step 5 · Add the missing-evidence boundary

Example:

> The audit remained incomplete because one valid branch failed technically.

### Step 6 · Generalise only as far as the study supports

Do not extend beyond:

- the declared policy;
- the declared specification space;
- the tested measurement model;
- the observed cohort;
- the fixed validation protocol.

## Methods rewrite pattern

### Weak

> We applied strict QC and robustness testing.

### Better

> Structural preflight was inspected before a researcher-declared readiness policy was evaluated. The policy's trial- and participant-level cohort consequences were previewed before the application scope was fixed. Analytical robustness was then evaluated across the declared valid specification space using one common scientific endpoint, with failed or unexecuted valid branches retained in the execution record.

This still needs the study's actual criteria, thresholds, specification factors, endpoint, timing, and software identity.

## Results rewrite pattern

### Weak

> The results were robust and insensitive to analysis choices.

### Better

> Across [successful] of [valid] valid represented specifications, estimates ranged from [min] to [max], with [positive/negative/exact-null pattern]. [Magnitude/direction] was [relatively stable/sensitive] within the declared specification space. [Failure/not-run accounting] remained visible in the execution denominator.

## Limitation rewrite pattern

### Weak

> Some limitations remain.

### Better

> The robustness audit covers only the declared analytical and measurement dimensions. It does not quantify uncertainty from [untested dimensions], and its across-specification summaries are descriptive rather than sampling-theory or posterior uncertainty intervals.

## Use the reporting center

Open the [Results Interpretation & Reporting Center]({{ '/docs/reporting-center/' | relative_url }}) and filter by:

- Structural QC;
- Readiness;
- Robustness;
- Sensitivity;
- Frozen evidence.

Each card preserves the same rewrite structure used in this exercise.

## API and reference routes

- [Evidence and denominator vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }})
- [`audit_study_qc()` pathway]({{ '/docs/reference/api-pathways/#api-audit-study-qc' | relative_url }})
- [`evaluate_analysis_readiness()` pathway]({{ '/docs/reference/api-pathways/#api-evaluate-analysis-readiness' | relative_url }})
- [`run_specs()` pathway]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [`effect_stability()` pathway]({{ '/docs/reference/api-pathways/#api-effect-stability' | relative_url }})
- [Reporting robustness]({{ '/docs/guides/reporting-robustness/' | relative_url }})
- [Claim-boundary reporting]({{ '/docs/guides/claim-boundary-reporting/' | relative_url }})
- [Validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }})

## Reuse boundary

Reuse the **rewrite procedure**.

Do not reuse:

- synthetic counts;
- thresholds;
- effect values;
- evidence labels;
- claim strength;
- limitation scope.

Those belong to the actual study record.
