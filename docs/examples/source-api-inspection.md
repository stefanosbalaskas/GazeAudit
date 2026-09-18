---
title: Source-level API inspection
description: A fully synthetic documentation exercise showing how to verify GazeStudy, run_specs, and aoi_probabilities from generated signatures through source links and governed pathways.
kicker: Example · API reference
permalink: /docs/examples/source-api-inspection/
search_category: Example
search_keywords: source api inspect signature GazeStudy run_specs aoi_probabilities source link pathway import synthetic
---

# Source-level API inspection

This is a **fully synthetic documentation exercise**. It shows how to verify a public interface and locate its surrounding documentation. It does not determine whether any method is scientifically appropriate for a real study.

## 1. Inspect `GazeStudy`

Open the direct symbol route:

[Open `GazeStudy`]({{ '/docs/reference/api-pathways/' | relative_url }}#api-gazestudy)

The enhanced symbol card exposes the currently installed class signature, source module, source line, docstring summary, and import:

```python
from gazeaudit import GazeStudy
```

The pathway backlink places the class inside **Structural QC**. Follow the linked data-onboarding guide or study-preflight example when the question changes from “what is the constructor contract?” to “how should I map my table?”

## 2. Inspect `run_specs`

Open:

[Open `run_specs`]({{ '/docs/reference/api-pathways/' | relative_url }}#api-run-specs)

Use the signature to verify which arguments are required and which are keyword-only. Then use **View source** when you need implementation-level confirmation.

For example, the current source-level contract is relevant when asking whether execution failures are silently converted into a status row. The [Evidence vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }}) explains the audited interpretation boundary; the source link lets you verify the implementation directly.

A minimal local inspection is:

```python
import inspect

from gazeaudit import run_specs

print(inspect.signature(run_specs))
print(inspect.getsourcefile(run_specs))
```

That is an inspection snippet, not a scientific analysis.

## 3. Inspect `aoi_probabilities`

Open:

[Open `aoi_probabilities`]({{ '/docs/reference/api-pathways/' | relative_url }}#api-aoi-probabilities)

The symbol is linked to the **AOI measurement uncertainty** pathway. From the same surface you can reach:

- the exact generated signature and source;
- the AOI uncertainty guide;
- the boundary example;
- the AOI probability-profile visual;
- the Korthals evidence boundary.

The Korthals link supplies protocol-bound context. It does not turn the function into a universally validated estimator for every AOI design.

## 4. Search a symbol directly

Open site search with **Ctrl/Cmd + K** and enter:

```text
run_specs
```

For non-empty queries, generated public symbols join the documentation search catalog as **Reference / API symbol** results. Selecting the result opens the exact symbol fragment rather than only the top of the API Pathways page.

The normal empty-query search remains documentation-focused; 36 symbol records are not dumped into the default browse state.

## 5. Compare website metadata with local introspection

For any governed symbol:

```python
import inspect

from gazeaudit import aoi_probabilities

print(inspect.signature(aoi_probabilities))
print(inspect.getmodule(aoi_probabilities).__name__)
print(inspect.getsourcelines(aoi_probabilities)[1])
```

The website generator records these same categories into a deterministic JSON artifact. CI regenerates the artifact from the installed package and compares it byte-for-byte with the checked-in reference.

## What is safe to infer?

| Metadata | Safe interpretation |
|---|---|
| signature | current Python calling contract for this revision |
| parameter default | software default, if one exists |
| annotation | interface/type metadata |
| docstring summary | source-authored compact description |
| source link | implementation location for this documentation revision |
| pathway backlink | governed documentation context |
| evidence link | context-specific evidence boundary |

None of those alone establishes that a scientific choice is suitable for a new dataset.

Return to [Read the source-level API reference]({{ '/docs/guides/read-api-reference/' | relative_url }}) for the general rules.
