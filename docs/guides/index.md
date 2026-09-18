---
title: Guides
description: Task-oriented GazeAudit guides for project setup, researcher decisions, data onboarding, uncertainty, robustness design, troubleshooting, result interpretation, manuscript readiness, peer-review revision checklists and amendments, reviewer responses, resubmission handoff, publication, and interoperability.
kicker: Guides
---

# Guides

The guides explain **how to design, govern, interpret, troubleshoot, review, revise, respond, finalize, and report** GazeAudit analyses. For copy-paste runnable demonstrations, use the [examples](../examples/).

## Choose by task

<div class="card-grid">
  <article class="card">
    <div class="card-icon" aria-hidden="true">1</div>
    <h3>Set up the research record</h3>
    <p>Separate source data, researcher-owned decisions, analysis code, generated evidence, and exact software identity before the project becomes difficult to audit.</p>
    <p><a href="project-starter/">Project starter →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">2</div>
    <h3>Govern researcher decisions</h3>
    <p>Use a before/during/after checklist and a copy-ready decision log so thresholds, exclusions, specifications, deviations, and reporting boundaries stay visible.</p>
    <p><a href="researcher-audit-checklist/">Researcher checklist →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">3</div>
    <h3>Interpret the completed audit</h3>
    <p>Check execution completeness first, then separate direction stability, magnitude sensitivity, descriptive factor alignment, and unresolved uncertainty before choosing manuscript wording.</p>
    <p><a href="interpret-audit-result/">Interpret an audit result →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">4</div>
    <h3>Check manuscript readiness</h3>
    <p>Verify that the endpoint, denominator, failures, decision trail, manuscript wording, limitations, archive manifest, and software identity can be reconstructed by someone outside the analysis team.</p>
    <p><a href="manuscript-readiness/">Manuscript readiness →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">5</div>
    <h3>Handle reviewer amendments</h3>
    <p>Keep the submitted audit recoverable when peer review requests new exclusions, thresholds, endpoints, measurement assumptions, or sensitivity analyses.</p>
    <p><a href="peer-review-revision-checklist/">Peer-review revision checklist →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">6</div>
    <h3>Write the reviewer response</h3>
    <p>Link each reviewer item to its response category, timing, execution denominator, manuscript changes, and archived revision evidence.</p>
    <p><a href="reviewer-response-letter/">Response-letter guide →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">7</div>
    <h3>Finalize the resubmission</h3>
    <p>Bind reviewer responses to stable version changes, final manuscript locations, temporal evidence layers, software identity, and an editor-facing evidence map.</p>
    <p><a href="resubmission-readiness/">Resubmission readiness →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">8</div>
    <h3>Prepare publication evidence</h3>
    <p>Bind the complete audit bundle, provenance, fingerprints, methods wording, results wording, revision evidence, and unresolved limitations into a durable record.</p>
    <p><a href="publication-audits/">Publication audits →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">9</div>
    <h3>Find the right documentation fast</h3>
    <p>Use grouped search, type filters, keyboard controls, and the Guide / Example / Reference / Evidence distinction without treating navigation as scientific advice.</p>
    <p><a href="find-information-fast/">Find information fast →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">10</div>
    <h3>Read signatures and source links correctly</h3>
    <p>Interpret generated callable signatures, defaults, annotations, source locations, import snippets, and pathway backlinks without turning software metadata into scientific defaults.</p>
    <p><a href="read-api-reference/">Source-level API guide →</a></p>
  </article>
</div>

## API reference literacy

### [Read the source-level API reference](read-api-reference/)

Use the generated source metadata safely: distinguish Python defaults from scientific decisions, interpret positional/keyword-only markers, follow revision-pinned source links for implementation questions, and use pathway backlinks to recover research context.

The companion [Source-level API inspection]({{ '/docs/examples/source-api-inspection/' | relative_url }}) traces three public symbols from signature to source and governed evidence boundary.

## Documentation navigation

### [Find information fast](find-information-fast/)

