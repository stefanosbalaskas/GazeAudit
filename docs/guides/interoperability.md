---
title: Interoperability guide
description: Use GazeAudit with Eye-Tracking-BIDS, pymovements, pEYES, and custom adapters without blurring software responsibilities.
kicker: Guide · Ecosystem
---

# Interoperability guide

GazeAudit is not intended to replace mature parsing or event-detection libraries. Its interoperability layer is deliberately narrow: external packages retain responsibility for their own semantics, while GazeAudit normalises only the information required for uncertainty and robustness analysis.

## Eye-Tracking-BIDS ingestion

```python
from gazeaudit import read_bids_eyetrack

record = read_bids_eyetrack(
    "sub-01_task-search_recording-eye1_physio.tsv.gz"
)

study = record.study
```

The reader normalises the eye-tracking record into a canonical `GazeStudy` while retaining relevant source metadata. Timestamps are normalised to milliseconds under the adapter contract.

Separate eye files remain separate participant-by-trial streams by default. GazeAudit is not presented as a replacement for the official BIDS Validator.

## pymovements

Install the optional extra:

```bash
python -m pip install "gazeaudit[pymovements]==0.1.0"
```

Then adapt a `pymovements.Gaze` object:

```python
from gazeaudit import from_pymovements_gaze

study = from_pymovements_gaze(
    gaze,
    coordinate="pixel",
    component="auto",
    participant_id="p01",
)
```

`component="auto"` accepts only two-component coordinates. Binocular four- or six-component vectors require an explicit `left`, `right`, or `cyclopian` choice. GazeAudit does not silently choose or average an eye.

A `pymovements.Dataset` can be adapted with `from_pymovements_dataset()` when dataset-level ingestion is more appropriate.

## pEYES detector execution

The current pEYES integration is available on Python 3.12+ under the package dependency range.

```bash
python -m pip install "gazeaudit[peyes]==0.1.0"
```

Create and run a detector:

```python
from gazeaudit import make_peyes_detector, run_peyes_detector

ivt = make_peyes_detector(
    "ivt",
    min_event_duration=40,
    saccade_velocity_threshold=30,
)

result = run_peyes_detector(
    study,
    ivt,
    viewer_distance_cm=60,
    pixel_size_cm=0.027,
)
```

The returned `DetectionResult` keeps sample labels separate from per-trial detector metadata so detector outputs can be compared through one normalised robustness contract.

## Custom study adapters

Third-party study objects can implement the runtime-checkable `StudyAdapter` protocol. The purpose is to translate external data into a `GazeStudy`, not to force external packages to adopt GazeAudit internals.

```python
from gazeaudit import adapt_study

study = adapt_study(my_adapter, external_object)
```

## Custom detector backends

A custom detector integration can implement `DetectorBackend` and return `DetectionResult` through `run_detector_backend()`.

This makes it possible to evaluate multiple detector families in a declared `PipelineSpace` without pretending that the detectors are methodologically identical.

## Responsibility boundary

| Task | Primary owner |
|---|---|
| Raw device acquisition | Tracker/vendor or acquisition software |
| Format-specific parsing | Source ecosystem / adapter |
| Event-detection algorithm semantics | Detector package |
| Canonical gaze representation | GazeAudit adapter layer |
| Measurement-error propagation | GazeAudit |
| Specification-space execution | GazeAudit |
| Robustness/sensitivity diagnostics | GazeAudit |
| Provenance/fingerprint audit bundle | GazeAudit |

<div class="callout info">
<strong>Why the boundary matters</strong>
Interoperability should preserve scientific provenance. A normalised interface is useful only if it does not erase which external package, detector, component choice, coordinate system, or source record produced the input.
</div>

## Version pinning

For formal validation or publication work, pin the versions of external packages that materially affect parsing or detector semantics. GazeAudit's own validation workflows verify expected upstream versions where those versions are part of a frozen protocol.

## Next

Use the [API map](../reference/api-map/) to find adapter functions or incorporate an external detector choice into the [robustness workflow](../workflows/robustness-audit/).
