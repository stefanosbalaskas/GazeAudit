---
title: Reviewer-requested amendments
description: Preserve the original GazeAudit record when peer review requests new exclusions, sensitivity checks, endpoints, or analytical branches, and document the added work as a dated amendment rather than rewriting history.
kicker: Guide · Peer review
permalink: /docs/guides/reviewer-requested-amendments/
search_category: Guide
search_keywords: reviewer revision amendment reanalysis sensitivity exclusion endpoint peer review response manuscript audit provenance post review
---

# Reviewer-requested amendments

Peer review often asks for another exclusion rule, sensitivity analysis, endpoint, perturbation, or robustness check. Those requests can strengthen a manuscript, but they should **extend the research record rather than silently replace the analysis that produced the submitted claim**.

<div class="callout warning">
<strong>Do not rewrite the original audit as if the reviewer-requested analysis had always been planned.</strong>
Preserve the submitted decision log, specification space, execution record, results, and software identity. Add a dated amendment that states what was requested, why it was added, when outcomes had already been seen, and which new evidence belongs to the amendment.
</div>

## First classify the request

Use the smallest category that accurately describes the requested work.

| Reviewer request | Record as | Typical consequence |
|---|---|---|
| Clarify wording or rationale without changing computation | documentation clarification | no new analytical denominator |
| Repair a coding/import defect | correction | rerun affected evidence and preserve the superseded record |
| Add another defensible level of an existing factor | sensitivity amendment | new amendment-specific branches |
| Add a new exclusion or preprocessing rule | analytical amendment | new researcher-owned decision plus new branches |
| Add a different scientific endpoint | endpoint amendment | usually a separate audit/result family |
| Add a new measurement assumption or AOI perturbation | measurement amendment | separate sensitivity evidence linked to the original claim |
| Reanalyse because the reviewer prefers one branch | not a robustness justification | do not replace the declared space with a preferred result |

The category determines how the new evidence should be described. It does **not** decide whether the reviewer request is scientifically justified.

## Preserve four layers

### 1. Submitted record

Keep the exact record that supported the submitted manuscript:

- source identity;
- original decision log;
- declared specification space;
- invalid-combination rules;
- execution-status table;
- robustness and sensitivity outputs;
- Methods/Results wording;
- software version or commit;
- archive fingerprints when used.

Do not edit this material merely to make the revised paper look prospectively cleaner.

### 2. Reviewer request

Record the request in a durable form:

```text
review_round: R1
reviewer_item: R1-C4
received: 2026-09-17
request: Add a sensitivity check excluding observations below an alternative quality rule.
results_already_seen: yes
```

The exact schema is illustrative. The key properties are identity, timing, and traceability.

### 3. Amendment decision

State what the research team decided to do and why:

```text
amendment_id: A01
linked_reviewer_item: R1-C4
status: accepted
scientific_rationale: evaluates sensitivity to an alternative defensible quality rule
changes_original_protocol: no
creates_new_evidence: yes
```

If the team declines or modifies a request, preserve that decision and rationale as well.

### 4. Amendment evidence

Write new outputs to a distinct amendment namespace, directory, or manifest rather than overwriting the submitted files.

```text
revision/
  submitted-record/
  amendments/
    A01-quality-sensitivity/
      amendment.md
      specifications.csv
      execution-status.csv
      robustness-summary.csv
      provenance.json
  revised-manuscript/
  response-to-reviewers/
```

The filenames are illustrative. The scientific requirement is separation between **submitted evidence** and **post-review evidence**.

## Denominator rules after peer review

A reviewer-requested branch does not retroactively change the denominator of the submitted audit.

Suppose the submitted audit contained 12 valid specifications and all 12 executed. A reviewer then requests four additional sensitivity branches.

Report them as two traceable sets:

- submitted audit: `12 / 12` valid branches executed;
- reviewer-requested amendment: `4 / 4` added branches executed.

Do not rewrite the original record as “16 specifications were predeclared.”

If the revised manuscript discusses all 16 together, explicitly distinguish the original and post-review evidence and explain the reason for the extension.

## When a correction is different

A genuine defect may require replacing an erroneous result. In that case:

1. preserve the superseded output;
2. document the defect and affected scope;
3. make the correction reproducible;
4. rerun all evidence materially affected by the defect;
5. state which manuscript claims changed;
6. do not present the correction as an ordinary sensitivity extension.

Corrections and reviewer-requested extensions answer different provenance questions.

## New endpoints need special care

A new endpoint can change the scientific question rather than merely stress-test the original one. Record:

- why the endpoint was added;
- whether it was requested after the original results were visible;
- whether it is confirmatory, sensitivity-oriented, descriptive, or exploratory in the revised manuscript;
- which specification space applies to it;
- whether multiplicity or other inferential considerations become relevant outside GazeAudit's robustness summaries.

Do not merge two distinct endpoints into one robustness denominator.

## Response-to-reviewer wording

A compact transparent structure is:

> In response to Reviewer 1, Comment 4, we added a post-review sensitivity analysis using an alternative quality rule. The submitted 12-specification audit is preserved unchanged. The added analysis is recorded as Amendment A01 and contributes four additional branches reported separately from the original denominator. The revised manuscript now distinguishes the submitted robustness evidence from the reviewer-requested extension.

This wording makes timing and provenance visible without implying that post-review work is scientifically inferior.

## Revised-manuscript wording

Avoid:

> We pre-specified 16 robustness analyses.

when four were added after review.

Prefer:

> The submitted audit evaluated 12 predeclared valid specifications. Following peer review, we added four sensitivity specifications using an alternative quality rule; these post-review analyses are reported separately as Amendment A01.

If the amendment materially changes the scientific interpretation, say so explicitly rather than allowing the response letter and manuscript to tell different stories.

## Amendment checklist

Before closing a reviewer-requested analysis, verify:

- the original submitted record is still recoverable;
- the reviewer item has a stable identifier;
- outcome visibility at the time of amendment is recorded;
- the scientific rationale is explicit;
- the amendment has its own denominator and execution status;
- failures remain visible;
- software identity is recorded for the amendment execution;
- revised wording distinguishes original from added evidence;
- limitations reflect any unresolved amendment branches;
- the response letter points to the exact added evidence.

## What this guide does not decide

It does not decide whether a reviewer request is scientifically appropriate, whether a new endpoint should be accepted, or whether an added analysis changes the substantive conclusion. Those remain researcher/editorial judgements. The purpose here is to make the temporal and evidential record auditable.

## Continue with

- [Reviewer-requested reanalysis example]({{ '/docs/examples/reviewer-requested-reanalysis/' | relative_url }}) — work through an original audit plus a post-review sensitivity amendment.
- [Manuscript readiness]({{ '/docs/guides/manuscript-readiness/' | relative_url }}) — verify that the revised manuscript and archive tell the same story.
- [Manuscript review path]({{ '/docs/workspace/manuscript-review-path/' | relative_url }}) — return to the compact interpretation-to-archive route.
- [Audit decision log template]({{ '/docs/guides/audit-decision-log-template/' | relative_url }}) — preserve researcher-owned decisions and amendment timing.
