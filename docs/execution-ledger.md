---
title: Execution Ledger & Recovery Center
description: Preserve declared validity, execution attempts, technical failures, non-finite endpoints, not-run branches, and repaired reruns as documentation-side evidence without inventing run_specs runtime statuses.
kicker: Workspace · Execution evidence
page_type: execution-ledger
permalink: /docs/execution-ledger/
search_category: Start
search_keywords: execution ledger technical failure non finite not run repair rerun run_specs valid denominator attempt history recovery provenance
---

# Execution Ledger & Recovery Center

Use this center **after the specification space and common endpoint are declared** and before failed or incomplete execution gets simplified into a results table.

<div class="callout warning">
<strong>These execution-state labels are documentation/audit vocabulary.</strong>
Core <code>run_specs()</code> returns successful result rows containing the specification plus <code>estimate</code>. If the processor or endpoint raises, the exception propagates. It does not create <code>technical_failure</code>, <code>not_run</code>, or repair-history rows for you.
</div>

The center has two purposes:

1. explain the governed execution-state vocabulary used across the documentation;
2. generate one documentation-side attempt record at a time so failure/recovery history can remain reconstructable.

## Governed execution states

<div class="execution-state-summary">
  <strong>{{ site.data.execution_states | size }} governed execution states/events</strong>
  <span>All cards remain visible without JavaScript.</span>
</div>

<form class="execution-state-controls" data-execution-state-controls role="search" aria-label="Filter execution states">
  <label>
    <span>Search states</span>
    <input
      type="search"
      autocomplete="off"
      placeholder="Try “non-finite”, “valid denominator”, or “rerun”…"
      data-execution-state-search
    >
  </label>

  <label>
    <span>Phase</span>
    <select data-execution-state-phase>
      <option value="">All phases</option>
      <option value="Pre-execution">Pre-execution</option>
      <option value="Execution">Execution</option>
      <option value="Endpoint">Endpoint</option>
      <option value="Recovery">Recovery</option>
    </select>
  </label>

  <button type="button" data-execution-state-clear>Clear filters</button>
</form>

<p
  class="execution-state-status"
  data-execution-state-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  Showing all {{ site.data.execution_states | size }} execution states/events.
</p>

<div class="execution-state-grid" data-execution-state-grid>
{% for state in site.data.execution_states %}
  {% capture execution_search %}{{ state.id }} {{ state.label }} {{ state.phase }} {{ state.kind }} {{ state.signal }} {{ state.meaning }} {{ state.record }} {{ state.next_step }} {{ state.boundary }}{% endcapture %}
  <article
    class="execution-state-card"
    id="execution-{{ state.id }}"
    data-execution-state-card
    data-execution-state-phase="{{ state.phase | escape }}"
    data-execution-state-search="{{ execution_search | downcase | escape }}"
  >
    <div class="execution-state-badges">
      <span>{{ state.phase }}</span>
      <span>{{ state.kind }}</span>
    </div>

    <p class="execution-state-signal"><code>{{ state.signal }}</code></p>
    <h2>{{ state.label }}</h2>
    <p>{{ state.meaning }}</p>

    <dl class="execution-state-meta">
      <div>
        <dt>Valid denominator</dt>
        <dd><code>{{ state.valid_denominator }}</code></dd>
      </div>
      <div>
        <dt>Attempted?</dt>
        <dd><code>{{ state.attempted }}</code></dd>
      </div>
      <div>
        <dt>Estimate state</dt>
        <dd><code>{{ state.estimate_state }}</code></dd>
      </div>
    </dl>

    <section>
      <h3>Preserve</h3>
      <p>{{ state.record }}</p>
    </section>

    <section>
      <h3>Next step</h3>
      <p>{{ state.next_step }}</p>
    </section>

    <section class="execution-state-boundary">
      <h3>Boundary</h3>
      <p>{{ state.boundary }}</p>
    </section>

    <details>
      <summary>Reporting wording</summary>
      <p data-execution-report-template>{{ state.reporting_template }}</p>
      <button type="button" data-execution-copy-report>Copy reporting wording</button>
    </details>
  </article>
{% endfor %}
</div>

