---
title: Reviewer reconstruction worked example
description: Walk through an illustrative GazeAudit manuscript archive as a reviewer and identify what is reconstructable, what is missing, and what must be repaired before submission.
kicker: Example · Review readiness
permalink: /docs/examples/reviewer-reconstruction/
search_category: Example
search_keywords: reviewer reconstruction manuscript readiness archive methods results limitations execution denominator robustness synthetic example
---

# Reviewer reconstruction worked example

This example treats a manuscript archive as if you were a reviewer who **did not participate in the analysis**. The goal is not to decide whether the synthetic result is scientifically important. The goal is to test whether the analysis and reporting record can be reconstructed without private context.

<div class="callout warning">
<strong>Illustrative evidence only.</strong>
Every participant count, estimate, threshold, specification, and manuscript sentence below is synthetic teaching material. Nothing on this page changes GazeAudit's frozen empirical validation records.
</div>

## Scenario

A manuscript states:

> The effect was robust across alternative preprocessing choices.

The authors provide an archive containing:

```text
submission-archive/
  decision-log.md
  endpoint-definition.md
  specifications.csv
  execution-status.csv
  robustness-summary.csv
  methods.md
  results.md
  limitations.md
  software-versions.txt
  manifest.json
```

The declared specification space crossed:

- missingness handling: `complete_case`, `bounded_interpolation`;
- minimum quality: `0.70`, `0.80`;
- sampling stride: `1`, `2`.

That creates **8 declared combinations**. One combination was ruled invalid before execution because the synthetic teaching protocol did not permit `bounded_interpolation` with `minimum_quality=0.80` and `stride=2`. Therefore the valid execution denominator is **7**, not 8.

## Step 1 — Reconstruct the endpoint

`endpoint-definition.md` says:

```text
Endpoint: condition-B minus condition-A mean dwell proportion
Unit: proportion points
Direction: positive values indicate greater dwell proportion in condition B
Aggregation: one estimate per declared valid analytical specification
```

The seven valid branches all estimate that same quantity.

**Reviewer finding:** endpoint reconstruction passes.

If one branch instead reported fixation count while the others reported dwell proportion, the archive would contain multiple scientific endpoints and the single robustness claim would be malformed.

## Step 2 — Reconstruct the denominator

`execution-status.csv` contains:

| spec_id | missingness | min_quality | stride | status |
|---|---|---:|---:|---|
| S01 | complete_case | 0.70 | 1 | success |
| S02 | complete_case | 0.70 | 2 | success |
| S03 | complete_case | 0.80 | 1 | success |
| S04 | complete_case | 0.80 | 2 | success |
| S05 | bounded_interpolation | 0.70 | 1 | success |
| S06 | bounded_interpolation | 0.70 | 2 | technical_failure |
| S07 | bounded_interpolation | 0.80 | 1 | success |
| S08 | bounded_interpolation | 0.80 | 2 | invalid_by_rule |

So the accounting is:

- declared combinations: **8**;
- invalid by pre-specified rule: **1**;
- valid combinations: **7**;
- successful valid branches: **6**;
- technically failed valid branches: **1**.

**Reviewer finding:** the archive is **not a complete seven-branch execution**, even though six estimates are available.

This is the first problem with the manuscript sentence. “Robust across alternative preprocessing choices” hides an unresolved valid branch.

## Step 3 — Inspect the successful estimates

The six synthetic successful estimates are:

| spec_id | estimate |
|---|---:|
| S01 | +0.041 |
| S02 | +0.039 |
| S03 | +0.036 |
| S04 | +0.043 |
| S05 | +0.031 |
| S07 | +0.028 |

Among the successful subset:

- all six estimates are positive;
- range = `0.028` to `0.043`;
- no successful branch changes sign.

**Reviewer finding:** the successful subset is directionally consistent, but this does not resolve S06.

Do **not** convert six positive estimates into “100% robust.” The denominator relevant to the declared valid space is seven, and one valid branch has no estimate.

## Step 4 — Check why S06 failed

`execution-status.csv` links S06 to a failure note:

```text
Failure: bounded interpolation produced no analyzable observations after the
predeclared quality rule for this branch.
Disposition: unresolved; branch retained in denominator; no replacement rule added.
```

The failure is not silently removed and no post-result repair branch is introduced.

**Reviewer finding:** failure handling is transparent, but the audit remains incomplete for the full valid space.

