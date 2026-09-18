---
title: Submission-to-accepted-record worked example
description: A synthetic end-to-end revision example that preserves submitted evidence, reviewer-requested amendments, response records, version changes, and the final editor-facing archive as separate temporal layers.
kicker: Example · Final handoff
permalink: /docs/examples/submission-to-accepted-record/
search_category: Example
search_keywords: submission revision accepted record resubmission reviewer amendment response manifest editor archive synthetic example final handoff
page_type: example
example_data: "Synthetic"
example_focus: "Peer review & publication"
example_reuse: "Submission-to-handoff workflow"
example_output: "Temporally separated submitted, amended, and final editor-facing records"
example_boundary: "Revision chronology preserves provenance; it does not certify scientific correctness."
---

# Submission-to-accepted-record worked example

<div class="callout warning">
<strong>Illustrative evidence only.</strong>
Every numerical value, reviewer request, manuscript location, file name, and journal-stage event on this page is synthetic teaching material. This example does not create or modify GazeAudit's frozen empirical validation records.
</div>

This example continues the documentation's synthetic review exercise from a submitted **8 / 8** robustness audit through reviewer-requested work, the response package, a version-change manifest, resubmission, and a final publication-associated archive.

The teaching question is simple: **can a future reader recover which evidence existed at submission, which evidence was added during review, and exactly what supports the final manuscript?**

## Stage 1 — submitted record

Assume manuscript version `v1` was submitted with one endpoint, `E1`, and the following declared robustness record:

```text
submitted endpoint: E1
valid submitted specifications: 8
successful submitted specifications: 8
technically failed valid specifications: 0
submitted execution: 8 / 8
```

The submission archive contains:

```text
submission/
  manuscript-v1/
    manuscript-v1.pdf
  submitted-analysis/
    specifications.csv
    effect-stability.csv
    marginal-sensitivity.csv
  submitted-manifest/
    audit-decision-log.md
    manifest.json
    fingerprints.txt
  environment/
    software-versions.txt
```

At this point the correct temporal statement is simply **8 / 8 valid specifications completed at submission**.

## Stage 2 — review arrives

Three synthetic reviewer items require different responses.

| Reviewer item | Request | Classification |
|---|---|---|
| R1-C2 | Clarify which denominator appears in the robustness paragraph | documentation clarification |
| R1-C4 | Repeat the analysis under a stricter quality threshold | sensitivity amendment |
| R1-C6 | Add a second outcome requested by the reviewer | endpoint amendment |

The first response requires no rerun. The second and third introduce new post-review evidence after the submitted outcomes already existed.

## Stage 3 — documentation clarification

For `R1-C2`, the manuscript is revised to state explicitly that the submitted robustness space contained eight valid branches and all eight completed successfully.

No analytical evidence changes:

```yaml
change_id: R1-C2-D1
category: documentation_clarification
results_already_seen: not_applicable
denominator_effect: unchanged
claim_impact: clarification
status: complete
```

The response letter points to the revised Methods/Results location and the existing submitted specification table.

## Stage 4 — reviewer-requested sensitivity amendment

For `R1-C4`, the researchers add a stricter quality-threshold sensitivity analysis with four valid branches.

Synthetic amendment record:

```text
review round: 1
reviewer item: R1-C4
results already seen: yes
valid amendment specifications: 4
successful amendment specifications: 4
technically failed valid amendment specifications: 0
amendment execution: 4 / 4
```

The temporal record is now:

> **8 / 8 submitted + 4 / 4 post-review**

It is not **“12 pre-specified analyses.”** The accumulated evidence contains 12 successful branch estimates, but four were introduced during peer review.

The amendment is archived separately:

```text
revision/round-1/amendments/R1-C4/
  specification-declaration.yaml
  specifications.csv
  effect-stability.csv
  software-identity.txt
  amendment-notes.md
```

### Response-letter wording

A bounded response could state:

> In response to R1-C4, we added a four-branch stricter-threshold sensitivity analysis after the submitted results had been inspected. All four added branches completed successfully. The submitted 8 / 8 audit remains preserved separately; the revised record is therefore 8 / 8 submitted + 4 / 4 post-review.

The wording reports timing and completeness without pretending the reviewer-requested branch set belonged to the original declaration.

## Stage 5 — endpoint amendment

For `R1-C6`, the reviewer requests a different endpoint, `E2`.

The new endpoint can be useful, but it is not part of the original `E1` robustness denominator.

```yaml
change_id: R1-C6-E1
category: endpoint_amendment
results_already_seen: yes
submitted_endpoint: E1
added_endpoint: E2
denominator_effect: different_endpoint
claim_impact: endpoint_specific
status: complete
```

The revised manuscript reports `E2` in a separate subsection and the response letter explicitly states that the new endpoint **did not merge into the original E1 robustness denominator**.

## Stage 6 — build the response matrix

The response package now links each request to its timing, action, manuscript location, and evidence record.

| Item | Category | Timing | Analytical action | Manuscript location | Archive location |
|---|---|---|---|---|---|
| R1-C2 | documentation clarification | N/A | no rerun | Methods ¶3; Results ¶2 | submission/submitted-analysis/ |
| R1-C4 | sensitivity amendment | outcomes already seen | 4 added branches | Results ¶4; Table S5 | revision/round-1/amendments/R1-C4/ |
| R1-C6 | endpoint amendment | outcomes already seen | new endpoint E2 | Supplement §S7 | revision/round-1/endpoint-amendments/R1-C6/ |

This matrix is a routing layer. The evidence itself remains in the submitted and revision archives.

