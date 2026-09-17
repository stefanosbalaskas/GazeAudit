---
title: Revision-package quickstart
description: Synthetic end-to-end quickstart for creating, populating, validating, and handing off a reviewer-revision provenance package with the real GazeAudit CLI.
kicker: Example · Peer review
permalink: /docs/examples/revision-package-quickstart/
search_category: Examples
search_keywords: revision package quickstart reviewer response cli amendment denominator evidence map validate synthetic
---

# Revision-package quickstart

This compact example uses the real `gazeaudit-revision-package` CLI to create and validate a reviewer-revision provenance package. Every reviewer item, denominator, endpoint, manuscript location, and file path below is **synthetic teaching material**.

<div class="callout info">
<strong>What this example proves.</strong>
It demonstrates the package structure, temporal provenance rules, governed CSV fields, and structural validator. It does not create empirical validation evidence and does not establish that any analysis or manuscript claim is scientifically valid.
</div>

## Scenario

Assume a submitted manuscript contained one endpoint, `E1`, with a complete robustness audit:

```text
submitted endpoint: E1
valid submitted specifications: 8
successful submitted specifications: 8
submitted execution: 8 / 8
```

Reviewer 1 then asks for three things:

- `R1-C2` — clarify how the submitted denominator was counted;
- `R1-C4` — rerun the same endpoint under a stricter quality threshold;
- `R1-C6` — add a second endpoint, `E2`.

The revision must preserve those as **three different record types** rather than merging them into one enlarged “pre-specified” analysis.

## 1. Create the package

```bash
gazeaudit-revision-package init \
  --output-dir revision-package \
  --project-slug synthetic-study \
  --review-round 1
```

The governed scaffold is:

```text
revision-package/
  README.md
  package-manifest.json
  submission/
    README.md
  revision/
    round-1/
      reviewer-response/
        response-matrix.csv
      change-manifest/
        version-change-manifest.csv
      amendments/
        README.md
      endpoint-amendments/
        README.md
  final/
    editor-facing-evidence-map.csv
    software-identity/
      environment.json
```

Do not treat this scaffold as a substitute for the real scientific artifacts. The CSV records should point to the evidence locations used by the project.

## 2. Record the reviewer-response matrix

The governed columns are:

```text
reviewer_item,category,results_already_seen,action,submitted_denominator,post_review_denominator,manuscript_location,archive_location,status
```

A compact synthetic matrix is:

| reviewer_item | category | results_already_seen | action | submitted_denominator | post_review_denominator | manuscript_location | archive_location | status |
|---|---|---|---|---|---|---|---|---|
| R1-C2 | documentation_clarification | not_applicable | clarify submitted denominator | 8 / 8 | none | Results ¶2 | submission/ | complete |
| R1-C4 | sensitivity_amendment | yes | stricter quality threshold | 8 / 8 | 4 / 4 | Results ¶4 | revision/round-1/amendments/R1-C4/ | complete |
| R1-C6 | endpoint_amendment | yes | add endpoint E2 | 8 / 8 E1 | separate E2 record | Supplement §S7 | revision/round-1/endpoint-amendments/R1-C6/ | complete |

The temporal interpretation is therefore:

```text
E1 submitted: 8 / 8
E1 post-review sensitivity amendment: 4 / 4
E2 post-review endpoint amendment: separate endpoint record
```

It is **not**:

```text
12 pre-specified E1 analyses
```

## 3. Record material version changes

The governed version-change columns are:

```text
change_id,category,results_already_seen,submitted_location,revised_location,evidence_added_or_regenerated,denominator_effect,claim_impact,status
```

One possible synthetic record is:

