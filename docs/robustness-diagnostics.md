---
title: Robustness Diagnostics & Sensitivity Interpretation Center
description: Interpret GazeAudit execution completeness, specification curves, effect stability, marginal sensitivity, pairwise sensitivity, and controlled perturbation curves with explicit denominator, visual, reporting, and inferential boundaries.
kicker: Workspace · Robustness interpretation
page_type: robustness-diagnostics
permalink: /docs/robustness-diagnostics/
search_category: Start
search_keywords: robustness diagnostics specification curve effect stability marginal sensitivity pairwise sensitivity interpretation plot reporting limitations denominator
---

# Robustness Diagnostics & Sensitivity Interpretation Center

Use this center **after the endpoint, specification space, validity rules, and execution ledger are fixed**.

<div class="callout warning">
<strong>Do not interpret robustness diagnostics before execution completeness is reconstructable.</strong>
A specification curve or sensitivity table summarises represented endpoint values. It does not erase unresolved valid branches, non-finite endpoints, or technical failures.
</div>

The six diagnostic families below are generated from one governed catalog. They keep three questions separate:

1. **What does the output literally describe?**
2. **What scientific interpretation can it support?**
3. **What stronger claim does it not support?**

<form class="robustness-diagnostic-controls" data-robustness-controls role="search" aria-label="Filter robustness diagnostics">
  <label>
    <span>Search diagnostics</span>
    <input
      type="search"
      autocomplete="off"
      placeholder="Try “sign”, “interaction”, “missingness”, or “failure”…"
      data-robustness-search
    >
  </label>

  <label>
    <span>Output type</span>
    <select data-robustness-kind>
      <option value="">All output types</option>
      <option value="prerequisite">Prerequisite</option>
      <option value="ordered branch table">Ordered branch table</option>
      <option value="descriptive summary">Descriptive summary</option>
      <option value="descriptive factor table">Descriptive factor table</option>
      <option value="descriptive pair table">Descriptive pair table</option>
      <option value="controlled perturbation curve">Controlled perturbation curve</option>
    </select>
  </label>

  <button type="button" data-robustness-clear>Clear filters</button>
</form>

<p
  class="robustness-diagnostic-status"
  data-robustness-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  Showing all {{ site.data.robustness_diagnostics | size }} diagnostic families.
</p>

<div class="robustness-diagnostic-grid" data-robustness-grid>
{% for diagnostic in site.data.robustness_diagnostics %}
  {% capture diagnostic_search %}{{ diagnostic.id }} {{ diagnostic.title }} {{ diagnostic.question }} {{ diagnostic.source }} {{ diagnostic.key_fields }} {{ diagnostic.can_answer }} {{ diagnostic.cannot_answer }} {{ diagnostic.reporting }}{% endcapture %}
  <article
    class="robustness-diagnostic-card"
    id="diagnostic-{{ diagnostic.id }}"
    data-robustness-card
    data-robustness-kind="{{ diagnostic.output_kind | escape }}"
    data-robustness-search="{{ diagnostic_search | downcase | escape }}"
  >
    <div class="robustness-diagnostic-topline">
      <span>{{ diagnostic.output_kind }}</span>
      <code>{{ diagnostic.source }}</code>
    </div>

    <h2>{{ diagnostic.title }}</h2>
    <p class="robustness-diagnostic-question"><strong>Question</strong> {{ diagnostic.question }}</p>

    <dl class="robustness-diagnostic-meta">
      <div>
        <dt>Key fields</dt>
        <dd>{{ diagnostic.key_fields }}</dd>
      </div>
      <div>
        <dt>Reporting rule</dt>
        <dd>{{ diagnostic.reporting }}</dd>
      </div>
    </dl>

    <div class="robustness-claim-grid">
      <section>
        <h3>Can support</h3>
        <p>{{ diagnostic.can_answer }}</p>
      </section>
      <section class="robustness-claim-boundary">
        <h3>Does not support</h3>
        <p>{{ diagnostic.cannot_answer }}</p>
      </section>
    </div>

    <div class="robustness-diagnostic-routes">
      <a href="{{ diagnostic.next_path | relative_url }}">Open practical route →</a>
      {% if diagnostic.api_anchor != '' %}
        <a href="{{ '/docs/reference/api-pathways/' | relative_url }}#{{ diagnostic.api_anchor }}">API pathway →</a>
      {% endif %}
      {% if diagnostic.plot_id != '' %}
        <a href="{{ '/docs/plots/#plot-' | append: diagnostic.plot_id | relative_url }}">Plot example →</a>
      {% endif %}
    </div>
  </article>
{% endfor %}
</div>

<div class="robustness-diagnostic-empty" data-robustness-empty hidden>
  <h2>No diagnostic matches these filters</h2>
  <p>Clear the filter or use site search with <strong>Ctrl/Cmd + K</strong>.</p>
</div>

## Interpretation order

Read diagnostics in this order.

### 1. Execution completeness

Before any estimate summary, reconstruct:

- declared combinations;
- valid combinations;
- successful branches;
- valid technical failures;
- non-finite endpoints;
- branches not run.

If the valid denominator is not fully represented, the available diagnostic pattern is incomplete.

Use the [Execution Ledger & Recovery Center]({{ '/docs/execution-ledger/' | relative_url }}).

### 2. Specification curve

Use the curve to inspect:

- range;
- sign changes;
- clusters;
- gaps;
- factor combinations attached to extreme estimates.

