---
title: Revision reproducibility package
description: Scaffold and structurally validate a reviewer-revision evidence package with separate submitted and post-review records, deterministic provenance, response matrices, version-change manifests, and an editor-facing evidence map.
kicker: Guide · Reproducibility
permalink: /docs/guides/reproducibility-package/
search_category: Guides
search_keywords: reproducibility revision package cli reviewer response manifest evidence map scaffold validate provenance amendment correction resubmission
---

# Revision reproducibility package

The `gazeaudit-revision-package` command turns the final review workflow into a concrete filesystem contract. It creates the small set of files needed to keep a submitted record, reviewer-response matrix, version-change manifest, post-review amendments, software identity, and final editor-facing evidence map reconstructable as separate layers.

<div class="callout warning">
<strong>Structural provenance only.</strong>
A passing package validation does not establish scientific validity, analytical completeness, manuscript quality, robustness, or publication readiness. It establishes that the expected structural record exists and that the package manifest has not silently changed.
</div>

## When to use it

Use the package after the submitted analysis record exists and peer review has created a need to preserve revision-stage evidence. It is especially useful when a revision includes one or more of:

- a documentation clarification with no rerun;
- a reviewer-requested sensitivity or analytical amendment;
- a new endpoint introduced during review;
- a measurement amendment;
- a technical failure that must remain visible in the amendment denominator;
- a correction that supersedes submitted evidence;
- a final editor-facing evidence map tying manuscript claims to files.

For the scientific reasoning behind those categories, read [reviewer-requested amendments]({{ '/docs/guides/reviewer-requested-amendments/' | relative_url }}) and the [version-change manifest guide]({{ '/docs/guides/version-change-manifest/' | relative_url }}) first.

## 1. Create the package

Install GazeAudit, then run:

```bash
gazeaudit-revision-package init \
  --output-dir revision-package \
  --project-slug synthetic-study \
  --review-round 1
```

The command prints a compact JSON receipt containing the action, package schema, deterministic manifest fingerprint, output directory, and number of required scaffold files.

The initial layout is:

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

This is a **revision provenance scaffold**, not a container for every raw or derived research file. The CSV rows should point to the real evidence locations used by the project.

## 2. Preserve the submitted layer

The `submission/` directory represents what existed at submission. Treat it as immutable history.

For example, if the submitted robustness record was:

```text
endpoint: E1
valid submitted specifications: 8
successful submitted specifications: 8
submitted execution: 8 / 8
```

then a later four-branch reviewer amendment does not change that historical statement. The accumulated record becomes:

> **8 / 8 submitted + 4 / 4 post-review**

Do not rewrite it as **12 pre-specified analyses**.

## 3. Fill the response matrix

`response-matrix.csv` starts with these governed columns:

```text
reviewer_item,category,results_already_seen,action,submitted_denominator,post_review_denominator,manuscript_location,archive_location,status
```

A compact synthetic record might contain:

| reviewer_item | category | results_already_seen | action | submitted_denominator | post_review_denominator | manuscript_location | archive_location | status |
|---|---|---|---|---|---|---|---|---|
| R1-C2 | documentation_clarification | not_applicable | clarify denominator | 8 / 8 | none | Results ¶2 | submission/ | complete |
| R1-C4 | sensitivity_amendment | yes | stricter quality threshold | 8 / 8 | 4 / 4 | Results ¶4 | revision/round-1/amendments/R1-C4/ | complete |
| R1-C6 | endpoint_amendment | yes | add endpoint E2 | 8 / 8 E1 | separate E2 record | Supplement §S7 | revision/round-1/endpoint-amendments/R1-C6/ | complete |

The matrix is a routing layer. It does not replace the underlying analysis artifacts.

## 4. Fill the version-change manifest

`version-change-manifest.csv` begins with:

```text
change_id,category,results_already_seen,submitted_location,revised_location,evidence_added_or_regenerated,denominator_effect,claim_impact,status
```

The supported change categories are:

```text
documentation_clarification
correction
sensitivity_amendment
analytical_amendment
endpoint_amendment
measurement_amendment
```

Use stable IDs such as `R1-C4-A1`. A sensitivity amendment added after outcome inspection should state that timing explicitly and retain its own denominator.

### Corrections need a supersession trail

A correction is not just another branch. If review exposes a coding, import, or analytical defect:

1. preserve the superseded submitted evidence;
2. record the defect and affected files;
3. regenerate every materially affected result;
4. identify which manuscript claims changed;
5. link superseded and corrected records in the change manifest.

Do not clean the archive by deleting the record that explains why the correction was needed.

## 5. Keep endpoint amendments endpoint-specific