| change_id | category | results_already_seen | submitted_location | revised_location | evidence_added_or_regenerated | denominator_effect | claim_impact | status |
|---|---|---|---|---|---|---|---|---|
| R1-C2-A1 | documentation_clarification | not_applicable | Results ¶2 | Results ¶2 | none | none | wording clarified | complete |
| R1-C4-A1 | sensitivity_amendment | yes | none | Results ¶4 | stricter-threshold amendment | separate 4 / 4 post-review denominator | adds sensitivity evidence | complete |
| R1-C6-A1 | endpoint_amendment | yes | none | Supplement §S7 | E2 analysis | separate endpoint denominator | adds endpoint-specific result | complete |

The manifest explains **what changed and when**. It does not convert post-review work into submitted work.

## 4. Add the amendment evidence

For `R1-C4`, create a study-owned evidence location such as:

```text
revision-package/
  revision/
    round-1/
      amendments/
        R1-C4/
          amendment-record.md
          specifications.csv
          results.csv
```

Suppose all four valid amendment branches execute successfully. The response record remains `4 / 4`.

If only three execute and one valid branch fails technically, preserve:

```text
valid amendment specifications: 4
successful amendment specifications: 3
unresolved valid failures: 1
amendment execution: 3 / 4
status: incomplete
```

Do not delete the failed branch and report `3 / 3`.

## 5. Keep the endpoint amendment separate

For `R1-C6`, preserve `E2` under the endpoint-amendment layer:

```text
revision-package/
  revision/
    round-1/
      endpoint-amendments/
        R1-C6/
          endpoint-record.md
          results.csv
```

The response letter can state that `E2` was added during revision while the original `E1` robustness denominator remains unchanged.

## 6. Build the editor-facing evidence map

The governed columns are:

```text
claim_id,claim_component,temporal_status,supporting_evidence,manuscript_location,verification_status
```

A compact synthetic map is:

| claim_id | claim_component | temporal_status | supporting_evidence | manuscript_location | verification_status |
|---|---|---|---|---|---|
| C1 | original E1 robustness record | submitted | submission/ | Results ¶2 | verified |
| C2 | stricter-threshold sensitivity | post-review R1-C4 | revision/round-1/amendments/R1-C4/ | Results ¶4 | verified |
| C3 | added E2 result | post-review R1-C6 | revision/round-1/endpoint-amendments/R1-C6/ | Supplement §S7 | verified |

This map tells an editor or coauthor **where to look**. It does not rank evidence quality.

## 7. Validate the structural package

Run:

```bash
gazeaudit-revision-package validate --root revision-package
```

A structurally valid scaffold returns JSON containing:

```json
{
  "manifest_fingerprint_valid": true,
  "missing_paths": [],
  "problems": [],
  "scope": "structural_provenance_only",
  "valid": true
}
```

The validator exits with `0` for a structurally valid package and `2` when required paths are missing or the manifest is invalid.

## 8. Run the outsider reconstruction check

Before resubmission, ask a collaborator who did not run the analyses to recover these answers from the package alone:

1. What existed at submission?
2. Which reviewer item triggered each new analysis?
3. Had outcomes already been inspected?
4. What was the submitted `E1` denominator?
5. What was the post-review `E1` amendment denominator?
6. Where is the separate `E2` evidence?
7. Are any valid technical failures still visible?
8. Which manuscript locations changed?
9. Which evidence files support each final claim component?
10. Which GazeAudit/software identity produced the revision-stage record?

If the answers require private lab memory, the handoff is not yet independently reconstructable.

## 9. What to do next

Use the [peer-review revision checklist]({{ '/docs/guides/peer-review-revision-checklist/' | relative_url }}) before making changes, then the [peer-review revision toolkit]({{ '/docs/workspace/revision-toolkit/' | relative_url }}) for task routing. Use the [full reproducibility-package example]({{ '/docs/examples/reproducibility-package-cli/' | relative_url }}) when you want the deliberate break → detect → repair exercise, and [resubmission readiness]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) for the final handoff gate.

## Evidence boundary

This example is synthetic and does not modify GazeAudit's frozen empirical records. The authoritative protocol-bound outcomes remain GazeBase `incomplete`, Korthals `robust_negative`, and Pedrotti/de Chambrier `materially_fragile`.