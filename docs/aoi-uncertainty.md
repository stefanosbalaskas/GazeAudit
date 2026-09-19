---
title: AOI & Measurement-Uncertainty Interpretation Center
description: Interpret GazeAudit gaze-error models, probabilistic AOI membership, overlap/outside semantics, Monte Carlo precision, hard-versus-probabilistic boundary diagnostics, uncertainty-weighted endpoints, grouped models, and spatial-error sensitivity.
kicker: Workspace · Measurement uncertainty
page_type: aoi-uncertainty-center
permalink: /docs/aoi-uncertainty/
search_category: Start
search_keywords: AOI uncertainty gaze error probabilistic membership overlap outside boundary risk flip probability expected dwell fixation count Monte Carlo grouped model spatial sensitivity
---

# AOI & Measurement-Uncertainty Interpretation Center

Use this center when gaze-position uncertainty could change AOI membership or an AOI-derived scientific endpoint.

<div class="callout warning">
<strong>Probabilistic membership is model-conditional evidence, not model-free truth.</strong>
The result depends on the declared gaze-error model, validation evidence, AOI geometry, Monte Carlo design, grouping, and endpoint. More simulation draws reduce Monte Carlo error under a fixed model; they do not validate the model itself.
</div>

The contracts below are generated from one governed reference. Every card separates:

- what the output literally represents;
- what it can support;
- what it cannot support;
- what must be reported;
- where to inspect the method, API, or reproducible plot.

<form
  class="aoi-uncertainty-controls"
  data-aoi-uncertainty-controls
  role="search"
  aria-label="Filter AOI uncertainty contracts"
>
  <label>
    <span>Search uncertainty contracts</span>
    <input
      type="search"
      autocomplete="off"
      placeholder="Try “outside”, “Monte Carlo”, “boundary”, or “grouped”…"
      data-aoi-uncertainty-search
    >
  </label>

  <button type="button" data-aoi-uncertainty-clear>Clear filter</button>
</form>

<p
  class="aoi-uncertainty-status"
  data-aoi-uncertainty-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  Showing all {{ site.data.aoi_uncertainty_contracts | size }} uncertainty contracts.
</p>

<div class="aoi-uncertainty-grid" data-aoi-uncertainty-grid>
{% for contract in site.data.aoi_uncertainty_contracts %}
  {% capture contract_search %}{{ contract.id }} {{ contract.title }} {{ contract.source }} {{ contract.question }} {{ contract.can_say }} {{ contract.cannot_say }} {{ contract.reporting }}{% endcapture %}
  <article
    class="aoi-uncertainty-card"
    id="uncertainty-{{ contract.id }}"
    data-aoi-uncertainty-card
    data-aoi-uncertainty-search="{{ contract_search | downcase | escape }}"
  >
    <div class="aoi-uncertainty-source">
      <span>Evidence object</span>
      <code>{{ contract.source }}</code>
    </div>

    <h2>{{ contract.title }}</h2>
    <p class="aoi-uncertainty-question"><strong>Question</strong> {{ contract.question }}</p>

    <div class="aoi-uncertainty-claim-grid">
      <section>
        <h3>Can support</h3>
        <p>{{ contract.can_say }}</p>
      </section>
      <section class="aoi-uncertainty-boundary">
        <h3>Does not support</h3>
        <p>{{ contract.cannot_say }}</p>
      </section>
    </div>

    <section class="aoi-uncertainty-reporting">
      <h3>Reporting rule</h3>
      <p>{{ contract.reporting }}</p>
    </section>

    <div class="aoi-uncertainty-routes">
      <a href="{{ contract.guide_path | relative_url }}">Method guide →</a>
      {% if contract.api_anchor != '' %}
        <a href="{{ '/docs/reference/api-pathways/' | relative_url }}#{{ contract.api_anchor }}">API pathway →</a>
      {% endif %}
      {% if contract.plot_path != '' %}
        <a href="{{ contract.plot_path | relative_url }}">Visual example →</a>
      {% endif %}
    </div>
  </article>
{% endfor %}
</div>

