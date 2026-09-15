---
title: Audit planner
description: Build a transparent GazeAudit route from study risks and research tasks without automating scientific judgement.
kicker: Plan an audit
page_type: planner
permalink: /docs/planner/
---

# Audit planner

Use this planner to turn **study conditions you already know** into a transparent navigation path through GazeAudit. It does not choose thresholds, exclude participants, declare validity, or decide which scientific assumptions are defensible for your study.

<div class="callout info">
<strong>Navigation, not scientific judgement.</strong>
Every recommendation comes from a visible planner rule and points to a method family already governed by the Method explorer. Selecting an item means “this issue is relevant to my audit,” not “GazeAudit has diagnosed a problem.”
</div>

<div class="audit-planner" data-audit-planner data-planner-index="{{ '/assets/planner-index.json' | relative_url }}" data-method-index="{{ '/assets/method-index.json' | relative_url }}" data-workflow-index="{{ '/assets/planner-workflow-index.json' | relative_url }}">
  <section class="planner-intro-card">
    <div>
      <span class="planner-kicker">Build your route</span>
      <h2>Select the conditions that actually apply.</h2>
      <p>Choose one or more statements. The planner will deduplicate the corresponding method families, preserve their canonical order, and explain why each method entered the route.</p>
    </div>
    <div class="planner-summary" aria-live="polite">
      <strong data-planner-count>0</strong>
      <span>method families selected</span>
    </div>
  </section>

  <div class="planner-choice-grid" data-planner-choices>
    {% for item in site.data.planner %}
    <label class="planner-choice" data-planner-choice-card data-choice-id="{{ item.id }}">
      <input type="checkbox" value="{{ item.id }}" data-planner-choice>
      <span class="planner-choice-copy">
        <small>{{ item.group }}</small>
        <strong>{{ item.label }}</strong>
        <span>{{ item.prompt }}</span>
      </span>
      <span class="planner-check" aria-hidden="true">✓</span>
    </label>
    {% endfor %}
  </div>

  <div class="planner-actions" data-planner-actions hidden>
    <button type="button" class="button primary" data-planner-share>Copy plan link</button>
    <button type="button" class="button" data-planner-copy-brief>Copy audit brief</button>
    <button type="button" class="button" data-planner-download-json>Download plan JSON</button>
    <button type="button" class="button" data-planner-clear>Clear selections</button>
    <a class="button" href="{{ '/docs/methods/' | relative_url }}">Open full Method explorer</a>
  </div>
  <p class="planner-export-status" data-planner-export-status aria-live="polite" hidden></p>

  <section class="planner-results" data-planner-results hidden aria-live="polite">
    <div class="planner-results-head">
      <div>
        <span class="planner-kicker">Recommended route</span>
        <h2>Your selected audit path</h2>
      </div>
      <p>Ordered by the governed method catalog, not by the order you clicked the choices.</p>
    </div>
    <div class="planner-route" data-planner-route></div>
  </section>

  <section class="planner-workflows" data-planner-workflows hidden aria-live="polite">
    <div class="planner-results-head">
      <div>
        <span class="planner-kicker">Workflow handoff</span>
        <h2>Continue from methods into an end-to-end workflow</h2>
      </div>
      <p>These handoffs are governed navigation links. They do not add methods, infer risks, or change your selected plan.</p>
    </div>
    <div class="planner-workflow-grid" data-planner-workflow-list></div>
  </section>

  <div class="planner-empty" data-planner-empty>
    <strong>No route selected yet.</strong>
    <p>Choose the study conditions that are relevant above. If you already know the methodological question, go directly to the <a href="{{ '/docs/methods/' | relative_url }}">Method explorer</a>.</p>
  </div>
</div>

## Exporting a plan

The **audit brief** and **JSON plan** are portable navigation records. They preserve the conditions you selected, the deduplicated method route, the reasons those methods entered the route, workflow handoffs, the current plan URL, and the documentation build revision when available. They deliberately do **not** contain invented thresholds, exclusions, diagnoses, or case-study outcomes for your study.

The JSON export has a stable `schema_version` field and is deterministic for the same selection on the same documentation build. No timestamp is inserted, so two collaborators can compare the substantive plan rather than an incidental export time.

## How the planner is governed

The planner has three machine-readable inputs. `planner-index.json` contains only the navigation rules shown on this page, `method-index.json` contains the ten governed method families, and `planner-workflow-index.json` contains the three end-to-end workflow handoffs. CI verifies that every planner rule references an existing method ID, every planner-reachable method maps to exactly one workflow handoff, and every generated guide, example, plot, evidence, and workflow link resolves.

The planner deliberately **does not** infer a missing risk from another answer. For example, selecting sampling-rate sensitivity does not automatically add missingness sensitivity. Likewise, selecting an empirical case-related method does not copy that case's outcome onto your study. Workflow handoffs are downstream navigation only; they do not alter the plan encoded in the URL.

## What to record in a study

A useful audit record should preserve why a method was included, the exact GazeAudit version or commit, the declared thresholds or perturbation levels, the executed specifications, and the resulting artifacts. Use the [publication-audit guide]({{ '/docs/guides/publication-audits/' | relative_url }}) when you need deterministic provenance for a manuscript or archive.
