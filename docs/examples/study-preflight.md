---
title: Study preflight example
description: Run the structural QC API on a deterministic synthetic GazeStudy and interpret review flags without automatic exclusion.
kicker: Example · Data QC
permalink: /docs/examples/study-preflight/
---

# Study preflight example

This example uses the repository script `examples/study_preflight.py`. It is intentionally small and deterministic so the structural-QC contract can be inspected without downloading data or making network requests.

The synthetic table contains two conditions that deserve review:

1. one row has a missing horizontal coordinate;
2. two rows in the same participant × trial unit share the same finite timestamp.

Neither condition is converted automatically into a participant/trial exclusion.

<figure class="plot-card">
  <img src="{{ '/assets/images/study-preflight.svg' | relative_url }}" alt="Synthetic five-row GazeStudy flowing through structural preflight checks, with one missing x coordinate and two duplicate timestamp rows producing review status">
  <figcaption>Synthetic illustration. `review` means inspect and document the structural condition; it is not a universal data-rejection rule.</figcaption>
</figure>

## Run the repository example

```bash
python examples/study_preflight.py
```

The script constructs the canonical study with explicit semantic column mapping:

```python
import pandas as pd

from gazeaudit import GazeStudy, audit_study_qc

frame = pd.DataFrame(
    {
        "participant_id": ["P01", "P01", "P01", "P02", "P02"],
        "trial_id": ["ad_1", "ad_1", "ad_1", "ad_2", "ad_2"],
        "time_ms": [0.0, 16.7, 16.7, 0.0, 33.4],
        "gaze_x_px": [520.0, 523.0, None, 610.0, 615.0],
        "gaze_y_px": [410.0, 412.0, 414.0, 390.0, 394.0],
    }
)

study = GazeStudy(
    frame,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)

report = audit_study_qc(study)
```

## Expected result

The example returns a machine-readable payload. The important fields are:

```text
status: review
issue_codes: ('coordinate_nonfinite', 'timestamp_duplicate')
coordinate_issue_rows: 1
duplicate_timestamp_rows: 2
```

The duplicate count is **two rows**, not one duplicate event: both rows participating in the repeated participant × trial × timestamp key are reported.

## Export a compact QC table

`StudyQCReport.to_frame()` converts the report into a two-column table suitable for inspection or export:

```python
qc_table = report.to_frame()
print(qc_table)
```

The table contains the primitive counts plus `status` and `has_structural_issues`. `issue_codes` remains available on the report and in `to_dict()`.

## Use issue codes for transparent branching

A pipeline can react to declared structural conditions without hiding the decision:

```python
if "coordinate_nonfinite" in report.issue_codes:
    print("Document how non-finite coordinates are handled before AOI analysis.")

if "timestamp_duplicate" in report.issue_codes:
    print("Inspect whether duplicate timestamps represent valid simultaneous records.")
```

This is deliberately different from silently dropping affected rows.

## What a clean report means

When no implemented structural condition is present:

```python
assert report.status == "pass"
assert report.issue_codes == ()
```

A `pass` means only that this structural preflight found no implemented issue. It does **not** establish calibration quality, detector validity, absence of informative missingness, correct AOI design, or robustness of the substantive conclusion.

## Continue the workflow

- [Data onboarding and structural preflight]({{ '/docs/guides/data-onboarding/' | relative_url }}) — full interpretation contract.
- [AOI uncertainty]({{ '/docs/guides/aoi-uncertainty/' | relative_url }}) — model spatial measurement uncertainty.
- [Interoperability]({{ '/docs/guides/interoperability/' | relative_url }}) — ingest supported BIDS/pymovements structures.
- [End-to-end robustness audit]({{ '/docs/examples/end-to-end-robustness/' | relative_url }}) — move from one canonical study to a declared specification space.
