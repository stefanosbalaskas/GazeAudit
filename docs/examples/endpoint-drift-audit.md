---
title: Endpoint drift audit
description: A fully synthetic worked example distinguishing acceptable specification variation from scientific endpoint drift in GazeAudit, including contrast reversal, unit mismatch, aggregation changes, different outcome families, and non-finite endpoint handling.
kicker: Example · Endpoint governance
page_type: example
permalink: /docs/examples/endpoint-drift-audit/
search_category: Example
search_keywords: endpoint drift run_specs common endpoint estimand contrast unit aggregation denominator nonfinite missing endpoint specification synthetic
example_data: "Synthetic"
example_focus: "Robustness & sensitivity"
example_reuse: "Common-endpoint invariance and drift-detection pattern"
example_output: "A branch-by-branch endpoint compatibility audit with corrected handoff rules"
example_boundary: "Synthetic endpoint scenarios teach comparability checks; they are not recommended eye-tracking endpoints or effect definitions."
---

# Endpoint drift audit

This is a **fully synthetic endpoint-governance exercise**. It asks a narrow question:

> Do all branches in one robustness audit still estimate the same scientific quantity?

The exercise deliberately mixes acceptable analytical variation with several forms of endpoint drift.

<div class="callout warning">
<strong>Do not copy the endpoint values or definitions.</strong>
The scenarios below are selected to make endpoint invariance visible. A real endpoint must come from the study question, protocol, measurement design, and analysis plan.
</div>

## Baseline declaration

Assume the intended endpoint is:

> Participant-weighted mean treatment-minus-control difference in target-AOI dwell time, expressed in milliseconds, among eligible paired trials.

Record it explicitly:

```json
{
  "schema": "gazeaudit-endpoint-declaration-v1",
  "endpoint_name": "target_aoi_dwell_contrast",
  "scientific_quantity": "participant-weighted mean treatment-minus-control target-AOI dwell difference",
  "unit": "milliseconds",
  "contrast_direction": "treatment - control",
  "analysis_unit": "participant; paired condition means computed within participant before the across-participant mean",
  "population_denominator": "participants with eligible paired treatment and control trials under the declared branch",
  "missingness_policy": "a participant without the required pair cannot yield the declared participant contrast; preserve that branch consequence explicitly",
  "nonfinite_policy": "non-finite endpoint is an execution-contract failure and is not converted to zero",
  "transformation": null,
  "scientific_null": "0 ms",
  "required_inputs": "target-AOI dwell duration by participant, condition, and eligible trial",
  "interpretation_boundary": "does not measure fixation count, latency, or gaze outside the target AOI",
  "generate_finite_guard": true
}
```

The declaration is documentation-side provenance. It does not implement the endpoint for you.

## A small synthetic processed table

```python
import pandas as pd

processed = pd.DataFrame(
    {
        "participant": ["P01", "P01", "P02", "P02"],
        "condition": ["control", "treatment", "control", "treatment"],
        "dwell_ms": [200.0, 240.0, 300.0, 330.0],
        "fixation_count": [2, 3, 4, 4],
        "latency_ms": [420.0, 390.0, 510.0, 470.0],
    }
)
```

The intended participant contrasts are:

```text
P01: 240 - 200 = +40 ms
P02: 330 - 300 = +30 ms
participant-weighted endpoint = (+40 + +30) / 2 = +35 ms
```

## Correct endpoint implementation

```python
import numpy as np

def target_aoi_dwell_contrast(processed, spec):
    wide = processed.pivot(
        index="participant",
        columns="condition",
        values="dwell_ms",
    )

    paired = wide.dropna(subset=["treatment", "control"])
    contrasts = paired["treatment"] - paired["control"]
    estimate = float(contrasts.mean())

    if not np.isfinite(estimate):
        raise ValueError(
            "endpoint estimate must be finite under the declared contract"
        )

    return estimate
```

For this fixture:

```python
assert target_aoi_dwell_contrast(processed, {}) == 35.0
```

