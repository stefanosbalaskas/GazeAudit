---
title: Documentation hub
description: Choose the GazeAudit documentation path that matches your research task, from first audit through troubleshooting, peer-review revision, and reproducible publication.
kicker: Documentation
---

# Documentation hub

GazeAudit documentation is organised around **research tasks**, not only modules. Start with the smallest runnable example, build a transparent audit route from study conditions, troubleshoot blocked execution without rewriting the scientific record, then move into structural preflight, measurement uncertainty, specification-space design, sensitivity analysis, frozen real-data case studies, peer-review revision, and reproducible publication.

<div class="callout info">
<strong>Current release</strong>
The public release is <code>0.1.0</code>. Use the <a href="install/">Install & environment center</a> to create an isolated environment, choose optional extras, verify Python compatibility, and generate the exact install command. The documentation also describes post-release development on <code>main</code>; when reproducibility matters, record the exact version or commit used.
</div>

<div class="callout tip">
<strong>Not sure what comes next?</strong>
Open <a href="guides/what-next/">What should I do next?</a> for a static five-stage decision map from planning through audit, interpretation, peer review, and final handoff. Then use the <a href="examples/project-lifecycle-walkthrough/">project lifecycle walkthrough</a> to follow one fully synthetic project across all five stages without importing its teaching choices into a real study.
</div>

<div class="callout tip">
<strong>Have your own gaze CSV already?</strong>
Open <a href="guides/first-real-audit/">First real audit with your own data</a> for the practical CSV → <code>GazeStudy</code> → structural preflight → declared robustness → saved evidence route. The companion <a href="examples/first-real-audit/">executable example</a> can be run first on deterministic demo data and then on your canonical table.
</div>

<div class="callout warning">
<strong>Something failed or the audit is blocked?</strong>
Use <a href="guides/troubleshooting/">Troubleshooting GazeAudit</a> to route the symptom to the environment, source/schema, structural-QC, measurement, specification-execution, endpoint, or provenance layer. Then work through the <a href="examples/failed-audit-recovery/">failed-audit recovery walkthrough</a> to see how a valid technical failure is preserved, repaired, rerun, and reconciled without silently shrinking the denominator.
</div>

<div class="callout info">
<strong>Already know the task and just need the exact contract?</strong>
Use the <a href="reference/">Reference hub</a> for public API contracts, installed CLI commands, evidence/denominator vocabulary, documentation provenance, validation authority, citation, and release identity. The <a href="examples/reference-lookup-workflow/">reference lookup walkthrough</a> shows how to move between those factual references without turning them into scientific decision rules.
</div>

Use **Ctrl/Cmd + K** anywhere on the site to search methods, workflows, examples, evidence pages, and reference material. Results are grouped by documentation type so the same topic can expose a Guide, Example, Reference, or Evidence authority without implying that one is scientifically preferred. Use [Find information fast](guides/find-information-fast/) for the keyboard controls, filters, query patterns, and navigation boundary.

## Choose by intent

<div class="documentation-compass compact" aria-label="Documentation routes by reader intent">
  <article class="documentation-compass-card">
    <span class="documentation-compass-mode">Learn</span>
    <h3>Learn by doing</h3>
    <p>Use Getting Started and bounded synthetic examples.</p>
    <a href="examples/">Browse learning examples →</a>
  </article>
  <article class="documentation-compass-card">
    <span class="documentation-compass-mode">Do</span>
    <h3>Complete a task</h3>
    <p>Use guides, workflows, and troubleshooting for real research work.</p>
    <a href="guides/">Browse task guides →</a>
  </article>
  <article class="documentation-compass-card">
    <span class="documentation-compass-mode">Look up</span>
    <h3>Find an exact contract</h3>
    <p>Use API, CLI, vocabulary, provenance, and validation references.</p>
    <a href="reference/">Browse reference →</a>
  </article>
  <article class="documentation-compass-card">
    <span class="documentation-compass-mode">Understand</span>
    <h3>Understand the rationale</h3>
    <p>Use articles, methods discussion, and bounded case studies.</p>
    <a href="articles/">Browse explanations →</a>
  </article>
