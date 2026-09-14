# GazeAudit

**Measurement uncertainty and inferential robustness for eye-tracking research.**

GazeAudit is a scientific Python package for asking a question that conventional eye-tracking pipelines rarely answer directly:

> Would the scientific conclusion survive other reasonable measurement and analytical choices?

The project combines two methodological pillars in one framework:

1. **Measurement uncertainty** — represent calibration/validation error, spatial uncertainty, and uncertain AOI membership instead of treating every observed gaze coordinate as exact.
2. **Analytical robustness** — evaluate defensible alternative preprocessing, QC, event-detection, AOI, missing-data, and sampling choices and quantify how much the scientific endpoint changes.

## Installation

The current public release is `0.1.0`:

```bash
pip install gazeaudit==0.1.0
```

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

GazeAudit `0.1.0` is the first public alpha release. The scientific MVP has been exercised with known-truth simulations and three deliberately different real-data validation outcomes:

| Case study | Scientific question | Canonical outcome |
|---|---|---|
| GazeBase multi-detector audit | Does the frozen detector specification space satisfy the predeclared completeness gate? | `incomplete` |
| Korthals target-tracking AOI | Does the negative paired AOI effect survive the frozen measurement-error propagation model? | `robust_negative` |
| Pedrotti/de Chambrier sampling + missingness | Does the frozen gaze-path-rate contrast recover across downsampling and added missingness? | `materially_fragile` |

These outcomes are not post-hoc labels. Each case used a frozen protocol, controlled source identity, deterministic provenance, checksummed scientific artifacts, and archive-before-reveal execution. See [`docs/VALIDATION_MATRIX.md`](docs/VALIDATION_MATRIX.md) for the authoritative provenance index.

The current scientific MVP includes:

- a canonical vendor-neutral `GazeStudy` object;
- rectangle and circle AOI primitives;
- transparent Gaussian gaze-error models fitted from validation information;
- Monte Carlo probabilistic AOI membership and endpoint propagation;
- hard-vs-probabilistic AOI comparison, flip probabilities, and boundary-risk summaries;
- uncertainty-weighted dwell time and fixation counts;
- declarative `PipelineSpace` specification grids and specification curves;
- marginal and pairwise interaction sensitivity diagnostics;
- known-truth AOI and scientific-endpoint recovery benchmarks;
- predeclared conclusion-recovery rules that do not optimize statistical significance;
- spatial-error, sampling-rate, and structured missingness sensitivity analyses;
- deterministic specification/results provenance fingerprints;
- deterministic publication audit bundles with scientific and execution fingerprints;
- generic user adapter protocols for external study and detector backends;
- direct Eye-Tracking-BIDS `physio.tsv[.gz]` ingestion;
- pymovements `Gaze`/`Dataset` ingestion;
- pEYES detector execution through a normalized `DetectionResult` contract;
- deterministic Markdown robustness reports;
- automated tests across supported Python versions.

The first measurement-error models remain deliberately transparent and assumption-bound. GazeAudit does not claim that one error model describes every tracker, participant, session, screen region, or study design.

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

## Conclusion recovery and publication audit bundles

A robustness analysis can be evaluated against a **predeclared scientific recovery rule**. The rule uses effect-error tolerances, optional direction recovery, and a minimum across-specification recovery fraction; it does not use statistical-significance optimization to decide which specifications count.

```python
import pandas as pd

from gazeaudit import ConclusionRule, build_conclusion_audit_bundle

results = pd.DataFrame(
    {
        "method": ["hard", "probabilistic", "probabilistic"],
        "error_scale": [None, 0.5, 1.5],
        "estimate": [9.5, 10.2, 8.7],
    }
)

rule = ConclusionRule(
    relative_tolerance=0.20,
    require_sign=True,
    minimum_recovery_fraction=0.90,
)

bundle = build_conclusion_audit_bundle(
    results,
    reference_effect=10.0,
    rule=rule,
    title="Example conclusion-robustness audit",
    endpoint="treatment-minus-control dwell",
    source_description="Synthetic known-truth validation fixture",
)

print(bundle.summary["classification"])
print(bundle.scientific_fingerprint)
print(bundle.manifest_json())
print(bundle.markdown)
```

