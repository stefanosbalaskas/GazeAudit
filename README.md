# GazeAudit

**Measurement uncertainty and inferential robustness for eye-tracking research.**

GazeAudit is a scientific Python package for asking a question that conventional eye-tracking pipelines rarely answer directly:

> Would the scientific conclusion survive other reasonable measurement and analytical choices?

The project combines two methodological pillars in one framework:

1. **Measurement uncertainty** — represent calibration/validation error, spatial uncertainty, and uncertain AOI membership instead of treating every observed gaze coordinate as exact.
2. **Analytical robustness** — evaluate defensible alternative preprocessing, QC, event-detection, AOI, missing-data, and sampling choices and quantify how much the scientific endpoint changes.

## Scientific scope

GazeAudit is intended to sit **above** existing eye-tracking preprocessing and event-detection tools, not replace them. The package will provide adapters to established ecosystems where possible and focus its own methodological contribution on uncertainty propagation, specification-space analysis, robustness diagnostics, benchmarking, and reproducible audit reports.

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

The repository is in **pre-alpha** development. The first foundation tranche currently implements:

- a canonical vendor-neutral `GazeStudy` object;
- rectangle and circle AOI primitives;
- a transparent bivariate Gaussian gaze-error model fitted from validation targets;
- Monte Carlo probabilistic AOI membership;
- uncertainty-weighted dwell time and fixation counts;
- declarative `PipelineSpace` specification grids;
- generic specification execution through `run_specs()`;
- effect-direction and specification-range summaries;
- marginal factor-sensitivity diagnostics;
- deterministic Markdown robustness reports;
- automated tests across supported Python versions.

The model is deliberately conservative: the first error model is global and Gaussian so that assumptions are explicit and testable. Spatially varying, participant-specific, robust, dynamic-AOI, missingness, and sampling-rate uncertainty are planned extensions rather than hidden claims in the first implementation.

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
- missingness sensitivity and multiple-imputation support;
- uncertainty-aware TTFF, revisits, and transitions;
- dynamic-AOI uncertainty;
- cross-device portability analyses.

### Phase 4 — interoperability and validation

- Eye-Tracking-BIDS import/export;
- pymovements and pEYES adapters;
- benchmark datasets with known scientific ground truth;
- publication-ready provenance and methods reporting.

## Explicit non-goals

GazeAudit will **not** begin as another generic preprocessing library, eye-tracker driver layer, fixation-detector collection, pupillometry package, heatmap GUI, BIDS-only converter, or LLM assistant. Those capabilities should be delegated to existing scientific tools when possible.

## Scientific principle

GazeAudit does not search for the pipeline that produces the most attractive result. Researchers define the set of **scientifically defensible** specifications first; GazeAudit then quantifies how the conclusion changes across that declared decision space.

## License

MIT.
