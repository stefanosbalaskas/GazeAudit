---
title: Declared → valid → successful
description: A fully synthetic GazeAudit specification-space exercise that separates the Cartesian declaration, pre-execution scientific validity, and technical execution outcomes in an 8 declared → 6 valid → 5 successful audit.
kicker: Example · Robustness governance
page_type: example
permalink: /docs/examples/specification-denominator-audit/
search_category: Example
search_keywords: specification declared valid successful invalid technical failure denominator PipelineSpace valid_if run_specs synthetic multiverse
example_data: "Synthetic"
example_focus: "Robustness & sensitivity"
example_reuse: "Declared → valid → successful denominator and failure-ledger pattern"
example_output: "An eight-combination declaration with six valid specifications, five successful endpoints, two predeclared-invalid combinations, and one preserved valid technical failure"
example_boundary: "The factors, levels, validity rule, failure, and estimates are teaching choices; they are not recommended detector, QC, AOI, or robustness decisions."
---

# Declared → valid → successful

This exercise demonstrates one denominator rule:

> A robustness audit begins with the declared space, then applies pre-execution validity, then records what happened when each valid branch was attempted.

The synthetic record is:

```text
8 declared
6 valid
5 successful
1 valid technical failure
2 invalid before execution
```

<div class="callout warning">
<strong>Teaching decisions only.</strong>
The detector names, QC labels, AOI modes, validity rule, technical failure, and endpoint values are synthetic. They are not methodological recommendations.
</div>

## Declare three factors

```python
from gazeaudit import PipelineSpace

space = (
    PipelineSpace()
    .add_choice("detector", ["ivt", "idt"])
    .add_choice("qc_policy", ["moderate", "strict"])
    .add_choice("aoi_mode", ["hard", "probabilistic"])
)

assert space.size == 8
```

The Cartesian declaration contains:

```text
2 detector levels
× 2 QC levels
× 2 AOI modes
= 8 declared combinations
```

## Declare the scientific validity rule before execution

For this synthetic protocol, suppose `idt + strict` is scientifically inadmissible regardless of AOI mode.

```python
def valid_spec(spec):
    return not (
        spec["detector"] == "idt"
        and spec["qc_policy"] == "strict"
    )
```

Now enumerate the valid set:

```python
valid_specs = space.enumerate_specs(valid_if=valid_spec)

assert len(valid_specs) == 6
```

The two rejected combinations are:

| Detector | QC | AOI | Status |
|---|---|---|---|
| idt | strict | hard | invalid before execution |
| idt | strict | probabilistic | invalid before execution |

These combinations remain part of the **eight declared** combinations even though they are not in the valid execution denominator.

## Inspect the deterministic valid order

The six valid specifications are:

```text
1. ivt / moderate / hard
2. ivt / moderate / probabilistic
3. ivt / strict / hard
4. ivt / strict / probabilistic
5. idt / moderate / hard
6. idt / moderate / probabilistic
```

Repeated enumeration returns the same order.

That order is useful for stable branch identity, but it is not a scientific ranking.

## Add one synthetic technical failure

Suppose the fourth valid branch cannot produce the required processed input because of a synthetic backend defect.

That is:

```text
ivt / strict / probabilistic
```

It was scientifically valid before execution.

Therefore it remains in the valid denominator.

## Core `run_specs()` behavior

If the endpoint or processor raises, core `run_specs()` propagates the exception.

It does not invent a `technical_failure` result row.

For example:

```python
def processor(study, spec):
    if (
        spec["detector"] == "ivt"
        and spec["qc_policy"] == "strict"
        and spec["aoi_mode"] == "probabilistic"
    ):
        raise RuntimeError("synthetic backend failure")
    return study

def endpoint(processed, spec):
    return 1.0

# This stops when the valid failing branch is reached.
# run_specs(
#     study,
#     space,
#     endpoint=endpoint,
#     processor=processor,
#     valid_if=valid_spec,
# )
```

A project that needs to continue other branches must wrap execution in an explicit audited ledger.

## Preserve every valid branch in an outer ledger

The following teaching pattern records the six valid branches without pretending that core `run_specs()` emits failure rows:

```python
def synthetic_endpoint(spec):
    base = {
        "hard": 0.02,
        "probabilistic": 0.03,
    }[spec["aoi_mode"]]

    detector_shift = 0.01 if spec["detector"] == "idt" else 0.0
    qc_shift = -0.005 if spec["qc_policy"] == "strict" else 0.0
    return base + detector_shift + qc_shift


ledger = []

for valid_id, spec in enumerate(valid_specs, start=1):
    try:
        if (
            spec["detector"] == "ivt"
            and spec["qc_policy"] == "strict"
            and spec["aoi_mode"] == "probabilistic"
        ):
            raise RuntimeError("synthetic backend failure")

        estimate = float(synthetic_endpoint(spec))
        ledger.append(
            {
                "valid_id": valid_id,
                **spec,
                "status": "successful",
                "estimate": estimate,
                "error": None,
            }
        )
    except Exception as exc:
        ledger.append(
            {
                "valid_id": valid_id,
                **spec,
                "status": "technical_failure",
                "estimate": None,
                "error": str(exc),
            }
        )
```

