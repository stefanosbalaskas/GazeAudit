---
title: Interpret robustness and sensitivity diagnostics
description: Methodological guidance for GazeAudit specification curves, effect stability, marginal and pairwise sensitivity, and controlled spatial, sampling, and missingness curves, including assumptions, limitations, reporting, and failure cases.
kicker: Guide · Robustness diagnostics
permalink: /docs/guides/diagnostic-interpretation/
search_category: Guide
search_keywords: specification curve effect stability marginal eta2 pairwise interaction spatial sampling missingness sensitivity interpretation reporting limitations
---

# Interpret robustness and sensitivity diagnostics

Use this guide after:

1. the endpoint is fixed;
2. the specification space is declared;
3. execution is reconciled;
4. the table passed to robustness summaries contains the intended finite represented estimates.

The [Robustness Diagnostics & Sensitivity Center]({{ '/docs/diagnostics/' | relative_url }}) provides a searchable contract for each public diagnostic.

## 1. Start with the evidence family

GazeAudit diagnostics fall into two different families.

### Specification-result diagnostics

These summarize the endpoint values produced by the represented analytical decision space:

- `specification_curve()`;
- `effect_stability()`;
- `marginal_sensitivity()`;
- `pairwise_interaction_sensitivity()`.

Their denominator is the represented finite result table supplied by the researcher.

### Controlled perturbation diagnostics

These deliberately alter one input/representation dimension:

- `spatial_sensitivity_curve()`;
- `sampling_sensitivity_curve()`;
- `missingness_sensitivity_curve()`.

Their denominator is the declared perturbation grid and whatever observations remain under each perturbation.

Do not mix these two families into one undifferentiated “robustness score”.

## 2. Reconcile incomplete execution first

Suppose:

```text
8 declared
7 valid
6 currently successful
1 valid not run
```

A six-row results table may be perfectly usable for descriptive diagnostics, but those diagnostics do not make the missing seventh valid branch disappear.

Report execution completeness before the diagnostic pattern.

Use the [Execution Ledger & Recovery Center]({{ '/docs/execution-ledger/' | relative_url }}) when the branch state is unresolved.

## 3. Verify the common endpoint

Across specification-result diagnostics, every row should represent the same scientific endpoint.

Do not place:

- dwell difference;
- fixation-count difference;
- latency difference;

into one curve merely because they all concern the same AOI.

Use the [Endpoint Definition & Handoff Center]({{ '/docs/endpoint-contract/' | relative_url }}) when endpoint invariance is uncertain.

## 4. Specification curve: order, do not rank scientifically

`specification_curve()` validates the estimate column and returns a stable ascending sort.

That means the curve can make visible:

- endpoint range;
- dense versus sparse regions;
- sign changes;
- branches near the scientific null;
- branch metadata associated with extremes.

It does not mean:

- the leftmost pipeline is worst;
- the rightmost pipeline is best;
- extreme branches should be discarded;
- the median branch is the scientifically preferred analysis.

The stable sort preserves input order among equal estimates.

## 5. Finite input is a hard software requirement for robustness summaries

The four specification-result diagnostics call the same internal estimate validator.

The validator:

- requires the estimate column;
- coerces it to numeric;
- requires at least one row;
- raises when any estimate is non-finite.

Therefore:

```python
effect_stability(results_with_nan)
```

raises rather than silently ignoring the non-finite branch.

That behavior protects the summaries from quietly changing the denominator.

Resolve the branch record explicitly instead.

## 6. Effect stability: separate location, spread, and direction

`effect_stability()` returns:

- `n_specifications`;
- `median_estimate`;
- `mean_estimate`;
- `min_estimate`;
- `max_estimate`;
- `q025`;
- `q975`;
- `positive_fraction`;
- `negative_fraction`;
- `exact_null_fraction`;
- `sign_stability`.

These fields answer different questions.

### Location

Median and mean describe the realised estimates.

### Spread

Range and empirical quantiles describe across-specification variation.

### Direction

Positive/negative/exact-null fractions describe sign relative to the supplied null.

### Sign stability

The maximum of those three fractions.

Do not compress all four dimensions into a single adjective when they tell different stories.

## 7. The null must be scientifically meaningful

The function defaults to:

```python
null=0.0
```

That is a software convenience, not a universal scientific reference.

Examples where another reference may be appropriate include:

- known-truth recovery around a non-zero target;
- ratio endpoints whose null is 1;
- transformed quantities with another reference.

Declare the null before using sign fractions substantively.

## 8. Empirical quantiles are not inferential intervals

`q025` and `q975` come from:

```python
np.quantile(estimates, 0.025)
np.quantile(estimates, 0.975)
```

They describe the empirical distribution of represented specification estimates.

They do not provide:

- repeated-sampling coverage;
- posterior probability;
- model-based standard errors;
- an uncertainty interval for an unobserved true effect.

