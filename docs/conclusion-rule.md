---
title: Conclusion Rule Design Center
description: Declare and document a GazeAudit conclusion-recovery rule with an independently defined reference effect, explicit tolerances, sign policy, minimum recovery fraction, timing, interpretation boundaries, reporting language, and governed API routes.
kicker: Workspace · Conclusion rule
page_type: conclusion-rule
permalink: /docs/conclusion-rule/
search_category: Start
search_keywords: conclusion rule recovery robust fragile reference effect tolerance sign minimum recovery fraction known truth publication audit
---

# Conclusion Rule Design Center

Use this center only when a categorical recovery decision is scientifically justified.

<div class="callout warning">
<strong>This builder does not choose a reference effect or threshold for you.</strong>
A conclusion rule is a researcher-owned scientific decision. The reference effect and tolerances must be justified independently of the robustness estimates being judged. The UI therefore supplies no scientific defaults and requires explicit choices even where the Python dataclass itself has defaults.
</div>

A conclusion rule is most straightforward when:

- the data-generating effect is known in a simulation or benchmark;
- an independently justified external/reference effect exists;
- the decision criterion was fixed before robustness-result inspection.

For ordinary real-data analyses without an independently justified reference effect, descriptive robustness reporting is usually the safer route.

<form class="conclusion-rule-builder" data-conclusion-builder>
  <div class="conclusion-rule-grid">
  {% for field in site.data.conclusion_rule_fields %}
    <label
      class="conclusion-rule-field"
      for="conclusion-{{ field.name }}"
      data-conclusion-field
      data-conclusion-name="{{ field.name }}"
      data-conclusion-required="{{ field.required }}"
    >
      <span class="conclusion-rule-head">
        <span>
          <code>{{ field.name }}</code>
          <strong>{{ field.label }}</strong>
        </span>
        {% if field.required %}
          <span class="conclusion-required">Required</span>
        {% else %}
          <span class="conclusion-optional">Optional</span>
        {% endif %}
      </span>

      <span class="conclusion-purpose">{{ field.purpose }}</span>

      {% if field.name == 'reference_type' %}
      <select id="conclusion-reference_type" data-conclusion-value required>
        <option value="">Choose explicitly…</option>
        <option value="known_truth">Known truth / simulation</option>
        <option value="independent_reference">Independently justified real-data reference</option>
      </select>
      {% elsif field.name == 'require_sign' %}
      <select id="conclusion-require_sign" data-conclusion-value required>
        <option value="">Choose explicitly…</option>
        <option value="true">Yes — same sign required</option>
        <option value="false">No — tolerance only</option>
      </select>
      {% elsif field.value_type == 'textarea' %}
      <textarea
        id="conclusion-{{ field.name }}"
        rows="3"
        {% if field.required %}required{% endif %}
        data-conclusion-value
      ></textarea>
      {% elsif field.value_type == 'number' %}
      <input
        id="conclusion-{{ field.name }}"
        type="number"
        step="any"
        inputmode="decimal"
        {% if field.required %}required{% endif %}
        data-conclusion-value
      >
      {% else %}
      <input
        id="conclusion-{{ field.name }}"
        type="text"
        autocomplete="off"
        {% if field.required %}required{% endif %}
        data-conclusion-value
      >
      {% endif %}

      <span class="conclusion-boundary">
        <strong>Boundary</strong>
        {{ field.boundary }}
      </span>
    </label>
  {% endfor %}
  </div>

  <div class="conclusion-rule-actions">
    <button type="submit">Generate conclusion rule</button>
    <button type="button" data-conclusion-clear>Clear declaration</button>
  </div>
</form>

<div
  class="conclusion-errors"
  data-conclusion-errors
  role="alert"
  tabindex="-1"
  hidden
></div>

<p
  class="conclusion-status"
  data-conclusion-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  No conclusion rule generated yet.
</p>

<div class="conclusion-output-grid">
  <article>
    <h2>Documentation-side declaration</h2>
    <p>
      This JSON preserves the scientific rule and timing. It is not a runtime object and does not validate the reference or thresholds.
    </p>
    <pre><code class="language-json" data-conclusion-json>{
  "schema": "gazeaudit-conclusion-rule-declaration-v1"
}</code></pre>
    <button type="button" data-conclusion-copy="json" disabled>Copy JSON</button>
  </article>

  <article>
    <h2>Python rule skeleton</h2>
    <p>
      The generated call supplies every scientific argument explicitly; it never relies on the dataclass's default sign or recovery-fraction values.
    </p>
    <pre><code class="language-python" data-conclusion-python># Complete the conclusion rule declaration first.</code></pre>
    <button type="button" data-conclusion-copy="python" disabled>Copy Python</button>
  </article>
