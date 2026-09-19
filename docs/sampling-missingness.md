---
title: Sampling & Missingness Sensitivity Center
description: Design and interpret controlled GazeAudit sampling-rate and gaze-missingness perturbations without confusing lower-rate representations with hardware simulation or benchmark missingness mechanisms with empirical missing-data causes.
kicker: Workspace · Controlled sensitivity
page_type: sampling-missingness
permalink: /docs/sampling-missingness/
search_category: Start
search_keywords: sampling missingness sensitivity downsample gaze MCAR block perturbation target rate retained fraction observed missing fraction seed endpoint reproducibility
---

# Sampling & Missingness Sensitivity Center

Use this center when the scientific question is about **controlled representation loss** rather than a full discrete multiverse.

<div class="callout warning">
<strong>No target rate, missingness fraction, mechanism, seed, or replication count is a scientific default.</strong>
The builder starts blank. Choose values from the study design, device/method evidence, preregistration, or another independently justified sensitivity plan. The frozen Pedrotti/de Chambrier protocol is a case-specific validation record, not a settings template.
</div>

Before designing the perturbation, preserve:

- the original sampling/time representation;
- observed gaze-coordinate missingness;
- one common scalar endpoint;
- the reason each target rate or missingness fraction belongs in the sensitivity range;
- whether the analysis is a single deterministic/seeded curve or an outer replicated perturbation design.

## Runtime contract reference

<div class="sampling-contract-summary">
  <strong>{{ site.data.sampling_missingness_contracts | size }} governed sampling/missingness contracts</strong>
  <span>All cards remain visible without JavaScript.</span>
</div>

<form
  class="sampling-contract-controls"
  data-sampling-contract-controls
  role="search"
  aria-label="Filter sampling and missingness contracts"
>
  <label>
    <span>Search contracts</span>
    <input
      type="search"
      autocomplete="off"
      placeholder="Try “MCAR”, “retained fraction”, or “hardware”…"
      data-sampling-contract-search
    >
  </label>

  <label>
    <span>Family</span>
    <select data-sampling-contract-family>
      <option value="">All families</option>
      <option value="Observed missingness">Observed missingness</option>
      <option value="Sampling perturbation">Sampling perturbation</option>
      <option value="Sampling sensitivity">Sampling sensitivity</option>
      <option value="Missingness perturbation">Missingness perturbation</option>
      <option value="Missingness sensitivity">Missingness sensitivity</option>
    </select>
  </label>

  <button type="button" data-sampling-contract-clear>Clear filters</button>
</form>

<p
  class="sampling-contract-status"
  data-sampling-contract-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  Showing all {{ site.data.sampling_missingness_contracts | size }} contracts.
</p>

<div class="sampling-contract-grid" data-sampling-contract-grid>
{% for contract in site.data.sampling_missingness_contracts %}
  {% capture sampling_search %}{{ contract.id }} {{ contract.label }} {{ contract.family }} {{ contract.function_name }} {{ contract.question }} {{ contract.operation }} {{ contract.input_contract }} {{ contract.output_contract }} {{ contract.randomness }} {{ contract.preserves }} {{ contract.when_use }} {{ contract.when_not }} {{ contract.boundary }}{% endcapture %}
  <article
    class="sampling-contract-card"
    id="sampling-contract-{{ contract.id }}"
    data-sampling-contract-card
    data-sampling-contract-family="{{ contract.family | escape }}"
    data-sampling-contract-search="{{ sampling_search | downcase | escape }}"
  >
    <div class="sampling-contract-badges">
      <span>{{ contract.family }}</span>
      <code>{{ contract.function_name }}</code>
    </div>

    <h2>{{ contract.label }}</h2>
    <p><strong>Question:</strong> {{ contract.question }}</p>
    <p>{{ contract.operation }}</p>

    <dl class="sampling-contract-meta">
      <div>
        <dt>Input contract</dt>
        <dd>{{ contract.input_contract }}</dd>
      </div>
      <div>
        <dt>Output contract</dt>
        <dd>{{ contract.output_contract }}</dd>
      </div>
      <div>
        <dt>Randomness</dt>
        <dd>{{ contract.randomness }}</dd>
      </div>
      <div>
        <dt>Preserves</dt>
        <dd>{{ contract.preserves }}</dd>
      </div>
    </dl>

    <div class="sampling-contract-use-grid">
      <section>
        <h3>Use when</h3>
        <p>{{ contract.when_use }}</p>
      </section>
      <section class="sampling-contract-boundary">
        <h3>Do not infer</h3>
        <p>{{ contract.when_not }}</p>
        <p><strong>Boundary:</strong> {{ contract.boundary }}</p>
      </section>
    </div>

    <a href="{{ '/docs/reference/api-pathways/' | relative_url }}#{{ contract.api_anchor }}">
      API contract →
    </a>
  </article>
{% endfor %}
</div>

<div class="sampling-contract-empty" data-sampling-contract-empty hidden>
  <h2>No contract matches these filters</h2>
  <p>Clear the filters or use site search with <strong>Ctrl/Cmd + K</strong>.</p>
