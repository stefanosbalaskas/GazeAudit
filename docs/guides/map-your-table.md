---
title: Map your table into GazeStudy
description: Turn an existing gaze or fixation table into a canonical GazeStudy while preserving source names, units, structural review conditions, and preprocessing provenance.
kicker: Guide · Data mapping
permalink: /docs/guides/map-your-table/
search_category: Guide
search_keywords: map table csv GazeStudy columns participant trial timestamp x y units schema source preprocessing structural preflight
---

# Map your table into GazeStudy

Use this guide when you have an existing pandas table or CSV and need to construct the canonical GazeAudit study representation.

The goal is **not** to force every source into one vendor schema. The goal is to make the semantic mapping explicit and reproducible.

For the compact contract and interactive snippet builder, use the [Data Contract & Schema Mapping Center]({{ '/docs/data-contract/' | relative_url }}).

## 1. Inventory the source before renaming anything

Write down the source columns that carry these five roles:

| Semantic role | Question to answer |
|---|---|
| x | Which numeric column represents horizontal gaze/fixation position? |
| y | Which numeric column represents vertical gaze/fixation position? |
| timestamp | Which numeric column carries within-trial time or another ordered time-like coordinate? |
| participant | Which column identifies the participant? |
| trial | Which column identifies the within-participant trial or analysis unit? |

Do not rename columns merely to make them look canonical. `GazeStudy` accepts the original source names.

## 2. Record units separately from names

A column name such as `gaze_x` does not tell GazeAudit whether the value is:

- pixels;
- normalized display coordinates;
- degrees of visual angle;
- stimulus-relative coordinates;
- another documented spatial system.

Likewise, `time` does not identify whether values are seconds, milliseconds, sample numbers, or another numeric scale.

Record units and coordinate conventions as preprocessing/provenance metadata. The constructor validates numeric dtype, not scientific unit suitability.

## 3. Read the table

For a CSV:

```python
import pandas as pd

frame = pd.read_csv("canonical-analysis-table.csv")
```

Keep import transformations explicit. If you parse decimal separators, convert timestamps, merge binocular channels, rescale coordinates, or derive a trial identifier, document those transformations before constructing the study.

## 4. Check the source dtypes

Inspect the five mapped columns:

```python
columns = [
    "participant_id",
    "trial_id",
    "time_ms",
    "gaze_x_px",
    "gaze_y_px",
]

print(frame[columns].dtypes)
```

The x, y, and timestamp mappings must be numeric pandas dtypes. Participant and trial columns can use string, integer, categorical, or another identifier-compatible dtype.

Missing values in numeric columns do not automatically prevent construction when the dtype remains numeric. They become structural-preflight evidence.

## 5. Construct the semantic mapping

For example:

```python
from gazeaudit import GazeStudy

study = GazeStudy(
    frame,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)
```

The names above are illustrative. Use the exact columns in your table.

The original table remains available through `study.data`. Additional columns are preserved.

## 6. Distinguish constructor errors from review conditions

The constructor fails closed when:

- `data` is not a pandas `DataFrame`;
- one of the five mapped columns is absent;
- x, y, or timestamp is nonnumeric;
- the table has zero observations.

Other conditions belong to structural review instead:

- missing coordinate values;
- infinite coordinate values;
- missing/infinite timestamp values;
- missing participant/trial identifiers;
- duplicate timestamps;
- decreasing within-trial time.

This distinction prevents structural observations from being silently turned into automatic exclusions.

## 7. Check time order explicitly

Construction does not require monotonically increasing timestamps.

To request a fail-fast order check:

```python
study.validate_time_order()
```

This ignores non-finite timestamp values when checking decreases and raises when finite timestamps decrease within a participant × trial unit.

For a diagnostic rather than fail-fast workflow, use structural preflight.

## 8. Run structural preflight

```python
from gazeaudit import audit_study_qc

report = audit_study_qc(study)

print(report.status)
print(report.issue_codes)
print(report.to_frame())
```

Interpret `review` as “inspect and document”, not “exclude”.

A `pass` also has a narrow meaning: none of the implemented structural conditions were detected. It does not establish calibration, event-detection, AOI, missingness, or inferential validity.

## 9. Preserve source and mapping provenance

Record at minimum:

- source file or immutable source identifier;
- source export / preprocessing version;
- exact participant/trial/timestamp/x/y mapping;
- coordinate units and orientation;
- timestamp unit and origin;
- any transformations applied before construction;
- structural-preflight result;
- researcher decision for each flagged condition.

A compact mapping note is often sufficient:

```text
source: exports/session_level_long.csv
participant: participant_code
trial: stimulus_trial
timestamp: recording_time_ms — milliseconds from trial onset
x: screen_x_px — display pixels, left-to-right
y: screen_y_px — display pixels, top-to-bottom
preprocessing: binocular channels combined before this table
```

## 10. Do not silently coerce a bad schema

Avoid repairs such as:

- converting arbitrary strings to numeric with coercion-to-missing and proceeding silently;
- inventing trial IDs when the analysis unit is ambiguous;
- replacing missing identifiers with a placeholder participant/trial;
- sorting rows without recording why;
- converting timestamp units without recording the transformation;
- dropping rows solely to make `GazeStudy` construct successfully.

Repair the source transformation deliberately, then reconstruct and rerun preflight.

## 11. Use extra columns explicitly downstream

Conditions, stimulus names, AOI labels, quality measures, fixation duration, pupil diameter, device metadata, and other variables stay in `study.data`.

When a downstream endpoint or specification needs one, require it explicitly instead of assuming its presence:

```python
study.require_columns(["condition", "quality"])
```

That call checks column presence. It does not decide whether the variable's coding or values are scientifically appropriate.

## 12. Safe mapping checklist

Before downstream analysis:

- [ ] the canonical source is identified;
- [ ] the five semantic roles are mapped to real source columns;
- [ ] x/y/timestamp dtypes are numeric;
- [ ] coordinate units and orientation are recorded;
- [ ] timestamp unit and origin are recorded;
- [ ] any preprocessing transformation is recorded;
- [ ] constructor errors were repaired at the source/mapping level;
- [ ] structural preflight was run;
- [ ] review conditions were inspected rather than automatically excluded;
- [ ] researcher-owned decisions are recorded.

Continue to [Valid, invalid, and reviewable tables]({{ '/docs/examples/data-contract-valid-invalid/' | relative_url }}) to practise the distinction with synthetic cases, then use [Data onboarding and structural preflight]({{ '/docs/guides/data-onboarding/' | relative_url }}) for the full QC/provenance workflow.
