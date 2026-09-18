---
title: Examples
description: Runnable synthetic and project-oriented examples for GazeAudit data preflight, researcher decisions, measurement uncertainty, robustness analysis, troubleshooting and recovery, sensitivity, result interpretation, reviewer reconstruction, post-review reanalysis, response packages, executable revision-package quickstarts, resubmission handoff, bounded reporting, and publication archive design.
kicker: Examples
---

# Examples

These examples are intentionally small. Demonstration datasets are **synthetic unless stated otherwise**; project-oriented examples are explicit about which parts must be replaced with study-specific decisions.

## Choose by task

<div class="card-grid">
  <article class="card">
    <div class="card-icon" aria-hidden="true">1</div>
    <h3>Bring your own gaze table</h3>
    <p>Start from a canonical CSV, inspect structural QC, declare alternatives, and write the complete audit bundle.</p>
    <p><a href="first-real-audit/">First real audit →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">2</div>
    <h3>Learn the robustness API</h3>
    <p>Run a deterministic 12-specification synthetic audit and inspect the specification curve, effect stability, and sensitivity summaries.</p>
    <p><a href="end-to-end-robustness/">End-to-end robustness →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">3</div>
    <h3>Recover a failed audit</h3>
    <p>Preserve invalid combinations and valid technical failures, diagnose the failing layer, repair the causal defect, and reconcile the execution denominator.</p>
    <p><a href="failed-audit-recovery/">Failed-audit recovery →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">4</div>
    <h3>Compare result patterns</h3>
    <p>Contrast complete/stable, magnitude-sensitive, sign-sensitive, and incomplete synthetic audits before choosing reporting language.</p>
    <p><a href="result-patterns/">Result-pattern reporting →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">5</div>
    <h3>Review the manuscript record</h3>
    <p>Act as an external reviewer: reconstruct the endpoint and denominator, find an unresolved valid branch, and repair over-strong manuscript wording without rewriting the audit.</p>
    <p><a href="reviewer-reconstruction/">Reviewer reconstruction →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">6</div>
    <h3>Respond to a reanalysis request</h3>
    <p>Extend a submitted 8/8 audit with a separately recorded 4/4 reviewer-requested amendment without relabelling post-review work as pre-specified.</p>
    <p><a href="reviewer-requested-reanalysis/">Reviewer-requested reanalysis →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">7</div>
    <h3>Assemble the response package</h3>
    <p>Link reviewer items to clarification, amendment, endpoint, manuscript-change, and archive records in one reconstructable revision package.</p>
    <p><a href="revision-response-package/">Revision response package →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">8</div>
    <h3>Run the revision-package quickstart</h3>
    <p>Create the governed reviewer-revision scaffold with the real CLI, populate the response/change/evidence records, and validate structural provenance.</p>
    <p><a href="revision-package-quickstart/">Revision-package quickstart →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">9</div>
    <h3>Trace the final handoff</h3>
    <p>Follow submitted evidence through post-review amendments, version changes, resubmission checks, and the final editor-facing evidence map.</p>
    <p><a href="submission-to-accepted-record/">Submission-to-accepted record →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">10</div>
    <h3>Prepare the publication handoff</h3>
    <p>Turn the synthetic audit record into a reviewer-friendly archive with decision history, complete execution status, manuscript wording, limitations, provenance, and a manifest.</p>
    <p><a href="publication-archive-handoff/">Publication/archive handoff →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">11</div>
    <h3>Look up the exact contract</h3>
    <p>Answer API, denominator, exception, non-finite endpoint, CLI, and frozen-label questions by moving through the factual reference layer.</p>
    <p><a href="reference-lookup-workflow/">Reference lookup →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">12</div>
    <h3>Search from ambiguity to authority</h3>
    <p>Use grouped search results to route a question into Guide, Example, Reference, or Evidence without turning ranking into a scientific recommendation.</p>
    <p><a href="search-to-contract/">Search → contract →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">13</div>
    <h3>Trace a function to its evidence boundary</h3>
    <p>Start from a public symbol and follow its stable deep link into the governed guide, runnable example, visual, and evidence context.</p>
    <p><a href="function-to-evidence/">Function → evidence →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">14</div>
    <h3>Inspect the live public interface</h3>
    <p>Compare generated signatures, revision-pinned source links, local Python introspection, and the research context for three representative public symbols.</p>
    <p><a href="source-api-inspection/">Source API inspection →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">15</div>
    <h3>Read a generated call contract</h3>
    <p>Practise required positional arguments, required keyword-only arguments, all-optional signatures, return annotations, and minimal call shapes without inventing study values.</p>
    <p><a href="api-call-contracts/">API call contracts →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">16</div>
    <h3>Verify a fresh installation</h3>
    <p>Create an isolated environment, install the public release, verify package identity, check representative imports, inspect one signature, and record the resolved environment.</p>
    <p><a href="install-smoke-check/">Install smoke check →</a></p>
  </article>
