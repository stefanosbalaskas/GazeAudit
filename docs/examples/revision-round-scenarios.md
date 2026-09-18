---
title: Revision-round routing scenarios
description: Synthetic peer-review scenarios showing clarification, correction, sensitivity amendments, incomplete post-review execution, endpoint amendments, response records, and revision-package handoff.
kicker: Worked revision scenarios
page_type: example
permalink: /docs/examples/revision-round-scenarios/
search_category: Example
search_keywords: reviewer revision scenarios rebuttal response amendment correction sensitivity endpoint failed branch denominator package synthetic peer review
example_data: "Synthetic"
example_focus: "Peer review & publication"
example_reuse: "Revision routing scenarios"
example_output: "Scenario-specific clarification, correction, amendment, and handoff routes"
example_boundary: "Scenario routes are teaching cases, not editorial rules."
---

# Revision-round routing scenarios

This page is a **synthetic teaching exercise** for choosing the correct revision route before editing a manuscript or rerunning an analysis. It does not create empirical validation evidence and does not determine whether a reviewer request is scientifically justified.

Start with the [peer-review revision route map]({{ '/docs/guides/revision-route-map/' | relative_url }}) if the request category is still unclear.

## Shared submitted record

Assume a manuscript was submitted with endpoint `E1` and a fully executed robustness space:

```text
submitted endpoint: E1
valid submitted branches: 8
successful submitted branches: 8
submitted execution record: 8 / 8
```

Peer review begins **after those outcomes have been inspected**. Any new analytical work therefore belongs to a post-review evidence layer.

## Scenario A — clarification, no rerun

**Reviewer request**

> Please explain whether the reported denominator includes all valid specifications.

**Correct route**

```text
category: documentation_clarification
submitted denominator: 8 / 8
post-review denominator: not applicable
analysis rerun: no
```

**Action**

1. verify the submitted execution record;
2. add a denominator sentence to Methods or Results;
3. cite the submitted specification table or execution summary;
4. record the manuscript location in the response matrix.

**Do not do this:** create a fictitious post-review analytical denominator merely because the prose changed.

A compact response record might be:

```csv
reviewer_item,category,results_already_seen,action,submitted_denominator,post_review_denominator,manuscript_location,archive_location,status
R1-01,documentation_clarification,yes,Clarified that all valid E1 branches were included,8/8,NA,Methods p.12,submission/specifications.csv,closed
```

## Scenario B — reviewer-requested sensitivity amendment

**Reviewer request**

> Please repeat the analysis under a stricter quality threshold.

**Correct route**

```text
category: sensitivity_amendment
endpoint: E1
submitted denominator: 8 / 8
post-review valid branches: 4
post-review successful branches: 4
post-review execution record: 4 / 4
```

Before running the amendment, record that the request occurred after outcome inspection and define the four valid branches. After execution, preserve the amendment as a separate temporal layer.

The final record is:

```text
E1 submitted: 8 / 8
E1 post-review sensitivity amendment: 4 / 4
```

It is **not**:

```text
12 pre-specified analyses
```

A version-change entry can state:

```csv
change_id,category,results_already_seen,submitted_location,revised_location,evidence_added_or_regenerated,denominator_effect,claim_impact,status
C-01,sensitivity_amendment,yes,Results p.18,Results p.19,revision/round-1/amendments/strict-threshold/,adds separate 4/4 post-review denominator,qualifies robustness wording,closed
```

## Scenario C — one valid post-review branch fails

Use the same four-branch sensitivity amendment, but now one valid branch encounters an unresolved technical failure.

The correct record is:

```text
valid post-review branches: 4
successful post-review branches: 3
amendment execution: 3 / 4
```

Do **not** report `3 / 3`. The failed branch was valid under the declared post-review amendment and remains part of the denominator.

A response entry should make the incomplete execution visible:

```csv
reviewer_item,category,results_already_seen,action,submitted_denominator,post_review_denominator,manuscript_location,archive_location,status
R1-02,sensitivity_amendment,yes,Ran stricter-threshold amendment; one valid branch failed technically,8/8,3/4,Results p.19,revision/round-1/amendments/strict-threshold/,incomplete
```

The manuscript should not convert the incomplete post-review result into a complete sensitivity claim.

## Scenario D — different endpoint

**Reviewer request**