</div>

## What the runtime requires

`ConclusionRule` requires at least one of:

- `relative_tolerance`;
- `absolute_tolerance`.

If both are supplied, **both must be satisfied** for tolerance recovery.

The tolerances must be finite and non-negative.

`minimum_recovery_fraction` must be in `[0, 1]`.

## Zero reference effects need special handling

When the reference effect is exactly zero:

- relative error is undefined;
- effect ratio is undefined;
- sign recovery is treated as recovered;
- a relative tolerance cannot be evaluated;
- use an absolute tolerance instead.

Do not work around this by adding an arbitrary epsilon to the reference value.

## Sign recovery is a separate criterion

For a non-zero reference effect and `require_sign=True`:

- the branch must satisfy the declared tolerance;
- the branch must also have the same sign as the reference.

With `require_sign=False`, only the tolerance rule governs branch recovery.

This is a scientific rule choice, not a significance test.

## Minimum recovery fraction applies to the supplied represented set

`summarize_conclusion_recovery()` computes the fraction of represented rows with `conclusion_recovered=True`.

It classifies the supplied set:

- `robust` when recovery fraction is at or above the declared minimum;
- `fragile` when below it.

That classification is conditional on:

- the supplied specification table;
- the reference effect;
- the tolerance rule;
- the sign rule;
- the declared minimum recovery fraction.

It is not a universal property of the dataset.

## Avoid circular references

Bad pattern:

> We used the median robustness estimate as the reference effect, then evaluated whether the robustness estimates recovered that reference.

The same evidence is defining and validating the target.

Better sources include:

- known simulation truth;
- independently generated calibration/benchmark truth;
- a preregistered external reference;
- another independently justified target whose provenance predates the recovery analysis.

## Conclusion rules are not p-value rules

`ConclusionRule` deliberately evaluates effect recovery using:

- absolute error;
- relative error;
- sign recovery;
- across-specification recovery fraction.

It does not use:

- p-values;
- confidence-interval crossing;
- specification selection;
- posterior probability.

Do not translate `robust` into “statistically significant” or `fragile` into “not significant”.

## Reporting example

### Methods

> Before robustness-result inspection, we defined the recovery target as [reference effect and provenance]. A specification-level endpoint was considered recovered when [absolute/relative tolerance rule] and [sign rule] were satisfied. The overall conclusion rule required at least [fraction] of represented specifications to recover the target. The reference and thresholds were fixed [timing].

### Results

> [R] of [N] represented specifications satisfied the predeclared recovery rule (recovery fraction = [x]). This [met/did not meet] the declared minimum recovery fraction of [threshold], yielding the rule-based classification [robust/fragile] for the supplied specification set.

### Limitation

> The classification is conditional on the independently defined reference effect, tolerance rule, sign criterion, represented specification space, and execution completeness. It does not establish statistical significance, external validity, or robustness to unrepresented analytical choices.

## API links

- [`ConclusionRule`]({{ '/docs/reference/api-pathways/#api-conclusionrule' | relative_url }})
- [`summarize_conclusion_recovery()`]({{ '/docs/reference/api-pathways/#api-summarize-conclusion-recovery' | relative_url }})
- [`build_conclusion_audit_bundle()`]({{ '/docs/reference/api-pathways/#api-build-conclusion-audit-bundle' | relative_url }})
- [`verify_publication_audit_bundle()`]({{ '/docs/reference/api-pathways/#api-verify-publication-audit-bundle' | relative_url }})
- [Machine-readable rule-field reference]({{ '/assets/conclusion-rule-reference.json' | relative_url }})

`conclusion_recovery_table()` is used in the package workflow, but this page does not invent a stable API deep link for a symbol absent from the governed source-level inventory.

## Continue from here

- [Design conclusion-recovery rules]({{ '/docs/guides/conclusion-rule-design/' | relative_url }}) — scientific rationale, zero-reference behavior, dual tolerance, timing, reporting, and misuse prevention.
- [Conclusion-rule edge cases]({{ '/docs/examples/conclusion-rule-edge-cases/' | relative_url }}) — deterministic synthetic recovery cases.
- [Publication audit guide]({{ '/docs/guides/publication-audits/' | relative_url }}) — bind the final rule and evidence into deterministic publication artifacts.
- [Robustness Diagnostics Center]({{ '/docs/robustness-diagnostics/' | relative_url }}) — use descriptive reporting when a categorical reference-based rule is not justified.
