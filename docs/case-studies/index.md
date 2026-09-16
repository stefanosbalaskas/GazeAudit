---
title: Evidence map
description: A visual, protocol-bound map of GazeAudit's three frozen real-data validation cases, their perturbations, endpoints, outcomes, and interpretation boundaries.
permalink: /docs/case-studies/
kicker: Frozen validation programme · evidence map
search_category: Evidence
search_keywords: evidence map case studies GazeBase Korthals Pedrotti validation robustness measurement uncertainty sampling missingness detectors frozen outcomes
---

# Evidence map

GazeAudit's real-data validation programme is deliberately designed to preserve different scientific outcomes rather than reward one preferred answer. Each case was governed by frozen scientific choices, source identity, checksummed artifacts, archive-before-reveal execution, and a post-outcome interpretation boundary.

<div class="callout callout-info">
  <strong>Read these as protocol-bound outcomes, not dataset scores.</strong>
  <code>incomplete</code>, <code>robust_negative</code>, and <code>materially_fragile</code> describe what happened under three different frozen audits. They do not rank the source datasets, methods, or research teams.
</div>

## See the three frozen outcomes

<div class="evidence-plot-grid">
  <figure class="plot-card evidence-figure">
    <img src="{{ '/assets/images/gazebase-completeness.svg' | relative_url }}" alt="Observed GazeBase detector completeness plot with five complete detector specifications and two with zero finite participant estimates" loading="lazy">
    <figcaption>
      <span class="evidence-state">Incomplete</span>
      <strong>GazeBase · detector-space completeness</strong>
      <p>Five detector specifications reached 322/322 finite participant estimates; two reached 0/322 under the frozen no-interpolation policy.</p>
      <a href="{{ '/docs/case-studies/gazebase-incomplete/' | relative_url }}">Open the frozen case →</a>
    </figcaption>
  </figure>

  <figure class="plot-card evidence-figure">
    <img src="{{ '/assets/images/korthals-effect.svg' | relative_url }}" alt="Observed Korthals hard and measurement-error propagated target-tracking AOI effects, both below zero" loading="lazy">
    <figcaption>
      <span class="evidence-state">Robust negative</span>
      <strong>Korthals · measurement uncertainty</strong>
      <p>The hard and uncertainty-propagated effects differed in magnitude, while all 2,000 prespecified measurement-model draws remained below zero.</p>
      <a href="{{ '/docs/case-studies/korthals-target-tracking/' | relative_url }}">Open the frozen case →</a>
    </figcaption>
  </figure>

  <figure class="plot-card evidence-figure">
    <img src="{{ '/assets/images/pedrotti-sampling-sensitivity.svg' | relative_url }}" alt="Observed Pedrotti sampling-rate sensitivity plot with negative estimates at every rate and failed magnitude recovery at lower rates" loading="lazy">
    <figcaption>
      <span class="evidence-state">Materially fragile</span>
      <strong>Pedrotti/de Chambrier · sampling sensitivity</strong>
      <p>The sign remained negative at every target rate, but magnitude recovery failed at 125, 100, and 50 Hz under the frozen ±20% tolerance.</p>
      <a href="{{ '/docs/case-studies/pedrotti-sensitivity/' | relative_url }}">Open the frozen case →</a>
    </figcaption>
  </figure>
</div>

## Compare the audits before comparing the labels

The three statuses come from different scientific questions and different frozen decision rules. The useful comparison is therefore **what was held fixed, what was deliberately varied, and what rule converted the resulting evidence into a status**.

| Case | Audit axis | Frozen target | Declared variation | Frozen decision rule | Frozen status |
|---|---|---|---|---|---|
| **GazeBase** | Specification-space completeness | Finite participant estimates for a fixed cohort of 322 participants | Seven predeclared detector specifications under a NaN-preserving, no-interpolation policy | The declared detector space had to satisfy a 95% finite-participant completeness gate before a robustness classification was permitted | `incomplete` |
| **Korthals** | AOI measurement uncertainty | Jumping-circle occupancy minus moving-circle occupancy within a 1-dva target-centred AOI | Grouped isotropic Gaussian gaze-error propagation with 2,000 prespecified Monte Carlo draws | The hard effect had to be negative and at least 95% of measurement-error draws had to remain below zero | `robust_negative` |
| **Pedrotti/de Chambrier** | Sampling and missingness sensitivity | Participant-balanced long-minus-short numeric gaze-path-rate difference in px/s | Prespecified downsampling plus MCAR and single-block added-missingness families | Recovery required sign agreement and no more than 20% relative magnitude deviation; material fragility was triggered when a frozen perturbation family reached the predeclared ceiling | `materially_fragile` |

## What each status establishes—and what it does not

