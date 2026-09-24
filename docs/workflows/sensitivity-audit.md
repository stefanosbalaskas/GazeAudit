---
title: Sensitivity audit workflow
description: Study-level workflow for adding controlled sampling, missingness, or spatial-error perturbations to a GazeAudit analysis while preserving endpoint identity and provenance.
kicker: Workflow · Sensitivity
permalink: /docs/workflows/sensitivity-audit/
search_category: Workflow
search_keywords: sensitivity workflow sampling missingness spatial error perturbation endpoint provenance reporting
---

# Sensitivity audit workflow

Use this workflow when a study has a specific **ordered uncertainty dimension** that should be stress-tested separately from the ordinary analytical specification space.

Typical examples are sampling representation, controlled missingness, and spatial-error scaling.

## Workflow overview

<div class="workflow-steps">
  <div class="workflow-step"><strong>Define the endpoint</strong><p>Freeze one scalar scientific quantity before choosing perturbation values.</p></div>
  <div class="workflow-step"><strong>Name the uncertainty dimension</strong><p>State exactly what is being varied and what is not.</p></div>
  <div class="workflow-step"><strong>Justify the range</strong><p>Choose values from design, validation, prior evidence, or a labelled stress-test rationale.</p></div>
  <div class="workflow-step"><strong>Declare reproducibility</strong><p>Record baseline, units, model or mechanism, seed or Monte Carlo settings, and software identity.</p></div>
  <div class="workflow-step"><strong>Execute the full curve</strong><p>Evaluate the same endpoint at every declared value and preserve failures explicitly.</p></div>
  <div class="workflow-step"><strong>Interpret direction and magnitude</strong><p>Describe what changes over the represented range without converting the curve into an inferential interval.</p></div>
</div>

## 1. Decide whether this is a sensitivity curve

A sensitivity audit is appropriate when one ordered dimension is intentionally perturbed.

If the alternatives are discrete scientific analysis choices such as detector family, AOI definition, or preprocessing method, use a [robustness audit]({{ '/docs/workflows/robustness-audit/' | relative_url }}) and a PipelineSpace instead.

The two designs can coexist.

## 2. Preserve the baseline

Before perturbation, record source-data identity, canonical mapping, endpoint definition, observed sampling information, observed missingness, measurement-error model when relevant, and exact software identity.

This prevents the sensitivity layer from silently redefining the starting analysis.

## 3. Define the perturbation protocol

For each uncertainty dimension, record the evaluated values and why they are plausible.

| Field | Example |
|---|---|
| endpoint | treatment − control dwell |
| dimension | target sampling rate |
| baseline | 120 Hz recorded stream |
| values | 120, 90, 60, 45, 30 Hz |
| transformation | nearest existing samples to regular target grid |
| randomness | none |
| interpretation | direction + magnitude over represented rates |

The values above are illustrative only.

## 4. Execute with the matching public API

Use <code>sampling_sensitivity_curve()</code> for lower-rate representation, <code>missingness_sensitivity_curve()</code> for controlled coordinate loss, and <code>spatial_sensitivity_curve()</code> for perturbing a declared gaze-error scale.

Keep each output table complete. If a declared value fails, preserve the failure and diagnose it rather than silently removing the row.

## 5. Visualise the complete range

For numerical one-dimensional outputs, use <code>plot_sensitivity_curve()</code>. For two-dimensional known-truth or recovery surfaces, use <code>plot_recovery_matrix()</code> when the input table satisfies that contract.

The [Plot gallery]({{ '/docs/plots/' | relative_url }}) is the visual reference for these output types.

## 6. Compare with the main robustness audit

After the curves are complete, ask whether their pattern changes the interpretation of the main specification-space result.

Examples include a direction-stable multiverse with material sampling sensitivity, ordinary analytical stability with strong spatial-error sensitivity, or an already sign-sensitive audit where additional perturbation confirms rather than resolves uncertainty.

Do not merge all numbers into one informal robustness score.

## 7. Report provenance and timing

Sensitivity added before outcome inspection and sensitivity added after peer review are both legitimate when clearly described, but they are different evidence layers.

Record when the protocol was defined, whether the endpoint had already been inspected, who requested the analysis if it was review-stage work, whether the perturbation layer changes the original valid denominator, and where the new evidence appears in the manuscript and archive.

For post-review work, use the [reviewer-requested amendments guide]({{ '/docs/guides/reviewer-requested-amendments/' | relative_url }}).

## 8. Publication handoff

A publication-ready sensitivity audit should preserve the protocol and rationale, baseline identity, full output tables, figures, seed or Monte Carlo information, failures, bounded Methods and Results wording, limitations, and exact software identity.

Then bind it into the broader [reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}).

## Next

- [Design a sensitivity analysis]({{ '/docs/guides/sensitivity-analysis-design/' | relative_url }})
- [Sensitivity protocol worked example]({{ '/docs/examples/sensitivity-protocol/' | relative_url }})
- [Read robustness diagnostics]({{ '/docs/guides/robustness-diagnostics/' | relative_url }})
- [Plot gallery]({{ '/docs/plots/' | relative_url }})
