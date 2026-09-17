---
title: Peer-review revision route map
description: Route reviewer requests into clarification, correction, sensitivity, analytical, endpoint, or measurement work while preserving submitted and post-review evidence as distinct temporal records.
kicker: Peer-review revision
page_type: guide
permalink: /docs/guides/revision-route-map/
search_category: Guides
search_keywords: peer review reviewer revision rebuttal response resubmission amendment correction sensitivity endpoint measurement denominator failed branch package route map
---

# Peer-review revision route map

Use this guide **before changing analysis files in response to peer review**. Its purpose is to route each reviewer request into the smallest auditable action while preserving what existed at submission.

The route map is a documentation and provenance aid. It does **not** decide whether a reviewer request is scientifically justified, whether a new analysis is appropriate, whether a result is robust, or whether a manuscript is publication-ready.

<div class="callout warning">
<strong>Revision extends the evidence history; it does not rewrite it.</strong>
If the submitted record was <code>8 / 8</code> and peer review later adds a valid <code>4 / 4</code> sensitivity amendment, preserve the record as <strong>8 / 8 submitted + 4 / 4 post-review</strong>. Do not relabel the combined history as “12 pre-specified analyses.”
</div>

## Start with one question

**What kind of change does the reviewer request actually require?**

| Reviewer request | Route | New execution denominator? | Minimum record |
|---|---|---:|---|
| Explain wording, method, denominator, or existing output | `documentation_clarification` | No | response item + manuscript location |
| Repair a coding, import, transcription, or analysis defect | `correction` | Usually yes | superseded evidence + corrected evidence + claim impact |
| Add a threshold, exclusion, perturbation, or robustness check on the same endpoint | `sensitivity_amendment` | Yes | amendment declaration + valid/successful denominator + outputs |
| Add another defensible analytical branch on the same endpoint | `analytical_amendment` | Yes | amendment declaration + denominator + outputs |
| Analyse a materially different endpoint | `endpoint_amendment` | Separate endpoint | endpoint record + separate denominator + manuscript location |
| Change AOI, detector, calibration, error model, or measurement assumption | `measurement_amendment` | Yes | measurement declaration + denominator + outputs |
| Decline or scope a request without new analysis | documented response | No | rationale + manuscript/response location |

A reviewer sentence can contain more than one request. Split it into separate response units when the actions, endpoints, evidence, or manuscript locations differ.

## Route 1 — clarification only

Use a clarification route when the requested answer already exists in the submitted record and no analytical result must be regenerated.

Record:

1. the reviewer item;
2. `documentation_clarification`;
3. whether outcomes had already been inspected — normally yes during peer review;
4. the submitted denominator exactly as it existed;
5. the manuscript location changed;
6. the archive location supporting the clarification.

Do **not** create a post-review analytical denominator simply because explanatory prose changed.

## Route 2 — correction

Use `correction` when the submitted record contains a defect rather than a newly requested sensitivity analysis.

A correction should preserve both temporal layers:

- the submitted evidence that is now superseded;
- the corrected evidence;
- what caused the defect;
- whether the numerical result changed;
- whether the manuscript claim changed;
- which files are now authoritative.

Do not erase the superseded file merely because it should no longer support the current claim. The revision archive should allow an outsider to reconstruct **what changed and why**.

## Route 3 — sensitivity or analytical amendment

Use a post-review amendment when the reviewer asks for new work on the same scientific endpoint.

Before execution, record:

- the reviewer item;
- the amendment category;
- the reason for the new branch or factor;
- the endpoint that must remain fixed;
- the number of valid post-review branches;
- that the request occurred after outcome inspection;
- the intended manuscript and archive destinations.

After execution, report the amendment denominator on its own. If all four valid branches succeed, record `4 / 4`. If one valid branch fails technically, record **3 successful / 4 valid** and preserve the failure.

<div class="callout warning">
<strong>A valid technical failure remains in the denominator.</strong>
A post-review amendment with three successful estimates and one unresolved valid failure is <code>3 / 4</code>, not <code>3 / 3</code>. Do not silently shrink the denominator to the successful branches.
</div>

