---
title: Pedrotti/de Chambrier — a materially fragile endpoint
description: Sampling-rate and missingness sensitivity for the frozen long-minus-short gaze-path-rate contrast.
permalink: /docs/case-studies/pedrotti-sensitivity/
kicker: Frozen case study · sampling and missingness
---

# Pedrotti/de Chambrier: a **materially fragile** endpoint

This case separates **directional stability** from **magnitude recovery**. The frozen long-minus-short gaze-path-rate contrast remained negative throughout the sampling analysis, yet several perturbations exceeded the predeclared 20% relative-deviation tolerance.

## Frozen estimand

The endpoint is the participant-balanced **long-minus-short numeric gaze-path-rate difference**, in pixels per second. Trial path displacement is divided by original trial duration, short and long numeric means are formed within participant, their difference is computed, and participant contrasts are averaged without weighting at study level.

Native missingness is preserved. Displacement is accumulated only across consecutive scheduled rows whose two gaze endpoints are finite; gaps are not bridged.

The frozen reference estimate is **−75.3781404722 px/s**.

## Sampling-rate sensitivity

<figure class="plot-card evidence-figure">
  <img src="{{ '/assets/images/pedrotti-sampling-sensitivity.svg' | relative_url }}" alt="Pedrotti sampling sensitivity plot showing recovery at 500 and 250 hertz and non-recovery at 125, 100, and 50 hertz while all estimates remain negative">
  <figcaption><strong>Observed frozen result.</strong> The sign remained negative at every target rate. Recovery failed at 125, 100, and 50 Hz because the magnitude moved outside the prespecified ±20% relative-deviation tolerance.</figcaption>
</figure>

| Target rate | Estimate (px/s) | Relative deviation | Same sign | Recovered |
|---:|---:|---:|:---:|:---:|
| 500 Hz | −74.5618 | 1.08% | yes | yes |
| 250 Hz | −66.3495 | 11.98% | yes | yes |
| 125 Hz | −47.4680 | 37.03% | yes | no |
| 100 Hz | −46.2298 | 38.67% | yes | no |
| 50 Hz | −20.5618 | 72.72% | yes | no |

Sampling-family recovery is therefore **0.4**.

## Added-missingness sensitivity

<figure class="plot-card evidence-figure">
  <img src="{{ '/assets/images/pedrotti-missingness-recovery.svg' | relative_url }}" alt="Recovery fraction plot for MCAR and single-block missingness at 1, 5, 10, and 20 percent added missingness">
  <figcaption><strong>Observed frozen result.</strong> Recovery remains complete at low MCAR levels but falls sharply with 10–20% perturbation. Single-block missingness is already less stable at 5%.</figcaption>
</figure>

| Mechanism | 1% | 5% | 10% | 20% |
|---|---:|---:|---:|---:|
| MCAR within trial | 1.00 | 1.00 | 0.40 | 0.00 |
| Single block within trial | 1.00 | 0.55 | 0.40 | 0.00 |

Each family contains **20 prespecified deterministic replicates** generated from root seed `20260913`.

## Why the classification is `materially_fragile`

The frozen individual-recovery rule requires both:

1. strict sign agreement with the reference estimate; and
2. no more than 20% relative deviation in magnitude.

The full audit is classified `materially_fragile` when any frozen perturbation family reaches the predeclared material-fragility ceiling. Several families recovered at **0.4** or **0.0**, so the rule necessarily returns `materially_fragile`.

<div class="callout callout-warning">
  <strong>Do not paraphrase this as sign reversal.</strong> Every sampling-rate estimate remained negative. The fragility concerns recovery of the declared magnitude-and-direction criterion, not a switch from negative to positive.
</div>

## What to learn from this case

A stable sign can coexist with scientifically important dependence on measurement resolution and missing-data structure. For rate-like eye-tracking endpoints, downsampling can change the amount of path displacement observed per unit time even when the broad ordering of conditions is unchanged.

That is why sensitivity analysis should report **how far** the endpoint moves, not merely whether a coefficient keeps its sign or a test remains significant.

## Provenance snapshot

- Scientific workflow: `pedrotti-scientific-execution #1`
- Execution commit: `270d444c599363ebd25f25e8a95f5f3c78e55b02`
- Protocol fingerprint: `efb194ad2c492768962320198d281c98574eb2dc22291279bfd176a15606a0d5`
- Artifact ID: `10328414078`
- ZIP SHA-256: `b411fe6a5f4ad7035ac606d60a952306c0b818d956f7b4930827b8cbe10ae8d5`
- Results fingerprint: `5bafe0d1d1d0d054a681cb7136fc4e259c0f75e07d51653acde472c7c6e4dce9`

## Authoritative source

This page is an explanatory view. The frozen authority is the [Pedrotti/de Chambrier authoritative result]({{ '/docs/results/pedrotti_sampling_missingness_v1.html' | relative_url }}) and the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}).