</div>

<p><a href="documentation-map/">Open the full Documentation compass →</a></p>

## Start here

| Goal | Recommended page |
|---|---|
| Set up Python, choose extras, and verify the installed environment | [Install & environment center](install/) |
| Map my existing table into the canonical GazeStudy contract | [Data Contract & Schema Mapping Center](data-contract/) |
| Preserve source, units, mapping, and transformation provenance | [Data mapping provenance](guides/data-mapping-provenance/) |
| Look up a structural-QC issue or diagnostic detail code | [Structural QC Issue Clinic](reference/qc-issue-clinic/) |
| Triage a `review` state without automatic exclusion | [Structural-QC triage](guides/structural-qc-triage/) |
| Design a readiness policy with no hidden threshold defaults | [Readiness Policy Design Center](readiness-policy/) |
| Practise primary/alternative readiness policy consequences | [Readiness policy design](examples/readiness-policy-design/) |
| Match evidence states to bounded Methods/Results/limitations wording | [Results Interpretation & Reporting Center](reporting-center/) |
| Practise rewriting over-strong manuscript claims | [Reporting-language rewrite](examples/reporting-language-rewrite/) |
| Declare the common scalar endpoint before building a multiverse | [Endpoint Definition & Handoff Center](endpoint-contract/) |
| Declare factors, levels, timing, validity, and failure policy before execution | [Specification Space Declaration Center](specification-declaration/) |
| Practise declared → valid → successful denominator accounting | [Declared → valid → successful](examples/specification-denominator-audit/) |
| Preserve failures, non-finite endpoints, not-run branches, and repair lineage | [Execution Ledger & Recovery Center](execution-ledger/) |
| Practise branch vs attempt reconciliation after repairs | [Failure → repair → reconciliation](examples/execution-ledger-reconciliation/) |
| Interpret specification curves, stability, and sensitivity diagnostics | [Robustness Diagnostics & Sensitivity Interpretation Center](robustness-diagnostics/) |
| Design controlled sampling and added-missingness perturbations | [Sampling & Missingness Sensitivity Center](sampling-missingness/) |
| Practise sampling/missingness denominators and reproducibility | [Sampling & missingness design audit](examples/sampling-missingness-design-audit/) |
| Practise diagnostic interpretation with exact synthetic outputs | [Diagnostic interpretation walkthrough](examples/robustness-diagnostic-walkthrough/) |
| Declare an independently justified categorical recovery rule | [Conclusion Rule Design Center](conclusion-rule/) |
| Practise conclusion-rule edge cases and threshold semantics | [Conclusion-rule edge cases](examples/conclusion-rule-edge-cases/) |
| Practise detecting endpoint drift across specifications | [Endpoint drift audit](examples/endpoint-drift-audit/) |
| Practise every current structural-QC issue/detail code | [All structural-QC issues](examples/all-structural-qc-issues/) |
| Practise valid, invalid, and reviewable table cases | [Data contract example](examples/data-contract-valid-invalid/) |
| Practise auditing a changed mapping without rewriting history | [Mapping change audit](examples/data-mapping-change-audit/) |
| I am unsure what the project should do next | [What should I do next?](guides/what-next/) |
| Follow one project from planning through final handoff | [Project lifecycle walkthrough](examples/project-lifecycle-walkthrough/) |
| Find the right guide, example, reference, or evidence page quickly | [Find information fast](guides/find-information-fast/) |
| Practise search → documentation type → authority | [Search → contract walkthrough](examples/search-to-contract/) |
| Start from a known function and trace its governed context | [API pathways](reference/api-pathways/) |
| Read generated signatures, source links, imports, and pathway backlinks | [Source-level API guide](guides/read-api-reference/) |
| Practise signature → source → research-context inspection | [Source-level API inspection](examples/source-api-inspection/) |
| Practise required arguments, returns, and minimal call shapes | [Generated API call contracts](examples/api-call-contracts/) |
| Browse every example by data context, focus, output, and boundary | [Example catalog](examples/catalog/) |
| Practise choosing the right learning example | [Choose the right example](examples/choose-the-right-example/) |
| Adapt a synthetic workflow without inheriting its teaching values | [Adapt examples to your study](guides/adapt-examples-to-study/) |
| Practise the example → real-study handoff | [Example → study handoff](examples/example-to-study-handoff/) |
| Practise symbol → example → evidence-boundary navigation | [Function → evidence walkthrough](examples/function-to-evidence/) |
| Something failed or the audit is blocked | [Troubleshooting GazeAudit](guides/troubleshooting/) |
| Practise a failure → repair → rerun workflow | [Failed-audit recovery walkthrough](examples/failed-audit-recovery/) |
| Apply GazeAudit to my own canonical CSV | [First real audit guide](guides/first-real-audit/) |
| See the whole project-level path from planning to publication | [Researcher workspace](workspace/) |
| Revise a manuscript after peer review | [Peer-review revision toolkit](workspace/revision-toolkit/) |
| Use a compact reviewer-revision gate before changing files | [Peer-review revision checklist](guides/peer-review-revision-checklist/) |
| Create and validate the reviewer-revision package | [Revision-package quickstart](examples/revision-package-quickstart/) |
| Install and run the smallest uncertainty example | [Getting started](getting-started/) |
| Record environment identity for reproducibility | [Environment setup guide](guides/environment-setup/) |
| Run a software-only installation smoke check | [Install → verify → first import](examples/install-smoke-check/) |
| Build and export a transparent audit route from study conditions | [Audit planner](planner/) |
| Map a research question to methods, public functions, examples, plots, and evidence | [Method explorer](methods/) |
| Map a vendor table into GazeStudy | [Map your table](guides/map-your-table/) |
| Inspect structural QC after mapping | [Data onboarding and structural preflight](guides/data-onboarding/) |
| Declare participant/trial readiness policies and preview cohort impact | [Analysis-readiness governance](guides/analysis-readiness/) |
| Browse reproducible code-generated figures | [Plot gallery](plots/) |
| Run one complete robustness audit | [End-to-end robustness example](examples/end-to-end-robustness/) |
| Understand uncertainty at AOI boundaries | [AOI uncertainty guide](guides/aoi-uncertainty/) |
| Build a multiverse/specification analysis | [Specification-space guide](guides/specification-space/) |
| Report robustness precisely | [Reporting robustness](guides/reporting-robustness/) |
| Inspect real validation outcomes | [Case studies](case-studies/) |
| Create deterministic publication evidence | [Publication audits](guides/publication-audits/) |
| Connect BIDS, pymovements, pEYES, or custom backends | [Interoperability](guides/interoperability/) |
| Look up an exact API, CLI, status, provenance, or release contract | [Reference hub](reference/) |
| Check installed console commands and exact revision-package syntax | [CLI reference](reference/cli-reference/) |
| Check declared/valid/failure denominator terminology | [Evidence vocabulary](reference/evidence-vocabulary/) |
| Practise finding an exact contract without rereading a workflow | [Reference lookup walkthrough](examples/reference-lookup-workflow/) |
| Find the right public function | [API map](reference/api-map/) |

