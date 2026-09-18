---
title: Documentation intent routing
description: A fully synthetic exercise showing how one research question moves through learning, task guidance, exact reference, and explanation without collapsing those purposes together.
kicker: Example · Documentation
permalink: /docs/examples/documentation-intent-routing/
search_category: Example
search_keywords: documentation intent learn do look up understand route search compass synthetic guide example reference article
page_type: example
example_data: "Documentation-only"
example_focus: "Documentation & API"
example_reuse: "Navigation pattern"
example_output: "Intent-routed documentation path"
example_boundary: "Navigation routing does not select a scientific method."
---

# Documentation intent routing

This is a **fully synthetic documentation-navigation exercise**. It shows how the same topic can require different documentation types at different moments. It does not select a scientific method, threshold, endpoint, exclusion, or interpretation for a real study.

Suppose a researcher asks:

> “I need to run a specification-space audit, but I am not sure how `run_specs` fits into the workflow or what its exact call contract is.”

The question contains several needs. Do not force all of them into one page.

## 1. Learn the workflow

Start with [End-to-end robustness]({{ '/docs/examples/end-to-end-robustness/' | relative_url }}).

The purpose here is **learning by doing**. The example can show a bounded synthetic workflow with concrete teaching values because those values are explicitly demonstrations rather than recommendations.

The question at this stage is:

> “What happens from study input to robustness output?”

## 2. Do the real task

Move to [Specification-space robustness]({{ '/docs/guides/specification-space/' | relative_url }}).

The purpose now is **goal-oriented guidance**. The researcher already understands the basic sequence and needs to construct a defensible analysis around their own study.

The question becomes:

> “What decisions do I need to declare and preserve for my actual audit?”

If the study-specific endpoint, valid specification set, or scientific rationale is unclear, the guide should stop rather than import teaching choices from the example.

## 3. Look up the exact contract

Open the [`run_specs` API pathway]({{ '/docs/reference/api-pathways/' | relative_url }}#api-run-specs).

The purpose is now **exact factual lookup**:

- What is the inspected signature?
- Which arguments are Python-required?
- Which arguments are keyword-only?
- What is the return annotation?
- Where is the source?
- What is the generated minimal call shape?

For the current revision, the generated structural call is:

```python
run_specs(study, space, endpoint)
```

That line answers a software-interface question. It does not define `study`, construct a scientifically defensible `space`, or choose `endpoint`.

## 4. Understand the rationale

Open [From one pipeline to a robustness audit]({{ '/docs/articles/from-one-pipeline-to-a-robustness-audit/' | relative_url }}).

The purpose here is **explanation**. The researcher no longer needs syntax or a procedure; they want to understand why a specification-space approach exists and how it changes interpretation.

The question becomes:

> “Why should analysis decisions be represented as a declared space rather than hidden inside one pipeline?”

## 5. Check the evidence boundary

If the researcher then asks whether a particular conclusion is empirically robust, move to the relevant [case study]({{ '/docs/case-studies/' | relative_url }}) or frozen [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}).

This is not a fifth documentation intent. It is the evidence authority that constrains what can be claimed after using the other documentation.

## What changed across the route?

| Stage | Main question | Appropriate surface |
|---|---|---|
| Learn | How does the workflow fit together? | Example |
| Do | How do I accomplish this task on my study? | Guide / workflow |
| Look up | What exactly is the software contract? | Reference |
| Understand | Why is the method structured this way? | Article / methods discussion |
| Evidence boundary | What does the frozen record actually support? | Validation authority / case study |

The topic stayed the same. The **reader's intent changed**.

## Search can enter at any stage

If the researcher starts with site search instead of the compass, a query such as:

```text
run_specs
```

can surface a Reference / API symbol result, while broader terms such as:

```text
specification robustness
```

can expose guides, examples, workflows, plots, and articles.

Search ranking is navigation support. It does not imply that the top result is the scientifically preferred route.

## Use the compass when the question feels mixed

When a page seems to contain too much tutorial, procedure, reference, and explanation at once, return to the [Documentation compass]({{ '/docs/documentation-map/' | relative_url }}) and split the needs.

For maintainers, the [Documentation authoring standard]({{ '/docs/guides/documentation-authoring/' | relative_url }}) gives the corresponding writing and governance rules.