<div class="aoi-uncertainty-empty" data-aoi-uncertainty-empty hidden>
  <h2>No uncertainty contract matches this filter</h2>
  <p>Clear the filter or use site search with <strong>Ctrl/Cmd + K</strong>.</p>
</div>

## Start with the measurement model

For the global Gaussian model, GazeAudit defines:

```text
error = observed - true
```

and represents the error distribution with:

- a mean x/y error vector;
- a 2 × 2 covariance matrix;
- the number of validation observations.

A new observed point is propagated by drawing plausible error values and subtracting those errors from the observation.

This is an auditable model assumption.

It is not a claim that all eye-tracker error is Gaussian, stationary, participant-invariant, or spatially homogeneous.

## Raw validation points versus mean radial error

### Pointwise validation

When observed and target x/y coordinates are available, `GaussianGazeErrorModel.fit()` estimates:

- systematic bias;
- residual covariance.

### Mean radial validation summary

`from_mean_radial_error()` can construct an isotropic model from a reported mean Euclidean error under an explicit Rayleigh-to-Gaussian approximation.

That approximation does not reconstruct:

- anisotropy;
- local error fields;
- time variation;
- uncertainty in the reported mean error;
- participant/session heterogeneity unless those are separately modelled.

Report the approximation as an assumption.

## What a membership probability means

`aoi_probabilities()` samples latent true gaze locations under the declared measurement model and calculates the fraction of samples inside each AOI.

A value such as:

```text
claim = 0.73
```

means:

> Under the declared error model and Monte Carlo design, 73% of sampled latent true positions for this observation fell inside the claim AOI.

It does **not** mean:

> There is a model-free 73% probability that the eye was truly looking at the claim.

## AOI probabilities are marginal, not exclusive

AOIs may overlap.

Therefore:

```text
P(AOI A) + P(AOI B)
```

can exceed 1.

That is not a probability error.

The AOI columns are marginal memberships, not mutually exclusive categories.

If `outside` is included, it means:

> the fraction of latent draws belonging to none of the supplied AOIs.

Do not calculate outside as:

```text
1 - sum(AOI probabilities)
```

when AOIs overlap.

## Monte Carlo draws versus model sensitivity

These are different uncertainty layers.

### More draws

Increasing `draws` reduces Monte Carlo simulation variability under the **same** error model.

### Different model scale

Changing the error-model SD or bias changes the scientific measurement assumption.

Use controlled spatial sensitivity to examine that second question.

A 20,000-draw run under a poor model can be more numerically precise while remaining scientifically misspecified.

## Hard assignment versus probabilistic membership

Hard AOI assignment asks:

> Is the observed coordinate inside the geometry?

Probabilistic membership asks:

> Under the declared error model, what fraction of plausible latent true positions fall inside the geometry?

Both can be useful evidence.

The scientifically important question is often:

> Does the substantive endpoint change when measurement uncertainty is propagated rather than ignored?

## Flip probability

For one observation/AOI pair, `compare_hard_probabilistic()` reports the probability that latent membership differs from the observed hard membership.

Examples:

### Hardly ambiguous

```text
hard = inside
membership probability = 0.99
flip probability = 0.01
```

### Highly ambiguous

```text
hard = inside
membership probability = 0.51
flip probability = 0.49
```

The second point is much more sensitive to the AOI boundary under the declared model.

That does not make it invalid.

## Boundary risk

Boundary risk is:

```text
2 × min(p, 1 - p)
```

It ranges from 0 to 1.

- near 0 → model-conditional membership is close to certainly in or certainly out;
- near 1 → membership probability is close to 0.5.

It is a descriptive ambiguity score.

It is not a universal exclusion criterion.

## Grouped models fail closed

When a grouped error model is used, every supplied observation must map to a declared model group.

An unknown or missing group raises rather than silently falling back to the pooled/global model.

That behavior protects the measurement contract.

Before grouped propagation, verify:

- group variable identity;
- complete model coverage;
- validation evidence per group;
- minimum validation support;
- whether grouping was declared before endpoint inspection.

## Expected dwell and expected count

`expected_dwell()` computes:

```text
sum(membership probability × event duration)
```

`expected_fixation_count()` computes:

```text
sum(membership probability)
```

