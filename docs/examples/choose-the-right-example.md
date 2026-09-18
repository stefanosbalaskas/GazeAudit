---
title: Choose the right example
description: A documentation-only walkthrough showing how to choose a GazeAudit example by learning need, data context, and output without treating catalog filtering as scientific method selection.
kicker: Example · Example catalog
page_type: example
permalink: /docs/examples/choose-the-right-example/
search_category: Example
search_keywords: choose example catalog filter data context focus learn workflow own data robustness reporting reviewer documentation
example_data: "Documentation-only"
example_focus: "Documentation & API"
example_reuse: "Example-selection pattern"
example_output: "A chosen learning route with an explicit reason and boundary"
example_boundary: "Catalog filtering chooses learning material, not scientific methods or study parameters."
---

# Choose the right example

This is a **documentation-only navigation exercise**. It shows how to use the [Example catalog]({{ '/docs/examples/catalog/' | relative_url }}) without confusing a good teaching match with a scientifically justified analysis choice.

The selection rule is:

> **Choose by the thing you need to learn next, then read the example contract before copying anything.**

## Scenario 1 — “I just installed GazeAudit”

The immediate question is software availability, not measurement or robustness.

Use the catalog with:

- **Data context:** Software-only
- **Focus:** Environment

That leads to [Install, verify, first import]({{ '/docs/examples/install-smoke-check/' | relative_url }}).

Why this is the right learning route:

- it verifies package identity, imports, optional capabilities, and console commands;
- it does not require a scientific dataset;
- its boundary explicitly says that successful installation is not scientific validation.

Do **not** begin with a robustness example merely because it contains more analysis code.

## Scenario 2 — “I have my own gaze CSV”

The need is to connect a real source table to the package safely.

Use:

- **Data context:** Demo or user data
- **Focus:** Data & QC

Open [First real audit]({{ '/docs/examples/first-real-audit/' | relative_url }}).

The reusable element is the **project template**: source mapping → structural QC → governed downstream analysis → saved evidence.

The demonstration settings are not a ready-made study protocol. Before transferring the workflow, use [Adapt a synthetic example to your study]({{ '/docs/guides/adapt-examples-to-study/' | relative_url }}).

## Scenario 3 — “I need to understand a specification-space audit”

Here the goal is learning the scientific workflow mechanics before applying them.

Use:

- **Data context:** Synthetic
- **Focus:** Robustness & sensitivity

Open [End-to-end robustness audit]({{ '/docs/examples/end-to-end-robustness/' | relative_url }}).

The contract tells you what transfers: the complete audit workflow. The evidence boundary tells you what does not: the synthetic specification levels and endpoint choices.

After learning the mechanics, move to the [Specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }}) for the real task.

## Scenario 4 — “The code ran; what can I report?”

This is no longer mainly an execution question.

Use:

- **Data context:** Synthetic
- **Focus:** Interpretation & reporting

Open [Result-pattern reporting]({{ '/docs/examples/result-patterns/' | relative_url }}) or [Decision-to-report]({{ '/docs/examples/decision-to-report/' | relative_url }}).

These examples teach how to separate:

- complete vs incomplete execution;
- direction stability;
- magnitude sensitivity;
- bounded manuscript wording.

Their synthetic result patterns are teaching cases, not empirical priors for your dataset.

## Scenario 5 — “A reviewer requested another analysis”

Filter to:

- **Data context:** Synthetic
- **Focus:** Peer review & publication

Several examples can legitimately match because the next action depends on the reviewer request:

| Need | Example |
|---|---|
| record a reviewer-requested sensitivity analysis separately | [Reviewer-requested reanalysis]({{ '/docs/examples/reviewer-requested-reanalysis/' | relative_url }}) |
| create and validate the governed package | [Revision-package quickstart]({{ '/docs/examples/revision-package-quickstart/' | relative_url }}) |
| connect response, manuscript change, and evidence | [Revision response package]({{ '/docs/examples/revision-response-package/' | relative_url }}) |
| trace the whole temporal record | [Submission-to-accepted record]({{ '/docs/examples/submission-to-accepted-record/' | relative_url }}) |

The catalog is allowed to return several matches. That is preferable to pretending one workflow is universally correct.

## Scenario 6 — “I know the function name, not the workflow”

Use:

- **Data context:** Documentation-only
- **Focus:** Documentation & API

Then choose between:

- [Generated API call contracts]({{ '/docs/examples/api-call-contracts/' | relative_url }}) for parameter/return structure;
- [Source-level API inspection]({{ '/docs/examples/source-api-inspection/' | relative_url }}) for signatures and source;
- [Function → evidence]({{ '/docs/examples/function-to-evidence/' | relative_url }}) for the governed research context.

Once the question changes from “what does this symbol do?” to “what should my study choose?”, leave the documentation-only route and use the corresponding guide.

## A compact selection checklist

Before opening an example, answer:

1. **What do I need to learn next?**
2. **Do I need synthetic, software-only, documentation-only, or user-data material?**
3. **What output do I expect from the exercise?**
4. **Which part of the example is explicitly reusable?**
5. **What does its evidence boundary prohibit me from transferring?**

If question 5 is still unclear, read the example contract before copying code.

Return to the [Example catalog]({{ '/docs/examples/catalog/' | relative_url }}) to try the filters.
