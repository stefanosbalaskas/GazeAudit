---
title: Method explorer
description: Navigate GazeAudit from a research question to the relevant public API, guide, runnable example, diagnostic plot, and validation evidence.
kicker: Methods
page_type: methods
permalink: /docs/methods/
---

# Method explorer

Start from the **methodological decision you need to defend**, not from a module name. This explorer connects each research question to the smallest relevant public API sequence, a guide or runnable workflow, a diagnostic plot, and—where one genuinely exists—a frozen validation case.

<div class="callout info">
<strong>Evidence is not filled in for appearance.</strong>
A method family without a directly relevant frozen empirical case says so explicitly. Synthetic known-truth benchmarks, live interoperability contracts, and protocol-bound real-data outcomes are different evidence types and remain labelled separately.
</div>

<div class="method-explorer" data-method-explorer data-method-index="{{ '/assets/method-index.json' | relative_url }}">
  <div class="method-explorer-summary" aria-label="Method explorer summary">
    <div><strong>{{ site.data.methods | size }}</strong><span>method families</span></div>
    <div><strong>8</strong><span>research phases</span></div>
    <div><strong>3</strong><span>frozen real-data cases</span></div>
    <div><strong>1</strong><span>governed catalog</span></div>
  </div>

  <div class="method-controls" data-method-controls hidden>
    <div class="method-search-wrap">
      <label for="method-search">Find a method</label>
      <input id="method-search" type="search" placeholder="Try “missingness”, “AOI”, “publication”…" autocomplete="off" data-method-search>
    </div>
    <div class="method-phase-filters" role="group" aria-label="Filter by research phase">
      <button type="button" data-method-filter="all" aria-pressed="true">All</button>
      <button type="button" data-method-filter="preflight" aria-pressed="false">Preflight</button>
      <button type="button" data-method-filter="governance" aria-pressed="false">Governance</button>
      <button type="button" data-method-filter="measurement" aria-pressed="false">Measurement</button>
      <button type="button" data-method-filter="robustness" aria-pressed="false">Robustness</button>
      <button type="button" data-method-filter="sensitivity" aria-pressed="false">Sensitivity</button>
      <button type="button" data-method-filter="benchmarking" aria-pressed="false">Benchmarking</button>
      <button type="button" data-method-filter="evidence" aria-pressed="false">Evidence</button>
      <button type="button" data-method-filter="integration" aria-pressed="false">Integration</button>
    </div>
    <p class="method-result-count" data-method-result-count aria-live="polite"></p>
  </div>

  <div class="method-grid" data-method-grid>
    {% for method in site.data.methods %}
    <article class="method-card" data-method-card data-method-id="{{ method.id }}" data-phase="{{ method.phase_key }}" data-search="{{ method.title | escape }} {{ method.question | escape }} {{ method.functions | join: ' ' | escape }} {{ method.keywords | escape }}">
      <div class="method-card-main">
        <div class="method-card-head">
          <span class="method-phase">{{ method.phase }}</span>
          <span class="method-number">{{ forloop.index | prepend: '0' | slice: -2, 2 }}</span>
        </div>
        <h2>{{ method.title }}</h2>
        <p class="method-question">{{ method.question }}</p>
        <p class="method-purpose">{{ method.purpose }}</p>

        <div class="method-api-block">
          <div class="method-api-head">
            <span>Public API route</span>
            <button type="button" data-copy-sequence="{{ method.functions | join: ' → ' | escape }}" hidden>Copy sequence</button>
          </div>
          <div class="method-function-list" aria-label="Public functions for {{ method.title }}">
            {% for function in method.functions %}<code>{{ function }}</code>{% endfor %}
          </div>
        </div>

        <div class="method-route-grid">
          <a href="{{ method.guide_url | relative_url }}"><span>Guide</span><strong>{{ method.guide_label }}</strong></a>
          <a href="{{ method.example_url | relative_url }}"><span>Run</span><strong>{{ method.example_label }}</strong></a>
          <a href="{{ method.plot_url | relative_url }}"><span>Visual</span><strong>{{ method.plot_label }}</strong></a>
        </div>

        <div class="method-evidence">
          <span>Evidence boundary</span>
          {% if method.evidence_url != '' %}
          <p>{{ method.evidence_note }} <a href="{{ method.evidence_url | relative_url }}">{{ method.evidence_label }} →</a></p>
          {% else %}
          <p>{{ method.evidence_note }}</p>
          {% endif %}
        </div>
      </div>
      <a class="method-plot-preview" href="{{ method.plot_url | relative_url }}" aria-label="Open {{ method.plot_label }}">
        <img src="{{ method.plot_url | relative_url }}" alt="{{ method.plot_label }} diagnostic preview" loading="lazy">
      </a>
    </article>
    {% endfor %}
  </div>

  <div class="method-empty" data-method-empty hidden>
    <strong>No method family matches this filter.</strong>
    <p>Try a broader term, choose another phase, or use the site-wide <strong>Ctrl/Cmd + K</strong> search.</p>
  </div>
</div>

## How to use the map

The **public API route** is a compact orientation sequence, not a mandatory pipeline. The linked guides explain inputs, assumptions, return objects, and scientific boundaries in more detail. A plot link identifies a diagnostic that helps inspect the method; it does not imply that a visual threshold determines validity.

The **evidence boundary** is deliberately conservative. Frozen case-study labels remain protocol-bound records: `incomplete` for GazeBase, `robust_negative` for Korthals, and `materially_fragile` for Pedrotti/de Chambrier. Synthetic benchmarks and CI interoperability checks are not silently promoted to empirical validation.

## Need the full function inventory?

Use the [task-oriented API map]({{ '/docs/reference/api-map/' | relative_url }}) for broader function coverage, or the [CI-protected core API inventory]({{ '/docs/reference/core-api-inventory/' | relative_url }}) when you need the governed export list.
