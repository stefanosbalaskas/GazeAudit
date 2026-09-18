---
title: AOI boundary example
description: A complete synthetic example of probabilistic AOI membership near a shared boundary.
kicker: Example · Measurement uncertainty
search_category: Example
page_type: example
example_data: "Synthetic"
example_focus: "Measurement uncertainty"
example_reuse: "Uncertainty workflow"
example_output: "Probabilistic AOI membership and uncertainty-aware summaries"
example_boundary: "Synthetic geometry and error values are not empirical calibration evidence."
---

# AOI boundary example

This example is fully synthetic. It demonstrates the mechanics of fitting a gaze-error model, defining adjacent AOIs, propagating measurement uncertainty, and auditing hard versus probabilistic membership.

## Complete example

```python
import numpy as np
import pandas as pd

from gazeaudit import (
    GaussianGazeErrorModel,
    RectangleAOI,
    aoi_probabilities,
    compare_hard_probabilistic,
    expected_dwell,
    summarize_aoi_risk,
)

# Synthetic validation observations around one target.
validation = pd.DataFrame(
    {
        "observed_x": [501.0, 500.0, 499.0, 502.0, 498.0, 501.5],
        "observed_y": [400.0, 399.0, 401.0, 400.0, 402.0, 398.5],
        "target_x": [500.0] * 6,
        "target_y": [400.0] * 6,
    }
)

error_model = GaussianGazeErrorModel.fit(validation)

# Two adjacent AOIs share the x = 500 edge.
aois = [
    RectangleAOI("claim", 450, 350, 500, 450),
    RectangleAOI("price", 500, 350, 550, 450),
]

# Synthetic fixation centroids and durations.
points = np.array(
    [
        [500.0, 400.0],
        [492.0, 401.0],
        [508.0, 397.0],
        [470.0, 410.0],
    ]
)

durations_ms = np.array([180.0, 220.0, 160.0, 250.0])

probabilities = aoi_probabilities(
    points,
    aois,
    error_model,
    draws=5000,
    rng=42,
)

comparison = compare_hard_probabilistic(
    points,
    aois,
    error_model,
    draws=5000,
    rng=42,
)

risk = summarize_aoi_risk(comparison)

claim_dwell = expected_dwell(
    probabilities,
    durations=durations_ms,
    aoi="claim",
)

price_dwell = expected_dwell(
    probabilities,
    durations=durations_ms,
    aoi="price",
)

print("Error-model bias:", error_model.mean_error)
print("Error-model covariance:\n", error_model.covariance)
print("\nAOI probabilities:\n", probabilities)
print("\nHard/probabilistic comparison:\n", comparison)
print("\nAOI risk summary:\n", risk)
print("\nExpected claim dwell (ms):", claim_dwell)
print("Expected price dwell (ms):", price_dwell)
```

## What to inspect

### The fixation on the boundary

The first synthetic fixation is observed exactly at x = 500. Depending on AOI boundary semantics, hard membership may assign it to one or both adjacent rectangles. Probabilistic membership instead asks how often latent true positions implied by the fitted error model fall inside each AOI.

<figure class="plot-card">
  <img src="{{ '/assets/images/aoi-boundary-uncertainty.svg' | relative_url }}" alt="Synthetic AOI boundary uncertainty illustration">
  <figcaption>The figure is explanatory rather than the literal numeric output of the code block.</figcaption>
</figure>

### Flip probability

For each observation × AOI row, `flip_probability` is the probability that latent true membership differs from the deterministic membership assigned to the observed coordinate.

### Boundary risk

`boundary_risk` rescales binary membership ambiguity to `[0, 1]`:

- near 0: membership is essentially certain in or out under the declared model;
- near 1: membership probability is near 0.5 and the hard label is maximally boundary-sensitive.

### Expected dwell

`expected_dwell()` weights each fixation duration by AOI membership probability. It does not relabel the fixation first and then sum durations.

## Reproducibility notes

- The seed is fixed (`rng=42`) so the Monte Carlo path is reproducible.
- Increasing `draws` reduces Monte Carlo noise but does not validate the Gaussian error assumption.
- The validation data and AOI geometry are synthetic.
- For a real study, store the validation source, model assumptions, AOI geometry, draw count, seed strategy, and software version with the analysis.

## Extend the example

Try moving the first fixation from `[500, 400]` to `[495, 400]` and `[505, 400]`. The hard classification can change abruptly, while probabilistic membership should usually change more smoothly under a fixed error model.

Then continue to the [measurement audit workflow]({{ '/docs/workflows/measurement-audit/' | relative_url }}) to place this calculation inside a complete study design.