These are expected endpoints under the declared measurement model.

They are not observed latent truth.

Preserve:

- AOI name;
- event/fixation denominator;
- duration unit;
- probability model;
- aggregation unit;
- hard-versus-probabilistic comparison where relevant.

## Spatial-error sensitivity

`scale_error_model()` and `spatial_sensitivity_curve()` let the analysis vary the assumed error magnitude deliberately.

This answers:

> How does the AOI result change as the declared spatial-error assumption changes?

It does not answer:

> Which scale is the true tracker precision?

That requires independent validation evidence.

## Visual interpretation

Use the reproducible [AOI probability profile]({{ '/docs/plots/#plot-aoi-probability-profile' | relative_url }}) to see how model-conditional membership changes across a boundary.

The figure is a synthetic visual contract, not empirical validation evidence.

Also see the [AOI boundary uncertainty illustration]({{ '/assets/images/aoi-boundary-uncertainty.svg' | relative_url }}).

## Reporting examples

### Methods

> Gaze-position uncertainty was modelled using [global/grouped] Gaussian measurement error defined as observed minus validation target position. The model was estimated from [validation source and n], and latent true positions were propagated using [draw count] Monte Carlo draws with [RNG/seed strategy]. AOI membership probabilities were treated as marginal model-conditional memberships; overlapping AOIs were not renormalised into exclusive categories.

### Results

> Hard-versus-probabilistic comparison showed that [x] observations had elevated model-conditional assignment ambiguity under the declared error model. The uncertainty-weighted [dwell/count] endpoint was [value] compared with the corresponding hard-assignment endpoint of [value]. Spatial-error sensitivity across [scales] produced [bounded pattern].

### Limitation

> These results are conditional on the declared gaze-error model, validation evidence, AOI geometry, grouping, and Monte Carlo design. Probabilistic membership does not provide model-free certainty about latent gaze position, and error-model perturbations do not identify the true physical tracker error.

## When not to over-interpret this center

Do not use uncertainty-aware AOI outputs to claim that:

- the Gaussian model is universally correct;
- the most probable AOI is the true AOI with model-free certainty;
- AOI probabilities must sum to one;
- more draws validate a weak measurement model;
- boundary-risk observations should automatically be removed;
- a grouped model can silently substitute pooled values;
- a controlled error scale is the physical tracker truth.

Those claims require evidence outside these functions.

## API links

- [`GaussianGazeErrorModel`]({{ '/docs/reference/api-pathways/#api-gaussiangazeerrormodel' | relative_url }})
- [`aoi_probabilities()`]({{ '/docs/reference/api-pathways/#api-aoi-probabilities' | relative_url }})
- [`compare_hard_probabilistic()`]({{ '/docs/reference/api-pathways/#api-compare-hard-probabilistic' | relative_url }})
- [`expected_dwell()`]({{ '/docs/reference/api-pathways/#api-expected-dwell' | relative_url }})
- [`scale_error_model()`]({{ '/docs/reference/api-pathways/#api-scale-error-model' | relative_url }})
- [`spatial_sensitivity_curve()`]({{ '/docs/reference/api-pathways/#api-spatial-sensitivity-curve' | relative_url }})
- [Machine-readable uncertainty contract reference]({{ '/assets/aoi-uncertainty-reference.json' | relative_url }})

The grouped-model, risk-summary, and expected-fixation-count helpers are documented through the method guide and worked examples when no governed source-level deep link is available.

## Continue from here

- [Interpret AOI uncertainty outputs]({{ '/docs/guides/aoi-uncertainty-interpretation/' | relative_url }}) — detailed semantic, Monte Carlo, overlap, grouping, endpoint, and reporting guidance.
- [AOI uncertainty interpretation walkthrough]({{ '/docs/examples/aoi-uncertainty-interpretation/' | relative_url }}) — deterministic/symmetric synthetic cases.
- [AOI uncertainty guide]({{ '/docs/guides/aoi-uncertainty/' | relative_url }}) — model construction and core workflow.
- [Robustness Diagnostics Center]({{ '/docs/robustness-diagnostics/' | relative_url }}) — combine measurement uncertainty with analytical robustness.