## Guided next step

The [What should I do next?](guides/what-next/) page is the static counterpart to the homepage project-stage router. It keeps the same five project stages—plan, audit, interpret, peer review, and handoff—in ordinary semantic documentation that remains useful without JavaScript.

Use it when the question is **where should I go next in the documentation?** rather than **which scientific choice is correct?** The guide deliberately stops when endpoint identity, valid denominators, reviewer timing, or study-specific justification are unclear instead of inventing a decision.

The companion [project lifecycle walkthrough](examples/project-lifecycle-walkthrough/) follows one fully synthetic endpoint from an eight-branch submitted audit into interpretation, a separately denominated post-review amendment with one valid technical failure, a separate endpoint amendment, and final handoff. It is teaching material, not empirical validation evidence.

## Troubleshoot a blocked audit

Use [Troubleshooting GazeAudit](guides/troubleshooting/) when execution itself is blocked: installation/import problems, source-schema mismatches, structural-QC flags, incomplete grouped-model coverage, valid specification failures, non-finite endpoints, denominator mismatches, or revision-package validation errors.

The symptom router separates **invalid before execution**, **valid and successful**, **valid but technically failed**, and **not run** states so troubleshooting cannot silently rewrite the valid denominator. The companion [failed-audit recovery walkthrough](examples/failed-audit-recovery/) follows a fully synthetic `8 declared → 7 valid → 6 initially successful` audit through diagnosis, technical repair, same-branch rerun, and final reconciliation while retaining the original failure event.