## Route 4 — endpoint amendment

A different endpoint is not another branch of the original endpoint denominator.

For example:

- submitted endpoint `E1`: `8 / 8`;
- reviewer-requested sensitivity amendment on `E1`: `4 / 4` post-review;
- reviewer-requested endpoint `E2`: a **separate endpoint record** with its own denominator.

Keep the endpoint identity explicit in the response letter, Results text, evidence map, and archive paths. Do not combine E2 into E1 merely to produce a larger branch count.

## Route 5 — measurement amendment

Use `measurement_amendment` when peer review changes the measurement layer rather than only the downstream analytical specification.

Examples include:

- a different AOI boundary treatment;
- a revised detector assumption;
- an uncertainty-aware assignment model;
- a calibration or gaze-error assumption;
- an alternative measurement preprocessing rule.

Preserve the original submitted measurement record, declare the post-review measurement change, and state which endpoint the amendment feeds. A new measurement assumption can change the meaning of downstream estimates even when the endpoint label is unchanged.

## Route 6 — no new analysis

Not every reviewer request should produce another analysis. If the response is a clarification, scope explanation, limitation, or reasoned decision not to add a requested analysis, preserve that response explicitly.

The route map does not tell you whether declining a request is scientifically correct. It only prevents a **no-analysis response** from being confused with an executed amendment.

## The five-record revision chain

A reconstructable review round should be able to answer five questions in order:

1. **Submitted record** — what evidence and denominator existed before review?
2. **Reviewer request** — what was requested, and when?
3. **Revision action** — clarification, correction, sensitivity, analytical, endpoint, measurement, or no new analysis?
4. **Post-review evidence** — what was executed, with what valid and successful denominator?
5. **Handoff record** — where are the response, manuscript change, evidence, and software identity now recorded?

If any link is missing, stop the handoff and repair the provenance record before calling the round reconstructable.

## Use the executable package when the route is known

Create a governed revision package:

```bash
gazeaudit-revision-package init \
  --output-dir revision-package \
  --project-slug my-study \
  --review-round 1
```

Populate the response matrix, version-change manifest, amendment records, endpoint-amendment records, evidence map, and software identity. Then run:

```bash
gazeaudit-revision-package validate --root revision-package
```

Passing validation establishes **structural provenance only**. It does not establish analytical validity, robustness, manuscript quality, reviewer satisfaction, editorial acceptance, or publication readiness.

For a short executable exercise, use the [revision-package quickstart]({{ '/docs/examples/revision-package-quickstart/' | relative_url }}). For scenario-based routing practice, continue to the [revision-round scenarios]({{ '/docs/examples/revision-round-scenarios/' | relative_url }}).

## Handoff checklist

Before returning the revision to coauthors, reviewers, or an editor, verify that:

- every reviewer item has one stable identifier;
- each item has one explicit response category;
- submitted evidence remains recoverable;
- post-review amendments have their own valid and successful denominators;
- different endpoints remain separate;
- unresolved valid failures remain visible;
- corrections preserve superseded evidence;
- response-letter statements match manuscript changes;
- response-letter statements match archive locations;
- the exact GazeAudit release or commit is recorded;
- package validation is described as structural provenance validation, not scientific validation.

Then use the [peer-review revision checklist]({{ '/docs/guides/peer-review-revision-checklist/' | relative_url }}), [reviewer response guide]({{ '/docs/guides/reviewer-response-letter/' | relative_url }}), and [resubmission-readiness guide]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) for the detailed gates.

## Evidence boundary

The examples on this page are synthetic teaching material. They do not create new empirical validation evidence and do not alter the frozen case-study outcomes:

- GazeBase `incomplete`;
- Korthals `robust_negative`;
- Pedrotti/de Chambrier `materially_fragile`.

Those outcomes remain protocol-bound records and must not be transferred to a new study because its revision uses a similar method family.