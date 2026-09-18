---
title: Reference lookup walkthrough
description: A fully synthetic example showing how to answer exact API, denominator, failure, CLI, and frozen-label questions by moving through the GazeAudit reference layer.
kicker: Example · Reference
page_type: example
permalink: /docs/examples/reference-lookup-workflow/
search_category: Example
search_keywords: reference lookup api cli status denominator valid_if run_specs non finite frozen labels synthetic example
---

# Reference lookup walkthrough

This is a **fully synthetic teaching exercise** for a user who already knows the research task and needs to answer exact contract questions without rereading an end-to-end tutorial.

No value, status, or outcome on this page is empirical validation evidence.

## Scenario

A fictional robustness audit declares three binary choices, so the Cartesian space contains **8 combinations**. One combination is ruled out by a predeclared `valid_if` constraint. Of the **7 valid** branches, one raises during processing.

Later, a reviewer asks for a separate revision package.

The questions are narrow:

1. How do I confirm the declared and valid counts?
2. Does `run_specs()` return a `technical_failure` row?
3. What if the endpoint returns `NaN`?
4. What is the exact revision-package command?
5. Can I call the synthetic result `robust_negative`?

Each is a **reference lookup**, not a request for GazeAudit to make a scientific decision.

## Lookup 1 — declared versus valid

The [API map]({{ '/docs/reference/api-map/' | relative_url }}) points to `PipelineSpace` and `enumerate_specs()`. The [evidence vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }}) supplies the denominator terms.

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


declared_count = space.size
valid_specs = space.enumerate_specs(valid_if=valid_if)

print(declared_count)      # 8
print(len(valid_specs))    # 7
```

The answer is factual: **8 declared, 7 valid**. Whether the validity rule is scientifically defensible remains a researcher-owned judgement.

## Lookup 2 — what happens when one valid branch raises?

The `run_specs()` contract executes each valid specification in sequence. It does not swallow an exception and it does not manufacture a row with `status="technical_failure"`.

Therefore, if the fictional S06 branch raises:

```text
declared = 8
valid = 7
successfully collected before/around the audited recovery = 6
technical failure = 1 valid branch
```

A provenance-preserving recovery ledger may call S06 `technical_failure`, but that label belongs to the **audit wrapper/documentation**, not to the normal `run_specs()` return schema.

For the operational recovery pattern, switch from reference to the [failed-audit recovery walkthrough]({{ '/docs/examples/failed-audit-recovery/' | relative_url }}).

## Lookup 3 — what if the endpoint returns `NaN`?

The package converts the endpoint value with `float(...)`. That conversion can still produce `NaN` or infinity.

So this is **not** sufficient:

```python
estimate = float(common_endpoint(processed, spec))
```

If the scientific endpoint contract requires a finite scalar, make that expectation explicit in the audited execution layer:

```python
import math

estimate = float(common_endpoint(processed, spec))
if not math.isfinite(estimate):
    raise ValueError("endpoint returned a non-finite estimate")
```

A non-finite endpoint is unresolved execution/endpoint evidence. It is **not** automatically a zero or null effect.

## Lookup 4 — exact reviewer-revision CLI syntax

The [CLI reference]({{ '/docs/reference/cli-reference/' | relative_url }}) records the installed command contract.

Create the scaffold:

```bash
gazeaudit-revision-package init \
  --output-dir revision-package \
  --project-slug synthetic-study \
  --review-round 1
```

Validate it:

```bash
gazeaudit-revision-package validate --root revision-package
```

The validator checks package structure and manifest integrity. A zero exit status does not mean the scientific analysis or manuscript has been validated.

## Lookup 5 — may the synthetic outcome use a frozen case label?

No. The [evidence vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }}) and [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) make the boundary explicit.

The canonical frozen labels remain:

- GazeBase: `incomplete`
- Korthals: `robust_negative`
- Pedrotti/de Chambrier: `materially_fragile`

Those labels belong to their protocol-bound records. This synthetic exercise remains simply a synthetic reference exercise.

## What this lookup sequence accomplished

| Question | Reference used | What was learned |
|---|---|---|
| declared vs valid count | API map + evidence vocabulary | `PipelineSpace.size` and `enumerate_specs(valid_if=...)` answer different denominator questions |
| branch exception | evidence vocabulary + source contract | `run_specs()` propagates; `technical_failure` is not a returned enum |
| `NaN` endpoint | evidence vocabulary | explicit finiteness checking belongs in the audited endpoint wrapper when required |
| revision command | CLI reference | exact `init` and `validate` syntax plus structural-only boundary |
| validation label | validation matrix | frozen case outcomes are not generic labels |

## When to leave Reference

Reference is useful when the question is **“what exactly is the contract?”** Move back to a guide or example when the question becomes **“what sequence should I follow?”**

- blocked execution → [Troubleshooting GazeAudit]({{ '/docs/guides/troubleshooting/' | relative_url }})
- first project → [First real audit]({{ '/docs/guides/first-real-audit/' | relative_url }})
- reviewer revision → [Revision-package quickstart]({{ '/docs/examples/revision-package-quickstart/' | relative_url }})
- interpretation → [Interpret an audit result]({{ '/docs/guides/interpret-audit-result/' | relative_url }})
