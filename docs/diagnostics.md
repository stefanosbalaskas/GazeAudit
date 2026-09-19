---
title: Robustness Diagnostics & Sensitivity Center
description: Interpret GazeAudit specification curves, effect stability, marginal and pairwise sensitivity, and controlled spatial, sampling, and missingness perturbation curves without turning descriptive diagnostics into inferential claims.
kicker: Workspace · Robustness diagnostics
page_type: diagnostic-center
permalink: /docs/diagnostics/
search_category: Start
search_keywords: robustness diagnostics specification curve effect stability marginal sensitivity pairwise interaction spatial sampling missingness interpretation reporting limitations
---

# Robustness Diagnostics & Sensitivity Center

Use this center **after the current valid branch state has been reconciled** and before turning robustness diagnostics into manuscript claims.

<div class="callout warning">
<strong>These diagnostics answer different questions.</strong>
Specification-result summaries describe variation across the represented analytical decision space. Controlled perturbation curves deliberately alter one uncertainty dimension. Neither family is a confidence interval, posterior distribution, causal variance decomposition, or automatic scientific conclusion.
</div>

If execution is incomplete, resolve or explicitly report that first in the [Execution Ledger & Recovery Center]({{ '/docs/execution-ledger/' | relative_url }}).

<div class="diagnostic-center-summary">
  <strong>{{ site.data.diagnostic_contracts | size }} governed diagnostic contracts</strong>
  <span>All cards remain visible without JavaScript.</span>
</div>

<form class="diagnostic-center-controls" data-diagnostic-controls role="search" aria-label="Filter robustness diagnostics">
  <label>
    <span>Search diagnostics</span>
    <input
      type="search"
      autocomplete="off"
      placeholder="Try “quantile”, “pairwise”, “sampling”, or “MCAR”…"
      data-diagnostic-search
    >
  </label>

  <label>
    <span>Diagnostic family</span>
    <select data-diagnostic-family>
      <option value="">All families</option>
      <option value="Specification results">Specification results</option>
      <option value="Controlled perturbation">Controlled perturbation</option>
    </select>
  </label>

  <button type="button" data-diagnostic-clear>Clear filters</button>
</form>

<p
  class="diagnostic-center-status"
  data-diagnostic-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  Showing all {{ site.data.diagnostic_contracts | size }} diagnostics.
</p>

<div class="diagnostic-contract-grid" data-diagnostic-grid>
{% for diagnostic in site.data.diagnostic_contracts %}
  {% capture diagnostic_search %}{{ diagnostic.id }} {{ diagnostic.family }} {{ diagnostic.function }} {{ diagnostic.question }} {{ diagnostic.input_contract }} {{ diagnostic.output_fields }} {{ diagnostic.interpretation }} {{ diagnostic.do_not_infer }}{% endcapture %}
  <article
    class="diagnostic-contract-card"
    id="diagnostic-{{ diagnostic.id }}"
    data-diagnostic-card
    data-diagnostic-family="{{ diagnostic.family | escape }}"
    data-diagnostic-search="{{ diagnostic_search | downcase | escape }}"
  >
    <div class="diagnostic-contract-head">
      <span>{{ diagnostic.family }}</span>
      <a href="{{ '/docs/reference/api-pathways/' | relative_url }}#{{ diagnostic.api_anchor }}">
        <code>{{ diagnostic.function }}()</code>
      </a>
    </div>

    <h2>{{ diagnostic.question }}</h2>

    <dl class="diagnostic-contract-meta">
      <div>
        <dt>Input contract</dt>
        <dd>{{ diagnostic.input_contract }}</dd>
      </div>
      <div>
        <dt>Output</dt>
        <dd><code>{{ diagnostic.output_fields }}</code></dd>
      </div>
    </dl>

    <section>
      <h3>Interpretation</h3>
      <p>{{ diagnostic.interpretation }}</p>
    </section>

    <section class="diagnostic-contract-boundary">
      <h3>Do not infer</h3>
      <p>{{ diagnostic.do_not_infer }}</p>
    </section>

    <details>
      <summary>Reporting wording</summary>
      <p data-diagnostic-template="reporting">{{ diagnostic.reporting_template }}</p>
      <button type="button" data-diagnostic-copy="reporting">Copy reporting wording</button>
    </details>

    <details>
      <summary>Limitation wording</summary>
      <p data-diagnostic-template="limitation">{{ diagnostic.limitation_template }}</p>
      <button type="button" data-diagnostic-copy="limitation">Copy limitation wording</button>
    </details>

    <div class="diagnostic-contract-routes">
      <a href="{{ diagnostic.guide_url | relative_url }}">Guide →</a>
      <a href="{{ diagnostic.example_url | relative_url }}">Worked example →</a>
      <a href="{{ diagnostic.plot_url | relative_url }}">Visual →</a>
      <a href="{{ '/docs/reference/api-pathways/' | relative_url }}#{{ diagnostic.api_anchor }}">API →</a>
    </div>
  </article>
{% endfor %}
</div>

