---
title: Failure → repair → reconciliation
description: A fully synthetic GazeAudit execution-ledger example that preserves one invalid combination, one valid technical failure, one non-finite endpoint, one valid not-run branch, and successful repair reruns without changing the scientific specification denominator.
kicker: Example · Execution recovery
page_type: example
permalink: /docs/examples/execution-ledger-reconciliation/
search_category: Example
search_keywords: execution ledger repair rerun technical failure non finite not run invalid denominator attempt branch reconciliation synthetic
example_data: "Synthetic"
example_focus: "Robustness & sensitivity"
example_reuse: "Branch identity → attempt history → repair lineage → current-state reconciliation pattern"
example_output: "A reconciled execution ledger separating 8 declared branches, 7 valid branches, historical attempt events, and current successful coverage"
example_boundary: "The failure types, repairs, endpoint values, and branch decisions are synthetic teaching material and are not recommended scientific rules."
---

# Failure → repair → reconciliation

This exercise focuses on a distinction that becomes important as soon as one branch is retried:

> **Scientific branches and execution attempts are not the same denominator.**

The synthetic declaration contains:

```text
8 declared branches
7 valid branches
1 invalid before execution
```

The initial execution state contains:

```text
4 successful
1 technical failure
1 non-finite endpoint
1 valid not-run branch
```

Two affected branches are later repaired and rerun successfully.

The final **current branch state** becomes:

```text
6 successful / 7 valid
1 valid not-run branch still unresolved
```

Historical failure/non-finite events remain in the attempt ledger.

<div class="callout warning">
<strong>All values and repairs are synthetic.</strong>
Reuse the lineage and denominator pattern, not the scientific choices or numerical endpoint values.
</div>

## 1. Start from the declared branch inventory

Assume eight declared branches have stable IDs:

| Branch | Valid before execution? | Reason |
|---|---|---|
| S01 | yes | — |
| S02 | yes | — |
| S03 | yes | — |
| S04 | yes | — |
| S05 | yes | — |
| S06 | yes | — |
| S07 | yes | — |
| S08 | no | predeclared unsupported factor combination |

Therefore:

```text
declared = 8
valid = 7
invalid before execution = 1
```

S08 is not an execution failure.

## 2. Preserve the initial current-state record

The first execution window produces:

| Branch | Attempt | State | Estimate / reason |
|---|---|---|---|
| S01 | A01 | successful | +0.018 |
| S02 | A01 | successful | +0.021 |
| S03 | A01 | successful | +0.016 |
| S04 | A01 | technical_failure | `KeyError: comparison` |
| S05 | A01 | non_finite_endpoint | `NaN` |
| S06 | A01 | successful | +0.024 |
| S07 | — | not_run | external dependency unavailable |
| S08 | — | invalid_before_execution | unsupported combination |

At this point:

```text
4 successful / 7 valid
1 valid technical failure
1 valid non-finite endpoint
1 valid not-run branch
1 invalid branch outside the valid denominator
```

## 3. Do not collapse non-finite into technical failure

S04 and S05 are different evidence states.

### S04

The branch raised before returning a normal endpoint.

That is a technical failure.

### S05

The branch returned `NaN`.

Core `run_specs()` can float-coerce that value; it does not automatically create a failure status.

The surrounding audit policy treats a non-finite endpoint as unresolved evidence.

Both remain in the valid denominator, but their diagnostic records differ.

## 4. Preserve an attempt record for S04

A documentation-side record might be:

```json
{
  "schema": "gazeaudit-execution-attempt-v1",
  "branch_id": "S04",
  "attempt_id": "A01",
  "scientific_validity": "valid",
  "execution_state": "technical_failure",
  "endpoint_reference": "E1",
  "temporal_evidence_layer": "submitted analysis",
  "factor_values": {
    "detector": "ivt",
    "qc_policy": "strict",
    "aoi_mode": "probabilistic"
  },
  "source_software_reference": "canonical-v1 / software-commit-X",
  "estimate": null,
  "error_type": "KeyError",
  "error_or_not_run_reason": "missing comparison condition",
  "prior_attempt_id": null,
  "repair_record_reference": null,
  "relevant_outcomes_already_inspected": true
}
```

