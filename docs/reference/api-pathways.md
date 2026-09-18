---
title: API pathways
description: Deep-linkable public API routes connecting GazeAudit symbols to their governed method family, guide, runnable example, visual, and evidence boundary.
kicker: Reference · API pathways
page_type: api-pathways
permalink: /docs/reference/api-pathways/
search_category: Reference
search_keywords: api pathways symbols deep links function anchors examples plots evidence boundary guide reference run_specs aoi probabilities
---

# API pathways

Use this page when you already know a **public symbol** and want to move from that symbol to the surrounding research context: its governed method family, practical guide, runnable example, diagnostic visual, and evidence boundary.

The page is generated from the same `_data/methods.yml` catalog that powers the [Method explorer]({{ '/docs/methods/' | relative_url }}). It does not maintain a second method taxonomy.

<div class="callout info">
<strong>Navigation, not scientific recommendation.</strong>
A pathway tells you where a public function appears in the governed documentation. It does not decide whether the method, threshold, exclusion, endpoint, perturbation, or evidence claim is appropriate for a particular study.
</div>

{% assign api_source_ref = site.github.build_revision | default: 'main' %}
<div data-api-pathways data-api-symbol-reference="{{ '/assets/api-symbol-reference.json' | relative_url }}" data-api-source-base="https://github.com/stefanosbalaskas/GazeAudit/blob/{{ api_source_ref }}">

## Jump by method family

<nav class="api-pathway-jumps" aria-label="API pathway families">
{% for method in site.data.methods %}
  <a href="#path-{{ method.id }}"><span>{{ method.phase }}</span><strong>{{ method.title }}</strong></a>
{% endfor %}
</nav>

## Deep link directly to a public symbol

Each symbol below has a stable fragment identifier. Opening or sharing a symbol link lands on the method family that currently governs its documentation context.

<div class="api-symbol-index" aria-label="Public API symbol deep links">
{% for method in site.data.methods %}
  <section class="api-symbol-index-group" aria-labelledby="symbol-index-{{ method.id }}">
    <h3 id="symbol-index-{{ method.id }}">{{ method.title }}</h3>
    <div class="api-symbol-index-links">
    {% for function in method.functions %}
      {% assign symbol_id = function | downcase | replace: '_', '-' %}
      <a href="#api-{{ symbol_id }}"><code>{{ function }}</code></a>
    {% endfor %}
    </div>
  </section>
{% endfor %}
</div>

## Governed API routes

{% for method in site.data.methods %}
<section class="api-pathway" aria-labelledby="path-{{ method.id }}">
  <div class="api-pathway-head">
    <div>
      <p class="api-pathway-phase">{{ method.phase }}</p>
      <h2 id="path-{{ method.id }}">{{ method.title }}</h2>
    </div>
    <a class="api-pathway-self-link" href="#path-{{ method.id }}" aria-label="Link to {{ method.title }} pathway"># pathway</a>
  </div>

  <p class="api-pathway-question">{{ method.question }}</p>
  <p>{{ method.purpose }}</p>

  <h3>Public API route</h3>

  <pre><code class="language-text">{{ method.functions | join: ' → ' }}</code></pre>

  <ul class="api-symbol-list" aria-label="Deep links for {{ method.title }}">
  {% for function in method.functions %}
    {% assign symbol_id = function | downcase | replace: '_', '-' %}
    <li id="api-{{ symbol_id }}">
      <a href="#api-{{ symbol_id }}"><code>{{ function }}</code><span>Direct link</span></a>
    </li>
  {% endfor %}
  </ul>

  <div class="api-pathway-route-grid">
    <a href="{{ method.guide_url | relative_url }}">
      <span>Guide</span>
      <strong>{{ method.guide_label }}</strong>
    </a>
    <a href="{{ method.example_url | relative_url }}">
      <span>Run / example</span>
      <strong>{{ method.example_label }}</strong>
    </a>
    <a href="{{ method.plot_url | relative_url }}">
      <span>Visual</span>
      <strong>{{ method.plot_label }}</strong>
    </a>
  </div>

  <div class="api-pathway-evidence">
    <p class="api-pathway-evidence-label">Evidence boundary</p>
    <p>{{ method.evidence_note }}</p>
    {% if method.evidence_url != '' %}
      <p><a href="{{ method.evidence_url | relative_url }}">{{ method.evidence_label }} →</a></p>
    {% else %}
      <p><strong>No frozen empirical case is assigned to this pathway.</strong></p>
    {% endif %}
  </div>
</section>
{% endfor %}

</div>

## Source-level details

When JavaScript is available, each governed symbol above is enhanced from the deterministic API metadata artifact with:

- the exact inspected Python signature;
- function/class kind and source module;
- repository-relative source file and first source line;
- the first source-docstring summary;
- a direct source link pinned to the documentation build revision;
- a copyable import statement;
- backlinks to every governed method pathway that uses the symbol.

The static symbol, method-family, guide, example, visual, and evidence-boundary links remain available when JavaScript or metadata loading is unavailable. The generated metadata is verified against the installed package in CI, so a signature/source change cannot silently leave the checked reference stale.

## How to use a symbol link

For example, a direct link to `run_specs` is:

```text
/docs/reference/api-pathways/#api-run-specs
```

That link does not make `run_specs` the correct tool for a study. It only resolves the symbol into its governed **Specification-space robustness** context, where you can inspect the guide, runnable example, specification-curve visual, and the exact evidence boundary.

For a worked exercise, continue to [Function → example → evidence]({{ '/docs/examples/function-to-evidence/' | relative_url }}). For broad task-first discovery, use the [Method explorer]({{ '/docs/methods/' | relative_url }}).
