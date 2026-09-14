---
title: Getting started
description: Install GazeAudit and run a minimal uncertainty-aware AOI analysis.
kicker: Start
---

# Getting started

This page takes you from installation to a small uncertainty-aware AOI analysis using only NumPy, pandas, and GazeAudit.

## 1. Install the public release

```bash
python -m pip install gazeaudit==0.1.0
```

Confirm the installed package:

```bash
python -c "import gazeaudit; print(gazeaudit.__version__)"
```

The package metadata for release `0.1.0` supports Python 3.10–3.13.

### Optional interoperability extras

Install only the adapter family you need:

```bash
python -m pip install "gazeaudit[pymovements]==0.1.0"
```

For pEYES integration, Python 3.12+ is required by the current pEYES dependency range:

```bash
python -m pip install "gazeaudit[peyes]==0.1.0"
```

## 2. Fit a transparent gaze-error model

A `GaussianGazeErrorModel` treats validation residuals as observed-minus-target x/y error. The model stores estimated systematic bias and the residual covariance matrix.

```python
import pandas as pd

from gazeaudit import GaussianGazeErrorModel

validation = pd.DataFrame(
    {
        "observed_x": [501, 500, 499, 502],
        "observed_y": [400, 399, 401, 400],
        "target_x": [500, 500, 500, 500],
        "target_y": [400, 400, 400, 400],
    }
)

error_model = GaussianGazeErrorModel.fit(validation)

print(error_model.mean_error)
print(error_model.covariance)
```

<div class="callout warning">
<strong>Model boundary</strong>
The global Gaussian model is deliberately transparent and assumption-bound. It does not claim that gaze error is universally Gaussian, isotropic, spatially stationary, or constant across participants and sessions.
</div>

## 3. Define AOIs

Rectangle and circle AOIs are available as lightweight primitives.

```python
from gazeaudit import RectangleAOI

aois = [
    RectangleAOI("claim", 450, 350, 500, 450),
    RectangleAOI("price", 500, 350, 550, 450),
]
```

Here the two rectangles share a boundary at x = 500. A conventional hard assignment has to decide which side owns a fixation observed on or near that boundary.

## 4. Propagate measurement uncertainty

```python
import numpy as np

from gazeaudit import aoi_probabilities

fixations = np.array(
    [
        [500.0, 400.0],
        [490.0, 405.0],
    ]
)

probabilities = aoi_probabilities(
    fixations,
    aois,
    error_model,
    draws=4000,
    rng=42,
)

print(probabilities)
```

Each AOI column is a **marginal membership probability**. AOIs may overlap, so AOI probabilities are not required to sum to one. When `include_outside=True` (the default), the result also contains the probability that a latent true point belongs to none of the supplied AOIs.

<figure class="plot-card">
  <img src="{{ '/assets/images/aoi-boundary-uncertainty.svg' | relative_url }}" alt="Illustration of probabilistic AOI membership near a shared boundary">
  <figcaption>The values in this figure are synthetic illustrations. The important idea is the representation: boundary ambiguity is retained rather than discarded.</figcaption>
</figure>

## 5. Convert probabilities to an endpoint

If fixation durations are available, use expected dwell instead of a hard AOI sum:

```python
from gazeaudit import expected_dwell

durations_ms = np.array([180.0, 220.0])

claim_dwell = expected_dwell(
    probabilities,
    durations=durations_ms,
    aoi="claim",
)

print(claim_dwell)
```

The same measurement-error model can then be scaled or grouped in a sensitivity analysis rather than treated as unquestionable truth.

## 6. Compare hard and probabilistic assignments

`compare_hard_probabilistic()` takes the observed points, AOIs, and fitted error model and returns one row per observation × AOI, including hard membership, probabilistic membership, flip probability, and boundary risk.

```python
from gazeaudit import compare_hard_probabilistic, summarize_aoi_risk

comparison = compare_hard_probabilistic(
    fixations,
    aois,
    error_model,
    draws=4000,
    rng=42,
)

risk = summarize_aoi_risk(comparison)

print(comparison)
print(risk)
```

The comparison is useful for identifying observations whose substantive contribution changes when spatial uncertainty is acknowledged. The `high_risk_threshold` used by `summarize_aoi_risk()` is a descriptive reporting threshold, not a universal exclusion rule.

## 7. Move from one pipeline to a decision space

A single uncertainty-aware analysis is still only one analytical specification. When multiple scientifically defensible choices exist, define them explicitly with `PipelineSpace` and evaluate a common endpoint across all valid combinations.

Continue with the [specification-space guide](guides/specification-space/) or jump directly to the [specification-curve example](examples/specification-curve/).

## Recommended learning path

<div class="workflow-steps">
  <div class="workflow-step"><strong>AOI uncertainty</strong><p>Understand error models, grouped error models, probabilistic membership, and boundary risk.</p></div>
  <div class="workflow-step"><strong>Specification spaces</strong><p>Declare the analytical decisions that could reasonably vary before looking for a preferred result.</p></div>
  <div class="workflow-step"><strong>Sensitivity curves</strong><p>Perturb spatial error, sampling, and missingness when those dimensions matter to the scientific endpoint.</p></div>
  <div class="workflow-step"><strong>Publication audits</strong><p>Bind the declared rule, specifications, results, methods wording, provenance, and fingerprints into a reproducible record.</p></div>
</div>