The ledger has six rows because there are six valid specifications.

## Synthetic execution ledger

| Valid ID | Detector | QC | AOI | Status | Estimate |
|---:|---|---|---|---|---:|
| 1 | ivt | moderate | hard | successful | +0.020 |
| 2 | ivt | moderate | probabilistic | successful | +0.030 |
| 3 | ivt | strict | hard | successful | +0.015 |
| 4 | ivt | strict | probabilistic | technical_failure | — |
| 5 | idt | moderate | hard | successful | +0.030 |
| 6 | idt | moderate | probabilistic | successful | +0.040 |

Therefore:

```text
successful = 5
valid = 6
```

The correct execution summary is:

> 5 successful / 6 valid.

Not:

> 5 / 5.

## Keep the invalid combinations in the declaration record

A complete audit record can preserve:

### Declared ledger

All eight Cartesian combinations.

### Validity classification

- six valid;
- two invalid-before-execution with the predeclared reason.

### Execution ledger

- five successful;
- one valid technical failure.

This gives:

```text
declared = valid + invalid-before-execution
8 = 6 + 2

valid = successful + valid technical failure
6 = 5 + 1
```

## Do not repair the denominator after seeing the failure

Bad response:

> The probabilistic strict IVT branch failed, so we updated `valid_if` to exclude it.

Why it fails:

The branch was scientifically admissible before execution.

Changing the validity rule after the technical failure rewrites a valid execution problem as scientific invalidity.

Better:

1. preserve the original failure event;
2. diagnose the technical cause;
3. repair the causal defect if possible;
4. rerun the **same valid branch**;
5. link the repaired execution to the original failure;
6. retain both records in history.

## A repaired rerun does not erase the original failure

Suppose the synthetic backend defect is fixed.

The rerun could produce:

```text
ivt / strict / probabilistic → +0.025
```

The final current-state summary may then have:

```text
6 / 6 valid branches successfully represented
```

But the audit history should still show:

- initial technical failure;
- repair;
- same-branch rerun;
- repaired endpoint.

Do not rewrite the history as though no failure occurred.

## Validity rule versus failure policy

These answer different questions.

### `valid_if`

> Should this declared combination enter the scientific execution set at all?

### Failure policy

> What do we record if a valid attempted branch cannot produce the declared endpoint?

Keeping the two rules separate protects the denominator from outcome-informed rewriting.

## Timing example

Suppose these six valid branches were the submitted audit.

A reviewer later asks for two new detector-threshold levels.

Record them as a separate post-review declaration.

Do not silently expand:

```text
submitted: 8 declared / 6 valid
```

into a new apparently predeclared denominator.

## Reporting example

### Methods

> We declared an eight-combination synthetic specification space crossing two detector families, two QC policies, and two AOI representations. A pre-execution protocol rule classified the two IDT + strict combinations as scientifically inadmissible, yielding six valid specifications. All valid branches targeted one common scalar endpoint.

### Results

> Five of six valid specifications successfully produced the endpoint. One valid IVT + strict + probabilistic branch failed technically and remained in the valid denominator. The two predeclared-invalid combinations were documented separately and were not treated as technical failures.

### Limitation

> The synthetic denominator exercise demonstrates branch accounting only. It does not establish that the teaching factors, validity rule, or endpoint are appropriate for an empirical eye-tracking study.

## API links

- [`PipelineSpace`]({{ '/docs/reference/api-pathways/#api-pipelinespace' | relative_url }})
- [`run_specs()`]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [Specification-space pathway]({{ '/docs/reference/api-pathways/#path-specification-robustness' | relative_url }})
- [Specification Space Declaration Center]({{ '/docs/specification-declaration/' | relative_url }})
- [Specification-space declaration and validity]({{ '/docs/guides/specification-declaration/' | relative_url }})

## Reuse boundary

Reuse:

- declared → valid → successful denominator structure;
- pre-execution validity timing;
- explicit invalid-combination reasons;
- valid-failure preservation;
- same-branch repair/rerun linkage.

Rebuild:

- factor set;
- levels;
- validity predicate;
- endpoint;
- failure policy;
- repair rules;
- temporal evidence layers.
