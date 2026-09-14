---
title: GazeBase — when the right answer is incomplete
description: Why GazeAudit preserved an incomplete multi-detector specification space instead of manufacturing a robustness classification.
permalink: /docs/case-studies/gazebase-incomplete/
kicker: Frozen case study · completeness gate
---

# GazeBase: when the right answer is **incomplete**

This case demonstrates a core GazeAudit rule: a declared specification space is not allowed to shrink after execution merely because some specifications are inconvenient or non-computable.

## Frozen question

The GazeBase protocol declared a seven-detector space and a 95% finite-participant completeness gate. The fixed cohort contained **322 participants**. A robustness classification was permitted only if the declared detector space satisfied the frozen completeness requirement.

<figure class="plot-card evidence-figure">
  <img src="{{ '/assets/images/gazebase-completeness.svg' | relative_url }}" alt="Coverage plot showing complete 322 of 322 finite participant estimates for IVT, IVVT, IDT, IDVT, and Engbert, but zero for NH and REMoDNaV, below the frozen 95 percent completeness gate">
  <figcaption><strong>Observed frozen result.</strong> Five detectors reached 322/322 finite participant estimates. NH and REMoDNaV reached 0/322 under the already-frozen NaN-preserving, no-interpolation policy.</figcaption>
</figure>

## What happened

| Detector | Finite participant estimates | Coverage |
|---|---:|---:|
| IVT | 322/322 | 100% |
| IVVT | 322/322 | 100% |
| IDT | 322/322 | 100% |
| IDVT | 322/322 | 100% |
| Engbert | 322/322 | 100% |
| NH | 0/322 | 0% |
| REMoDNaV | 0/322 | 0% |

The five computable detector estimates remain archived descriptive outputs, but they are not promoted into a robustness claim. Removing NH and REMoDNaV after seeing their failure would change the declared specification space after outcome inspection.

## Why `incomplete` is scientifically informative

The result shows that **workflow completeness is itself part of the scientific claim**. GazeAudit fails closed when a frozen prerequisite is violated. It does not silently delete failed specifications and then summarise the remainder as if the smaller space had been declared from the beginning.

This distinction matters whenever robustness analysis includes external detectors, preprocessing packages, model families, or other alternatives that may fail under a particular data contract.

<div class="callout callout-warning">
  <strong>Interpretation boundary.</strong> `incomplete` is not a statement that GazeBase is a poor dataset, that the five computable detectors are invalid, or that a different future protocol could not be executed. It means only that this exact frozen seven-detector analysis did not satisfy its own predeclared completeness gate.
</div>

## Provenance snapshot

- Frozen protocol fingerprint: `3f64122f62cbc9762b0bd0e0b95c7fef6ff40c4700215ee4b90f005af77003b1`
- Scientific commit: `609203dfc37f2ef4984de82b888660e7cc30675c`
- Final artifact: `gazebase-partitioned-final-609203df`
- Artifact ID: `10284017265`
- ZIP SHA-256: `2fae4e99243e6738047a34b8dc24a183e8fb98606e4873723d43b8baa4ae937b`
- Execution fingerprint: `35975d89dea728bd3aa146739dc58ea2bcb9322e357a44856b424fffb4183632`

## What to learn from this case

Use a completeness gate when the scientific meaning of the robustness audit depends on evaluating **all** predeclared alternatives. Decide in advance what counts as an admissible failure, whether failed specifications can be repaired, and whether a reduced space is scientifically equivalent to the original one. If it is not equivalent, stop rather than silently redefine the multiverse.

## Authoritative sources

This page is an explanatory view. The frozen authority remains the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}), [GazeBase protocol]({{ '/docs/case_studies/GAZEBASE_MULTIDETECTOR_PROTOCOL.html' | relative_url }}), and [controlled execution procedure]({{ '/docs/case_studies/gazebase_real_data_execution.html' | relative_url }}).
