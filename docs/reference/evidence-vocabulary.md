---
title: Evidence and denominator vocabulary
description: Exact GazeAudit terminology for declared and valid specifications, execution outcomes, non-finite endpoints, temporal evidence layers, and frozen validation labels.
kicker: Reference · Vocabulary
page_type: reference
permalink: /docs/reference/evidence-vocabulary/
search_category: Reference
search_keywords: status glossary vocabulary declared valid invalid technical failure not run non finite denominator incomplete robust negative materially fragile
---

# Evidence and denominator vocabulary

This reference distinguishes **package runtime contracts** from **documentation/audit vocabulary**. That distinction matters: some terms on this page describe how researchers should preserve an execution record, but are not enum values returned by `run_specs()`.

<div class="callout warning">
<strong>Do not convert bookkeeping terms into scientific conclusions.</strong>
“Valid”, “successful”, “technical failure”, “incomplete”, and the frozen case labels answer different questions. None is a universal data-quality score.
</div>

## Specification-space terms

| Term | Exact meaning in GazeAudit | Denominator consequence |
|---|---|---|
| declared combination | one combination in the Cartesian product represented by `PipelineSpace`; `PipelineSpace.size` reports the declared count | belongs to the declared-space count |
| `valid_if` | optional predicate passed to `enumerate_specs()` or `run_specs()` to reject combinations before execution | defines which declared combinations enter the valid set |
| valid specification | a specification returned by `PipelineSpace.enumerate_specs(valid_if=...)` | belongs to the valid execution denominator |
| invalid before execution | documentation term for a declared combination rejected by the pre-execution validity rule | documented separately; does **not** belong to the valid execution denominator |
| evaluated specification | a valid specification for which the processing/endpoint path is attempted | should remain traceable even if execution fails |

Validity rules are researcher-owned scientific constraints. GazeAudit enumerates them; it does not decide which combinations are scientifically defensible.

## Execution terms

| Term | Runtime or documentation? | Meaning |
|---|---|---|
| `spec_id` | runtime field from `run_specs()` | deterministic integer identifier for each successfully collected result row |
| `estimate` | runtime field from `run_specs()` | `float(...)` conversion of the common scalar endpoint returned by the endpoint callable |
| successful execution | audit vocabulary | processor and endpoint complete and the result is accepted by the surrounding workflow's endpoint checks |
| technical failure | audit/recovery vocabulary, **not a `run_specs()` enum** | a valid branch raises during processing or endpoint evaluation and therefore does not yield a normal result row |
| not run | audit vocabulary | an execution target was not attempted; the reason must be preserved rather than silently treating it as success or invalidity |
| non-finite endpoint | audit vocabulary around the endpoint contract | endpoint produces `NaN` or infinity; this is not evidence of a zero/null effect |

### Important `run_specs()` behavior

`run_specs()` enumerates valid specifications, executes them sequentially, converts each endpoint result with `float(...)`, and appends one row containing the specification plus `estimate`.

Two consequences follow:

1. if the processor or endpoint raises, the exception propagates; `run_specs()` does **not** create a `technical_failure` row for you;
2. `float(...)` accepts values such as `NaN` and infinity, so `run_specs()` itself does **not** enforce finiteness.

If finiteness is part of the endpoint contract, check it explicitly in the audited wrapper before interpretation. The [Execution Ledger & Recovery Center]({{ '/docs/execution-ledger/' | relative_url }}) defines the documentation-side execution states and attempt record, while the [failed-audit recovery walkthrough]({{ '/docs/examples/failed-audit-recovery/' | relative_url }}) demonstrates one explicit ledger pattern.

## Denominator terms

| Denominator | What belongs in it |
|---|---|
| declared | every combination in the declared `PipelineSpace` |
| valid | only combinations that survive the pre-execution validity rule |
| successful | valid branches that complete under the stated execution/endpoint contract |
| post-review valid | valid branches introduced by a reviewer-requested amendment, kept separate from the submitted denominator when timing differs |

Example:

```text
8 declared
7 valid
6 initially successful
1 valid technical failure
1 invalid-before-execution combination
```

The execution summary is **6 successful / 7 valid**, not `6 / 6`. The invalid-before-execution combination remains documented but is not recast as a technical failure.

## Temporal evidence terms

| Term | Meaning |
|---|---|
| submitted evidence | analysis record available at submission time |
| post-review amendment | analysis added after reviewer/editor feedback; timing must remain visible |
| separate endpoint amendment | reviewer-requested analysis whose endpoint is different from the submitted endpoint and therefore should not be folded into the original endpoint denominator |
| superseded evidence | an earlier record replaced by a correction but retained so history remains reconstructable |

Combining temporally distinct analyses into one apparently pre-specified denominator rewrites the provenance boundary.

## Frozen scientific-validation labels

The following labels are **case-specific canonical outcomes**, not generic runtime statuses:

| Label | Canonical case | Meaning boundary |
|---|---|---|
| `incomplete` | GazeBase | the frozen completeness gate was not satisfied |
| `robust_negative` | Korthals | the negative paired AOI effect survived the frozen uncertainty model |
| `materially_fragile` | Pedrotti/de Chambrier | the endpoint changed materially under the frozen perturbation protocol |

Use the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) for the authoritative protocol-bound claims. Do not assign these labels to synthetic teaching data merely because an example looks similar.

## Structural validation is not scientific validation

A passing structural-QC rule, readiness policy, artifact verifier, or revision-package validator establishes only the contract each tool actually checks. It does not establish scientific validity, causal identification, measurement validity, universal robustness, manuscript quality, or publication readiness.

For action-oriented recovery, use [Troubleshooting GazeAudit]({{ '/docs/guides/troubleshooting/' | relative_url }}). For reporting-language boundaries, use the [Results Interpretation & Reporting Center]({{ '/docs/reporting-center/' | relative_url }}). For a compact synthetic lookup exercise, use the [reference lookup walkthrough]({{ '/docs/examples/reference-lookup-workflow/' | relative_url }}).
