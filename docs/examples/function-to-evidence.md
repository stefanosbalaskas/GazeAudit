---
title: Function to evidence walkthrough
description: A fully synthetic navigation exercise that starts from a GazeAudit public symbol and follows its governed path to a guide, runnable example, visual, and evidence boundary.
kicker: Example · Reference
permalink: /docs/examples/function-to-evidence/
search_category: Example
search_keywords: api symbol function deep link example plot evidence boundary run_specs aoi_probabilities read_bids_eyetrack synthetic navigation
page_type: example
example_data: "Documentation-only"
example_focus: "Documentation & API"
example_reuse: "Symbol-to-context navigation pattern"
example_output: "Function-to-guide-example-visual-evidence route"
example_boundary: "Linked validation evidence remains protocol-bound."
---

# Function → example → evidence

This is a **fully synthetic documentation-navigation exercise**. It demonstrates how to move from a public API symbol to the surrounding GazeAudit documentation without turning that navigation path into a scientific recommendation.

The exercise uses three symbols with deliberately different evidence contexts:

1. `run_specs` — robustness execution;
2. `aoi_probabilities` — measurement uncertainty;
3. `read_bids_eyetrack` — interoperability.

## Start with `run_specs`

Open the direct symbol link:

[Open `run_specs` in API pathways]({{ '/docs/reference/api-pathways/' | relative_url }}#api-run-specs)

The symbol resolves into the **Specification-space robustness** pathway. From one governed card you can recover:

- the public API sequence: `PipelineSpace → run_specs → specification_curve → effect_stability`;
- the [Specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }});
- the [End-to-end robustness example]({{ '/docs/examples/end-to-end-robustness/' | relative_url }});
- the specification-curve visual;
- the pathway's evidence boundary.

The linked GazeBase case is intentionally bounded: its frozen programme ended at the predeclared completeness gate. That does **not** mean `run_specs` is invalid, validated for every study, or guaranteed to produce a robust conclusion.

## Follow `aoi_probabilities`

Open:

[Open `aoi_probabilities` in API pathways]({{ '/docs/reference/api-pathways/' | relative_url }}#api-aoi-probabilities)

This resolves into **AOI measurement uncertainty**. The pathway connects:

```text
GaussianGazeErrorModel → aoi_probabilities → compare_hard_probabilistic → expected_dwell
```

to:

- the [AOI uncertainty guide]({{ '/docs/guides/aoi-uncertainty/' | relative_url }});
- the [AOI boundary example]({{ '/docs/examples/aoi-boundary/' | relative_url }});
- the AOI probability-profile visual;
- the Korthals frozen case and its exact evidence note.

The evidence link is contextual, not transferable. The Korthals `robust_negative` outcome belongs to that frozen protocol and dataset; it is not a generic status for every use of `aoi_probabilities`.

## Follow `read_bids_eyetrack`

Open:

[Open `read_bids_eyetrack` in API pathways]({{ '/docs/reference/api-pathways/' | relative_url }}#api-read-bids-eyetrack)

This resolves into **Interoperability**. The route connects external data/detector adapters to:

- the [Interoperability guide]({{ '/docs/guides/interoperability/' | relative_url }});
- canonical onboarding context;
- the gaze-trajectory/AOI visual;
- an evidence boundary stating that interoperability is guarded by live contract CI rather than a frozen empirical outcome.

That distinction is important: passing a software interoperability contract is not the same thing as empirically validating a scientific measurement claim.

## Use the direct links as bookmarks

A symbol fragment is a navigation handle:

```text
/docs/reference/api-pathways/#api-run-specs
/docs/reference/api-pathways/#api-aoi-probabilities
/docs/reference/api-pathways/#api-read-bids-eyetrack
```

It is useful in lab notes, issue reports, reviewer-response records, and internal documentation because it points collaborators to the same governed context.

It should not be cited as if the fragment itself were scientific evidence.

## What this walkthrough teaches

| Starting point | Governed pathway | Example | Evidence boundary |
|---|---|---|---|
| `run_specs` | Specification-space robustness | End-to-end robustness | GazeBase case stopped at completeness gate |
| `aoi_probabilities` | AOI measurement uncertainty | AOI boundary | Korthals outcome is protocol-bound |
| `read_bids_eyetrack` | Interoperability | Canonical onboarding | live software contract, not frozen empirical validation |

## Reusable pattern

```text
public symbol
    ↓
stable symbol link
    ↓
governed method family
    ↓
guide + runnable example + visual
    ↓
explicit evidence boundary
```

When you do not know the symbol yet, start with the [Method explorer]({{ '/docs/methods/' | relative_url }}). When you know the symbol but need the exact source-level contract, use the [API map]({{ '/docs/reference/api-map/' | relative_url }}) alongside the package docstring.
