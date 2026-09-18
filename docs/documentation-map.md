---
title: Documentation compass
description: "Choose GazeAudit documentation by intent: learn a workflow, complete a task, look up an exact contract, or understand the reasoning and evidence boundary."
kicker: Documentation · Compass
permalink: /docs/documentation-map/
search_category: Start
search_keywords: documentation map compass learn do look up understand tutorial how-to reference explanation examples guides articles case studies
---

# Documentation compass

Choose the route that matches **what you are trying to do right now**. The same topic may appear in more than one documentation type because learning a workflow, completing a task, looking up an exact contract, and understanding the reasoning are different needs.

This structure is adapted from the tutorial / how-to / reference / explanation separation described by [Diátaxis](https://diataxis.fr/). GazeAudit keeps its existing public sections, but makes their intended use explicit instead of renaming every page.

<div class="documentation-compass" aria-label="Choose documentation by intent">
  <article class="documentation-compass-card">
    <span class="documentation-compass-mode">Learn</span>
    <h2>Build confidence by doing</h2>
    <p>Use a small synthetic or guided workflow when the goal is to learn how the pieces fit together.</p>
    <div class="documentation-compass-links">
      <a href="{{ '/docs/getting-started/' | relative_url }}">Getting started</a>
      <a href="{{ '/docs/examples/' | relative_url }}">Examples</a>
      <a href="{{ '/docs/examples/catalog/' | relative_url }}">Example catalog</a>
      <a href="{{ '/docs/examples/end-to-end-robustness/' | relative_url }}">End-to-end robustness</a>
      <a href="{{ '/docs/guides/adapt-examples-to-study/' | relative_url }}">Adapt examples safely</a>
    </div>
  </article>

  <article class="documentation-compass-card">
    <span class="documentation-compass-mode">Do</span>
    <h2>Complete a research task</h2>
    <p>Use goal-oriented guidance when you already have a study, decision, reviewer request, or blocked workflow to handle.</p>
    <div class="documentation-compass-links">
      <a href="{{ '/docs/guides/' | relative_url }}">Guides</a>
      <a href="{{ '/docs/guides/data-mapping-provenance/' | relative_url }}">Data mapping provenance</a>
      <a href="{{ '/docs/guides/structural-qc-triage/' | relative_url }}">Structural-QC triage</a>
      <a href="{{ '/docs/guides/readiness-policy-design/' | relative_url }}">Readiness policy design</a>
      <a href="{{ '/docs/guides/claim-boundary-reporting/' | relative_url }}">Claim-boundary reporting</a>
      <a href="{{ '/docs/workflows/' | relative_url }}">Workflows</a>
      <a href="{{ '/docs/guides/troubleshooting/' | relative_url }}">Troubleshooting</a>
    </div>
  </article>

  <article class="documentation-compass-card">
    <span class="documentation-compass-mode">Look up</span>
    <h2>Find an exact fact or contract</h2>
    <p>Use reference material when the question is factual: a function signature, CLI command, denominator term, source revision, or frozen authority.</p>
    <div class="documentation-compass-links">
      <a href="{{ '/docs/reference/' | relative_url }}">Reference hub</a>
      <a href="{{ '/docs/data-contract/' | relative_url }}">Data contract</a>
      <a href="{{ '/docs/reference/qc-issue-clinic/' | relative_url }}">Structural QC Issue Clinic</a>
      <a href="{{ '/docs/readiness-policy/' | relative_url }}">Readiness Policy Design Center</a>
      <a href="{{ '/docs/reporting-center/' | relative_url }}">Results & Reporting Center</a>
      <a href="{{ '/docs/reference/api-pathways/' | relative_url }}">API pathways</a>
      <a href="{{ '/docs/VALIDATION_MATRIX.html' | relative_url }}">Validation matrix</a>
    </div>
  </article>

  <article class="documentation-compass-card">
    <span class="documentation-compass-mode">Understand</span>
    <h2>Understand why the system is structured this way</h2>
    <p>Use conceptual material and bounded case studies when the goal is interpretation, rationale, or methodological context rather than a procedure.</p>
    <div class="documentation-compass-links">
      <a href="{{ '/docs/articles/' | relative_url }}">Articles</a>
      <a href="{{ '/docs/case-studies/' | relative_url }}">Case studies</a>
      <a href="{{ '/docs/SCIENTIFIC_METHODS.html' | relative_url }}">Scientific methods</a>
    </div>
  </article>
</div>

<div class="callout info">
<strong>The compass is navigation support, not a scientific decision rule.</strong>
Choosing a documentation type does not choose an endpoint, threshold, exclusion rule, AOI definition, perturbation, estimator, or evidence claim.
</div>

## One topic can legitimately have several routes

For **specification-space robustness**:

| Need | Route |
|---|---|
| Learn the sequence on deterministic data | [End-to-end robustness example]({{ '/docs/examples/end-to-end-robustness/' | relative_url }}) |
| Apply the method to a research decision | [Specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }}) |
| Look up the public function contract | [`run_specs` API pathway]({{ '/docs/reference/api-pathways/' | relative_url }}#api-run-specs) |
| Understand why one pipeline is insufficient | [From one pipeline to a robustness audit]({{ '/docs/articles/from-one-pipeline-to-a-robustness-audit/' | relative_url }}) |
| Inspect the empirical boundary | [Case studies]({{ '/docs/case-studies/' | relative_url }}) |

The pages are related, but they should not collapse into one giant page. Reference stays factual; how-to guidance stays task-oriented; teaching examples remain explicit about synthetic choices; conceptual pages can explain rationale without pretending to be executable instructions.

## If you are blocked

Use the intent that best matches the blocker:

1. **I do not know how the workflow works** → start with **Learn**.
2. **I know what I need to accomplish** → use **Do**.
3. **I need exact syntax, terminology, or provenance** → use **Look up**.
4. **I need to understand the rationale or evidence boundary** → use **Understand**.

If the problem is a failure rather than a documentation-choice problem, go directly to [Troubleshooting GazeAudit]({{ '/docs/guides/troubleshooting/' | relative_url }}).

## Search is a second route

Use **Ctrl/Cmd + K** when you already have useful words such as `run_specs`, `AOI uncertainty`, `technical_failure`, or `revision package`. Search results are grouped by documentation type so you can choose the kind of answer you need rather than treating ranking as a scientific recommendation.

For a worked exercise, continue to [Documentation intent routing]({{ '/docs/examples/documentation-intent-routing/' | relative_url }}).
