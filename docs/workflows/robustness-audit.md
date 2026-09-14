---
title: Robustness audit workflow
description: End-to-end workflow for declaring an analytical decision space and diagnosing conclusion stability.
kicker: Workflow · Analytical robustness
---

# Robustness audit workflow

Use this workflow when more than one analytical path is scientifically defensible and you want to know whether the conclusion depends on those choices.

## Workflow overview

<div class="workflow-steps">
  <div class="workflow-step"><strong>Define the scientific endpoint</strong><p>State the scalar quantity whose stability will be evaluated before constructing the decision space.</p></div>
  <div class="workflow-step"><strong>Declare the decision factors</strong><p>List each defensible choice and its levels with a methodological rationale.</p></div>
  <div class="workflow-step"><strong>Reject invalid combinations</strong><p>Encode scientific constraints before execution rather than discarding rows after seeing their estimates.</p></div>
  <div class="workflow-step"><strong>Execute the complete valid space</strong><p>Run every declared valid specification against the same endpoint.</p></div>
  <div class="workflow-step"><strong>Diagnose stability</strong><p>Inspect ordered estimates, sign/magnitude stability, marginal factor sensitivity, and pairwise interaction sensitivity.</p></div>
  <div class="workflow-step"><strong>Interpret without optimisation</strong><p>Explain where instability arises instead of selecting the most favourable pipeline.</p></div>
</div>

## 1. Define the common endpoint

Examples of a suitable endpoint include:

- condition-minus-control dwell difference;
- paired AOI occupancy contrast;
- gaze-path-rate contrast;
- mean fixation-duration contrast;
- a prespecified model coefficient;
- a known-truth recovery error in simulation.

The endpoint should have the same scientific meaning under every specification.

## 2. Declare the decision space

```python
from gazeaudit import PipelineSpace

space = (
    PipelineSpace()
    .add_choice("detector", ["ivt", "idt"])
    .add_choice("qc", ["moderate", "strict"])
    .add_choice("aoi_mode", ["hard", "probabilistic"])
)
```

The point is not to maximise the number of combinations. A smaller justified space is scientifically stronger than a large arbitrary one.

## 3. Encode invalid combinations

```python
def valid_if(spec):
    # Replace this illustration with study-specific scientific constraints.
    return not (
        spec["detector"] == "idt"
        and spec["qc"] == "strict"
    )
```

Invalidity should be based on design or methodological incompatibility—not on an unattractive estimate.

## 4. Execute all valid specifications

```python
from gazeaudit import run_specs

results = run_specs(
    study,
    space,
    endpoint=endpoint_function,
    processor=processor_function,
    valid_if=valid_if,
)
```

Preserve the full output table. The scientific record is the complete valid specification space, not only a preferred row.

## 5. Order the estimates

```python
from gazeaudit import specification_curve

curve = specification_curve(results)
```

<figure class="plot-card">
  <img src="{{ '/assets/images/specification-curve.svg' | relative_url }}" alt="Synthetic ordered specification curve">
  <figcaption>A specification curve reveals range, direction, clustering, and outlying analytical paths. The figure uses synthetic values.</figcaption>
</figure>

Questions to ask:

- Is the sign invariant?
- Is the range substantively narrow or wide?
- Are there clusters corresponding to particular methods?
- Are extreme estimates linked to one factor level or interaction?

## 6. Summarise overall stability

```python
from gazeaudit import effect_stability

stability = effect_stability(results, null=0.0)
```

Report sign fractions and the actual range/quantiles rather than reducing the analysis to a single adjective.

## 7. Screen factor sensitivity

```python
from gazeaudit import marginal_sensitivity, pairwise_interaction_sensitivity

factors = ["detector", "qc", "aoi_mode"]

marginal = marginal_sensitivity(results, factors)
pairwise = pairwise_interaction_sensitivity(results, factors)
```

These are descriptive diagnostics. They help locate instability but are not a causal attribution of variance.

## 8. Add perturbation families when scientifically relevant

Not every sensitivity axis belongs inside an ordinary categorical multiverse. Controlled perturbations such as:

- spatial-error scale;
- target sampling rate;
- added missingness;

can be more interpretable as explicit sensitivity curves.

<figure class="plot-card">
  <img src="{{ '/assets/images/sensitivity-curves.svg' | relative_url }}" alt="Synthetic robustness sensitivity curves">
  <figcaption>Keep perturbation families semantically distinct so a reader can tell whether instability comes from measurement assumptions, sampling representation, missingness, or ordinary analytical choices.</figcaption>
</figure>

## 9. Interpret instability scientifically

A materially unstable result is not a software failure. It can be an important methodological finding.

Possible interpretations include:

- the endpoint is highly sensitive to one methodological choice;
- a detector family changes the substantive direction;
- only boundary-sensitive AOI definitions create instability;
- downsampling removes information required by the endpoint;
- missingness interacts with a particular analysis branch;
- multiple defensible choices produce genuinely different scientific conclusions.

The appropriate response may be narrower claims, additional validation, redesigned measurement, or explicit reporting of uncertainty—not choosing whichever specification is most convenient.

## 10. Preserve the robustness record

Archive:

- full declared factor/level definitions;
- validity rule;
- exact executed specification table;
- one endpoint estimate per specification;
- ordered specification curve;
- effect-stability summary;
- marginal and pairwise sensitivity tables;
- any perturbation curves;
- software and source provenance.

## Optional conclusion-recovery rule

If a known-truth or independently justified reference effect exists, add a `ConclusionRule` and use the publication-audit layer. Do not manufacture a reference from the same results that will be evaluated against it.

## Next

Bind the complete robustness record with the [reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) or review the [specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }}) for function-level detail.
