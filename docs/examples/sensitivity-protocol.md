---
title: Sensitivity protocol worked example
description: Build a deterministic synthetic sampling and missingness sensitivity protocol, preserve the declared grid, plot complete curves, and write bounded interpretation.
kicker: Example · Sensitivity protocol
permalink: /docs/examples/sensitivity-protocol/
search_category: Example
page_type: example
example_data: "Synthetic"
example_focus: "Robustness & sensitivity"
example_reuse: "Predeclared perturbation protocol"
example_output: "Sampling and missingness sensitivity tables with reproducible plots and bounded reporting"
example_boundary: "The synthetic ranges and endpoint are teaching values, not recommended thresholds or acquisition standards."
search_keywords: sensitivity protocol sampling missingness perturbation rng plot reporting synthetic endpoint
---

# Sensitivity protocol worked example

This example shows how to define a **small, explicit perturbation protocol before inspecting the resulting endpoint values**.

The teaching question is:

> Does one synthetic endpoint remain directionally and quantitatively similar when the same gaze-like stream is downsampled or exposed to controlled coordinate missingness?

<div class="callout warning">
<strong>Teaching values only.</strong>
The rates, missingness fractions, endpoint, and interpretation choices below are synthetic. Reuse the protocol structure, not the numerical choices.
</div>

## 1. Build a deterministic synthetic study

~~~python
import numpy as np
import pandas as pd

from gazeaudit import GazeStudy

rng = np.random.default_rng(24)
rows = []

for participant in ["P01", "P02", "P03", "P04"]:
    for trial in [1, 2]:
        condition = "treatment" if trial == 2 else "control"
        shift = 0.035 if condition == "treatment" else 0.0
        time_ms = np.arange(0.0, 1500.0, 1000.0 / 120.0)

        for i, timestamp in enumerate(time_ms):
            rows.append(
                {
                    "participant": participant,
                    "trial": trial,
                    "timestamp": timestamp,
                    "x": 0.50 + shift + 0.08 * np.sin(i / 9) + rng.normal(0, 0.006),
                    "y": 0.50 + 0.06 * np.cos(i / 11) + rng.normal(0, 0.006),
                    "condition": condition,
                }
            )

study = GazeStudy(pd.DataFrame(rows))
study.validate_time_order()
~~~

## 2. Fix one endpoint

~~~python
def endpoint(current):
    means = current.data.groupby("condition", sort=False)["x"].mean()
    return float(means["treatment"] - means["control"])
~~~

This endpoint is deliberately simple so the example remains focused on sensitivity design.

## 3. Record the protocol before execution

~~~python
protocol = {
    "endpoint": "treatment-minus-control mean x",
    "sampling_rates_hz": [120, 90, 60, 45, 30],
    "missingness_fractions": [0.00, 0.05, 0.10, 0.20],
    "missingness_mechanism": "mcar",
    "missingness_seed": 20260924,
}
~~~

In a real project, also record the scientific rationale for the range, software identity, source commit, and timing relative to outcome inspection.

## 4. Run sampling sensitivity

~~~python
from gazeaudit import sampling_sensitivity_curve

sampling = sampling_sensitivity_curve(
    study,
    target_rates=protocol["sampling_rates_hz"],
    endpoint=endpoint,
    timestamp_unit="ms",
)

print(sampling)
~~~

The output preserves both the endpoint and how much of the original row representation remains at each target rate.

## 5. Run controlled missingness sensitivity

~~~python
from gazeaudit import missingness_sensitivity_curve

missingness = missingness_sensitivity_curve(
    study,
    fractions=protocol["missingness_fractions"],
    endpoint=endpoint,
    mechanism=protocol["missingness_mechanism"],
    rng=protocol["missingness_seed"],
)

print(missingness)
~~~

The seed makes the teaching run reproducible. It does not make MCAR a correct model of real study loss.

## 6. Plot the complete declared curves

~~~python
from gazeaudit import plot_sensitivity_curve

sampling_fig = plot_sensitivity_curve(
    sampling,
    x_col="target_hz",
    title="Sampling-rate sensitivity",
    x_label="Target sampling rate (Hz)",
)

missingness_fig = plot_sensitivity_curve(
    missingness,
    x_col="observed_missing_fraction",
    title="Controlled missingness sensitivity",
    x_label="Observed missing fraction",
)
~~~

The public [Plot gallery]({{ '/docs/plots/' | relative_url }}) contains deterministic examples of both sensitivity-curve styles.

## 7. Summarise without inventing an inferential interval

~~~python
def summarize_curve(frame):
    estimates = frame["estimate"].astype(float)
    return {
        "minimum": float(estimates.min()),
        "maximum": float(estimates.max()),
        "all_positive": bool((estimates > 0).all()),
        "all_negative": bool((estimates < 0).all()),
        "contains_exact_null": bool((estimates == 0).any()),
    }

print(summarize_curve(sampling))
print(summarize_curve(missingness))
~~~

These are descriptive properties of the represented perturbation curves. They are not confidence intervals or posterior probabilities.

## 8. Keep the curves conceptually separate

The sampling analysis changes temporal representation by retaining existing observations near a target grid.

The missingness analysis masks gaze coordinates according to the declared perturbation mechanism.

Even when both curves move the same endpoint, they represent different uncertainty questions and should remain separately labelled in the archive and manuscript.

## 9. Example reporting structure

### Methods

> We evaluated the same synthetic treatment-minus-control endpoint across a prespecified set of lower target sampling rates and controlled missingness fractions. Sampling perturbation retained existing observations nearest to the target grid; missingness perturbation used a seeded MCAR masking process. The analyses were treated as controlled sensitivity checks rather than simulations of alternative physical trackers or claims about the empirical missing-data mechanism.

### Results

> We reported the endpoint at every declared perturbation value, together with row retention for sampling and observed missing fraction for missingness. Direction and magnitude were interpreted separately, and the complete curves were retained irrespective of whether individual values strengthened or weakened the baseline pattern.

### Limitation

> The results describe only the declared synthetic perturbation protocols and do not establish robustness to untested measurement, preprocessing, detector, AOI, or modelling choices.

## 10. What changes in a real study

Replace the synthetic generator with the canonical study table, the teaching endpoint with the prespecified scientific endpoint, the example rates and fractions with independently justified values, and the teaching seed with the project's reproducibility policy.

Keep the **declare → execute → preserve → interpret** sequence.

## Next

Use the [Sensitivity-analysis design guide]({{ '/docs/guides/sensitivity-analysis-design/' | relative_url }}) for protocol design and the [Sensitivity-audit workflow]({{ '/docs/workflows/sensitivity-audit/' | relative_url }}) for study-level integration.
