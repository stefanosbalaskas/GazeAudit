---
title: Endpoint definition and invariance
description: Define one scientific endpoint for GazeAudit robustness analysis, preserve its contrast, unit, aggregation, denominator, missingness and non-finite behavior across branches, distinguish endpoint variation from processor variation, and prevent endpoint drift.
kicker: Guide · Analytical robustness
permalink: /docs/guides/endpoint-definition/
search_category: Guide
search_keywords: endpoint definition estimand invariance run_specs common scalar contrast unit aggregation denominator missingness nonfinite endpoint drift robustness
---

# Endpoint definition and invariance

A specification-space audit is only interpretable if the branches are comparable.

In GazeAudit, `run_specs()` operationalises that principle by calling one endpoint callable for every valid specification:

```python
estimate = float(endpoint(processed, spec))
```

The software interface is simple. The scientific contract is not.

The researcher must define what that scalar **means** and ensure the meaning does not drift across branches.

Use the [Endpoint Definition & Handoff Center]({{ '/docs/endpoint-contract/' | relative_url }}) to create a documentation-side declaration before implementing the calculation.

## 1. Write the endpoint in words before code

A useful endpoint declaration should answer:

> What single scientific quantity will every valid branch estimate?

Weak:

> AOI metric

Better:

> Mean participant-level treatment-minus-control difference in the proportion of eligible gaze observations assigned to the target AOI.

The second statement identifies:

- outcome family;
- contrast direction;
- aggregation level;
- denominator concept.

Do not rely on the function name to carry this meaning.

## 2. Fix the sign / contrast convention

These are different endpoint definitions:

```text
treatment - control
control - treatment
```

The absolute magnitude may be identical while the sign reverses.

If direction stability matters, record the subtraction order or reference category before execution.

Likewise, a ratio such as:

```text
treatment / control
```

is not interchangeable with a difference merely because both compare the same two conditions.

## 3. Fix the unit or scale

Examples:

- milliseconds;
- seconds;
- proportion;
- percentage points;
- expected fixation count;
- log milliseconds;
- standardized difference.

A specification branch must not silently return seconds when another returns milliseconds.

If a transformation is part of the endpoint, declare it once and preserve it.

## 4. Fix the analysis unit and aggregation target

These can estimate different quantities:

### Observation-weighted mean

Every gaze/fixation observation contributes equally.

### Trial-weighted mean

Each trial contributes equally regardless of its row/event count.

### Participant-weighted mean

Each participant contributes equally after within-participant aggregation.

Changing weighting changes the target quantity.

Do not describe these simply as alternative implementation details unless the scientific estimand truly remains the same.

## 5. Fix the eligible population / denominator

Define which units are eligible **before** specification-specific processing.

Examples:

- all randomised participants with at least one eligible trial;
- all valid participant × trial units under a declared readiness policy;
- fixations occurring within the prespecified stimulus window;
- observations with the required measured variables.

A branch that silently drops units because an intermediate operation fails can change the endpoint denominator.

Preserve that change as execution or missingness evidence rather than pretending the endpoint stayed identical.

## 6. Separate processor choices from endpoint meaning

`run_specs()` has two callable layers.

### Processor

```python
processed = processor(study, spec)
```

The processor can implement declared branch choices:

- QC;
- detector;
- missing-data handling;
- sampling;
- AOI representation;
- preprocessing;
- another representation decision.

### Endpoint

```python
estimate = endpoint(processed, spec)
```

The endpoint should calculate the common scientific quantity from that processed representation.

A processor can change the data that enter the endpoint without changing what the endpoint means.

That is the purpose of a robustness audit.

## 7. Do not hide undeclared specification choices inside the endpoint

Because the endpoint receives `spec`, it can technically branch on specification fields.

That is useful when the endpoint needs a declared representation choice such as an AOI radius.

It is not permission to add undeclared analysis decisions.

Bad pattern:

```python
def endpoint(processed, spec):
    if result_looks_small(processed):
        return alternative_outcome(processed)
    return primary_outcome(processed)
```

This is outcome-dependent endpoint drift.

Every branch decision should either be:

- fixed in the endpoint declaration;
- represented explicitly in `PipelineSpace`;
- or kept as a separate endpoint/audit.

## 8. Decide whether an operationalisation change preserves the scientific quantity

Some changes are defensible specification factors.

Example:

> AOI radius varies, but every branch returns the same treatment-minus-control AOI occupancy contrast.

The spatial operationalisation changes while the high-level endpoint remains a common occupancy contrast.

Other changes alter the scientific endpoint.

Example:

- branch A: treatment-minus-control dwell time;
- branch B: treatment-minus-control fixation count;
- branch C: latency-to-first-fixation difference.

Those should not be collapsed into one specification curve merely because they concern the same AOI.

If several endpoint operationalisations are scientifically intended to represent one construct, document the rationale explicitly. In many cases the safer design is separate endpoint audits followed by a higher-level comparison.

## 9. Treat endpoint transformations as part of the contract

These are not numerically identical:

- raw duration;
- log duration;
- square-root duration;
- standardized duration;
- rate per second.

If transformation varies across specifications, decide whether:

1. it is truly an analytical choice applied to the same estimand and can be harmonised for comparison; or
2. it changes the endpoint scale enough that separate summaries are required.

