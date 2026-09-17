---
title: Failed-audit recovery walkthrough
description: A fully synthetic break-diagnose-repair example that preserves invalid combinations, valid technical failures, rerun history, and execution denominators.
kicker: Example · Troubleshooting
page_type: example
permalink: /docs/examples/failed-audit-recovery/
search_category: Example
search_keywords: troubleshooting failed audit recovery technical failure invalid specification denominator run_specs exception non finite repair provenance synthetic example
---

# Failed-audit recovery walkthrough

This is a **fully synthetic teaching exercise** for the point where an audit does not finish cleanly. It shows how to distinguish an invalid combination from a valid technical failure, preserve the failure, repair the causal defect, rerun the same branch, and reconcile the final execution record without rewriting history.

No value or outcome on this page is empirical validation evidence.

<div class="callout warning">
<strong>The repair is technical, not scientific.</strong>
The exercise does not change the endpoint, threshold, exclusion rule, specification space, or interpretation because a branch failed. Those choices remain fixed while the execution defect is diagnosed.
</div>

## Starting declaration

A fictional project varies three binary choices:

| Factor | Levels |
|---|---|
| assignment | `hard`, `probabilistic` |
| summary | `mean`, `trimmed` |
| sample policy | `A`, `B` |

The cross-product contains **8 declared combinations**.

Before execution, the team has an independently justified validity rule: the `probabilistic + trimmed + B` combination is unsupported by the fictional processor contract. It is rejected **before any endpoint result is inspected**.

Therefore:

```text
8 declared combinations
7 valid combinations
```

The invalid combination is documented but is not part of the valid execution denominator.

## 1. Enumerate validity before execution

The same public API used by GazeAudit robustness workflows can enumerate the valid space explicitly:

```python
from gazeaudit import PipelineSpace

space = (
    PipelineSpace()
    .add_choice("assignment", ["hard", "probabilistic"])
    .add_choice("summary", ["mean", "trimmed"])
    .add_choice("sample_policy", ["A", "B"])
)


def valid_if(spec):
    return not (
        spec["assignment"] == "probabilistic"
        and spec["summary"] == "trimmed"
        and spec["sample_policy"] == "B"
    )


valid_specs = space.enumerate_specs(valid_if=valid_if)
print(space.size)       # 8 declared
print(len(valid_specs)) # 7 valid
```

The important point is the timing: the validity rule exists before endpoint execution.

## 2. One valid branch fails technically

A first execution attempt produces six estimates and one exception among the seven valid specifications.

Synthetic ledger:

| branch | validity | execution | estimate |
|---|---|---|---:|
| S01 | valid | success | -0.18 |
| S02 | valid | success | -0.14 |
| S03 | valid | success | -0.11 |
| S04 | valid | success | -0.09 |
| S05 | valid | success | -0.07 |
| S06 | valid | technical failure | — |
| S07 | valid | success | -0.05 |
| S08 | invalid before execution | not executed | — |

The correct status is:

```text
6 successful / 7 valid
1 predeclared-invalid combination documented separately
```

It is **not** `6 / 6`. Removing S06 because it failed would silently change the denominator after execution.

It is also not `6 / 8` if that notation is presented as an execution-success rate, because S08 was never a valid execution target.

## 3. Preserve the exact failure before debugging

A compact failure record might look like:

```text
spec_id: S06
valid_before_execution: true
execution_status: technical_failure
endpoint_id: E1_claim_minus_comparison
exception_type: KeyError
exception_message: missing required condition 'comparison'
affected_rows_after_processing: 42
outcomes_already_seen: true
```

The exception text here is synthetic. The principle is to retain enough information to reconstruct **which declared valid branch failed and why the software stopped**.

## 4. Diagnose the layer

The raw canonical source contains both fictional endpoint conditions. Inspection shows that S06's processor accidentally filters the `comparison` condition because a string label is misspelled in one branch-specific code path.

That is a **technical processor defect**. It is not evidence that:

- S06 was scientifically invalid;
- comparison trials should be excluded;
- the endpoint should be redefined;
- the specification space should be reduced;
- the failed estimate should be treated as zero.

The smallest safe repair is to correct the branch-specific label handling while leaving every declared scientific choice unchanged.

## 5. Use an execution ledger while diagnosing

`run_specs()` is intentionally concise: a valid branch exception propagates rather than being silently swallowed. During recovery, a researcher can execute the already-enumerated valid specifications with an explicit ledger so the failure remains visible.

```python
import math
import pandas as pd

rows = []
for index, spec in enumerate(valid_specs):
    spec_id = f"S{index + 1:02d}"
    try:
        processed = process_specification(study, spec)
        estimate = float(common_endpoint(processed, spec))
        if not math.isfinite(estimate):
            raise ValueError("endpoint returned a non-finite estimate")
        rows.append(
            {
                "spec_id": spec_id,
                **spec,
                "status": "success",
                "estimate": estimate,
                "error": None,
            }
        )
    except Exception as exc:
        rows.append(
            {
                "spec_id": spec_id,
                **spec,
                "status": "technical_failure",
                "estimate": float("nan"),
                "error": f"{type(exc).__name__}: {exc}",
            }
        )

ledger = pd.DataFrame(rows)
print(ledger[["spec_id", "status", "estimate", "error"]])
```

