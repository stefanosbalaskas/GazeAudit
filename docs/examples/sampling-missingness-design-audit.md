---
title: Sampling & missingness design audit
description: A fully synthetic worked exercise linking GazeAudit sampling and missingness runtime contracts to exact row-retention, missingness, reproducibility, interpretation, reporting, and limitation decisions.
kicker: Example · Controlled sensitivity
page_type: example
permalink: /docs/examples/sampling-missingness-design-audit/
search_category: Example
search_keywords: sampling missingness downsample MCAR block seed retained fraction observed missingness sensitivity curve synthetic
example_data: "Synthetic"
example_focus: "Robustness & sensitivity"
example_reuse: "Sampling/missingness perturbation declaration, denominator, reproducibility, and reporting pattern"
example_output: "Exact lower-rate row retention plus reproducible controlled missingness summaries"
example_boundary: "Synthetic target rates, fractions, mechanisms, and seeds are teaching choices and are not recommended settings for another study."
---

# Sampling & missingness design audit

This fully synthetic exercise demonstrates four contracts:

1. lower-rate sampling retains existing source rows and does not interpolate;
2. added missingness acts only on currently complete gaze rows;
3. a seed makes the benchmark perturbation reproducible but does not make it empirically realistic;
4. sampling and added missingness are interpreted as separate sensitivity families.

<div class="callout warning">
<strong>Do not reuse the numerical settings.</strong>
The rates, fractions, mechanisms, and seeds below are chosen to make the runtime behavior easy to inspect in a tiny fixture.
</div>

## Part A · Exact nearest-row downsampling

Create one 100-Hz-like synthetic trial with ten rows:

```python
import numpy as np
import pandas as pd

from gazeaudit import GazeStudy

sampling_study = GazeStudy(
    pd.DataFrame(
        {
            "participant": ["P01"] * 10,
            "trial": [1] * 10,
            "timestamp": np.arange(0.0, 100.0, 10.0),
            "x": np.arange(10, dtype=float),
            "y": np.zeros(10),
        }
    )
)
```

The source timestamps are:

```text
0, 10, 20, 30, 40, 50, 60, 70, 80, 90 ms
```

### Downsample to 50 Hz

```python
from gazeaudit import downsample_gaze

down50 = downsample_gaze(
    sampling_study,
    50.0,
    timestamp_unit="ms",
)

print(down50.data["timestamp"].tolist())
```

The live runtime contract retains:

```text
[0.0, 20.0, 40.0, 60.0, 80.0]
```

No coordinate was interpolated.

The output has five rows.

The original study still has ten rows.

## Part B · Sampling sensitivity with one common endpoint

Use the mean x coordinate only as a transparent teaching endpoint:

```python
def endpoint(current):
    return float(current.data["x"].mean())
```

Now evaluate 100 and 50 Hz:

```python
from gazeaudit import sampling_sensitivity_curve

sampling_curve = sampling_sensitivity_curve(
    sampling_study,
    target_rates=[100.0, 50.0],
    endpoint=endpoint,
    timestamp_unit="ms",
)

print(sampling_curve)
```

The expected deterministic result is:

| target_hz | n_rows | retained_fraction | estimate |
|---:|---:|---:|---:|
| 100 | 10 | 1.00 | 4.5 |
| 50 | 5 | 0.50 | 4.0 |

The shift from 4.5 to 4.0 is a property of this tiny teaching endpoint under this row-retention representation.

It is not evidence about a physical 50-Hz tracker.

## Why 50 Hz keeps these rows

A 50-Hz interval is 20 ms.

Starting at 0 ms, the target grid is approximately:

```text
0, 20, 40, 60, 80
```

Those positions already exist in the source table, so they are retained directly.

No new row is created.

## Part C · Observe missingness before injecting it

Create a separate 20-row complete study:

```python
missing_study = GazeStudy(
    pd.DataFrame(
        {
            "participant": ["P01"] * 10 + ["P02"] * 10,
            "trial": [1] * 20,
            "timestamp": np.arange(20, dtype=float),
            "x": np.arange(20, dtype=float),
            "y": np.arange(20, dtype=float) * 0.5,
        }
    )
)
```

Baseline summary:

```python
from gazeaudit import summarize_missingness

baseline = summarize_missingness(missing_study)
print(baseline)
```

