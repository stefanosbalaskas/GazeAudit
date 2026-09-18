---
title: Example → study handoff
description: A fully synthetic walkthrough showing how to reuse the structure of a GazeAudit robustness example while replacing teaching values with explicitly declared study decisions.
kicker: Example · Research handoff
permalink: /docs/examples/example-to-study-handoff/
search_category: Example
search_keywords: example study handoff synthetic own data teaching values defaults thresholds PipelineSpace run_specs decision record adaptation
---

# Example → study handoff

This is a **fully synthetic adaptation exercise**. It demonstrates how to move from a teaching example to a study-owned analysis plan without treating the example's values as scientific defaults.

Nothing on this page selects an AOI, threshold, endpoint, exclusion, detector setting, or specification level for a real experiment.

## Starting point: a teaching example

Imagine that a robustness tutorial contains this compact teaching configuration:

```python
from gazeaudit import PipelineSpace, run_specs

teaching_choices = {
    "min_quality": (0.80, 0.90),
    "sample_stride": (1, 2),
    "aoi_radius": (60.0, 80.0),
}

space = PipelineSpace(choices=teaching_choices)
results = run_specs(study, space, endpoint)
```

The numbers are **teaching values for this exercise**. They exist only so the example has a concrete, deterministic decision space.

Do not begin a real study by copying the dictionary.

## 1. Split structure from values

The safe reusable structure is:

```text
public imports
→ declared choices
→ PipelineSpace
→ one common endpoint
→ run_specs
→ complete result table
```

The values require a new decision.

| Example element | Classification | Handoff action |
|---|---|---|
| `PipelineSpace(...)` | software structure | reuse if specification-space analysis is appropriate |
| `run_specs(...)` | software structure | reuse with the real study, declared space, and endpoint |
| `min_quality=(0.80, 0.90)` | teaching values | replace with defensible study levels or omit factor |
| `sample_stride=(1, 2)` | teaching values | replace with declared sampling perturbations or omit |
| `aoi_radius=(60, 80)` | teaching values | rebuild from actual stimulus geometry or omit |
| `endpoint` | scientific decision | define from the real research question |
| tutorial output | synthetic evidence | never merge into the empirical study record |

## 2. Write the handoff record before replacing values

Create a small record that says what came from the example and what must be rebuilt.

```python
handoff = {
    "source_example": "end-to-end robustness teaching workflow",
    "reused_structure": [
        "PipelineSpace declaration",
        "common endpoint across valid specifications",
        "run_specs execution",
        "complete specification-result table",
    ],
    "teaching_values_not_inherited": [
        "min_quality",
        "sample_stride",
        "aoi_radius",
    ],
    "study_decisions_required": [
        "canonical source mapping",
        "endpoint definition",
        "specification factors and levels",
        "validity rules",
        "AOI geometry",
        "QC/exclusion policy",
    ],
}
```

This record is intentionally descriptive. It does not make any scientific decision.

## 3. Bind the real study source

Replace the tutorial's already-clean `study` object with an explicit source mapping.

For example:

```python
from pathlib import Path

import pandas as pd

from gazeaudit import GazeStudy

source = Path("canonical-study.csv")
data = pd.read_csv(source)

study = GazeStudy(
    data,
    x="gaze_x",
    y="gaze_y",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)
```

The column names above are still part of this **synthetic walkthrough**. In a real handoff, use the actual canonical columns and record their units.

Then run structural preflight before scientific specification execution.

## 4. Replace the teaching dictionary with a decision inventory

Do not jump directly from three tutorial values to three new numbers.

First write what must be decided:

```python
decision_inventory = {
    "min_quality": {
        "status": "study decision",
        "levels": None,
        "rationale": None,
    },
    "sample_stride": {
        "status": "study decision or not applicable",
        "levels": None,
        "rationale": None,
    },
    "aoi_radius": {
        "status": "rebuild from real stimulus or not applicable",
        "levels": None,
        "rationale": None,
    },
}
```

A `None` here is a useful stop condition: the real audit is not ready merely because the tutorial was runnable.

## 5. Define the endpoint in words

Before implementing the endpoint function, write its contract.

For this synthetic exercise:

> For every valid specification, compute the same participant-level contrast in the same direction using the same analysis population implied by that specification.

A real study needs more detail than this example. Record the unit of analysis, grouping, sign convention, denominator behavior, and any aggregation.

Only then implement the callable used by `run_specs`.

## 6. Declare real alternatives before execution

Once the study team has justified the levels, construct the real specification space.

The shape is:

```python
declared_choices = {
    # "factor_name": (<declared level 1>, <declared level 2>, ...),
}

space = PipelineSpace(choices=declared_choices)
```

The empty dictionary shown here is deliberate. This walkthrough does not fabricate replacement thresholds to make the block look complete.

Before running, verify for each factor:

- the factor is scientifically or methodologically relevant;
- every level is defensible;
- invalid combinations are identifiable before outcome inspection;
- the endpoint remains the same across valid branches;
- the choice is recorded in the study decision log.

## 7. Keep technical validity separate from scientific choice

A validity predicate can prevent nonsensical combinations from executing:

```python
results = run_specs(
    study,
    space,
    endpoint,
    valid_if=valid_if,
)
```

But `valid_if` is not a tool for removing inconvenient results after execution.

Its rules should be declared from the design or computational contract before inspecting the branch outcomes.

## 8. Reconcile the execution denominator

After execution, keep four quantities conceptually separate:

```text
declared specifications
→ valid specifications
→ valid successful specifications
→ valid technical failures
```

Do not silently drop a valid branch because it failed technically. Diagnose, preserve, and rerun through the governed failure-recovery route when appropriate.

Use [Failed-audit recovery]({{ '/docs/examples/failed-audit-recovery/' | relative_url }}) for the detailed pattern.

## 9. Keep the tutorial outside the evidence record

The study archive can record that a tutorial informed the **software workflow**, but synthetic tutorial results are not study evidence.

A compact handoff note can say:

```text
Workflow structure adapted from:
  GazeAudit end-to-end robustness example

Not inherited:
  teaching thresholds, AOI sizes, sampling levels, endpoint values,
  exclusions, conclusions, or synthetic outputs

Study-owned decisions:
  recorded separately with rationale and timing
```

That distinction protects both reproducibility and interpretation.

## Before-and-after summary

| Teaching example | Real-study handoff |
|---|---|
| values chosen to expose mechanics | values justified from the study |
| clean known data | canonical source + structural preflight |
| compact illustrative endpoint | explicitly defined research endpoint |
| small demonstrative decision space | declared defensible specification space |
| synthetic output | study-owned execution record |
| example interpretation | bounded interpretation from the real denominator |

## Final gate

Do not call the adaptation complete until you can answer **yes** to all of these:

- Is every concrete teaching value either replaced, justified, or marked not applicable?
- Is the endpoint defined independently of the tutorial's output?
- Are AOIs tied to the real stimulus and coordinate system?
- Are QC/exclusion decisions recorded as researcher-owned decisions?
- Is the valid specification set defined before outcome inspection?
- Is every valid technical failure preserved?
- Is the software revision/environment recorded?
- Are synthetic outputs excluded from the empirical evidence claim?

Return to [Adapt a synthetic example to your study]({{ '/docs/guides/adapt-examples-to-study/' | relative_url }}) for the general procedure.
