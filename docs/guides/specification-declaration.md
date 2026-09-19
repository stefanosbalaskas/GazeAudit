---
title: Specification-space declaration and validity
description: Methodological guidance for declaring GazeAudit PipelineSpace factors, levels, timing, endpoint identity, pre-execution validity rules, reference branches, technical-failure policy, and declared/valid/successful denominators before robustness execution.
kicker: Guide · Analytical robustness
permalink: /docs/guides/specification-declaration/
search_category: Guide
search_keywords: specification space declaration PipelineSpace factors levels valid_if declared valid successful denominator timing rationale failure policy multiverse
---

# Specification-space declaration and validity

Use this guide **before** running a robustness analysis.

A useful specification space is not a large grid. It is a documented set of scientifically defensible choices whose consequences you actually want to understand.

Start with the [Specification Space Declaration Center]({{ '/docs/specification-declaration/' | relative_url }}) when you want to build the declaration interactively.

## 1. Fix the common endpoint first

Before declaring factors, define the scientific quantity every valid branch will estimate.

Use the [Endpoint Definition & Handoff Center]({{ '/docs/endpoint-contract/' | relative_url }}).

If different branches answer different scientific questions, they do not belong in one ordinary common-endpoint specification curve merely because they share input data.

## 2. State the robustness question

A good declaration starts with a question such as:

> How much does the treatment-minus-control target-AOI dwell contrast change across the two defensible detector families, two prespecified QC policies, and two AOI representations used in this study?

This makes the factor set interpretable.

Weak:

> Try lots of reasonable settings.

The second statement does not define the intended decision space or its boundary.

## 3. Include factors because they are scientifically defensible, not because they are configurable

Potential factors can include:

- detector family;
- detector parameter;
- QC/readiness policy;
- missing-data handling;
- AOI definition or uncertainty representation;
- sampling representation;
- preprocessing;
- inclusion rule;
- another declared analytical choice.

A software parameter is not automatically a scientific factor.

For every factor, record why it can plausibly vary.

## 4. Give every level a rationale

A factor level should be defensible independently of the observed endpoint.

Possible rationale sources:

- preregistration;
- protocol;
- instrument or algorithm validation;
- established methodological alternatives;
- sensitivity bounds fixed before result inspection;
- reviewer-requested analysis, clearly labelled post-review;
- legacy/reference pipeline retained for continuity.

Avoid level sets chosen because:

- they bracket the observed estimate conveniently;
- one level produces the expected sign;
- one level reaches significance;
- a dense grid makes the audit look more comprehensive.

## 5. Keep factor names unique

`PipelineSpace.add_choice(name, values)` stores choices in a mapping.

If the same name is added again, the later mapping replaces the earlier one.

The documentation builder therefore rejects duplicate factor names.

This is a documentation guardrail, not a change to the package runtime.

Use stable names that make exported tables readable:

```python
space = (
    PipelineSpace()
    .add_choice("detector", ["ivt", "idt"])
    .add_choice("qc_policy", ["moderate", "strict"])
    .add_choice("aoi_mode", ["hard", "probabilistic"])
)
```

## 6. Preserve typed levels

These are different declarations:

```python
.add_choice("threshold", [1, 2])
```

and:

```python
.add_choice("threshold", ["1", "2"])
```

The browser builder supports:

- text;
- finite numbers;
- booleans.

It does not infer scientific units from numeric levels.

If `0.05` means a fraction, millimetres, degrees, or seconds, document that meaning in the factor rationale.

## 7. Calculate the declared denominator before execution

`PipelineSpace.size` returns the Cartesian product of all factor level counts.

For:

- detector: 2 levels;
- QC policy: 2 levels;
- AOI mode: 2 levels;

the declared space is:

```text
2 × 2 × 2 = 8 declared combinations
```

This count exists before a validity predicate is applied.

Record it.

## 8. Separate declared from valid

A `valid_if` predicate removes scientifically inadmissible combinations **before execution**.

Example:

```python
def valid_spec(spec):
    if spec["detector"] == "idt" and spec["qc_policy"] == "strict":
        return False
    return True
```

If both AOI modes exist, that rule removes two of the eight declared combinations:

```text
8 declared
6 valid
```

The invalid combinations remain part of the declared-space record.

Do not describe the study as having only six declared specifications.

## 9. Validity rules must be independent of the endpoint result

Appropriate validity logic can encode:

- impossible parameter/model combinations;
- methods that require inputs another branch cannot produce by design;
- combinations ruled out by protocol;
- logically incompatible representation choices.

Do not encode:

```python
return estimate > 0
```

or another outcome-dependent rule.

That would transform result selection into supposed pre-execution validity.

## 10. Invalid-before-execution is not technical failure

These are different states.

### Invalid before execution

A declared combination is rejected by the fixed scientific rule before the processor/endpoint path is attempted.

It does not belong in the valid execution denominator.

### Valid technical failure

A scientifically admissible branch is attempted but raises or cannot produce the declared endpoint.

It remains in the valid denominator.

Example:

```text
8 declared
6 valid
5 successful
1 valid technical failure
2 invalid before execution
```

Report:

> 5 successful / 6 valid

not:

> 5 / 5

## 11. A non-finite endpoint is not predeclared invalidity

If a valid branch returns `NaN` or infinity, that happened during endpoint execution.

Do not retrospectively change `valid_if` to make the branch disappear from the valid denominator.

Use the endpoint/failure policy to determine how the non-finite event is preserved.

