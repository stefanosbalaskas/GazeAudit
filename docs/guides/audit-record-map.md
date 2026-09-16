---
title: Audit record map
description: Follow a GazeAudit study from source data and researcher-owned decisions through QC, declared specifications, robustness evidence, provenance, and publication claims.
kicker: Guide · Audit lineage
permalink: /docs/guides/audit-record-map/
search_category: Guide
search_keywords: audit record lineage provenance decisions outputs artifacts publication claims QC specifications robustness fingerprints manuscript archive
---

# Audit record map

A GazeAudit analysis is easier to review when the **lineage of the research record** is visible. This map shows how study inputs and researcher-owned scientific decisions connect to structural QC, declared specifications, execution evidence, robustness summaries, provenance, and the final publication record.

<div class="callout callout-info">
  <strong>This map is navigation, not scientific authority.</strong>
  GazeAudit can preserve the chain from a declared decision to an output. It does not decide which thresholds, exclusions, AOIs, perturbations, specifications, endpoints, or validity claims are scientifically justified for a study.
</div>

## The record in seven stages

<div class="workflow-steps">
  <div class="workflow-step">
    <strong>1 · Bind the study source</strong>
    <p>Preserve the canonical gaze table, coordinate system, units, participant/trial identity, and source provenance before analytical branching.</p>
  </div>
  <div class="workflow-step">
    <strong>2 · Record researcher decisions</strong>
    <p>Write down the endpoint, exclusions, thresholds, uncertainty assumptions, specification factors, perturbations, and invalid combinations that are scientifically defensible.</p>
  </div>
  <div class="workflow-step">
    <strong>3 · Inspect structural QC</strong>
    <p>Generate the study-QC record and investigate structural flags before they silently become scientific exclusions.</p>
  </div>
  <div class="workflow-step">
    <strong>4 · Execute the declared space</strong>
    <p>Run every valid predeclared specification and preserve technical failures instead of deleting inconvenient branches after outcome inspection.</p>
  </div>
  <div class="workflow-step">
    <strong>5 · Summarise robustness</strong>
    <p>Inspect specification curves, effect stability, and sensitivity summaries as empirical descriptions of the declared analysis space.</p>
  </div>
  <div class="workflow-step">
    <strong>6 · Bind provenance and fingerprints</strong>
    <p>Record the exact software identity, manifests, source locks, scientific inputs/outputs, and bundle-level execution context needed to reconstruct the analysis.</p>
  </div>
  <div class="workflow-step">
    <strong>7 · Write the scoped claim</strong>
    <p>Report only what the frozen protocol and preserved evidence support, including the uncertainty dimensions that were not tested.</p>
  </div>
</div>

The stages are ordered for traceability, not because every study needs every GazeAudit method. Use the smallest audit layer that answers the actual methodological question.

## What moves through the record

<div class="audit-output-preview">
  <div class="audit-output-panel">
    <span>Study + decisions</span>
    <h3>Inputs establish the scientific contract.</h3>
    <div class="audit-file-tree" aria-label="Representative study and decision records">
      <code>canonical gaze table</code>
      <code>coordinate system + units</code>
      <code>participant / trial identity</code>
      <code>endpoint definition</code>
      <code>researcher-owned thresholds</code>
      <code>declared specification factors</code>
    </div>
    <p>Start with the <a href="{{ '/docs/guides/data-onboarding/' | relative_url }}">data-onboarding guide</a> or the <a href="{{ '/docs/planner/' | relative_url }}">Audit planner</a>.</p>
  </div>
  <div class="audit-output-panel">
    <span>Executed evidence</span>
    <h3>The audit keeps the whole declared space.</h3>
    <div class="audit-file-tree" aria-label="Representative GazeAudit evidence artifacts">
      <code>study-qc/</code>
      <code>specifications.csv</code>
      <code>specification-curve.csv</code>
      <code>effect-stability.csv</code>
      <code>marginal-sensitivity.csv</code>
      <code>pairwise-sensitivity.csv</code>
    </div>
    <p>Use the <a href="{{ '/docs/guides/audit-output-bundle/' | relative_url }}">output-bundle explorer</a> to inspect what each artifact describes and what it cannot establish.</p>
  </div>
</div>

## Artifact → question → boundary