## Scenario A · QC varies, endpoint stays the same

Suppose one specification uses a moderate QC policy and another uses a stricter policy, but both processors return the same required columns and the endpoint still calculates:

> participant-weighted treatment-minus-control dwell milliseconds.

This is ordinary robustness variation.

The cohort may change. The endpoint meaning does not.

### Compatible with one audit?

**Yes**, provided the denominator change is itself an explicitly declared specification consequence and every branch still computes the same scientific quantity.

---

## Scenario B · AOI radius varies, dwell contrast stays the same

Suppose `aoi_radius` varies across the specification space.

Each branch recomputes target-AOI dwell under that declared AOI representation, then returns the same participant-weighted treatment-minus-control dwell contrast in milliseconds.

### Compatible with one audit?

Potentially **yes**.

The AOI representation is a declared measurement/operationalisation factor. The resulting scientific endpoint remains the same high-level dwell contrast.

The endpoint declaration should make clear that AOI representation is allowed to vary upstream.

---

## Scenario C · Contrast silently reverses

Branch 1:

```text
treatment - control
```

Branch 2:

```text
control - treatment
```

The fixture produces +35 ms versus -35 ms.

### Compatible with one audit?

**No.**

A sign reversal caused by a changed subtraction convention is not robustness sensitivity. It is endpoint drift.

### Repair

Choose one declared contrast direction and apply it in every branch.

---

## Scenario D · Seconds appear in one branch

Branch 1 returns:

```text
35.0 ms
```

Branch 2 returns:

```text
0.035 s
```

### Compatible with one raw specification curve?

**No**, not without harmonising the scale.

The scientific quantity may be conceptually the same, but the numerical units are not.

### Repair

Convert every branch to the declared common unit before returning the scalar.

Do not rely on downstream interpretation to notice the scale change.

---

## Scenario E · Dwell changes to fixation count

Branch 1 returns target-AOI dwell difference.

Branch 2 returns:

```python
def fixation_count_contrast(processed, spec):
    wide = processed.pivot(
        index="participant",
        columns="condition",
        values="fixation_count",
    )
    paired = wide.dropna(subset=["treatment", "control"])
    return float((paired["treatment"] - paired["control"]).mean())
```

### Compatible with one common-endpoint audit?

**No.**

Both concern the same AOI, but dwell time and fixation count are different scientific quantities with different units and interpretations.

### Repair

Run separate endpoint audits, or define a higher-level multi-endpoint analysis plan that preserves each endpoint's identity.

---

## Scenario F · Participant weighting changes to observation weighting

Assume P01 has many more eligible trials than P02.

One branch computes:

> mean participant contrast, weighting P01 and P02 equally.

Another pools all eligible observations before taking the treatment-control difference.

These can produce different estimates even from the same data because the aggregation target changed.

### Compatible with one audit?

Not automatically.

If participant weighting is part of the endpoint declaration, pooled observation weighting is endpoint drift.

If weighting strategy itself is a scientifically defensible analytical factor, define exactly what common estimand allows that variation—or keep the alternatives as separate endpoint analyses.

Do not hide weighting changes inside a helper function.

---

## Scenario G · Missing pair silently becomes zero

Suppose strict processing removes P02's control trial.

Bad endpoint code:

```python
control = participant_control_mean_or_zero(...)
treatment = participant_treatment_mean_or_zero(...)
return treatment - control
```

### Why this fails

The missing condition is being converted into an observed value of zero.

That changes the scientific meaning of the contrast.

### Better

Follow the declared missingness policy:

- preserve that P02 cannot yield the required paired contrast;
- decide whether the branch can still estimate the declared participant-level endpoint under the predeclared denominator rule;
- if not, preserve the endpoint/execution failure rather than fabricating zero.

---

## Scenario H · Endpoint returns `NaN`

```python
from gazeaudit import PipelineSpace, run_specs

space = PipelineSpace().add_choice("branch", ["finite", "nonfinite"])

def endpoint(processed, spec):
    if spec["branch"] == "nonfinite":
        return float("nan")
    return 1.0

results = run_specs(
    study,
    space,
    endpoint=endpoint,
)
```