<div class="diagnostic-center-empty" data-diagnostic-empty hidden>
  <h2>No diagnostic matches these filters</h2>
  <p>Clear the filters or use site search with <strong>Ctrl/Cmd + K</strong>.</p>
</div>

## Two diagnostic families

### Specification-result summaries

These functions start from a table of represented endpoint estimates.

They answer questions such as:

- what range of finite estimates was represented?;
- how stable was sign relative to a declared null?;
- which factor levels align with the largest descriptive variation?;
- which factor pairs show the largest non-additive descriptive pattern?

The relevant functions are:

- `specification_curve()`;
- `effect_stability()`;
- `marginal_sensitivity()`;
- `pairwise_interaction_sensitivity()`.

All four depend on the **represented result table**. They do not repair an incomplete valid denominator.

### Controlled perturbation curves

These functions deliberately change a specific uncertainty dimension:

- `spatial_sensitivity_curve()` — scale of a declared Gaussian gaze-error model;
- `sampling_sensitivity_curve()` — retained existing samples near lower-rate target grids;
- `missingness_sensitivity_curve()` — injected MCAR or blockwise missing gaze.

These curves ask:

> What happens to the chosen outcome or diagnostic as this declared perturbation changes?

They do not claim that the perturbation reproduces another physical tracker or the study's true missingness process.

## Finite-estimate boundary

The specification-result diagnostics share a strict input guard.

`effect_stability()`, `marginal_sensitivity()`, `pairwise_interaction_sensitivity()`, and `specification_curve()` call the same internal finite-estimate validation:

- estimate column must exist;
- table must contain at least one specification;
- values are coerced to numeric;
- any resulting non-finite value raises.

Therefore, reconcile non-finite endpoint branches **before** passing a result table into these summaries.

`sampling_sensitivity_curve()` and `missingness_sensitivity_curve()` also require the supplied endpoint to return a finite scalar at every perturbation level.

## Empirical specification quantiles are not confidence intervals

`effect_stability()` returns `q025` and `q975`.

These are empirical quantiles of the represented specification estimates.

They do **not** provide:

- 95% frequentist coverage;
- posterior credible probability;
- uncertainty about an unobserved population parameter.

Preferred wording:

> The empirical 2.5th and 97.5th percentiles of the represented specification estimates were [values].

Avoid:

> The 95% confidence interval was [values].

unless a separate inferential model actually produced that interval.

## The null is a scientific input

`effect_stability()` has a software default:

```python
null=0.0
```

That default is not a scientific recommendation.

If zero is not the scientifically meaningful reference for the endpoint, pass the appropriate declared null and report it.

The function computes sign fractions after centering estimates on that null.

## Sign stability is descriptive

The function reports:

```text
positive_fraction
negative_fraction
exact_null_fraction
sign_stability
```

`sign_stability` is the maximum of those three observed fractions.

It is not:

- probability that the true effect has that sign;
- posterior model probability;
- evidence that magnitude is stable.

A specification set can have `sign_stability = 1.0` while estimates vary materially in size.

## Marginal sensitivity

For each declared factor, `marginal_sensitivity()` reports:

- `n_levels`;
- `marginal_eta2`;
- `level_mean_range`.

`marginal_eta2` is the between-level sum of squares divided by total endpoint sum of squares in the represented table.

If total endpoint variation is zero, the function reports `0.0`.

Because multiverse factors can be dependent or interacting, these ratios:

- can overlap;
- need not sum to one;
- are not causal shares of scientific uncertainty.

## Pairwise interaction sensitivity

For each factor pair, the diagnostic compares observed cell means with an additive prediction:

```text
mean(A level) + mean(B level) - grand mean
```

It reports:

- number of represented cells;
- `interaction_ratio`;
- maximum absolute non-additive deviation.

This is a descriptive screening diagnostic.