## 12. Reference specifications are optional

A project may define one reference pipeline.

Possible reasons:

- preregistered primary analysis;
- legacy analysis for continuity;
- conventional pipeline used for comparison.

The reference branch can orient plots or narrative.

It does not automatically receive greater scientific truth value.

Do not define the reference after inspecting which branch is most favourable.

## 13. Declare the execution-failure policy before running the space

Decide how your audited workflow will represent:

- processor exception;
- endpoint exception;
- missing required endpoint input;
- non-finite endpoint;
- branch not run.

GazeAudit core `run_specs()` stops when an exception propagates.

If your project uses an outer ledger/recovery workflow that continues other branches, preserve:

- branch identity;
- failure type;
- original error;
- timing;
- any repair;
- same-branch rerun linkage.

Do not silently drop the failed row.

## 14. Record declaration timing

Useful timing labels include:

- preregistered;
- protocol-fixed before analysis;
- analyst-declared before outcome inspection;
- post hoc sensitivity;
- reviewer-requested amendment;
- correction.

A useful post-review factor can still be scientifically informative.

It should not be rewritten as part of the original submitted space.

## 15. Keep reviewer-requested additions separate when timing differs

Suppose the submitted audit contains:

```text
8 declared
8 valid
8 successful
```

A reviewer then requests four additional sensitivity combinations.

Record:

```text
submitted: 8 declared / 8 valid / 8 successful
post-review amendment: 4 declared / 4 valid / 4 successful
```

Do not rewrite this as one apparently predeclared 12-specification space.

If the endpoint also changes, preserve that as a separate endpoint amendment.

## 16. Avoid specification explosion

A larger Cartesian product is not automatically better.

Before adding another factor or level, ask:

- What scientific uncertainty does it represent?
- Is the level defensible?
- Does it preserve the endpoint?
- Is it independent of the observed result?
- Is it computationally and interpretively manageable?
- Will the audit still support complete branch accounting?

Do not add decorative factors merely to produce a larger multiverse.

## 17. Consider dependencies among factors

In some spaces, factor levels are not independent.

That matters for:

- validity;
- balance;
- sensitivity summaries;
- interpretation.

A `valid_if` predicate can make the valid space unbalanced.

Descriptive marginal/pairwise sensitivity diagnostics can then overlap or be harder to interpret.

Document that structure rather than pretending the valid space is a full factorial design.

## 18. Preserve the complete branch identity

Each represented result should remain traceable to:

- factor names;
- factor levels;
- valid/invalid status;
- execution status;
- endpoint identity;
- software identity;
- timing layer.

A robustness conclusion is about the pattern across branches, not only the estimates.

## 19. Test the declaration on synthetic truth before the real audit

Useful contract tests include:

### Enumeration

Verify the expected Cartesian count.

### Validity

Verify exactly which combinations the pre-execution predicate rejects.

### Determinism

Verify repeated enumeration yields the same ordering.

### Endpoint invariance

Confirm representative valid branches still estimate the declared common endpoint.

### Failure preservation

Confirm valid technical failures remain visible in the audit ledger.

### Denominator accounting

Check:

```text
declared = valid + invalid-before-execution
valid = successful + valid-failure/not-run states
```

within the project's explicit ledger vocabulary.

## 20. Reporting the declaration

### Methods

> We declared an eight-combination analytical specification space before endpoint inspection, crossing detector family (IVT/IDT), QC policy (moderate/strict), and AOI representation (hard/probabilistic). A pre-execution rule classified IDT + strict combinations as scientifically inadmissible under the declared protocol, yielding six valid specifications. Every valid branch targeted the same prespecified endpoint.

### Results

> Five of six valid specifications successfully produced the endpoint; one valid branch failed technically and remained in the valid denominator. The two predeclared-invalid combinations were documented separately and were not reclassified as technical failures.

### Limitation

> The robustness audit is bounded by the declared factors, levels, validity predicate, and endpoint. Choices outside this space were not evaluated and should not be inferred to be robust.

## 21. Specification declaration checklist

Before execution:

- [ ] common endpoint declaration exists;
- [ ] robustness question stated;
- [ ] each factor is scientifically motivated;
- [ ] every level has a rationale;
- [ ] factor names are unique;
- [ ] numeric level units are documented;
- [ ] declared Cartesian count recorded;
- [ ] validity rule fixed before estimates;
- [ ] invalid combinations documented;
- [ ] reference branch timing recorded, if used;
- [ ] execution-failure policy declared;
- [ ] non-finite endpoint policy declared;
- [ ] temporal evidence layer recorded;
- [ ] untested uncertainty dimensions listed;
- [ ] branch identity/provenance plan defined.

## API links

- [`PipelineSpace`]({{ '/docs/reference/api-pathways/#api-pipelinespace' | relative_url }})
- [`run_specs()`]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [`specification_curve()`]({{ '/docs/reference/api-pathways/#api-specification-curve' | relative_url }})
- [`effect_stability()`]({{ '/docs/reference/api-pathways/#api-effect-stability' | relative_url }})
- [Specification Space Declaration Center]({{ '/docs/specification-declaration/' | relative_url }})
- [Machine-readable declaration fields]({{ '/assets/specification-declaration-reference.json' | relative_url }})

## Worked exercise

Continue to [Declared → valid → successful]({{ '/docs/examples/specification-denominator-audit/' | relative_url }}) for a fully synthetic 8 → 6 → 5 denominator exercise with one explicit invalidity rule and one valid technical failure.
