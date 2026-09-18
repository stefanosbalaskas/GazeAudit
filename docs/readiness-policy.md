---
title: Readiness Policy Design Center
description: Build a researcher-declared GazeAudit ReadinessThresholds policy without hidden defaults, inspect the scope and interpretation of every rule, and generate auditable Python plus a descriptive JSON draft before filtering any data.
kicker: Workspace · Readiness governance
page_type: readiness-policy
permalink: /docs/readiness-policy/
search_category: Start
search_keywords: readiness policy builder thresholds cohort impact ReadinessThresholds evaluate_analysis_readiness trial participant governance filter preview active rules
---

# Readiness Policy Design Center

Use this center **after structural QC has been inspected** and before a readiness rule is allowed to change the analysis cohort.

<div class="callout warning">
<strong>No scientific threshold is pre-filled.</strong>
Every readiness criterion starts inactive. Enter values only when your acquisition protocol, preregistration, task requirements, device/analysis evidence, or a declared sensitivity design justifies them. GazeAudit does not supply a universal “good data” cutoff.
</div>

The builder is local to this documentation page. It does not upload a dataset, inspect your outcomes, infer thresholds, or filter a `GazeStudy`.

<form class="readiness-builder" data-readiness-builder>
  <div class="readiness-builder-head">
    <label for="readiness-policy-name">
      <span>Policy name <strong>(required)</strong></span>
      <input
        id="readiness-policy-name"
        name="policy_name"
        type="text"
        required
        autocomplete="off"
        placeholder="e.g. preregistered_primary"
        aria-describedby="readiness-policy-name-help"
        data-readiness-policy-name
      >
    </label>
    <p id="readiness-policy-name-help">
      Use a stable project-owned label. The name identifies the policy; it does not establish scientific validity.
    </p>
  </div>

  <fieldset class="readiness-rule-set">
    <legend>Choose only criteria that belong to the declared policy</legend>
    <p class="readiness-rule-set-note">
      Activating a criterion makes its value required. Leaving a criterion inactive maps it to `None` in `ReadinessThresholds`.
    </p>

    <div class="readiness-rule-grid">
    {% for rule in site.data.readiness_thresholds %}
      <article
        class="readiness-rule-card"
        data-readiness-rule
        data-rule-name="{{ rule.name }}"
        data-rule-type="{{ rule.value_type }}"
        data-rule-scope="{{ rule.scope }}"
      >
        <div class="readiness-rule-title">
          <div>
            <code>{{ rule.name }}</code>
            <h2>{{ rule.label }}</h2>
          </div>
          <span>{{ rule.scope }}</span>
        </div>

        <p>{{ rule.description }}</p>

        <dl class="readiness-rule-contract">
          <div>
            <dt>Runtime comparison</dt>
            <dd><code>{{ rule.metric }}</code> {{ rule.comparator }} declared value</dd>
          </div>
          <div>
            <dt>Interpretation</dt>
            <dd>{{ rule.interpretation }}</dd>
          </div>
        </dl>

        <div class="readiness-rule-control">
          <label for="readiness-active-{{ rule.name }}">
            <input
              id="readiness-active-{{ rule.name }}"
              type="checkbox"
              data-readiness-active
            >
            <span>Include this criterion</span>
          </label>

          {% if rule.value_type == 'fraction' %}
          <label for="readiness-value-{{ rule.name }}">
            <span>Declared fraction (0–1)</span>
            <input
              id="readiness-value-{{ rule.name }}"
              type="number"
              min="0"
              max="1"
              step="{{ rule.input_step }}"
              inputmode="decimal"
              disabled
              data-readiness-value
            >
          </label>
          {% elsif rule.value_type == 'integer' %}
          <label for="readiness-value-{{ rule.name }}">
            <span>Declared minimum</span>
            <input
              id="readiness-value-{{ rule.name }}"
              type="number"
              min="1"
              step="{{ rule.input_step }}"
              inputmode="numeric"
              disabled
              data-readiness-value
            >
          </label>
          {% else %}
          <p class="readiness-boolean-note">
            When included, this builder emits <code>{{ rule.name }}=True</code>. The unchecked state means the criterion is not assessed.
          </p>
          {% endif %}
        </div>

        <div class="readiness-rule-boundary">
          <strong>Boundary</strong>
          <p>{{ rule.boundary }}</p>
        </div>
      </article>
    {% endfor %}
    </div>
  </fieldset>

  <div class="readiness-builder-actions">
    <button type="submit">Generate policy draft</button>
    <button type="button" data-readiness-clear>Clear policy</button>
  </div>
</form>

<div class="readiness-builder-errors" data-readiness-errors role="alert" hidden></div>

<p class="readiness-builder-status" data-readiness-status role="status" aria-live="polite" aria-atomic="true">
  No policy draft generated yet.
</p>

<section class="readiness-output-grid" aria-label="Generated readiness policy outputs">
  <article>
    <h2>Python policy + preview</h2>
    <p>
      The generated code evaluates and previews only. It deliberately does not call <code>filter_study_by_readiness()</code>.
    </p>
    <pre><code class="language-python" data-readiness-python># Choose a policy name and activate at least one justified criterion.</code></pre>
    <button type="button" data-readiness-copy="python" disabled>Copy Python</button>
  </article>

  <article>
    <h2>Descriptive JSON draft</h2>
    <p>
      This documentation-side draft mirrors the declared threshold values. It is not a runtime readiness manifest and is not proof that the thresholds are scientifically justified.
    </p>
    <pre><code class="language-json" data-readiness-json>{
  "schema": "gazeaudit-readiness-policy-draft-v1",
  "policy_name": "",
  "thresholds": {}
}</code></pre>
    <button type="button" data-readiness-copy="json" disabled>Copy JSON</button>
  </article>
