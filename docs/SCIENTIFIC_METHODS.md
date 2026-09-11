# GazeAudit scientific methods plan

GazeAudit is being developed as a **methods project first and a software project second**. New functionality should be admitted only when its scientific assumptions can be stated, tested, and benchmarked.

## 1. Core scientific question

GazeAudit asks:

> How much does an eye-tracking scientific conclusion depend on uncertainty in the measurement and on reasonable, defensible analytical choices?

Two distinct uncertainty sources are represented explicitly:

- **measurement uncertainty**: the observed gaze coordinate is an error-prone measurement of latent true gaze;
- **analytical-choice uncertainty**: several preprocessing, QC, event, AOI, missing-data, and sampling decisions may all be scientifically defensible.

The package does not assume that these uncertainty sources are additive or independent. Their interaction is part of the research problem.

## 2. Phase-1 measurement model

The first implementation uses a deliberately transparent global bivariate Gaussian model.

For validation observation `i`:

```text
e_i = observed_i - target_i
```

with

```text
e_i ~ N(mu_error, Sigma_error)
```

For a new observed gaze position `g_obs`, GazeAudit samples plausible latent true positions as:

```text
g_true = g_obs - e
```

where `e` is sampled from the fitted validation-error distribution.

This model is not intended as a universal description of eye-tracker error. It provides a falsifiable baseline against which spatially varying, participant-specific, robust, mixture, and time-varying models can be compared.

## 3. Probabilistic AOI membership

Conventional AOI analysis commonly maps one coordinate to one deterministic label. GazeAudit instead estimates marginal membership probabilities:

```text
P(AOI_j | observed gaze, fitted error model)
```

For static AOIs in the first implementation, these probabilities are estimated by Monte Carlo draws of latent true gaze followed by geometric membership tests.

Important limitation: overlapping AOIs are permitted. Their marginal probabilities therefore need not sum to one. The `outside` probability represents membership in none of the supplied AOIs.

## 4. Uncertainty-aware endpoints

The first implemented endpoints are intentionally simple:

- expected dwell time;
- expected fixation/event count.

For AOI `A` and event durations `d_i`, expected dwell is:

```text
E[dwell_A] = sum_i P(A_i) * d_i
```

Future endpoints such as TTFF, revisits, transitions, scanpath quantities, and model coefficients require explicit treatment of joint event uncertainty and should not be added as naive probability-weighted formulas.

## 5. Analytical specification space

A specification is a declared set of defensible analytical choices. Examples include:

- event detector;
- detector parameterization;
- interpolation rule;
- missing-data handling;
- data-quality threshold;
- participant/trial exclusion rule;
- binocular combination rule;
- AOI definition or boundary perturbation;
- sampling-rate representation;
- measurement-error model.

GazeAudit must never construct a specification space by searching for choices that maximize statistical significance. The admissible decision space should be declared from methodological justification before the robustness result is inspected.

## 6. Robustness outputs

The current descriptive layer includes:

- number of evaluated specifications;
- median and mean endpoint estimates;
- full and central specification ranges;
- fraction of positive, negative, or null estimates;
- sign stability;
- ordered specification curves;
- marginal factor-sensitivity diagnostics.

Marginal sensitivity currently uses between-level sum of squares divided by total endpoint sum of squares. Because specification factors can be dependent and interact, these values are **not** an additive or causal variance decomposition.

A later methods tranche will compare interaction-aware alternatives such as hierarchical variance components, functional ANOVA, Shapley-style attribution, and surrogate-model sensitivity analysis.

## 7. Validation programme

The package should not be considered scientifically validated merely because unit tests pass. The methods programme will include at least four validation families.

### 7.1 Known-truth simulation

Generate studies with known:

- experimental effects;
- participant and stimulus variance;
- gaze-event structure;
- spatial measurement error;
- drift;
- missingness;
- sampling-rate degradation.

Primary criterion: recovery of the scientific effect and correct identification of deliberately robust versus deliberately fragile scenarios.

### 7.2 Event-classifier multiverse

Run multiple established event detectors on the same recordings and distinguish:

- event-level disagreement that does not alter the scientific endpoint;
- event-level disagreement that materially changes the conclusion.

The package should consume established detector implementations through adapters rather than claiming novelty from reimplementing them.

### 7.3 AOI uncertainty benchmark

Use known validation targets and deliberately small/adjacent AOIs. Compare:

- hard AOI assignment;
- bias-corrected hard assignment;
- probabilistic AOI assignment;
- Monte Carlo propagated endpoints.

Evaluate probability calibration, endpoint bias, interval coverage, and effect recovery as spatial error increases.

### 7.4 Sampling and missingness benchmark

Systematically downsample high-rate data and impose controlled missingness mechanisms. Evaluate whether the same substantive endpoint survives alternative acquisition/cleaning regimes.

## 8. Software-validation requirements

Every scientific engine should eventually have:

- deterministic seeded tests where stochastic algorithms are used;
- numerical invariants;
- simulation-based recovery tests;
- regression fixtures;
- explicit failure modes for invalid inputs;
- provenance sufficient to reproduce every evaluated specification.

## 9. Interoperability principle

GazeAudit should orchestrate rather than replace mature tools. Planned adapters include:

- pymovements;
- pEYES;
- Eye-Tracking-BIDS;
- user-defined event detectors and preprocessing functions.

Adapters must preserve the backend, backend version, parameters, input fingerprint, and transformation metadata whenever this information is available.

## 10. Scope guardrails

The project should reject feature requests whose main value is one of the following unless they directly serve the uncertainty/robustness research question:

- another generic fixation/saccade detector;
- generic pupil preprocessing;
- generic gaze plotting or heatmaps;
- eye-tracker device drivers;
- GUI-only convenience features;
- BIDS conversion without an analytical/provenance contribution;
- LLM/chat interfaces;
- unvalidated AI classification presented as ground truth.

## 11. Publication criterion

A feature belongs in the flagship methods paper only if it contributes to at least one of:

1. a new or validated representation of eye-tracking measurement uncertainty;
2. a new or validated way to propagate that uncertainty into a scientific endpoint;
3. a new or validated measure of inferential robustness across defensible eye-tracking pipelines;
4. a benchmark demonstrating when conventional deterministic/single-pipeline analysis is adequate and when it is not.

The target is therefore not a large function count. The target is a small set of methods whose assumptions and scientific consequences are exceptionally well validated.
