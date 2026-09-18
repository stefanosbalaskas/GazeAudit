---
title: Results Interpretation & Reporting Center
description: Match GazeAudit structural, readiness, robustness, sensitivity, and frozen-evidence outputs to bounded claims, denominator requirements, limitations, reporting language, and governed API/documentation routes.
kicker: Workspace · Interpretation & reporting
page_type: reporting-center
permalink: /docs/reporting-center/
search_category: Start
search_keywords: reporting interpretation claims limitations methods results wording robustness readiness structural qc sensitivity frozen evidence denominator overclaim
---

# Results Interpretation & Reporting Center

Use this center **after you have the evidence object or audit pattern in hand** and before converting it into manuscript wording.

<div class="callout warning">
<strong>This center constrains claims; it does not make the scientific judgement for you.</strong>
Runtime statuses, interpretation patterns, and frozen validation labels are deliberately kept separate. A card can show what a given evidence state licenses you to report, but it cannot decide whether a threshold, endpoint, specification, magnitude, or scientific null was appropriate for your study.
</div>

The contracts below are generated from one governed catalog. Each card identifies:

- the evidence layer;
- whether the signal is a runtime status, interpretation pattern, or protocol-bound label;
- the denominator that must remain visible;
- what the evidence can support;
- what it cannot support;
- bounded Methods, Results, and limitation wording;
- the guide/example/API route that provides the surrounding context.

<div class="reporting-center-summary">
  <strong>{{ site.data.reporting_contracts | size }} governed reporting contracts</strong>
  <span>All remain visible when JavaScript is unavailable.</span>
</div>

<form class="reporting-center-controls" data-reporting-controls role="search" aria-label="Filter reporting contracts">
  <label>
    <span>Search reporting contracts</span>
    <input
      type="search"
      autocomplete="off"
      placeholder="Try “review_under_policy”, “technical failure”, or “confidence interval”…"
      data-reporting-search
    >
  </label>

  <label>
    <span>Evidence layer</span>
    <select data-reporting-layer>
      <option value="">All layers</option>
      <option value="Structural QC">Structural QC</option>
      <option value="Readiness">Readiness</option>
      <option value="Robustness">Robustness</option>
      <option value="Sensitivity">Sensitivity</option>
      <option value="Frozen evidence">Frozen evidence</option>
    </select>
  </label>

  <label>
    <span>Contract type</span>
    <select data-reporting-kind>
      <option value="">All contract types</option>
      <option value="Runtime status">Runtime status</option>
      <option value="Interpretation pattern">Interpretation pattern</option>
      <option value="Protocol-bound evidence label">Protocol-bound evidence label</option>
    </select>
  </label>

  <button type="button" data-reporting-clear>Clear filters</button>
</form>

<p
  class="reporting-center-status"
  data-reporting-status
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  Showing all {{ site.data.reporting_contracts | size }} reporting contracts.
</p>

<div class="reporting-contract-grid" data-reporting-contracts>
{% for contract in site.data.reporting_contracts %}
  <article
    class="reporting-contract-card"
    id="reporting-{{ contract.id }}"
    data-reporting-contract
    data-reporting-layer="{{ contract.layer | escape }}"
    data-reporting-kind="{{ contract.kind | escape }}"
    data-reporting-search="{{ contract.id }} {{ contract.layer }} {{ contract.kind }} {{ contract.signal }} {{ contract.runtime_source }} {{ contract.meaning }} {{ contract.denominator }} {{ contract.can_say }} {{ contract.cannot_say }} | downcase | escape }}"
  >
    <div class="reporting-contract-badges">
      <span>{{ contract.layer }}</span>
      <span>{{ contract.kind }}</span>
    </div>

    <p class="reporting-contract-signal"><code>{{ contract.signal }}</code></p>

    <h2>{{ contract.meaning }}</h2>

    <dl class="reporting-contract-meta">
      <div>
        <dt>Source / evidence object</dt>
        <dd><code>{{ contract.runtime_source }}</code></dd>
      </div>
      <div>
        <dt>Denominator to preserve</dt>
        <dd>{{ contract.denominator }}</dd>
      </div>
    </dl>

    <div class="reporting-claim-grid">
      <section>
        <h3>Evidence can support</h3>
        <p>{{ contract.can_say }}</p>
      </section>
      <section class="reporting-claim-boundary">
        <h3>Do not claim</h3>
        <p>{{ contract.cannot_say }}</p>
      </section>
    </div>

    <details>
      <summary>Methods wording</summary>
      <p data-reporting-template="methods">{{ contract.methods_template }}</p>
      <button type="button" data-reporting-copy="methods">Copy Methods wording</button>
    </details>

    <details>
      <summary>Results wording</summary>
      <p data-reporting-template="results">{{ contract.results_template }}</p>
      <button type="button" data-reporting-copy="results">Copy Results wording</button>
    </details>

    <details>
      <summary>Limitation wording</summary>
      <p data-reporting-template="limitation">{{ contract.limitation_template }}</p>
      <button type="button" data-reporting-copy="limitation">Copy limitation wording</button>
    </details>

    <div class="reporting-contract-routes">
      <a href="{{ contract.guide_url | relative_url }}">Guide / authority →</a>
      <a href="{{ contract.example_url | relative_url }}">Worked context →</a>
      {% if contract.api_anchor != '' %}
        <a href="{{ '/docs/reference/api-pathways/' | relative_url }}#{{ contract.api_anchor }}">API pathway →</a>
      {% endif %}
    </div>
  </article>
{% endfor %}
</div>