If the study also uses confidence or credible intervals, report those separately with their own model assumptions.

## 9. Sign stability can be high while magnitude is unstable

Example:

```text
0.006
0.011
0.019
0.028
0.041
0.057
0.073
0.091
```

All values are positive.

Therefore sign stability is 1.0 relative to zero.

But the magnitude spans more than an order of magnitude.

Preferred interpretation:

> Direction was stable across the represented specifications, while quantitative magnitude varied materially.

Avoid:

> The effect was fully robust.

unless “robust” has been independently defined to include the relevant magnitude criterion.

## 10. Marginal sensitivity is a screening diagnostic

For each factor, `marginal_sensitivity()` calculates factor-level means and compares their between-level sum of squares with total endpoint sum of squares.

Outputs:

- `factor`;
- `n_levels`;
- `marginal_eta2`;
- `level_mean_range`.

A larger ratio means more of the realised endpoint variation aligns with differences among that factor's represented level means.

It does not prove that factor **caused** that proportion of uncertainty.

## 11. Why marginal ratios need not sum to one

Specification factors can be:

- dependent;
- constrained by validity rules;
- unbalanced;
- interacting.

The same endpoint variation can therefore align with multiple factors.

Do not interpret:

```text
factor A marginal_eta2 = 0.70
factor B marginal_eta2 = 0.40
```

as an error because the sum exceeds one.

These are overlapping descriptive diagnostics, not an orthogonal variance partition.

## 12. Constant endpoints return zero marginal ratios

When total endpoint sum of squares is zero, `marginal_sensitivity()` returns `0.0` for marginal eta-squared.

That means there is no endpoint variation to localize in that table.

It does not establish that the factor is scientifically irrelevant under other data or endpoints.

## 13. Pairwise interaction sensitivity screens non-additivity

For each factor pair, the function constructs an additive cell prediction:

```text
factor-A level mean
+ factor-B level mean
- grand mean
```

The observed cell mean is compared with that prediction.

Outputs:

- `factor_a`;
- `factor_b`;
- `n_cells`;
- `interaction_ratio`;
- `max_abs_interaction`.

This identifies where the represented joint pattern departs most from the additive marginal pattern.

## 14. Pairwise sensitivity is not a factorial inferential model

Do not report:

> Detector significantly interacted with AOI mode.

from `pairwise_interaction_sensitivity()` alone.

Preferred:

> The largest descriptive non-additive specification pattern involved detector × AOI mode.

If inferential interaction testing is scientifically required, fit and report an appropriate statistical model separately.

## 15. Fewer than two factors has a defined empty result

When fewer than two factors are supplied, pairwise sensitivity returns an empty DataFrame with the expected columns.

That is a structural result:

> no factor pairs were available to screen.

It is not evidence that interactions are zero.

## 16. Spatial sensitivity changes the uncertainty model, not observed gaze

`spatial_sensitivity_curve()` takes:

- observed points;
- AOIs;
- a Gaussian gaze-error model;
- non-negative `sd_scales`.

For each scale:

1. the model standard deviations are multiplied by that scale;
2. covariance is therefore multiplied by `sd_scale**2`;
3. systematic mean error is retained;
4. AOI probabilities and boundary diagnostics are recomputed.

The observed gaze points themselves are not jittered into a pretend new dataset.

## 17. Interpret spatial outputs by AOI and scale

The output includes:

- `sd_scale`;
- `aoi`;
- `expected_fixation_count`;
- `mean_flip_probability`;
- `mean_boundary_risk`;
- optional `expected_dwell`.

Look for:

- monotonic or non-monotonic endpoint changes;
- AOIs especially sensitive to error scale;
- boundary risk increasing near decision boundaries;
- divergence between hard labels and probabilistic membership.

Do not call a particular scale “realistic” without external validation evidence.

## 18. Sampling sensitivity retains existing samples

`downsample_gaze()` creates an ideal target grid and keeps existing samples nearest to that grid.

It does not interpolate gaze coordinates.

`sampling_sensitivity_curve()` then reports:

- target rate;
- retained row count;
- retained fraction;
- finite endpoint.

This supports statements about a controlled lower-density representation of the recorded stream.

It does not reproduce:

- another device's spatial noise;
- another device's filtering;
- another device's latency;
- another device's missingness;
- another physical measurement process.

## 19. Missingness sensitivity distinguishes requested and observed missingness

`missingness_sensitivity_curve()` reports both:

- `requested_fraction`;
- `observed_missing_fraction`.

They can differ because the canonical study may already contain missing gaze before additional perturbation.

Always report the mechanism:

- `mcar`;
- `block`.

These are synthetic benchmark mechanisms.

Do not infer the study's real missingness mechanism from sensitivity behavior under them.

## 20. Seeds are reproducibility controls, not scientific parameters