If the software ran but the decision history, archive, or reporting boundary is weak, use [Common audit mistakes and repairs](guides/common-audit-mistakes/) instead. Troubleshooting is not a mechanism for choosing a more convenient scientific rule.

## Reference layer

Use the [Reference hub](reference/) when the question is factual rather than procedural: **Which public function? Which installed command? What exactly does this denominator/status term mean? Which revision built the site? Which frozen record is authoritative?**

The reference layer deliberately stays separate from how-to guidance. [CLI reference](reference/cli-reference/) records the commands declared by the package, while [Evidence and denominator vocabulary](reference/evidence-vocabulary/) distinguishes actual runtime fields from audit-ledger terms such as `technical_failure`. The [reference lookup walkthrough](examples/reference-lookup-workflow/) demonstrates that distinction on fully synthetic teaching data.

Reference pages do not choose thresholds, exclusions, endpoints, validity predicates, reviewer amendments, or conclusions. When the question becomes “what sequence should I follow?”, return to a guide or workflow.

## Researcher workspace

The [Researcher workspace](workspace/) is the project-level route when you want to connect several documentation layers without losing their scientific boundaries. It links six stages: scope the audit, inspect the governed method route, run the smallest relevant workflow, inspect visuals in context, check the evidence boundary, and preserve the publication record.

Use it as an orientation layer rather than a new source of scientific rules. The workspace does not choose thresholds, exclusions, perturbation levels, specifications, or validity claims.

## Peer-review revision

If the manuscript is already in a revision round, use the [Peer-review revision toolkit](workspace/revision-toolkit/) rather than reconstructing the route from publication pages manually. The toolkit separates clarification, analytical amendments, endpoint changes, corrections, reviewer-response records, package validation, and final editor handoff while preserving the submitted evidence layer.

For the shortest operational route, run the [peer-review revision checklist](guides/peer-review-revision-checklist/) before changing files, then use the [revision-package quickstart](examples/revision-package-quickstart/) to create and structurally validate the governed package with the real `gazeaudit-revision-package` CLI.

A valid revision package establishes **structural provenance only**. It does not certify scientific validity, robustness, manuscript quality, or publication readiness.

## Plan an audit from study conditions

The [Audit planner](planner/) is the shortest route when you know which study conditions or methodological risks are relevant but do not yet know which parts of GazeAudit to combine. Select only the conditions that genuinely apply; the planner deduplicates the corresponding governed method families, explains why each method entered the route, and links directly to its guide, runnable example, diagnostic plot, and evidence boundary.

The planner is deliberately **non-diagnostic**. It does not choose thresholds, infer unselected risks, exclude participants, or decide whether a result is scientifically valid. A shared planner URL records navigation choices, not a scientific conclusion.

