---
title: Valid, invalid, and reviewable tables
description: A fully synthetic walkthrough showing which table conditions prevent GazeStudy construction, which construct but require structural review, and which checks belong downstream.
kicker: Example · Data contract
page_type: example
permalink: /docs/examples/data-contract-valid-invalid/
search_category: Example
search_keywords: GazeStudy data contract valid invalid reviewable missing column nonnumeric empty timestamp duplicate decreasing missing identifier synthetic
example_data: "Synthetic"
example_focus: "Data & QC"
example_reuse: "Schema-validation and preflight pattern"
example_output: "A classified set of constructor failures and structural-review conditions"
example_boundary: "Passing the constructor or structural preflight does not establish measurement or scientific validity."
---

# Valid, invalid, and reviewable tables

This is a **fully synthetic data-contract exercise**. It separates three states that should not be collapsed:

1. **valid constructor input** — `GazeStudy` can represent the table;
2. **invalid constructor input** — the canonical representation cannot be created;
3. **reviewable structural condition** — construction succeeds, but structural preflight records something that requires interpretation.

No case on this page defines a universal exclusion rule.

## Baseline valid table

Start with a minimal long-form table:

```python
import pandas as pd

from gazeaudit import GazeStudy, audit_study_qc

base = pd.DataFrame(
    {
        "participant_id": ["P01", "P01", "P02", "P02"],
        "trial_id": ["T01", "T01", "T01", "T01"],
        "time_ms": [0.0, 16.7, 0.0, 16.7],
        "gaze_x_px": [500.0, 504.0, 610.0, 614.0],
        "gaze_y_px": [400.0, 402.0, 390.0, 394.0],
    }
)

study = GazeStudy(
    base,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)

report = audit_study_qc(study)
print(report.status)
```

For this fixture the structural status is `pass`.

That means only that the implemented structural checks found no issue. It does not establish calibration quality, AOI appropriateness, detector validity, sampling adequacy, or inferential robustness.

## Case 1 — missing mapped column: constructor failure

Remove the mapped y column:

```python
missing_y = base.drop(columns=["gaze_y_px"])

GazeStudy(
    missing_y,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)
```

Expected behavior: `ValueError` because the required mapped source column is absent.

This is a **schema failure**, not a structural-review flag. Repair the mapping or source transformation before proceeding.

## Case 2 — nonnumeric coordinate: constructor failure

Replace the horizontal coordinate with text:

```python
nonnumeric_x = base.copy()
nonnumeric_x["gaze_x_px"] = ["left", "left", "right", "right"]

GazeStudy(
    nonnumeric_x,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)
```

Expected behavior: `TypeError` because the mapped x column is not numeric.

Do not solve this by silently coercing arbitrary strings to missing values. If the source encodes coordinates as strings, define and record the intended conversion.

## Case 3 — empty table: constructor failure

```python
empty = base.iloc[0:0].copy()

GazeStudy(
    empty,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)
```

Expected behavior: `ValueError` because the canonical study must contain at least one observation.

## Case 4 — missing coordinate: construct, then review

Keep the column numeric but insert a missing value:

```python
missing_x = base.copy()
missing_x.loc[1, "gaze_x_px"] = float("nan")

study_missing_x = GazeStudy(
    missing_x,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)

report = audit_study_qc(study_missing_x)
print(report.status)
print(report.issue_codes)
```

Construction succeeds because the mapped column still has a numeric dtype.

Structural preflight reports a coordinate issue. The package does not silently impute the value or decide that the row, trial, or participant must be excluded.

## Case 5 — missing participant identifier: construct, then review

```python
missing_id = base.copy()
missing_id.loc[2, "participant_id"] = None

study_missing_id = GazeStudy(
    missing_id,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)

report = audit_study_qc(study_missing_id)
print(report.issue_codes)
```

The participant column exists, so construction succeeds.

Structural preflight records `identifier_missing`. Whether the source can be repaired, the row should be retained for another purpose, or the representation is unusable is researcher-owned.

## Case 6 — duplicate timestamp: construct, then review

```python
duplicate_time = base.copy()
duplicate_time.loc[1, "time_ms"] = 0.0

study_duplicate = GazeStudy(
    duplicate_time,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)

report = audit_study_qc(study_duplicate)
print(report.issue_codes)
```

Expected structural issue: `timestamp_duplicate`.

A duplicate can be a representation artifact, simultaneous channels, limited acquisition precision, or an error. GazeAudit reports it but does not choose the interpretation.

## Case 7 — decreasing timestamp: construct, review, optional fail-fast

```python
decreasing = base.copy()
decreasing.loc[1, "time_ms"] = -1.0

study_decreasing = GazeStudy(
    decreasing,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)
```

Construction still succeeds.

Structural preflight records a decreasing-time group. If your workflow requires an immediate stop instead:

```python
study_decreasing.validate_time_order()
```

That explicit method raises when finite timestamps decrease within a participant × trial unit.

The distinction matters: **constructor validity and temporal-order validity are separate contracts**.

## Case 8 — extra scientific columns: preserved, not interpreted

```python
with_condition = base.assign(
    condition=["control", "control", "treatment", "treatment"],
    quality=[0.92, 0.89, 0.95, 0.93],
)

study_extra = GazeStudy(
    with_condition,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)

assert "condition" in study_extra.data.columns
assert "quality" in study_extra.data.columns
```

`GazeStudy` preserves these columns but does not decide how their values should be interpreted.

A downstream endpoint or specification can fail explicitly if it needs one:

```python
study_extra.require_columns(["condition", "quality"])
```

Presence is not semantic validation.

## Summary table

| Case | Constructor | Structural preflight | Main lesson |
|---|---|---|---|
| baseline valid | succeeds | pass | constructor + implemented structural conditions satisfied |
| missing mapped column | fails | not reached | mapping/source schema must be repaired |
| nonnumeric x/y/time | fails | not reached | mapped numeric semantics must actually be numeric |
| empty table | fails | not reached | canonical representation needs observations |
| missing coordinate | succeeds | review | missingness remains explicit |
| missing participant/trial value | succeeds | review | identifier gaps are review evidence |
| duplicate time | succeeds | review | duplicate representation is contextual |
| decreasing time | succeeds | review | order check is separate; fail-fast is opt-in |
| extra columns | succeeds | depends on mapped fields | preserved does not mean interpreted |

## What not to infer

A table that constructs and receives `status == "pass"` is not automatically:

- calibrated accurately;
- sampled adequately;
- free from informative missingness;
- using defensible event detection;
- using valid AOIs;
- using a robust endpoint;
- ready for a scientific claim.

Use the [Data Contract & Schema Mapping Center]({{ '/docs/data-contract/' | relative_url }}) for the schema contract and [Data onboarding and structural preflight]({{ '/docs/guides/data-onboarding/' | relative_url }}) for the provenance-aware QC workflow.
