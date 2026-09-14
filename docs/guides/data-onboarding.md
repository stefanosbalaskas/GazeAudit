---
title: Data onboarding and structural preflight
description: Map vendor or analysis tables into GazeStudy, inspect structural QC, and decide what must be reviewed before uncertainty or robustness analysis.
kicker: Guide · Data
permalink: /docs/guides/data-onboarding/
---

# Data onboarding and structural preflight

GazeAudit deliberately does not require a vendor-specific export schema. The first job is therefore to create a canonical `GazeStudy` that tells the package which columns represent horizontal position, vertical position, time, participant, and trial. The second job is to inspect whether that representation contains structural conditions that deserve review before downstream analysis.

This guide separates those two steps. **Structural QC is not scientific validity.** A table can pass these checks and still have poor calibration, unsuitable event detection, inappropriate AOIs, or an analytically weak endpoint. Conversely, a flagged condition is not automatically an exclusion rule.

## 1. Start from the table you actually have

A conventional CSV can keep its original names:

```python
import pandas as pd

from gazeaudit import GazeStudy

frame = pd.read_csv("my_eye_tracking_export.csv")

study = GazeStudy(
    frame,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)
```

`GazeStudy` stores the original table and the semantic mapping. You do **not** have to rename every vendor column to `x`, `y`, `timestamp`, `participant`, and `trial`.

The five mapped columns must exist. Coordinates and timestamps must be numeric, and the table must contain at least one row. Additional columns—condition labels, fixation duration, pupil size, stimulus identifiers, AOI labels, quality flags, or experimental covariates—remain available in `study.data`.

## 2. Run the structural preflight

Use `audit_study_qc()` before building an uncertainty model or specification space:

```python
from gazeaudit import audit_study_qc

report = audit_study_qc(study)

print(report.status)
print(report.issue_codes)
print(report.to_frame())
```

The result is a frozen `StudyQCReport` with raw counts plus derived fields.

### What is checked

| Condition | Report field | Interpretation |
|---|---|---|
| missing x/y values | `missing_x_rows`, `missing_y_rows` | rows where a mapped coordinate is missing |
| infinite x/y values | `infinite_x_rows`, `infinite_y_rows` | rows containing `+inf` or `-inf` coordinates |
| any non-finite coordinate | `coordinate_issue_rows` | rows where x or y is missing or infinite |
| missing timestamps | `missing_timestamp_rows` | rows without a finite observed time value |
| infinite timestamps | `infinite_timestamp_rows` | rows containing `+inf` or `-inf` time |
| any non-finite timestamp | `timestamp_issue_rows` | rows where the mapped timestamp is missing or infinite |
| missing participant/trial IDs | `missing_identifier_rows` | rows that cannot be unambiguously assigned to both canonical identifiers |
| repeated timestamps | `duplicate_timestamp_rows` | rows sharing participant, trial, and finite timestamp with another row |
| decreasing time within unit | `decreasing_time_groups` | participant × trial units whose finite timestamps decrease in observed row order |

`n_rows`, `n_participants`, and `n_trials` are also recorded so the preflight can be saved with the analysis record.

## 3. Read `status` conservatively

The report exposes only two descriptive states:

- `pass` — none of the implemented structural conditions were detected;
- `review` — at least one implemented condition was detected.

`review` does **not** mean “bad dataset”, and `pass` does **not** mean “validated dataset”. GazeAudit intentionally does not convert these counts into a universal quality score or automatic exclusion decision.

Stable symbolic `issue_codes` make the report easy to inspect programmatically:

```python
if "timestamp_decreasing" in report.issue_codes:
    print("Inspect within-trial row ordering before time-dependent analysis.")
```

The current codes are:

- `coordinate_nonfinite`
- `timestamp_nonfinite`
- `identifier_missing`
- `timestamp_duplicate`
- `timestamp_decreasing`

## 4. Why duplicate timestamps are a review flag, not an automatic failure

Repeated timestamps can arise for several reasons: binocular records represented as separate rows, merged channels, acquisition-system resolution, duplicated exports, or preprocessing mistakes. GazeAudit therefore reports the condition but does not decide what it means for your study.

The correct response is to inspect the representation and acquisition semantics. If duplicates represent valid simultaneous channels, preserve that provenance. If they are accidental duplicated observations, repair the source transformation and rerun the preflight.

## 5. Why time order matters

Several downstream operations interpret observations in their presented within-trial order. A decreasing timestamp may therefore indicate that rows were concatenated or sorted incorrectly.

`GazeStudy.validate_time_order()` remains available when you explicitly want a fail-fast check:

```python
study.validate_time_order()
```

The preflight is less disruptive: it counts affected participant × trial units and leaves the decision to the researcher.

## 6. Nullable pandas columns are supported

Real imports often use pandas nullable dtypes such as `Float64`. The preflight treats `pd.NA` as missing rather than failing during numeric conversion.

```python
frame["gaze_x_px"] = frame["gaze_x_px"].astype("Float64")
report = audit_study_qc(study)
```

Missingness remains explicit in the report; it is not silently imputed.

## 7. Keep structural QC separate from measurement QC

Structural preflight answers questions such as:

- Are mapped coordinates finite?
- Are identifiers present?
- Is within-trial time order internally coherent?

It does **not** answer:

- Was calibration accurate enough for the scientific task?
- Is the gaze-error model appropriate?
- Are fixation/event detector settings defensible?
- Are AOI boundaries scientifically meaningful?
- Is missingness ignorable?
- Is the endpoint robust to defensible analytical choices?

Those questions belong to GazeAudit's uncertainty, detector, missingness, sampling, and robustness workflows.

## 8. A practical onboarding sequence

<div class="workflow-steps">
  <div class="workflow-step"><strong>Map</strong><p>Create a `GazeStudy` using the original table and explicit semantic column names.</p></div>
  <div class="workflow-step"><strong>Preflight</strong><p>Run `audit_study_qc()` and inspect every flagged condition in context.</p></div>
  <div class="workflow-step"><strong>Document</strong><p>Record any repair, exclusion, channel-combination, or sorting decision rather than silently mutating the table.</p></div>
  <div class="workflow-step"><strong>Audit</strong><p>Proceed to measurement uncertainty, detector robustness, sampling/missingness sensitivity, or specification-space analysis as appropriate.</p></div>
</div>

## 9. Complete executable example

The repository contains a deterministic example with a missing coordinate and repeated within-trial timestamp:

```bash
python examples/study_preflight.py
```

It intentionally returns `status == "review"` so users can see how issue codes and counts behave without needing external data.

## Recommended next pages

- [Getting started]({{ '/docs/getting-started/' | relative_url }}) — minimal uncertainty-aware AOI analysis.
- [Interoperability guide]({{ '/docs/guides/interoperability/' | relative_url }}) — BIDS, pymovements, pEYES, and custom adapters.
- [AOI uncertainty]({{ '/docs/guides/aoi-uncertainty/' | relative_url }}) — move from validation error to probabilistic AOI membership.
- [End-to-end robustness audit]({{ '/docs/examples/end-to-end-robustness/' | relative_url }}) — evaluate a complete declared analysis space.
