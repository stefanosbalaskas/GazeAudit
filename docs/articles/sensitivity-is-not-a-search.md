---
title: Sensitivity analysis is not a search for a stable answer
description: Why defensible sensitivity analysis varies justified assumptions without using the observed endpoint to search for the most reassuring result.
kicker: Article · Sensitivity
permalink: /docs/articles/sensitivity-is-not-a-search/
search_category: Article
search_keywords: sensitivity analysis robustness perturbation specification search sampling missingness spatial error endpoint
---

# Sensitivity analysis is not a search for a stable answer

Sensitivity analysis is most informative when it asks a question defined **before the answer is known**:

> How much would the scientific endpoint change under other plausible assumptions or controlled perturbations?

That is different from repeatedly changing the analysis until a preferred conclusion becomes stable.

GazeAudit makes this distinction explicit because robustness evidence is only interpretable when the represented alternatives are scientifically defensible and the endpoint remains fixed.

## The scientific object is the perturbation protocol

A useful sensitivity protocol identifies five things before execution:

1. the baseline analysis;
2. the uncertainty dimension being perturbed;
3. the range and grid of values to evaluate;
4. the common endpoint evaluated at every value;
5. the interpretation rule used after the curve is visible.

For example, sampling-rate sensitivity can examine controlled lower-rate representations of one recorded stream. The question is whether the endpoint depends materially on temporal representation. It is not a search for the lowest rate that preserves a desired result.

Likewise, spatial-error sensitivity can perturb the scale of a declared gaze-error model. That asks how the AOI result behaves under a family of measurement assumptions. It does not establish that one scale is the true tracker error.

## A wide grid is not automatically stronger

Adding many perturbation values can make a figure look thorough while weakening the scientific rationale.

A defensible grid should reflect a plausible range supported by the study design, validation data, acquisition characteristics, prior evidence, or an explicitly labelled stress-test objective. Values chosen only because they reveal a convenient transition in the result are post-outcome exploration and should be labelled as such.

The same principle applies to specification spaces: coverage should follow the scientific decision problem, not the desire for a large multiverse.

## Keep perturbation families semantically separate

Sampling rate, missingness, spatial measurement error, detector choice, AOI definition, and readiness policy do not represent the same type of uncertainty.

A useful design often separates:

- analytical alternatives, represented as a declared specification space;
- ordered perturbations, represented as sensitivity curves;
- measurement uncertainty, represented through an explicit error model;
- execution uncertainty, preserved in the execution ledger rather than converted into an estimate.

The outputs can be discussed together, but their evidential meanings should remain distinct.

## Stable direction does not guarantee stable magnitude

Suppose every sensitivity estimate remains positive. That supports a bounded statement about direction under the represented perturbations.

It does not automatically support stable effect magnitude, equivalence across devices, robustness to untested preprocessing choices, population-level statistical certainty, or a causal explanation for why the endpoint moved.

A curve can preserve sign while changing enough in magnitude to alter the substantive interpretation.

## Fragility is an informative result

If the endpoint changes materially over a scientifically justified perturbation range, the analysis has found something important: the conclusion depends on an assumption that matters.

That can motivate narrower claims, more explicit limitations, improved calibration or validation data, stronger justification of acquisition or preprocessing decisions, or replication focused on the uncertainty dimension that mattered most.

The appropriate response is not to remove the inconvenient part of the curve.

## What to report

A compact sensitivity report should identify the baseline endpoint, perturbation dimension and rationale, evaluated range, randomness contract, estimate at every represented value, direction and magnitude changes, failures or unsupported values, and uncertainty dimensions that were not evaluated.

When the range was exploratory rather than predeclared, say so.

## Continue

Use the [Sensitivity-analysis design guide]({{ '/docs/guides/sensitivity-analysis-design/' | relative_url }}) to define a study-specific protocol, then run the [worked sensitivity protocol]({{ '/docs/examples/sensitivity-protocol/' | relative_url }}). The [robustness-audit workflow]({{ '/docs/workflows/robustness-audit/' | relative_url }}) shows how sensitivity curves relate to an ordinary specification space.
