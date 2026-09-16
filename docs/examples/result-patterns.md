---
title: Result-pattern reporting example
description: Compare four synthetic robustness patterns to practise separating execution completeness, direction stability, magnitude sensitivity, and bounded manuscript wording.
kicker: Example · Interpretation
permalink: /docs/examples/result-patterns/
search_category: Example
search_keywords: result pattern reporting stable sign magnitude fragile incomplete execution synthetic robustness interpretation manuscript wording
---

# Result-pattern reporting example

This example compares four **synthetic teaching patterns**. The purpose is to show why “robust or not?” is often too coarse a question. A defensible interpretation first checks execution completeness, then separates direction from magnitude, and finally scopes the claim to the uncertainty dimensions that were actually varied.

<div class="callout warning">
<strong>Synthetic teaching material only.</strong>
None of the values or descriptive pattern names on this page are validation evidence, package-generated classifications, recommended thresholds, or replacements for the frozen GazeAudit case-study outcomes.
</div>

Assume each complete scenario began with the same predeclared eight-specification space and one fixed scientific endpoint. The only difference is the resulting estimate pattern.

## Pattern A · Direction and magnitude both relatively stable

Synthetic estimates:

```text
+0.041, +0.043, +0.039, +0.044,
+0.040, +0.042, +0.038, +0.041
```

Descriptively:

- 8/8 declared branches represented;
- all eight estimates are positive;
- range `+0.038` to `+0.044`;
- median approximately `+0.041`;
- the spread is small relative to the centre of this synthetic set.

### What can be said

The observed conclusion changes little across the **declared synthetic specification set** in both direction and magnitude.

### What cannot be said

This does not establish that every reasonable analysis would produce the same result, that sampling uncertainty is small, or that untested measurement choices are irrelevant.

### Bounded Results wording

> Across all eight declared synthetic specifications, estimates remained positive and ranged from +0.038 to +0.044, with a median of approximately +0.041. The observed direction and magnitude therefore varied little within this demonstration specification space. This descriptive robustness pattern does not address untested analytical or measurement choices.

---

## Pattern B · Direction stable, magnitude materially variable

Synthetic estimates:

```text
+0.006, +0.011, +0.019, +0.028,
+0.041, +0.057, +0.073, +0.091
```

Descriptively:

- 8/8 declared branches represented;
- all eight estimates are positive;
- range `+0.006` to `+0.091`;
- the sign is stable, but magnitude changes by more than an order of magnitude.

### What can be said

Direction is more stable than magnitude in this synthetic specification space.

### What cannot be said

The stable sign does not justify describing the effect size as robust. Whether the magnitude variation is scientifically material depends on an independently justified substantive scale.

### Bounded Results wording

> All eight synthetic estimates were positive, but their magnitude ranged from +0.006 to +0.091. The directional conclusion was therefore less sensitive than the quantitative estimate within the declared demonstration space. Interpretation of the magnitude spread requires a study-specific substantive scale rather than the sign pattern alone.

---

## Pattern C · Direction changes across defensible specifications

Synthetic estimates:

```text
-0.052, -0.031, -0.014, -0.006,
+0.004, +0.017, +0.029, +0.046
```

Descriptively:

- 8/8 declared branches represented;
- four estimates are negative and four are positive;
- range `-0.052` to `+0.046`;
- the direction changes within the declared specification space.

### What can be said

The directional conclusion is sensitive to analytical choices represented in the synthetic declaration.

### What cannot be said

Neither the most positive nor the most negative branch should be promoted as the “correct” answer simply because it supports a preferred narrative. Marginal or pairwise diagnostics may localise where variation aligns with declared factors, but they do not by themselves establish causal mechanisms.

### Bounded Results wording

> The synthetic estimates crossed zero across the eight declared specifications, ranging from -0.052 to +0.046. Four estimates were negative and four were positive. The directional conclusion therefore depended on analytical choices represented in this demonstration space, so a single-direction summary would not represent the complete pattern.

---

## Pattern D · Execution incomplete

Declared space: eight branches.

Observed status:

| Branch | Status | Estimate |
|---|---|---:|
| S1 | executed | +0.031 |
| S2 | executed | +0.029 |
| S3 | executed | +0.035 |
| S4 | executed | +0.028 |
| S5 | technical_failure | — |
| S6 | executed | +0.033 |
| S7 | not_run | — |
| S8 | executed | +0.030 |

The six observed estimates are tightly grouped and positive. It would still be misleading to write “the result was robust across all specifications,” because two declared branches are not represented by estimates.

### What can be said

The available executed branches show a narrow positive range, but the original eight-branch audit is incomplete.

### What cannot be said

The missing branches cannot be silently removed from the denominator. Their estimates are unknown, not zero, and not evidence of stability.

### Bounded Results wording

> Six of eight declared synthetic specifications were successfully executed and produced estimates from +0.028 to +0.035. One valid branch failed technically and one declared branch was not run. The available estimates were similar, but the robustness audit remains incomplete relative to the original specification declaration.

---

## Compare the four patterns

| Pattern | Declared space represented? | Direction | Magnitude | Appropriate emphasis |
|---|---|---|---|---|
| A | Yes | stable in synthetic set | relatively stable | report full range and scope |
| B | Yes | stable in synthetic set | materially variable | separate direction from magnitude |
| C | Yes | changes | variable | avoid single-direction headline |
| D | No | observed branches align | observed spread narrow | report incompleteness before robustness |

The table is an interpretation aid, not a classifier. Real studies require domain-specific judgements about meaningful magnitude, valid branches, scientific nulls, and unresolved uncertainty.

## A compact interpretation sequence

When looking at a new audit, ask in this order:

1. **Denominator:** Were all declared valid branches accounted for?
2. **Endpoint:** Did every branch estimate the same scientific quantity?
3. **Direction:** Does the estimate remain on one side of the scientific null?
4. **Magnitude:** Does the size move enough to change substantive interpretation?
5. **Sensitivity:** Which declared factors align with the observed variation?
6. **Coverage:** Which plausible uncertainty dimensions were not varied?
7. **Wording:** Can the manuscript sentence be traced back to the complete branch-level evidence?

If step 1 or step 2 fails, resolve that problem before summarising robustness.

## Methods wording shared across all four examples

> We defined the scientific endpoint and analytical specification space before inspecting the robustness outputs. All declared branches were retained in the execution record, including branches that did not produce an estimate. Across-specification summaries were interpreted descriptively, with direction stability, magnitude variation, and execution completeness reported separately.

This wording does not imply that the synthetic space is exhaustive or that across-specification variation is equivalent to sampling uncertainty.

## What this example is designed to prevent

It is specifically intended to prevent five common reporting errors:

- calling a result “robust” because most branches share one sign;
- ignoring large magnitude variation when the sign is stable;
- selecting one preferred branch from a sign-changing pattern;
- deleting failed or unexecuted branches from the denominator;
- treating a synthetic teaching pattern as a real-data case classification.

Continue with the [interpret an audit result guide]({{ '/docs/guides/interpret-audit-result/' | relative_url }}) for the decision sequence, the [reporting robustness guide]({{ '/docs/guides/reporting-robustness/' | relative_url }}) for manuscript language, and the [publication/archive handoff]({{ '/docs/examples/publication-archive-handoff/' | relative_url }}) for the final reviewer-facing record.