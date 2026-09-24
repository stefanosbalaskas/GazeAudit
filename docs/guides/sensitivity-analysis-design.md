---
title: Design a sensitivity analysis
description: Build a defensible GazeAudit sensitivity protocol for sampling rate, missingness, spatial measurement error, and related perturbations without choosing ranges after inspecting the endpoint.
kicker: Guide · Sensitivity design
permalink: /docs/guides/sensitivity-analysis-design/
search_category: Guide
search_keywords: sensitivity design protocol sampling missingness spatial error perturbation range grid endpoint rng predeclare robustness
---

# Design a sensitivity analysis

Use this guide when you know **which source of uncertainty you want to stress-test** but need to define the perturbation protocol before execution.

The objective is not to discover a setting that preserves the preferred conclusion. The objective is to expose how one fixed scientific endpoint behaves over a justified range of uncertainty.

## 1. State the sensitivity question

Write one sentence that names the uncertainty dimension and the endpoint.

Examples:

> How does the treatment-minus-control dwell contrast change when the recorded stream is represented at lower target sampling rates?

> How does expected target-AOI dwell change as the declared gaze-error standard deviation is scaled?

> How does the endpoint change as controlled gaze-coordinate missingness is added under a specified perturbation mechanism?

If the sentence changes the endpoint as the perturbation changes, the design is not ready.

## 2. Separate sensitivity from the specification space

Use a **specification space** when the alternatives are discrete analysis choices such as detector family, AOI rule, or preprocessing option.

Use a **sensitivity curve** when one ordered quantity is deliberately perturbed, such as sampling rate, missingness fraction, spatial-error scale, or another study-justified numerical parameter.

The two designs can coexist while retaining separate provenance.

## 3. Declare the baseline

For sampling, record the observed acquisition rate and timestamp unit. For missingness, record the observed missing fraction before adding controlled loss. For spatial uncertainty, record the fitted error-model identity, validation sample, coordinate unit, grouping level, and baseline covariance.

The baseline is part of the interpretation and should not be reconstructed after the analysis.

## 4. Justify the perturbation range

A range can come from hardware or acquisition constraints, calibration or validation uncertainty, prior methodological evidence, preregistered tolerances, or a deliberately labelled stress-test range.

Avoid defining the range by first running a very wide grid and then reporting only the reassuring region. Preserve the full evaluated grid.

## 5. Fix the endpoint contract

At every perturbation value, evaluate the same scalar scientific quantity.

Good examples include a treatment-minus-control dwell contrast, paired AOI occupancy contrast, path-rate contrast, a prespecified model coefficient, or known-truth recovery error.

If a perturbation makes the endpoint undefined, preserve that state explicitly rather than substituting another estimator.

## 6. Declare randomness

Some sensitivity analyses are deterministic; others involve Monte Carlo propagation or controlled random masking.

When randomness exists, set an explicit seed or generator policy, preserve it in the analysis record, distinguish Monte Carlo variability from scientific sensitivity, and do not rerun seeds until the desired pattern appears.

## 7. Use the API that matches the uncertainty dimension

### Sampling representation

~~~python
from gazeaudit import sampling_sensitivity_curve

sampling = sampling_sensitivity_curve(
    study,
    target_rates=[120, 90, 60, 45, 30],
    endpoint=endpoint,
    timestamp_unit="ms",
)
~~~

This retains existing samples near an ideal target grid. It does not emulate another physical tracker.

### Controlled missingness

~~~python
from gazeaudit import missingness_sensitivity_curve

missing = missingness_sensitivity_curve(
    study,
    fractions=[0.00, 0.05, 0.10, 0.20],
    endpoint=endpoint,
    mechanism="mcar",
    rng=20260924,
)
~~~

The mechanism is a perturbation model, not a claim about the empirical missing-data process.

### Spatial measurement error

~~~python
from gazeaudit import spatial_sensitivity_curve

spatial = spatial_sensitivity_curve(
    points,
    aois,
    error_model,
    sd_scales=[0.5, 1.0, 1.5, 2.0],
    durations=durations_ms,
    draws=4000,
    rng=20260924,
)
~~~

The scale factors perturb the declared error model. They do not estimate a new device.

## 8. Plot the complete curve

Use <code>plot_sensitivity_curve()</code> for one-dimensional numerical sensitivity outputs.

~~~python
from gazeaudit import plot_sensitivity_curve

fig = plot_sensitivity_curve(
    sampling,
    x_col="target_hz",
    title="Sampling-rate sensitivity",
    x_label="Target sampling rate (Hz)",
)
~~~

Do not crop away values because they weaken the preferred interpretation.

## 9. Interpret direction and magnitude separately

Ask in order whether the endpoint remained defined, whether the sign changed, how much the magnitude changed, whether that change is scientifically material under an independent criterion, whether one region behaves qualitatively differently, and which uncertainty dimensions remain untested.

A sign-stable curve can still be materially sensitive.

## 10. Preserve a sensitivity protocol record

At minimum, preserve:

~~~text
sensitivity_id
endpoint_name
baseline_definition
perturbation_dimension
perturbation_values
mechanism_or_model
seed_or_rng_policy
software_version
source_commit
execution_date
output_table
figure_path
interpretation_boundary
~~~

When sensitivity analysis was added after outcome inspection, for example during peer review, record that timing rather than describing it as originally prespecified.

## Reporting template

### Methods

> We evaluated sensitivity of [endpoint] to [uncertainty dimension] over the independently defined range [values/range]. The same endpoint definition was used at every perturbation value. [Randomness/Monte Carlo details]. The analysis was treated as a controlled sensitivity analysis rather than as evidence that another physical device or unobserved data process would have produced the perturbed observations.

### Results

> Across the evaluated range, the endpoint varied from [min] to [max]. Direction [remained / did not remain] stable. The largest magnitude change occurred at [value], where the estimate was [estimate]. These values describe the represented perturbation protocol and were not interpreted as confidence or posterior intervals.

### Limitation

> The analysis addresses sensitivity to the declared perturbation model and range only. It does not establish robustness to untested acquisition, preprocessing, measurement, or modelling choices.

## Checklist

- [ ] one fixed endpoint;
- [ ] baseline recorded;
- [ ] perturbation dimension named;
- [ ] range justified independently of the observed endpoint;
- [ ] all evaluated values retained;
- [ ] randomness seeded where relevant;
- [ ] unsupported or failed values preserved explicitly;
- [ ] direction and magnitude interpreted separately;
- [ ] no device-equivalence claim from downsampling alone;
- [ ] no causal missing-data claim from injected missingness alone;
- [ ] no claim that an error-model scale is physically true without validation;
- [ ] untested uncertainty dimensions stated.

## Next

Work through the [Sensitivity protocol example]({{ '/docs/examples/sensitivity-protocol/' | relative_url }}) and inspect the [Plot gallery]({{ '/docs/plots/' | relative_url }}) for reproducible sensitivity displays.