Expected:

```text
n_rows              20
n_missing            0
missing_fraction      0
n_complete           20
```

## Part D · Reproducible MCAR benchmark masking

Add 25% missingness with a fixed seed:

```python
from gazeaudit import inject_missingness

first = inject_missingness(
    missing_study,
    0.25,
    mechanism="mcar",
    rng=123,
    reason="synthetic_benchmark",
)

second = inject_missingness(
    missing_study,
    0.25,
    mechanism="mcar",
    rng=123,
    reason="synthetic_benchmark",
)

pd.testing.assert_frame_equal(first.data, second.data)
```

The live runtime masks exactly:

```text
round(0.25 × 20 complete rows) = 5 rows
```

so:

```python
summary = summarize_missingness(first)
assert int(summary["n_missing"]) == 5
assert float(summary["missing_fraction"]) == 0.25
```

The original `missing_study` remains complete.

The reason column is provenance for the injected rows; it does not diagnose the source study's missingness mechanism.

## Part E · Reproducible block benchmark masking

Use the same complete 20-row study:

```python
block_a = inject_missingness(
    missing_study,
    0.30,
    mechanism="block",
    rng=77,
)

block_b = inject_missingness(
    missing_study,
    0.30,
    mechanism="block",
    rng=77,
)

pd.testing.assert_frame_equal(block_a.data, block_b.data)

block_summary = summarize_missingness(block_a)
assert int(block_summary["n_missing"]) == 6
```

Again, reproducibility means the same algorithm/seed recreates the same benchmark perturbation.

It does not mean block loss is the empirical data-generating process.

## Part F · Native missingness changes the denominator of added loss

Start with ten rows where one is already missing:

```python
native = pd.DataFrame(
    {
        "participant": ["P01"] * 10,
        "trial": [1] * 10,
        "timestamp": np.arange(10, dtype=float),
        "x": np.arange(10, dtype=float),
        "y": np.arange(10, dtype=float),
    }
)
native.loc[0, ["x", "y"]] = np.nan
native_study = GazeStudy(native)
```

Now request 50% added MCAR missingness:

```python
perturbed = inject_missingness(
    native_study,
    0.50,
    mechanism="mcar",
    rng=1,
)

summary = summarize_missingness(perturbed)
print(summary)
```

The request applies to nine currently complete rows:

```text
round(0.50 × 9) = 4 newly masked rows
1 native missing + 4 added = 5 missing rows total
```

So:

```python
assert int(summary["n_missing"]) == 5
assert float(summary["missing_fraction"]) == 0.5
```

The number `0.50` appears twice here but refers to different quantities:

- requested **added** fraction among complete rows;
- observed **total** missing fraction among all rows.

Do not treat those denominators as interchangeable.

## Part G · One missingness curve call gives one perturbation per fraction

```python
from gazeaudit import missingness_sensitivity_curve

def missing_endpoint(current):
    return float(current.data["x"].mean(skipna=True))

curve_a = missingness_sensitivity_curve(
    missing_study,
    fractions=[0.0, 0.25, 0.50],
    endpoint=missing_endpoint,
    mechanism="mcar",
    rng=11,
)

curve_b = missingness_sensitivity_curve(
    missing_study,
    fractions=[0.0, 0.25, 0.50],
    endpoint=missing_endpoint,
    mechanism="mcar",
    rng=11,
)

pd.testing.assert_frame_equal(curve_a, curve_b)
```

The exact missing counts are:

```text
[0, 5, 10]
```

The two curves are identical because the root seed is identical.

But each fraction still has **one perturbation realization per call**.

This is not a replicate distribution.

## Part H · Add replication only when the protocol requires it

A project may explicitly decide that multiple random realizations are necessary.

Then wrap the curve in a declared outer loop:

```python
replicate_seeds = [101, 202, 303]
rows = []

for replicate, seed in enumerate(replicate_seeds, start=1):
    curve = missingness_sensitivity_curve(
        missing_study,
        fractions=[0.10, 0.20],
        endpoint=missing_endpoint,
        mechanism="mcar",
        rng=seed,
    )
    curve["replicate"] = replicate
    curve["root_seed"] = seed
    rows.append(curve)

replicated = pd.concat(rows, ignore_index=True)
```

