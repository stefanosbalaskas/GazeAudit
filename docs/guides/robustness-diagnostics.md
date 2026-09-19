---
title: Read robustness diagnostics
description: Methodological guidance for interpreting GazeAudit specification curves, effect-stability summaries, marginal and pairwise sensitivity, controlled perturbation curves, execution completeness, and code-generated plots without upgrading descriptive evidence into inference.
kicker: Guide · Robustness interpretation
permalink: /docs/guides/robustness-diagnostics/
search_category: Guide
search_keywords: specification curve effect stability marginal sensitivity pairwise sensitivity robustness diagnostics plot interpretation sign magnitude incomplete nonfinite
---

# Read robustness diagnostics

Robustness diagnostics are useful only when the upstream audit contract is intact.

Before reading any curve or sensitivity table, confirm:

- one common endpoint;
- reconstructable declared and valid denominators;
- explicit execution state for every valid branch;
- finite endpoint values for the rows entering robustness summaries;
- a factor set fixed independently of the observed endpoint;
- no silent branch deletion.

If those conditions are not satisfied, return to the [Execution Ledger & Recovery Center]({{ '/docs/execution-ledger/' | relative_url }}) or [Specification Space Declaration Center]({{ '/docs/specification-declaration/' | relative_url }}).

## 1. Start with the denominator

A robustness diagnostic cannot repair an incomplete audit.

Write down:

```text
declared = ?
valid = ?
successful finite endpoint = ?
valid technical failure = ?
valid non-finite endpoint = ?
valid not run = ?
```

The descriptive estimate diagnostics should be interpreted against that ledger.

If the summary table contains only successful finite endpoints, say so.

Do not silently redefine the valid denominator as the number of rows that happen to enter `effect_stability()`.

## 2. Know the finite-estimate contract

The robustness summary functions call a common internal estimate validator.

The selected estimate column must:

- exist;
- contain at least one row;
- be coercible to numeric;
- contain only finite values.

If `NaN` or infinity appears, the summary fails.

This is different from core `run_specs()`, which float-coerces endpoint returns and can therefore preserve a non-finite endpoint until a later robustness summary rejects it.

That distinction is scientifically useful:

- execution evidence can preserve the non-finite branch;
- robustness summaries refuse to reinterpret it as an ordinary estimate.

## 3. Read a specification curve as an ordered evidence display

`specification_curve()` sorts represented rows by the endpoint estimate.

The ordering is useful for seeing:

- the full range;
- sign changes;
- exact-null values;
- clusters;
- gaps;
- factor combinations near the extremes.

It is not:

- a ranking of scientific quality;
- evidence that the median pipeline is best;
- permission to choose the leftmost or rightmost branch;
- an inferential procedure.

The branch metadata should remain attached to every estimate.

### Plot interpretation

[`plot_specification_curve()`]({{ '/docs/plots/#plot-specification-curve' | relative_url }}) visualises the ordered estimates with a zero line.

Read the axes literally.

The plot does not add statistical uncertainty.

## 4. Separate sign stability from magnitude stability

`effect_stability()` reports both.

A result can be:

### Sign stable, magnitude stable

All represented estimates have one sign and remain in a narrow substantively similar range.

### Sign stable, magnitude variable

All estimates have one sign, but the smallest and largest estimates imply meaningfully different quantitative conclusions.

### Sign sensitive

Positive and negative estimates both occur.

### Exact-null sensitive

Some branches land exactly on the declared null.

Do not collapse these patterns into one number.

`sign_stability` only records the largest positive/negative/exact-null fraction.

It does not evaluate substantive magnitude.

## 5. Interpret the empirical quantiles correctly

`effect_stability()` returns `q025` and `q975`.

These are quantiles of the **realised specification estimates**.

They are not:

- frequentist confidence limits;
- Bayesian credible limits;
- uncertainty intervals for a population parameter;
- guarantees about unrepresented specifications.

Preferred wording:

> The central 95% of represented specification estimates ranged from [q025] to [q975].

Avoid:

> The 95% confidence interval was [q025, q975].

unless a separate inferential procedure truly produced that confidence interval.