Do not use ordered position as a quality ranking.

The leftmost and rightmost specifications are simply the lowest and highest represented endpoint estimates.

### 3. Effect stability

`effect_stability()` reports:

- count;
- mean;
- median;
- minimum;
- maximum;
- empirical 2.5% and 97.5% specification quantiles;
- positive, negative, and exact-null fractions;
- sign stability.

These are **descriptive summaries of the represented specifications**.

The empirical quantiles are not confidence intervals or credible intervals.

### 4. Marginal sensitivity

`marginal_sensitivity()` compares endpoint means across levels of each declared factor.

Its `marginal_eta2` is a descriptive between-level sum-of-squares ratio.

It can help locate where variation aligns with declared choices.

It is not:

- causal variance attribution;
- a probability;
- an inferential effect size;
- guaranteed to sum to one across factors.

### 5. Pairwise sensitivity

`pairwise_interaction_sensitivity()` compares represented cell means with an additive factor-level expectation.

Use it to identify non-additive specification patterns.

Do not call `interaction_ratio` a statistical interaction test.

If a formal interaction is scientifically required, fit an appropriate model under its own assumptions.

### 6. Controlled sensitivity curves

Sampling, missingness, and spatial-error sensitivity curves differ conceptually from discrete specification spaces.

They ask:

> What happens as one declared perturbation dimension changes?

Do not interpret downsampling as a physical simulation of another eye tracker, or added missingness as a causal missing-data experiment unless the design independently supports that claim.

## Finite endpoint prerequisite

The robustness summary functions use a common finite-estimate validation path.

If the selected endpoint column:

- is missing;
- contains no rows;
- contains `NaN`;
- contains infinity;

the summary should fail rather than silently reinterpret the unavailable value.

That is desirable.

Resolve the execution/end-point contract before asking for robustness summaries.

## Read the plot as a visual summary, not new evidence

The [Plot gallery]({{ '/docs/plots/' | relative_url }}) contains deterministic code-generated examples.

Two especially relevant plots are:

- [Specification curve]({{ '/docs/plots/#plot-specification-curve' | relative_url }});
- [Specification-factor sensitivity]({{ '/docs/plots/#plot-factor-sensitivity' | relative_url }}).

The plots help visualise an existing analysis table. They do not create a new inferential result.

## A four-question diagnostic reading

For every plot or table, ask:

1. **Denominator:** Which valid represented branches produced this output?
2. **Quantity:** Which exact endpoint field is being summarised?
3. **Pattern:** What is literally visible or numerically described?
4. **Boundary:** Which stronger interpretation remains unsupported?

If one of those answers is missing, do not compress the result into a label such as “robust”.

## Reporting examples

### Methods

> Robustness was evaluated across the declared valid specification space using a single common endpoint. Execution completeness was reconciled before descriptive specification summaries were calculated. We inspected the ordered specification curve, effect-stability summary, marginal factor sensitivity, and pairwise non-additive sensitivity. These diagnostics were treated descriptively rather than as confidence intervals, posterior probabilities, causal decompositions, or inferential interaction tests.

### Results

> [S] of [V] valid specifications successfully yielded finite endpoint estimates. Across those represented branches, estimates ranged from [min] to [max], with median [median] and empirical 2.5%–97.5% specification quantiles of [q025] to [q975]. [Positive/negative/exact-null pattern]. Descriptive marginal sensitivity was largest for [factor], while the strongest pairwise non-additive pattern involved [factor A × factor B].

### Limitation

> These diagnostics characterise the declared and successfully represented analytical space. They do not quantify uncertainty from untested analytical or measurement choices, and the specification quantiles/sign fractions are not sampling-theory or posterior uncertainty statements.

## When not to use a robustness diagnostic

Do not interpret these summaries when:

- branches estimate different endpoints;
- the valid denominator cannot be reconstructed;
- non-finite endpoints were silently converted to zero;
- failed valid branches were deleted;
- specification factors were chosen after inspecting which values produced attractive outcomes;
- the scientific question actually concerns sampling uncertainty rather than across-specification variation.

Resolve the upstream contract first.

## API links

- [`specification_curve()`]({{ '/docs/reference/api-pathways/#api-specification-curve' | relative_url }})
- [`effect_stability()`]({{ '/docs/reference/api-pathways/#api-effect-stability' | relative_url }})
- [`spatial_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-spatial-sensitivity-curve' | relative_url }})
- [`sampling_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-sampling-sensitivity-curve' | relative_url }})
- [`missingness_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-missingness-sensitivity-curve' | relative_url }})
- [Machine-readable diagnostic reference]({{ '/assets/robustness-diagnostic-reference.json' | relative_url }})

`marginal_sensitivity()` and `pairwise_interaction_sensitivity()` are documented here and in the worked examples, but this center does not invent stable API deep links for symbols absent from the governed source-level API inventory.

## Continue from here

- [Read robustness diagnostics]({{ '/docs/guides/robustness-diagnostics/' | relative_url }}) — detailed methodological interpretation and failure cases.
- [Diagnostic interpretation walkthrough]({{ '/docs/examples/robustness-diagnostic-walkthrough/' | relative_url }}) — one synthetic result table interpreted across all diagnostic layers.
- [Reporting robustness]({{ '/docs/guides/reporting-robustness/' | relative_url }}) — manuscript wording.
- [Results Interpretation & Reporting Center]({{ '/docs/reporting-center/' | relative_url }}) — cross-method claim boundaries.
