---
title: Endpoint Definition & Handoff Center
description: Declare the scientific quantity that every GazeAudit specification must estimate, preserve units, contrast direction, aggregation, denominator, missingness and non-finite behavior, and generate an auditable endpoint skeleton without inventing calculation code.
kicker: Workspace · Endpoint contract
page_type: endpoint-contract
permalink: /docs/endpoint-contract/
search_category: Start
search_keywords: endpoint definition estimand scientific quantity scalar run_specs contrast unit analysis unit denominator missing nonfinite endpoint drift handoff
---

# Endpoint Definition & Handoff Center

Use this center **before executing a specification space**. A robustness audit is interpretable only when every valid branch estimates the **same declared scientific quantity**, even though preprocessing, measurement, AOI, QC, sampling, or other defensible analytical choices may vary.

<div class="callout warning">
<strong>This builder does not invent an endpoint.</strong>
It records your endpoint declaration and generates an intentionally incomplete Python skeleton. You must implement and validate the scientific calculation yourself. No contrast, unit, aggregation, missingness rule, null value, or non-finite policy is supplied by GazeAudit.
</div>

The runtime contract behind this page is small but important: `run_specs()` passes `(processed_object, specification)` to the endpoint callable and coerces the returned value with `float(...)`. That coercion does **not** itself reject `NaN` or infinity. If finiteness is part of your endpoint contract, enforce it explicitly.

<form class="endpoint-builder" data-endpoint-builder>
  <div class="endpoint-field-grid">
  {% for field in site.data.endpoint_contract_fields %}
    <label
      class="endpoint-field-card"
      for="endpoint-{{ field.name }}"
      data-endpoint-field
      data-endpoint-name="{{ field.name }}"
      data-endpoint-required="{{ field.required }}"
    >
      <span class="endpoint-field-head">
        <span>
          <code>{{ field.name }}</code>
          <strong>{{ field.label }}</strong>
        </span>
        {% if field.required %}
          <span class="endpoint-required">Required</span>
        {% else %}
          <span class="endpoint-optional">Optional</span>
        {% endif %}
      </span>

      <span class="endpoint-field-purpose">{{ field.purpose }}</span>

      {% if field.value_type == 'textarea' %}
      <textarea
        id="endpoint-{{ field.name }}"
        rows="3"
        {% if field.required %}required{% endif %}
        data-endpoint-value
      ></textarea>
      {% else %}
      <input
        id="endpoint-{{ field.name }}"
        type="text"
        autocomplete="off"
        {% if field.required %}required{% endif %}
        data-endpoint-value
      >
      {% endif %}

      <span class="endpoint-field-boundary">
        <strong>Boundary</strong>
        {{ field.boundary }}
      </span>
    </label>
  {% endfor %}
  </div>

  <fieldset class="endpoint-finite-guard">
    <legend>Optional code guard</legend>
    <label>
      <input type="checkbox" data-endpoint-finite-guard>
      <span>Generate an explicit `np.isfinite(...)` failure guard in the Python skeleton.</span>
    </label>
    <p>
      Leave this unchecked if your declared non-finite policy is implemented elsewhere. Checking it is a software guard choice, not a package recommendation about your scientific endpoint.
    </p>
  </fieldset>

  <div class="endpoint-builder-actions">
    <button type="submit">Generate endpoint declaration</button>
    <button type="button" data-endpoint-clear>Clear declaration</button>
  </div>
</form>

<div
  class="endpoint-builder-errors"
  data-endpoint-errors
  role="alert"
  tabindex="-1"
  hidden
></div>

<p
  class="endpoint-builder-status"
  data-endpoint-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  No endpoint declaration generated yet.
</p>

<div class="endpoint-output-grid">
  <article>
    <h2>Documentation-side endpoint declaration</h2>
    <p>
      This JSON is a descriptive project record. It is not a new GazeAudit runtime object and does not prove construct validity.
    </p>
    <pre><code class="language-json" data-endpoint-json>{
  "schema": "gazeaudit-endpoint-declaration-v1"
}</code></pre>
    <button type="button" data-endpoint-copy="json" disabled>Copy JSON</button>
  </article>

  <article>
    <h2>Python endpoint skeleton</h2>
    <p>
      The generated skeleton is **intentionally incomplete**. The calculation remains a `NotImplementedError` until you replace it with the prespecified endpoint implementation.
    </p>
    <pre><code class="language-python" data-endpoint-python># Complete the endpoint declaration first.</code></pre>
    <button type="button" data-endpoint-copy="python" disabled>Copy Python</button>
  </article>
</div>

## The common-endpoint rule

`run_specs()` is designed to answer:

> How does the **same scientific quantity** change when defensible analytical choices change?

A branch may vary:

- QC policy;
- detector family/parameters;
- AOI representation;
- missing-data handling;
- sampling representation;
- preprocessing;
- another declared analytical decision.

But every branch sent into one robustness summary should still return the same scientific quantity, with the same:

- direction/sign convention;
- unit or scale;
- analysis unit and aggregation logic;
- scientific denominator;
- endpoint transformation;
- interpretive target.

If one branch estimates dwell difference and another estimates fixation-count difference, that is endpoint drift—not ordinary specification variation.

## What may vary without changing the endpoint?

This depends on the scientific declaration.

For example, a robustness audit might legitimately vary AOI radius while holding the endpoint definition as:

> treatment minus control proportion of eligible gaze observations assigned inside the declared AOI representation.

The **measurement/operationalisation choice** changes, but the high-level scientific quantity and contrast remain fixed.

By contrast, switching from that occupancy contrast to latency-to-first-fixation changes the scientific quantity and should normally be a separate audit or explicitly separate endpoint amendment.

## Endpoint invariance checklist

Before calling two branches comparable, verify:

- [ ] same scientific question;
- [ ] same endpoint name/meaning;
- [ ] same contrast direction;
- [ ] same unit or explicitly harmonised scale;
- [ ] same analysis unit;
- [ ] same aggregation/weighting target;
- [ ] same eligible population/denominator definition;
- [ ] same missing-input interpretation;
- [ ] same transformation;
- [ ] same scientific null/reference where direction is interpreted;
- [ ] same meaning when a branch cannot produce an endpoint;
- [ ] one scalar returned per represented specification.

The [Endpoint definition and invariance]({{ '/docs/guides/endpoint-definition/' | relative_url }}) guide explains each item.

## Non-finite endpoint values

The package runtime does this internally:

```python
estimate = float(endpoint(processed, spec))
```

`float(np.nan)` and `float(np.inf)` are legal Python values.

Therefore:

- a non-finite endpoint is not automatically rejected by `run_specs()`;
- it is not a zero/null effect;
- it should remain visible in the audit record;
- if your endpoint contract requires finite output, check that explicitly in your endpoint/wrapper before interpretation.

The optional builder guard can generate:

```python
estimate = float(estimate)
if not np.isfinite(estimate):
    raise ValueError("endpoint estimate must be finite under the declared contract")
```

Only enable that guard when it matches the declared endpoint/execution policy.

## Endpoint versus processor

Keep responsibilities distinct.

### Processor

Changes the representation according to the current specification.

Examples:

- filter by a declared QC policy;
- run a detector;
- apply a missingness rule;
- choose AOI geometry;
- downsample;
- perform another declared transformation.

### Endpoint

Consumes the processed object and returns the **common scalar scientific estimate**.

Do not hide undeclared preprocessing choices inside the endpoint merely because the callable has access to `spec`.

## Endpoint versus validity rule

`valid_if` answers:

> Is this combination scientifically admissible before execution?

The endpoint answers:

> What scalar scientific quantity does this valid processed branch produce?

Do not use endpoint exceptions to implement a scientific validity rule that could have been declared transparently before execution.

## Endpoint versus conclusion rule

An endpoint is the scientific estimate.

A conclusion/recovery rule is a separate mapping from estimates/evidence to a categorical decision.

Do not bake the desired conclusion threshold into the endpoint calculation unless that threshold is itself part of the declared scientific quantity.

## Reporting examples

### Methods

> A single endpoint was defined before specification execution as [scientific quantity], expressed in [unit], with [contrast direction], [analysis-unit/aggregation rule], and [eligible denominator]. Every valid specification returned this same scalar quantity; preprocessing and measurement choices varied only through declared specification factors.

### Results

> Endpoint estimates were compared only across branches preserving the declared endpoint contract. [N] valid represented specifications yielded [finite/non-finite/failure accounting] under the same [endpoint name] definition.

### Limitation

> The robustness audit characterises variation in the declared endpoint across the represented analytical choices. It does not establish that alternative scientific endpoints, aggregation targets, constructs, or untested transformations would yield the same conclusion.

## API links

- [`run_specs()`]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [`PipelineSpace`]({{ '/docs/reference/api-pathways/#api-pipelinespace' | relative_url }})
- [`expected_dwell()`]({{ '/docs/reference/api-pathways/#api-expected-dwell' | relative_url }})
- [Specification-space API pathway]({{ '/docs/reference/api-pathways/#path-specification-robustness' | relative_url }})
- [Machine-readable endpoint field reference]({{ '/assets/endpoint-contract-reference.json' | relative_url }})

## Continue from here

- [Endpoint definition and invariance]({{ '/docs/guides/endpoint-definition/' | relative_url }}) — methodological design, implementation, validation, and reporting.
- [Endpoint drift audit]({{ '/docs/examples/endpoint-drift-audit/' | relative_url }}) — compare acceptable specification variation with scientific endpoint changes.
- [Specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }}) — declare the analytical decision space.
- [Results Interpretation & Reporting Center]({{ '/docs/reporting-center/' | relative_url }}) — translate the completed endpoint evidence into bounded wording.
