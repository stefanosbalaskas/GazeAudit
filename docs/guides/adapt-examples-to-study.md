---
title: Adapt a synthetic example to your study
description: Move from a GazeAudit teaching example to a real study without copying demonstration values, software defaults, endpoints, exclusions, or evidence claims as scientific decisions.
kicker: Guide · Examples
permalink: /docs/guides/adapt-examples-to-study/
search_category: Guide
search_keywords: adapt example own data synthetic teaching values defaults thresholds endpoint exclusions aoi specification study decisions handoff real study
---

# Adapt a synthetic example to your study

Use this guide after a GazeAudit example has helped you understand a workflow and you are ready to apply the same **structure** to a real study.

The core rule is simple:

> **Copy the workflow shape. Rebuild the scientific decisions.**

Synthetic examples are teaching material. Their thresholds, AOIs, endpoint definitions, perturbation levels, sampling choices, missingness settings, random seeds, and other concrete values are not automatically appropriate for your data.

<div class="callout warning">
<strong>Do not promote demonstration values into study defaults.</strong>
A value can be reasonable for a synthetic example because it makes the mechanism visible, the output stable, or the code compact. That does not make it a justified scientific choice for another design.
</div>

## 1. Separate four kinds of content

When reading an example, classify each important element before copying it.

| Element | What it means | What to do for your study |
|---|---|---|
| **software structure** | imports, object construction, function order, output writing | usually safe to reuse after checking the current API |
| **teaching value** | concrete value chosen to make the example understandable or deterministic | replace or justify; never inherit silently |
| **study decision** | endpoint, QC rule, AOI, exclusion, perturbation, validity predicate, model choice | declare from your design, protocol, literature, or sensitivity plan |
| **evidence statement** | interpretation tied to synthetic or frozen outputs | do not transfer; derive a new statement from your own complete record |

This classification is more important than whether a line is technically copyable.

## 2. Bind the real source first

Before adapting analysis code, establish which file or object is the canonical input for the study.

Record at minimum:

- source file or immutable source identifier;
- participant and trial identifiers;
- coordinate columns and units;
- timestamp column and unit;
- condition/stimulus fields needed by the endpoint;
- provenance needed to reproduce the import.

Then construct the canonical representation deliberately rather than assuming that the example's column names match your export.

A structural pattern such as:

```python
study = GazeStudy(
    data,
    x="x",
    y="y",
    timestamp="timestamp",
    participant="participant",
    trial="trial",
)
```

shows the constructor contract. The literal column names are not instructions to rename every study that way.

## 3. Inventory every demonstration value

Before running the real analysis, make a short table of values that came from the example.

For a robustness workflow this might include:

- quality thresholds;
- detector settings;
- AOI dimensions or margins;
- sampling rates;
- missingness fractions or mechanisms;
- specification factors;
- validity rules;
- endpoint definition;
- random seed;
- Monte Carlo draws;
- conclusion-recovery tolerance.

For each item, mark one of:

- **retain as software behavior**;
- **replace with study-specific value**;
- **include as one declared sensitivity level**;
- **not applicable**.

If you cannot explain why a scientific value is present, do not run the final study with it yet.

## 4. Rebuild the endpoint from the research question

Examples often need a simple scalar endpoint so the mechanics stay visible. Your study may need a different endpoint, aggregation level, denominator, or statistical model.

Write the endpoint in words before writing it in code:

> For each declared specification, the endpoint is …

Then verify:

- unit of analysis;
- grouping structure;
- direction/sign convention;
- handling of missing or invalid observations;
- whether the same endpoint is computed under every valid specification;
- whether the endpoint has been changed after inspecting outcomes.

A new endpoint is a new scientific record, not merely a code refactor.

## 5. Rebuild the specification space

Do not copy a synthetic `PipelineSpace` merely because it runs.

Start from defensible alternatives for the real study:

```python
space = PipelineSpace(
    choices=declared_choices,
)
```

