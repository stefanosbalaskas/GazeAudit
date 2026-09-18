---
title: Reviewer-requested reanalysis worked example
description: Extend a synthetic submitted GazeAudit record with a reviewer-requested sensitivity analysis while preserving the original denominator, decision history, and manuscript provenance.
kicker: Example · Peer review
permalink: /docs/examples/reviewer-requested-reanalysis/
search_category: Example
search_keywords: reviewer revision amendment reanalysis sensitivity post review denominator response letter synthetic robustness
page_type: example
example_data: "Synthetic"
example_focus: "Peer review & publication"
example_reuse: "Post-review amendment workflow"
example_output: "Separate submitted and reviewer-requested evidence layers"
example_boundary: "Post-review analyses must not be relabelled as pre-specified."
---

# Reviewer-requested reanalysis worked example

This synthetic example shows how to answer a peer-review request **without rewriting the submitted audit as if the new analysis had been planned from the beginning**.

<div class="callout warning">
<strong>Illustrative evidence only.</strong>
All values, thresholds, reviewer comments, and manuscript sentences below are synthetic teaching material. They do not modify GazeAudit's frozen empirical validation records.
</div>

## Submitted audit

Assume the submitted manuscript evaluated a condition-B minus condition-A dwell-proportion endpoint across eight valid specifications.

The declared space crossed:

- missingness handling: `complete_case`, `bounded_interpolation`;
- minimum quality: `0.70`, `0.80`;
- sampling stride: `1`, `2`.

All eight valid branches executed successfully.

| spec_id | missingness | min_quality | stride | estimate |
|---|---|---:|---:|---:|
| S01 | complete_case | 0.70 | 1 | +0.042 |
| S02 | complete_case | 0.70 | 2 | +0.039 |
| S03 | complete_case | 0.80 | 1 | +0.035 |
| S04 | complete_case | 0.80 | 2 | +0.037 |
| S05 | bounded_interpolation | 0.70 | 1 | +0.031 |
| S06 | bounded_interpolation | 0.70 | 2 | +0.029 |
| S07 | bounded_interpolation | 0.80 | 1 | +0.026 |
| S08 | bounded_interpolation | 0.80 | 2 | +0.028 |

Submitted denominator: **8 / 8 valid specifications completed**.

The submitted Results sentence was:

> Across the eight declared valid specifications, estimates remained positive and ranged from 0.026 to 0.042 proportion points.

That sentence is bounded to the submitted specification space.

## Reviewer request

Reviewer 1 asks:

> Please repeat the robustness analysis under a stricter minimum-quality threshold of 0.90 to show whether the result depends on inclusion of lower-quality observations.

The request arrives **after the authors have seen all submitted results**.

The correct response is not to edit the original decision log and pretend `0.90` was always one of the declared levels.

## Amendment record

Create a post-review amendment:

```text
amendment_id: A01
review_round: R1
reviewer_item: R1-C4
results_already_seen: yes
request: add min_quality = 0.90 sensitivity branches
scientific_rationale: evaluate sensitivity to a stricter defensible quality rule
original_audit_changed: no
```

The amendment fixes `min_quality=0.90` and varies the two previously declared dimensions of missingness handling and sampling stride. That creates **4 added branches**.

## Amendment execution

| amendment_spec | missingness | min_quality | stride | status | estimate |
|---|---|---:|---:|---|---:|
| A01-01 | complete_case | 0.90 | 1 | success | +0.024 |
| A01-02 | complete_case | 0.90 | 2 | success | +0.021 |
| A01-03 | bounded_interpolation | 0.90 | 1 | success | +0.013 |
| A01-04 | bounded_interpolation | 0.90 | 2 | success | +0.010 |

Amendment denominator: **4 / 4 reviewer-requested branches completed**.

The new estimates are all positive, but their magnitude is smaller than the submitted range. That observation belongs to the amendment evidence.

## Do not retroactively change the original denominator