Spatial and missingness sensitivity can use an integer seed or NumPy generator.

A fixed seed supports exact reproduction of the Monte Carlo/masking path.

It does not make a perturbation model scientifically more valid.

When simulation variability matters, a separate design may need multiple seeds/replicates rather than treating one seed as evidence.

## 21. Controlled sensitivity values need independent justification

Examples:

- spatial error scales;
- target sampling rates;
- injected missingness fractions.

Choose them from:

- validation evidence;
- device capabilities;
- literature;
- protocol;
- preregistration;
- explicitly bounded stress tests;
- reviewer request, with timing visible.

Do not choose perturbation values because they produce a desired conclusion transition.

## 22. Keep discrete choices separate from ordered perturbations

A discrete specification factor such as detector family asks:

> Which defensible method choice was used?

A controlled perturbation such as sampling rate asks:

> How does the endpoint change as one ordered dimension is systematically varied?

They can coexist in one research programme but should not be interpreted identically.

## 23. Report factor imbalance and missing cells

If `valid_if` removes combinations, marginal and pairwise summaries operate on the represented valid result table.

That can produce:

- unequal cell counts;
- missing factor combinations;
- correlated factors.

Report this when it affects interpretation.

Do not imply a balanced factorial experiment when the multiverse is constrained.

## 24. Reporting specification-result diagnostics

### Methods

> Robustness summaries were calculated from the reconciled finite endpoint table. Specification estimates were ordered descriptively, effect stability was computed relative to the prespecified scientific null, and marginal/pairwise sensitivity diagnostics were used to localize factor-level and non-additive variation without inferential or causal interpretation.

### Results

> Across [N] represented specifications, estimates ranged from [min] to [max] with median [median]. [X]% were above, [Y]% below, and [Z]% exactly at the declared null. Marginal sensitivity was largest for [factor], while the largest pairwise non-additive pattern involved [pair].

### Limitation

> Across-specification quantiles and sensitivity ratios are descriptive properties of the represented decision space. They are not confidence/credible intervals, posterior probabilities, causal variance shares, or fitted interaction tests.

## 25. Reporting controlled perturbation curves

### Methods

> We separately evaluated controlled spatial-error, sampling-rate, and/or missingness perturbations using the same declared endpoint where applicable. Perturbation levels were fixed from [rationale] and were not selected based on observed endpoint movement.

### Results

> The endpoint changed from [range] across [perturbation values]. For sampling, retained row fractions were [values]. For missingness, requested and observed missingness were reported separately. For spatial uncertainty, AOI membership/boundary metrics were reported by error scale.

### Limitation

> These perturbations are analysis stress tests. They do not reproduce the complete measurement process of another tracker or establish the true missingness/error mechanism.

## 26. Diagnostic interpretation checklist

Before writing the conclusion:

- [ ] valid execution denominator reconciled;
- [ ] only intended finite endpoint rows summarized;
- [ ] common endpoint verified;
- [ ] null scientifically justified;
- [ ] empirical quantiles not called confidence intervals;
- [ ] sign and magnitude discussed separately;
- [ ] marginal ratios not called causal variance shares;
- [ ] pairwise ratios not called inferential interactions;
- [ ] factor imbalance/missing cells disclosed where relevant;
- [ ] controlled perturbation family named explicitly;
- [ ] requested versus observed missingness distinguished;
- [ ] downsampling not described as another physical tracker;
- [ ] spatial scaling not described as a measured new tracker;
- [ ] seed documented as reproducibility metadata;
- [ ] untested uncertainty dimensions stated;
- [ ] reporting linked to the exact represented evidence.

## API links

- [`specification_curve()`]({{ '/docs/reference/api-pathways/#api-specification-curve' | relative_url }})
- [`effect_stability()`]({{ '/docs/reference/api-pathways/#api-effect-stability' | relative_url }})
- [`marginal_sensitivity()`]({{ '/docs/reference/api-pathways/#api-marginal-sensitivity' | relative_url }})
- [`pairwise_interaction_sensitivity()`]({{ '/docs/reference/api-pathways/#api-pairwise-interaction-sensitivity' | relative_url }})
- [`spatial_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-spatial-sensitivity-curve' | relative_url }})
- [`sampling_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-sampling-sensitivity-curve' | relative_url }})
- [`missingness_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-missingness-sensitivity-curve' | relative_url }})
- [Robustness Diagnostics & Sensitivity Center]({{ '/docs/diagnostics/' | relative_url }})
- [Machine-readable diagnostic contracts]({{ '/assets/diagnostic-contract-reference.json' | relative_url }})

## Worked exercise

Continue to [Diagnostic interpretation]({{ '/docs/examples/diagnostic-interpretation/' | relative_url }}) for exact synthetic outputs from effect stability, marginal sensitivity, pairwise sensitivity, and controlled perturbation curves.
