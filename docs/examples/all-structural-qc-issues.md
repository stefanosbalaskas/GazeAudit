---
title: All structural-QC issues in one synthetic table
description: A fully synthetic GazeAudit example exercising all five implemented structural-QC issue families and all ten current diagnostic detail codes, with interpretation, decision, reporting, and limitation guidance.
kicker: Example · Structural QC
page_type: example
permalink: /docs/examples/all-structural-qc-issues/
search_category: Example
search_keywords: structural qc all issues coordinate_nonfinite timestamp_nonfinite identifier_missing timestamp_duplicate timestamp_decreasing x_missing y_infinite diagnostics triage
example_data: "Synthetic"
example_focus: "Data & QC"
example_reuse: "Complete structural-QC diagnostic and triage pattern"
example_output: "One review report plus row/group diagnostics covering all current issue families and detail-code types"
example_boundary: "Synthetic flags demonstrate software behavior; they are not default repair, retention, exclusion, or quality rules."
---

# All structural-QC issues in one synthetic table

This example is deliberately constructed to exercise every currently implemented structural-QC issue family:

- `coordinate_nonfinite`;
- `timestamp_nonfinite`;
- `identifier_missing`;
- `timestamp_duplicate`;
- `timestamp_decreasing`.

It also exercises all ten current **detail-code types**. Because two rows participate in one duplicate timestamp key, the diagnostic table contains eleven records.

<div class="callout warning">
<strong>Teaching fixture, not a data-cleaning recipe.</strong>
The values below are synthetic failure cases selected to demonstrate software behavior. Do not copy their frequency, handling, or implied severity into a real study.
</div>

## Build the synthetic table

```python
import numpy as np
import pandas as pd

from gazeaudit import GazeStudy

frame = pd.DataFrame(
    {
        "participant_id": ["P01", "P01", "P01", None, "P02", "P02", "P03"],
        "trial_id": ["A", "A", "A", "A", "B", "B", None],
        "time_ms": [0.0, 0.0, np.nan, 2.0, 2.0, 1.0, np.inf],
        "gaze_x_px": [100.0, np.nan, np.inf, 103.0, 200.0, 201.0, 300.0],
        "gaze_y_px": [50.0, 51.0, 52.0, np.nan, 60.0, np.inf, 70.0],
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
```

The table remains constructible because the mapped coordinate/time columns are numeric and every required source column exists. Missing/infinite values remain explicit.

## Run structural preflight

```python
from gazeaudit import audit_study_qc

report = audit_study_qc(study)

print(report.status)
print(report.issue_codes)
print(report.to_frame())
```

Expected structural summary:

```text
status: review
issue_codes:
  coordinate_nonfinite
  timestamp_nonfinite
  identifier_missing
  timestamp_duplicate
  timestamp_decreasing

coordinate_issue_rows: 4
timestamp_issue_rows: 2
missing_identifier_rows: 2
duplicate_timestamp_rows: 2
decreasing_time_groups: 1
```

The denominators are deliberately mixed:

- the first four counts above are **rows**;
- `decreasing_time_groups` counts participant × trial **groups**.

Do not sum them into a single number of “bad observations.” One row can also contribute to more than one condition.

## Inspect every diagnostic record

```python
from gazeaudit import study_qc_diagnostics

diagnostics = study_qc_diagnostics(study)

print(
    diagnostics[
        [
            "diagnostic_id",
            "scope",
            "issue_code",
            "detail_code",
            "row_position",
            "participant",
            "trial",
            "timestamp",
        ]
    ]
)
```

For this exact synthetic representation, the diagnostic sequence is deterministic:

| ID | Scope | Issue | Detail | Why it appears |
|---|---|---|---|---|
| `D000001` | row | `timestamp_duplicate` | `timestamp_duplicate` | first `P01 × A × 0.0` row |
| `D000002` | row | `coordinate_nonfinite` | `x_missing` | horizontal coordinate missing |
| `D000003` | row | `timestamp_duplicate` | `timestamp_duplicate` | second `P01 × A × 0.0` row |
| `D000004` | row | `coordinate_nonfinite` | `x_infinite` | horizontal coordinate infinite |
| `D000005` | row | `timestamp_nonfinite` | `timestamp_missing` | timestamp missing |
| `D000006` | row | `coordinate_nonfinite` | `y_missing` | vertical coordinate missing |
| `D000007` | row | `identifier_missing` | `participant_missing` | participant ID missing |
| `D000008` | row | `coordinate_nonfinite` | `y_infinite` | vertical coordinate infinite |
| `D000009` | row | `timestamp_nonfinite` | `timestamp_infinite` | timestamp infinite |
| `D000010` | row | `identifier_missing` | `trial_missing` | trial ID missing |
| `D000011` | group | `timestamp_decreasing` | `timestamp_decreasing` | finite `P02 × B` time goes 2.0 → 1.0 |

