---
title: Reproducible publication workflow
description: Turn a GazeAudit robustness analysis into an auditable publication record with deterministic fingerprints, reviewer-reconstructable manuscript evidence, traceable post-review amendments, an evidence-linked reviewer response, and a final resubmission handoff.
kicker: Workflow · Reproducibility
---

# Reproducible publication workflow

This workflow is for analyses intended to support a manuscript, validation record, benchmark, or other durable scientific claim.

<div class="callout callout-info">
  <strong>Need the lineage before the archive layout?</strong>
  Use the <a href="{{ '/docs/guides/audit-record-map/' | relative_url }}">audit record map</a> to trace how source data and researcher-owned decisions become QC, specification evidence, robustness summaries, provenance, fingerprints, and scoped publication claims.
</div>

## Workflow overview

<div class="workflow-steps">
  <div class="workflow-step"><strong>Identify the exact software</strong><p>Record GazeAudit version/commit and material external package versions.</p></div>
  <div class="workflow-step"><strong>Bind the source</strong><p>Preserve stable source identity, source locks, checksums, or immutable retrieval metadata where appropriate.</p></div>
  <div class="workflow-step"><strong>Freeze scientific choices</strong><p>Preserve the endpoint, specification space, validity rules, measurement assumptions, and conclusion rule before final classification.</p></div>
  <div class="workflow-step"><strong>Execute and preserve all outputs</strong><p>Keep the complete valid specification and sensitivity evidence rather than selected rows.</p></div>
  <div class="workflow-step"><strong>Build the audit bundle</strong><p>Generate deterministic methods, report, manifest, summaries, and fingerprints from the executed evidence.</p></div>
  <div class="workflow-step"><strong>Review, amend, respond, finalize, and archive</strong><p>Test whether an independent reader can reconstruct the claim; preserve post-review analyses as dated amendments; bind responses and version changes to evidence; verify the final bundle.</p></div>
</div>

## 1. Record software identity

For release 0.1.0:

```bash
python -m pip install gazeaudit==0.1.0
```

The version-specific archive DOI is [10.5281/zenodo.22757340](https://doi.org/10.5281/zenodo.22757340).

For analyses run from development `main`, record the exact Git commit rather than describing the code only as “latest”.

## 2. Preserve source identity

Depending on the source, preserve one or more of:

- DOI and version;
- immutable repository commit;
- download URL and retrieval timestamp;
- cryptographic checksum;
- source manifest;
- participant/file inventory;
- preprocessing provenance supplied by the upstream ecosystem.

The level of source locking should match the strength of the claim. Formal validation evidence benefits from stricter source control than an exploratory tutorial.

## 3. Freeze the scientific specification

Before final classification, preserve:

- endpoint definition;
- AOI geometry;
- measurement-error model and grouping;
- specification factors and levels;
- invalid-combination rules;
- perturbation grids;
- reference effect and rationale, if used;
- `ConclusionRule`, if used;
- expected software/version constraints when external packages are scientifically material.

## 4. Execute without post-hoc filtering

Preserve every valid specification that was declared. If a specification fails technically, record the failure and its reason rather than silently deleting it.

This distinction is central to the GazeBase validation record, where completeness itself is part of the scientific gate.

<div class="callout warning">
<strong>Before interpreting, audit the audit.</strong>
Use <a href="{{ '/docs/guides/common-audit-mistakes/' | relative_url }}">common audit mistakes and repairs</a> to check for outcome-informed specification changes, silent failed-branch deletion, endpoint drift, undocumented exclusions or repairs, overwritten amendments, and inferential over-reading of descriptive robustness summaries.
</div>

## 5. Build a conclusion audit bundle

```python
from gazeaudit import ConclusionRule, build_conclusion_audit_bundle

rule = ConclusionRule(
    relative_tolerance=0.20,
    require_sign=True,
    minimum_recovery_fraction=0.90,
)

bundle = build_conclusion_audit_bundle(
    results,
    reference_effect=reference_effect,
    rule=rule,
    title="Study robustness audit",
    endpoint="predeclared scientific endpoint",
    source_description="immutable source description",
)
```

Only use a reference effect when its scientific meaning is independently justified.

## 6. Preserve deterministic outputs

Useful bundle outputs include:

```python
bundle.summary
bundle.scientific_fingerprint
bundle.bundle_fingerprint
bundle.manifest_json()
bundle.markdown
```

The **scientific fingerprint** binds scientific inputs/outputs. The **bundle fingerprint** additionally binds recorded execution context.

## 7. Verify before publication

```python
from gazeaudit import verify_publication_audit_bundle

verify_publication_audit_bundle(bundle)
```

If bound content has changed, verification should fail rather than silently bless the modified bundle.

## 8. Archive methods and complete evidence

Recommended archive layout:

```text
analysis/
  protocol/
    scientific-specification.json
    source-lock.json
  results/
    specifications.csv
    sensitivity-curves.csv
    robustness-summary.json
  publication/
    manifest.json
    methods.md
    report.md
    fingerprints.txt
  environment/
    software-versions.txt
```

This is an illustrative structure, not a required GazeAudit filesystem schema.

For a more complete reviewer-facing example—including decision history, execution-status accounting, Methods/Results wording, limitations, provenance, fingerprints, and a human-readable archive manifest—see the [publication and archive handoff example]({{ '/docs/examples/publication-archive-handoff/' | relative_url }}). Its effect values are synthetic teaching material, not validation evidence.

## 9. Run the manuscript-readiness gate

Before submission, test whether the manuscript and archive can be reconstructed **without private lab context**.

Use the [manuscript readiness checklist]({{ '/docs/guides/manuscript-readiness/' | relative_url }}) to verify:

1. one reconstructable scientific endpoint;
2. the full declared/valid/successful/failed denominator;
3. researcher decisions separated from software diagnostics;
4. Results wording that matches the complete observed pattern;
5. agreement among manuscript, decision log, limitations, and archive manifest;
6. exact software identity and claim-supporting files.

Then work through the [reviewer reconstruction example]({{ '/docs/examples/reviewer-reconstruction/' | relative_url }}) to see why six directionally consistent estimates do not license a complete-space robustness claim when a seventh valid branch remains unresolved.

<div class="callout tip">
<strong>Use an outsider test.</strong>
Give the archive to someone who did not run the analysis. If they cannot recover the endpoint, denominator, failures, amendments, software identity, and evidence supporting the main claim without oral explanation, improve the record before submission.
</div>

## 10. Preserve reviewer-requested amendments

Peer review can legitimately add new sensitivity analyses, thresholds, exclusions, measurement assumptions, or endpoints. Those analyses belong in the final scientific record, but they should **extend the submitted audit rather than retrospectively rewrite it**.

Use the [reviewer-requested amendments guide]({{ '/docs/guides/reviewer-requested-amendments/' | relative_url }}) to record:

- the reviewer item and review round;
- whether the original outcomes had already been inspected;
- the scientific rationale for the added work;
- the amendment-specific specification space and execution status;
- the software identity used for the amendment;
- the relationship between amendment evidence and the revised manuscript claim.

Keep temporal denominators explicit. For example, a submitted `8 / 8` audit followed by a reviewer-requested `4 / 4` sensitivity amendment remains **8 / 8 submitted + 4 / 4 post-review**. It is not “12 pre-specified analyses.”

Work through the [reviewer-requested reanalysis example]({{ '/docs/examples/reviewer-requested-reanalysis/' | relative_url }}) for a complete synthetic revision exercise, including response-letter wording, revised Results and limitations, amendment archive structure, and failed-branch handling.

<div class="callout warning">
<strong>Corrections are not ordinary amendments.</strong>
If review uncovers a coding, import, or analysis defect, preserve the superseded record, document the defect, rerun all materially affected evidence, and identify which manuscript claims changed. Do not present a correction as merely another robustness branch.
</div>

## 11. Bind the reviewer response to the evidence

Once revision analyses are complete, keep the response letter synchronized with the manuscript and revision archive.

Use the [reviewer response letter guide]({{ '/docs/guides/reviewer-response-letter/' | relative_url }}) so each reviewer item records:

- the request and response category;
- whether the relevant decision was introduced after outcome inspection;
- the analytical action, including no-change decisions;
- the submitted and post-review denominators separately;
- the manuscript locations changed;
- the revision files that support the response.

Then work through the [revision response package example]({{ '/docs/examples/revision-response-package/' | relative_url }}) to see a clarification, a stricter-threshold sensitivity amendment, and a different-endpoint request carried through one synthetic response matrix and archive.

<div class="callout tip">
<strong>Response letters are part of the audit trail.</strong>
A reviewer should not have to infer whether a new analysis was submitted, added after review, corrected after a defect, or reported under a different endpoint. Make that temporal status explicit in the response itself.
</div>

## 12. Finalize the resubmission and editor handoff

Before sending the revised manuscript, bind the response package to the final version transition.

Use the [version-change manifest guide]({{ '/docs/guides/version-change-manifest/' | relative_url }}) to give each material manuscript change a stable identifier and distinguish:

- editorial text changes;
- documentation clarifications;
- corrections with superseded evidence;
- sensitivity and analytical amendments;
- endpoint and measurement amendments;
- reporting-boundary changes.

Then apply the [resubmission readiness and editor handoff guide]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) to verify that:

- every reviewer item has a stable disposition;
- submitted and post-review evidence remain temporally distinct;
- the response letter and revised manuscript use the same denominators and endpoint definitions;
- every manifest entry points to real revision evidence;
- software identity and fingerprints correspond to final claim-supporting files;
- unresolved failures and uncertainty remain visible;
- an outsider can follow the editor-facing evidence map from final claim to source evidence.

The [submission-to-accepted-record worked example]({{ '/docs/examples/submission-to-accepted-record/' | relative_url }}) demonstrates the entire synthetic sequence from an `8 / 8` submitted audit through a `4 / 4` review amendment, separate endpoint amendment, response matrix, version manifest, and final archive.

<div class="callout warning">
<strong>Editorial status is not scientific validation.</strong>
A manuscript can be editorially complete while still containing uncertainty, limitations, or disagreement. The final handoff records the evidence history; it does not turn acceptance into an empirical validation result.
</div>

## 13. Report claims at the right scope

A robust conclusion under one frozen protocol does not imply universal robustness to every conceivable pipeline. A fragile conclusion under one protocol does not imply the source dataset is unusable.

Report:

- what was varied;
- what was held fixed;
- the endpoint;
- the conclusion rule, if any;
- the observed stability/fragility pattern;
- the execution denominator and unresolved valid failures;
- any post-review amendment and its separate denominator;
- the response-letter relationship to the final manuscript claim;
- material version changes that affect claim scope;
- the protocol boundary;
- known untested uncertainty dimensions.

## 14. Cite reproducibly

For GazeAudit 0.1.0, cite the version DOI and record the software version or commit:

> Balaskas, S. (2026). *GazeAudit: Measurement uncertainty and inferential robustness for eye-tracking research* (Version 0.1.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.22757340

Use the concept DOI `10.5281/zenodo.22757339` only when you intentionally want a reference that resolves to the latest archived version.

## GazeAudit's own frozen evidence

The package's validation programme applies stronger archive-before-reveal controls to its canonical case studies. See the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) and [scientific methods]({{ '/docs/SCIENTIFIC_METHODS.html' | relative_url }}) for the authoritative records.
