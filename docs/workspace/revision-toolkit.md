---
title: Peer-review revision toolkit
description: Task-based workspace for classifying reviewer requests, preserving post-review analyses, writing response evidence, building a revision reproducibility package, and completing the final resubmission handoff.
kicker: Workspace · Revision toolkit
permalink: /docs/workspace/revision-toolkit/
search_category: Start
search_keywords: reviewer revision response rebuttal amendment reanalysis correction endpoint package cli response matrix version change manifest evidence map resubmission editor handoff
---

# Peer-review revision toolkit

Use this workspace when a manuscript has entered peer review and the revision now mixes **prose changes, new analyses, changed endpoints, corrections, and final archive work**. It routes each task to the smallest relevant guide or worked example while keeping the submitted record recoverable.

<div class="callout warning">
<strong>Revision extends the evidence history; it does not rewrite it.</strong>
Keep what existed at submission distinct from work introduced after outcomes had already been inspected. A submitted <code>8 / 8</code> audit followed by a reviewer-requested <code>4 / 4</code> sensitivity amendment remains <strong>8 / 8 submitted + 4 / 4 post-review</strong>, not “12 pre-specified analyses.”
</div>

## Choose what you need to do now

<div class="card-grid">
  <article class="card">
    <div class="card-icon" aria-hidden="true">1</div>
    <h3>Classify the reviewer request</h3>
    <p>Decide whether the item is a clarification, correction, sensitivity amendment, analytical amendment, endpoint amendment, or measurement amendment before changing the record.</p>
    <p><a href="{{ '/docs/guides/reviewer-requested-amendments/' | relative_url }}">Classify the request →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">2</div>
    <h3>Run and preserve new analysis</h3>
    <p>Declare the post-review specification space, record whether outcomes were already seen, keep valid failures in the denominator, and save the amendment separately.</p>
    <p><a href="{{ '/docs/examples/reviewer-requested-reanalysis/' | relative_url }}">Worked reanalysis →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">3</div>
    <h3>Write the response letter</h3>
    <p>Bind each reviewer item to its category, timing, action, evidence, manuscript location, archive location, and execution denominator.</p>
    <p><a href="{{ '/docs/guides/reviewer-response-letter/' | relative_url }}">Response-letter guide →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">4</div>
    <h3>Record what changed</h3>
    <p>Give every material v1 → v2 change a stable ID and distinguish editorial edits from corrections and analytical amendments.</p>
    <p><a href="{{ '/docs/guides/version-change-manifest/' | relative_url }}">Version-change manifest →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">5</div>
    <h3>Build the revision package</h3>
    <p>Use the real CLI to scaffold response, change, amendment, software-identity, and editor-facing evidence-map records, then validate the structural manifest.</p>
    <p><a href="{{ '/docs/guides/reproducibility-package/' | relative_url }}">Reproducibility package →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">6</div>
    <h3>Run the final handoff check</h3>
    <p>Verify reviewer-item closure, temporal denominators, response/manuscript agreement, software identity, archive evidence, and unresolved limitations before resubmission.</p>
    <p><a href="{{ '/docs/guides/resubmission-readiness/' | relative_url }}">Resubmission readiness →</a></p>
  </article>
</div>

## Request → record → evidence map

| Reviewer situation | Preserve | Do not do | Continue with |
|---|---|---|---|
| Wording is unclear; no analysis changes | response item + manuscript location | invent an analytical amendment | [Response-letter guide]({{ '/docs/guides/reviewer-response-letter/' | relative_url }}) |
| Reviewer asks for another threshold or exclusion | dated amendment + separate denominator | merge it into the submitted denominator | [Reanalysis example]({{ '/docs/examples/reviewer-requested-reanalysis/' | relative_url }}) |
| Reviewer asks for a different endpoint | endpoint-specific amendment record | mix endpoints inside one robustness denominator | [Amendment guide]({{ '/docs/guides/reviewer-requested-amendments/' | relative_url }}) |
| One valid post-review branch fails technically | valid denominator + failure reason + incomplete status | relabel `3 / 4` as `3 / 3` | [Revision-package example]({{ '/docs/examples/reproducibility-package-cli/' | relative_url }}) |
| Review exposes a coding/import/analysis defect | superseded evidence + defect record + regenerated outputs | delete the superseded record | [Version-change manifest]({{ '/docs/guides/version-change-manifest/' | relative_url }}) |
| All reviewer work is complete | response matrix + change manifest + evidence map | rely on the response letter alone | [Resubmission readiness]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) |

