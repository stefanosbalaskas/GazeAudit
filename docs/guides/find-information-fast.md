---
title: Find information fast
description: Use GazeAudit search, documentation types, reference pages, keyboard controls, and evidence boundaries to reach the right page without treating navigation as scientific advice.
kicker: Guide · Documentation
permalink: /docs/guides/find-information-fast/
search_category: Guide
search_keywords: search documentation find page reference guide example workflow evidence keyboard shortcut facets grouped results navigation
---

# Find information fast

GazeAudit has several documentation layers because **learning a workflow**, **looking up an exact contract**, **understanding a concept**, and **checking frozen evidence** are different tasks. This guide shows how to reach the right layer quickly.

The search interface is navigation support. It does **not** decide which threshold, exclusion, endpoint, specification, model, or conclusion is scientifically appropriate.

## Start from the question you are asking

| Your question sounds like… | Start with | Why |
|---|---|---|
| “How do I do this?” | [Guides]({{ '/docs/guides/' | relative_url }}) | task-oriented sequence and decision boundaries |
| “Show me a complete worked path.” | [Examples]({{ '/docs/examples/' | relative_url }}) | runnable or synthetic demonstrations |
| “What exactly does this API, command, field, or status mean?” | [Reference]({{ '/docs/reference/' | relative_url }}) | factual contract lookup |
| “Why is GazeAudit designed this way?” | [Articles]({{ '/docs/articles/' | relative_url }}) | conceptual explanation |
| “Which research workflow connects several methods?” | [Workflows]({{ '/docs/workflows/' | relative_url }}) | project-level sequences |
| “What happened in the frozen validation programme?” | [Validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) | protocol-bound evidence authority |

This separation follows the same basic distinction used by the Diátaxis documentation framework: tutorials/examples, how-to guidance, reference, and explanation serve different user needs.

## Open search

Use either:

- **Ctrl/Cmd + K** from anywhere on the site;
- **/** when focus is not already inside a text field; or
- the **Search** button in the header or mobile documentation dock.

The search query remains in the input while you inspect the result groups.

## Search by the smallest distinctive phrase

Prefer the exact concept you need rather than a full research question.

| Need | Useful search |
|---|---|
| own CSV onboarding | `first real audit` |
| specification execution | `run_specs` |
| non-finite endpoint behavior | `NaN` or `non-finite` |
| denominator vocabulary | `declared valid successful` |
| reviewer revision CLI | `CLI command` or `revision package` |
| AOI measurement uncertainty | `AOI uncertainty` |
| frozen Korthals outcome | `robust_negative` |

The quick-query chips in the dialog provide common starting points. They set only the search text; they do not make a scientific selection.

## Read the result groups before opening a page

Search results are grouped by documentation type. The same topic can legitimately appear in several groups.

For example, searching **AOI uncertainty** may surface:

- a **Guide** explaining the workflow;
- an **Example** showing synthetic code;
- a **Reference** page listing exact APIs;
- an **Evidence** page describing a frozen case.

That is intentional. Choose the group that matches the information need rather than assuming the top result is a scientific recommendation.

## Use the type filter when the intent is already clear

The type buttons narrow the current query to one documentation kind. Useful combinations include:

- `run_specs` + **Reference** when you need the exact public contract;
- `run_specs` + **Example** when you need runnable context;
- `revision package` + **Guide** for the workflow;
- `revision package` + **Reference** for exact CLI syntax;
- a validation label + **Evidence** when you need the frozen result authority.

Choose **All** again when the query is too narrow.

## Keyboard behavior

Inside the search dialog:

- **↑ / ↓** changes the selected result;
- **Enter** opens the selected result;
- **Esc** closes the dialog.

The selected result is announced through a dedicated live-status region. The result list itself remains ordinary linked content, so it can still be traversed with standard browser and assistive-technology navigation.

## When search finds the contract, stop searching

Once you reach a reference page that answers the exact factual question, do not keep browsing merely to find a more convenient interpretation.

Examples:

- the [Evidence and denominator vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }}) defines how declared, valid, successful, and technically failed branches differ;
- the [CLI reference]({{ '/docs/reference/cli-reference/' | relative_url }}) defines installed console commands and structural validation behavior;
- the [API map]({{ '/docs/reference/api-map/' | relative_url }}) maps tasks to public functions;
- the [Validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) is authoritative for protocol-bound validation outcomes.

If the question changes from **“what is the contract?”** to **“what sequence should I follow?”**, move from Reference back to a Guide or Example.

## When search is not the right tool

Use [Troubleshooting GazeAudit]({{ '/docs/guides/troubleshooting/' | relative_url }}) if execution is blocked. Use the [Audit planner]({{ '/docs/planner/' | relative_url }}) when you need to route declared study conditions into documented method families. Use the [Researcher workspace]({{ '/docs/workspace/' | relative_url }}) when several project stages need to be connected.

None of those interfaces decides scientific validity for you.

## Accessibility and design rationale

The grouped search follows W3C cognitive-accessibility guidance to provide search and group results with headings when appropriate. It also follows U.S. Web Design System guidance to preserve the query, label the search control, support keyboard operation, and test the component in its actual site context.

- [W3C: Provide Search](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o2p06-search/)
- [USWDS: Search component](https://designsystem.digital.gov/components/search/)
- [Diátaxis documentation framework](https://diataxis.fr/start-here/)

## Worked companion

Use the [Search → contract walkthrough]({{ '/docs/examples/search-to-contract/' | relative_url }}) for a fully synthetic exercise that starts with three ambiguous search needs and shows how the result groups lead to the correct documentation layer without turning navigation into scientific advice.