## 6. Interpret sign fractions as branch proportions

Suppose:

```text
positive_fraction = 0.75
negative_fraction = 0.25
exact_null_fraction = 0.00
```

This means:

> 75% of represented specification estimates were above the declared null and 25% were below it.

It does not mean:

> There is a 75% probability the true effect is positive.

The denominator is the represented specification set, not a posterior distribution.

## 7. Read marginal sensitivity as descriptive factor alignment

`marginal_sensitivity()` calculates a between-level sum-of-squares ratio for each factor.

Useful questions:

- Which factor has the largest `marginal_eta2`?
- How large is the difference between factor-level means?
- Is the valid space balanced across factor levels?
- Does the factor align with a visible shift in the specification curve?

Preferred wording:

> Endpoint variation differed most across AOI-definition levels.

Avoid:

> AOI definition caused 60% of uncertainty.

Why?

Because:

- factors can be dependent;
- valid spaces can be unbalanced;
- factors can interact;
- marginal ratios can overlap;
- the diagnostic is descriptive rather than causal.

### Plot interpretation

[`plot_factor_sensitivity()`]({{ '/docs/plots/#plot-factor-sensitivity' | relative_url }}) ranks the descriptive ratios visually.

The longest bar is the largest observed diagnostic value.

It is not an inferential winner.

## 8. Read pairwise sensitivity as non-additive pattern screening

`pairwise_interaction_sensitivity()` compares observed factor-pair cell means with the additive expectation derived from factor-level means.

Useful questions:

- Which pair has the largest `interaction_ratio`?
- What is the largest absolute cell deviation from the additive expectation?
- Is the factor-pair table complete?
- Is the specification space balanced?

Preferred wording:

> The strongest descriptive non-additive pattern involved detector × AOI definition.

Avoid:

> Detector significantly interacted with AOI definition.

The diagnostic does not fit an inferential factorial model.

## 9. Do not force pairwise diagnostics on an incomplete multiverse

When branches are missing:

- some factor cells can disappear;
- cell counts can become uneven;
- marginal and pairwise summaries can change because the represented design changed.

First determine **why** the space is incomplete.

If the missing combinations were predeclared invalid, report that design structure.

If they were valid failures/not-run branches, report the incompleteness before interpreting sensitivity.

## 10. Controlled sensitivity is a different design

Sampling, missingness, and spatial-error curves usually vary one ordered perturbation dimension.

They answer questions such as:

> How does the endpoint change as the target sampling representation is reduced?

or:

> How does expected AOI membership change as the assumed spatial-error scale increases?

Do not mix these automatically with a discrete factorial specification space.

Report them as controlled sensitivity analyses with their own perturbation range.

## 11. Sampling sensitivity is not another hardware experiment

`downsample_gaze()` and sampling-sensitivity functions operate on the recorded stream.

They do not recreate:

- another device's optics;
- firmware;
- physical sensor noise;
- sample loss process;
- timing jitter;
- calibration characteristics.

Preferred language:

> We evaluated sensitivity to a controlled lower-rate representation of the recorded stream.

Avoid:

> We simulated what a 30 Hz tracker would have measured.

unless the simulation model independently justifies that claim.

## 12. Missingness sensitivity is not a causal missing-data effect

Adding missingness can probe robustness to controlled data loss.

It does not prove:

- why the empirical missingness occurred;
- what the unobserved gaze values were;
- that the study satisfies MAR/MNAR assumptions;
- how another imputation model would behave.

Keep controlled perturbation and missing-data mechanism claims separate.

## 13. Spatial-error sensitivity is conditional on the error model

Scaling a gaze-error model asks:

> How does the AOI result behave when the declared error magnitude is perturbed?

It does not establish that the perturbed model is the true physical tracker error.

Report:

- error-model identity;
- scaling rule;
- perturbation range;
- Monte Carlo settings;
- seed/provenance where relevant.

## 14. Use diagnostic disagreement constructively

Diagnostics can point in different directions.

Example:

- sign fraction = 1.0;
- range = +0.005 to +0.090;
- AOI factor has large marginal sensitivity;
- detector × AOI pair has strong non-additivity.

