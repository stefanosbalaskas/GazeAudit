---
title: Execution ledger and recovery
description: Methodological guidance for preserving GazeAudit branch attempts, technical failures, non-finite endpoints, not-run states, repairs, reruns, current-state reconciliation, temporal evidence layers, and denominator-aware reporting.
kicker: Guide · Execution evidence
permalink: /docs/guides/execution-ledger-recovery/
search_category: Guide
search_keywords: execution ledger failure recovery technical failure non finite not run repair rerun attempt history denominator run_specs provenance
---

# Execution ledger and recovery

Use this guide when a declared valid specification space does not execute cleanly or when a repair/rerun creates more than one attempt for the same scientific branch.

The companion [Execution Ledger & Recovery Center]({{ '/docs/execution-ledger/' | relative_url }}) provides a governed state reference and a documentation-side attempt-record builder.

## 1. Keep branch identity separate from attempt identity

A **scientific branch** is defined by the declared factor values and endpoint identity.

An **attempt** is one execution event for that branch.

A branch can therefore have:

```text
branch S06
├── attempt-01: technical_failure
└── attempt-02: repair_rerun_success
```

The repaired attempt does not create a second scientific specification.

This distinction prevents historical attempt rows from inflating the valid specification denominator.

## 2. Keep validity separate from execution state

Validity is decided before execution.

Execution state records what happened when a valid branch was attempted—or why it was not attempted.

### Invalid before execution

A declared combination rejected by the pre-execution scientific validity rule.

It belongs to the declared space but not the valid execution denominator.

### Successful

A valid branch that completes the declared processing/endpoint contract and yields an accepted endpoint.

### Technical failure

A valid branch whose processor or endpoint raises.

It remains in the valid denominator.

### Non-finite endpoint

A valid attempted branch that yields `NaN` or infinity.

It remains in the valid denominator and must not be interpreted as zero.

### Not run

A declared branch that was not attempted.

If it was scientifically valid, it remains unresolved in the valid denominator.

### Successful repair rerun

A new attempt for the same valid scientific branch after a documented technical repair.

The prior failure remains in history.

## 3. Do not invent package runtime statuses

Core `run_specs()` does not return a status column.

Successful calls produce rows containing:

- specification fields;
- `spec_id`;
- `estimate`.

If a valid branch raises, the exception propagates.

Therefore terms such as:

- `technical_failure`;
- `not_run`;
- `repair_rerun_success`;

are documentation/audit vocabulary.

Use them in an explicit outer ledger when needed, but do not describe them as package enum values.

## 4. Preserve the failure before debugging

Before changing code, record:

- branch ID;
- attempt ID;
- factor values;
- endpoint reference;
- source/representation/software identity;
- exact exception type;
- exact exception message;
- failing layer when known;
- relevant outcomes already inspected?;
- timestamp or temporal evidence layer.

The point is to make the original failure reconstructable after the code is fixed.

## 5. Diagnose the causal layer

Useful layers include:

- environment;
- source/schema;
- structural representation;
- processor;
- measurement model;
- endpoint inputs;
- endpoint calculation;
- output writing;
- package/integration boundary.

A branch failure does not by itself prove that the scientific specification was invalid.

## 6. Repair the causal defect, not the scientific result

A technical repair should change the implementation defect required to execute the **same scientific branch**.

Examples:

- correct a misspelled condition label;
- repair an incorrect column mapping;
- update a parser that dropped required fields;
- fix a deterministic software defect;
- restore a missing dependency/environment requirement.

A repair becomes a scientific amendment when it changes:

- endpoint;
- factor level;
- validity rule;
- eligibility;
- missingness assumption;
- AOI definition;
- detector rule;
- another substantive analytical decision.

Do not call a scientific amendment a technical repair merely because it makes the branch run.

## 7. Rerun the same branch where possible

A repair rerun should retain:

- the same branch ID;
- a new attempt ID;
- prior attempt ID;
- repair record reference;
- unchanged scientific factor values;
- unchanged endpoint reference;
- new software/representation identity when applicable.

This gives a lineage:

```text
S06 / A01 / technical_failure
          ↓
repair R01
          ↓
S06 / A02 / repair_rerun_success
```

## 8. Non-finite endpoints require their own evidence

Because Python `float(...)` accepts `NaN` and infinity, core `run_specs()` does not automatically reject them.

If your surrounding endpoint contract requires finite values, check explicitly.

Preserve:

- exact non-finite value;
- branch/attempt identity;
- endpoint reference;
- input diagnostics relevant to the failure;
- declared non-finite policy;
- repair/rerun history, if any.

Do not convert `NaN` to zero.

## 9. Not-run branches need an explicit reason

Examples:

- external compute interruption;
- dependency unavailable;
- data source temporarily inaccessible;
- branch intentionally deferred under a dated amendment;
- execution window closed before completion.

Do not use “not run” as a vague catch-all for:

- invalidity;
- technical failure;
- non-finite endpoint;
- deliberate post-result removal.

If the branch was valid, it remains part of the unresolved valid denominator.

## 10. Reconcile current branch state separately from attempt history

Suppose:

```text
7 valid branches
6 successful on first attempt
1 technical failure on first attempt
1 repair rerun for that failed branch, now successful
```

Current branch state:

```text
7 / 7 valid branches currently represented successfully
```

Historical attempt record:

```text
8 attempts total
7 success events
1 technical failure event
```

Both are correct.

They answer different questions.

Do not report “7/8 branches successful” simply because there are eight attempt rows.

## 11. Reconciliation equations

At the branch level:

```text
declared
= invalid_before_execution
+ valid
```

For current valid branch state:

```text
valid
= current_success
+ unresolved_technical_failure
+ unresolved_non_finite
+ valid_not_run
```

At the attempt-history level:

```text
attempt rows
= initial attempts
+ repair/retry attempts
+ other explicitly recorded execution events
```

Attempt rows are not the specification denominator.

## 12. Preserve outcome-inspection timing

For every repair or rerun, record whether relevant results were already known.

This matters because a later “technical” decision can become outcome-informed if the repair changes scientific choices.

Useful timing fields:

- before any endpoint inspection;
- after partial endpoint inspection;
- after full original results;
- reviewer-requested;
- correction after publication/submission.

Do not rewrite a post-result change as predeclared.

## 13. Use status-specific evidence requirements

### Successful

Preserve:

- finite estimate;
- branch/attempt identity;
- endpoint identity;
- source/software identity.

### Technical failure

Preserve:

- exception type/message;
- branch/attempt identity;
- failing layer;
- diagnostic evidence;
- repair link if resolved.

### Non-finite endpoint

Preserve:

- exact non-finite value;
- endpoint inputs relevant to diagnosis;
- declared endpoint policy;
- repair link if resolved.

### Not run

Preserve:

- reason;
- branch validity;
- timing;
- closure or rerun plan.

### Repair rerun

Preserve:

- prior attempt;
- repair description/reference;
- unchanged scientific branch;
- new current estimate/state.

## 14. Keep repair scope minimal

After a technical correction, rerun the smallest scope that restores the causal evidence while maintaining consistency.

Examples:

- one branch if the defect was branch-specific;
- all branches using a corrected shared processor;
- structural preflight plus all downstream analyses if the canonical representation changed;
- entire endpoint family if the endpoint implementation changed.

The appropriate rerun scope depends on what the repair changed.

Do not rerun only the favourable subset.

## 15. When the repair changes representation

If the source/canonical table changes:

1. preserve original source identity;
2. record the transformation;
3. create a new representation identity/fingerprint;
4. rerun structural preflight;
5. rerun all downstream branches dependent on that representation;
6. link old and new attempts.

A representation repair can have broader consequences than a local software bug.

## 16. When the repair changes the endpoint

That is not a same-branch technical rerun.

Create a separate endpoint declaration and, when timing differs, a separate amendment layer.

The original failed attempt remains tied to the original endpoint.

## 17. When the repair changes validity

Be especially careful.

If a branch was valid under the rule fixed before execution, a later failure is not enough to justify changing `valid_if`.

A new validity rule may be defensible only if there is independent scientific evidence for the amendment.

Record it as an amendment, not as a retroactive correction of history.

## 18. Build downstream summaries from reconciled current state

After recovery:

- identify one current state per valid scientific branch;
- exclude superseded failed attempts from numerical robustness summaries;
- retain those attempts in provenance/history;
- keep unresolved valid branches visible in completeness reporting;
- rebuild robustness summaries only after reconciliation.

The historical ledger and the current branch table should be different artifacts.

## 19. Reporting a repaired execution

### Methods

> We preserved branch-level execution attempts in a separate audit ledger. A valid branch that failed technically remained in the valid denominator. The causal implementation defect was repaired without changing the endpoint, factor values, eligibility, or validity rule, and the same branch was rerun under a new attempt ID linked to the original failure.

### Results

> Six of seven valid branches succeeded initially. One valid branch failed technically. After a documented technical repair, the same branch was rerun successfully, yielding seven currently represented valid branches. The original failure event remained in the attempt history.

### Limitation

> The recovery ledger establishes execution lineage and current branch completeness. It does not independently establish that the scientific specification space, endpoint, validity rule, or repair was substantively correct.

## 20. Reporting unresolved execution

### Results

> Six of seven valid specifications successfully produced the declared endpoint. One valid branch remained unresolved after technical failure and therefore the audit remained incomplete relative to the valid denominator.

Do not write:

> All completed analyses agreed.

That sentence silently substitutes the successful denominator for the valid denominator.

## 21. Recovery checklist

Before closing a failure:

- [ ] branch ID preserved;
- [ ] attempt ID preserved;
- [ ] scientific validity preserved separately;
- [ ] exact failure/non-finite/not-run evidence preserved;
- [ ] outcome-inspection timing recorded;
- [ ] causal layer diagnosed;
- [ ] technical versus scientific change classified;
- [ ] repair record created;
- [ ] same-branch identity retained where appropriate;
- [ ] new attempt linked to prior attempt;
- [ ] source/software identity updated if changed;
- [ ] current branch state reconciled;
- [ ] historical attempt record retained;
- [ ] downstream summaries rebuilt from reconciled current state;
- [ ] manuscript denominator reflects valid branches, not attempt rows.

## API and reference links

- [`run_specs()`]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [`PipelineSpace`]({{ '/docs/reference/api-pathways/#api-pipelinespace' | relative_url }})
- [Evidence and denominator vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }})
- [Execution Ledger & Recovery Center]({{ '/docs/execution-ledger/' | relative_url }})
- [Machine-readable execution-state reference]({{ '/assets/execution-state-reference.json' | relative_url }})
- [Troubleshooting GazeAudit]({{ '/docs/guides/troubleshooting/' | relative_url }})
- [Failed-audit recovery]({{ '/docs/examples/failed-audit-recovery/' | relative_url }})

## Worked exercise

Continue to [Failure → repair → reconciliation]({{ '/docs/examples/execution-ledger-reconciliation/' | relative_url }}) to reconcile one predeclared-invalid combination, one technical failure, one non-finite endpoint, one not-run branch, and two successful repair attempts without changing the scientific branch denominator.
