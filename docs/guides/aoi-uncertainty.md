---
title: AOI uncertainty guide
description: Model gaze-position uncertainty and propagate it into probabilistic AOI membership and endpoints.
kicker: Guide · Measurement uncertainty
---

# AOI uncertainty guide

A gaze coordinate is an observation, not a known true point. Calibration/validation error, tracker noise, head movement, geometry, and local measurement conditions can make deterministic AOI assignment especially brittle near boundaries. GazeAudit makes that uncertainty explicit.

## The core model

For the global Gaussian model, GazeAudit defines measurement error as

`error = observed - true`.

`GaussianGazeErrorModel.fit()` estimates the mean x/y error and residual covariance from validation observations. For a new observed point, latent true locations are sampled by subtracting error draws from the observation.

```python
from gazeaudit import GaussianGazeErrorModel

model = GaussianGazeErrorModel.fit(validation_frame)
```

This is intentionally a simple, auditable model. It should be treated as a scientific assumption that can itself be stress-tested.

## When only mean radial error is available

Some validation summaries report only mean Euclidean position error. `from_mean_radial_error()` converts that summary into an isotropic Gaussian model under an explicit Rayleigh-to-Gaussian assumption:

```python
model = GaussianGazeErrorModel.from_mean_radial_error(
    mean_radial_error=28.0,
    n_validation=9,
)
```

This constructor does **not** recover anisotropy, spatial variation, or uncertainty in the reported validation summary. Use it only when that approximation is defensible and state the assumption in the methods.

## Grouped error models

When uncertainty is expected to differ across participants, sessions, calibration blocks, devices, or other predeclared strata, use `GroupedGaussianGazeErrorModel`.

```python
from gazeaudit import GroupedGaussianGazeErrorModel

grouped = GroupedGaussianGazeErrorModel.from_mean_radial_errors(
    {
        "p01": 24.0,
        "p02": 31.0,
        "p03": 19.0,
    },
    n_validation={"p01": 9, "p02": 9, "p03": 9},
)
```

Grouped models fail closed: every observation supplied to a grouped uncertainty audit must map to a declared model key. GazeAudit does not silently fall back to a pooled model when a group is missing.

## Probabilistic AOI membership

`aoi_probabilities()` draws latent true positions and calculates the fraction of draws inside each AOI.

```python
probabilities = aoi_probabilities(
    points,
    aois,
    model,
    draws=5000,
    rng=42,
)
```

With grouped models:

```python
probabilities = aoi_probabilities(
    points,
    aois,
    grouped,
    groups=participant_ids,
    draws=5000,
    rng=42,
)
```

### Important probability semantics

- AOI probabilities are **marginal membership probabilities**.
- Overlapping AOIs are allowed.
- Therefore AOI probabilities need not sum to one.
- `outside` is the probability of belonging to none of the supplied AOIs.
- Monte Carlo uncertainty can be reduced by increasing `draws`, but more draws do not make the underlying measurement model more correct.

<figure class="plot-card">
  <img src="{{ '/assets/images/aoi-boundary-uncertainty.svg' | relative_url }}" alt="Synthetic illustration of uncertainty around an AOI boundary">
  <figcaption>A hard boundary can turn small coordinate changes into categorical changes. Probabilistic membership retains the measurement ambiguity instead.</figcaption>
</figure>

## Hard versus probabilistic assignment

A useful audit is not merely to replace one metric with another but to quantify where the interpretation changes.

```python
from gazeaudit import compare_hard_probabilistic, summarize_aoi_risk

comparison = compare_hard_probabilistic(
    points,
    aois,
    model,
    draws=5000,
    rng=42,
)
risk = summarize_aoi_risk(comparison)
```

Use this comparison to ask questions such as:

- Which observations are near an AOI decision boundary?
- How often does the hard assignment disagree with the model-conditional membership probability?
- Are the scientifically important trials disproportionately boundary-sensitive?
- Does a substantive endpoint change when probability weights replace binary labels?

## Expected endpoints

GazeAudit includes uncertainty-weighted dwell and fixation-count helpers:

```python
from gazeaudit import expected_dwell, expected_fixation_count

claim_dwell = expected_dwell(
    probabilities,
    durations=durations_ms,
    aoi="claim",
)

claim_fixations = expected_fixation_count(
    probabilities,
    aoi="claim",
)
```

The result should be interpreted as an endpoint under the declared measurement-error model, not as a direct observation of latent truth.

## Sensitivity to the error model

The error model belongs inside the robustness analysis. `scale_error_model()` can generate controlled alternatives around a fitted model, and `spatial_sensitivity_curve()` evaluates a common endpoint across scales.

A practical analysis can therefore distinguish:

1. **within-model Monte Carlo uncertainty** — finite draws under a fixed error model;
2. **measurement-model sensitivity** — how the endpoint changes when the assumed error magnitude changes;
3. **analytical sensitivity** — how the endpoint changes under other defensible pipeline choices.

Conflating those layers makes it difficult to tell where instability actually comes from.

## Recommended reporting

At minimum, report:

- the source of validation information;
- the error definition and model family;
- whether the model is global or grouped;
- the number of validation observations used for each fitted model;
- the Monte Carlo draw count and random seed strategy;
- AOI geometry and overlap semantics;
- whether `outside` was retained;
- the endpoint derived from membership probabilities;
- any error-scale sensitivity analysis;
- hard-versus-probabilistic discrepancies when they affect interpretation.

<div class="callout success">
<strong>Good scientific use</strong>
Use probabilistic membership to expose sensitivity to plausible measurement error. Do not present it as proof that the sampled latent points are the unique true gaze path.
</div>

## Next

Run the [AOI boundary example]({{ '/docs/examples/aoi-boundary/' | relative_url }}) or combine AOI uncertainty with a declared analytical multiverse in the [specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }}).