<div class="reporting-center-empty" data-reporting-empty hidden>
  <h2>No reporting contract matches these filters</h2>
  <p>Clear one or more filters, use site search with <strong>Ctrl/Cmd + K</strong>, or open the evidence-vocabulary reference.</p>
</div>

## Use the evidence hierarchy in the right order

Before choosing wording, answer these questions:

1. **What is the evidence object?** Runtime status, branch-level estimates, sensitivity summary, or frozen protocol outcome?
2. **What denominator produced it?** Rows, trial units, participants, valid specifications, successful specifications, or a frozen case-specific execution set?
3. **Is the signal generated by the package or interpreted by the researcher?**
4. **Does the wording stay inside the uncertainty dimensions actually tested?**
5. **What limitation must remain next to the claim?**

If any of those cannot be reconstructed, resolve the evidence record before polishing the sentence.

## Runtime status ≠ interpretation pattern ≠ frozen label

These three categories are intentionally different.

### Runtime status

Examples:

- `StudyQCReport.status == "pass"`;
- `StudyQCReport.status == "review"`;
- `AnalysisReadinessReport.status == "unassessed"`;
- `AnalysisReadinessReport.status == "ready_under_policy"`;
- `AnalysisReadinessReport.status == "review_under_policy"`.

These are software-returned states with bounded meanings.

### Interpretation pattern

Examples:

- complete specification execution with relatively stable direction/magnitude;
- stable direction but materially variable magnitude;
- sign-changing estimates;
- incomplete execution;
- descriptive marginal/pairwise sensitivity.

These are not package enum values. They require researcher interpretation of the complete evidence record.

### Protocol-bound evidence label

`incomplete`, `robust_negative`, and `materially_fragile` belong only to the frozen validation cases that define them.

Do not transfer those labels to a new dataset.

## Preserve the denominator before the adjective

A sentence such as:

> The result was robust.

is not reconstructable.

A bounded statement starts with the evidence denominator:

> Across all [N] valid represented specifications in the declared analysis space, estimates remained [direction] and ranged from [min] to [max].

Likewise, readiness reporting should say whether retention refers to rows, trial units, participant units, trial-scope filtering, or participant-scope filtering.

## Avoid inferential upgrades

Descriptive GazeAudit outputs should not be silently rewritten as:

- confidence intervals;
- Bayesian credible intervals;
- posterior probabilities;
- statistical significance;
- causal variance decomposition;
- inferential interaction effects;
- universal data-quality grades.

If the study includes a separate inferential model, report that model under its own assumptions and denominator.

## Reporting workflow

<div class="workflow-steps">
  <div class="workflow-step">
    <strong>Identify</strong>
    <p>Locate the runtime status, complete branch ledger, sensitivity summary, or frozen evidence record.</p>
  </div>
  <div class="workflow-step">
    <strong>Denominate</strong>
    <p>Write down exactly which rows, units, participants, valid branches, or protocol runs belong in the denominator.</p>
  </div>
  <div class="workflow-step">
    <strong>Interpret</strong>
    <p>Separate observation from researcher judgement, and direction from magnitude where relevant.</p>
  </div>
  <div class="workflow-step">
    <strong>Bound</strong>
    <p>Add the limitation that prevents the descriptive evidence from becoming a stronger inferential claim.</p>
  </div>
  <div class="workflow-step">
    <strong>Archive</strong>
    <p>Bind the final wording to the evidence object, decision record, software identity, and manuscript location.</p>
  </div>
</div>

## Reporting examples are templates, not automatic prose

Every copy button on this page returns **bounded template language**. Bracketed placeholders must be replaced with the actual evidence record. Remove wording that does not apply.

Do not paste a template into a manuscript without checking:

- endpoint identity;
- analysis timing;
- denominator;
- execution completeness;
- filter scope;
- magnitude scale;
- unresolved uncertainty;
- temporal evidence layer.

## Companion guidance

- [Claim-boundary reporting guide]({{ '/docs/guides/claim-boundary-reporting/' | relative_url }}) — systematic workflow for status → denominator → claim → limitation → archive.
- [Reporting-language rewrite exercise]({{ '/docs/examples/reporting-language-rewrite/' | relative_url }}) — rewrite over-strong synthetic manuscript sentences into evidence-bounded language.
- [Evidence and denominator vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }}) — exact runtime vs audit terminology.
- [Interpret an audit result]({{ '/docs/guides/interpret-audit-result/' | relative_url }}) — interpretation sequence for robustness evidence.
- [Reporting robustness]({{ '/docs/guides/reporting-robustness/' | relative_url }}) — descriptive specification/sensitivity reporting.
- [Publication audits]({{ '/docs/guides/publication-audits/' | relative_url }}) — preserve the final evidence/wording record.

## Machine-readable reference

The same governed contracts are available as [`reporting-contract-reference.json`]({{ '/assets/reporting-contract-reference.json' | relative_url }}).

That JSON is documentation metadata. It does not classify an analysis automatically.
