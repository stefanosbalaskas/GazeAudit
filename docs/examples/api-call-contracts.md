---
title: Generated API call contracts
description: A fully synthetic interface-reading exercise for required positional arguments, required keyword-only arguments, all-optional signatures, return annotations, and minimal call shapes.
kicker: Example · API contracts
permalink: /docs/examples/api-call-contracts/
search_category: Example
search_keywords: api call contract parameters required keyword-only returns minimal call run_specs make_peyes_detector simulate_known_aoi_effect synthetic
page_type: example
example_data: "Documentation-only"
example_focus: "Documentation & API"
example_reuse: "Interface-reading pattern"
example_output: "Interpreted parameter, return, and minimal-call contracts"
example_boundary: "Software-call structure does not choose scientific values."
---

# Generated API call contracts

This is a **fully synthetic interface-reading exercise**. It teaches how to read the generated public-call contract without inventing study values. A minimal call shape is not a completed analysis, a scientific recommendation, or evidence that an omitted software default is appropriate.

The source of truth is the deterministic metadata generated from the installed public API. Open each symbol on [API pathways]({{ '/docs/reference/api-pathways/' | relative_url }}), then expand **Parameters & minimal call**.

## 1. Required positional arguments: `run_specs`

[Open `run_specs`]({{ '/docs/reference/api-pathways/' | relative_url }}#api-run-specs)

The current generated minimal call is:

```python
run_specs(study, space, endpoint)
```

Read this as a **call structure**:

- `study`, `space`, and `endpoint` have no Python defaults, so they appear in the minimal call;
- optional keyword-only arguments such as `processor` and `valid_if` are omitted;
- the placeholders do not create a `GazeStudy`, choose a specification space, or define a scientifically defensible endpoint.

The contract card also reports the inspected return annotation. For `run_specs`, that lets you verify the interface-level expectation that the call returns a pandas DataFrame before you move to the specification-space guide for research decisions.

## 2. Required keyword-only argument: `make_peyes_detector`

[Open `make_peyes_detector`]({{ '/docs/reference/api-pathways/' | relative_url }}#api-make-peyes-detector)

Its current minimal call keeps the required keyword-only parameter explicit:

```python
make_peyes_detector(
    algorithm,
    min_event_duration=min_event_duration,
)
```

The repeated name on the right-hand side is a placeholder. The generated contract deliberately does **not** fabricate an event-duration value.

This distinction is useful when reading a signature containing `*`: the parameter table can show that an argument is required by Python while the call shape preserves the fact that it must be supplied by keyword.

## 3. All-optional signature: `simulate_known_aoi_effect`

[Open `simulate_known_aoi_effect`]({{ '/docs/reference/api-pathways/' | relative_url }}#api-simulate-known-aoi-effect)

Because every public parameter currently has a Python default, the generated minimal call is:

```python
simulate_known_aoi_effect()
```

That does **not** mean the default simulation settings are scientifically preferred, universal, or suitable for a real study. It only means Python can call the function without additional arguments.

For teaching or benchmarking, inspect the parameter table before changing any default and record why a changed value is appropriate for the exercise.

## 4. Class constructor: `GazeStudy`

[Open `GazeStudy`]({{ '/docs/reference/api-pathways/' | relative_url }}#api-gazestudy)

The current minimal constructor shape is:

```python
GazeStudy(data)
```

This communicates that a data object is required while the canonical column-name arguments have software defaults. It does not guarantee that an arbitrary DataFrame already has the required semantics or structural quality.

When the question becomes “how should this table be mapped and checked?”, leave the contract surface and use [Data onboarding and structural preflight]({{ '/docs/guides/data-onboarding/' | relative_url }}).

## 5. Compare the contract with local introspection

You can reproduce the underlying signature information locally:

```python
import inspect

from gazeaudit import make_peyes_detector, run_specs

for callable_ in (run_specs, make_peyes_detector):
    signature = inspect.signature(callable_)
    print(callable_.__name__)
    print(signature)
    for parameter in signature.parameters.values():
        print(parameter.name, parameter.kind, parameter.default)
    print("returns:", signature.return_annotation)
```

The website generator turns the same categories into deterministic JSON and derives the minimal call shape from **required** parameters only. CI regenerates that artifact and compares it byte-for-byte with the checked-in reference.

## What the generated contract can and cannot answer

| Question | Contract can answer? |
|---|---|
| Which arguments lack Python defaults? | Yes |
| Is a required argument keyword-only? | Yes |
| What return annotation is declared? | Yes |
| What is the smallest structural call shape? | Yes |
| Which AOI, threshold, endpoint, or exclusion should my study use? | No |
| Is a software default scientifically justified for my design? | No |
| Does the function have transferable empirical validity for my dataset? | No |

Use [Read the source-level API reference]({{ '/docs/guides/read-api-reference/' | relative_url }}) for the interpretation rules, and use the symbol's linked guide, runnable example, visual, and evidence boundary when the question moves from software interface to research design.
