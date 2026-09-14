---
title: Measurement uncertainty is a modelling problem
description: Why gaze coordinates, AOI boundaries, and validation error should be treated as part of the scientific model.
kicker: Article · Measurement
---

# Measurement uncertainty is a modelling problem

Eye-tracking analysis often begins as if every recorded gaze coordinate were the true point of regard. That assumption is convenient, but it is stronger than the measurement process warrants.

A recorded point is the output of hardware, calibration, validation, signal processing, coordinate transformations, participant behaviour, and study geometry. The distance between the recorded coordinate and the latent point we would ideally like to know is therefore part of the measurement problem—not merely a nuisance to mention in a limitations paragraph.

## Why AOI boundaries are especially sensitive

A continuous coordinate can be converted into a categorical AOI label by a single boundary test:

```text
x < boundary  -> AOI A
x >= boundary -> AOI B
```

That transformation is discontinuous. A tiny displacement can produce a categorical change even when the underlying scientific difference between the two points is negligible.

This is why a fixation near an AOI boundary is methodologically different from one located deep inside a large AOI. The same nominal tracker error can have very different inferential consequences depending on geometry.

<figure class="plot-card">
  <img src="{{ '/assets/images/aoi-boundary-uncertainty.svg' | relative_url }}" alt="Synthetic illustration of probabilistic AOI membership near a boundary">
  <figcaption>Near a boundary, the question is not only “where was the coordinate recorded?” but also “how sensitive is AOI membership to plausible measurement error?”</figcaption>
</figure>

## Validation information is evidence, not decoration

Calibration and validation results are often reported as quality-control summaries and then dropped from the analysis. GazeAudit instead treats validation information as potential input to an explicit measurement-error model.

For the MVP global Gaussian model:

```text
error = observed - true
```

The fitted mean error represents estimated systematic bias and the covariance matrix represents residual spatial variability.

That model is not assumed to be universally correct. Its value is that the assumptions are visible, parameterised, and therefore testable through sensitivity analysis.

## Probabilistic AOI membership changes the representation

A deterministic AOI label asks whether the **observed** point is inside a shape.

A probabilistic AOI analysis asks what fraction of latent true positions implied by the declared measurement model would fall inside the shape.

The result is not a claim that one sampled latent location is “the truth”. It is a representation of uncertainty conditional on the model.

This distinction matters:

- hard membership hides measurement ambiguity;
- probabilistic membership exposes ambiguity;
- model sensitivity exposes how much that ambiguity depends on the assumed error model.

## More Monte Carlo draws do not validate the model

A common misunderstanding is to equate simulation precision with scientific validity. If 2,000 draws produce a noisy probability estimate, 20,000 draws can make that probability estimate more numerically stable.

But if the error model is poorly chosen, 20,000 draws simply estimate the wrong model more precisely.

A complete uncertainty analysis therefore separates:

1. **Monte Carlo error** — finite simulation noise;
2. **parameter uncertainty** — uncertainty in estimated model parameters;
3. **model uncertainty** — whether the chosen error structure is an adequate scientific representation;
4. **analytical uncertainty** — whether downstream pipeline choices change the endpoint.

GazeAudit 0.1.0 addresses the first layer directly and provides transparent global/grouped model structures and sensitivity tools for parts of the latter layers. It does not claim to solve every form of measurement uncertainty.

## Why grouped models matter

A pooled tracker-wide error model may be convenient but can erase meaningful heterogeneity. Validation quality may differ across participants, sessions, devices, or calibration blocks.

`GroupedGaussianGazeErrorModel` allows separate declared models and fails closed when an observation cannot be mapped to one of them. That behaviour is scientifically important: silent fallback would turn missing measurement provenance into an unreported modelling decision.

## The endpoint is where measurement uncertainty becomes scientific

Measurement uncertainty matters only insofar as it changes the scientific quantity of interest.

For example, a participant may have several boundary-sensitive fixations, but the condition contrast could still be stable. Conversely, only a few high-weight observations may be enough to alter the endpoint materially.

The useful question is therefore not:

> How inaccurate is the tracker?

but:

> Under a defensible model of measurement error, how much does uncertainty propagate into the endpoint and conclusion?

## What a careful measurement audit reports

A defensible report should state:

- where validation information came from;
- how error was defined;
- whether the model was global or grouped;
- the model assumptions;
- the Monte Carlo draw count and seed strategy;
- AOI geometry and overlap semantics;
- the hard-versus-probabilistic discrepancy pattern;
- the endpoint derived from probabilistic membership;
- sensitivity to plausible changes in error magnitude or structure;
- unmodelled sources of uncertainty.

## The broader methodological point

Measurement quality should not be reduced to a single tracker accuracy number. The inferential effect of measurement error depends on the interaction among error, geometry, task, endpoint, and analytical pipeline.

That is why GazeAudit treats measurement uncertainty as a first-class part of the scientific model and then asks whether the final conclusion survives it.

Continue with the [AOI uncertainty guide](../guides/aoi-uncertainty/) or the [measurement audit workflow](../workflows/measurement-audit/).
