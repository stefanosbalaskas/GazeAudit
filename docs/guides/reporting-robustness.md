---
title: Reporting robustness without overclaiming
description: Translate GazeAudit specification and sensitivity outputs into precise methods and results language while preserving their descriptive and protocol-bound limits.
kicker: Guide · Reporting
permalink: /docs/guides/reporting-robustness/
---

# Reporting robustness without overclaiming

GazeAudit separates **what was varied**, **what happened to the endpoint**, and **what can legitimately be concluded**. This guide turns that separation into manuscript-ready reporting logic without converting descriptive robustness diagnostics into stronger inferential claims.

## Report the decision space first

A robustness analysis is interpretable only if the reader can reconstruct the set of defensible alternatives.

Report:

- each specification factor;
- every evaluated level;
- any combinations excluded by a declared validity rule;
- the common scientific endpoint evaluated under every branch;
- the total number of valid specifications.

Do not describe a collection of post-hoc alternatives as a prespecified multiverse if the choices were added after inspecting results.

## Distinguish four different questions

A useful interpretation separates:

| Question | GazeAudit output | What it tells you |
|---|---|---|
| How wide is the result range? | `min_estimate`, `max_estimate`, empirical quantiles | descriptive magnitude variation across specifications |
| Does direction change? | positive / negative / exact-null fractions | how often the declared branches fall on each side of the null |
| Which choices track the variation? | `marginal_sensitivity()` | descriptive between-level association with endpoint variation |
| Are factor combinations non-additive? | `pairwise_interaction_sensitivity()` | descriptive departure from an additive specification pattern |

These answers are related but not interchangeable.

## What `effect_stability()` does not provide

`effect_stability()` summarises the realised estimates across the declared specification set. Its 2.5% and 97.5% values are **empirical specification quantiles**.

They are not:

- sampling-theory confidence intervals;
- Bayesian credible intervals;
- posterior probabilities;
- evidence that one specification is statistically superior to another.

Likewise, `sign_stability` is the largest observed fraction of positive, negative, or exact-null estimates. It is a descriptive concentration measure, not a probability that the underlying effect has that sign.

## How to describe magnitude stability

Appropriate wording focuses on the realised spread:

> Across the declared specification space, estimates ranged from *a* to *b*, with a median of *m*. The central 95% empirical specification interval spanned *q*<sub>.025</sub> to *q*<sub>.975</sub>.

This wording says exactly what the calculation represents. It does not imply repeated-sampling coverage.

## How to describe direction stability

If all valid branches share one sign:

> All evaluated specifications produced effects in the same direction, although magnitude varied across the declared decision space.

If signs differ:

> Effect direction was specification-sensitive: both positive and negative estimates occurred across defensible branches.

If exact-null estimates occur:

> The declared specification space included positive, negative, and exact-null estimates, indicating that the qualitative conclusion depends on analytical choices represented in the audit.

Do not convert these patterns automatically into “significant”, “non-significant”, “confirmed”, or “refuted”. Those labels require an inferential procedure that is separate from the descriptive specification summary.

## How to report marginal sensitivity

`marginal_sensitivity()` reports a between-level sum-of-squares ratio for each factor. It is useful for screening which declared choice is most associated with result variation.

A defensible description is:

> Variation across levels of the AOI-definition factor accounted for the largest marginal share of observed specification-level endpoint variation.

Avoid:

> AOI definition caused X% of the uncertainty.

The diagnostic is not causal, factors may be dependent, and marginal ratios do not need to sum to one.

## How to report pairwise interaction sensitivity

`pairwise_interaction_sensitivity()` compares observed specification-cell means with the additive expectation implied by the corresponding factor-level means.

A defensible description is:

> The strongest non-additive specification sensitivity involved detector choice and AOI definition, indicating that the effect of one analytical choice depended descriptively on the level of the other.

The pairwise diagnostic is **not a replacement for a fitted factorial model**. Do not call its ratio an inferential interaction effect or substitute it for a fitted factorial analysis.

## Separate robustness from measurement uncertainty

A result can be stable across analytical branches while still being sensitive to measurement assumptions. Conversely, a well-characterised measurement model does not guarantee robustness to preprocessing or specification choices.

When both layers are relevant, report them separately:

1. **measurement uncertainty:** what coordinate/AOI uncertainty model was used and how it changed the endpoint;
2. **analytical robustness:** what defensible pipeline choices were varied and how the endpoint behaved across them.

This separation is central to GazeAudit's design.

## Do not universalise protocol-bound validation labels

The package's frozen labels—`incomplete`, `robust_negative`, and `materially_fragile`—belong to specific validation protocols. They are not generic thresholds that should be copied into unrelated studies.

For a new study, define the study's own conclusion rule if a categorical decision is required. The [publication-audit guide]({{ '/docs/guides/publication-audits/' | relative_url }}) shows how to bind a declared rule to deterministic evidence.

## Minimal Methods checklist

A reproducible Methods section should identify:

- the GazeAudit version or exact commit;
- the canonical study representation or adapter used;
- the endpoint definition;
- the specification factors and levels;
- the validity/exclusion rule for combinations;
- the functions used to execute and summarise the audit;
- whether measurement uncertainty, sampling sensitivity, missingness sensitivity, or other perturbations were additionally evaluated.

## Minimal Results checklist

A compact Results section should report:

- number of valid specifications;
- minimum, maximum, median, and empirical specification quantiles;
- positive, negative, and exact-null fractions when relevant;
- the most influential specification factors descriptively;
- any important non-additive factor-pair sensitivity;
- a conclusion stated at the level justified by the declared audit.

## Reusable results template

> We evaluated **N** prespecified/declared analytical specifications spanning **[factor names]**, all targeting the same endpoint, **[endpoint definition]**. Estimates ranged from **[min]** to **[max]**, with median **[median]** and empirical 2.5%–97.5% specification quantiles of **[q025]** to **[q975]**. **[x%]** of specifications were positive, **[y%]** negative, and **[z%]** exactly null. Descriptive marginal sensitivity was greatest for **[factor]**; the largest pairwise non-additive sensitivity involved **[factor A] × [factor B]**. These diagnostics characterise robustness across the declared analysis space and are not confidence intervals, posterior probabilities, or causal variance decompositions.

Adapt the template to the actual analysis rather than filling it mechanically.

## Recommended companion pages

- [End-to-end robustness audit]({{ '/docs/examples/end-to-end-robustness/' | relative_url }}) — executable synthetic demonstration.
- [Specification spaces]({{ '/docs/guides/specification-space/' | relative_url }}) — how to construct the decision space.
- [How to read a fragile result]({{ '/docs/articles/how-to-read-a-fragile-result/' | relative_url }}) — interpretation when conclusions change materially.
- [Reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) — bind the final evidence and provenance.