</div>

<div class="callout info">
<strong>Starting with your own data?</strong>
Use the <a href="first-real-audit/">first real audit example</a> for a CSV-oriented command-line path that writes structural-QC provenance and robustness tables. Use the <a href="study-preflight/">study preflight example</a> when you want to focus only on canonical mapping and structural diagnostics. Use the <a href="../guides/researcher-audit-checklist/">researcher audit checklist</a> before treating any demonstration value as a study-specific decision.
</div>

<div class="callout warning">
<strong>Audit blocked or failing?</strong>
Start with <a href="../guides/troubleshooting/">Troubleshooting GazeAudit</a> to identify the failing layer, then use <a href="failed-audit-recovery/">failed-audit recovery</a> to practise declared → valid → successful denominator accounting and a provenance-preserving technical rerun.
</div>

<div class="callout info">
<strong>Need a fact, not another workflow?</strong>
Use the <a href="../reference/">Reference hub</a> for API, CLI, evidence vocabulary, provenance, and validation authority. The <a href="reference-lookup-workflow/">reference lookup walkthrough</a> demonstrates when to stop reading procedural material and consult an exact contract instead.
</div>

## [Install → verify → first import](install-smoke-check/)

Run a software-only smoke check from a fresh virtual environment through package identity, representative public imports, one exact signature, a CLI entry point, and a minimal environment record.

**Use this when:** you want to prove that the intended software environment is available before beginning a scientific workflow.

## [Source-level API inspection](source-api-inspection/)

Use `GazeStudy`, `run_specs`, and `aoi_probabilities` to practise reading generated signatures, following revision-pinned source links, copying public imports, and comparing website metadata with local `inspect` output.

**Use this when:** you know the symbol and want to verify the exact callable interface before moving into a research workflow.

## [Function → example → evidence](function-to-evidence/)

Start from `run_specs`, `aoi_probabilities`, and `read_bids_eyetrack`, then follow each symbol through the deep-linkable [API pathways](../reference/api-pathways/) surface. The example shows why a linked frozen case or live contract is contextual evidence rather than a transferable scientific verdict.

**Use this when:** you know a public symbol and want to recover its guide, runnable example, visual, and evidence boundary without searching the site manually.

## [Search → contract walkthrough](search-to-contract/)

Start with four ambiguous synthetic questions—`run_specs NaN`, reviewer-revision commands, AOI uncertainty, and `robust_negative`—then use grouped search results to select the documentation type that answers the actual information need.

**Use this when:** you know the topic but are unsure whether you need procedural guidance, runnable context, exact reference, or frozen evidence authority.

## [Reference lookup walkthrough](reference-lookup-workflow/)

Use one fully synthetic scenario to look up declared versus valid specification counts, the actual exception behavior of `run_specs()`, the difference between a non-finite estimate and a null effect, exact reviewer-revision CLI syntax, and the boundary around frozen validation labels.

**Use this when:** you already know the research task but need to verify exactly what a public API, command, denominator term, or validation label means.

## [First real audit](first-real-audit/)

Run one practical script on deterministic demo data or a canonical eye-tracking CSV. The script combines `GazeStudy`, structural-QC fingerprints, a declared 12-specification robustness space, stability/sensitivity summaries, and output writing.

**Use this when:** you have a project file and want a concrete operational template to adapt before moving into study-specific methods.

## [Study preflight](study-preflight/)

Create a canonical `GazeStudy`, run `audit_study_qc()`, inspect stable issue codes, and export a compact QC table. The synthetic example deliberately contains one missing coordinate and a repeated timestamp.

**Use this when:** you are onboarding a new table and want a transparent structural check before measurement or robustness analysis.

## [End-to-end robustness audit](end-to-end-robustness/)

Run a complete 12-specification synthetic audit from `GazeStudy` construction through `PipelineSpace`, `run_specs()`, specification ordering, effect stability, marginal sensitivity, and pairwise interaction diagnostics.

**Use this when:** you want a copy-ready template showing how the main robustness pieces fit together in one executable analysis.

