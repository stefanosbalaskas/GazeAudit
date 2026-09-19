---
title: Diagnostic interpretation
description: A deterministic synthetic GazeAudit example for specification curves, effect stability, marginal and pairwise sensitivity, plus controlled spatial, sampling, and missingness perturbation curves with bounded interpretation and reporting.
kicker: Example · Robustness diagnostics
page_type: example
permalink: /docs/examples/diagnostic-interpretation/
search_category: Example
search_keywords: diagnostic interpretation specification curve effect stability marginal eta2 pairwise interaction spatial sampling missingness synthetic
example_data: "Synthetic"
example_focus: "Robustness & sensitivity"
example_reuse: "Finite-result diagnostics → controlled perturbations → bounded interpretation pattern"
example_output: "Exact four-specification diagnostic summaries plus deterministic controlled-sensitivity examples"
example_boundary: "Synthetic values are teaching truth for API behavior, not recommended endpoint magnitudes, nulls, factor levels, perturbation values, or reporting thresholds."
---

# Diagnostic interpretation

This example uses two deliberately separate evidence families:

1. a **four-specification synthetic result table** for exact robustness-summary calculations;
2. **controlled perturbation examples** for spatial error, sampling rate, and missingness.

The goal is to practise interpretation without turning descriptive diagnostics into stronger inferential claims.

<div class="callout warning">
<strong>Teaching values only.</strong>
The effect values, factors, perturbation levels, null, AOI geometry, and seeds below are synthetic. Reuse the diagnostic workflow, not the scientific choices.
</div>

## Part A · Four represented specifications

Start with:

```python
import pandas as pd

results = pd.DataFrame(
    {
        "factor_a": ["low", "low", "high", "high"],
        "factor_b": ["x", "y", "x", "y"],
        "estimate": [1.0, 3.0, 5.0, 9.0],
    }
)
```

All four endpoint values are finite.

The scientific null in this teaching exercise is `0.0`.

## 1. Order the specification curve

```python
from gazeaudit import specification_curve

curve = specification_curve(results)
print(curve)
```

The estimates are already ordered:

```text
1.0
3.0
5.0
9.0
```

If the input rows were shuffled, `specification_curve()` would return the same ascending estimate order.

### Interpretation

This tells us the **represented range is 1.0 to 9.0**.

It does not tell us that the 9.0 branch is the best analysis.

## 2. Compute effect stability

```python
from gazeaudit import effect_stability

stability = effect_stability(results, null=0.0)
print(stability)
```

Exact teaching output:

| Field | Value |
|---|---:|
| `n_specifications` | 4 |
| `median_estimate` | 4.0 |
| `mean_estimate` | 4.5 |
| `min_estimate` | 1.0 |
| `max_estimate` | 9.0 |
| `q025` | 1.15 |
| `q975` | 8.70 |
| `positive_fraction` | 1.0 |
| `negative_fraction` | 0.0 |
| `exact_null_fraction` | 0.0 |
| `sign_stability` | 1.0 |

### Interpretation

Every represented estimate is positive relative to zero.

Direction is therefore fully stable **within this four-row teaching table**.

Magnitude is not constant: it ranges from 1 to 9.

Do not rewrite `q025=1.15` and `q975=8.70` as a 95% confidence interval.

## 3. Compute marginal sensitivity

```python
from gazeaudit import marginal_sensitivity

marginal = marginal_sensitivity(
    results,
    ["factor_a", "factor_b"],
)
print(marginal)
```

Exact teaching output:

| Factor | Levels | `marginal_eta2` | `level_mean_range` |
|---|---:|---:|---:|
| factor_a | 2 | 0.7142857143 | 5.0 |
| factor_b | 2 | 0.2571428571 | 3.0 |

Why?

Grand mean:

```text
(1 + 3 + 5 + 9) / 4 = 4.5
```

Factor A level means:

```text
low  = 2.0
high = 7.0
```

Factor B level means:

```text
x = 3.0
y = 6.0
```

Total endpoint sum of squares is `35`.

Factor A's between-level sum of squares is `25`:

```text
25 / 35 = 0.7142857143
```

Factor B's is `9`:

```text
9 / 35 = 0.2571428571
```

### Interpretation

In this synthetic table, more of the realised endpoint variation aligns with factor A's level means than factor B's.

Do not write:

> Factor A caused 71.4% of the uncertainty.

That is not what the diagnostic estimates.

## 4. Compute pairwise non-additivity

