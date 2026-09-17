---
title: Revision response package worked example
description: A synthetic peer-review response package linking reviewer requests to amendment timing, separate denominators, manuscript edits, and archived revision evidence.
kicker: Example · Peer review
permalink: /docs/examples/revision-response-package/
search_category: Examples
search_keywords: reviewer response package rebuttal revision amendment denominator manuscript change log archive response letter synthetic
---

# Revision response package worked example

This worked example shows how a manuscript revision can remain reconstructable across the **response letter, revised manuscript, and revision archive**.

<div class="callout warning">
<strong>Illustrative evidence only.</strong>
All values and reviewer comments on this page are synthetic teaching material. They do not create or modify GazeAudit's frozen empirical validation records.
</div>

## Submitted record

Assume the submitted manuscript reported one scientific endpoint and a declared robustness audit with:

- **8 / 8 valid specifications completed**;
- all eight estimates in the same direction;
- no unresolved valid failures;
- the exact submitted decision log and software identity archived before peer review.

The submitted record remains recoverable after revision.

## Reviewer item R1-C2: clarify the denominator

**Reviewer request**

> Please clarify how many specifications were declared, valid, and successfully executed.

**Classification:** documentation clarification.

**Analytical action:** none. No specification was added, removed, or rerun.

**Response-letter wording**

> Thank you for highlighting this ambiguity. We have clarified that the submitted audit contained eight declared and valid specifications, all eight of which completed successfully. No analytical change was made in response to this comment. The clarification appears in the revised Methods and Results, and the original 8 / 8 execution record remains unchanged.

**Manuscript change**

Methods now states the declared and valid denominator explicitly. Results now reports `8 / 8 valid specifications completed` rather than “all analyses completed.”

**Archive change**

```text
revision/round-1/R1-C2/
  response-record.yml
  manuscript-change.md
```

No new results file is created because no analysis was rerun.

## Reviewer item R1-C4: stricter quality threshold

**Reviewer request**

> Please repeat the robustness analysis under a stricter quality threshold.

The request arrives after the submitted outcomes have already been inspected.

**Classification:** sensitivity amendment.

**Amendment declaration**

```yaml
review_round: 1
reviewer_item: R1-C4
category: sensitivity_amendment
results_already_seen: yes
submitted_execution: "8 / 8 valid branches completed"
amendment_space: "4 added branches under stricter quality threshold"
```

The four added branches are executed and all four complete successfully.

**Temporal evidence record**

| Layer | Valid branches | Successful | Failed | How reported |
|---|---:|---:|---:|---|
| Submitted audit | 8 | 8 | 0 | pre-review evidence |
| Reviewer-requested amendment | 4 | 4 | 0 | post-review evidence |

The final record is therefore **8 / 8 submitted + 4 / 4 post-review**. It is not “12 pre-specified analyses.”

**Response-letter wording**

> In response to this request, and after inspection of the submitted results, we added a separately documented four-branch sensitivity amendment using the stricter quality threshold. The original submitted audit remains 8 / 8 valid specifications completed. The reviewer-requested amendment completed 4 / 4 additional branches. We report the amendment separately in the revised Methods, Results, and Supplementary Table S7.

**Archive change**

```text
revision/round-1/R1-C4/
  amendment-record.yml
  specifications.csv
  robustness-summary.json
  response-record.yml
  manuscript-change.md
```

## Reviewer item R1-C6: use a different endpoint

**Reviewer request**

> Please repeat the analysis using total dwell time rather than the submitted endpoint.

Assume total dwell time is scientifically meaningful but targets a different estimand.

**Classification:** endpoint amendment.

The new endpoint is not inserted into the original eight-branch denominator. If the team decides to report it, it receives its own post-review declaration and execution record.

**Response-letter wording**

> We agree that total dwell time provides a useful complementary view, but it targets a different endpoint from the one submitted. We therefore did not merge it into the original robustness denominator. We report it as a separate post-review endpoint analysis in the Supplement, with its own specification and execution record.

This wording preserves agreement with the reviewer request without implying that two endpoints belong to one robustness denominator.

## What if one amendment branch fails?

Suppose the R1-C4 amendment had declared four valid branches but only three completed successfully.

The response package should then report:

- submitted audit: **8 / 8**;
- post-review amendment: **3 successful / 4 valid**;
- one unresolved valid amendment branch retained in the archive.

It should not say that the reviewer-requested sensitivity analysis was complete.

## Response matrix

The final response letter can summarize the revision as follows:

| Item | Category | Analytical change? | Submitted denominator | Post-review denominator | Main location |
|---|---|---:|---:|---:|---|
| R1-C2 | clarification | no | 8 / 8 | — | Methods + Results |
| R1-C4 | sensitivity amendment | yes | 8 / 8 | 4 / 4 | Methods + Results + S7 |
| R1-C6 | endpoint amendment | yes, separate endpoint | 8 / 8 original endpoint | separate record | Supplement |

## Manuscript change log

A compact change log makes the response package easier to audit:

```text
R1-C2
  Methods: declared/valid/successful denominator clarified
  Results: explicit 8 / 8 denominator added
  Analysis rerun: no

R1-C4
  Methods: reviewer-requested sensitivity amendment added
  Results: 4 / 4 post-review branches reported separately
  Supplement: Table S7 added
  Analysis rerun: yes, amendment only

R1-C6
  Methods: endpoint distinction clarified
  Supplement: separate endpoint analysis added
  Analysis rerun: yes, separate endpoint record
```

## Final archive layout

```text
submission/
  decision-log.md
  specifications.csv
  robustness-summary.json
  software-identity.txt

revision/
  round-1/
    response-matrix.csv
    R1-C2/
      response-record.yml
      manuscript-change.md
    R1-C4/
      amendment-record.yml
      specifications.csv
      robustness-summary.json
      response-record.yml
      manuscript-change.md
    R1-C6/
      endpoint-record.yml
      specifications.csv
      results.csv
      response-record.yml
      manuscript-change.md

publication/
  final-manuscript-change-log.md
  final-manifest.json
  fingerprints.txt
```

This layout is illustrative rather than a required filesystem schema. Its purpose is to preserve the distinction among **submitted evidence, reviewer-requested extensions, and the final publication record**.

## Reviewer reconstruction test

An outsider should be able to answer all of the following from the package alone:

1. What was the submitted endpoint?
2. How many submitted branches were valid and successful?
3. Which reviewer items changed the analysis?
4. Which decisions were introduced after outcome inspection?
5. What evidence belongs to the original endpoint versus a new endpoint?
6. Were any valid reviewer-requested branches unresolved?
7. Where did each revision appear in the manuscript?
8. Which exact files support the final claim?

If those answers require private lab knowledge, the response package is not yet reviewer-reconstructable.

## Continue with

Use the [reviewer response letter guide]({{ '/docs/guides/reviewer-response-letter/' | relative_url }}) for a reusable response structure, then use the [reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) to bind the final revision evidence into the publication archive.
