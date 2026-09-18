---
title: Read the source-level API reference
description: Interpret generated GazeAudit signatures, parameter kinds, defaults, source links, import snippets, and pathway backlinks without treating interface metadata as scientific advice.
kicker: Guide · API reference
permalink: /docs/guides/read-api-reference/
search_category: Guide
search_keywords: api reference signature parameters defaults annotations source code inspect import symbol pathway deep link function class
---

# Read the source-level API reference

The [API pathways]({{ '/docs/reference/api-pathways/' | relative_url }}) page combines two different kinds of information:

1. **static research context** from the governed method catalog: method family, guide, runnable example, visual, and evidence boundary;
2. **generated source metadata** from the installed GazeAudit package: signature, structured parameter contract, return annotation, minimal call shape, callable kind, module, source file/line, docstring summary, import statement, and pathway backlinks.

Keeping those layers separate matters. A Python signature can tell you what arguments a callable accepts. It cannot tell you whether a threshold, endpoint, exclusion, or model is scientifically appropriate.

## Read a generated symbol card

When metadata loads, a symbol such as `run_specs` gains a detail card containing:

- **function/class** — the inspected callable kind;
- **signature** — Python's current callable signature;
- **parameters & minimal call** — an expandable contract showing parameter name, Python parameter kind, annotation, whether the argument is required, any software default, and a mechanically derived minimal call shape;
- **returns** — the inspected return annotation when one is present;
- **summary** — the first line of the source docstring;
- **module** — where the public export is defined;
- **source** — repository-relative file and first source line;
- **used by pathways** — every governed method family that references the symbol;
- **copy call / copy import** — the generated minimal call shape and exact public import statement.

The source link is pinned to the same Git revision used to build the documentation, so the visible signature and linked source remain revision-aligned.

## Understand signature markers

GazeAudit generates signatures with Python's standard `inspect.signature()`. Python defines the parameter kinds represented by the signature, including positional-only, positional-or-keyword, variadic positional, keyword-only, and variadic keyword parameters.

Two punctuation markers are especially useful:

- `/` means parameters before it are **positional-only**;
- `*` means following parameters are **keyword-only** unless captured by `*args`.

A default such as `processor=None` describes the Python call contract. It is not a scientific default for your study.

### Required does not mean scientifically required

The generated parameter table marks a parameter **Required** only when Python's signature has no default for that parameter and it is not `*args` or `**kwargs`. That is a software-call requirement, not a claim that the corresponding construct, threshold, or modelling choice is scientifically mandatory.

For Python's authoritative signature semantics, see [`inspect.signature`](https://docs.python.org/3/library/inspect.html#inspect.signature).

## Treat annotations as interface metadata

Annotations help describe expected Python objects and return values. They may include GazeAudit classes, pandas objects, mappings, callables, or scalar types.

Annotations do not establish:

- empirical validity;
- measurement validity;
- appropriate sampling thresholds;
- a defensible missingness mechanism;
- a valid exclusion policy;
- a causal interpretation.

Use the linked guide and evidence boundary for that surrounding context.

## Use source links for implementation questions

Open **View source** when the question is implementation-specific, for example:

- Does `run_specs()` catch a processor exception?
- Is a result converted with `float(...)`?
- Does a sampling helper interpolate coordinates or retain observed samples?
- Which object actually owns a validation check?

The source link is for verifying implementation behavior, not for replacing the public contract with undocumented internals.

## Use pathway backlinks for research context

A symbol can appear in more than one governed method family. The generated **Used by pathways** backlinks expose that relationship directly.

This avoids a common documentation problem: seeing one function in isolation and assuming it belongs to only one research task.

## Read the minimal call shape

The generated card also derives a **minimal call shape** from the public signature. It includes required positional arguments and required keyword-only arguments, while omitting optional arguments.

For example, the current `run_specs` contract yields:

```python
run_specs(study, space, endpoint)
```

Those names are placeholders for objects you must construct or justify elsewhere. The call shape is not guaranteed to run when pasted by itself, and it does not endorse omitted software defaults. Use it to answer “what must Python receive?”, not “what should my study choose?”.

A required keyword-only parameter remains explicit. For example, the current detector factory contract is represented as:

```python
make_peyes_detector(algorithm, min_event_duration=min_event_duration)
```

## Copy the import, not a fabricated analysis

The generated card exposes the smallest safe reusable import:

```python
from gazeaudit import run_specs
```

That import is mechanically derived from the public package export. The site deliberately does not fabricate required study objects, thresholds, AOIs, or endpoints merely to make every symbol look runnable in one line.

For an actual workflow, follow the linked runnable example.

## Verify the reference locally

You can inspect the installed package yourself:

```python
import inspect

from gazeaudit import run_specs

print(inspect.signature(run_specs))
print(inspect.getmodule(run_specs).__name__)
print(inspect.getdoc(run_specs).splitlines()[0])
```

The website metadata is generated with the same standard-library introspection machinery and checked in CI against the current source.

## When to use each API surface

| Need | Use |
|---|---|
| I know the research task, not the function | [API map]({{ '/docs/reference/api-map/' | relative_url }}) |
| I know the public symbol and want context/source | [API pathways]({{ '/docs/reference/api-pathways/' | relative_url }}) |
| I want the compact protected export inventory | [Core API inventory]({{ '/docs/reference/core-api-inventory/' | relative_url }}) |
| I need a runnable research sequence | [Examples]({{ '/docs/examples/' | relative_url }}) |
| I need exact frozen empirical evidence | [Validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) |

## Worked companion

Use [Source-level API inspection]({{ '/docs/examples/source-api-inspection/' | relative_url }}) to trace `GazeStudy`, `run_specs`, and `aoi_probabilities` from generated signature metadata into their source and governed research context. Then use [Generated API call contracts]({{ '/docs/examples/api-call-contracts/' | relative_url }}) to practise required positional arguments, required keyword-only arguments, all-optional signatures, and return annotations without inventing study values.