The publication bundle binds the declared rule, reference effect, specification table, recovery table, summary, source description, optional researcher metadata, and software provenance. It exposes a **scientific fingerprint** for scientific inputs/outputs and a **bundle fingerprint** that additionally binds the recorded execution environment. `verify_publication_audit_bundle()` detects later mutation of the specification, recovery, summary, methods text, report, or manifest.

For real-data analyses, `reference_effect` is not inferred by GazeAudit. The researcher must define and justify what the reference effect represents before inspecting robustness outputs.

## Interoperability

GazeAudit's interoperability layer is intentionally narrow: external packages retain responsibility for their own parsing and detection semantics, while GazeAudit normalizes only the information required for robustness analysis.

### Eye-Tracking-BIDS

```python
from gazeaudit import read_bids_eyetrack

record = read_bids_eyetrack(
    "sub-01_task-search_recording-eye1_physio.tsv.gz"
)
study = record.study
```

The reader requires the eye-tracking-specific metadata needed for canonical ingestion and normalizes timestamps to milliseconds while retaining relevant source metadata. Separate eye files remain separate participant-by-trial streams by default. GazeAudit is not presented as a replacement for the official BIDS Validator.

### pymovements

Install with `pip install "gazeaudit[pymovements]"`.

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

pEYES 0.2.x currently requires Python 3.12+. Install with `pip install "gazeaudit[peyes]"`.

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

The normalized result keeps sample labels separate from per-trial detector metadata.

### User-defined adapters

Third-party integrations can implement the runtime-checkable `StudyAdapter` or `DetectorBackend` protocols. Detector backends return `DetectionResult`, giving multiverse analyses one auditable output contract without forcing external packages into GazeAudit internals.

## Validation and roadmap

The **scientific MVP validation programme is complete** for its predeclared baseline:

- known-truth scientific recovery benchmarks — complete;
- multi-detector GazeBase real-data audit — complete, canonical result `incomplete`;
- probabilistic-AOI measurement-error Korthals case study — complete, canonical result `robust_negative`;
- sampling/missingness Pedrotti case study — complete, canonical result `materially_fragile`;
- paired high-robustness and material-fragility demonstrations — complete;
- deterministic publication audit bundle and methods wording — complete.

Post-MVP development is intentionally separated from those frozen results. Planned methodological expansion includes richer interpolation/QC multiverses, spatially varying error models, uncertainty-aware TTFF/revisits/transitions, dynamic-AOI uncertainty, richer missingness models, cross-device portability analyses, and Eye-Tracking-BIDS export. None of those planned additions alter the canonical validation outcomes above.

Release/publication hardening is tracked separately in [Issue #43](https://github.com/stefanosbalaskas/GazeAudit/issues/43).

## Explicit non-goals

GazeAudit will **not** become another generic preprocessing library, eye-tracker driver layer, fixation-detector collection, pupillometry package, heatmap GUI, BIDS-only converter, or LLM assistant. Those capabilities should be delegated to existing scientific tools when possible.

## Scientific principle

GazeAudit does not search for the pipeline that produces the most attractive result. Researchers define the set of **scientifically defensible** specifications first; GazeAudit then quantifies how the conclusion changes across that declared decision space.

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff).

For analyses using release `0.1.0`, cite the version-specific Zenodo DOI **10.5281/zenodo.22757340** and record the exact software version or commit used. The concept DOI **10.5281/zenodo.22757339** represents all Zenodo versions and resolves to the latest archived version.

External publication provenance is recorded in [`release/0.1.0-external-publication-verification.json`](release/0.1.0-external-publication-verification.json).

## License

MIT.
