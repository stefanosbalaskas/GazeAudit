---
title: Revision reproducibility package worked example
description: A synthetic executable-style example that scaffolds a reviewer-revision package, records separate submitted and post-review evidence, demonstrates a missing-file failure, and validates the repaired structure.
kicker: Example · Revision package
permalink: /docs/examples/reproducibility-package-cli/
search_category: Examples
search_keywords: reproducibility package cli synthetic reviewer revision scaffold validate manifest response matrix evidence map failure repair
---

# Revision reproducibility package worked example

<div class="callout warning">
<strong>Illustrative evidence only.</strong>
All reviewer items, denominators, endpoints, file names, manuscript locations, and outcomes below are synthetic teaching material. Running the real CLI in this example tests package structure; it does not create empirical validation evidence for GazeAudit or certify the synthetic scientific claims.
</div>

This example operationalizes the documentation's recurring review scenario:

- submitted endpoint `E1`: **8 / 8** valid specifications completed;
- reviewer item `R1-C2`: denominator clarification, no rerun;
- reviewer item `R1-C4`: four-branch stricter-threshold sensitivity amendment added after outcomes were seen, **4 / 4** completed;
- reviewer item `R1-C6`: new endpoint `E2`, stored separately from the original `E1` denominator.

The temporal record remains:

> **8 / 8 submitted + 4 / 4 post-review**, plus a separate post-review `E2` endpoint record.

It is not **12 pre-specified analyses**.

## Step 1 — scaffold the revision package

Run:

```bash
gazeaudit-revision-package init \
  --output-dir synthetic-revision \
  --project-slug synthetic-review-study \
  --review-round 1
```

The command creates nine governed scaffold files and prints a deterministic package-manifest fingerprint.

```text
synthetic-revision/
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

The generated `environment.json` records the software environment at scaffold creation. It is not a substitute for preserving the exact software identity used to execute earlier submitted analyses if those analyses were run in a different environment.

## Step 2 — preserve the submitted record

Assume the immutable submission evidence is copied or referenced under the project's submitted layer:

```text
submission/
  manuscript-v1.pdf
  submitted-analysis/
    specifications.csv
    effect-stability.csv
    marginal-sensitivity.csv
  submitted-software/
    environment.txt
```

The historically correct denominator is:

```text
submitted endpoint: E1
valid submitted specifications: 8
successful submitted specifications: 8
execution: 8 / 8
```

Nothing added during review changes what existed at submission.

## Step 3 — populate the response matrix

The scaffold starts with a header-only `response-matrix.csv`. Add the three synthetic reviewer items:

```csv
reviewer_item,category,results_already_seen,action,submitted_denominator,post_review_denominator,manuscript_location,archive_location,status
R1-C2,documentation_clarification,not_applicable,clarify submitted denominator,8 / 8,none,Results paragraph 2,submission/,complete
R1-C4,sensitivity_amendment,yes,run stricter quality threshold,8 / 8,4 / 4,Results paragraph 4,revision/round-1/amendments/R1-C4/,complete
R1-C6,endpoint_amendment,yes,add endpoint E2,8 / 8 E1,separate E2 record,Supplement S7,revision/round-1/endpoint-amendments/R1-C6/,complete
```

The response matrix now makes timing and denominator relationships explicit rather than leaving them to prose.

## Step 4 — populate the version-change manifest

Add stable change IDs:

```csv
change_id,category,results_already_seen,submitted_location,revised_location,evidence_added_or_regenerated,denominator_effect,claim_impact,status
R1-C2-D1,documentation_clarification,not_applicable,Results paragraph 2,Results paragraph 2,,unchanged,clarification,complete
R1-C4-A1,sensitivity_amendment,yes,not present,Results paragraph 4,revision/round-1/amendments/R1-C4/,4 / 4 post-review branches added separately,expanded with post-review sensitivity evidence,complete
R1-C6-E1,endpoint_amendment,yes,not present,Supplement S7,revision/round-1/endpoint-amendments/R1-C6/,different endpoint,endpoint-specific,complete
```

The `R1-C4-A1` row does not pretend that the new branches were available before review. `R1-C6-E1` does not merge `E2` into the `E1` robustness denominator.

## Step 5 — add amendment evidence

Create the actual amendment directories referenced by the matrix:

```text
revision/round-1/amendments/R1-C4/
  specification-declaration.json
  specifications.csv
  effect-stability.csv
  amendment-notes.md
  software-identity.txt

revision/round-1/endpoint-amendments/R1-C6/
  endpoint-definition.md
  results.csv
  software-identity.txt