</section>

## What the generated code does

The output follows this sequence:

```python
from gazeaudit import (
    ReadinessThresholds,
    cohort_impact_preview,
    evaluate_analysis_readiness,
)

policy = ReadinessThresholds(
    # only your active, declared criteria appear here
)

readiness = evaluate_analysis_readiness(
    study,
    policy,
    policy_name="your_policy_name",
)

print(readiness.status)
print(cohort_impact_preview(readiness))
```

This produces a **policy-relative assessment and no-mutation cohort preview**.

It does not remove rows, trials, or participants.

## Understand the eight criteria before declaring them

<div class="table-wrap">
<table>
  <thead>
    <tr>
      <th>Criterion</th>
      <th>Scope</th>
      <th>Observed metric</th>
      <th>Runtime rule</th>
      <th>Scientific boundary</th>
    </tr>
  </thead>
  <tbody>
  {% for rule in site.data.readiness_thresholds %}
    <tr>
      <td><code>{{ rule.name }}</code></td>
      <td>{{ rule.scope }}</td>
      <td><code>{{ rule.metric }}</code></td>
      <td>{{ rule.interpretation }}</td>
      <td>{{ rule.boundary }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>
</div>

### Scope matters

Trial-level evaluation can fail:

- coordinate, timestamp, identifier, or duplicate-timestamp fractions;
- `min_rows_per_trial`;
- `require_monotonic_time=True`.

Participant-level evaluation can fail:

- the four aggregate issue fractions;
- `max_flagged_trial_fraction`;
- `min_trials_per_participant`;
- `require_monotonic_time=True` when any trial unit has decreasing time.

`max_flagged_trial_fraction` is **downstream of the active trial policy**. Changing the trial rules can therefore change the participant-level flagged-trial fraction even when the source table is unchanged.

## Read readiness status conservatively

| Status | Meaning | Do not interpret it as |
|---|---|---|
| `unassessed` | no active readiness rule participated in the policy | “all data passed” |
| `ready_under_policy` | all evaluated trial and participant units satisfy the declared active rules | universal data validity |
| `review_under_policy` | at least one evaluated unit fails one or more declared active rules | automatic exclusion |

The status is always relative to the declared policy.

## Preview before applying

Inspect:

```python
readiness.trial_summary
readiness.participant_summary
readiness.cohort_impact
```

The cohort preview preserves three denominators:

- rows;
- participant × trial units;
- participant units.

Do not report only a retained percentage without stating which denominator and filter scope produced it.

Only after the policy and its cohort consequence have been justified should filtering be considered:

```python
from gazeaudit import filter_study_by_readiness

analysis_study = filter_study_by_readiness(
    study,
    readiness,
    scope="trial",  # or "participant"; this is a separate scientific decision
)
```

The scope above is intentionally not selected by this builder.

## Methodological guidance

Before activating a threshold, record:

1. **criterion** — which runtime rule is being used;
2. **rationale source** — preregistration, protocol, device evidence, task demand, prior validation, or sensitivity plan;
3. **timing** — whether the value was fixed before observing outcome results;
4. **scope** — trial or participant consequence;
5. **cohort impact** — rows/trials/participants retained under the policy;
6. **alternative policies** — whether nearby defensible policies materially alter the cohort or endpoint;
7. **deviation** — whether the final policy differs from the originally declared rule.

The [Design and audit readiness policies]({{ '/docs/guides/readiness-policy-design/' | relative_url }}) guide develops each step.

## Reporting examples

### Methods

> Analysis readiness was evaluated using a predeclared structural policy comprising [criteria and values]. GazeAudit first generated trial- and participant-level summaries and a no-mutation cohort-impact preview. Filtering was applied only after the declared policy and filter scope were fixed; omitted readiness criteria were not evaluated.

### Results

> Under the declared [policy name] policy, readiness status was [status]. Trial-level application retained [rows/trials/participants and denominators], whereas participant-level preview retained [corresponding denominators]. The analysis used the predeclared [trial/participant] scope.

### Limitation

> Readiness status is policy-relative and reflects the declared structural criteria only. It does not establish calibration accuracy, event-detector validity, AOI validity, missingness ignorability, or inferential robustness.

Replace every bracketed field with the actual project record.

## API links

- [`ReadinessThresholds`]({{ '/docs/reference/api-pathways/#api-readinessthresholds' | relative_url }})
- [`evaluate_analysis_readiness()`]({{ '/docs/reference/api-pathways/#api-evaluate-analysis-readiness' | relative_url }})
- [`cohort_impact_preview()`]({{ '/docs/reference/api-pathways/#api-cohort-impact-preview' | relative_url }})
- [`readiness_policy_table()`]({{ '/docs/reference/api-pathways/#api-readiness-policy-table' | relative_url }})
- [Analysis-readiness method pathway]({{ '/docs/reference/api-pathways/#path-readiness-governance' | relative_url }})
- [Machine-readable threshold reference]({{ '/assets/readiness-threshold-reference.json' | relative_url }})

## Continue from here

- [Design and audit readiness policies]({{ '/docs/guides/readiness-policy-design/' | relative_url }}) — methodological rationale, timing, sensitivity, denominator governance, and reporting.
- [Readiness policy design worked example]({{ '/docs/examples/readiness-policy-design/' | relative_url }}) — fully synthetic primary/alternative policy exercise.
- [Analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}) — runtime workflow, repair comparison, artifact export, and specification-space integration.
- [Structural-QC triage]({{ '/docs/guides/structural-qc-triage/' | relative_url }}) — understand the structural evidence before turning it into a policy.
