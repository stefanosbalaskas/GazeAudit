---
title: What should I do next?
description: A static-first decision map from study planning through audit, interpretation, peer review, resubmission, and publication handoff.
kicker: Start
search_category: Start
search_keywords: what next next step onboarding where do I start project stage plan audit interpret peer review revision resubmission publication handoff first audit
---

# What should I do next?

Use this page when you know **where the project is** but not which GazeAudit page should come next. It is a navigation guide, not a scientific decision engine.

The shortest route is:

1. **Plan** the research record before analysis choices become outcome-informed.
2. **Audit** the canonical data and execute the declared alternatives.
3. **Interpret** the complete evidence pattern before reducing it to manuscript prose.
4. **Revise** after peer review without rewriting the submitted evidence layer.
5. **Handoff** the final manuscript, response package, software identity, and archive as one reconstructable record.

<div class="callout warning">
<strong>Stop rather than guess.</strong>
If the endpoint, valid execution denominator, source identity, reviewer timing, or study-specific justification is unclear, do not let this route invent it. Recover or declare the missing information first. GazeAudit can organise evidence and provenance; it does not decide scientific validity, thresholds, exclusions, endpoints, or acceptable reviewer requests for you.
</div>

## Fast decision map

| Your current state | Build next | Start here | You are ready to leave the stage when… |
|---|---|---|---|
| The study is being designed or the analysis route is not yet declared | A governed project route | [Audit planner](../planner/) and [Project starter](project-starter/) | source, endpoint, researcher-owned decisions, and intended method route are explicit |
| A canonical gaze table exists but the audit record is not complete | Structural QC + declared execution record | [First real audit](first-real-audit/) | the canonical mapping, QC record, valid branch denominator, execution status, and saved evidence are recoverable |
| The audit has run but the manuscript claim is not yet settled | Bounded interpretation | [Interpret an audit result](interpret-audit-result/) | completeness, endpoint identity, direction, magnitude, sensitivity, and unresolved uncertainty are separated |
| A reviewer has requested clarification or new work | A temporally separated revision record | [Revision toolkit](../workspace/revision-toolkit/) and [Revision route map](revision-route-map/) | every request is classified and linked to response, manuscript, evidence, and archive locations |
| The revision is complete and the manuscript is moving to resubmission/final record | Editor-facing and publication handoff | [Resubmission readiness](resubmission-readiness/) and [Reproducible publication](../workflows/reproducible-publication/) | reviewer items, version changes, evidence layers, software identity, and final claims reconcile |

## Stage 1 — plan before analysis

### Use this stage when

- the canonical source has not yet been bound to an analysis record;
- the endpoint is still being defined;
- several defensible preprocessing, measurement, QC, or analytical choices could vary;
- you need to decide which GazeAudit workflow families are relevant.

### Build now

Preserve at least:

- source-data identity and expected schema;
- the scientific endpoint and unit of analysis;
- researcher-owned QC and exclusion decisions;
- plausible method families and alternative specifications;
- known uncertainty dimensions;
- software/version expectations.

### Open next

1. [Audit planner](../planner/) — route declared study conditions to method families.
2. [Project starter](project-starter/) — create the study/evidence directory structure.
3. [Researcher audit checklist](researcher-audit-checklist/) — record decisions before, during, and after execution.
4. [Audit decision log template](audit-decision-log-template/) — preserve the reasoning in a copy-ready record.

<div class="callout info">
<strong>Do not use the planner as a diagnostic instrument.</strong>
Selecting a condition records a navigation choice. It does not prove that the condition exists, that a particular method is required, or that a threshold is scientifically defensible.
</div>

## Stage 2 — audit the canonical data

### Use this stage when

- the input table is available;
- you need to map semantic columns explicitly;
- structural QC has not yet been preserved;
- a declared specification space needs to be executed;
- generated evidence is still scattered across notebooks or temporary files.

### Build now

Your record should make it possible to recover:

- which canonical file was analysed;
- how participant, trial, timestamp, and gaze variables were mapped;
- which structural conditions were observed;
- which branches were valid before execution;
- which valid branches succeeded or failed;
- which outputs and fingerprints belong to the run.

### Open next

1. [First real audit](first-real-audit/) — the practical CSV → QC → specification → evidence route.
2. [Data onboarding](data-onboarding/) — focus on structural mapping and preflight.
3. [Analysis-readiness governance](analysis-readiness/) — preview cohort consequences when readiness policy is part of the question.
4. [Audit output bundle](audit-output-bundle/) — learn what each saved artifact establishes.

### Stop condition

Do **not** move to interpretation because one preferred estimate exists. Move on when the **declared valid denominator and execution status** are recoverable, including valid failures.

## Stage 3 — interpret before writing

### Use this stage when

- analysis code has finished;
- a specification curve or sensitivity summary exists;
- coauthors are asking whether the result is “robust” or “fragile”;
- the Results section is about to be written.

