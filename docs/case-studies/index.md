---
title: Case studies
description: Protocol-bound real-data validation case studies for GazeAudit.
permalink: /docs/case-studies/
---

# Case studies

GazeAudit's real-data validation programme is deliberately designed to preserve different scientific outcomes rather than reward one preferred answer. Each case was governed by frozen scientific choices, source identity, checksummed artifacts, archive-before-reveal execution, and a post-outcome interpretation boundary.

<div class="evidence-grid">
  <article class="evidence-card evidence-incomplete">
    <span class="evidence-state">Incomplete</span>
    <h2>GazeBase multi-detector audit</h2>
    <p>A seven-detector specification space was declared in advance. Five detectors produced finite participant estimates for all 322 fixed-cohort participants, while NH and REMoDNaV produced none under the frozen no-interpolation policy. The 95% completeness gate therefore failed and no robustness label was manufactured.</p>
    <p><a href="{{ '/docs/case-studies/gazebase-incomplete/' | relative_url }}">Read the case →</a></p>
  </article>

  <article class="evidence-card evidence-robust">
    <span class="evidence-state">Robust negative</span>
    <h2>Korthals target-tracking AOI</h2>
    <p>The jumping-minus-moving occupancy contrast remained negative under the frozen grouped Gaussian measurement-error model. All 2,000 prespecified Monte Carlo draws were below zero.</p>
    <p><a href="{{ '/docs/case-studies/korthals-target-tracking/' | relative_url }}">Read the case →</a></p>
  </article>

  <article class="evidence-card evidence-fragile">
    <span class="evidence-state">Materially fragile</span>
    <h2>Pedrotti/de Chambrier sensitivity</h2>
    <p>The long-minus-short gaze-path-rate contrast retained its negative direction, but recovery deteriorated under lower sampling rates and controlled missingness. Several frozen perturbation families fell to 0.4 recovery or below.</p>
    <p><a href="{{ '/docs/case-studies/pedrotti-sensitivity/' | relative_url }}">Read the case →</a></p>
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
- [Korthals authoritative result]({{ '/docs/results/korthals2026_target_tracking_aoi_v2.html' | relative_url }})
- [Pedrotti/de Chambrier authoritative result]({{ '/docs/results/pedrotti_sampling_missingness_v1.html' | relative_url }})