When the route is useful, preserve it as a **shareable URL**, a **Markdown audit brief**, or a deterministic **JSON navigation manifest**. The JSON record includes a stable schema version, selected conditions, ordered methods, API sequences, workflow handoffs, the GazeAudit release identity, and the documentation revision; it intentionally does not insert a volatile timestamp.

## Explore methods by research question

The [method explorer](methods/) connects ten methodological questions to a compact public API route, a guide or runnable example, a diagnostic figure, and an explicit evidence boundary. Use it when you know **what decision you need to defend** but do not yet know which GazeAudit functions or workflow page to open.

Its evidence column is deliberately conservative: frozen real-data cases are linked only where they are substantively relevant, while synthetic known-truth benchmarks and live interoperability checks remain labelled as different evidence types.

## Data onboarding

Before applying measurement or robustness methods to a new table, map its semantic columns explicitly with `GazeStudy` and run the structural preflight. The [data onboarding guide](guides/data-onboarding/) explains how `audit_study_qc()` reports non-finite coordinates/timestamps, missing identifiers, duplicate within-trial timestamps, and decreasing time order without turning those diagnostics into universal exclusion rules. If preflight returns `review`, use the [Structural QC Issue Clinic](reference/qc-issue-clinic/) for exact issue/detail-code lookup and the [Structural-QC triage guide](guides/structural-qc-triage/) for the inspection → decision → repair/rerun → reporting sequence.

For a single practical path that continues beyond preflight into robustness outputs and saved evidence, use [First real audit with your own data](guides/first-real-audit/).

## Runnable examples

The examples use synthetic data unless a page explicitly points to a frozen real-data validation record. This keeps demonstrations runnable without private participant data while separating demonstration values from empirical claims.

- [Project lifecycle walkthrough](examples/project-lifecycle-walkthrough/) — five-stage synthetic project from declared route through audit, interpretation, peer-review amendment, separate endpoint record, and final handoff.
- [Failed-audit recovery walkthrough](examples/failed-audit-recovery/) — synthetic declared/valid/successful denominator accounting, technical failure preservation, causal repair, same-branch rerun, and reconciliation.
- [Valid, invalid, and reviewable tables](examples/data-contract-valid-invalid/) — learn which schema conditions fail construction and which remain visible as structural-review evidence.
- [Mapping change audit](examples/data-mapping-change-audit/) — distinguish source-label changes from substantive source, unit, coordinate, grouping, and exclusion changes.
- [First real audit](examples/first-real-audit/) — CSV-oriented project template with structural-QC provenance, complete specification execution, and saved robustness tables.
- `python examples/study_preflight.py` — inspect a deliberately flagged canonical study before downstream analysis.
- [End-to-end robustness audit](examples/end-to-end-robustness/) — canonical study → declared specification space → complete execution → stability and sensitivity diagnostics.
- [Generated API call contracts](examples/api-call-contracts/) — read required positional and keyword-only arguments, return annotations, and mechanically generated minimal call shapes without inventing study values.
- [Example → study handoff](examples/example-to-study-handoff/) — separate reusable workflow structure from teaching values and rebuild the analysis as a study-owned record.
- [AOI boundary uncertainty](examples/aoi-boundary/) — fit a gaze-error model and convert a hard boundary decision into probabilistic membership.
- [Specification curve](examples/specification-curve/) — summarise an explicit analytical decision space.
- [Sampling sensitivity](examples/sampling-sensitivity/) — perturb sampling rate and inspect endpoint stability.
- [Revision-package quickstart](examples/revision-package-quickstart/) — synthetic reviewer requests → governed revision scaffold → response/change/evidence records → structural validation.

## Research workflows

Use the workflow pages when you are designing a study or analysis rather than learning one function.

