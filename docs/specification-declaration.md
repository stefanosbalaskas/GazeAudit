---
title: Specification Space Declaration Center
description: Declare GazeAudit analytical decision factors, typed levels, scientific rationale, timing, endpoint identity, validity-rule mode, failure policy, and interpretation boundary before executing a PipelineSpace.
kicker: Workspace · Robustness declaration
page_type: specification-declaration
permalink: /docs/specification-declaration/
search_category: Start
search_keywords: specification space declaration multiverse PipelineSpace factors levels valid_if declared valid successful denominator endpoint rationale timing
---

# Specification Space Declaration Center

Use this center **after the endpoint is declared and before specification estimates are visible**.

<div class="callout warning">
<strong>This builder records a decision space; it does not decide which alternatives are scientifically defensible.</strong>
Factors, levels, invalid combinations, and timing remain researcher-owned. The browser computes only the Cartesian <em>declared</em> count. It never invents a valid-specification count or a scientific validity predicate.
</div>

Before using this page, define the common endpoint in the [Endpoint Definition & Handoff Center]({{ '/docs/endpoint-contract/' | relative_url }}).

<form class="spec-declaration-builder" data-spec-builder>
  <section class="spec-declaration-section" aria-labelledby="spec-declaration-context">
    <h2 id="spec-declaration-context">Declaration context</h2>

    <div class="spec-declaration-field-grid">
    {% for field in site.data.specification_declaration_fields %}
      {% if field.name != 'validity_mode' %}
      <label
        class="spec-declaration-field"
        for="spec-{{ field.name }}"
        data-spec-global-field
        data-spec-name="{{ field.name }}"
        data-spec-required="{{ field.required }}"
      >
        <span class="spec-declaration-field-head">
          <span>
            <code>{{ field.name }}</code>
            <strong>{{ field.label }}</strong>
          </span>
          {% if field.required %}
            <span class="spec-required">Required</span>
          {% else %}
            <span class="spec-optional">Optional</span>
          {% endif %}
        </span>

        <span class="spec-field-purpose">{{ field.purpose }}</span>

        {% if field.value_type == 'textarea' %}
        <textarea
          id="spec-{{ field.name }}"
          rows="3"
          {% if field.required %}required{% endif %}
          data-spec-global-value
        ></textarea>
        {% else %}
        <input
          id="spec-{{ field.name }}"
          type="text"
          autocomplete="off"
          {% if field.required %}required{% endif %}
          data-spec-global-value
        >
        {% endif %}

        <span class="spec-field-boundary">
          <strong>Boundary</strong>
          {{ field.boundary }}
        </span>
      </label>
      {% endif %}
    {% endfor %}
    </div>
  </section>

  <section class="spec-declaration-section" aria-labelledby="spec-factor-heading">
    <div class="spec-section-head">
      <div>
        <h2 id="spec-factor-heading">Declared factors</h2>
        <p>Each factor needs a unique name, an explicit value type, at least one level, and a study-specific rationale.</p>
      </div>
      <button type="button" data-spec-add-factor>Add factor</button>
    </div>

    <div class="spec-factor-list" data-spec-factor-list>
      <fieldset class="spec-factor-card" data-spec-factor>
        <legend>Factor 1</legend>

        <div class="spec-factor-grid">
          <label for="spec-factor-name-1">
            <span>Factor name</span>
            <input
              id="spec-factor-name-1"
              type="text"
              autocomplete="off"
              required
              data-spec-factor-name
            >
          </label>

          <label for="spec-factor-type-1">
            <span>Level type</span>
            <select id="spec-factor-type-1" data-spec-factor-type>
              <option value="string">Text</option>
              <option value="number">Number</option>
              <option value="boolean">Boolean</option>
            </select>
          </label>

          <label class="spec-factor-wide" for="spec-factor-levels-1">
            <span>Levels — one per line</span>
            <textarea
              id="spec-factor-levels-1"
              rows="4"
              required
              data-spec-factor-levels
            ></textarea>
          </label>

          <label class="spec-factor-wide" for="spec-factor-rationale-1">
            <span>Scientific rationale</span>
            <textarea
              id="spec-factor-rationale-1"
              rows="3"
              required
              data-spec-factor-rationale
            ></textarea>
          </label>
        </div>

        <button
          type="button"
          class="spec-remove-factor"
          data-spec-remove-factor
          disabled
        >
          Remove factor
        </button>
      </fieldset>
    </div>

    <template data-spec-factor-template>
      <fieldset class="spec-factor-card" data-spec-factor>
        <legend>Factor __INDEX__</legend>

        <div class="spec-factor-grid">
          <label for="spec-factor-name-__INDEX__">
            <span>Factor name</span>
            <input
              id="spec-factor-name-__INDEX__"
              type="text"
              autocomplete="off"
              required
              data-spec-factor-name
            >
          </label>

          <label for="spec-factor-type-__INDEX__">
            <span>Level type</span>
            <select id="spec-factor-type-__INDEX__" data-spec-factor-type>
              <option value="string">Text</option>
              <option value="number">Number</option>
              <option value="boolean">Boolean</option>
            </select>
          </label>

          <label class="spec-factor-wide" for="spec-factor-levels-__INDEX__">
            <span>Levels — one per line</span>
            <textarea
              id="spec-factor-levels-__INDEX__"
              rows="4"
              required
              data-spec-factor-levels
            ></textarea>
          </label>

          <label class="spec-factor-wide" for="spec-factor-rationale-__INDEX__">
            <span>Scientific rationale</span>
            <textarea
              id="spec-factor-rationale-__INDEX__"
              rows="3"
              required
              data-spec-factor-rationale
            ></textarea>
          </label>
        </div>

        <button
          type="button"
          class="spec-remove-factor"
          data-spec-remove-factor
        >
          Remove factor
        </button>
      </fieldset>
    </template>
  </section>

  <section class="spec-declaration-section" aria-labelledby="spec-validity-heading">
    <h2 id="spec-validity-heading">Pre-execution validity</h2>

    <label class="spec-validity-mode" for="spec-validity-mode">
      <span>Validity-rule mode</span>
      <select id="spec-validity-mode" required data-spec-validity-mode>
        <option value="all_valid">All Cartesian combinations are scientifically admissible</option>
        <option value="predicate_required">Some combinations are invalid before execution</option>
      </select>
    </label>

    <p class="spec-validity-note">
      If some combinations are invalid, describe the rule in the declaration-context field above. The generated Python will contain a <code>NotImplementedError</code> validity stub rather than guessing the predicate.
    </p>
  </section>

  <div class="spec-declaration-actions">
    <button type="submit">Generate specification declaration</button>
    <button type="button" data-spec-clear>Clear declaration</button>
  </div>