### Read the record in this order

1. **Execution completeness** — how many valid branches were declared and how many succeeded?
2. **Endpoint identity** — did every compared branch estimate the same scientific endpoint?
3. **Direction** — does the sign change across valid successful branches?
4. **Magnitude** — how much does the estimate move even when direction is stable?
5. **Sensitivity structure** — which declared factors align descriptively with larger changes?
6. **Untested uncertainty** — what important dimensions were not varied?

### Open next

- [Interpret an audit result](interpret-audit-result/)
- [Result-pattern reporting example](../examples/result-patterns/)
- [Decision-to-report example](../examples/decision-to-report/)
- [Reporting robustness](reporting-robustness/)
- [Manuscript readiness](manuscript-readiness/)

<div class="callout warning">
<strong>Do not compress descriptive diagnostics into inferential claims they do not support.</strong>
Specification quantiles are not confidence intervals, sign fractions are not posterior probabilities, and marginal/pairwise sensitivity summaries are not causal variance decompositions.
</div>

## Stage 4 — revise after peer review

### Use this stage when

- reviewer comments have arrived;
- a clarification can be answered without rerunning analysis;
- the reviewer requests a new threshold, exclusion, sensitivity analysis, measurement assumption, or endpoint;
- a factual or analytical correction is required.

### First classify the request

Use the [Revision route map](revision-route-map/) to distinguish:

- `documentation_clarification`;
- `correction`;
- `sensitivity_amendment`;
- `analytical_amendment`;
- `endpoint_amendment`;
- `measurement_amendment`.

Then preserve the timing explicitly. A submitted `8 / 8` audit plus a reviewer-requested `4 / 4` amendment remains **8 / 8 submitted + 4 / 4 post-review**. It does not become “12 pre-specified analyses.” If one of four valid post-review branches fails, the amendment is **3 successful / 4 valid**, not `3 / 3`.

### Open next

1. [Peer-review revision checklist](peer-review-revision-checklist/) — the compact pre-change gate.
2. [Revision toolkit](../workspace/revision-toolkit/) — the full revision workspace.
3. [Revision-round scenarios](../examples/revision-round-scenarios/) — compare common revision paths.
4. [Revision-package quickstart](../examples/revision-package-quickstart/) — create and validate structural provenance with the real CLI.
5. [Reviewer response letter](reviewer-response-letter/) — reconcile request, action, manuscript, and archive.

## Stage 5 — resubmission and durable handoff

### Use this stage when

- every reviewer item has an intended disposition;
- revised analyses and manuscript edits are complete;
- the team is preparing an editor-facing package;
- the publication-associated archive needs to be frozen.

### Build now

Check that the final record connects:

- reviewer item → response category and action;
- response → submitted/post-review evidence layer;
- evidence → manuscript location;
- manuscript change → version-change manifest;
- generated outputs → exact software identity and provenance;
- final claim → editor-facing evidence map;
- unresolved limitation → final manuscript limitation text.

### Open next

- [Resubmission readiness](resubmission-readiness/)
- [Version-change manifest](version-change-manifest/)
- [Submission-to-accepted-record example](../examples/submission-to-accepted-record/)
- [Publication/archive handoff example](../examples/publication-archive-handoff/)
- [Reproducible publication workflow](../workflows/reproducible-publication/)

## Common branch points

### “I only need to answer a reviewer clarification.”

Stay in the revision stage, classify it as documentation-only when appropriate, and preserve that **no analytical rerun occurred**. Do not manufacture an amendment denominator.

### “A reviewer asks for a different endpoint.”

Create a separate endpoint record. Do not add the new endpoint to the denominator of the submitted endpoint merely because both appear in the same revised manuscript.

### “A valid analysis branch fails technically.”

Keep the branch in the valid denominator, preserve the failure evidence, and report successful/valid counts separately. Do not shrink the denominator after observing execution.

### “The manuscript is accepted. Is the science now validated?”

Editorial status and scientific validity are different layers. Archive the accepted record and its provenance without converting acceptance into a GazeAudit scientific label.

### “My new study resembles one of the frozen case studies.”

Do not inherit the frozen outcome label. GazeBase `incomplete`, Korthals `robust_negative`, and Pedrotti/de Chambrier `materially_fragile` are protocol-bound records for those frozen cases.

## A static route you can bookmark

This page is deliberately useful without JavaScript. The interactive homepage project-stage router is a faster entry point when scripting is available, while this guide keeps the same project-stage logic in a stable, searchable, linkable document.

For one continuous synthetic exercise across all five stages, continue to the [project lifecycle walkthrough](../examples/project-lifecycle-walkthrough/).

## Scientific boundary

This route helps answer **where to go next in the documentation**. It does not answer whether a study design is valid, which threshold should be used, which participants should be excluded, whether a reviewer request is scientifically justified, whether an endpoint should change, or what substantive conclusion the study should reach.