<div class="evidence-grid">
  <article class="evidence-card evidence-incomplete">
    <span class="evidence-state">Incomplete</span>
    <h2>GazeBase</h2>
    <p><strong>Establishes:</strong> this exact seven-detector audit did not satisfy its predeclared completeness prerequisite, so the remaining computable specifications were not promoted into a robustness label.</p>
    <p><strong>Does not establish:</strong> that GazeBase is a poor dataset, that the five computable detectors are invalid, or that a differently frozen future protocol could not be executed.</p>
    <p><a href="{{ '/docs/case_studies/GAZEBASE_MULTIDETECTOR_PROTOCOL.html' | relative_url }}">Read the frozen protocol →</a></p>
  </article>

  <article class="evidence-card evidence-robust">
    <span class="evidence-state">Robust negative</span>
    <h2>Korthals</h2>
    <p><strong>Establishes:</strong> the negative direction of the frozen paired AOI estimand remained stable under the prespecified measurement-error propagation model.</p>
    <p><strong>Does not establish:</strong> that the measurement-model interval is a population confidence interval, Bayesian posterior interval, causal-effect interval, or population p-value.</p>
    <p><a href="{{ '/docs/results/korthals2026_target_tracking_aoi_v2.html' | relative_url }}">Read the authoritative result →</a></p>
  </article>

  <article class="evidence-card evidence-fragile">
    <span class="evidence-state">Materially fragile</span>
    <h2>Pedrotti/de Chambrier</h2>
    <p><strong>Establishes:</strong> several frozen sampling or missingness perturbation families failed the declared magnitude-and-direction recovery criterion.</p>
    <p><strong>Does not establish:</strong> a sign reversal. Every sampling-rate estimate remained negative; the fragility concerns magnitude recovery under the frozen criterion.</p>
    <p><a href="{{ '/docs/results/pedrotti_sampling_missingness_v1.html' | relative_url }}">Read the authoritative result →</a></p>
  </article>
</div>

## Choose a case by methodological question

These routes are organised by the uncertainty you want to inspect, not by the desirability of the observed outcome.

- **Can a declared multiverse be called complete when some specifications fail to compute?** Start with [GazeBase]({{ '/docs/case-studies/gazebase-incomplete/' | relative_url }}).
- **Does an AOI contrast retain its direction after explicitly propagating gaze-position error?** Start with [Korthals]({{ '/docs/case-studies/korthals-target-tracking/' | relative_url }}).
- **How far can a rate-like endpoint move under lower sampling resolution or controlled missingness while keeping the same sign?** Start with [Pedrotti/de Chambrier]({{ '/docs/case-studies/pedrotti-sensitivity/' | relative_url }}).

## Read the programme in three layers

<div class="evidence-grid">
  <article class="evidence-card">
    <span class="evidence-state">01 · Freeze</span>
    <h3>Define the scientific question before outcome inspection.</h3>
    <p>Fix the estimand, cohort, perturbation space, decision rule, and source identity before the final result is known.</p>
  </article>
  <article class="evidence-card">
    <span class="evidence-state">02 · Perturb</span>
    <h3>Vary the declared methodological dimension.</h3>
    <p>Detector choice, measurement-error propagation, sampling resolution, and missingness are different audit axes and should not be collapsed into one generic robustness score.</p>
  </article>
  <article class="evidence-card">
    <span class="evidence-state">03 · Preserve</span>
    <h3>Apply the frozen rule literally.</h3>
    <p>Stop when prerequisites fail, retain stable results when the rule supports them, and preserve fragility when the declared criterion is not recovered.</p>
  </article>
</div>

## Why three different outcomes matter

A robustness framework is scientifically useful only if it can stop, preserve a stable conclusion, or expose fragility. These cases therefore exercise three distinct states:

1. **Incomplete** — the declared specification space is not complete enough to support a robustness classification.
2. **Robust** — the prespecified scientific direction remains stable under the declared uncertainty model.
3. **Materially fragile** — the endpoint fails the declared magnitude-and-direction recovery criterion under defensible perturbations.

The case-study pages are explanatory views over the frozen authoritative records. They do not replace those records and do not change scientific choices after outcome inspection.

## Authoritative records

- [Validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }})
- [Scientific methods]({{ '/docs/SCIENTIFIC_METHODS.html' | relative_url }})
- [GazeBase frozen protocol]({{ '/docs/case_studies/GAZEBASE_MULTIDETECTOR_PROTOCOL.html' | relative_url }})
- [Korthals authoritative result]({{ '/docs/results/korthals2026_target_tracking_aoi_v2.html' | relative_url }})
- [Pedrotti/de Chambrier authoritative result]({{ '/docs/results/pedrotti_sampling_missingness_v1.html' | relative_url }})