> Please also test a dwell-time endpoint rather than the originally submitted endpoint.

Assume the submitted endpoint `E1` was a different scientific quantity. The requested dwell-time endpoint is `E2`.

**Correct route**

```text
category: endpoint_amendment
E1 submitted: 8 / 8
E1 post-review sensitivity amendment: 4 / 4
E2 post-review endpoint amendment: separate endpoint record
```

E2 must have its own denominator. Do not append its branches to the E1 denominator.

An editor-facing evidence map can keep the temporal and endpoint layers explicit:

```csv
claim_id,claim_component,temporal_status,supporting_evidence,manuscript_location,verification_status
CL-01,E1 submitted robustness,submitted,submission/e1-results.csv,Results p.18,verified
CL-02,E1 stricter-threshold sensitivity,post-review,revision/round-1/amendments/strict-threshold/,Results p.19,verified
CL-03,E2 dwell-time analysis,post-review,revision/round-1/endpoint-amendments/e2-dwell/,Supplement S4,verified
```

## Scenario E — correction rather than amendment

Assume the team discovers that one submitted file was produced with a coding defect.

**Correct route**

```text
category: correction
submitted evidence: retained as superseded
corrected evidence: generated and marked authoritative
claim impact: recorded explicitly
```

The correction record should answer:

- what was wrong;
- how it was detected;
- which submitted artifact is superseded;
- which corrected artifact is authoritative;
- whether the endpoint changed;
- whether the numerical result changed;
- whether the manuscript claim changed.

Do not delete the superseded evidence simply to make the final archive look cleaner. The revision record should preserve the change history.

## Assemble the synthetic review round

Once the routes are classified, scaffold the revision package with the real CLI:

```bash
gazeaudit-revision-package init \
  --output-dir revision-package \
  --project-slug synthetic-review \
  --review-round 1
```

Populate the generated response matrix, version-change manifest, amendment records, endpoint-amendment records, editor-facing evidence map, and software identity. Then validate the package:

```bash
gazeaudit-revision-package validate --root revision-package
```

The validator checks the governed package structure and manifest integrity. Passing validation establishes **structural provenance only**.

It does **not** establish that:

- the reviewer request was scientifically justified;
- the chosen amendment was the best analysis;
- the endpoint is valid;
- the result is robust;
- the manuscript wording is scientifically correct;
- the editor or reviewer should accept the revision.

## Outsider reconstruction exercise

Give the synthetic package to someone who did not perform the analysis and ask them to recover, without private explanation:

1. the submitted E1 denominator;
2. which reviewer item required no rerun;
3. which item added a new E1 sensitivity denominator;
4. whether every valid post-review branch succeeded;
5. which item introduced a separate endpoint;
6. which evidence was superseded by a correction;
7. where each response maps into the revised manuscript;
8. the exact software identity used for the revision.

If they cannot reconstruct those eight facts, the revision package is not yet a reliable handoff even if every analysis script runs.

## What the complete synthetic record should say

A bounded summary of the worked scenarios is:

```text
Submitted evidence: E1 8 / 8.
Post-review clarification: no new analytical denominator.
Post-review sensitivity amendment: E1 4 / 4, or 3 / 4 in the incomplete variant.
Post-review endpoint amendment: E2 recorded separately.
Correction path: superseded and corrected evidence both retained.
```

The record should never collapse those temporal layers into a single pre-specified denominator.

## Continue the workflow

- [Peer-review revision checklist]({{ '/docs/guides/peer-review-revision-checklist/' | relative_url }}) — run the compact gate before changing files.
- [Reviewer-requested amendments]({{ '/docs/guides/reviewer-requested-amendments/' | relative_url }}) — document analytical changes in detail.
- [Revision-package quickstart]({{ '/docs/examples/revision-package-quickstart/' | relative_url }}) — execute the governed package workflow.
- [Reviewer response letter]({{ '/docs/guides/reviewer-response-letter/' | relative_url }}) — bind each item to evidence and manuscript locations.
- [Resubmission readiness]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) — run the final handoff gate.

## Evidence boundary

All values and reviewer requests on this page are synthetic teaching material. They do not alter the frozen empirical records:

- GazeBase `incomplete`;
- Korthals `robust_negative`;
- Pedrotti/de Chambrier `materially_fragile`.