The exact strings are synthetic.

The important pieces are branch identity, attempt identity, validity, failure evidence, endpoint identity, and outcome-inspection timing.

## 5. Preserve an attempt record for S05

```json
{
  "schema": "gazeaudit-execution-attempt-v1",
  "branch_id": "S05",
  "attempt_id": "A01",
  "scientific_validity": "valid",
  "execution_state": "non_finite_endpoint",
  "endpoint_reference": "E1",
  "temporal_evidence_layer": "submitted analysis",
  "factor_values": {
    "detector": "idt",
    "qc_policy": "moderate",
    "aoi_mode": "hard"
  },
  "source_software_reference": "canonical-v1 / software-commit-X",
  "estimate": "NaN",
  "error_type": null,
  "error_or_not_run_reason": "empty contrast after branch processing",
  "prior_attempt_id": null,
  "repair_record_reference": null,
  "relevant_outcomes_already_inspected": true
}
```

Do not rewrite `NaN` as `0`.

## 6. Preserve the not-run valid branch

S07 is scientifically valid but was never attempted because an external dependency was unavailable.

Record:

```text
branch = S07
validity = valid
state = not_run
reason = external dependency unavailable during execution window
```

S07 remains part of the seven-valid denominator.

It is not:

- successful;
- invalid;
- a technical failure;
- a null effect.

## 7. Diagnose S04 without changing the scientific branch

Inspection shows that S04's processor contains a synthetic condition-label bug.

The intended branch still has the same:

- factor values;
- endpoint E1;
- validity classification;
- participant/trial eligibility;
- missingness policy.

Repair R01 changes only the implementation defect.

That supports a same-branch rerun.

## 8. Diagnose S05 without changing the endpoint

Inspection shows that S05 divides by a branch-specific empty denominator because a synthetic preprocessing adapter failed to preserve one required condition.

Repair R02 corrects that adapter behavior.

The scientific endpoint remains E1.

If the correction had instead changed the endpoint definition or eligibility rule, it would require a scientific amendment rather than a simple repair rerun.

## 9. Rerun S04 under a new attempt ID

```json
{
  "schema": "gazeaudit-execution-attempt-v1",
  "branch_id": "S04",
  "attempt_id": "A02",
  "scientific_validity": "valid",
  "execution_state": "repair_rerun_success",
  "endpoint_reference": "E1",
  "temporal_evidence_layer": "submitted-analysis technical recovery",
  "factor_values": {
    "detector": "ivt",
    "qc_policy": "strict",
    "aoi_mode": "probabilistic"
  },
  "source_software_reference": "canonical-v1 / software-commit-Y",
  "estimate": "0.019",
  "error_type": null,
  "error_or_not_run_reason": null,
  "prior_attempt_id": "A01",
  "repair_record_reference": "R01",
  "relevant_outcomes_already_inspected": true
}
```

The original S04/A01 failure remains in history.

## 10. Rerun S05 under a new attempt ID

```json
{
  "schema": "gazeaudit-execution-attempt-v1",
  "branch_id": "S05",
  "attempt_id": "A02",
  "scientific_validity": "valid",
  "execution_state": "repair_rerun_success",
  "endpoint_reference": "E1",
  "temporal_evidence_layer": "submitted-analysis technical recovery",
  "factor_values": {
    "detector": "idt",
    "qc_policy": "moderate",
    "aoi_mode": "hard"
  },
  "source_software_reference": "canonical-v1 / software-commit-Y",
  "estimate": "0.022",
  "error_type": null,
  "error_or_not_run_reason": null,
  "prior_attempt_id": "A01",
  "repair_record_reference": "R02",
  "relevant_outcomes_already_inspected": true
}
```

Again, S05 remains one scientific branch.

## 11. Reconcile current state

After the two successful repairs:

| Branch | Current state | Current estimate |
|---|---|---:|
| S01 | successful | +0.018 |
| S02 | successful | +0.021 |
| S03 | successful | +0.016 |
| S04 | repair_rerun_success | +0.019 |
| S05 | repair_rerun_success | +0.022 |
| S06 | successful | +0.024 |
| S07 | not_run | — |
| S08 | invalid_before_execution | — |