Use the site search deliberately: start with the smallest distinctive phrase, read the grouped Guide / Example / Reference / Evidence results, filter only when your information need is already clear, and stop searching once the authoritative contract has been found. The guide also documents keyboard behavior and the boundary between navigation support and scientific judgement.

For a worked navigation exercise, use the [Search → contract walkthrough]({{ '/docs/examples/search-to-contract/' | relative_url }}).

## Start with your own data

### [Start a reproducible GazeAudit project](project-starter/)

Set up a compact study directory that separates the canonical input table, analysis code, researcher decisions, software record, and generated evidence. Use this when you want a clean project scaffold before adapting the practical first-audit example.

### [Researcher audit checklist](researcher-audit-checklist/)

Use a before/during/after checklist for source binding, endpoint declaration, QC policy, exclusions, specification design, failure handling, robustness interpretation, reporting language, and archive handoff. This is the practical governance layer between reproducible code and defensible scientific judgement.

### [Audit decision log template](audit-decision-log-template/)

Copy a structured Markdown record into the project repository to preserve source identity, endpoints, QC decisions, exclusions, declared specification factors, perturbations, deviations, software identity, generated evidence, and reporting boundaries.

### [First real audit with your own data](first-real-audit/)

Take one canonical eye-tracking CSV through `GazeStudy`, structural preflight, researcher-owned decisions, a declared specification space, robustness summaries, and saved evidence. This is the recommended practical entry point when you have a study file and want to understand how the package pieces connect.

### [Audit record map](audit-record-map/)

Follow the research record from source data and researcher-owned decisions through structural QC, declared specification execution, robustness and sensitivity summaries, provenance, fingerprints, and publication claims. Use this when you need to understand **how one artifact supports the next stage of the audit** rather than only what each file contains.

### [Understanding the audit output bundle](audit-output-bundle/)

Read the files produced by the practical workflow as one evidence bundle: structural QC and fingerprints, every declared specification, the specification curve, effect-stability summaries, and marginal and pairwise sensitivity outputs. The guide separates what each artifact describes from conclusions it cannot establish.

## Data onboarding

### [Data onboarding and structural preflight](data-onboarding/)

Map vendor or analysis tables into `GazeStudy`, inspect structural QC, and separate import/ordering problems from scientific quality decisions before running uncertainty or robustness analyses.

### [Analysis-readiness governance](analysis-readiness/)

Declare structural-QC policies, preview cohort impact, separate repairable structural conditions from scientific exclusions, and bind the resulting readiness record to provenance.

## Measurement uncertainty

### [AOI uncertainty](aoi-uncertainty/)

Fit global or grouped gaze-error models, propagate spatial uncertainty into AOI membership, compare hard and probabilistic assignments, and identify boundary-sensitive observations.

## Analytical robustness

### [Specification spaces](specification-space/)

Turn defensible analytical decisions into an explicit `PipelineSpace`, reject invalid combinations before execution, and summarise endpoint stability without selecting a preferred specification after the fact.

### [Interpret an audit result](interpret-audit-result/)

Move from completed robustness outputs to bounded scientific interpretation. The guide starts with the declared execution denominator, then separates direction stability from magnitude sensitivity, treats marginal/pairwise summaries as descriptive rather than causal, records untested uncertainty dimensions, and maps each evidence pattern to an appropriate next action.

For a side-by-side worked comparison, use the [result-pattern reporting example](../examples/result-patterns/).

### [Reporting robustness](reporting-robustness/)

Translate specification curves, sign fractions, marginal sensitivity, and pairwise sensitivity into precise Methods and Results language without treating descriptive diagnostics as confidence intervals, posterior probabilities, or causal decompositions.

For a complete worked interpretation exercise, use the [decision-to-report example](../examples/decision-to-report/).

## Troubleshooting

### [Troubleshooting GazeAudit](troubleshooting/)

