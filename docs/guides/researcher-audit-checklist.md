---
title: Researcher audit checklist
description: A before-during-after checklist for declaring decisions, preserving the full audit record, interpreting robustness outputs, and reporting only what the evidence supports.
kicker: Guide · Research practice
permalink: /docs/guides/researcher-audit-checklist/
search_category: Guide
search_keywords: checklist decision log preregistration robustness reporting researcher decisions manuscript reproducibility archive exclusions thresholds endpoint specifications perturbations
---

# Researcher audit checklist

Use this checklist to keep the **scientific decisions around a GazeAudit analysis visible**. It is designed for the points where an otherwise reproducible workflow can still become hard to review: decisions are made after results are visible, diagnostic flags silently become exclusions, the specification space changes during execution, or descriptive robustness summaries are reported as stronger forms of inference.

<div class="callout info">
<strong>This checklist records decisions; it does not make them.</strong>
GazeAudit does not determine the scientifically correct endpoint, AOI, QC threshold, exclusion rule, perturbation range, detector, preprocessing path, or validity claim for a study. Those choices require study-specific justification.
</div>

## The four checkpoints

<div class="card-grid">
  <article class="card">
    <div class="card-icon" aria-hidden="true">1</div>
    <h3>Before execution</h3>
    <p>Bind the study source, endpoint, researcher-owned decisions, valid alternatives, invalid combinations, and intended uncertainty dimensions before outcome inspection.</p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">2</div>
    <h3>During execution</h3>
    <p>Preserve every declared branch, structural warning, technical failure, and protocol-relevant deviation rather than silently pruning the audit record.</p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">3</div>
    <h3>Before interpretation</h3>
    <p>Check that robustness summaries answer the declared methodological question and are not being upgraded into confidence, posterior, or causal claims they do not support.</p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">4</div>
    <h3>Before publication</h3>
    <p>Bind the complete evidence bundle, software identity, provenance, fingerprints, Methods language, Results language, and unresolved limitations into the durable record.</p>
  </article>
</div>

## 1. Before execution: declare the scientific contract

Record enough information that a collaborator can distinguish a **planned analytical alternative** from an adjustment made after seeing the outcome.

- [ ] The canonical source table or immutable source reference is identified.
- [ ] Coordinate system, units, sampling information, participant identity, and trial identity are documented.
- [ ] The scientific endpoint is defined in words and code-level terms.
- [ ] Structural-QC diagnostics are separated from scientific exclusion decisions.
- [ ] Every exclusion rule that can affect the endpoint has a study-specific rationale.
- [ ] Every specification factor represents a defensible analytical alternative rather than a search for favourable estimates.
- [ ] Invalid factor combinations are declared before running the specification space.
- [ ] Perturbation families and ranges correspond to uncertainty dimensions the study actually intends to test.
- [ ] Technical failure handling is defined: failures remain visible in the audit trail rather than disappearing from denominators.
- [ ] The intended interpretation rule is stated before looking at the robustness summaries.

### Minimum decision log

| Decision field | Record | Why it matters |
|---|---|---|
| Study/source identity | file, dataset version, checksum, immutable URL, or other stable identifier | prevents accidental source drift |
| Endpoint | exact scientific quantity being compared or summarised | prevents outcome switching across branches |
| Structural-QC policy | what each relevant flag triggers for human review | separates diagnostics from automatic exclusion |
| Exclusions | rule + scientific rationale | makes cohort changes reviewable |
| Specification factors | factor name + allowed values + rationale | defines the declared robustness space |
| Invalid combinations | combinations that cannot be interpreted or executed | keeps the denominator scientifically coherent |
| Perturbations | uncertainty dimension + range/grid + rationale | distinguishes sensitivity testing from arbitrary stress |
| Failure policy | how technical failures and incomplete branches are retained | prevents silent deletion |
| Interpretation rule | what pattern would count as stable, fragile, incomplete, or simply unresolved for this analysis | constrains post-hoc storytelling |
| Software identity | release and, when needed, exact commit | binds code to evidence |

Use the [decision-log template]({{ '/docs/guides/audit-decision-log-template/' | relative_url }}) when you want a copy-ready record for a project repository.

## 2. During execution: preserve the declared space

A complete audit record should make it possible to reconstruct **what was attempted**, not only what succeeded.

- [ ] `GazeStudy` mapping is explicit; source columns are not guessed silently.
- [ ] Structural QC is inspected before analytical filtering is treated as scientifically justified.
- [ ] The declared specification space is executed without adding or removing values in response to observed estimates.
- [ ] Invalid combinations are distinguished from technical failures.
- [ ] Technical failures remain identifiable in logs or result tables.
- [ ] The scientific endpoint is not quietly redefined for difficult branches.
- [ ] Any unavoidable deviation from the original plan is written to the decision log with a reason and timing.
- [ ] Output tables are saved in full, including rows that are inconvenient to the final narrative.

<div class="callout warning">
<strong>Do not repair the specification space by outcome.</strong>
If a branch is removed because its estimate looks implausible, extreme, null, or inconvenient, the resulting table no longer represents the originally declared robustness space. Investigate the branch, record the reason, and distinguish scientific invalidity from result-driven pruning.
</div>