```python
from gazeaudit import pairwise_interaction_sensitivity

pairwise = pairwise_interaction_sensitivity(
    results,
    ["factor_a", "factor_b"],
)
print(pairwise)
```

Exact teaching output:

| Factor A | Factor B | Cells | `interaction_ratio` | `max_abs_interaction` |
|---|---|---:|---:|---:|
| factor_a | factor_b | 4 | 0.0285714286 | 0.5 |

For the low/x cell, the additive prediction is:

```text
factor_a(low) mean
+ factor_b(x) mean
- grand mean

= 2.0 + 3.0 - 4.5
= 0.5
```

Observed cell mean is `1.0`, so the deviation is `+0.5`.

The four cell deviations are ±0.5, producing weighted non-additive sum of squares `1.0`:

```text
1 / 35 = 0.0285714286
```

### Interpretation

There is a small descriptive non-additive pattern in this teaching table.

Do not report it as a statistically significant interaction.

## 5. Fewer than two factors

```python
empty_pairwise = pairwise_interaction_sensitivity(
    results,
    ["factor_a"],
)

assert empty_pairwise.empty
assert list(empty_pairwise.columns) == [
    "factor_a",
    "factor_b",
    "n_cells",
    "interaction_ratio",
    "max_abs_interaction",
]
```

Interpretation:

> No factor pairs were supplied to screen.

Not:

> There were no interactions.

## 6. Non-finite specification estimates fail closed

```python
bad = results.copy()
bad.loc[0, "estimate"] = float("nan")

# Each of these raises ValueError:
# specification_curve(bad)
# effect_stability(bad)
# marginal_sensitivity(bad, ["factor_a", "factor_b"])
# pairwise_interaction_sensitivity(bad, ["factor_a", "factor_b"])
```

This is different from core `run_specs()`, which can return a `NaN` endpoint because `float("nan")` is valid Python.

Reconcile non-finite branch evidence before robustness summaries.

---

# Part B · Controlled sampling sensitivity

Create a tiny six-row study:

```python
import pandas as pd

from gazeaudit import GazeStudy, sampling_sensitivity_curve

study = GazeStudy(
    pd.DataFrame(
        {
            "participant": ["P01"] * 6,
            "trial": [1] * 6,
            "timestamp": [0, 10, 20, 30, 40, 50],
            "x": [100, 101, 102, 103, 104, 105],
            "y": [200, 201, 202, 203, 204, 205],
        }
    )
)

sampling = sampling_sensitivity_curve(
    study,
    [100, 50],
    endpoint=lambda current: float(len(current.data)),
    timestamp_unit="ms",
)
```

Exact teaching output:

| `target_hz` | `n_rows` | `retained_fraction` | `estimate` |
|---:|---:|---:|---:|
| 100 | 6 | 1.0 | 6.0 |
| 50 | 3 | 0.5 | 3.0 |

At 50 Hz, the target interval is 20 ms and existing samples nearest the ideal grid are retained.

No gaze coordinates are interpolated.

### Interpretation

The endpoint in this teaching example is simply retained row count.

The function demonstrates controlled temporal thinning—not a physical simulation of another tracker.

---

# Part C · Controlled missingness sensitivity

Use the same complete six-row study.

```python
from gazeaudit import (
    missingness_sensitivity_curve,
    summarize_missingness,
)

missing = missingness_sensitivity_curve(
    study,
    [0.0, 0.5],
    endpoint=lambda current: float(
        summarize_missingness(current)["missing_fraction"]
    ),
    mechanism="mcar",
    rng=123,
)
```

Because the original study has no missing coordinates:

| `requested_fraction` | `mechanism` | `observed_missing_fraction` | `n_missing` | `estimate` |
|---:|---|---:|---:|---:|
| 0.0 | mcar | 0.0 | 0 | 0.0 |
| 0.5 | mcar | 0.5 | 3 | 0.5 |

### Interpretation

Requested and observed missingness happen to match here because the baseline table is complete.

With pre-existing missingness, observed total missingness can be larger than the newly requested injected fraction.

Do not infer that real missingness is MCAR.

---

# Part D · Controlled spatial-error sensitivity

Create two points and one target AOI:

```python
import numpy as np

from gazeaudit import (
    GaussianGazeErrorModel,
    RectangleAOI,
    spatial_sensitivity_curve,
)

points = np.array(
    [
        [50.0, 50.0],
        [99.0, 50.0],
    ]
)

aoi = RectangleAOI(
    "target",
    0.0,
    0.0,
    100.0,
    100.0,
)

error_model = GaussianGazeErrorModel(
    mean_error=np.array([0.0, 0.0]),
    covariance=np.array(
        [
            [25.0, 0.0],
            [0.0, 25.0],
        ]
    ),
    n_validation=20,
)

spatial_1 = spatial_sensitivity_curve(
    points,
    [aoi],
    error_model,
    [0.0, 1.0],
    durations=np.array([100.0, 100.0]),
    draws=2000,
    rng=42,
)

spatial_2 = spatial_sensitivity_curve(
    points,
    [aoi],
    error_model,
    [0.0, 1.0],
    durations=np.array([100.0, 100.0]),
    draws=2000,
    rng=42,
)

assert spatial_1.equals(spatial_2)
```

Expected columns:

```text
sd_scale
aoi
expected_fixation_count
mean_flip_probability
mean_boundary_risk
expected_dwell
```

There are two rows:

```text
2 sd_scales × 1 AOI = 2 rows
```

At `sd_scale=0`, covariance collapses to zero under the declared model scale.

At `sd_scale=1`, the original covariance is retained.

The exact Monte Carlo values are deterministic for this fixed seed and draw count, but they are not scientific target values to copy into another study.

### Interpretation

The second point lies near the AOI boundary, so the spatial-error perturbation is designed to expose membership sensitivity there.

The curve does not claim that `sd_scale=1` or any other scale is empirically correct for a real participant/session without validation evidence.

---

# Part E · Put the evidence into bounded prose

## Methods

> We first reconciled the represented finite specification results, then inspected the ordered specification curve and descriptive effect-stability summaries relative to a prespecified null. Marginal and pairwise sensitivity diagnostics were used as descriptive screens for factor-level and non-additive variation. Spatial-error, sampling-rate, and missingness perturbations were analysed separately as controlled sensitivity experiments with fixed seeds where stochastic simulation was used.

## Results

> In the four-specification teaching table, estimates ranged from 1 to 9 with median 4.0. All four estimates were positive relative to zero. Descriptive marginal sensitivity was larger for factor A (0.714) than factor B (0.257), while the pairwise interaction-sensitivity ratio was 0.029. Controlled sampling from 100 to 50 Hz reduced retained rows from 6 to 3 in the separate representation exercise.

## Limitations

> The specification summaries are descriptive properties of the represented analytical choices, not inferential intervals or causal variance decompositions. The controlled perturbations are synthetic stress tests and do not establish another tracker's measurement behavior or the study's true missingness/error process.

## Diagnostic checklist for this example

- [x] represented endpoint values finite;
- [x] common endpoint within the specification table;
- [x] null stated explicitly;
- [x] quantiles described as empirical;
- [x] sign and magnitude separated;
- [x] marginal ratios not interpreted causally;
- [x] pairwise ratio not called an inferential interaction;
- [x] sampling described as nearest-existing-sample retention;
- [x] requested and observed missingness distinguished;
- [x] spatial Monte Carlo seed recorded;
- [x] controlled perturbations kept separate from the discrete specification table.

## API links

- [`specification_curve()`]({{ '/docs/reference/api-pathways/#api-specification-curve' | relative_url }})
- [`effect_stability()`]({{ '/docs/reference/api-pathways/#api-effect-stability' | relative_url }})
- [`marginal_sensitivity()`]({{ '/docs/reference/api-pathways/#api-marginal-sensitivity' | relative_url }})
- [`pairwise_interaction_sensitivity()`]({{ '/docs/reference/api-pathways/#api-pairwise-interaction-sensitivity' | relative_url }})
- [`sampling_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-sampling-sensitivity-curve' | relative_url }})
- [`missingness_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-missingness-sensitivity-curve' | relative_url }})
- [`spatial_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-spatial-sensitivity-curve' | relative_url }})
- [Robustness Diagnostics & Sensitivity Center]({{ '/docs/diagnostics/' | relative_url }})
- [Interpret robustness and sensitivity diagnostics]({{ '/docs/guides/diagnostic-interpretation/' | relative_url }})

## Reuse boundary

Reuse:

- finite-result guard;
- diagnostic sequence;
- exact interpretation distinctions;
- controlled-perturbation separation;
- reporting structure.

Rebuild:

- endpoint;
- scientific null;
- factors/levels;
- perturbation values;
- AOIs;
- error model;
- seeds/replicate design;
- substantive magnitude criteria.