## The minimum revision record

A reconstructable review round should answer seven questions without oral explanation:

1. **What existed at submission?**
2. **Which reviewer item introduced this change?**
3. **Had the relevant outcomes already been inspected?**
4. **What analysis or documentation action was taken?**
5. **What is the submitted denominator and what is the post-review denominator?**
6. **Where did the manuscript change?**
7. **Which archived file supports the response?**

If one of those answers is hidden in email, lab memory, or an untracked local folder, the revision record is not yet independently reconstructable.

## Fast executable path

Create the governed scaffold:

```bash
gazeaudit-revision-package init \
  --output-dir revision-package \
  --project-slug my-study \
  --review-round 1
```

Populate the response matrix, version-change manifest, amendment folders, and editor-facing evidence map, then run:

```bash
gazeaudit-revision-package validate --root revision-package
```

A passing validation establishes **structural provenance only**. It checks the expected package files and deterministic manifest integrity; it does not certify the scientific validity of the analysis or the editorial quality of the manuscript.

For the full break-and-repair exercise, use the [revision reproducibility package worked example]({{ '/docs/examples/reproducibility-package-cli/' | relative_url }}).

## Three records that should not be collapsed

<div class="workflow-steps">
  <div class="workflow-step"><strong>Submitted</strong><p>The endpoint, decisions, valid denominator, successes, failures, software identity, and claims that existed before peer-review amendments.</p></div>
  <div class="workflow-step"><strong>Post-review</strong><p>Reviewer-triggered clarifications, sensitivity analyses, analytical changes, endpoint additions, measurement changes, and corrections, each with timing.</p></div>
  <div class="workflow-step"><strong>Final handoff</strong><p>The revised manuscript, response matrix, version-change manifest, evidence map, software record, limitations, and publication-associated archive.</p></div>
</div>

The final archive can contain all three layers, but they should remain identifiable as different temporal records.

## Worked routes

### One sensitivity amendment

Use the [reviewer-requested reanalysis example]({{ '/docs/examples/reviewer-requested-reanalysis/' | relative_url }}) when the main challenge is adding one post-review analysis without rewriting the submitted declaration.

### Multiple reviewer items

Use the [revision response package example]({{ '/docs/examples/revision-response-package/' | relative_url }}) when clarification, new analysis, and endpoint changes must all agree across the response letter, manuscript, and archive.

### Executable package validation

Use the [reproducibility-package CLI example]({{ '/docs/examples/reproducibility-package-cli/' | relative_url }}) when you want to create the actual scaffold, deliberately break a governed file, see the validator fail, and repair it.

### Complete submission → final record

Use [submission-to-accepted-record]({{ '/docs/examples/submission-to-accepted-record/' | relative_url }}) to trace the synthetic submitted `8 / 8` record, reviewer-requested `4 / 4` amendment, separate endpoint amendment, response matrix, version manifest, final evidence map, and publication-associated archive.

## Five-minute pre-resubmission check

Before the revised manuscript leaves the team, verify that:

- every reviewer item has a stable disposition;
- every new analysis is labelled with its post-review timing;
- submitted and post-review denominators are not collapsed;
- failed valid branches remain visible;
- endpoint amendments remain endpoint-specific;
- corrections retain superseded evidence and affected-claim provenance;
- response wording matches manuscript wording;
- every material response points to real archived evidence;
- the final software identity is recorded;
- the evidence map points from each final claim component back to its temporal evidence layer.

Then run the fuller [resubmission readiness and editor handoff]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) gate.

## Evidence boundaries

<div class="callout info">
<strong>This toolkit is provenance infrastructure, not an acceptance predictor.</strong>
It does not decide whether a reviewer request is scientifically justified, whether a model is appropriate, whether an effect is robust, whether a manuscript should be accepted, or whether editorial acceptance validates a result. Those remain separate scientific and editorial judgements.
</div>

GazeAudit's frozen empirical case-study outcomes are unchanged and remain authoritative only within their own protocols: GazeBase `incomplete`, Korthals `robust_negative`, and Pedrotti/de Chambrier `materially_fragile`. The reviewer examples linked from this page are synthetic teaching material.

## Full review route

For the complete interpret → draft → reconstruct → amend → respond → archive sequence, continue to the [manuscript review path]({{ '/docs/workspace/manuscript-review-path/' | relative_url }}). For durable publication provenance after the revision is finalized, continue to the [reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}).