The IDs are stable only for this deterministic study representation. If mapped values or row order change, rerun the diagnostics and do not carry old IDs forward.

## Triage by meaning, not by code alone

### 1. `coordinate_nonfinite`

The fixture contains missing and infinite x/y coordinates. In real data, first determine whether these represent tracker loss, an export convention, a failed transformation, or another documented state.

Do not automatically replace them with zero or interpolate them.

### 2. `timestamp_nonfinite`

The fixture contains one missing and one infinite timestamp.

A time-dependent endpoint cannot treat these as ordinary finite times. Whether the row can be repaired depends on authoritative source information.

### 3. `identifier_missing`

One row lacks a participant ID and another lacks a trial ID.

The package reports the ambiguity but does not invent grouping identifiers. Recover IDs only from defensible source provenance.

### 4. `timestamp_duplicate`

Two rows share `P01 × A × 0.0`, so **both rows** are counted and diagnosed.

In a real export, inspect whether this is a valid simultaneous-channel representation, limited timestamp precision, or actual duplication before deciding.

### 5. `timestamp_decreasing`

Within `P02 × B`, finite time appears as `2.0, 1.0` in observed row order.

Do not sort automatically. Establish the intended temporal order from source/processing provenance first.

## Use the clinic as a lookup layer

The [Structural QC Issue Clinic]({{ '/docs/reference/qc-issue-clinic/' | relative_url }}) exposes each issue family, its report field, current detail codes, inspection route, common representation causes, and “do not infer” boundary.

The clinic is reference material. The [Structural-QC triage guide]({{ '/docs/guides/structural-qc-triage/' | relative_url }}) is the task-oriented procedure.

## Record one illustrative decision

Suppose source documentation establishes that the two duplicate timestamps are valid simultaneous-channel records.

An explicit decision could be:

```python
from gazeaudit import StudyQCDecision, build_study_qc_audit

duplicate_decision = StudyQCDecision(
    issue_code="timestamp_duplicate",
    action="retain after representation review",
    rationale=(
        "Source documentation identifies the two rows as simultaneous "
        "channel records rather than duplicated observations."
    ),
    diagnostic_ids=("D000001", "D000003"),
)

audit = build_study_qc_audit(
    study,
    decisions=(duplicate_decision,),
)
```

That decision is valid only under the hypothetical source evidence stated here. It is **not** a recommendation to retain duplicate timestamps generally.

Other unresolved issue families remain unresolved until separately inspected and documented.

## A repair creates a new evidence state

Imagine authoritative source information shows that `P02 × B` was accidentally concatenated in reverse order.

A repair might change row order. After that change:

```python
repaired_study = GazeStudy(
    repaired_frame,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)

repaired_report = audit_study_qc(repaired_study)
repaired_diagnostics = study_qc_diagnostics(repaired_study)
```

Do not edit the old diagnostic record to make it look as though the decreasing-time condition never occurred.

Preserve the before/after provenance and rerun downstream operations affected by the changed representation.

## Reporting practice

### Methods example

> Structural preflight evaluated non-finite gaze coordinates and timestamps, missing canonical identifiers, duplicate participant × trial timestamps, and decreasing within-unit time. Row/group diagnostics were inspected against source and preprocessing provenance, and researcher-owned actions were recorded explicitly.

### Results example for this synthetic fixture

> The synthetic preflight returned `review` and exercised all five implemented structural issue families. Four rows contained non-finite coordinates, two rows contained non-finite timestamps, two rows lacked a canonical identifier, two rows participated in a duplicate timestamp key, and one participant × trial group had decreasing finite time.

This numerical statement belongs only to this synthetic teaching fixture.

### Limitation wording

> Structural preflight identifies a bounded set of representation-level conditions; it does not determine calibration accuracy, event-detector validity, AOI validity, missingness mechanism, or inferential robustness.

## API links

- [`audit_study_qc()`]({{ '/docs/reference/api-pathways/#api-audit-study-qc' | relative_url }})
- [`study_qc_diagnostics()`]({{ '/docs/reference/api-pathways/#api-study-qc-diagnostics' | relative_url }})
- [`build_study_qc_audit()`]({{ '/docs/reference/api-pathways/#api-build-study-qc-audit' | relative_url }})
- [Structural-QC method pathway]({{ '/docs/reference/api-pathways/#path-structural-qc' | relative_url }})

## Next steps

- [Structural-QC triage]({{ '/docs/guides/structural-qc-triage/' | relative_url }}) — inspection, decision, repair, rerun, endpoint dependence, and reporting.
- [Data onboarding]({{ '/docs/guides/data-onboarding/' | relative_url }}) — deterministic QC audit artifacts and fingerprints.
- [Data-mapping provenance]({{ '/docs/guides/data-mapping-provenance/' | relative_url }}) — preserve source/mapping/unit/transformation identity.
- [Analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}) — evaluate declared thresholds only after the structural evidence is understood.
