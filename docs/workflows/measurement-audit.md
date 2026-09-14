---
title: Measurement audit workflow
description: End-to-end workflow for fitting gaze-error models, propagating AOI uncertainty, and stress-testing measurement assumptions.
kicker: Workflow · Measurement uncertainty
---

# Measurement audit workflow

Use this workflow when the scientific endpoint depends on gaze position, AOI membership, or a spatial decision boundary that could plausibly be affected by tracker error.

## Workflow overview

<div class="workflow-steps">
  <div class="workflow-step"><strong>Preserve validation evidence</strong><p>Retain pointwise target/observed coordinates when available; otherwise preserve the exact summary from which an approximation is constructed.</p></div>
  <div class="workflow-step"><strong>Declare the error model</strong><p>Choose global versus grouped structure and document the assumptions before inspecting downstream endpoint sensitivity.</p></div>
  <div class="workflow-step"><strong>Propagate to AOIs</strong><p>Use Monte Carlo latent positions to estimate marginal membership probabilities for every declared AOI.</p></div>
  <div class="workflow-step"><strong>Audit boundary risk</strong><p>Compare deterministic and probabilistic membership and identify observations with high flip probability or ambiguity.</p></div>
  <div class="workflow-step"><strong>Propagate to the endpoint</strong><p>Calculate uncertainty-weighted dwell, fixation count, or a study-specific effect from the probabilistic memberships.</p></div>
  <div class="workflow-step"><strong>Stress-test the model</strong><p>Scale or stratify the error model and inspect whether the scientific conclusion depends materially on the measurement assumption.</p></div>
</div>

## 1. Preserve validation evidence

Preferred input is pointwise validation data containing observed and target x/y coordinates. This allows `GaussianGazeErrorModel.fit()` to estimate systematic bias and residual covariance directly.

If only mean radial error is available, the package can construct an isotropic approximation, but the conversion is assumption-driven and should be reported as such.

For participant-, session-, device-, or block-specific validation evidence, use a grouped model rather than pooling automatically.

## 2. Fit the declared model

```python
from gazeaudit import GaussianGazeErrorModel

error_model = GaussianGazeErrorModel.fit(validation)
```

Record at least:

- error definition (`observed - true`);
- validation source;
- number of complete validation observations;
- fitted mean error;
- fitted covariance;
- grouping structure if used;
- any approximation from radial summaries.

## 3. Propagate to AOI membership

```python
from gazeaudit import aoi_probabilities

probabilities = aoi_probabilities(
    points,
    aois,
    error_model,
    draws=5000,
    rng=42,
)
```

The draw count governs Monte Carlo precision under the model. It does not express confidence that the model itself is correct.

## 4. Audit boundary risk

```python
from gazeaudit import compare_hard_probabilistic, summarize_aoi_risk

comparison = compare_hard_probabilistic(
    points,
    aois,
    error_model,
    draws=5000,
    rng=42,
)

risk_summary = summarize_aoi_risk(comparison)
```

Inspect where hard membership is most likely to flip under the declared measurement model. High-risk observations are not automatically invalid; they are observations whose interpretation is especially dependent on the measurement assumption.

## 5. Propagate uncertainty into the endpoint

```python
from gazeaudit import expected_dwell

weighted_dwell = expected_dwell(
    probabilities,
    durations=durations_ms,
    aoi="target",
)
```

For study-level inference, the endpoint may be a contrast constructed after aggregating probabilistic dwell or fixation contributions. Keep the endpoint definition fixed while measurement assumptions vary.

## 6. Stress-test spatial error

Use `scale_error_model()` or `spatial_sensitivity_curve()` when the magnitude of spatial error itself is uncertain or when you want to show how conclusions change under controlled scaling.

A useful design is to include the fitted model as the reference scale and evaluate smaller/larger plausible scales around it. The scale grid should be justified before inspecting which value produces the preferred result.

<figure class="plot-card">
  <img src="{{ '/assets/images/sensitivity-curves.svg' | relative_url }}" alt="Synthetic sensitivity curves under increasing perturbation">
  <figcaption>Generic synthetic illustration. A real measurement audit should display the actual endpoint curve and the declared perturbation scale.</figcaption>
</figure>

## 7. Decide whether measurement uncertainty is substantively important

Useful questions include:

- Does the sign of the endpoint change?
- Does the magnitude change enough to alter the substantive interpretation?
- Are only a small number of boundary observations driving the difference?
- Is sensitivity concentrated in one participant/session/device group?
- Does hard-versus-probabilistic disagreement align with the scientific contrast?
- Does the conclusion remain stable when the error magnitude is scaled within a plausible range?

## 8. Preserve the evidence

For formal work, archive:

- validation data or immutable source identity;
- fitted error-model parameters;
- AOI geometry;
- point/observation identifiers;
- Monte Carlo seed strategy and draw count;
- hard/probabilistic comparison table;
- risk summary;
- endpoint table;
- spatial sensitivity curve;
- exact GazeAudit version/commit.

## Failure modes to avoid

### Treating validation error as a universal constant

A single tracker-wide accuracy number may not represent participant/session-specific uncertainty. Use grouped models when the design and evidence justify them.

### Increasing draws instead of questioning the model

More Monte Carlo draws reduce simulation noise. They do not solve model misspecification.

### Excluding high-risk observations automatically

Boundary risk is diagnostic. It is not a universal QC rule.

### Comparing different endpoints across models

If the scientific endpoint changes definition when the error model changes, measurement sensitivity and endpoint redefinition become confounded.

## Next

If multiple analytical choices exist beyond the measurement model, continue to the [robustness audit workflow](robustness-audit/). For publication-grade provenance, finish with the [reproducible publication workflow](reproducible-publication/).
