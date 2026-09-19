---
title: Specification-space guide
description: Declare, execute, and interpret defensible analytical alternatives with PipelineSpace.
kicker: Guide · Analytical robustness
---

# Specification-space guide

Robustness analysis is useful only when the alternative specifications are scientifically defensible. GazeAudit therefore separates **declaring the decision space** from **summarising the resulting estimates**.

## 1. Identify decisions that could reasonably vary

Examples include:

- detector family or detector threshold;
- QC threshold;
- missing-data rule;
- AOI geometry or uncertainty model;
- sampling-rate perturbation;
- preprocessing branch;
- inclusion rule;
- endpoint implementation when multiple operationalisations are defensible.

Do not add arbitrary choices merely to enlarge the multiverse. Each level should have a methodological rationale.

## 2. Declare the space

Before constructing `PipelineSpace`, record the robustness question, endpoint reference, factors, typed levels, rationale, decision timing, validity-rule mode, failure policy, and untested uncertainty dimensions. The [Specification Space Declaration Center]({{ '/docs/specification-declaration/' | relative_url }}) generates a no-default declaration and preserves the declared Cartesian count separately from the valid execution denominator.

```python
from gazeaudit import PipelineSpace

space = (
    PipelineSpace()
    .add_choice("detector", ["ivt", "idt"])
    .add_choice("qc", ["strict", "moderate"])
    .add_choice("aoi_mode", ["hard", "probabilistic"])
)

print(space.size)
# 8
```

`PipelineSpace` enumerates combinations in deterministic order.

## 3. Reject invalid combinations before execution

Some combinations may be technically possible but scientifically nonsensical. Use `valid_if` to remove them explicitly:

```python
def valid_spec(spec):
    if spec["detector"] == "idt" and spec["qc"] == "strict":
        return False
    return True

specs = space.enumerate_specs(valid_if=valid_spec)
```

This is preferable to running every combination and discarding inconvenient rows after inspecting estimates.

## 4. Use one common scientific endpoint

Before implementation, record the endpoint's scientific quantity, unit, contrast direction, analysis unit/aggregation, eligible denominator, missing-input behavior, non-finite behavior, transformations, required inputs, and interpretation boundary. The [Endpoint Definition & Handoff Center]({{ '/docs/endpoint-contract/' | relative_url }}) provides a no-default declaration builder, and [Endpoint definition and invariance]({{ '/docs/guides/endpoint-definition/' | relative_url }}) explains how to distinguish upstream specification variation from endpoint drift.

`run_specs()` evaluates every valid specification and collects one scalar estimate.

```python
from gazeaudit import run_specs

results = run_specs(
    study,
    space,
    endpoint=endpoint_function,
    processor=processor_function,
    valid_if=valid_spec,
)
```

The processor receives `(study, specification)`. The endpoint receives `(processed_object, specification)` and must return one finite scalar.

A common endpoint is essential: the purpose is to compare what happens to the **same scientific quantity** under different defensible analytical paths.

## 5. Inspect the specification curve

```python
from gazeaudit import specification_curve

curve = specification_curve(results)
print(curve[["spec_id", "estimate"]])
```

<figure class="plot-card">
  <img src="{{ '/assets/images/specification-curve.svg' | relative_url }}" alt="Synthetic ordered specification curve">
  <figcaption>Illustrative curve only. A specification curve makes the range and ordering of declared estimates visible without designating one post-hoc winner.</figcaption>
</figure>

## 6. Summarise sign and magnitude stability

```python
from gazeaudit import effect_stability

stability = effect_stability(results, null=0.0)
print(stability)
```

The summary includes the number of specifications, mean/median/range, central quantiles, positive/negative/exact-null fractions, and a descriptive sign-stability measure.

These are descriptive robustness summaries. They are not posterior probabilities and they do not replace a formal inferential model.

## 7. Locate sensitive decisions

Use marginal sensitivity to screen which declared factors account for the largest differences in cell means:

```python
from gazeaudit import marginal_sensitivity

marginal = marginal_sensitivity(
    results,
    factors=["detector", "qc", "aoi_mode"],
)
```

For pairwise descriptive interactions:

```python
from gazeaudit import pairwise_interaction_sensitivity

interactions = pairwise_interaction_sensitivity(
    results,
    factors=["detector", "qc", "aoi_mode"],
)
```

The ratios are **screening diagnostics**, not causal variance decompositions. In dependent, incomplete, or unbalanced specification spaces, sensitivity ratios can overlap and need not sum to one.

## 8. Distinguish robustness from optimisation

A robustness analysis asks:

> How much does the scientific conclusion change across reasonable choices?

It should not ask:

> Which reasonable-looking choice gives the strongest effect or smallest p-value?

GazeAudit's scientific principle is deliberately anti-optimisation: declare the defensible space first, then characterise its consequences.

## Practical design checklist

Before running the multiverse, write down:

- the scientific endpoint;
- each factor and its levels;
- why each level is defensible;
- invalid combinations and the reason for excluding them;
- the reference specification, if one exists;
- the conclusion rule or robustness criterion, if one will be used;
- any perturbation analyses that are separate from ordinary analytical choices;
- the software/data provenance that must be captured.

## From descriptive robustness to conclusion recovery

When a known-truth or otherwise prejustified reference effect exists, a `ConclusionRule` can define acceptable recovery using effect-error tolerance, direction recovery, and a minimum across-specification recovery fraction.

The reference effect is **not inferred by GazeAudit** for real-data analyses. It must be defined and justified independently before robustness outputs are inspected.

Continue with [publication audits]({{ '/docs/guides/publication-audits/' | relative_url }}) or run the [specification-curve example]({{ '/docs/examples/specification-curve/' | relative_url }}).
