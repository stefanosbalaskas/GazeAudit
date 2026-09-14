---
title: Study preflight example
description: Run structural QC, inspect row/group diagnostics, record decisions, and preserve deterministic provenance.
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

The script constructs the canonical study with explicit semantic column mapping and then builds a provenance-aware `StudyQCAudit`.

```python
import pandas as pd

from gazeaudit import GazeStudy

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
```

## Expected structural result

The important summary fields remain:

```text
status: review
issue_codes: ('coordinate_nonfinite', 'timestamp_duplicate')
coordinate_issue_rows: 1
duplicate_timestamp_rows: 2
```

The duplicate count is **two rows**, not one duplicate event: both rows participating in the repeated participant × trial × timestamp key are reported.

## Inspect the diagnostics before deciding

```python
from gazeaudit import study_qc_diagnostics

diagnostics = study_qc_diagnostics(study)
print(diagnostics[["diagnostic_id", "issue_code", "detail_code", "row_position"]])
```

For this fixture the deterministic diagnostics are:

| Diagnostic | Issue | Detail | Scope |
|---|---|---|---|
| `D000001` | `timestamp_duplicate` | `timestamp_duplicate` | row |
| `D000002` | `coordinate_nonfinite` | `x_missing` | row |
| `D000003` | `timestamp_duplicate` | `timestamp_duplicate` | row |

The ID is a stable reference **within the deterministic study representation being audited**. If mapped data or row order changes, rerun the audit rather than carrying old IDs forward.

## Record what you decided

The repository example records two explicit decisions:

```python
from gazeaudit import StudyQCDecision, build_study_qc_audit

decisions = (
    StudyQCDecision(
        issue_code="coordinate_nonfinite",
        action="retain for explicit downstream missingness handling",
        rationale=(
            "The missing coordinate is retained so its handling remains visible "
            "to the downstream sensitivity analysis."
        ),
        diagnostic_ids=("D000002",),
    ),
    StudyQCDecision(
        issue_code="timestamp_duplicate",
        action="retain after representation review",
        rationale=(
            "The repeated timestamp is documented rather than silently deduplicated."
        ),
        diagnostic_ids=("D000001", "D000003"),
    ),
)

audit = build_study_qc_audit(study, decisions=decisions)
```

These actions are illustrative, not recommended defaults. A real dataset may justify repair, exclusion, channel combination, reordering, retention, or another documented treatment.

## Read the provenance fingerprints

```python
print(audit.study_fingerprint)
print(audit.audit_fingerprint)
print(audit.manifest_fingerprint)
```

The three levels answer different questions:

- `study_fingerprint` — are the five mapped structural-QC columns and their row order the same?
- `audit_fingerprint` — are the study identity, structural findings, and researcher decisions the same?
- `manifest_fingerprint` — is that audit record also bound to the same recorded software environment?

The study fingerprint deliberately excludes unrelated columns that structural QC did not inspect.

## Export evidence

```python
from gazeaudit import write_study_qc_artifacts, verify_study_qc_artifacts

write_study_qc_artifacts(audit, "qc-evidence")
assert verify_study_qc_artifacts("qc-evidence")
```

This writes deterministic report/diagnostic/decision data plus an audit manifest and a byte-level artifact manifest. Editing one exported payload causes verification to fail.

## Bind the QC record into a publication audit

```python
from gazeaudit import study_qc_publication_metadata

qc_metadata = study_qc_publication_metadata(audit)

bundle = build_conclusion_audit_bundle(
    results,
    reference_effect=reference_effect,
    rule=rule,
    title="Primary robustness audit",
    endpoint="primary endpoint",
    source_description="Analysis dataset",
    metadata={"study_qc": qc_metadata},
)
```

The compact QC descriptor becomes part of the publication bundle's existing scientific fingerprint. The publication schema itself does not change.

## What a clean report means

When no implemented structural condition is present:

```python
assert audit.report.status == "pass"
assert audit.report.issue_codes == ()
```

A `pass` means only that this structural preflight found no implemented issue. It does **not** establish calibration quality, detector validity, absence of informative missingness, correct AOI design, or robustness of the substantive conclusion.

## Continue the workflow

- [Data onboarding and structural preflight]({{ '/docs/guides/data-onboarding/' | relative_url }}) — full interpretation and provenance contract.
- [Publication audit guide]({{ '/docs/guides/publication-audits/' | relative_url }}) — bind QC identity into robustness evidence.
- [AOI uncertainty]({{ '/docs/guides/aoi-uncertainty/' | relative_url }}) — model spatial measurement uncertainty.
- [Interoperability]({{ '/docs/guides/interoperability/' | relative_url }}) — ingest supported BIDS/pymovements structures.
- [End-to-end robustness audit]({{ '/docs/examples/end-to-end-robustness/' | relative_url }}) — move from one canonical study to a declared specification space.