A bounded interpretation is:

> Direction remained positive, but magnitude was sensitive to AOI definition and showed additional detector-dependent non-additive variation.

Do not reduce that evidence to:

> The result was robust.

## 15. Use substantive thresholds only when independently justified

A magnitude threshold can be helpful when deciding whether specification variation matters scientifically.

But the threshold must come from:

- theory;
- measurement precision;
- domain convention;
- decision relevance;
- preregistered criterion;
- another independent rationale.

Do not define the threshold after inspecting the observed range merely to preserve a preferred conclusion.

## 16. Plot examples are evidence displays, not validation evidence

The [Plot gallery]({{ '/docs/plots/' | relative_url }}) is generated from deterministic synthetic data and checked in CI.

Use it to learn:

- axis meaning;
- expected input/output structure;
- visual reporting patterns.

Do not cite the gallery plot as evidence for your empirical result.

## 17. Report diagnostics in a stable order

A compact Results sequence is:

1. execution completeness;
2. estimate range and empirical specification quantiles;
3. sign pattern;
4. magnitude interpretation;
5. marginal factor sensitivity;
6. pairwise non-additive sensitivity;
7. controlled perturbation analyses;
8. unresolved/unrepresented uncertainty.

This order keeps the denominator visible before the interpretation.

## 18. Reporting language

### Methods

> We evaluated the declared valid specification space against one common endpoint. After reconciling execution status for all valid branches, finite represented estimates were ordered using the specification curve and summarised descriptively with `effect_stability()`. We then inspected marginal and pairwise specification sensitivity. Empirical specification quantiles, sign fractions, and sensitivity ratios were treated as descriptive properties of the represented analysis space.

### Results

> [S] of [V] valid specifications yielded finite endpoint estimates. Estimates ranged from [min] to [max], with median [median] and empirical specification quantiles [q025, q975]. [Sign pattern]. Descriptive marginal sensitivity was largest for [factor], while the strongest pairwise non-additive pattern involved [factor A × factor B].

### Limitation

> The diagnostics summarise only the declared and successfully represented analytical choices. They are not confidence intervals, posterior probabilities, causal variance decompositions, or inferential interaction tests, and they do not establish robustness to untested measurement or analytical dimensions.

## 19. Diagnostic checklist

Before approving the robustness interpretation:

- [ ] endpoint identity fixed;
- [ ] valid denominator reconstructed;
- [ ] unresolved valid failures visible;
- [ ] finite endpoint prerequisite satisfied;
- [ ] curve read as ordered estimates, not pipeline ranking;
- [ ] direction separated from magnitude;
- [ ] empirical quantiles labelled correctly;
- [ ] sign fractions not called probabilities;
- [ ] marginal sensitivity not called causal variance explained;
- [ ] pairwise sensitivity not called inferential interaction;
- [ ] controlled sensitivity separated from factorial multiverse;
- [ ] untested uncertainty dimensions stated;
- [ ] plot examples treated as visual aids only;
- [ ] reporting language bound to the represented space.

## API and visual routes

- [`specification_curve()`]({{ '/docs/reference/api-pathways/#api-specification-curve' | relative_url }})
- [`effect_stability()`]({{ '/docs/reference/api-pathways/#api-effect-stability' | relative_url }})
- [`spatial_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-spatial-sensitivity-curve' | relative_url }})
- [`sampling_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-sampling-sensitivity-curve' | relative_url }})
- [`missingness_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-missingness-sensitivity-curve' | relative_url }})
- [Specification-curve plot]({{ '/docs/plots/#plot-specification-curve' | relative_url }})
- [Factor-sensitivity plot]({{ '/docs/plots/#plot-factor-sensitivity' | relative_url }})
- [Robustness Diagnostics Center]({{ '/docs/robustness-diagnostics/' | relative_url }})

## Worked exercise

Continue to [Diagnostic interpretation walkthrough]({{ '/docs/examples/robustness-diagnostic-walkthrough/' | relative_url }}) for a deterministic synthetic table that moves from finite-estimate validation through specification curve, effect stability, marginal sensitivity, pairwise sensitivity, plotting, and bounded reporting.