<div class="execution-state-empty" data-execution-state-empty hidden>
  <h2>No execution state matches these filters</h2>
  <p>Clear the filters or use site search with <strong>Ctrl/Cmd + K</strong>.</p>
</div>

## Build one attempt record

Use this form to preserve **one branch attempt or recovery event**. It does not execute code, inspect participant data, or decide whether a branch is scientifically valid.

<form class="execution-attempt-builder" data-execution-attempt-builder>
  <div class="execution-attempt-grid">
    <label for="execution-branch-id">
      <span>Branch ID</span>
      <input id="execution-branch-id" type="text" autocomplete="off" required data-attempt-branch>
    </label>

    <label for="execution-attempt-id">
      <span>Attempt ID</span>
      <input id="execution-attempt-id" type="text" autocomplete="off" required data-attempt-id>
    </label>

    <label for="execution-validity">
      <span>Scientific validity at attempt time</span>
      <select id="execution-validity" required data-attempt-validity>
        <option value="">Choose explicitly…</option>
        <option value="valid">Valid</option>
        <option value="invalid_before_execution">Invalid before execution</option>
      </select>
    </label>

    <label for="execution-state">
      <span>Execution state / event</span>
      <select id="execution-state" required data-attempt-state>
        <option value="">Choose explicitly…</option>
        {% for state in site.data.execution_states %}
        <option value="{{ state.signal | escape }}">{{ state.label }}</option>
        {% endfor %}
      </select>
    </label>

    <label for="execution-endpoint-ref">
      <span>Endpoint declaration reference</span>
      <input id="execution-endpoint-ref" type="text" autocomplete="off" required data-attempt-endpoint>
    </label>

    <label for="execution-evidence-layer">
      <span>Temporal evidence layer</span>
      <input
        id="execution-evidence-layer"
        type="text"
        autocomplete="off"
        placeholder="e.g. submitted, post-review amendment"
        required
        data-attempt-layer
      >
    </label>

    <label class="execution-attempt-wide" for="execution-factor-values">
      <span>Factor values / branch identity</span>
      <textarea
        id="execution-factor-values"
        rows="3"
        placeholder="One factor=value per line"
        required
        data-attempt-factors
      ></textarea>
    </label>

    <label class="execution-attempt-wide" for="execution-source-ref">
      <span>Source / representation / software reference</span>
      <textarea
        id="execution-source-ref"
        rows="2"
        required
        data-attempt-source
      ></textarea>
    </label>

    <label for="execution-estimate">
      <span>Estimate, when applicable</span>
      <input
        id="execution-estimate"
        type="text"
        autocomplete="off"
        placeholder="finite number, NaN, Infinity, or blank"
        data-attempt-estimate
      >
    </label>

    <label for="execution-error-type">
      <span>Error type, when applicable</span>
      <input id="execution-error-type" type="text" autocomplete="off" data-attempt-error-type>
    </label>

    <label class="execution-attempt-wide" for="execution-error-message">
      <span>Error / not-run reason, when applicable</span>
      <textarea
        id="execution-error-message"
        rows="3"
        data-attempt-error-message
      ></textarea>
    </label>

    <label for="execution-prior-attempt">
      <span>Prior attempt ID, for repair reruns</span>
      <input id="execution-prior-attempt" type="text" autocomplete="off" data-attempt-prior>
    </label>

    <label for="execution-repair-ref">
      <span>Repair record reference</span>
      <input id="execution-repair-ref" type="text" autocomplete="off" data-attempt-repair>
    </label>

    <label for="execution-outcome-seen">
      <span>Relevant outcomes already inspected?</span>
      <select id="execution-outcome-seen" required data-attempt-outcome-seen>
        <option value="">Choose explicitly…</option>
        <option value="false">No</option>
        <option value="true">Yes</option>
      </select>
    </label>
  </div>

  <div class="execution-attempt-actions">
    <button type="submit">Generate attempt record</button>
    <button type="button" data-attempt-clear>Clear attempt</button>
  </div>
</form>

<div
  class="execution-attempt-errors"
  data-attempt-errors
  role="alert"
  tabindex="-1"
  hidden
