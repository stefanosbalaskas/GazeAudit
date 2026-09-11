# GazeAudit

**Measurement uncertainty and inferential robustness for eye-tracking research.**

GazeAudit is a scientific Python package for asking a question that conventional eye-tracking pipelines rarely answer directly:

> Would the scientific conclusion survive other reasonable measurement and analytical choices?

The project combines two methodological pillars in one framework:

1. **Measurement uncertainty** — represent calibration/validation error, spatial uncertainty, and uncertain AOI membership instead of treating every observed gaze coordinate as exact.
2. **Analytical robustness** — evaluate defensible alternative preprocessing, QC, event-detection, AOI, missing-data, and sampling choices and quantify how much the scientific endpoint changes.

## Scientific scope

GazeAudit is intended to sit **above** existing eye-tracking preprocessing and event-detection tools, not replace them. The package will provide adapters to established ecosystems where possible and focus its own methodological contribution on uncertainty propagation, specification-space analysis, robustness diagnostics, benchmarking, and reproducible audit reports.

Planned core workflow:

```text
raw / processed gaze
        |
        v
measurement-error model
        |
        v
probabilistic AOI membership
        |
        +----------------------+
        |                      |
        v                      v
alternative defensible pipelines
        |
        v
common scientific endpoint
        |
        v
robustness + uncertainty audit
```

## Initial MVP

The first validated release is deliberately narrow:

- canonical screen-based gaze-study object;
- calibration/validation-derived spatial error model;
- probabilistic AOI membership;
- standard AOI endpoints such as dwell time and time-to-first-fixation;
- declarative pipeline/specification spaces;
- execution of alternative defensible specifications;
- effect/sign stability and specification-curve summaries;
- uncertainty attribution diagnostics;
- deterministic provenance and reproducible audit reports.

## Explicit non-goals

GazeAudit will **not** begin as another generic preprocessing library, eye-tracker driver layer, fixation-detector collection, pupillometry package, heatmap GUI, BIDS-only converter, or LLM assistant. Those capabilities should be delegated to existing scientific tools when possible.

## Status

Early development. API and scientific assumptions are not yet stable.

## License

MIT (planned for the initial development release).