<div class="callout info">
<strong>This wrapper is a troubleshooting pattern, not a replacement scientific API.</strong>
It is useful for preserving branch-level failure evidence while diagnosing a known declared space. A real project should still decide in advance which exceptions/statuses are technically meaningful and should not use exception-catching to turn scientifically invalid inputs into apparently successful branches.
</div>

## 6. Repair and rerun the same branch

The fictional label bug is corrected. The team reruns S06 under the **same**:

- canonical source;
- endpoint E1;
- scientific factor levels;
- validity rule;
- participant/trial eligibility policy.

The repaired S06 returns `-0.08`.

The audit history now contains two execution events for S06:

| branch | attempt | status | estimate | record treatment |
|---|---:|---|---:|---|
| S06 | 1 | technical failure | — | retained |
| S06 | 2 | success after technical repair | -0.08 | retained and marked as repaired execution |

The previous failure is not deleted merely because the repair worked.

## 7. Reconcile the denominator after repair

The final current execution state is:

```text
8 declared
7 valid
7 currently successful
1 historical technical failure event retained for S06
1 predeclared-invalid combination retained outside the valid denominator
```

A transparent methods/provenance note can say:

> Seven of eight declared synthetic combinations satisfied the predeclared validity rule. One valid branch initially failed because of a branch-specific implementation defect. After correcting that defect without changing the endpoint or scientific decision rules, the same branch was rerun successfully. The original failure event was retained in the execution history.

This is different from pretending the first attempt never happened.

## 8. What if the repair cannot recover S06?

Then the current audit remains:

```text
6 successful / 7 valid
```

The failure stays visible. Any completeness-dependent interpretation must respect that incomplete execution state.

Do not:

- shrink the denominator to `6 / 6`;
- reclassify S06 as invalid after seeing it fail unless a genuinely pre-existing validity rule establishes that status;
- substitute the nearest successful estimate;
- report the missing endpoint as zero;
- change the scientific endpoint solely to make execution complete.

## 9. What if the endpoint returns `NaN` instead of raising?

Treat that as an unresolved endpoint execution problem until diagnosed. A non-finite estimate is not evidence of a null effect.

The ledger pattern above checks `math.isfinite()` explicitly so non-finite outputs cannot silently enter robustness summaries as ordinary estimates.

Inspect the branch for empty groups, missing conditions, zero denominators, or upstream non-finite values while preserving the same scientific target.

## 10. What if the problem is in the canonical table?

If structural preflight shows a source-representation problem such as a malformed timestamp or an incorrectly parsed identifier:

1. retain the original source identity;
2. record the affected rows/trials;
3. create a corrected canonical representation;
4. document the transformation;
5. rerun preflight;
6. bind the repaired execution to the corrected representation/fingerprint.

Do not turn a structural diagnostic directly into a participant exclusion. Eligibility remains a researcher-owned scientific decision.

Use [Data onboarding]({{ '/docs/guides/data-onboarding/' | relative_url }}) and [Analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}) for that distinction.

## Recovery record

A small durable record for the synthetic exercise could be:

```text
recovery/
├── declaration/
│   ├── specification-space.json
│   └── validity-rule.md
├── attempt-01/
│   ├── execution-ledger.csv
│   └── S06-error.txt
├── repair/
│   └── processor-label-fix.md
├── attempt-02/
│   └── S06-rerun.json
└── reconciliation/
    └── execution-status.md
```

The structure keeps **declaration, failure, repair, rerun, and final state** distinguishable.

## Recovery checklist

Before calling a blocked audit repaired, verify:

- [ ] the original declaration still exists;
- [ ] invalid combinations were identified independently of observed endpoint values;
- [ ] every valid branch is accounted for;
- [ ] the original technical failure is retained;
- [ ] the repair changes the causal defect rather than the scientific target;
- [ ] the same branch was rerun when possible;
- [ ] non-finite values were not converted to zero by convenience;
- [ ] current and historical execution status are distinguishable;
- [ ] downstream summaries use the reconciled current execution record;
- [ ] manuscript wording does not hide unresolved valid failures.

## Continue

Use [Troubleshooting GazeAudit]({{ '/docs/guides/troubleshooting/' | relative_url }}) as the symptom router, [Common audit mistakes and repairs]({{ '/docs/guides/common-audit-mistakes/' | relative_url }}) if the software ran but the decision trail is weak, and [Understanding the audit output bundle]({{ '/docs/guides/audit-output-bundle/' | relative_url }}) to decide which repaired evidence belongs in the durable record.

## Frozen evidence boundary

This worked recovery is synthetic teaching material. It does not alter or imitate the authority of the frozen cases. GazeBase remains `incomplete`, Korthals remains `robust_negative`, and Pedrotti/de Chambrier remains `materially_fragile`.