Start here when a workflow is **blocked or failing**. The guide routes symptoms across installation/environment, source/schema, structural preflight, grouped measurement models, specification execution, non-finite endpoints, denominator mismatches, and revision-package validation. Each route identifies what to inspect, the smallest safe repair, and what evidence should be preserved before changing anything.

For a worked technical recovery, use the [failed-audit recovery walkthrough](../examples/failed-audit-recovery/). It keeps `8 declared → 7 valid → 6 initially successful` distinct, preserves a valid technical failure, repairs the causal processor defect, reruns the same branch, and retains the original failure event.

### [Common audit mistakes and repairs](common-audit-mistakes/)

Use this when execution **ran**, but the decision trail, denominator governance, reporting boundary, or archive is difficult to defend. It covers outcome-informed specification design, silent branch deletion, endpoint drift, QC/exclusion confusion, hidden interpolation or missingness repair, inferential over-reading of robustness summaries, rewritten decision history, incomplete archives, and transfer of protocol-bound case labels to new data.

The two troubleshooting routes are deliberately different: the troubleshooting center diagnoses blocked execution; this guide repairs weaknesses in the research record without rewriting inconvenient results.

## Manuscript and review readiness

### [Manuscript readiness checklist](manuscript-readiness/)

Verify six pre-submission gates: endpoint reconstruction, execution-denominator accounting, researcher-decision provenance, complete-pattern Results wording, manuscript/archive consistency, and independent reviewer reconstruction. Use this after interpretation but before calling the manuscript record submission-ready.

For a worked review exercise, use the [reviewer reconstruction example](../examples/reviewer-reconstruction/).

### [Peer-review revision checklist](peer-review-revision-checklist/)

Use the compact revision gate before changing files. It classifies clarifications, sensitivity/analytical amendments, endpoint changes, measurement changes, and corrections; records whether outcomes were already inspected; preserves submitted versus post-review denominators; keeps failed valid branches visible; and checks response/manuscript/archive agreement before handoff.

For the shortest real-CLI exercise, use the [revision-package quickstart](../examples/revision-package-quickstart/).

### [Reviewer-requested amendments](reviewer-requested-amendments/)

Preserve the submitted record when peer review asks for new exclusions, sensitivity checks, endpoints, thresholds, or measurement assumptions. The guide separates clarifications, corrections, sensitivity amendments, analytical amendments, endpoint amendments, and measurement amendments; it also requires outcome-inspection timing, amendment-specific execution status, and separate submitted versus post-review denominators.

For a complete revision exercise, use the [reviewer-requested reanalysis example](../examples/reviewer-requested-reanalysis/), which keeps a synthetic submitted **8 / 8** audit distinct from a reviewer-requested **4 / 4** amendment.

### [Reviewer response letter](reviewer-response-letter/)

Build a reviewer response around stable response units: the reviewer request, response category, outcome-inspection timing, action, submitted and post-review denominators, manuscript locations, and archive locations. The guide includes copy-ready wording for clarifications, sensitivity amendments, failed amendments, corrections, endpoint changes, and requests that do not lead to an analytical change.

For a complete response package, use the [revision response package worked example](../examples/revision-response-package/).

### [Version-change manifest](version-change-manifest/)

Record the transition from submitted to revised manuscript using stable change IDs and explicit categories for editorial text, documentation clarification, correction, sensitivity/analytical amendment, endpoint amendment, measurement amendment, and reporting-boundary changes. The guide links each material revision to timing, manuscript locations, evidence, denominator effects, claim impact, and archive provenance.

### [Resubmission readiness and editor handoff](resubmission-readiness/)

Run seven final-handoff gates across reviewer-item closure, temporal evidence layers, response/manuscript agreement, version-change completeness, archive reproducibility, software identity, and an editor-facing evidence map. The guide explicitly treats editorial status as separate from scientific validity.

For the complete temporal exercise, use the [submission-to-accepted-record worked example](../examples/submission-to-accepted-record/).

## Reproducibility

### [Revision reproducibility package](reproducibility-package/)