A reviewer-requested endpoint belongs under `endpoint-amendments/` and should not be silently combined with the denominator for the submitted endpoint.

For example:

```text
submitted endpoint E1: 8 / 8
post-review sensitivity amendment for E1: 4 / 4
post-review endpoint E2: separate endpoint record
```

This preserves the meaning of each denominator.

## 6. Keep failed valid branches visible

Suppose a four-branch amendment produces three estimates and one valid technical failure. Record:

```text
valid amendment specifications: 4
successful amendment specifications: 3
unresolved valid failures: 1
amendment execution: 3 / 4
status: incomplete
```

Do not delete the failed branch and report `3 / 3`. The package structure exists to preserve the history, not to improve the appearance of completeness.

## 7. Build the editor-facing evidence map

`final/editor-facing-evidence-map.csv` starts with:

```text
claim_id,claim_component,temporal_status,supporting_evidence,manuscript_location,verification_status
```

Use it to map final manuscript components back to evidence layers:

| claim_id | claim_component | temporal_status | supporting_evidence | manuscript_location | verification_status |
|---|---|---|---|---|---|
| C1 | original E1 robustness record | submitted | submission/submitted-analysis/ | Results ¶2 | verified |
| C2 | stricter-threshold sensitivity | post-review R1-C4 | revision/round-1/amendments/R1-C4/ | Results ¶4 | verified |
| C3 | added E2 result | post-review R1-C6 | revision/round-1/endpoint-amendments/R1-C6/ | Supplement §S7 | verified |

The final map is a navigation aid. It does not rank evidence quality or certify the manuscript.

## 8. Validate the package

Run:

```bash
gazeaudit-revision-package validate --root revision-package
```

A valid scaffold returns JSON containing:

```json
{
  "manifest_fingerprint_valid": true,
  "missing_paths": [],
  "problems": [],
  "scope": "structural_provenance_only",
  "valid": true
}
```

The command exits with:

- `0` when the structural package is valid;
- `2` when required files are missing or the manifest is invalid.

A missing amendment record is not guessed away. It remains visible in `missing_paths`.

## 9. Understand the manifest fingerprint

`package-manifest.json` declares:

- the schema version;
- project slug;
- review round;
- exact required scaffold paths;
- recognized revision categories;
- temporal safeguards;
- a deterministic SHA-256 manifest fingerprint.

If the bound manifest content changes without recomputing the fingerprint, validation fails with a fingerprint mismatch. This detects structural manifest drift; it is **not** a checksum of every external scientific artifact referenced by the CSVs.

## 10. Overwrite behavior is deliberately narrow

Running `init` again without `--overwrite` fails if governed scaffold files already exist. This protects an existing revision package from accidental replacement.

With explicit `--overwrite`, GazeAudit rewrites only its known scaffold files. It does not recursively delete the directory and it does not remove unrelated researcher files.

Use overwrite to regenerate an empty template, not to erase revision history.

## 11. Multi-round review

Create another round with a different output directory or an explicitly governed project structure:

```bash
gazeaudit-revision-package init \
  --output-dir revision-package-round-2 \
  --project-slug synthetic-study \
  --review-round 2
```

The generated paths become `revision/round-2/...`. Do not fold round-2 decisions into round 1 if their timing matters to interpretation.

## What validation does not prove

A structurally valid package does **not** prove that:

- the specification space was scientifically defensible;
- every relevant uncertainty source was tested;
- the statistical model was appropriate;
- the reviewer-requested analysis supports the manuscript claim;
- an endpoint change should be interpreted together with the original endpoint;
- the manuscript is publication-ready;
- editorial acceptance validates the scientific result.

Use [resubmission readiness]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) for the final consistency gate and [publication audits]({{ '/docs/guides/publication-audits/' | relative_url }}) for deterministic scientific bundle provenance.

## Recommended route

1. [Reviewer-requested amendments]({{ '/docs/guides/reviewer-requested-amendments/' | relative_url }}) — classify the request and preserve timing.
2. [Reviewer response letter]({{ '/docs/guides/reviewer-response-letter/' | relative_url }}) — link the response to evidence and manuscript locations.
3. [Version-change manifest]({{ '/docs/guides/version-change-manifest/' | relative_url }}) — record what changed between manuscript versions.
4. **Revision reproducibility package** — scaffold and validate the revision record.
5. [Resubmission readiness]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) — run the final outsider consistency gate.
6. [Reproducibility-package worked example]({{ '/docs/examples/reproducibility-package-cli/' | relative_url }}) — deliberately break and repair a synthetic package.
7. [Submission-to-accepted-record]({{ '/docs/examples/submission-to-accepted-record/' | relative_url }}) — trace the complete temporal scientific record.
