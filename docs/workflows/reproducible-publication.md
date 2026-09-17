---
title: Reproducible publication workflow
description: Turn a GazeAudit robustness analysis into an auditable publication record with deterministic fingerprints and a reviewer-reconstructable manuscript handoff.
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
  <div class="workflow-step"><strong>Review, verify, and archive</strong><p>Test whether an independent reader can reconstruct the claim, then verify the bundle and cite the exact software identity.</p></div>
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

## 10. Report claims at the right scope

A robust conclusion under one frozen protocol does not imply universal robustness to every conceivable pipeline. A fragile conclusion under one protocol does not imply the source dataset is unusable.

Report:

- what was varied;
- what was held fixed;
- the endpoint;
- the conclusion rule, if any;
- the observed stability/fragility pattern;
- the execution denominator and unresolved valid failures;
- the protocol boundary;
- known untested uncertainty dimensions.

## 11. Cite reproducibly

For GazeAudit 0.1.0, cite the version DOI and record the software version or commit:

> Balaskas, S. (2026). *GazeAudit: Measurement uncertainty and inferential robustness for eye-tracking research* (Version 0.1.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.22757340

Use the concept DOI `10.5281/zenodo.22757339` only when you intentionally want a reference that resolves to the latest archived version.

## GazeAudit's own frozen evidence

The package's validation programme applies stronger archive-before-reveal controls to its canonical case studies. See the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) and [scientific methods]({{ '/docs/SCIENTIFIC_METHODS.html' | relative_url }}) for the authoritative records.
