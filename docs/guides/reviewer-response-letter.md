---
title: Reviewer response letter guide
description: Build an evidence-linked response letter that preserves review timing, submitted and post-review denominators, manuscript changes, and archived revision evidence.
kicker: Guide · Peer review
permalink: /docs/guides/reviewer-response-letter/
search_category: Guides
search_keywords: reviewer response letter revision rebuttal amendment denominator correction manuscript archive response table
---

# Reviewer response letter guide

A strong response letter should do more than say that a reviewer request was “addressed.” It should let an editor or reviewer recover **what was requested, what changed, when the change was introduced, which evidence supports it, and where the corresponding manuscript and archive changes can be found**.

<div class="callout info">
<strong>This is a provenance guide, not a persuasion template.</strong>
GazeAudit does not decide whether a reviewer request is scientifically justified. The purpose of this guide is to keep the revision record accurate when you clarify, amend, correct, decline, or scope a requested analysis.
</div>

## The response unit

Treat each reviewer item as one auditable response unit with seven fields:

1. **Reviewer request** — quote or summarize the methodological request faithfully.
2. **Response category** — clarification, correction, sensitivity amendment, analytical amendment, endpoint amendment, measurement amendment, or no analytical change.
3. **Timing** — state whether the original outcomes had already been inspected before the new decision was introduced.
4. **Action** — describe exactly what was changed or why no change was made.
5. **Evidence** — give the submitted and post-review execution denominators separately, including failures.
6. **Manuscript location** — identify the revised Methods, Results, table, figure, supplement, or limitation.
7. **Archive location** — identify the decision record and files that preserve the change.

A compact response-record entry can look like this:

```yaml
review_round: 1
reviewer_item: R1-C4
category: sensitivity_amendment
results_already_seen: yes
request: "Repeat the robustness analysis using a stricter quality threshold."
action: "Added a four-branch post-review sensitivity amendment."
submitted_execution: "8 / 8 valid branches completed"
amendment_execution: "4 / 4 added branches completed"
manuscript_locations:
  - "Methods: Revision analyses"
  - "Results: Reviewer-requested sensitivity analysis"
  - "Supplementary Table S7"
archive_locations:
  - "revision/round-1/R1-C4/amendment-record.yml"
  - "revision/round-1/R1-C4/specifications.csv"
```

## A practical response structure

For each comment, use the same four-part sequence:

**1. Acknowledge the request.** State what you understand the reviewer to be asking.

**2. State the action and timing.** Say whether the change is a clarification, a post-review amendment, a correction, or no analytical change. If the decision was introduced after outcome inspection, say so.

**3. Report the evidence at the correct denominator.** Keep submitted and post-review work temporally separate. If a valid branch failed, keep it visible.

**4. Point to the revised record.** Give manuscript locations and archive files so the reviewer does not have to infer what changed.

## Copy-ready response patterns

### Clarification only

> We clarified the original analysis description without changing the submitted specification space or rerunning the endpoint. The submitted execution record therefore remains 8 / 8 valid branches completed. The clarification appears in the revised Methods and in the decision log.

### Reviewer-requested sensitivity amendment

> In response to this request, and after the original outcomes had already been inspected, we added a separately recorded sensitivity amendment using the stricter threshold. The submitted audit remains 8 / 8 valid branches completed; the post-review amendment contributed 4 / 4 additional branches. We report the amendment separately in the revised Methods, Results, and Supplementary Table S7.

### Amendment with a technical failure

> The reviewer-requested amendment declared four valid branches. Three completed successfully and one remained technically unresolved. We therefore report the amendment denominator as 3 successful / 4 valid branches, retain the failed branch in the revision record, and avoid presenting the amendment as complete.

### Correction

> Review identified an analysis defect that affected the original evidence rather than adding a new sensitivity branch. We preserved the superseded record, corrected the defect, reran all materially affected analyses, and identified the manuscript claims and tables that changed. The corrected record should not be described as an ordinary robustness amendment.

### Endpoint change

> The requested analysis targets a different scientific endpoint. We therefore did not merge it into the original endpoint denominator. Where reported, the additional endpoint is identified as a separate post-review analysis with its own specification and execution record.

### No analytical change

> We considered the requested analysis but did not add it to the audit because it changes the target estimand rather than probing uncertainty around the submitted endpoint. We clarified this boundary in the revised Methods and limitations and preserved the reviewer item and rationale in the revision record.

These are wording patterns, not mandatory language. Replace the denominators, locations, and rationale with the actual revision record.

## Do not collapse temporal layers

Avoid statements such as:

- “Twelve analyses were pre-specified” when eight were submitted and four were added after review;
- “All analyses were successful” when one valid reviewer-requested branch failed;
- “We corrected the analysis” when the work was actually an optional sensitivity amendment;
- “The result was unchanged” without stating which endpoint and denominator were compared.

Prefer explicit temporal wording:

> The submitted audit completed 8 / 8 valid branches. After peer review, a separately documented sensitivity amendment completed 4 / 4 additional branches.

## Response-letter evidence table

A compact table can prevent drift between the response letter and the archive:

| Reviewer item | Category | Outcomes already seen? | Submitted evidence | Post-review evidence | Manuscript location | Archive location |
|---|---|---:|---|---|---|---|
| R1-C2 | clarification | yes | 8 / 8 | no new execution | Methods | decision log |
| R1-C4 | sensitivity amendment | yes | 8 / 8 | 4 / 4 | Methods + Results + S7 | round-1/R1-C4/ |
| R1-C6 | endpoint amendment | yes | 8 / 8 original endpoint | separate endpoint record | Supplement | round-1/R1-C6/ |

The table documents provenance. It does not by itself establish that any requested analysis was scientifically necessary.

## Revision package checklist

Before resubmission, verify that:

- every reviewer item has a stable identifier;
- response categories match the actual analytical action;
- outcome-inspection timing is recorded for new decisions;
- submitted and post-review denominators are not combined into a false pre-specification count;
- valid failed branches remain visible;
- corrections preserve the superseded record;
- new endpoints have their own denominator;
- response-letter claims match the revised manuscript;
- manuscript claims match the archived evidence;
- exact software identity is recorded for materially affected analyses.

## Continue with

Use the [reviewer-requested amendments guide]({{ '/docs/guides/reviewer-requested-amendments/' | relative_url }}) to classify and preserve new work, then work through the [revision response package example]({{ '/docs/examples/revision-response-package/' | relative_url }}) for a complete synthetic response letter, manuscript-change log, and revision archive handoff.

<div class="callout warning">
<strong>Do not use the response letter to rewrite history.</strong>
The final publication record may contain stronger, weaker, or simply more qualified evidence than the submitted manuscript. Preserve that progression explicitly rather than making post-review decisions appear as though they were part of the original declaration.
</div>
