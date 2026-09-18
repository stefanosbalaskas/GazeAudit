---
title: Search to contract walkthrough
description: A fully synthetic example showing how grouped GazeAudit search results lead from an ambiguous query to the correct guide, example, reference, or evidence authority.
kicker: Example · Documentation
permalink: /docs/examples/search-to-contract/
search_category: Example
search_keywords: search grouped results reference guide evidence cli run_specs NaN AOI uncertainty validation contract synthetic walkthrough
---

# Search → contract walkthrough

This is a **fully synthetic documentation-navigation exercise**. It demonstrates how to find the correct source of information; it does not validate an analysis or recommend a scientific decision.

The exercise uses four fictional questions:

1. “My `run_specs()` endpoint became `NaN`. What exactly does the package do?”
2. “What command creates a reviewer-revision package?”
3. “I need to understand AOI uncertainty. Where should I start?”
4. “Can I call my new result `robust_negative`?”

## Question 1 — `run_specs NaN`

Open search with **Ctrl/Cmd + K** and enter:

```text
run_specs NaN
```

The grouped results may include **Reference**, **Guide**, and **Example** material.

Because the question asks **what exactly the runtime contract does**, choose Reference first. The [Evidence and denominator vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }}) records two relevant facts:

- `run_specs()` propagates processor/endpoint exceptions rather than manufacturing a technical-failure row;
- converting the endpoint with `float(...)` does not itself reject `NaN` or infinity.

If a finite scalar is part of the audited endpoint contract, the surrounding workflow should check it explicitly:

```python
import math

estimate = float(common_endpoint(processed, spec))
if not math.isfinite(estimate):
    raise ValueError("endpoint returned a non-finite estimate")
```

A non-finite value is not automatically a zero or null effect.

If execution is actually blocked, leave Reference and continue with [Troubleshooting GazeAudit]({{ '/docs/guides/troubleshooting/' | relative_url }}).

## Question 2 — reviewer revision command

Search:

```text
revision package
```

You may see both **Guide/Example** and **Reference** groups.

The exact command belongs to Reference:

```bash
gazeaudit-revision-package init \
  --output-dir revision-package \
  --project-slug synthetic-study \
  --review-round 1
```

Validate the resulting structure with:

```bash
gazeaudit-revision-package validate --root revision-package
```

The [CLI reference]({{ '/docs/reference/cli-reference/' | relative_url }}) defines the command and exit behavior. The [revision-package quickstart]({{ '/docs/examples/revision-package-quickstart/' | relative_url }}) is the procedural companion.

The distinction is useful: **Reference** answers “what is the command?”; **Example** answers “how does the workflow fit together?”

## Question 3 — AOI uncertainty

Search:

```text
AOI uncertainty
```

This topic legitimately spans several documentation kinds:

| Group | What to use it for |
|---|---|
| Guide | learn the measurement-uncertainty workflow |
| Example | inspect a worked synthetic AOI-boundary analysis |
| Reference | look up `GaussianGazeErrorModel`, `aoi_probabilities`, or related APIs |
| Evidence | inspect a protocol-bound validation case when substantively relevant |
| Article | understand why boundary uncertainty is a modelling problem |

There is no universal “best” result. Choose the documentation type that matches the question you are currently asking.

## Question 4 — `robust_negative`

Search:

```text
robust_negative
```

This is an evidence-authority question. The [Validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) and [Evidence vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }}) establish that `robust_negative` is the canonical **Korthals protocol-bound outcome**.

It is not a generic status to assign to this synthetic exercise or to an unrelated dataset.

## What the search interface does

It:

- ranks documentation metadata against the query;
- groups visible matches by documentation type;
- allows filtering by type;
- keeps the query visible;
- supports keyboard navigation;
- links to the underlying documentation authority.

It does **not**:

- infer which analysis choice is scientifically defensible;
- choose thresholds or exclusions;
- decide whether a result is robust;
- select a manuscript conclusion;
- relabel frozen validation evidence.

## A reusable lookup pattern

Use this compact sequence:

```text
1. Search the smallest distinctive phrase.
2. Identify whether the need is Guide, Example, Reference, Workflow, Article, or Evidence.
3. Open the authoritative page for that need.
4. Stop when the factual contract is answered.
5. Move to a procedural guide only when the question becomes "what should I do next?"
```

For the general navigation rules, return to [Find information fast]({{ '/docs/guides/find-information-fast/' | relative_url }}).
