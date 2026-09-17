---
title: Resubmission readiness and editor handoff
description: Verify that the revised manuscript, reviewer responses, post-review analyses, change manifest, software identity, and final archive describe one reconstructable evidence record before resubmission.
kicker: Guide · Final handoff
permalink: /docs/guides/resubmission-readiness/
search_category: Guides
search_keywords: resubmission revision editor handoff readiness accepted record response letter change manifest archive evidence map final manuscript
---

# Resubmission readiness and editor handoff

Use this guide after the response letter and revision analyses are complete but **before** the revised manuscript is sent back to the journal or deposited as the final publication record.

The goal is not to decide whether the study is scientifically valid. The goal is narrower: verify that the editor, reviewers, coauthors, and future analysts can reconstruct **what was submitted, what changed after review, why it changed, what evidence was regenerated, and which record supports the final claim**.

<div class="callout warning">
<strong>Resubmission readiness is not an acceptance prediction or validity score.</strong>
A complete handoff can still contain uncertainty, unresolved technical limitations, or reviewer disagreement. Those conditions should remain visible rather than being converted into a pass/fail scientific judgement.
</div>

## The seven final-handoff gates

### 1. Every reviewer item has a stable disposition

Each reviewer item should end in one explicit state:

- clarification only;
- documentation change;
- correction;
- sensitivity amendment;
- analytical amendment;
- endpoint amendment;
- measurement amendment;
- no analytical change, with rationale;
- unresolved, with the remaining limitation stated.

Do not leave a response dependent on phrases such as “addressed in the manuscript” when the changed location, evidence file, or analytical status cannot be recovered.

### 2. Submitted and post-review evidence remain temporally distinct

The final record should preserve the submitted denominator and every post-review extension separately.

For example:

```text
submitted audit:        8 / 8 valid branches completed
review-round amendment: 4 / 4 added branches completed
final temporal record:  8 / 8 submitted + 4 / 4 post-review
```

Do **not** rewrite this as “12 pre-specified analyses.” The final manuscript may discuss the complete accumulated evidence, but the record must retain when each layer entered the study.

### 3. The revised manuscript and response letter agree

Check every analytical reviewer response against the revised manuscript:

| Check | Question |
|---|---|
| Endpoint | Does the response name the same endpoint reported in the revised manuscript? |
| Denominator | Do submitted, amendment, successful, failed, and invalid counts match? |
| Timing | Is post-review work identified as post-review wherever that distinction matters? |
| Direction and magnitude | Does the prose match the complete observed pattern rather than a preferred branch? |
| Limitations | Are unresolved failures or untested uncertainty dimensions still visible? |
| Location | Can the changed Methods, Results, figure, table, or supplement be found from the response? |

A response package is not synchronized when the response letter is accurate but the manuscript silently collapses the temporal evidence layers.

### 4. The version-change manifest is complete

Create a stable manifest describing the transition from the submitted version to the revised version. Use the [version-change manifest guide]({{ '/docs/guides/version-change-manifest/' | relative_url }}) so editorial text changes, documentation clarifications, corrections, and analytical amendments are distinguishable.

At minimum, each material change should record:

- a stable change ID;
- source reviewer item or author-initiated rationale;
- change category;
- submitted-version location;
- revised-version location;
- whether outcomes had already been inspected;
- evidence regenerated or added;
- claim impact;
- archive location.

### 5. The final archive can reproduce the revised claim

The archive should contain enough information to reconstruct the final manuscript without private lab memory. A practical structure is:

```text
submission/
  manuscript-v1/
  submitted-analysis/
  submitted-manifest/
revision/
  round-1/
    reviewer-response/
    change-manifest/
    amendments/
    revised-analysis/
final/
  manuscript-final/
  evidence-map/
  software-identity/
  publication-bundle/
```

This is illustrative, not a required filesystem schema.

If a correction replaced a submitted result, keep the superseded record and the correction record. Do not make the original evidence disappear merely because the corrected analysis is now authoritative.

### 6. Software identity and generated evidence are bound to the final version

Record the exact GazeAudit release or commit and any scientifically material external software versions used for the final evidence.

The final handoff should make clear whether:

- the submitted and revised analyses used the same software identity;
- an amendment required a different environment;
- a correction was caused by software, data, or analysis logic;
- regenerated tables or figures came from the final evidence bundle;
- fingerprints or checksums correspond to the files actually cited by the manuscript.

### 7. An outsider can follow the editor-facing evidence map

Create one compact map that links the editorial record to the evidence record.

| Editor-facing item | What should be recoverable |
|---|---|
| Reviewer response | reviewer item, response category, timing, action |
| Manuscript change | exact revised location and claim impact |
| Analysis evidence | submitted or post-review denominator and execution status |
| Archive evidence | file or directory supporting the response |
| Software identity | release/commit and material dependencies |
| Remaining limitation | unresolved failure, uncertainty, or scope boundary |

A useful final check is whether a collaborator who did not perform the analysis can answer: **“Why did this sentence change, which evidence supports it now, and when was that evidence introduced?”**

## Copy-ready final handoff record

```yaml
resubmission_round: 1
submitted_record:
  manuscript_version: v1
  execution: "8 / 8 valid branches completed"
revision_record:
  manuscript_version: v2
  amendment_execution: "4 / 4 added branches completed"
  results_already_seen: yes
final_claim_record:
  temporal_summary: "8 / 8 submitted + 4 / 4 post-review"
  unresolved_valid_failures: 0
  endpoint_changed: no
software:
  gazeaudit: "record exact release or commit"
editor_handoff:
  response_matrix: revision/round-1/reviewer-response/response-matrix.csv
  change_manifest: revision/round-1/change-manifest/version-change-manifest.csv
  evidence_map: final/evidence-map/editor-evidence-map.csv
```

Replace demonstration values with the study's actual record. Do not infer missing history from the final manuscript alone.

## Final resubmission checklist

Before sending the revision, verify that:

- [ ] every reviewer item has one stable disposition;
- [ ] submitted and post-review denominators remain separate;
- [ ] all technically failed valid branches remain visible;
- [ ] corrections preserve the superseded record;
- [ ] endpoint changes are not merged into the original endpoint denominator;
- [ ] response-letter claims match the revised manuscript;
- [ ] the version-change manifest covers every material analytical or reporting change;
- [ ] manuscript tables and figures trace to final evidence files;
- [ ] exact software identity is recorded;
- [ ] the final archive contains the response matrix, change manifest, evidence map, and publication bundle;
- [ ] limitations still describe unresolved uncertainty honestly;
- [ ] an outsider can reconstruct why the final claim differs from the submitted claim.

## What “accepted record” should mean here

In GazeAudit documentation, an **accepted record** is a temporal archive state used for teaching final handoff. It means the manuscript and evidence package have reached the version associated with the publication decision in the synthetic example. It does **not** mean the journal validated the scientific conclusion, and it does not create a new empirical validation result for GazeAudit.

Continue with the [submission-to-accepted-record worked example]({{ '/docs/examples/submission-to-accepted-record/' | relative_url }}) to see the full synthetic path from submitted audit through reviewer amendment, response package, version manifest, and final editor-facing evidence map.
