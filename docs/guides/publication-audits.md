---
title: Publication audit guide
description: Build deterministic robustness evidence with predeclared conclusion rules, structural-QC provenance, and fingerprints.
kicker: Guide · Reproducibility
---

# Publication audit guide

GazeAudit can package a robustness analysis into a deterministic evidence bundle that binds the scientific inputs, decision rule, specification table, recovery results, summary, methods wording, provenance, and report text.

The goal is not to make a result immutable by policy. The goal is to make later mutation **detectable** and the scientific decision process inspectable.

## Start with a predeclared conclusion rule

A `ConclusionRule` can define recovery using relative/absolute effect-error tolerance, direction recovery, and a minimum across-specification recovery fraction.

```python
from gazeaudit import ConclusionRule

rule = ConclusionRule(
    relative_tolerance=0.20,
    require_sign=True,
    minimum_recovery_fraction=0.90,
)
```

The rule does not optimise statistical significance and should not be tuned after seeing which settings make the conclusion look strongest.

## Build the audit bundle

```python
import pandas as pd

from gazeaudit import build_conclusion_audit_bundle

results = pd.DataFrame(
    {
        "method": ["hard", "probabilistic", "probabilistic"],
        "error_scale": [None, 0.5, 1.5],
        "estimate": [9.5, 10.2, 8.7],
    }
)

bundle = build_conclusion_audit_bundle(
    results,
    reference_effect=10.0,
    rule=rule,
    title="Example conclusion-robustness audit",
    endpoint="treatment-minus-control dwell",
    source_description="Synthetic known-truth validation fixture",
)
```

The values above are synthetic demonstration values.

## Bind structural-QC provenance when available

If the analysis dataset has a `StudyQCAudit`, turn it into a compact publication descriptor and pass that descriptor through the existing `metadata` channel:

```python
from gazeaudit import study_qc_publication_metadata

qc_metadata = study_qc_publication_metadata(qc_audit)

bundle = build_conclusion_audit_bundle(
    results,
    reference_effect=10.0,
    rule=rule,
    title="Example conclusion-robustness audit",
    endpoint="treatment-minus-control dwell",
    source_description="Synthetic known-truth validation fixture",
    metadata={"study_qc": qc_metadata},
)
```

The descriptor records the structural status, stable issue codes, study fingerprint, QC audit fingerprint, diagnostic count, and decision count. Because publication metadata already belongs to the scientific manifest, changing the bound QC audit changes the publication scientific fingerprint.

This integration is backward-compatible: publication bundles without structural-QC metadata retain the existing `gazeaudit-publication-audit-v1` schema and behavior.

<div class="callout info">
<strong>Why the audit fingerprint, not the manifest fingerprint?</strong>
The compact publication link binds the substantive structural evidence and researcher decisions. The QC manifest fingerprint additionally binds the software environment, which is preserved in the QC evidence directory but is not needed to redefine the publication's scientific identity.
</div>

## Understand the two publication fingerprints

The bundle exposes two different integrity concepts:

- **scientific fingerprint** — binds the scientific specification/results content, including supplied metadata such as structural-QC provenance;
- **bundle fingerprint** — additionally binds the recorded execution environment and full publication bundle.

This separation matters because scientific identity and execution identity answer different provenance questions.

```python
print(bundle.scientific_fingerprint)
print(bundle.bundle_fingerprint)
```

## Render methods and report text

The bundle can generate deterministic Markdown and methods wording:

```python
print(bundle.markdown)
print(bundle.manifest_json())
```

The publication layer is intended to reduce manual drift between what was analysed and what was reported. It does not decide whether the scientific design itself was appropriate.

## Verify later

```python
from gazeaudit import verify_publication_audit_bundle

verify_publication_audit_bundle(bundle)
```

Verification is designed to detect later mutation of bound specification, recovery, summary, methods, report, or manifest content. If structural-QC metadata was supplied, its descriptor is part of that bound scientific manifest.

## Real-data reference effects require justification

For known-truth simulation, `reference_effect` can be the known generating effect. For real data, GazeAudit does **not** infer the reference effect. If a conclusion-recovery design uses one, its meaning must be justified independently and before robustness outputs are inspected.

<div class="callout warning">
<strong>Avoid circular validation</strong>
Do not define the reference effect from the same robustness results that will later be judged against that reference. The audit machinery can preserve provenance; it cannot rescue a circular scientific rule.
</div>

## Recommended archive contents

A serious robustness publication should preserve, directly or by stable reference:

- software version/commit;
- source-data identity or source lock;
- structural-QC study fingerprint, audit fingerprint, diagnostics, and explicit decision log where applicable;
- predeclared specification space;
- invalid-combination rules;
- scientific endpoint definition;
- measurement-error assumptions where applicable;
- conclusion rule and reference effect rationale;
- complete specification results;
- sensitivity summaries;
- generated methods/report text;
- scientific and execution fingerprints;
- any frozen source/validation artifacts required to reproduce the run.

For a GazeAudit-native structural-QC archive, `write_study_qc_artifacts()` writes the report, row/group diagnostics, decisions, QC manifest, and byte-level artifact manifest as deterministic JSON/CSV files.

## Archive-before-reveal workflows

GazeAudit's own frozen case studies use stricter protocol/source/artifact controls than a generic user needs for every exploratory analysis. The general principle is still useful: where a result is intended to function as formal validation evidence, freeze source identity and scientific decision rules before revealing the final classification.

For implementation patterns, continue to the [data onboarding guide]({{ '/docs/guides/data-onboarding/' | relative_url }}), [reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}), and the package's [citation and reuse record]({{ '/docs/CITATION_AND_REUSE.html' | relative_url }}).