></div>

<p
  class="execution-attempt-status"
  data-attempt-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  No attempt record generated yet.
</p>

<article class="execution-attempt-output">
  <h2>Documentation-side attempt JSON</h2>
  <p>
    This record is provenance. It is not a package runtime object and does not certify the scientific validity of the branch or repair.
  </p>
  <pre><code class="language-json" data-attempt-json>{
  "schema": "gazeaudit-execution-attempt-v1"
}</code></pre>
  <button type="button" data-attempt-copy disabled>Copy attempt JSON</button>
</article>

## Attempt-state compatibility rules

The builder enforces only a few structural consistency rules.

### Invalid before execution

Must use:

- validity = `invalid_before_execution`;
- state = `invalid_before_execution`;
- no estimate;
- no execution error.

It is a declaration/validity record, not an attempted branch.

### Successful

Must use:

- validity = `valid`;
- a finite numeric estimate.

### Technical failure

Must use:

- validity = `valid`;
- an error type or message;
- no scientific estimate.

### Non-finite endpoint

Must use:

- validity = `valid`;
- estimate text equal to `NaN`, `Infinity`, or `-Infinity`.

### Not run

Requires:

- an explicit reason;
- no estimate.

If the branch was scientifically valid, it remains unresolved in the valid denominator.

### Successful repair rerun

Requires:

- validity = `valid`;
- a finite estimate;
- prior attempt ID;
- repair record reference.

The earlier failure remains in history.

## Current state and historical events are different

A branch can have more than one attempt.

Example:

```text
S06 / attempt-01 / technical_failure
S06 / attempt-02 / repair_rerun_success
```

The current scientific result may use the successful rerun, while the provenance record still preserves the initial failure.

Do not overwrite attempt 1 with attempt 2.

## Reconciliation rule

For a declared space:

```text
declared = invalid-before-execution + valid
```

For the current execution state of valid branches:

```text
valid = successful + unresolved technical failure + unresolved non-finite + valid not-run
```

Historical repair events can add extra **attempt rows** without increasing the number of scientific branches.

That distinction prevents an attempt ledger from being mistaken for a specification denominator.

## Reporting examples

### Methods

> Every declared branch was assigned a stable branch identity. Pre-execution scientific validity was recorded separately from execution attempts. Valid technical failures, non-finite endpoints, and not-run branches remained in the valid denominator. Technical repairs created new attempt records linked to the original failed attempt rather than overwriting history.

### Results

> [S] of [V] valid specifications currently yielded accepted finite endpoints; [F] remained technical failures, [N] remained non-finite, and [R] were not run. [K] repaired branches had historical failure events retained in the attempt ledger.

### Limitation

> The execution ledger establishes branch and attempt accountability. It does not determine whether the declared factor space, endpoint, validity rule, repair, or scientific interpretation is substantively correct.

## API links

- [`run_specs()`]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [`PipelineSpace`]({{ '/docs/reference/api-pathways/#api-pipelinespace' | relative_url }})
- [Specification Space Declaration Center]({{ '/docs/specification-declaration/' | relative_url }})
- [Endpoint Definition & Handoff Center]({{ '/docs/endpoint-contract/' | relative_url }})
- [Evidence and denominator vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }})
- [Machine-readable execution-state reference]({{ '/assets/execution-state-reference.json' | relative_url }})

## Continue from here

- [Execution ledger and recovery]({{ '/docs/guides/execution-ledger-recovery/' | relative_url }}) — design, lineage, reconciliation, repair, and reporting guidance.
- [Failure → repair → reconciliation]({{ '/docs/examples/execution-ledger-reconciliation/' | relative_url }}) — a fully synthetic multi-attempt ledger with one invalid branch, one non-finite endpoint, one technical failure, and one repaired rerun.
- [Failed-audit recovery]({{ '/docs/examples/failed-audit-recovery/' | relative_url }}) — detailed causal repair workflow.
- [Results Interpretation & Reporting Center]({{ '/docs/reporting-center/' | relative_url }}) — convert reconciled evidence into bounded claims.
