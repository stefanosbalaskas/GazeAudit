# GazeAudit

**Measurement uncertainty and inferential robustness for eye-tracking research.**

GazeAudit is a scientific Python package for asking a question that conventional eye-tracking pipelines rarely answer directly:

> Would the scientific conclusion survive other reasonable measurement and analytical choices?

The project combines two methodological pillars in one framework:

1. **Measurement uncertainty** — represent calibration/validation error, spatial uncertainty, and uncertain AOI membership instead of treating every observed gaze coordinate as exact.
2. **Analytical robustness** — evaluate defensible alternative preprocessing, QC, event-detection, AOI, missing-data, and sampling choices and quantify how much the scientific endpoint changes.

## Scientific scope

GazeAudit sits **above** existing eye-tracking preprocessing and event-detection tools rather than replacing them. Its methodological contribution is uncertainty propagation, specification-space analysis, robustness diagnostics, benchmarking, and reproducible audit reports, with explicit interoperability contracts for external scientific software.

```text
raw / processed gaze
        |
        v
measurement-error model
        |
        v
probabilistic AOI membership
        |
        v
alternative defensible pipelines
        |
        v
common scientific endpoint
        |
        v
robustness + uncertainty audit
```

## Development status

The repository is in **pre-alpha** development. The current scientific MVP line implements:

- a canonical vendor-neutral `GazeStudy` object;
- rectangle and circle AOI primitives;
- a transparent bivariate Gaussian gaze-error model fitted from validation targets;
- Monte Carlo probabilistic AOI membership;
- hard-vs-probabilistic AOI comparison, flip probabilities, and boundary-risk summaries;
- uncertainty-weighted dwell time and fixation counts;
- declarative `PipelineSpace` specification grids and specification curves;
- marginal and pairwise interaction sensitivity diagnostics;
- known-truth AOI and scientific-endpoint recovery benchmarks;
- spatial-error, sampling-rate, and structured missingness sensitivity analyses;
- deterministic specification/results provenance fingerprints;
- generic user adapter protocols for external study and detector backends;
- direct Eye-Tracking-BIDS `physio.tsv[.gz]` ingestion;
- pymovements `Gaze`/`Dataset` ingestion;
- pEYES detector execution through a normalized `DetectionResult` contract;
- deterministic Markdown robustness reports;
- automated tests across supported Python versions.

The first measurement-error model remains deliberately conservative and global Gaussian so that its assumptions are explicit and testable. GazeAudit does not claim that this baseline describes every tracker, participant, session, or screen region.

## Quick example

```python
import numpy as np
import pandas as pd

from gazeaudit import (
    GaussianGazeErrorModel,
    RectangleAOI,
    aoi_probabilities,
    expected_dwell,
)

validation = pd.DataFrame(
    {
        "observed_x": [501, 500, 499, 502],
        "observed_y": [400, 399, 401, 400],
        "target_x": [500, 500, 500, 500],
        "target_y": [400, 400, 400, 400],
    }
)

error_model = GaussianGazeErrorModel.fit(validation)

aois = [
    RectangleAOI("claim", 450, 350, 500, 450),
    RectangleAOI("price", 500, 350, 550, 450),
]

fixations = np.array([[500.0, 400.0], [490.0, 405.0]])
probabilities = aoi_probabilities(fixations, aois, error_model, rng=42)

expected_claim_dwell = expected_dwell(
    probabilities,
    durations=np.array([180.0, 220.0]),
    aoi="claim",
)
```

A fixation at an AOI boundary is therefore represented as uncertain membership rather than being forced immediately into one deterministic label.

## Interoperability

GazeAudit's interoperability layer is intentionally narrow: external packages retain responsibility for their own parsing and detection semantics, while GazeAudit normalizes only the information required for robustness analysis.

### Eye-Tracking-BIDS

GazeAudit can ingest the current BIDS eye-tracking `physio.tsv` or `physio.tsv.gz` representation directly:

```python
from gazeaudit import read_bids_eyetrack

record = read_bids_eyetrack(
    "sub-01_task-search_recording-eye1_physio.tsv.gz"
)
study = record.study
```

The reader follows the current eye-tracking-specific BIDS requirements needed for canonical ingestion: `PhysioType="eyetrack"`, `recording-<label>`, the initial `timestamp`, `x_coordinate`, and `y_coordinate` columns, `RecordedEye`, `SampleCoordinateSystem`, and coordinate/time unit metadata. Timestamps are normalized to milliseconds while the original BIDS timestamp and eye metadata can be retained alongside the canonical columns.

Separate eye files remain separate participant-by-trial streams by default, preventing left/right/cyclopean recordings from being accidentally interleaved. This reader is deliberately not presented as a replacement for the official BIDS Validator.

### pymovements

Install the optional dependency with `pip install "gazeaudit[pymovements]"`.

```python
from gazeaudit import from_pymovements_gaze

study = from_pymovements_gaze(
    gaze,
    coordinate="pixel",
    component="auto",
    participant_id="p01",
)
```

`component="auto"` accepts only two-component coordinates. Binocular four- or six-component vectors require an explicit `left`, `right`, or `cyclopian` choice so GazeAudit never silently chooses or averages an eye.

### pEYES

pEYES 0.2.x currently requires Python 3.12+. Install with `pip install "gazeaudit[peyes]"` and create the detector through pEYES or GazeAudit's lazy factory.

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

The normalized result keeps sample labels separate from per-trial detector metadata. GazeAudit currently requires pixel coordinates for pEYES because the pEYES public detector API interprets `x` and `y` as pixels and converts them using viewer distance and pixel size.

### User-defined adapters

Third-party integrations can implement the runtime-checkable `StudyAdapter` or `DetectorBackend` protocols. Detector backends return `DetectionResult`, which gives multiverse analyses one auditable output contract without forcing external packages into GazeAudit's internal implementation.

## Initial scientific roadmap

### Phase 1 — foundation

- canonical study representation;
- validation-derived spatial uncertainty;
- probabilistic AOIs;
- declarative pipeline spaces;
- common scalar endpoints;
- specification curves and audit reports.

### Phase 2 — inferential robustness

- adapters for alternative event detectors;
- interpolation and exclusion-rule variants;
- QC-threshold multiverses;
- AOI-boundary perturbation;
- sampling-rate perturbation;
- richer robustness surfaces and interaction diagnostics.

### Phase 3 — uncertainty propagation

- spatially varying and anisotropic error models;
- participant/session-specific measurement models;
- richer missingness mechanisms and multiple-imputation support;
- uncertainty-aware TTFF, revisits, and transitions;
- dynamic-AOI uncertainty;
- cross-device portability analyses.

### Phase 4 — interoperability and validation

- Eye-Tracking-BIDS import complete; export remains planned;
- pymovements and pEYES adapters;
- benchmark datasets with known scientific ground truth;
- publication-ready provenance and methods reporting.

## Explicit non-goals

GazeAudit will **not** become another generic preprocessing library, eye-tracker driver layer, fixation-detector collection, pupillometry package, heatmap GUI, BIDS-only converter, or LLM assistant. Those capabilities should be delegated to existing scientific tools when possible.

## Scientific principle

GazeAudit does not search for the pipeline that produces the most attractive result. Researchers define the set of **scientifically defensible** specifications first; GazeAudit then quantifies how the conclusion changes across that declared decision space.

## License

MIT.