</form>

<div
  class="spec-builder-errors"
  data-spec-errors
  role="alert"
  tabindex="-1"
  hidden
></div>

<p
  class="spec-builder-status"
  data-spec-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  No specification declaration generated yet.
</p>

<div class="spec-output-grid">
  <article>
    <h2>Declaration record</h2>
    <p>
      This JSON is documentation-side provenance. It records the declared factor space and timing; it does not certify that the factors or levels are scientifically defensible.
    </p>
    <pre><code class="language-json" data-spec-json>{
  "schema": "gazeaudit-specification-declaration-v1"
}</code></pre>
    <button type="button" data-spec-copy="json" disabled>Copy JSON</button>
  </article>

  <article>
    <h2>PipelineSpace skeleton</h2>
    <p>
      Factor levels are emitted exactly as declared. When a pre-execution validity predicate is required, the generated function intentionally remains unimplemented.
    </p>
    <pre><code class="language-python" data-spec-python># Complete the specification declaration first.</code></pre>
    <button type="button" data-spec-copy="python" disabled>Copy Python</button>
  </article>
</div>

## Declared, valid, and successful are different denominators

### Declared

The Cartesian product represented by `PipelineSpace.size`.

For factors with 2 × 2 × 3 levels:

```text
declared combinations = 12
```

The browser can calculate this from your factor declaration.

### Valid

The subset that survives a scientific `valid_if` rule fixed before execution.

If validity exclusions exist, this center deliberately reports the valid count as **unknown until the predicate is actually implemented and enumerated**.

### Successful

Valid branches that complete the processor/endpoint execution contract.

Technical failures remain part of the valid denominator even though they do not yield a normal endpoint row.

Do not rewrite:

```text
6 successful / 7 valid
```

as:

```text
6 / 6
```

## What belongs in a factor?

A factor should represent a scientifically defensible analytical or measurement decision whose consequences you intend to audit.

