# GazeAudit scientific methods and validation programme

GazeAudit is developed as a **methods project first and a software project second**.
Functionality belongs in the project only when its scientific assumptions can be stated,
tested, benchmarked, and preserved through reproducible provenance.

## 1. Core scientific question

GazeAudit asks:

> How much does an eye-tracking scientific conclusion depend on uncertainty in the
> measurement and on reasonable, defensible analytical choices?

Two uncertainty sources are represented explicitly:

- **measurement uncertainty**: an observed gaze coordinate is an error-prone
  measurement of latent true gaze;
- **analytical-choice uncertainty**: multiple preprocessing, QC, event, AOI,
  missing-data, sampling, and modeling choices may all be scientifically defensible.

The package does not assume these sources are additive or independent.

## 2. Measurement-error models

The baseline implementation uses transparent Gaussian error models derived from
validation information. The original global bivariate Gaussian model remains useful as
a falsifiable baseline; grouped participant/session/recalibration models are also
supported where the source design supplies the required mapping.

GazeAudit does not treat any one model as universally correct. A model must fail closed
when the required validation mapping is absent rather than silently falling back to a
pooled error distribution.

## 3. Probabilistic AOI membership

Conventional AOI analysis maps a coordinate to a deterministic label. GazeAudit can
instead propagate a declared gaze-error model into marginal AOI-membership probability
and then into scientific endpoints.

Overlapping AOIs are permitted. Their marginal probabilities need not sum to one.
`outside` represents membership in none of the supplied AOIs.

## 4. Uncertainty-aware endpoints

Implemented baseline endpoints include expected dwell/fixation quantities and controlled
case-study-specific scientific estimands. More complex endpoints such as TTFF, revisits,
transitions, scanpaths, and model coefficients require an explicit treatment of joint
event uncertainty and must not be added as naive probability-weighted formulas.

## 5. Analytical specification space

A specification is a declared set of defensible analytical choices. Examples include
event detector, parameterization, interpolation rule, missing-data handling,
data-quality threshold, participant/trial exclusion rule, binocular combination rule,
AOI definition, sampling-rate representation, and measurement-error model.

GazeAudit must never construct a specification space by searching for choices that
maximize statistical significance. The admissible decision space is justified before
robustness outputs are inspected.

## 6. Robustness outputs

The package supports specification curves, sign summaries, central/full endpoint
ranges, conclusion-recovery rules, factor-sensitivity summaries, pairwise interaction
diagnostics, deterministic provenance, and publication-facing audit bundles.

Sensitivity diagnostics are descriptive properties of the declared specification
space; they are not automatically causal variance decompositions.

## 7. Validation programme

The scientific MVP validation programme is now complete for its baseline methods.

### 7.1 Known-truth simulation — complete

Known-truth generators and recovery benchmarks test endpoint recovery and deliberately
robust versus deliberately fragile scenarios under controlled perturbations.

### 7.2 Event-classifier multiverse — complete baseline

The authoritative GazeBase audit preserves seven predeclared detector specifications.
Its canonical result is `incomplete` because the frozen 95% completeness gate failed.
Failed detector specifications were retained as incomplete rather than removed after
outcome inspection.

### 7.3 AOI measurement-error benchmark — complete baseline

The authoritative Korthals target-tracking case propagates the frozen measurement-error
model through a paired AOI endpoint. Its canonical classification is
`robust_negative`: the hard effect is negative and all 2,000 prespecified
measurement-error draws remain below zero.

The resulting interval is measurement-model-induced. It is not a population confidence
interval or Bayesian posterior interval.

### 7.4 Sampling and missingness benchmark — complete baseline

The authoritative Pedrotti/de Chambrier case applies five frozen downsampling targets
and two controlled added-missingness mechanisms across four fractions and 20
deterministic replicates per family. Its canonical classification is
`materially_fragile`: several perturbation families fail the prespecified
magnitude-and-direction recovery criterion.

The three authoritative real-data outcomes are indexed in
`docs/VALIDATION_MATRIX.md`.

## 8. Software-validation requirements

Scientific engines require deterministic seeded tests where stochastic algorithms are
used, numerical invariants, simulation-based recovery tests, regression fixtures,
explicit invalid-input failures, and provenance sufficient to reproduce every evaluated
specification.

Real-data validation additionally uses protocol/source freezing, exact-code execution,
checksummed artifacts, and archive-before-reveal workflows.

## 9. Interoperability principle

GazeAudit orchestrates rather than replaces mature tools. Current interoperability
covers Eye-Tracking-BIDS ingestion, pymovements, pEYES, and user-defined study/detector
adapters.

Adapters should preserve backend identity, backend version, parameters, input
fingerprints, and transformation metadata whenever those quantities are available.

## 10. Scope guardrails

The project should reject feature requests whose main value is another generic
fixation/saccade detector, generic pupil preprocessing, generic heatmap tooling, device
drivers, GUI-only convenience features, BIDS conversion without an
analytical/provenance contribution, LLM/chat interfaces, or unvalidated AI
classification presented as ground truth.

## 11. Publication criterion

A feature belongs in the flagship methods programme only if it contributes to at least
one of:

1. a new or validated representation of eye-tracking measurement uncertainty;
2. a new or validated way to propagate uncertainty into a scientific endpoint;
3. a new or validated measure of inferential robustness across defensible pipelines;
4. a benchmark showing when deterministic/single-pipeline analysis is adequate and
   when it is not.

The target is not a large function count. The target is a compact set of methods whose
assumptions and scientific consequences are unusually well validated.

## 12. Post-outcome boundary

The GazeBase, Korthals, and Pedrotti case studies are now post-outcome frozen.
Scientific choices in those cases may not be changed in response to their observed
results. Permitted follow-up is limited to independent verification, reproducibility,
archival, publication reporting, and non-scientific infrastructure/release work.