```

For `R1-C4`, the synthetic execution record is:

```text
valid amendment specifications: 4
successful amendment specifications: 4
unresolved valid failures: 0
execution: 4 / 4
results already seen before amendment design: yes
```

## Step 6 — map final claims back to evidence

Populate `final/editor-facing-evidence-map.csv`:

```csv
claim_id,claim_component,temporal_status,supporting_evidence,manuscript_location,verification_status
C1,original E1 robustness record,submitted,submission/submitted-analysis/,Results paragraph 2,verified
C2,stricter-threshold sensitivity,post-review R1-C4,revision/round-1/amendments/R1-C4/,Results paragraph 4,verified
C3,added E2 result,post-review R1-C6,revision/round-1/endpoint-amendments/R1-C6/,Supplement S7,verified
```

The evidence map tells an outsider where to look. It does not decide whether any claim is scientifically convincing.

## Step 7 — validate the intact package

Run:

```bash
gazeaudit-revision-package validate --root synthetic-revision
```

Expected structural result:

```json
{
  "manifest_fingerprint_valid": true,
  "missing_paths": [],
  "problems": [],
  "scope": "structural_provenance_only",
  "valid": true
}
```

The command exits `0`.

## Step 8 — deliberately break the governed structure

Delete the scaffold marker:

```text
revision/round-1/amendments/README.md
```

Run validation again:

```bash
gazeaudit-revision-package validate --root synthetic-revision
```

Now the validator exits `2` and retains the exact missing governed path in the result:

```json
{
  "missing_paths": [
    "revision/round-1/amendments/README.md"
  ],
  "problems": [
    "required package files are missing"
  ],
  "scope": "structural_provenance_only",
  "valid": false
}
```

The validator does not infer that an amendment folder is unnecessary because the remaining files look plausible. Missing governed structure remains visible.

## Step 9 — repair the structure

Restore the amendment README or explicitly regenerate the known scaffold after preserving all project evidence. Then rerun validation.

A successful structural validation means the expected package contract is intact again. It does **not** mean the `R1-C4` analysis is correct, exhaustive, or persuasive.

## Failure variant — 3 successful / 4 valid

Suppose `R1-C4` instead had one unresolved technical failure:

```text
valid amendment specifications: 4
successful amendment specifications: 3
unresolved valid failures: 1
execution: 3 / 4
status: incomplete
```

The package should preserve that record. Do not remove the failed valid branch and change the denominator to `3 / 3`.

The response matrix should change `status` from `complete` to `incomplete`, and the reviewer response should state the unresolved failure explicitly.

A structurally valid folder can still contain an analytically incomplete amendment. **Structure and scientific completeness are different questions.**

## Correction variant

If review uncovers a defect in the submitted `E1` analysis, do not place the corrected result beside `R1-C4` as if it were just another sensitivity branch.

Preserve:

```text
submission/
  superseded-submitted-analysis/
revision/round-1/
  corrections/
    R1-CX/
      defect-record.md
      corrected-analysis/
      affected-claims.csv
```

Then add a `correction` row to the version-change manifest linking the superseded evidence, defect, regenerated results, and changed manuscript claims.

The scaffold deliberately does not erase or reclassify the superseded submitted record.

## What the example demonstrates

After the exercise, an outsider can recover:

1. what evidence existed at submission;
2. which reviewer items caused new work;
3. whether outcomes had already been inspected;
4. which denominator belongs to each temporal layer;
5. why the added endpoint remains separate;
6. whether a valid amendment branch failed;
7. which manuscript locations changed;
8. where the final claim-supporting evidence lives;
9. whether the package manifest and expected structure are intact.

The exercise does **not** demonstrate that the synthetic analyses are scientifically valid or publication-worthy.

## Continue the workflow

- [Revision reproducibility package guide]({{ '/docs/guides/reproducibility-package/' | relative_url }}) — command and field reference.
- [Reviewer response letter]({{ '/docs/guides/reviewer-response-letter/' | relative_url }}) — bounded response wording.
- [Version-change manifest]({{ '/docs/guides/version-change-manifest/' | relative_url }}) — revision taxonomy and supersession rules.
- [Resubmission readiness]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) — final manuscript/archive consistency gate.
- [Submission-to-accepted-record]({{ '/docs/examples/submission-to-accepted-record/' | relative_url }}) — full synthetic temporal record.
- [Publication/archive handoff]({{ '/docs/examples/publication-archive-handoff/' | relative_url }}) — durable end-state packaging.