Examples can include:

- detector family;
- declared detector parameter;
- QC/readiness policy;
- missingness handling rule;
- AOI representation;
- spatial-error model;
- sample-retention or sampling representation;
- another preprocessing decision.

A factor should not be included merely because the software can vary it.

## What belongs in a level?

Every level should have a rationale independent of the observed endpoint.

Good evidence sources can include:

- protocol;
- preregistration;
- device or method validation;
- established analysis alternatives;
- reviewer-requested sensitivity, labelled with its timing;
- deliberately bounded sensitivity values.

Do not populate a dense grid simply to search for a favourable estimate.

## Unique factor names matter

`PipelineSpace.add_choice(name, values)` stores factor choices by name.

This builder requires unique names so a later factor cannot silently replace the declaration of an earlier factor in the generated skeleton.

Use names that remain meaningful in exported tables and manuscript provenance.

## Validity rules belong before execution

Use `valid_if` for combinations known to be scientifically inadmissible **before** the endpoint is evaluated.

Examples:

- one detector parameter exists only for a particular detector family;
- a preprocessing mode is incompatible with a declared representation;
- a model choice requires an input that another declared branch does not produce by design.

Do not use `valid_if` to discard branches because:

- the estimate is surprising;
- the sign is inconvenient;
- the p-value is unattractive;
- execution failed technically;
- the endpoint was non-finite.

Those are different evidence states.

## Reference specification is optional

A study may define one reference pipeline for orientation, comparison, or legacy continuity.

A reference branch is not automatically:

- the truth;
- the scientifically best branch;
- the branch that should receive more interpretive weight.

Robustness summaries should still account for the complete valid represented space.

## Failure policy must be declared separately

Before execution, decide how to preserve:

- processor exceptions;
- endpoint exceptions;
- missing required endpoint inputs;
- non-finite endpoints;
- branches that were never run.

GazeAudit core `run_specs()` propagates exceptions. If your project uses an audited wrapper/ledger to continue other branches, retain the original failure event and the valid denominator.

## Timing must remain visible

Classify the declaration honestly:

- preregistered;
- fixed before outcome inspection;
- post hoc sensitivity;
- reviewer-requested amendment;
- correction.

A later factor or level can be scientifically useful while still being temporally distinct from the submitted decision space.

## Reporting examples

### Methods

> We declared a specification space before endpoint inspection comprising [factor names] with [levels and rationale]. The Cartesian space contained [N] combinations. [All combinations were admissible / a pre-execution validity rule excluded X combinations for stated scientific reasons], yielding [V] valid specifications. Every valid branch targeted the same endpoint declaration, [endpoint reference].

### Results

> [S] of [V] valid specifications successfully produced the declared endpoint. [Technical failure / non-finite / not-run accounting] remained visible in the valid denominator. Estimates were summarised across the represented valid branches without selecting a preferred pipeline after outcome inspection.

### Limitation

> The audit covers only the declared factors and levels. Stability within this space does not establish robustness to analytical, measurement, endpoint, or population choices that were not represented.

## API links

- [`PipelineSpace`]({{ '/docs/reference/api-pathways/#api-pipelinespace' | relative_url }})
- [`run_specs()`]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [`specification_curve()`]({{ '/docs/reference/api-pathways/#api-specification-curve' | relative_url }})
- [`effect_stability()`]({{ '/docs/reference/api-pathways/#api-effect-stability' | relative_url }})
- [Specification-space pathway]({{ '/docs/reference/api-pathways/#path-specification-robustness' | relative_url }})
- [Machine-readable declaration-field reference]({{ '/assets/specification-declaration-reference.json' | relative_url }})

## Continue from here

- [Specification-space declaration and validity]({{ '/docs/guides/specification-declaration/' | relative_url }}) — methodological design, denominator governance, timing, and failure accounting.
- [Declared → valid → successful]({{ '/docs/examples/specification-denominator-audit/' | relative_url }}) — fully synthetic denominator exercise.
- [Endpoint Definition & Handoff Center]({{ '/docs/endpoint-contract/' | relative_url }}) — define the scalar quantity shared across branches.
- [Specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }}) — execute and interpret the declared space.
- [Results Interpretation & Reporting Center]({{ '/docs/reporting-center/' | relative_url }}) — translate completed evidence into bounded claims.