The seed list and replicate count are now part of the scientific perturbation declaration.

Do not add replicates post hoc until one gives a preferred endpoint.

## Part I · Sampling and missingness are separate families

Preferred structure:

```text
common baseline + common endpoint
├── sampling curve
└── missingness curve
```

Do not automatically cross:

```text
100 Hz × 0%
100 Hz × 25%
50 Hz × 0%
50 Hz × 25%
...
```

unless the scientific protocol explicitly asks about the interaction and records:

- operation order;
- fraction denominator;
- seed derivation;
- endpoint;
- interpretation.

## Part J · Non-finite endpoints fail the curve helpers

Both sensitivity-curve helpers require a finite scalar endpoint.

For example:

```python
import pytest

with pytest.raises(ValueError, match="finite scalar"):
    sampling_sensitivity_curve(
        sampling_study,
        [50.0],
        endpoint=lambda current: np.inf,
    )
```

A non-finite endpoint is not silently recoded as zero.

Preserve the failure and diagnose the declared endpoint/perturbation contract.

## Interpretation

This exercise establishes several runtime facts:

1. downsampling retains existing rows near a regular grid;
2. no gaze interpolation occurs;
3. retained fraction is observed from the output, not assumed from the target Hz;
4. added missingness acts on currently complete rows;
5. native missingness remains present;
6. the same seed recreates the same random perturbation;
7. one missingness-curve call gives one realization per fraction;
8. finite endpoint output is required by both sensitivity-curve helpers.

It does **not** establish:

- which sampling rates are scientifically sufficient;
- that empirical missingness is MCAR or blockwise;
- that another tracker would reproduce the lower-rate representation;
- that the synthetic endpoint is meaningful for a real study;
- that a particular missingness fraction should be tolerated.

## Reporting example

### Methods

> Observed coordinate missingness was quantified before perturbation. Sampling sensitivity retained existing observations nearest to the declared 100- and 50-Hz target grids using millisecond timestamps, without interpolating gaze coordinates. Added-missingness sensitivity was evaluated separately using seeded MCAR and block benchmark perturbations. The same scalar endpoint was used within each controlled sensitivity family.

### Results

> In the sampling teaching fixture, the 100-Hz representation retained 10/10 rows and yielded endpoint 4.5, whereas the 50-Hz representation retained 5/10 rows and yielded endpoint 4.0. In the missingness fixture, 25% seeded MCAR masking produced 5/20 missing rows, and 30% seeded block masking produced 6/20 missing rows. With one native missing row among 10 rows, requesting 50% added masking acted on the nine complete rows and yielded five total missing rows.

### Limitation

> These values belong only to deterministic synthetic teaching fixtures. The perturbations do not identify real missingness mechanisms, simulate another eye tracker, reconstruct lost gaze, or define acceptable sampling/missingness thresholds.

## API links

- [`downsample_gaze()`]({{ '/docs/reference/api-pathways/#api-downsample-gaze' | relative_url }})
- [`sampling_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-sampling-sensitivity-curve' | relative_url }})
- [`missingness_mask()`]({{ '/docs/reference/api-pathways/#api-missingness-mask' | relative_url }})
- [`summarize_missingness()`]({{ '/docs/reference/api-pathways/#api-summarize-missingness' | relative_url }})
- [`inject_missingness()`]({{ '/docs/reference/api-pathways/#api-inject-missingness' | relative_url }})
- [`missingness_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-missingness-sensitivity-curve' | relative_url }})
- [Sampling & Missingness Sensitivity Center]({{ '/docs/sampling-missingness/' | relative_url }})
- [Design sampling and missingness sensitivity]({{ '/docs/guides/sampling-missingness-sensitivity/' | relative_url }})

## Reuse boundary

Reuse:

- baseline-before-perturbation sequence;
- explicit endpoint identity;
- target/fraction rationale;
- timestamp-unit and mechanism declaration;
- seed/replication provenance;
- requested-versus-observed denominator distinction;
- separate-family reporting;
- non-finite endpoint guardrails.

Rebuild:

- target rates;
- missingness fractions;
- mechanism set;
- seed scheme;
- replication count;
- endpoint;
- substantive interpretation;
- acceptable-change criteria.