- [Workflow map](workflows/) — choose the right workflow family.
- [First-study audit](workflows/first-study-audit/) — canonical data → preflight → optional readiness/measurement layers → robustness → publication provenance.
- [Measurement audit](workflows/measurement-audit/) — validation information → error model → AOI uncertainty → endpoint propagation.
- [Robustness audit](workflows/robustness-audit/) — defensible choices → common endpoint → specification curve → sensitivity diagnostics.
- [Reproducible publication](workflows/reproducible-publication/) — declared rule → audit bundle → fingerprints → methods/report output.

## Real-data case studies

The case-study layer turns the frozen validation records into readable methodological walkthroughs while leaving the underlying scientific records untouched.

<div class="evidence-grid">
  <article class="evidence-card evidence-incomplete">
    <span class="evidence-state">Incomplete</span>
    <h3>GazeBase</h3>
    <p>See why a seven-detector analysis stopped when two frozen specifications failed the completeness gate.</p>
    <p><a href="{{ '/docs/case-studies/gazebase-incomplete/' | relative_url }}">Open case →</a></p>
  </article>
  <article class="evidence-card evidence-robust">
    <span class="evidence-state">Robust negative</span>
    <h3>Korthals</h3>
    <p>Compare hard AOI membership with the uncertainty-propagated target-tracking effect.</p>
    <p><a href="{{ '/docs/case-studies/korthals-target-tracking/' | relative_url }}">Read the frozen case →</a></p>
  </article>
  <article class="evidence-card evidence-fragile">
    <span class="evidence-state">Materially fragile</span>
    <h3>Pedrotti/de Chambrier</h3>
    <p>See how sampling resolution and controlled missingness changed magnitude recovery.</p>
    <p><a href="{{ '/docs/case-studies/pedrotti-sensitivity/' | relative_url }}">Read the frozen case →</a></p>
  </article>
</div>

## Conceptual articles

The articles explain why the package is structured the way it is and where its scientific boundaries sit.

- [Measurement uncertainty is a modelling problem](articles/measurement-uncertainty-is-a-modeling-problem/)
- [From one pipeline to a robustness audit](articles/from-one-pipeline-to-a-robustness-audit/)
- [How to read a fragile result](articles/how-to-read-a-fragile-result/)

## Reporting layer

After running an audit, use [Reporting robustness without overclaiming](guides/reporting-robustness/) to distinguish descriptive specification quantiles from confidence intervals, sign fractions from probabilities, and sensitivity screening from causal variance decomposition.

## Frozen validation evidence

GazeAudit's validation programme deliberately preserves different scientific outcomes. The authoritative index is the [validation matrix](VALIDATION_MATRIX.html).

| Case | Canonical outcome | What the outcome means |
|---|---|---|
| GazeBase multi-detector audit | `incomplete` | The predeclared completeness gate was not satisfied. |
| Korthals target-tracking AOI | `robust_negative` | The negative paired AOI effect survived the frozen uncertainty model. |
| Pedrotti/de Chambrier sampling + missingness | `materially_fragile` | The endpoint changed materially under the frozen perturbation protocol. |

These labels are **protocol-bound records**, not universal properties of the source datasets.

## Scientific and release reference

For deeper provenance or publication operations, use the existing authoritative records:

- [Reference hub](reference/) — API, CLI, vocabulary, provenance, validation, citation, and release lookup.
- [Scientific methods](SCIENTIFIC_METHODS.html)
- [Validation matrix](VALIDATION_MATRIX.html)
- [Citation and reuse](CITATION_AND_REUSE.html)
- [Release notes 0.1.0](RELEASE_NOTES_0.1.0.html)
- [External publication record](EXTERNAL_PUBLICATION_0.1.0.html)

## Need a quick answer?

Open the [FAQ](faq/) for installation, interpretation, versioning, and scope questions, or [Troubleshooting GazeAudit](guides/troubleshooting/) when a workflow is blocked or failing.

## Code-generated visual reference

The [plot gallery](plots/) contains 14 deterministic Matplotlib SVGs tied to executable source, including readiness, cohort-impact, repair, specification, sensitivity, AOI, and recovery diagnostics.