## [Failed-audit recovery](failed-audit-recovery/)

Work through a fully synthetic audit with **8 declared combinations, 7 valid specifications, and 6 initially successful executions**. The example preserves one predeclared-invalid combination outside the valid denominator, records one valid technical failure, diagnoses a branch-specific processor defect, reruns the same branch after a causal technical repair, and retains both the original failure and repaired execution in history.

**Use this when:** a declared audit stops or returns an incomplete result and you need to distinguish scientific validity from technical execution before changing anything.

## [Result-pattern reporting](result-patterns/)

Compare four synthetic audit outcomes side by side: direction and magnitude both relatively stable, direction stable but magnitude materially variable, sign-changing evidence, and incomplete execution. Each pattern includes bounded Results wording and explicit claims that remain unsupported.

**Use this when:** you have robustness outputs but need to decide what the complete pattern actually licenses you to say before moving into manuscript prose.

## [Decision-to-report worked example](decision-to-report/)

Use the deterministic 12-branch robustness demo to practise recording analytical choices before outcome inspection, reading the complete positive/negative/zero pattern, separating direction from magnitude, and translating the result into bounded Methods and Results language.

**Use this when:** you understand the code path but want to learn what a defensible interpretation and manuscript handoff look like.

## [Reviewer reconstruction](reviewer-reconstruction/)

Read an illustrative submission archive from the perspective of a reviewer who was not involved in the analysis. The example reconstructs one endpoint, an eight-combination declared space, one invalid combination, seven valid branches, six successful estimates, and one unresolved technical failure. It then rewrites an over-strong robustness sentence so the valid denominator remains visible.

**Use this when:** the manuscript draft looks finished but you want to test whether the claim can actually be reconstructed from the preserved record without private lab knowledge.

## [Reviewer-requested reanalysis](reviewer-requested-reanalysis/)

Extend a synthetic submitted **8 / 8** robustness audit with a stricter quality threshold requested after peer review. The amendment contributes **4 / 4** separately denominated branches and demonstrates revision timing, response-letter wording, revised Results and limitations, archive layout, failed-amendment handling, and why the combined record must not be described as “12 pre-specified analyses.”

**Use this when:** a reviewer asks for another exclusion, threshold, sensitivity branch, measurement assumption, or endpoint and you need a concrete model for extending the record without retrospectively rewriting the submitted audit.

## [Revision response package](revision-response-package/)

Follow three synthetic reviewer items from request to final record: a denominator clarification with no rerun, a four-branch stricter-threshold sensitivity amendment, and a different-endpoint request that is preserved outside the original denominator. The example provides response-letter wording, a response matrix, manuscript-change log, round-specific archive layout, and an outsider reconstruction test.

**Use this when:** the new analyses are complete but you need to ensure the response letter, revised manuscript, and archive all describe the same temporal evidence record.

## [Revision-package quickstart](revision-package-quickstart/)

Use the real `gazeaudit-revision-package init` and `validate` commands on a fully synthetic review round. The example creates the governed scaffold, populates the response matrix and version-change manifest, separates a post-review sensitivity amendment from a new endpoint, builds an editor-facing evidence map, preserves the `3 / 4` incomplete-amendment variant, and finishes with an outsider reconstruction check.

**Use this when:** you want the shortest executable path from reviewer requests to a structurally validated revision-provenance package before moving into the longer break → detect → repair exercise.

## [Submission-to-accepted-record worked example](submission-to-accepted-record/)

Continue the same synthetic revision through the final handoff. The example keeps the submitted **8 / 8** record, reviewer-requested **4 / 4** sensitivity amendment, separate endpoint amendment, response matrix, version-change manifest, resubmission-readiness gate, editor-facing evidence map, and publication-associated archive distinct.

It also shows the incomplete amendment variant (**3 successful / 4 valid**) and the correction path where superseded evidence must remain visible.

**Use this when:** the response package is complete and you want to test whether the final manuscript can be traced back through submitted, post-review, and final evidence layers without rewriting history.

## [Publication and archive handoff](publication-archive-handoff/)

Continue the synthetic exercise into an illustrative archive containing decision history, source identity, structural-QC evidence, complete specification/execution records, manuscript Methods/Results wording, limitations, software/provenance records, fingerprints, and a human-readable manifest.

**Use this when:** the analysis and interpretation are already clear and you want a concrete model for what a coauthor, reviewer, editor, or future analyst should be able to recover from the final handoff.

