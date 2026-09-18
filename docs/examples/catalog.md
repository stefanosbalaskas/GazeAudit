---
title: Example catalog
description: Browse every governed GazeAudit worked example by data context and methodological focus, with explicit reuse, output, and evidence-boundary contracts.
kicker: Examples · Catalog
page_type: example-catalog
permalink: /docs/examples/catalog/
search_category: Start
search_keywords: example catalog browse filter synthetic own data documentation software robustness measurement qc peer review publication api
---

# Example catalog

Use this catalog when you know that you want to **learn by doing** but are not yet sure which example best matches your task. Every listed example is generated from the example's own governed front matter rather than a second hand-maintained inventory.

The contract on each card answers five questions before you open the example:

1. **Data** — what kind of input context does the example use?
2. **Focus** — which methodological or project problem does it teach?
3. **Reuse** — which structural part is intended to transfer?
4. **Expected output** — what should the worked exercise produce?
5. **Evidence boundary** — what must not be inferred or transferred from the example?

<div class="callout warning">
<strong>Catalog filters are navigation, not scientific recommendations.</strong>
Filtering to a focus or data context does not rank methods, choose thresholds, define validity, or imply that the first matching example is appropriate for a study.
</div>

{% assign governed_examples = site.pages | where: "search_category", "Example" | sort: "title" %}

<div class="example-catalog-summary">
  <strong>{{ governed_examples | size }} governed examples</strong>
  <span>All remain visible when JavaScript is unavailable.</span>
</div>

<form class="example-catalog-controls" data-example-catalog-controls role="search" aria-label="Filter example catalog">
  <label>
    <span>Search examples</span>
    <input type="search" autocomplete="off" placeholder="Try “run_specs”, “reviewer”, or “AOI”…" data-example-catalog-search>
  </label>
  <label>
    <span>Data context</span>
    <select data-example-data-filter>
      <option value="">All data contexts</option>
      <option value="Synthetic">Synthetic</option>
      <option value="Demo or user data">Demo or user data</option>
      <option value="Software-only">Software-only</option>
      <option value="Documentation-only">Documentation-only</option>
    </select>
  </label>
  <label>
    <span>Focus</span>
    <select data-example-focus-filter>
      <option value="">All focus areas</option>
      <option value="Data & QC">Data &amp; QC</option>
      <option value="Measurement uncertainty">Measurement uncertainty</option>
      <option value="Robustness & sensitivity">Robustness &amp; sensitivity</option>
      <option value="Interpretation & reporting">Interpretation &amp; reporting</option>
      <option value="Documentation & API">Documentation &amp; API</option>
      <option value="Environment">Environment</option>
      <option value="Project lifecycle">Project lifecycle</option>
      <option value="Peer review & publication">Peer review &amp; publication</option>
      <option value="Reproducibility">Reproducibility</option>
    </select>
  </label>
  <button type="button" data-example-catalog-clear>Clear filters</button>
</form>

<p class="example-catalog-status" data-example-catalog-status role="status" aria-live="polite" aria-atomic="true">
  Showing all {{ governed_examples | size }} examples.
</p>

<div class="example-catalog-grid" data-example-catalog>
{% for example in governed_examples %}
  <article
    class="example-catalog-card"
    data-example-card
    data-example-data="{{ example.example_data | escape }}"
    data-example-focus="{{ example.example_focus | escape }}"
    data-example-search="{{ example.title | append: ' ' | append: example.description | append: ' ' | append: example.example_reuse | append: ' ' | append: example.example_output | append: ' ' | append: example.search_keywords | downcase | escape }}"
  >
    <div class="example-catalog-badges">
      <span>{{ example.example_data }}</span>
      <span>{{ example.example_focus }}</span>
    </div>
    <h2><a href="{{ example.url | relative_url }}">{{ example.title }}</a></h2>
    {% if example.description %}<p>{{ example.description }}</p>{% endif %}
    <dl>
      <div>
        <dt>Reuse</dt>
        <dd>{{ example.example_reuse }}</dd>
      </div>
      <div>
        <dt>Expected output</dt>
        <dd>{{ example.example_output }}</dd>
      </div>
      <div class="example-catalog-boundary">
        <dt>Evidence boundary</dt>
        <dd>{{ example.example_boundary }}</dd>
      </div>
    </dl>
    <p class="example-catalog-open"><a href="{{ example.url | relative_url }}">Open example →</a></p>
  </article>
{% endfor %}
</div>

<div class="example-catalog-empty" data-example-catalog-empty hidden>
  <h2>No examples match these filters</h2>
  <p>Clear one or more filters, use the site-wide search with <strong>Ctrl/Cmd + K</strong>, or return to the <a href="{{ '/docs/documentation-map/' | relative_url }}">Documentation compass</a>.</p>
</div>

## How to choose safely

Prefer the example whose **learning problem** matches yours, not the one whose synthetic values look most similar to your data.

- If you are learning a software interface, start with **Documentation-only** or **Software-only** material.
- If you are learning a scientific workflow, use **Synthetic** material and treat every concrete scientific value as a teaching value until independently justified.
- If you already have a canonical table, use **Demo or user data** routes and run structural preflight before scientific analysis.
- If you are preparing a revision or archive, use the peer-review/publication examples but preserve your own temporal evidence layers and denominators.

Before moving an example into a real analysis, use [Adapt a synthetic example to your study]({{ '/docs/guides/adapt-examples-to-study/' | relative_url }}).

For a worked catalog-selection exercise, continue to [Choose the right example]({{ '/docs/examples/choose-the-right-example/' | relative_url }}).
