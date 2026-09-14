---
title: How to read a fragile result
description: Interpret analytical fragility as scientific information without turning robustness analysis into post-hoc optimisation.
kicker: Article · Interpretation
---

# How to read a fragile result

A robustness analysis is allowed to conclude that the result is fragile. That outcome is not a failed analysis. It is evidence that the scientific conclusion depends materially on one or more defensible measurement or analytical choices.

The useful next question is not “how do I make the result robust?” It is:

> Which assumptions carry the conclusion, and what claim remains justified after that dependence is made explicit?

## Fragility has different forms

### Directional fragility

Some defensible specifications produce positive effects and others negative effects. This is usually the strongest warning that a simple directional claim is not stable under the declared decision space.

### Magnitude fragility

The sign is stable but the size varies enough to change the substantive interpretation. A conclusion can therefore be directionally stable yet materially fragile.

### Threshold fragility

The estimate crosses a scientifically meaningful decision threshold. The threshold should be substantively justified; a p-value boundary should not automatically become the definition of scientific robustness.

### Localised fragility

Most specifications agree, but one factor level or factor interaction creates a distinct cluster of results. This is where marginal and pairwise sensitivity diagnostics are especially useful.

### Perturbation fragility

A controlled change in measurement assumptions, sampling rate, or missingness produces a systematic endpoint drift or direction change.

<figure class="plot-card">
  <img src="{{ '/assets/images/sensitivity-curves.svg' | relative_url }}" alt="Synthetic sensitivity curves showing stable and fragile patterns">
  <figcaption>Synthetic illustration. Fragility can appear as direction change, magnitude drift, or sensitivity concentrated in one perturbation family.</figcaption>
</figure>

## First locate the source

Before interpreting the fragility globally, ask where it comes from.

Useful diagnostics include:

- the complete specification curve;
- sign fractions and estimate range;
- marginal sensitivity by factor;
- pairwise interaction sensitivity;
- hard-versus-probabilistic AOI disagreement;
- spatial-error sensitivity;
- sampling-rate sensitivity;
- missingness sensitivity;
- participant/session/device grouping where scientifically justified.

The goal is to distinguish a broad instability from a narrow method-specific dependence.

## Do not delete the uncomfortable branch

If a specification was declared scientifically defensible before results were inspected, an inconvenient estimate is not a reason to remove it.

A branch can be excluded only if a genuine scientific or technical invalidity is established and documented. The reason should be independent of whether that branch strengthens or weakens the preferred conclusion.

Otherwise the robustness audit becomes a selection exercise.

## Narrow the claim to the evidence

Fragility often means the original claim was too broad.

For example:

- If direction is stable but magnitude is not, report directional robustness and magnitude sensitivity.
- If only one detector family reverses the effect, report detector dependence and investigate why the event definitions differ.
- If AOI uncertainty changes the endpoint, report sensitivity to boundary/measurement assumptions.
- If downsampling materially alters the conclusion, avoid claiming portability across lower sampling representations without further validation.
- If added missingness creates instability, make the dropout mechanism part of the interpretation rather than treating it as generic data loss.

## A canonical fragile result in GazeAudit

The frozen Pedrotti/de Chambrier sampling-and-missingness audit has the canonical outcome `materially_fragile` under its declared protocol.

That label should be read at the **protocol level**: the frozen gaze-path-rate contrast did not remain sufficiently stable across the specified downsampling and added-missingness perturbations. It is not a generic claim that the source dataset, study, or every possible endpoint is “fragile”.

The authoritative provenance and wording remain in the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) and case-specific frozen records.

## Fragility can identify the next experiment

A good sensitivity analysis often tells you what to validate next.

Examples:

- collect better participant-level validation if spatial error drives AOI instability;
- preregister detector thresholds if detector choice dominates the estimate;
- acquire at a higher rate if sampling sensitivity threatens the endpoint;
- redesign AOIs with more spatial separation if boundary ambiguity dominates;
- model dropout explicitly if missingness patterns drive the result;
- replicate across devices when portability is the uncertainty of interest.

In this sense, fragility is not the end of the analysis. It is a map of where the scientific design is most vulnerable.

## What a transparent paper should report

When a result is materially sensitive, report:

1. the declared alternatives or perturbations;
2. the complete estimate range and sign pattern;
3. the factor(s) most associated with instability;
4. any interaction or boundary-risk evidence;
5. which conclusions remain stable;
6. which conclusions must be narrowed;
7. what uncertainty dimensions remain untested;
8. the exact software/protocol version used.

Avoid replacing the full robustness evidence with one selected “main analysis” plus a vague statement that sensitivity checks were similar when they were not.

## Robustness analysis is useful because failure is possible

A method that always declares success cannot audit robustness. The scientific value of GazeAudit's framework depends on allowing `robust`, `fragile`, and incomplete evidence states to remain distinct when the data and frozen rules support them.

Continue with the [robustness audit workflow]({{ '/docs/workflows/robustness-audit/' | relative_url }}) or inspect the [frozen validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}).
