---
title: Korthals — a robust negative AOI result
description: How a frozen target-tracking AOI contrast remained negative after prespecified measurement-error propagation.
permalink: /docs/case-studies/korthals-target-tracking/
kicker: Frozen case study · measurement uncertainty
---

# Korthals target-tracking: a **robust negative** result

This case shows what GazeAudit means by propagating measurement uncertainty into a scientific endpoint without turning a measurement-model interval into a population confidence interval.

## Frozen estimand

The AOI is a target-centred circle with radius **1 dva**. The endpoint is **jumping-circle occupancy minus moving-circle occupancy**. Complete matched-cell contrasts are averaged without weighting within participants and participant estimates are then averaged without weighting at study level.

The frozen grouped isotropic Gaussian gaze-error model uses validation `error_avg`, zero bias, **2,000 Monte Carlo draws**, batch size 8, seed `20260316`, and zero as the directional reference.

<figure class="plot-card evidence-figure">
  <img src="{{ '/assets/images/korthals-effect.svg' | relative_url }}" alt="Korthals effect plot showing a hard effect of minus 0.09864 and a measurement-error expected effect of minus 0.07401 with a 95 percent measurement-model interval entirely below zero">
  <figcaption><strong>Observed frozen result.</strong> Hard and uncertainty-propagated effects differ in magnitude but retain the same negative direction. The interval shown is induced by the prespecified measurement model.</figcaption>
</figure>

## Authoritative numbers

| Quantity | Frozen result |
|---|---:|
| Observations | 448,336 |
| Retained trials | 999 |
| Monte Carlo draws | 2,000 |
| Hard effect | −0.0986408756 |
| Expected membership effect | −0.0740075674 |
| Monte Carlo SD | 0.0013013517 |
| 95% measurement-model interval | [−0.0765249127, −0.0714615962] |
| Probability below zero | 1.0 |
| Probability above zero | 0.0 |
| Classification | `robust_negative` |

The predeclared rule assigns `robust_negative` when the hard effect is negative and at least 95% of measurement-error draws are below zero. **All 2,000 draws were below zero.**

## What changed after propagating measurement uncertainty?

The estimated magnitude moved toward zero: from approximately **−0.09864** under hard binary membership to **−0.07401** under expected probabilistic membership. That shift is substantively useful. A stable direction does not imply that deterministic AOI assignment and uncertainty-aware assignment are numerically interchangeable.

The scientific statement is intentionally narrow:

> Under the frozen paired AOI estimand, target-centred 1-dva occupancy was lower for jumping circles than for moving circles, and the negative direction remained stable under the prespecified measurement-error propagation model.

<div class="callout callout-info">
  <strong>Inferential boundary.</strong> The 95% interval is a measurement-model-induced interval. It is not a population confidence interval, Bayesian posterior interval, or causal-effect interval. The Monte Carlo sign probabilities describe uncertainty induced by the frozen measurement model; they are not population p-values.
</div>

## Why this matters for practice

Hard AOI membership can hide boundary uncertainty even when the final sign is stable. For a new study, the useful question is therefore not merely whether a probabilistic analysis changes significance. Ask how the endpoint moves, which observations drive uncertainty, and whether the declared scientific conclusion survives the measurement model you justified before inspecting the result.

## Provenance snapshot

- Scientific workflow: `korthals-scientific-execution #1`
- Execution commit: `3312423cb43b1d9da3877914455dd471aba81174`
- Protocol-v2 fingerprint: `1cd4150c9341db145b8f6aee544f9634c67c46116e61e7e675ae3c50282d2d55`
- Artifact ID: `10306308440`
- ZIP SHA-256: `2eaab8171d9d5f70e138eb929554648cb6bed10b21646ab0acd7cfae4d607d11`
- Audit scientific fingerprint: `aa4c04af9c011fe997ef107c8250b20d6a20824b180abdeb16871b5b5a2fc768`

## Authoritative source

This page is an explanatory view. The frozen authority is the [Korthals protocol-v2 result]({{ '/docs/results/korthals2026_target_tracking_aoi_v2.html' | relative_url }}) and the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}).