Do not compare raw and transformed estimates in one range without a common interpretable scale.

## 10. Define missing-input behavior

The endpoint declaration should say what happens when required inputs are unavailable.

Examples:

- an AOI probability is missing;
- a condition has no eligible trial after processing;
- duration is unavailable;
- one participant lacks the contrast pair;
- a model-derived endpoint cannot be estimated.

Do not silently:

- replace missing with zero;
- drop the affected unit;
- change aggregation;
- substitute another variable.

If a branch cannot produce the endpoint under the declared contract, preserve that as an execution/evidence event.

## 11. Define the non-finite endpoint policy

The runtime converts the endpoint output using `float(...)`.

Python accepts:

```python
float(np.nan)
float(np.inf)
```

Therefore `run_specs()` alone does not enforce finite scientific estimates.

If finiteness is required:

```python
import numpy as np

def endpoint(processed, spec):
    estimate = calculate_declared_endpoint(processed, spec)
    estimate = float(estimate)

    if not np.isfinite(estimate):
        raise ValueError(
            "endpoint estimate must be finite under the declared contract"
        )

    return estimate
```

An exception then remains an execution failure that must be preserved by the surrounding audit workflow.

Do not convert a non-finite endpoint to zero.

## 12. Keep `valid_if` separate from endpoint failure

`valid_if` represents a rule known **before execution**:

> This combination is scientifically invalid.

An endpoint failure means:

> This valid attempted branch did not produce the declared scalar under the execution contract.

Do not use endpoint failure retrospectively to relabel an inconvenient valid branch as invalid.

## 13. Keep endpoint and conclusion rule separate

The endpoint is a scalar estimate.

A conclusion rule can evaluate:

- sign;
- tolerance relative to a reference;
- recovery fraction;
- another declared criterion.

Do not change the endpoint calculation to make it satisfy the conclusion rule.

For known-truth recovery, the reference effect must be independently defined before result inspection.

## 14. Test endpoint invariance before the full audit

Useful tests include:

### Shape

Every valid branch returns one scalar.

### Unit

Known synthetic input produces the expected unit/scale.

### Contrast direction

A simple fixture confirms the subtraction/reference convention.

### Aggregation

A deliberately unbalanced synthetic table confirms whether participants/trials/observations receive the intended weights.

### Missingness

A fixture with missing endpoint inputs verifies the declared failure/handling rule.

### Non-finite output

A fixture verifies whether `NaN`/infinity is rejected, preserved, or recorded as declared.

### Specification invariance

Two specifications that should differ only in preprocessing still compute the same conceptual endpoint.

## 15. Endpoint change during peer review

A reviewer may request a different endpoint.

Treat that as a separate temporal evidence layer when it changes the scientific quantity.

Do not fold a new endpoint into the original denominator and describe all branches as one prespecified audit.

Record:

- original endpoint declaration;
- reviewer-requested endpoint declaration;
- timing;
- reason;
- separate specification/execution denominator;
- manuscript location.

## 16. Reporting endpoint identity

### Methods

> The scientific endpoint was defined before robustness execution as [quantity], expressed in [unit], using [contrast direction], [aggregation/analysis unit], and [eligible denominator]. All valid specifications returned this same scalar; declared preprocessing and measurement choices varied upstream of the endpoint.

### Results

> The endpoint was successfully obtained for [successful]/[valid] valid specifications. All represented estimates corresponded to the same [endpoint name] definition; [failure/non-finite accounting] remained explicit in the execution record.

### Limitation

> The robustness audit applies to the declared endpoint and does not establish that alternative endpoint definitions, aggregation targets, transformations, or constructs would show the same pattern.

## 17. Endpoint handoff checklist

Before handing the analysis to a collaborator, reviewer, or future self:

- [ ] endpoint name recorded;
- [ ] scientific quantity stated in words;
- [ ] unit/scale recorded;
- [ ] contrast direction recorded;
- [ ] analysis unit and weighting recorded;
- [ ] eligible population/denominator recorded;
- [ ] missing-input behavior recorded;
- [ ] non-finite behavior recorded;
- [ ] transformations recorded;
- [ ] scientific null/reference recorded when relevant;
- [ ] required processed inputs recorded;
- [ ] interpretation boundary recorded;
- [ ] endpoint implementation tested on synthetic edge cases;
- [ ] common-endpoint invariance checked across representative specifications;
- [ ] endpoint changes after submission/review stored as separate temporal evidence.

## API links

- [`run_specs()`]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [`PipelineSpace`]({{ '/docs/reference/api-pathways/#api-pipelinespace' | relative_url }})
- [`expected_dwell()`]({{ '/docs/reference/api-pathways/#api-expected-dwell' | relative_url }})
- [Specification-space pathway]({{ '/docs/reference/api-pathways/#path-specification-robustness' | relative_url }})
- [Endpoint Definition & Handoff Center]({{ '/docs/endpoint-contract/' | relative_url }})
- [Machine-readable endpoint field reference]({{ '/assets/endpoint-contract-reference.json' | relative_url }})

## Worked exercise

Continue to [Endpoint drift audit]({{ '/docs/examples/endpoint-drift-audit/' | relative_url }}) to compare branches that preserve a common scientific quantity with branches that silently change contrast, unit, aggregation, or outcome family.