## 3. Before interpretation: ask what the output actually establishes

Use the [audit output bundle]({{ '/docs/guides/audit-output-bundle/' | relative_url }}) and [audit record map]({{ '/docs/guides/audit-record-map/' | relative_url }}) to connect each artifact to its interpretation boundary.

### Specification-level results

Check:

- [ ] all valid declared branches are represented;
- [ ] effect direction and magnitude are inspected separately;
- [ ] technical failures are counted and described;
- [ ] a preferred specification is not selected merely because it supports the desired conclusion.

### Effect stability

Check:

- [ ] empirical quantiles are described as summaries of the declared specification set;
- [ ] sign fractions are not described as posterior probabilities;
- [ ] stability across analytical choices is not presented as evidence that the underlying causal model is correct;
- [ ] a stable sign is not used to hide practically important magnitude variation.

### Marginal and pairwise sensitivity

Check:

- [ ] sensitivity summaries are treated as descriptive contrasts across the declared analytical space;
- [ ] larger movement is not automatically called a causal contribution;
- [ ] pairwise non-additivity is not described as mechanism identification;
- [ ] sparse or structurally constrained combinations are interpreted cautiously.

### Perturbation and recovery analyses

Check:

- [ ] the reference condition and recovery rule were declared before interpretation;
- [ ] direction recovery and magnitude recovery are reported separately when the protocol distinguishes them;
- [ ] the tested perturbation range is stated explicitly;
- [ ] conclusions do not extend to uncertainty dimensions that were not perturbed.

## 4. Before publication: bind evidence to wording

The publication record should allow another researcher to answer four questions: **What was fixed? What varied? What failed? What claim followed?**

- [ ] Methods identify the canonical study representation and relevant source provenance.
- [ ] Methods distinguish researcher-owned decisions from package-generated diagnostics.
- [ ] The declared specification factors and invalid combinations are described.
- [ ] The endpoint is defined once and used consistently.
- [ ] The Results section reports the full robustness pattern rather than only one preferred branch.
- [ ] Descriptive robustness outputs are not described as confidence intervals, posterior probabilities, p-values, causal decompositions, or model-selection evidence unless an independent method genuinely supplies that inferential object.
- [ ] Incomplete or failed branches that affect interpretation are disclosed.
- [ ] The exact GazeAudit release or commit used for analysis is recorded.
- [ ] Relevant manifests, fingerprints, source locks, and output tables are retained in the archive.
- [ ] Limitations identify uncertainty dimensions that were **not** audited.

## A compact stop/go review

Before moving from one stage to the next, use these questions.

| Stage | Continue when… | Stop and resolve when… |
|---|---|---|
| Source → QC | identity, units, ordering, and structural mapping are explicit | canonical mapping or participant/trial identity is ambiguous |
| QC → specifications | QC flags have explicit researcher decisions where required | a diagnostic is being converted into an exclusion without justification |
| specifications → summaries | the declared valid space has been executed and failures are visible | branches were added/removed after seeing estimates |
| summaries → reporting | interpretation matches the generated evidence object | descriptive robustness is being upgraded into inferential or causal language |
| reporting → archive | methods, outputs, provenance, and software identity agree | the manuscript cannot be reconstructed from the preserved record |

## Common failure patterns

### “The QC tool told us to exclude these participants”

Structural-QC output identifies conditions that may require investigation. A scientific exclusion still needs an explicit study-specific rule and rationale.

### “Most specifications were significant”

A GazeAudit specification space is not automatically a collection of independent hypothesis tests. Report the endpoint behaviour across the declared analytical choices using the quantities actually computed.

### “The sign never changed, so the result is robust”

Sign stability may coexist with large magnitude variation. State which robustness criterion was used and whether direction and magnitude tell the same story.

### “This factor caused most of the variation”

Marginal and pairwise sensitivity are descriptive summaries of endpoint movement across the declared specification set. They do not by themselves identify causal contributions.

### “The analysis is reproducible, therefore the conclusion is valid”

Reproducibility preserves what was run. It does not establish that the scientific choices, data-generating assumptions, or interpretation are valid.

## Recommended working sequence

1. Create the project structure with [Project starter]({{ '/docs/guides/project-starter/' | relative_url }}).
2. Copy the [decision-log template]({{ '/docs/guides/audit-decision-log-template/' | relative_url }}) into the study repository.
3. Run the [first real audit]({{ '/docs/guides/first-real-audit/' | relative_url }}) or the [first-study workflow]({{ '/docs/workflows/first-study-audit/' | relative_url }}).
4. Use this checklist before interpreting the output bundle.
5. Work through the [decision-to-report example]({{ '/docs/examples/decision-to-report/' | relative_url }}) to see how the same synthetic robustness results can be translated into bounded reporting language.
6. Finish with the [reproducible-publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}).

## Boundary reminder

This checklist is a governance aid for transparency and reviewability. It cannot substitute for domain expertise, study design knowledge, measurement validity, or a defensible statistical model. The goal is to make researcher judgement **visible and auditable**, not to automate it.