## Step 5 — Compare the decision log with the Methods

The decision log records the specification factors before outcome inspection. It also records one later amendment:

```text
Amendment: clarified the prose definition of bounded interpolation.
Results already inspected? yes
Scientific effect on specification space? none
```

The Methods section reports the same factor levels and explicitly marks S08 as invalid by the original rule.

**Reviewer finding:** decision history and Methods agree.

A problematic archive would silently replace the original decision log with a cleaned-up post-result version.

## Step 6 — Compare Results wording with the evidence

### Original wording

> The effect was robust across alternative preprocessing choices.

This is too strong because it implies the declared valid space was completely evaluated.

### Bounded wording

> Six of seven declared valid specifications completed successfully. The six observed estimates were positive and ranged from 0.028 to 0.043 proportion points. One valid interpolation-based branch remained unresolved because it produced no analyzable observations after the predeclared quality rule; therefore the full declared space was not completely evaluated.

This wording preserves three distinct facts:

1. what was successfully observed;
2. what pattern those observed estimates showed;
3. what remains unresolved.

It does not invent an estimate for S06 or downgrade the denominator from seven to six.

## Step 7 — Check the limitations section

A reviewer should find the unresolved branch again in `limitations.md`:

> The specification audit did not yield an estimate for one of seven valid declared branches. Directional consistency among the six successful branches therefore should not be interpreted as evidence that the unresolved branch would have produced the same sign or magnitude.

**Reviewer finding:** the limitation matches the execution record and Results wording.

## Step 8 — Check software identity and archive binding

`software-versions.txt` records an exact GazeAudit release or commit and material dependencies. `manifest.json` enumerates the files used for the manuscript claim. Where deterministic fingerprints are part of the workflow, the archive preserves and verifies them.

The reviewer should not have to infer that “current package version” means a particular commit.

## Reconstruction scorecard

This scorecard is a **record-completeness teaching device**, not a scientific validity score.

| Question | Reconstructable? | Evidence |
|---|---|---|
| Endpoint definition | yes | `endpoint-definition.md` |
| Declared denominator | yes | `specifications.csv` |
| Invalid combinations | yes | decision log + S08 status |
| Valid failures | yes | S06 status + failure note |
| Complete observed pattern | yes | `robustness-summary.csv` |
| Researcher amendments | yes | `decision-log.md` |
| Exact software identity | yes | `software-versions.txt` |
| Full valid-space conclusion | **no** | S06 unresolved |

The correct response to the final row is not to lower the denominator. It is to keep the claim bounded to what the archive actually establishes.

## What would fail review readiness?

Any of these would break reconstruction:

- `specifications.csv` contains only the six successful rows;
- S08 disappears instead of being identified as invalid by rule;
- S06 disappears instead of being recorded as a technical failure;
- the Methods section lists factors not present in the decision log;
- the endpoint definition changes across branches;
- the Results sentence says “all specifications” despite the unresolved branch;
- the archive records only a floating software label such as “latest”;
- limitations omit the unresolved denominator;
- descriptive sensitivity outputs are presented as causal explanations.

## Repair before submission

For this synthetic scenario, the minimum repair is **reporting repair**, not post-hoc analytical optimisation:

1. keep S06 in the valid denominator;
2. preserve the failure reason;
3. replace the blanket robustness claim with bounded wording;
4. repeat the unresolved branch in limitations;
5. archive the exact software identity and complete execution table.

If the researchers later decide that another scientifically defensible execution policy is necessary, that change should be documented as a new amendment or protocol version rather than silently replacing the original audit.

## Reviewer-ready handoff sentence

> The archive defines one endpoint, accounts for all eight declared combinations, identifies one pre-specified invalid combination, preserves one unresolved valid branch, and reports the six successful estimates without treating the successful subset as the complete declared space.

That sentence describes record reconstruction. It is not an automatic judgement about the scientific importance of the effect.

## Continue with

- [Manuscript readiness checklist](../guides/manuscript-readiness/) — apply the same reconstruction gates to a real project.
- [Interpret an audit result](../guides/interpret-audit-result/) — separate completeness, direction, magnitude, and unresolved uncertainty.
- [Publication/archive handoff](publication-archive-handoff/) — assemble the broader archive.
- [Reproducible publication workflow](../workflows/reproducible-publication/) — verify and preserve deterministic publication evidence.