| Record layer | Representative artifact or record | Question it helps answer | Boundary to preserve |
|---|---|---|---|
| Study contract | canonical table + source identity | What data and units entered the audit? | Provenance does not establish data quality or causal validity. |
| Researcher decisions | endpoint, thresholds, factors, invalid combinations | What was scientifically declared before execution? | GazeAudit does not choose these decisions for the researcher. |
| Structural QC | `study-qc/` | Are there structural conditions that require investigation? | A flag is not a universal exclusion rule or validity judgement. |
| Specification execution | `specifications.csv` | What happened across every valid declared branch? | The table does not identify one preferred specification. |
| Robustness summary | `specification-curve.csv` and `effect-stability.csv` | How stable is the endpoint across the declared space? | Empirical quantiles and stability summaries are not confidence intervals, posterior probabilities, or causal evidence. |
| Sensitivity summary | `marginal-sensitivity.csv` and `pairwise-sensitivity.csv` | Which declared analytical choices coincide with larger endpoint movement? | Descriptive sensitivity is not causal variance decomposition or mechanism identification. |
| Publication record | manifest, methods/report text, fingerprints, software identity | Can collaborators reconstruct what was run and reported? | Reproducibility does not expand the scientific scope of the claim. |

## What may vary—and what should remain scientifically anchored

A robustness audit is useful only when the intended variation is distinguishable from accidental drift.

| Element | Typical role in the record |
|---|---|
| Scientific endpoint | Keep fixed across branches unless the protocol explicitly declares endpoint choice as a factor. |
| Specification factors | Vary only over defensible, declared alternatives. |
| Perturbation grid | Declare the tested uncertainty range before interpreting recovery. |
| Structural-QC policy | Record the rule and the researcher decision it triggers; do not convert a diagnostic into an automatic scientific exclusion. |
| Source identity | Preserve stable identifiers, checksums, manifests, or immutable retrieval metadata when material to the claim. |
| Software identity | Record the release or exact commit used for the analysis. |
| Reporting language | Match the evidence actually generated; do not upgrade descriptive robustness evidence into population or causal inference. |

<div class="callout callout-warning">
  <strong>No preferred-result shortcut.</strong>
  Do not filter the bundle after seeing the outcomes and then present the surviving rows as if they were the original declared analysis space. Technical failures, invalid combinations, and completeness limitations belong in the audit trail when they affect interpretation.
</div>

## From your first file to a publication record

<div class="card-grid">
  <article class="card">
    <div class="card-icon" aria-hidden="true">1</div>
    <h3>Run the practical path</h3>
    <p>Take a canonical CSV through study representation, structural preflight, declared alternatives, and saved evidence.</p>
    <p><a href="{{ '/docs/guides/first-real-audit/' | relative_url }}">First real audit →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">2</div>
    <h3>Read the generated bundle</h3>
    <p>Inspect the purpose and interpretation boundary of each saved artifact before selecting figures or prose for a manuscript.</p>
    <p><a href="{{ '/docs/guides/audit-output-bundle/' | relative_url }}">Output bundle →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">3</div>
    <h3>Bind the publication record</h3>
    <p>Preserve source identity, frozen choices, complete evidence, manifests, fingerprints, and exact software identity.</p>
    <p><a href="{{ '/docs/workflows/reproducible-publication/' | relative_url }}">Publication workflow →</a></p>
  </article>
</div>

## Use frozen evidence as a boundary check

GazeAudit's own [evidence map]({{ '/docs/case-studies/' | relative_url }}) demonstrates why lineage matters. The three canonical cases reach different protocol-bound outcomes because they ask different questions under different frozen rules. Their labels are not transferable scores for new datasets.

- **GazeBase** preserves an `incomplete` outcome because a predeclared completeness prerequisite failed.
- **Korthals** preserves `robust_negative` for the frozen AOI estimand under its measurement-error model.
- **Pedrotti/de Chambrier** preserves `materially_fragile` because the declared magnitude-and-direction recovery criterion failed under several perturbation families.

The practical lesson is not to seek one label. It is to preserve enough of the record that another researcher can see **what was fixed, what varied, what failed, what was summarised, and what claim followed**.

## Fast routes

- [Researcher workspace]({{ '/docs/workspace/' | relative_url }}) — project-level starting map.
- [Audit planner]({{ '/docs/planner/' | relative_url }}) — translate study conditions into governed method routes.
- [First real audit]({{ '/docs/guides/first-real-audit/' | relative_url }}) — run the practical CSV-to-evidence path.
- [Output-bundle explorer]({{ '/docs/guides/audit-output-bundle/' | relative_url }}) — inspect generated artifacts.
- [Reproducible publication]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) — build and verify the durable record.
- [Evidence map]({{ '/docs/case-studies/' | relative_url }}) — inspect frozen protocol-bound validation cases.