## [Analysis readiness](analysis-readiness/)

Work through executable policy, cohort-impact, repair, and specification-space decisions while keeping structural diagnostics separate from scientific exclusions.

**Use this when:** readiness policy and its effect on the analyzable cohort are part of the audit question.

## [AOI boundary uncertainty](aoi-boundary/)

Fit `GaussianGazeErrorModel`, define adjacent AOIs, estimate probabilistic membership, and compare hard versus uncertainty-aware assignment.

**Use this when:** you want to understand the measurement-error layer before building a larger analysis.

## [Specification curve](specification-curve/)

Create a synthetic results table, order estimates with `specification_curve()`, calculate `effect_stability()`, and screen factor sensitivity.

**Use this when:** you already have one estimate per defensible analytical specification and want to understand the robustness summaries.

## [Sampling sensitivity](sampling-sensitivity/)

Create a canonical `GazeStudy`, downsample the same participant-by-trial stream to controlled target rates, and evaluate one endpoint with `sampling_sensitivity_curve()`.

**Use this when:** sampling rate is a plausible source of inferential sensitivity.

## Suggested learning path

1. Start with the [first real audit](first-real-audit/) when you want to adapt GazeAudit to your own canonical CSV.
2. Use the [researcher audit checklist](../guides/researcher-audit-checklist/) and [decision-log template](../guides/audit-decision-log-template/) to replace demonstration choices with documented study-specific decisions.
3. Use the [study preflight](study-preflight/) when structural onboarding itself needs closer inspection.
4. Run the [end-to-end robustness audit](end-to-end-robustness/) to study the specification API in isolation.
5. If execution blocks, use [Troubleshooting GazeAudit](../guides/troubleshooting/) and practise the [failed-audit recovery](failed-audit-recovery/) workflow before interpreting an incomplete result.
6. Use the [interpret an audit result guide](../guides/interpret-audit-result/) to check denominator, endpoint, direction, magnitude, sensitivity, and untested uncertainty in the right order.
7. Compare the four [result-pattern examples](result-patterns/) before choosing bounded reporting language.
8. Work through [decision-to-report](decision-to-report/) to practise interpreting the deterministic 12-branch pattern without selecting a preferred branch after the fact.
9. Use [common audit mistakes and repairs](../guides/common-audit-mistakes/) to diagnose a weak decision trail or incomplete evidence record.
10. Apply the [manuscript readiness checklist](../guides/manuscript-readiness/) to the draft claim and archive.
11. Work through [reviewer reconstruction](reviewer-reconstruction/) to practise finding denominator and reporting gaps from outside the analysis team.
12. Use the [peer-review revision checklist](../guides/peer-review-revision-checklist/) before changing files in response to review.
13. Use the [reviewer-requested amendments guide](../guides/reviewer-requested-amendments/) when peer review adds analytical work.
14. Work through [reviewer-requested reanalysis](reviewer-requested-reanalysis/) to keep submitted and post-review denominators distinct.
15. Use the [reviewer response letter guide](../guides/reviewer-response-letter/) to connect each response to timing, evidence, manuscript locations, and archive locations.
16. Work through the [revision response package](revision-response-package/) to audit the response letter, manuscript-change log, and revision archive together.
17. Use the [version-change manifest guide](../guides/version-change-manifest/) to bind every material manuscript change to its rationale and evidence layer.
18. Run the [revision-package quickstart](revision-package-quickstart/) to create and structurally validate the governed package with the real CLI.
19. Apply the [resubmission readiness guide](../guides/resubmission-readiness/) to the final manuscript, response package, version manifest, and evidence map.
20. Work through [submission-to-accepted-record](submission-to-accepted-record/) to reconstruct the complete synthetic temporal handoff.
21. Build the [publication/archive handoff](publication-archive-handoff/) to practise packaging the complete record for review and preservation.
22. Run the [AOI boundary example](aoi-boundary/) if spatial measurement uncertainty is part of the question.
23. Use [sampling sensitivity](sampling-sensitivity/) when temporal resolution is part of the scientific question.
24. Move to the [first-study workflow](../workflows/first-study-audit/) when assembling the full research process.

## Visual convention

Plots in these example pages are explanatory figures. When they display synthetic values, the page and figure say so explicitly. Frozen empirical validation results remain in the [validation matrix](../VALIDATION_MATRIX.html) and case-specific result records.

- [Plot gallery]({{ '/docs/plots/' | relative_url }}) — 14 deterministic code-generated figures with source links.