Use the `gazeaudit-revision-package` CLI to scaffold reviewer-response, change-manifest, amendment, endpoint-amendment, software-identity, and editor-facing evidence-map records, then validate deterministic package structure without conflating structural provenance with scientific validity.

### [Publication audits](publication-audits/)

Use a predeclared conclusion rule, deterministic manifests, methods/report generation, and scientific/bundle fingerprints to make robustness evidence auditable.

### [Publication and archive handoff example](../examples/publication-archive-handoff/)

See one illustrative end state that brings together decision history, complete branch accountability, manuscript Methods/Results wording, limitations, source/software provenance, fingerprints, and a reviewer-friendly archive manifest. All effect values in the worked handoff are synthetic teaching material.

## Ecosystem integration

### [Interoperability](interoperability/)

Understand the division of responsibility between GazeAudit and Eye-Tracking-BIDS, pymovements, pEYES, and custom study/detector adapters.

## A practical sequence

1. [Project starter](project-starter/) — create the study structure.
2. [Researcher audit checklist](researcher-audit-checklist/) — declare and govern decisions.
3. [Decision log template](audit-decision-log-template/) — preserve those decisions and amendments.
4. [First real audit](first-real-audit/) — run the practical CSV-to-evidence path.
5. [Audit output bundle](audit-output-bundle/) — understand what each artifact establishes.
6. [Troubleshooting GazeAudit](troubleshooting/) — diagnose a blocked or failed workflow without rewriting scientific choices.
7. [Failed-audit recovery](../examples/failed-audit-recovery/) — practise preserving a valid technical failure and reconciling a causal repair.
8. [Common audit mistakes](common-audit-mistakes/) — diagnose research-record failures before interpretation.
9. [Interpret an audit result](interpret-audit-result/) — separate completeness, direction, magnitude, and unresolved uncertainty.
10. [Result-pattern example](../examples/result-patterns/) — compare four synthetic evidence patterns and bounded wording.
11. [Decision-to-report example](../examples/decision-to-report/) — practise bounded interpretation on the deterministic 12-branch exercise.
12. [Manuscript readiness](manuscript-readiness/) — test whether the claim and evidence can be reconstructed independently.
13. [Reviewer reconstruction](../examples/reviewer-reconstruction/) — practise finding denominator and reporting gaps from the outside.
14. [Peer-review revision checklist](peer-review-revision-checklist/) — classify reviewer requests and preserve temporal provenance before changes begin.
15. [Reviewer-requested amendments](reviewer-requested-amendments/) — preserve the submitted audit when revision adds new evidence.
16. [Reviewer-requested reanalysis](../examples/reviewer-requested-reanalysis/) — practise a separately denominated post-review sensitivity amendment.
17. [Reviewer response letter](reviewer-response-letter/) — connect each reviewer item to the revision evidence and manuscript changes.
18. [Revision response package](../examples/revision-response-package/) — reconstruct the response letter, change log, and round-specific archive together.
19. [Version-change manifest](version-change-manifest/) — bind material v1 → v2 changes to timing, evidence, and claim impact.
20. [Revision-package quickstart](../examples/revision-package-quickstart/) — create and structurally validate the governed package with the real CLI.
21. [Resubmission readiness](resubmission-readiness/) — run the final editor-handoff consistency gate.
22. [Submission-to-accepted-record example](../examples/submission-to-accepted-record/) — trace submitted, post-review, and final evidence layers end to end.
23. [Publication/archive handoff](../examples/publication-archive-handoff/) — assemble a reviewable end state.
24. [Publication audits](publication-audits/) — build and verify the durable research record.

## What a guide is not

Guides describe GazeAudit's scientific contracts and recommended use. They do not replace study-specific justification. Researchers remain responsible for deciding which AOIs, error models, detectors, preprocessing choices, QC thresholds, perturbations, specifications, reviewer-requested extensions, revision interpretations, and scientific endpoints are defensible for their design.