The correct branch-level reconciliation is:

```text
8 declared
7 valid
6 currently represented successfully
1 valid not-run branch
1 invalid before execution
```

The valid execution summary is:

> 6 successful / 7 valid.

## 12. Reconcile history separately

Historical events include:

- S04/A01 technical failure;
- S04/A02 repair success;
- S05/A01 non-finite endpoint;
- S05/A02 repair success.

Those extra attempt rows do not turn seven valid specifications into nine.

The history can contain more records than the current branch table.

## 13. Why attempt count is not a robustness denominator

Suppose someone counts all valid execution-related records:

```text
S01/A01
S02/A01
S03/A01
S04/A01
S04/A02
S05/A01
S05/A02
S06/A01
S07/not-run
```

That is nine historical records/events associated with seven valid branches.

Reporting:

> 6 successful out of 9

would mix:

- initial failures;
- repaired reruns;
- current success;
- not-run state;

inside one inappropriate denominator.

Robustness summaries operate on reconciled current scientific branches, not raw attempt-history row count.

## 14. What if S07 is run later?

Create a new S07 attempt record.

If it succeeds, current state becomes:

```text
7 successful / 7 valid
```

The earlier not-run event remains historical provenance if the project records it as an event.

Do not delete the earlier execution gap merely because it was later resolved.

## 15. What if a repair changes the endpoint?

Then the new record does not belong to the same endpoint branch lineage.

Create:

- a new endpoint declaration;
- a separate amendment/evidence layer;
- a separate execution denominator where appropriate.

Do not set `repair_rerun_success` merely because the new endpoint produces a usable result.

## 16. What if a repair changes participant eligibility?

That can alter the scientific denominator.

Treat it as a researcher-owned analytical amendment unless it is genuinely a representation correction with independently justified reconstruction.

Re-run the affected provenance, readiness, and downstream analyses accordingly.

## 17. Reporting example

### Methods

> Execution attempts were preserved separately from scientific branch identity. Valid branches that raised, returned non-finite endpoints, or were not run remained in the valid denominator. Technical repairs created new attempts linked to the original event while preserving the branch's endpoint and factor values.

### Results

> Four of seven valid branches succeeded initially; one failed technically, one returned a non-finite endpoint, and one was not run. The technical and non-finite branches were repaired without changing their scientific specification and succeeded on linked reruns. The reconciled current state therefore contained six successful endpoint branches and one unresolved not-run branch (6/7 valid).

### Limitation

> Recovery establishes execution lineage and current branch coverage, not the scientific correctness of the factor space, endpoint, validity rule, or repairs. One valid branch remained unexecuted.

## 18. Final consistency check

Before rebuilding robustness summaries:

- [ ] exactly one current state per valid branch;
- [ ] historical failed attempts preserved;
- [ ] repair reruns linked to prior attempts;
- [ ] no attempt row counted as a new scientific branch;
- [ ] no non-finite value converted to zero;
- [ ] no valid failed/not-run branch relabelled invalid retrospectively;
- [ ] endpoint identity unchanged for same-branch reruns;
- [ ] current valid denominator reconciled;
- [ ] unresolved valid branches remain visible;
- [ ] temporal evidence layer recorded.

## API and reference links

- [`run_specs()`]({{ '/docs/reference/api-pathways/#api-run-specs' | relative_url }})
- [`PipelineSpace`]({{ '/docs/reference/api-pathways/#api-pipelinespace' | relative_url }})
- [Execution Ledger & Recovery Center]({{ '/docs/execution-ledger/' | relative_url }})
- [Execution ledger and recovery]({{ '/docs/guides/execution-ledger-recovery/' | relative_url }})
- [Evidence and denominator vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }})
- [Failed-audit recovery]({{ '/docs/examples/failed-audit-recovery/' | relative_url }})

## Reuse boundary

Reuse:

- branch/attempt separation;
- current-state reconciliation;
- historical event retention;
- repair linkage;
- denominator equations;
- bounded reporting structure.

Rebuild:

- branch identities;
- failure causes;
- endpoint values;
- repair decisions;
- timing;
- software/source identities;
- rerun scope.