Here `declared_choices` is intentionally symbolic. It should be built from the study's design, preprocessing plan, measurement assumptions, relevant literature, and sensitivity questions.

For every factor ask:

1. Why is this factor scientifically relevant?
2. Why are these levels defensible?
3. Which combinations are invalid before execution?
4. Is the factor a scientific choice, a technical implementation detail, or a stress test?
5. Will every valid branch compute the same endpoint?

Use [Specification-space robustness]({{ '/docs/guides/specification-space/' | relative_url }}) for the full workflow.

## 6. Rebuild AOIs and measurement assumptions

An AOI from a synthetic example is especially unsafe to copy literally because geometry depends on stimulus layout, display scaling, coordinate system, and the construct being operationalised.

For real data:

- bind AOI geometry to the actual stimulus;
- record coordinate units and transformations;
- distinguish hard membership from uncertainty-aware membership;
- justify measurement-error assumptions separately from AOI geometry;
- preserve the relationship between calibration/validation evidence and any propagated error model.

Use the [AOI uncertainty guide]({{ '/docs/guides/aoi-uncertainty/' | relative_url }}) when spatial uncertainty matters.

## 7. Treat software defaults as interface behavior

A function default answers:

> “What happens if Python receives no explicit value?”

It does not answer:

> “What value should my experiment use?”

For example, a default number of Monte Carlo draws, a default missingness mechanism, or a default tolerance can be appropriate software behavior while still requiring explicit scientific consideration in a particular analysis.

The [source-level API reference guide]({{ '/docs/guides/read-api-reference/' | relative_url }}) separates callable contracts from research decisions.

## 8. Run structural preflight before the scientific audit

A teaching example normally starts from clean, known data. Real data should not.

Before downstream robustness or uncertainty analysis:

1. map the source into `GazeStudy`;
2. run structural QC;
3. inspect row/trial/participant diagnostics;
4. distinguish repairable structural problems from researcher-owned exclusions;
5. record any repair or readiness policy;
6. only then run the declared scientific specification space.

Use [Data onboarding and structural preflight]({{ '/docs/guides/data-onboarding/' | relative_url }}) and [Analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}).

## 9. Preserve the handoff in a decision record

Keep a short adaptation record containing:

| Field | Record |
|---|---|
| example used | page/commit or release |
| software structure reused | imports, call order, output pattern |
| teaching values encountered | list |
| study-specific replacements | value + rationale/source |
| omitted example components | reason |
| newly added study decisions | rationale/source |
| endpoint definition | exact text |
| declared specification space | factors and levels |
| validity rules | pre-execution rules |
| software identity | release/commit + environment |

This makes it possible to distinguish “we followed the example's workflow pattern” from “we inherited the example's analytical choices.”

## 10. Verify the complete execution record

After running:

- confirm the declared denominator;
- confirm how many specifications were valid;
- preserve valid technical failures;
- verify endpoint consistency;
- inspect sensitivity rather than selecting a convenient branch;
- keep synthetic-example outputs out of the empirical evidence record;
- report study results from the study record only.

A successful run establishes execution, not scientific validity.

## Safe handoff checklist

Before treating an adapted example as part of the real analysis, verify:

- [ ] the canonical source is bound;
- [ ] semantic columns and units are explicit;
- [ ] every teaching value has been classified;
- [ ] the endpoint is written in words;
- [ ] AOIs and measurement assumptions come from the real study;
- [ ] QC/exclusion rules are researcher-owned and recorded;
- [ ] the specification space is declared from defensible alternatives;
- [ ] software defaults have not been mistaken for scientific defaults;
- [ ] valid technical failures remain in the execution record;
- [ ] the environment/revision is recorded;
- [ ] no synthetic output is being cited as empirical evidence.

For a worked transformation, continue to [Example → study handoff]({{ '/docs/examples/example-to-study-handoff/' | relative_url }}).
