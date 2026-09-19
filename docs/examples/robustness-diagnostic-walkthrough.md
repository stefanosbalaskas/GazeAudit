---
title: Diagnostic interpretation walkthrough
description: A deterministic synthetic robustness example that moves from eight finite specification estimates through specification ordering, effect stability, marginal and pairwise sensitivity, plot routes, bounded interpretation, reporting, and an explicit incomplete-execution contrast.
kicker: Example · Robustness interpretation
page_type: example
permalink: /docs/examples/robustness-diagnostic-walkthrough/
search_category: Example
search_keywords: robustness diagnostics specification curve effect stability marginal sensitivity pairwise sensitivity plot interpretation synthetic
example_data: "Synthetic"
example_focus: "Interpretation & reporting"
example_reuse: "Finite-estimate → curve → stability → marginal/pairwise sensitivity → bounded reporting sequence"
example_output: "Eight-specification diagnostic tables, exact descriptive summaries, visual routes, and reporting language"
example_boundary: "The factors, estimates, diagnostic values, and interpretation thresholds are synthetic teaching material rather than empirical validation evidence."
---

# Diagnostic interpretation walkthrough

This example starts **after** the endpoint and specification space have already been declared.

The goal is to interpret one finite synthetic result table without upgrading descriptive diagnostics into inference.

<div class="callout warning">
<strong>Synthetic teaching data only.</strong>
The factors, estimates, and resulting diagnostic values below are designed to exercise the API. They are not recommended detector, QC, AOI, or effect-size choices.
</div>

## 1. Build the represented result table

```python
import pandas as pd

from gazeaudit import (
    effect_stability,
    marginal_sensitivity,
    pairwise_interaction_sensitivity,
    specification_curve,
)

results = pd.DataFrame(
    [
        {"spec_id": 0, "detector": "ivt", "qc_policy": "moderate", "aoi_mode": "hard", "estimate": -0.01},
        {"spec_id": 1, "detector": "ivt", "qc_policy": "moderate", "aoi_mode": "probabilistic", "estimate": 0.02},
        {"spec_id": 2, "detector": "ivt", "qc_policy": "strict", "aoi_mode": "hard", "estimate": 0.00},
        {"spec_id": 3, "detector": "ivt", "qc_policy": "strict", "aoi_mode": "probabilistic", "estimate": 0.03},
        {"spec_id": 4, "detector": "idt", "qc_policy": "moderate", "aoi_mode": "hard", "estimate": 0.01},
        {"spec_id": 5, "detector": "idt", "qc_policy": "moderate", "aoi_mode": "probabilistic", "estimate": 0.05},
        {"spec_id": 6, "detector": "idt", "qc_policy": "strict", "aoi_mode": "hard", "estimate": 0.02},
        {"spec_id": 7, "detector": "idt", "qc_policy": "strict", "aoi_mode": "probabilistic", "estimate": 0.06},
    ]
)
```

Assume the upstream execution ledger says:

```text
8 declared
8 valid
8 successful finite endpoints
```

Only under that assumption is the table a complete represented valid space.

## 2. Order the specification curve

```python
curve = specification_curve(results)
print(curve[["spec_id", "detector", "qc_policy", "aoi_mode", "estimate"]])
```

The ordered estimates are:

```text
-0.01
 0.00
 0.01
 0.02
 0.02
 0.03
 0.05
 0.06
```

### What this supports

The represented estimates:

- span both sides of zero;
- include one exact-zero branch;
- have a total observed range of 0.07.

### What this does not support

The order does not identify a best or most credible specification.

The highest estimate is not automatically preferred.

## 3. Visualise the curve

With plotting support installed:

```python
from gazeaudit.plotting import plot_specification_curve

fig = plot_specification_curve(results)
```

Compare with the code-generated [Specification curve plot]({{ '/docs/plots/#plot-specification-curve' | relative_url }}).

The gallery plot demonstrates the visual contract. Your empirical figure must be generated from your own audit table.

## 4. Summarise effect stability

```python
stability = effect_stability(results)
print(stability)
```

For this deterministic table:

| Field | Value |
|---|---:|
| `n_specifications` | 8 |
| `mean_estimate` | 0.0225 |
| `median_estimate` | 0.0200 |
| `min_estimate` | -0.0100 |
| `max_estimate` | 0.0600 |
| `q025` | -0.00825 |
| `q975` | 0.05825 |
| `positive_fraction` | 0.750 |
| `negative_fraction` | 0.125 |
| `exact_null_fraction` | 0.125 |
| `sign_stability` | 0.750 |

### Bounded interpretation

> Six of eight represented estimates were positive, one was negative, and one was exactly zero. The direction therefore changed across the declared synthetic specification space.

Do **not** write:

> There is a 75% probability that the true effect is positive.

`positive_fraction` is a branch proportion.

## 5. Interpret the empirical specification quantiles

The synthetic central 95% specification interval is:

```text
q025 = -0.00825
q975 =  0.05825
```

Preferred:

> The central 95% of represented specification estimates ranged from -0.00825 to 0.05825.

Avoid:

> The 95% confidence interval was [-0.00825, 0.05825].

No sampling-theory coverage calculation produced those values.

## 6. Calculate marginal sensitivity

```python
factors = ["detector", "qc_policy", "aoi_mode"]

marginal = marginal_sensitivity(
    results,
    factors=factors,
)
print(marginal)
```

Expected values:

| Factor | `marginal_eta2` | `level_mean_range` |
|---|---:|---:|
| `aoi_mode` | 0.620253 | 0.035 |
| `detector` | 0.316456 | 0.025 |
| `qc_policy` | 0.050633 | 0.010 |

