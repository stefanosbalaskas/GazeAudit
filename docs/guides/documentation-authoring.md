---
title: Documentation authoring standard
description: Author GazeAudit documentation with consistent intent, structure, code examples, accessibility, scientific boundaries, metadata, and maintenance rules.
kicker: Guide · Documentation
permalink: /docs/guides/documentation-authoring/
search_category: Guide
search_keywords: documentation authoring style guide examples code samples headings accessibility placeholders reference how-to tutorial explanation scientific boundaries metadata
---

# Documentation authoring standard

Use this guide when adding or substantially revising public GazeAudit documentation. The goal is not stylistic uniformity for its own sake: predictable page types, headings, code samples, links, and scientific boundaries help readers find the right information and help CI detect drift.

The content model is adapted from [Diátaxis](https://diataxis.fr/) and current developer-documentation practice. GazeAudit does not force every page into a rigid taxonomy; instead, each page should have **one dominant user intent**.

## 1. Declare the page's dominant intent

Before writing, finish this sentence:

> The reader opens this page because they want to **…**

Route the answer into one primary mode:

| Intent | Typical GazeAudit surface | Write for |
|---|---|---|
| Learn | Getting Started, worked examples | skill acquisition through a safe, bounded exercise |
| Do | Guides, workflows, troubleshooting | completing a concrete research or software task |
| Look up | Reference, API/CLI, vocabulary, provenance | accurate and compact facts |
| Understand | Articles, methods discussion, case-study interpretation | rationale, context, trade-offs, and evidence boundaries |

Do not turn a reference page into a long tutorial, or a worked example into a literature essay. Link across documentation types when another need appears.

## 2. Start with the outcome and boundary

The opening should make two things clear quickly:

1. **what the reader will get from the page**;
2. **what the page does not establish**.

For synthetic examples, say that they are synthetic near the start. For frozen validation evidence, state that the outcome is protocol-bound. For generated software metadata, distinguish software contracts from scientific decisions.

## 3. Use predictable heading structure

Use one page-level H1, then H2 sections, then H3 subsections when needed. Do not skip heading levels merely for visual styling.

Headings should describe the content that follows. Prefer:

- `## Inspect structural QC`
- `## Declare the specification space`
- `## Interpret incomplete execution`

over vague headings such as:

- `## More`
- `## Details`
- `## Other notes`

W3C guidance emphasizes meaningful heading structure because headings support orientation and in-page navigation.

## 4. Write code examples for copying and adaptation

Before each substantial code block, explain what the block does and what the reader must replace.

For new or substantially revised examples:

- specify the code language on fenced blocks;
- omit shell prompts such as `$` so commands remain copyable;
- keep examples focused on the relevant operation rather than reproducing an entire unrelated file;
- keep explanatory prose outside the code block unless a code comment is itself part of the teaching point;
- show output only when it helps the reader verify success;
- use obvious placeholders for values the reader must replace;
- explain placeholders in nearby prose;
- avoid fabricating scientific values merely to make an API call appear complete.

GitHub's documentation style guide similarly recommends copyable commands without prompts, explained placeholders, and focused code samples; Google recommends introducing code examples with explanatory text and keeping them readable in narrow views.

### Software placeholder vs scientific placeholder

These are different.

A software placeholder can safely communicate structure:

```python
run_specs(study, space, endpoint)
```

A scientific value should not be invented simply to create a copy-ready line:

```python
# Avoid presenting an arbitrary threshold as though it were a recommended choice.
```

When a demonstration needs a concrete value, identify it as a **teaching value** and state that it must not be transferred to a real study without justification.

## 5. Make examples reconstructable

A worked example should make it possible to answer:

- What are the prerequisites?
- What input is being used?
- Is the input synthetic, public, or frozen validation data?
- Which public functions are exercised?
- What output should exist at the end?
- What would count as a technical failure?
- What scientific conclusion is explicitly out of scope?
- Where should the reader go next?

A quick example does not need every one of these as a dedicated heading, but the information should be recoverable from the page.

### Example contract metadata

Every public page with `search_category: Example` must also declare:

```yaml
page_type: example
example_data: "Synthetic"
example_focus: "Robustness & sensitivity"
example_reuse: "Complete audit workflow"
example_output: "Specification results and sensitivity summaries"
example_boundary: "Teaching choices are not study defaults."
```

The governed values for `example_data` are:

- `Synthetic`;
- `Demo or user data`;
- `Software-only`;
- `Documentation-only`.

The governed `example_focus` vocabulary is deliberately compact: Data & QC, Measurement uncertainty, Robustness & sensitivity, Interpretation & reporting, Documentation & API, Environment, Project lifecycle, Peer review & publication, and Reproducibility.

The shared layout renders these fields as the **Example contract**, while the [Example catalog]({{ '/docs/examples/catalog/' | relative_url }}) generates its cards and filters from the same front matter. Do not add an example to a separate manual taxonomy.

`example_reuse` should identify the transferable structure. `example_output` should describe the artifact or learning output. `example_boundary` should state the strongest nearby inference that the example does **not** license.

## 6. Keep reference material factual

Reference pages should prioritize:

- exact names;
- signatures or syntax;
- parameter/return contracts;
- installed command names;
- status/denominator definitions;
- file or source locations;
- version/revision identity;
- authoritative links.

Do not use reference ranking or wording to imply that one scientifically defensible choice is preferred. When interpretation is needed, link to a guide, article, workflow, or evidence page.

## 7. Keep procedures goal-oriented

A guide should help the reader accomplish a concrete task. Use numbered steps when order matters.

If a procedure needs more than a short explanation of *why*, move the deeper rationale to an article or scientific-methods page and link to it. Keep troubleshooting close to the task when the failure is specific; use the dedicated troubleshooting center when the problem can arise across many workflows.

## 8. Preserve scientific boundaries

Public documentation must keep these distinctions explicit:

- **software default ≠ scientific recommendation**;
- **Python-required argument ≠ scientifically mandatory construct**;
- **synthetic demonstration ≠ empirical validation**;
- **successful execution ≠ valid inference**;
- **structural provenance ≠ scientific validity**;
- **navigation ranking ≠ method ranking**;
- **frozen case outcome ≠ universal property of a dataset or method**.

Do not rewrite or soften an inconvenient frozen outcome to make the documentation read more smoothly.

## 9. Prefer semantic HTML and native controls

Use ordinary Markdown/HTML semantics before adding custom ARIA or JavaScript.

For interactive documentation:

- use native links for navigation;
- use native buttons for actions;
- use native `details` / `summary` for compact disclosure when appropriate;
- give controls concise accessible names;
- preserve visible focus;
- support forced colours and reduced motion;
- keep essential content available when progressive enhancement fails.

W3C and MDN both recommend semantic structure because browsers and assistive technology receive built-in behavior that custom controls otherwise have to recreate.

## 10. Provide more than one discovery route

A page should normally be reachable through at least two mechanisms, for example:

- hierarchical navigation plus search;
- a hub page plus related-content links;
- a method pathway plus a guide/example link;
- the documentation compass plus a direct sidebar route.

This supports different navigation strategies and aligns with WCAG's multiple-ways principle.

## 11. Use front matter consistently

Every new public documentation page should normally provide:

```yaml
---
title: Descriptive page title
description: One-sentence description used by search and metadata.
kicker: Section · Type
permalink: /docs/example-route/
search_category: Guide
search_keywords: useful query terms here
---
```

Choose a stable permalink. Search keywords should include likely task language and exact public terms where useful; do not stuff unrelated keywords.

The shared site layout also uses `search_category` to expose a compact **page-intent cue** for core documentation types:

- `Example` → **Learn**;
- `Guide` or `Workflow` → **Do**;
- `Reference` → **Look up**;
- `Article` → **Understand**;
- `Case study` or `Evidence` → **Evidence**.

Choose the category that matches the page's dominant purpose. Do not select a category merely to obtain a preferred visual badge.

## 12. Link instead of duplicating authority

Before copying a definition, command, outcome, or workflow rule into another page, ask whether a single authoritative home already exists.

Prefer:

- one generated API contract plus links;
- one CLI reference plus workflow examples;
- one frozen validation authority plus bounded case-study interpretation;
- one troubleshooting rule plus contextual links.

Duplication is appropriate only when the repeated text is short, stable, and improves task completion without creating a second authority.

## 13. Run the documentation gates

A documentation tranche is not complete merely because the Markdown renders.

The repository gates verify, among other things:

- internal references;
- site structure;
- governed search metadata;
- planner handoff;
- researcher utilities;
- accessibility contracts;
- package-generated API/install metadata;
- test/lint integrity across the supported Python matrix.

If a new public route is important enough to depend on, add it to generated-site governance and add a focused regression test for the contract it introduces.

## Author checklist

Before opening a documentation PR, verify:

- the page has one dominant intent;
- the opening states the outcome and any important boundary;
- heading levels are logical;
- links say where they go;
- code blocks are introduced and copyable;
- placeholders are explained;
- synthetic values are labelled as teaching values;
- empirical claims point to the correct frozen authority;
- interactive elements work by keyboard and retain focus indication;
- the page is discoverable from an appropriate hub;
- search metadata is present;
- a regression test protects the new route or behavior when appropriate.

For the user-facing version of this content model, see the [Documentation compass]({{ '/docs/documentation-map/' | relative_url }}).