Incorrect reconstruction:

> Twelve pre-specified analyses were conducted.

That statement is false because four branches were introduced only after the reviewer request.

Correct reconstruction:

- submitted audit: **8 / 8** valid specifications;
- post-review Amendment A01: **4 / 4** added sensitivity specifications.

The revised manuscript may discuss the combined evidence, but it should preserve those two temporal layers.

## Response-to-reviewer wording

A transparent reply could state:

> We thank the reviewer for this suggestion. We added a post-review sensitivity analysis using a stricter minimum-quality threshold of 0.90. The original eight-specification audit is preserved unchanged. The reviewer-requested analysis is recorded separately as Amendment A01 and contains four added branches crossing missingness handling and sampling stride. All four branches completed successfully, with estimates ranging from 0.010 to 0.024 proportion points.

This directly answers the reviewer without misrepresenting the amendment as prospective.

## Revised Results wording

A bounded revision could state:

> The submitted audit contained eight declared valid specifications, all of which completed and produced positive estimates ranging from 0.026 to 0.042 proportion points. Following peer review, we added four sensitivity specifications using a stricter minimum-quality threshold of 0.90 (Amendment A01). These post-review estimates also remained positive but were smaller, ranging from 0.010 to 0.024 proportion points.

This wording separates **directional consistency** from **magnitude sensitivity** and preserves the timing of the additional analysis.

## Revised limitation

The revision should not imply that the extra threshold exhausts quality-related uncertainty:

> The reviewer-requested amendment evaluated one additional quality threshold. It does not establish robustness to all possible quality definitions, exclusion policies, or measurement-error assumptions.

## Archive structure

A reviewer-friendly revision archive could look like:

```text
revision-round-1/
  submitted-record/
    decision-log.md
    specifications.csv
    execution-status.csv
    results.md
  amendments/
    A01-quality-090/
      amendment.md
      specifications.csv
      execution-status.csv
      robustness-summary.csv
      provenance.json
  revised-manuscript/
    methods.md
    results.md
    limitations.md
  response-to-reviewers/
    R1-C4.md
  manifest.json
```

The original files are preserved rather than overwritten by the post-review version.

## What if one amendment branch fails?

Suppose `A01-04` fails technically. The amendment denominator becomes:

- four added valid branches;
- three successful;
- one unresolved failure.

Do not report “three sensitivity analyses confirmed the result” while dropping the fourth branch. Keep the failed valid branch visible and bound any amendment-level conclusion accordingly.

## What if the reviewer requests a new endpoint?

A new endpoint is different from adding another threshold. For example, replacing dwell proportion with fixation count changes the scientific quantity being estimated.

In that case:

1. create a separate endpoint amendment;
2. define the endpoint explicitly;
3. define the specification space that applies to it;
4. do not mix its branches into the original endpoint denominator;
5. describe its post-review status in the manuscript and response letter.

## Reconstruction check

A future reader should be able to answer all of these from the archive alone:

- What analysis supported the submitted manuscript?
- Which reviewer item triggered A01?
- Had the original results already been inspected? **Yes.**
- How many original valid branches existed? **8.**
- How many branches were added after review? **4.**
- Were any original files overwritten? **No.**
- Did the amendment preserve direction? **In this synthetic example, yes.**
- Did magnitude change? **Yes; the amendment estimates were smaller.**

If those answers require private correspondence or memory, the revision record is incomplete.

## Continue with

- [Reviewer-requested amendments guide]({{ '/docs/guides/reviewer-requested-amendments/' | relative_url }}) — apply the provenance rules to a real revision.
- [Manuscript readiness]({{ '/docs/guides/manuscript-readiness/' | relative_url }}) — verify that the revised manuscript and archive agree.
- [Reviewer reconstruction example]({{ '/docs/examples/reviewer-reconstruction/' | relative_url }}) — practise reconstructing the submitted record from the outside.
- [Reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) — preserve deterministic publication evidence.