### Bounded interpretation

> In this synthetic table, endpoint variation differed most across AOI-mode levels, followed by detector levels.

Avoid:

> AOI mode caused 62% of the uncertainty.

The ratio is descriptive and factors can overlap or interact.

## 7. Visualise marginal sensitivity

```python
from gazeaudit.plotting import plot_factor_sensitivity

fig = plot_factor_sensitivity(marginal)
```

Compare with the generated [Specification-factor sensitivity plot]({{ '/docs/plots/#plot-factor-sensitivity' | relative_url }}).

The longest bar is the largest observed descriptive ratio.

It is not an inferential winner.

## 8. Calculate pairwise sensitivity

```python
pairwise = pairwise_interaction_sensitivity(
    results,
    factors=factors,
)
print(pairwise)
```

For this synthetic table, detector × AOI mode has the largest non-additive ratio:

```text
interaction_ratio ≈ 0.012658
max_abs_interaction ≈ 0.0025
```

The other two pairs are essentially additive in this deliberately simple construction.

### Bounded interpretation

> The strongest descriptive non-additive pattern involved detector × AOI mode, although its ratio was small in this synthetic table.

Avoid:

> Detector significantly interacted with AOI mode.

No inferential interaction model was fitted.

## 9. Read all diagnostics together

The combined pattern is:

- complete synthetic 8/8 execution;
- estimates cross zero;
- one exact-null branch;
- AOI mode has the largest marginal factor alignment;
- detector has the second-largest marginal alignment;
- detector × AOI mode has the largest pairwise non-additive pattern.

A bounded summary is:

> The synthetic directional conclusion was specification-sensitive. AOI representation aligned most strongly with endpoint variation, with additional smaller detector-related variation and a modest detector × AOI non-additive pattern.

Do not compress this to:

> The effect was robust.

## 10. Now make the execution incomplete

Imagine specification 7 was a valid technical failure.

The valid denominator remains:

```text
8 valid
```

but only:

```text
7 successful finite estimates
```

The robustness summary calculated on the seven available rows can describe those seven estimates.

It cannot establish the complete eight-valid-branch pattern.

Preferred reporting:

> Seven of eight valid specifications yielded finite endpoint estimates. The available estimates crossed zero, but the declared audit remained incomplete because one valid branch failed technically.

Do not write:

> Seven specifications were evaluated and the result was specification-sensitive.

That silently changes the valid denominator from eight to seven.

## 11. Non-finite endpoint contrast

If the missing branch instead returned `NaN`:

- preserve that branch in the execution ledger;
- do not replace `NaN` with zero;
- do not pass the non-finite table to `effect_stability()` and reinterpret the error as a scientific null;
- resolve/report the non-finite endpoint contract first.

The robustness summary functions deliberately reject non-finite estimates.

## 12. Controlled sensitivity is separate

Suppose the same study also evaluates sampling rates:

```text
60 Hz
30 Hz
20 Hz
```

That ordered perturbation curve is conceptually different from the discrete detector/QC/AOI specification space.

Report it separately:

> We additionally evaluated a controlled lower-rate representation of the recorded stream.

Do not imply that the analysis physically recreated another tracker.

## 13. Methods example

> We declared an eight-specification synthetic analytical space crossing detector, QC policy, and AOI representation, all targeting one common scalar endpoint. After confirming 8/8 valid branches yielded finite endpoint estimates, we ordered the represented estimates with `specification_curve()`, summarised their range, empirical quantiles, and sign proportions using `effect_stability()`, and inspected descriptive marginal and pairwise sensitivity. These across-specification diagnostics were treated as descriptive rather than inferential quantities.

## 14. Results example

> Across eight represented specifications, endpoint estimates ranged from -0.010 to 0.060 (median = 0.020; empirical specification q2.5 = -0.00825, q97.5 = 0.05825). Six estimates were positive, one negative, and one exactly zero. Descriptive marginal sensitivity was largest for AOI mode (0.620), followed by detector (0.316), while the strongest pairwise non-additive pattern involved detector × AOI mode (interaction ratio ≈ 0.0127).

## 15. Limitation example

> These synthetic diagnostics characterise only the represented factor levels and common endpoint. The empirical quantiles and sign fractions are not confidence intervals or posterior probabilities, marginal ratios are not causal variance decompositions, and pairwise ratios are not inferential interaction tests.

## API and visual routes

- [`specification_curve()`]({{ '/docs/reference/api-pathways/#api-specification-curve' | relative_url }})
- [`effect_stability()`]({{ '/docs/reference/api-pathways/#api-effect-stability' | relative_url }})
- [Specification curve plot]({{ '/docs/plots/#plot-specification-curve' | relative_url }})
- [Factor sensitivity plot]({{ '/docs/plots/#plot-factor-sensitivity' | relative_url }})
- [Robustness Diagnostics Center]({{ '/docs/robustness-diagnostics/' | relative_url }})
- [Reporting robustness]({{ '/docs/guides/reporting-robustness/' | relative_url }})

## Reuse boundary

Reuse:

- the interpretation sequence;
- finite-estimate gate;
- direction-versus-magnitude separation;
- marginal/pairwise wording boundaries;
- execution-completeness check;
- reporting structure.

Rebuild:

- factor set;
- endpoint;
- estimates;
- null/reference value;
- substantive magnitude criterion;
- execution ledger;
- sensitivity perturbation range;
- scientific conclusion.