</div>

## Build a controlled sensitivity plan

This form generates documentation-side provenance plus an explicit Python skeleton. It does not inspect data or choose perturbations.

<form class="sampling-plan-builder" data-sampling-plan-builder>
  <div class="sampling-plan-grid">
    <label for="sampling-plan-name">
      <span>Plan name</span>
      <input id="sampling-plan-name" type="text" autocomplete="off" required data-plan-name>
    </label>

    <label for="sampling-endpoint-reference">
      <span>Endpoint declaration reference</span>
      <input
        id="sampling-endpoint-reference"
        type="text"
        autocomplete="off"
        required
        data-plan-endpoint
      >
    </label>

    <label for="sampling-family">
      <span>Sensitivity family</span>
      <select id="sampling-family" required data-plan-family>
        <option value="">Choose explicitly…</option>
        <option value="sampling">Sampling only</option>
        <option value="missingness">Added missingness only</option>
        <option value="separate_both">Sampling and missingness as separate families</option>
      </select>
    </label>

    <label for="sampling-baseline-reference">
      <span>Baseline representation / observed-missingness reference</span>
      <input
        id="sampling-baseline-reference"
        type="text"
        autocomplete="off"
        required
        data-plan-baseline
      >
    </label>

    <label class="sampling-plan-wide" for="sampling-rationale">
      <span>Scientific rationale for the perturbation range</span>
      <textarea id="sampling-rationale" rows="3" required data-plan-rationale></textarea>
    </label>

    <label class="sampling-plan-wide" for="sampling-interpretation-boundary">
      <span>Interpretation boundary</span>
      <textarea
        id="sampling-interpretation-boundary"
        rows="3"
        required
        data-plan-boundary
      ></textarea>
    </label>
  </div>

  <fieldset class="sampling-plan-family" data-plan-sampling-fields disabled>
    <legend>Sampling representation</legend>

    <label for="sampling-target-rates">
      <span>Target rates — one Hz value per line</span>
      <textarea id="sampling-target-rates" rows="5" data-plan-rates></textarea>
    </label>

    <label for="sampling-timestamp-unit">
      <span>Timestamp unit</span>
      <select id="sampling-timestamp-unit" data-plan-timestamp-unit>
        <option value="">Choose explicitly…</option>
        <option value="ms">Milliseconds</option>
        <option value="s">Seconds</option>
      </select>
    </label>
  </fieldset>

  <fieldset class="sampling-plan-family" data-plan-missingness-fields disabled>
    <legend>Added missingness</legend>

    <label for="missingness-fractions">
      <span>Requested fractions — one value from 0 to 1 per line</span>
      <textarea id="missingness-fractions" rows="5" data-plan-fractions></textarea>
    </label>

    <label for="missingness-mechanism">
      <span>Benchmark mechanism</span>
      <select id="missingness-mechanism" data-plan-mechanism>
        <option value="">Choose explicitly…</option>
        <option value="mcar">MCAR benchmark perturbation</option>
        <option value="block">Within-stream block benchmark perturbation</option>
      </select>
    </label>

    <label for="missingness-seed">
      <span>Root seed</span>
      <input
        id="missingness-seed"
        type="number"
        step="1"
        inputmode="numeric"
        data-plan-seed
      >
    </label>

    <label for="missingness-replication">
      <span>Outer replication plan (optional)</span>
      <input
        id="missingness-replication"
        type="text"
        autocomplete="off"
        placeholder="e.g. 20 independent outer calls per fraction"
        data-plan-replication
      >
    </label>
  </fieldset>

  <div class="sampling-plan-actions">
    <button type="submit">Generate sensitivity plan</button>
    <button type="button" data-plan-clear>Clear plan</button>
  </div>
</form>

<div
  class="sampling-plan-errors"
  data-plan-errors
  role="alert"
  tabindex="-1"
  hidden
></div>

<p
  class="sampling-plan-status"
  data-plan-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  No sensitivity plan generated yet.
</p>

<div class="sampling-plan-output-grid">
  <article>
    <h2>Documentation-side plan JSON</h2>
    <p>
      This record is provenance only. It does not establish that the selected rates, fractions, mechanism, seed, or replication scheme are scientifically appropriate.
    </p>
    <pre><code class="language-json" data-plan-json>{
  "schema": "gazeaudit-sampling-missingness-plan-v1"
}</code></pre>
    <button type="button" data-plan-copy="json" disabled>Copy JSON</button>
  </article>

  <article>
    <h2>Python sensitivity skeleton</h2>
    <p>
      Sampling and added missingness are generated as separate curves. The builder never creates a sampling × missingness cross-product implicitly.
    </p>
    <pre><code class="language-python" data-plan-python># Complete the sensitivity plan first.</code></pre>
    <button type="button" data-plan-copy="python" disabled>Copy Python</button>
  </article>
</div>

## Observed missingness comes first

Before injecting anything:

```python
from gazeaudit import summarize_missingness

baseline_missingness = summarize_missingness(study)
print(baseline_missingness)
```

The baseline tells you what is already absent in the canonical representation.

Added missingness is then a **perturbation on top of that baseline**.

## Requested and observed missingness can differ

`inject_missingness()` selects from currently complete rows.

If one row is already missing in a 10-row study, then a requested fraction of 0.50 acts on 9 complete rows:

```text
round(0.50 × 9) = 4 additional rows masked
1 native missing + 4 added missing = 5 / 10 total missing
```

So:

```text
requested added fraction = 0.50 of complete rows
observed total missing fraction = 0.50 of all rows
```

Those quantities can coincide numerically in one fixture while still having different denominators and meanings. In other source sizes they can differ because of rounding and native missingness.

## One curve call is not a replicate distribution

`missingness_sensitivity_curve()` derives one child seed per fraction and produces one perturbed endpoint per fraction for that call.

A single call does **not** estimate:

- a confidence interval;
- Monte Carlo uncertainty;
- a distribution of possible missingness realizations;
- uncertainty about the empirical missingness mechanism.

If repeated random perturbations are part of the scientific plan, declare an outer replication design explicitly and preserve every seed/replicate.

## Sampling is not hardware simulation

`downsample_gaze()` retains existing rows nearest to an ideal lower-rate grid.

It does not simulate:

- different optics;
- calibration quality;
- firmware;
- device-specific sample loss;
- timing jitter;
- sensor noise;
- a physically different trajectory.

Report it as a controlled lower-rate representation of the same recorded stream.

## Sampling does not interpolate

No new gaze coordinate is created.

A lower target rate may retain fewer rows than a simple source-rate ratio suggests because source timing, trial boundaries, and uniqueness of nearest positions matter.

Always report actual `n_rows` and `retained_fraction` from the curve.

## MCAR and block are benchmark mechanisms

The two built-in added-missingness mechanisms answer:

> How does the endpoint react to this controlled form of gaze loss?

They do not answer:

> Why was gaze missing in the empirical study?

Using `mechanism="mcar"` is not evidence that empirical missingness is MCAR.

Using `mechanism="block"` is not evidence that empirical loss occurs in one contiguous block.

## Report sampling and missingness separately by default

A lower-rate representation and added missingness are different perturbations.

Unless the protocol explicitly defines their combination, report:

- one sampling sensitivity family;
- one added-missingness family.

Do not automatically build a Cartesian sampling × missingness multiverse.

## Reporting examples

### Methods

> Sampling sensitivity was evaluated by retaining existing source observations nearest to prespecified lower-rate grids of [rates] Hz using [timestamp unit] timestamps; gaze coordinates were not interpolated. Added-missingness sensitivity was evaluated separately at the declared baseline representation using [MCAR/block] benchmark masking at fractions [fractions] with root seed [seed]. The same prespecified endpoint was evaluated for every perturbation.

### Results

> Across the sampling curve, retained rows ranged from [n/retained fraction] and the endpoint ranged from [min] to [max]. Under added missingness, requested fractions ranged from [x] to [y], realized total missingness ranged from [x] to [y], and endpoint values ranged from [min] to [max]. [Replication accounting, if used.]

### Limitation

> These analyses probe controlled representations of the recorded data. They do not establish equivalence to another physical tracker, identify the empirical missingness mechanism, recover unobserved gaze, or provide sampling-theory uncertainty intervals.

## API links

- [`downsample_gaze()`]({{ '/docs/reference/api-pathways/#api-downsample-gaze' | relative_url }})
- [`sampling_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-sampling-sensitivity-curve' | relative_url }})
- [`missingness_mask()`]({{ '/docs/reference/api-pathways/#api-missingness-mask' | relative_url }})
- [`summarize_missingness()`]({{ '/docs/reference/api-pathways/#api-summarize-missingness' | relative_url }})
- [`inject_missingness()`]({{ '/docs/reference/api-pathways/#api-inject-missingness' | relative_url }})
- [`missingness_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-missingness-sensitivity-curve' | relative_url }})
- [Machine-readable contract reference]({{ '/assets/sampling-missingness-reference.json' | relative_url }})

## Continue from here

- [Design sampling and missingness sensitivity]({{ '/docs/guides/sampling-missingness-sensitivity/' | relative_url }}) — full methodological guidance.
- [Sampling & missingness design audit]({{ '/docs/examples/sampling-missingness-design-audit/' | relative_url }}) — synthetic runtime-linked exercise.
- [Sampling sensitivity example]({{ '/docs/examples/sampling-sensitivity/' | relative_url }}) — existing compact sampling workflow.
- [Robustness Diagnostics Center]({{ '/docs/robustness-diagnostics/' | relative_url }}) — interpret completed controlled sensitivity alongside the rest of the audit.
- [Pedrotti/de Chambrier frozen protocol]({{ '/docs/protocols/PEDROTTI2023_SAMPLING_MISSINGNESS_V1.html' | relative_url }}) — protocol-bound empirical validation example; do not reuse its settings automatically.