It is not a fitted factorial model, inferential interaction coefficient, significance test, or causal interaction estimate.

With fewer than two factors, the function returns an empty table with the expected columns.

## Controlled spatial sensitivity

`spatial_sensitivity_curve()` varies `sd_scale`.

Important boundaries:

- scales must be non-negative;
- points must be finite n×2 coordinates;
- optional durations must be finite and non-negative;
- the scale multiplies standard deviations, so covariance scales by `sd_scale**2`;
- systematic mean bias is unchanged in this curve;
- repeated runs with the same seed are reproducible, while each scale receives a separate child seed.

A scaled error model is a sensitivity perturbation—not an empirical estimate of a new tracker.

## Controlled sampling sensitivity

`sampling_sensitivity_curve()` uses `downsample_gaze()`.

The perturbation:

- requires positive finite target rates;
- supports timestamp units `ms` and `s`;
- validates within-unit time order;
- retains existing samples nearest an ideal target grid;
- does not interpolate gaze coordinates;
- reports row retention alongside the finite endpoint.

Therefore it is a **representation sensitivity analysis**, not a hardware simulation.

## Controlled missingness sensitivity

`missingness_sensitivity_curve()` supports:

- `mcar`;
- `block`.

Injected fractions must lie between 0 and 1.

The output separates:

- requested injected fraction;
- observed total missing fraction;
- number missing;
- endpoint.

Observed total missingness can differ from the requested injected fraction because the original study may already contain missing gaze.

The MCAR/block labels describe the synthetic perturbation mechanism, not an empirical diagnosis of the real missing-data process.

## A safe interpretation sequence

1. **Reconcile execution completeness.** Do not summarize away unresolved valid branches.
2. **Verify one common endpoint.**
3. **Inspect the ordered specification curve.**
4. **Separate sign from magnitude with effect stability.**
5. **Localize descriptive factor-level variation.**
6. **Inspect pairwise non-additivity when scientifically useful.**
7. **Keep controlled perturbation curves separate from the discrete specification space.**
8. **State untested uncertainty dimensions.**
9. **Write the denominator and limitation next to the diagnostic claim.**

## Reporting examples

### Methods

> Robustness diagnostics were calculated on the reconciled table of finite represented endpoint estimates. We inspected the ordered specification curve, descriptive effect-stability summaries relative to the declared null, and marginal/pairwise factor sensitivity. Controlled spatial, sampling, and missingness curves were analysed separately as explicit perturbation experiments.

### Results

> Across [N] represented specifications, endpoint estimates ranged from [min] to [max] with median [median]. Directional fractions relative to the declared null were [values]. Descriptive marginal sensitivity was greatest for [factor], while the strongest pairwise non-additive pattern involved [factor pair]. Controlled perturbation curves are reported separately.

### Limitation

> These diagnostics are descriptive and conditional on the represented specification space and declared perturbation families. Empirical specification quantiles are not confidence or credible intervals, sensitivity ratios are not causal variance decompositions, and controlled perturbations do not establish the true data-generating mechanism.

## API links

- [`specification_curve()`]({{ '/docs/reference/api-pathways/#api-specification-curve' | relative_url }})
- [`effect_stability()`]({{ '/docs/reference/api-pathways/#api-effect-stability' | relative_url }})
- [`marginal_sensitivity()`]({{ '/docs/reference/api-pathways/#api-marginal-sensitivity' | relative_url }})
- [`pairwise_interaction_sensitivity()`]({{ '/docs/reference/api-pathways/#api-pairwise-interaction-sensitivity' | relative_url }})
- [`spatial_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-spatial-sensitivity-curve' | relative_url }})
- [`sampling_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-sampling-sensitivity-curve' | relative_url }})
- [`missingness_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-missingness-sensitivity-curve' | relative_url }})
- [Machine-readable diagnostic contracts]({{ '/assets/diagnostic-contract-reference.json' | relative_url }})

## Continue from here

- [Interpret robustness and sensitivity diagnostics]({{ '/docs/guides/diagnostic-interpretation/' | relative_url }}) — detailed methodology, failure cases, and reporting rules.
- [Diagnostic interpretation worked example]({{ '/docs/examples/diagnostic-interpretation/' | relative_url }}) — deterministic synthetic truth for specification and controlled sensitivity outputs.
- [Results Interpretation & Reporting Center]({{ '/docs/reporting-center/' | relative_url }}) — convert the completed diagnostic evidence into bounded manuscript wording.