The core runtime performs `float(...)` coercion, so the `NaN` can remain in the returned result table.

### What this means

It does **not** mean:

- zero effect;
- exact null;
- successful finite endpoint;
- invalid predeclared specification.

The surrounding audited workflow must define how non-finite endpoints are detected and recorded before interpretation.

If finite output is required, enforce it explicitly.

---

## Scenario I · Reviewer requests latency instead of dwell

Submitted endpoint:

> treatment-minus-control target-AOI dwell difference.

Reviewer-requested endpoint:

> treatment-minus-control latency-to-first-fixation difference.

### Same audit denominator?

**No.**

This is a new scientific endpoint and a new temporal evidence layer.

Preserve:

- submitted endpoint declaration;
- submitted specification denominator;
- reviewer-requested endpoint declaration;
- reviewer-requested specification denominator;
- timing and reason for the amendment.

Do not rewrite the final archive as though latency had been part of the original endpoint.

## Compatibility matrix

| Change | Common endpoint preserved? | Recommended record |
|---|---|---|
| QC rule varies upstream | usually yes | one declared robustness space |
| AOI representation varies but dwell contrast stays fixed | potentially yes | one declared measurement/robustness factor |
| contrast reverses | no | correct to one declared direction |
| milliseconds vs seconds | only after harmonisation | convert to one declared unit |
| dwell vs fixation count | no | separate endpoint audits |
| participant vs observation weighting | depends on declared estimand | justify explicitly or separate |
| missing pair replaced by zero | no | preserve missingness/failure rule |
| finite vs `NaN` output | endpoint unavailable in one branch | preserve non-finite execution evidence |
| reviewer changes dwell to latency | no | separate post-review endpoint layer |

## Runtime demonstration of the common-endpoint contract

`run_specs()` passes the current processed object and specification to one endpoint:

```python
from gazeaudit import PipelineSpace, run_specs

space = (
    PipelineSpace()
    .add_choice("qc_policy", ["moderate", "strict"])
    .add_choice("aoi_radius", [80, 100])
)

results = run_specs(
    study,
    space,
    endpoint=target_aoi_dwell_contrast,
    processor=process_specification,
)
```

The processor may change the branch representation.

The endpoint identity does not.

## Reporting example

### Methods

> The endpoint was fixed before robustness execution as the participant-weighted treatment-minus-control difference in target-AOI dwell time (ms), calculated from eligible paired condition trials. QC and AOI-representation choices varied through the declared specification space; contrast direction, endpoint unit, participant weighting, and missing-pair rule were held fixed.

### Results

> All successfully represented branches returned the declared dwell-time contrast. Branches unable to produce a finite endpoint under the declared missingness/non-finite contract were preserved as execution evidence rather than recoded as zero.

### Limitation

> The audit characterises robustness of the declared dwell-time contrast and does not establish that fixation-count, latency, alternative weighting, or other endpoint definitions would yield the same conclusion.

## API links

- [`run_specs()`]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [`PipelineSpace`]({{ '/docs/reference/api-pathways/#api-pipelinespace' | relative_url }})
- [`expected_dwell()`]({{ '/docs/reference/api-pathways/#api-expected-dwell' | relative_url }})
- [Specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }})
- [Endpoint Definition & Handoff Center]({{ '/docs/endpoint-contract/' | relative_url }})
- [Endpoint definition and invariance]({{ '/docs/guides/endpoint-definition/' | relative_url }})

## Reuse boundary

Reuse:

- the endpoint declaration fields;
- invariance checklist;
- processor-versus-endpoint distinction;
- non-finite accounting;
- temporal separation of endpoint amendments.

Rebuild:

- scientific quantity;
- units;
- contrast;
- aggregation;
- population denominator;
- missingness/non-finite policy;
- transformations;
- endpoint implementation;
- interpretation boundary.