## Stage 7 — create the version-change manifest

The manifest records the manuscript transition rather than merely storing tracked changes.

```yaml
- change_id: R1-C2-D1
  category: documentation_clarification
  submitted_location: "Results paragraph 2"
  revised_location: "Results paragraph 2"
  evidence_added_or_regenerated: []
  denominator_effect: unchanged
  claim_impact: clarification
  status: complete

- change_id: R1-C4-A1
  category: sensitivity_amendment
  results_already_seen: yes
  submitted_location: "not present"
  revised_location: "Results paragraph 4; Supplementary Table S5"
  evidence_added_or_regenerated:
    - revision/round-1/amendments/R1-C4/specifications.csv
    - revision/round-1/amendments/R1-C4/effect-stability.csv
  denominator_effect: "4 / 4 post-review branches added separately"
  claim_impact: "expanded with new post-review evidence"
  status: complete

- change_id: R1-C6-E1
  category: endpoint_amendment
  results_already_seen: yes
  submitted_location: "not present"
  revised_location: "Supplement section S7"
  denominator_effect: different_endpoint
  claim_impact: endpoint_specific
  status: complete
```

Notice that the manifest preserves both **where** and **why** the revision changed.

## Stage 8 — run the resubmission-readiness gate

Before resubmission, the team verifies:

- R1-C2 is a clarification, not a hidden reanalysis;
- R1-C4 remains separately identified as post-review;
- the final temporal denominator remains **8 / 8 submitted + 4 / 4 post-review**;
- R1-C6 remains a separate endpoint record;
- response wording matches the revised manuscript;
- every revision file referenced by the response matrix exists;
- the exact software identity is preserved for the submitted and amendment evidence;
- the final limitations section still states untested uncertainty dimensions.

The record is ready for editorial handoff when these statements can be reconstructed from files rather than from team memory.

## Stage 9 — final editor-facing evidence map

After the revision process is complete, create a compact final map:

| Final claim component | Temporal status | Supporting evidence | Manuscript location |
|---|---|---|---|
| Original E1 robustness record | submitted | submission/submitted-analysis/ | Results ¶2 |
| Stricter-threshold sensitivity | post-review R1-C4 | revision/round-1/amendments/R1-C4/ | Results ¶4; Table S5 |
| Added E2 result | post-review R1-C6 | revision/round-1/endpoint-amendments/R1-C6/ | Supplement §S7 |
| Reviewer-response provenance | post-review | revision/round-1/reviewer-response/ | response letter |
| Version transition | post-review | revision/round-1/change-manifest/ | tracked manuscript + manifest |
| Final software and fingerprints | final | final/software-identity/ + final/publication-bundle/ | archive record |

The map lets an editor or future analyst travel from a final manuscript statement back to its temporal evidence layer.

## Stage 10 — final publication-associated archive

The synthetic final archive is:

```text
submission/
  manuscript-v1/
  submitted-analysis/
  submitted-manifest/
revision/
  round-1/
    reviewer-response/
      response-matrix.csv
      response-letter.pdf
    change-manifest/
      version-change-manifest.csv
    amendments/
      R1-C4/
    endpoint-amendments/
      R1-C6/
    manuscript/
      manuscript-v2.pdf
      tracked-changes-v1-to-v2.pdf
final/
  manuscript-final/
    manuscript-final.pdf
  evidence-map/
    editor-evidence-map.csv
  software-identity/
    software-versions.txt
  publication-bundle/
    manifest.json
    fingerprints.txt
```

This layout preserves the submitted record rather than allowing the final directory to replace it.

## What if one reviewer-requested branch failed?

Suppose the `R1-C4` amendment had produced only **3 successful / 4 valid** branches, with one unresolved valid amendment branch retained in the archive.

Then the final record should say:

```text
submitted: 8 / 8
post-review R1-C4 amendment: 3 successful / 4 valid
unresolved valid amendment failures: 1
```

The response letter should not say the reviewer-requested sensitivity analysis was complete. The unresolved branch remains part of the amendment denominator and should remain visible in the limitations and editor-facing evidence map.

## What if review uncovers a correction?

A correction creates a supersession trail rather than an ordinary added branch. Preserve:

1. the submitted evidence that contained the defect;
2. the defect description;
3. the corrected analysis;
4. the manuscript claims affected;
5. the new fingerprints or generated evidence;
6. the reason the corrected record is now authoritative.

Do not rewrite the archive so the corrected result appears to have been the original submission result.

## Reviewer reconstruction test

A person outside the analysis team should be able to answer all of the following from the archive:

1. What endpoint and denominator existed at submission?
2. Which reviewer items required no new analysis?
3. Which analyses were introduced after outcomes had been seen?
4. Which new branches belong to the original endpoint and which belong to a different endpoint?
5. Were all valid reviewer-requested branches completed?
6. Where is the response letter's supporting evidence?
7. Which manuscript sentences changed because of new evidence?
8. What exact software identity supports the final tables and figures?
9. Which records were superseded, if any?
10. Which limitations remain unresolved in the final manuscript?

If one of these questions requires oral explanation, improve the manifest or evidence map before calling the handoff reconstructable.

<div class="callout info">
<strong>Publication status is not scientific validation.</strong>
The term “accepted record” in this synthetic workflow describes the final temporal package associated with the editorial process. It does not imply that acceptance establishes the truth, validity, or generality of the scientific conclusion.
</div>

Continue with the [version-change manifest guide]({{ '/docs/guides/version-change-manifest/' | relative_url }}) for the provenance schema and the [resubmission readiness guide]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) for the final gate.
