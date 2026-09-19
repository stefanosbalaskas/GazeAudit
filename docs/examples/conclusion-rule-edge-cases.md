---
title: Conclusion-rule edge cases
description: Deterministic synthetic examples for GazeAudit ConclusionRule covering missing tolerances, invalid thresholds, dual-tolerance conjunction, sign recovery, zero reference effects, threshold equality, circular-reference boundaries, and bounded reporting.
kicker: Example · Conclusion governance
page_type: example
permalink: /docs/examples/conclusion-rule-edge-cases/
search_category: Example
search_keywords: ConclusionRule recovery robust fragile tolerance sign zero reference threshold edge cases synthetic
example_data: "Synthetic"
example_focus: "Interpretation & reporting"
example_reuse: "Reference / tolerance / sign / recovery-threshold edge-case pattern"
example_output: "Deterministic branch-recovery tables and summary classifications"
example_boundary: "Teaching reference effects and tolerances are not recommended empirical thresholds or generic robustness rules."
---

# Conclusion-rule edge cases

This exercise uses deliberately small synthetic values to expose the exact `ConclusionRule` contract.

<div class="callout warning">
<strong>Teaching values only.</strong>
The reference effects, tolerances, and recovery thresholds below are selected to make edge cases visible. They are not recommendations for an empirical study.
</div>

## Case 1 · A rule needs at least one tolerance

```python
from gazeaudit import ConclusionRule

ConclusionRule()
```

Expected result:

```text
ValueError:
at least one of relative_tolerance or absolute_tolerance is required
```

The runtime does not allow a branch-recovery rule with no numerical error criterion.

## Case 2 · Tolerances must be finite and non-negative

These are invalid:

```python
ConclusionRule(absolute_tolerance=-1.0)
ConclusionRule(relative_tolerance=float("inf"))
ConclusionRule(relative_tolerance=float("nan"))
```

The same applies to either tolerance field.

A tolerance is a scientific threshold; invalid numeric values fail rather than being silently coerced.

## Case 3 · Both tolerances mean AND, not OR

Suppose:

```text
reference effect = 10
estimate = 12
absolute tolerance = 3
relative tolerance = 0.10
```

Then:

```text
absolute error = |12 - 10| = 2
relative error = 2 / 10 = 0.20
```

The absolute tolerance passes:

```text
2 <= 3
```

The relative tolerance fails:

```text
0.20 > 0.10
```

Because both declared tolerances must be satisfied, the branch does **not** recover the tolerance criterion.

```python
import pandas as pd

from gazeaudit import ConclusionRule, conclusion_recovery_table

results = pd.DataFrame({"estimate": [12.0]})

rule = ConclusionRule(
    absolute_tolerance=3.0,
    relative_tolerance=0.10,
    require_sign=True,
    minimum_recovery_fraction=1.0,
)

recovery = conclusion_recovery_table(
    results,
    true_effect=10.0,
    rule=rule,
)

assert bool(recovery.loc[0, "absolute_tolerance_recovered"])
assert not bool(recovery.loc[0, "relative_tolerance_recovered"])
assert not bool(recovery.loc[0, "tolerance_recovered"])
assert not bool(recovery.loc[0, "conclusion_recovered"])
```

Do not read two tolerance fields as interchangeable alternatives.

## Case 4 · Sign recovery is independent of tolerance recovery

Use a deliberately wide absolute tolerance:

```text
reference = +10
estimate = -10
absolute error = 20
absolute tolerance = 25
```

Tolerance passes.

### Sign required

```python
strict_direction = ConclusionRule(
    absolute_tolerance=25.0,
    require_sign=True,
    minimum_recovery_fraction=1.0,
)

strict = conclusion_recovery_table(
    pd.DataFrame({"estimate": [-10.0]}),
    true_effect=10.0,
    rule=strict_direction,
)

assert bool(strict.loc[0, "tolerance_recovered"])
assert not bool(strict.loc[0, "sign_recovered"])
assert not bool(strict.loc[0, "conclusion_recovered"])
```

### Sign not required

```python
tolerance_only = ConclusionRule(
    absolute_tolerance=25.0,
    require_sign=False,
    minimum_recovery_fraction=1.0,
)

relaxed = conclusion_recovery_table(
    pd.DataFrame({"estimate": [-10.0]}),
    true_effect=10.0,
    rule=tolerance_only,
)

assert bool(relaxed.loc[0, "tolerance_recovered"])
assert bool(relaxed.loc[0, "conclusion_recovered"])
```

This difference comes from the scientific rule, not from statistical significance.

## Case 5 · Zero reference effects cannot use relative tolerance

A relative error from zero is undefined.

```python
zero_relative = ConclusionRule(
    relative_tolerance=0.10,
    require_sign=True,
    minimum_recovery_fraction=1.0,
)

conclusion_recovery_table(
    pd.DataFrame({"estimate": [0.0]}),
    true_effect=0.0,
    rule=zero_relative,
)
```

Expected result:

```text
ValueError:
relative_tolerance cannot be evaluated when true_effect is zero;
provide absolute_tolerance
```

### Use absolute tolerance instead

```python
zero_absolute = ConclusionRule(
    absolute_tolerance=0.5,
    require_sign=True,
    minimum_recovery_fraction=1.0,
)

zero_recovery = conclusion_recovery_table(
    pd.DataFrame({"estimate": [0.2]}),
    true_effect=0.0,
    rule=zero_absolute,
)

assert bool(zero_recovery.loc[0, "tolerance_recovered"])
assert bool(zero_recovery.loc[0, "sign_recovered"])
assert bool(zero_recovery.loc[0, "conclusion_recovered"])
```

For a zero reference:

- `relative_error` is `NaN`;
- `effect_ratio` is `NaN`;
- sign recovery is treated as recovered;
- the absolute tolerance carries the branch-level error criterion.

Do not add a fake epsilon to create a percentage error.

## Case 6 · Equality at the recovery threshold passes

Create five synthetic estimates around a true/reference effect of 10:

```python
results = pd.DataFrame(
    {
        "estimate": [
            10.0,
            10.5,
            9.5,
            11.0,
            12.0,
        ]
    }
)
```

Use:

```text
absolute tolerance = 1.0
require sign = True
```

The first four estimates recover the target; the fifth does not.

Therefore:

```text
recovered = 4 / 5
recovery fraction = 0.80
```

### Minimum = 0.80

```python
from gazeaudit import summarize_conclusion_recovery

rule_080 = ConclusionRule(
    absolute_tolerance=1.0,
    require_sign=True,
    minimum_recovery_fraction=0.80,
)

recovery_080 = conclusion_recovery_table(
    results,
    true_effect=10.0,
    rule=rule_080,
)

summary_080 = summarize_conclusion_recovery(
    recovery_080,
    rule_080,
)

assert summary_080["conclusion_recovery_fraction"] == 0.80
assert summary_080["classification"] == "robust"
```

Equality passes because the runtime uses:

```text
recovery_fraction >= minimum_recovery_fraction
```

### Minimum = 0.81

Use the same evidence:

```python
rule_081 = ConclusionRule(
    absolute_tolerance=1.0,
    require_sign=True,
    minimum_recovery_fraction=0.81,
)

recovery_081 = conclusion_recovery_table(
    results,
    true_effect=10.0,
    rule=rule_081,
)

summary_081 = summarize_conclusion_recovery(
    recovery_081,
    rule_081,
)

assert summary_081["conclusion_recovery_fraction"] == 0.80
assert summary_081["classification"] == "fragile"
```

The evidence did not change.

The **declared rule** changed.

That is why the minimum recovery fraction must be justified before result inspection.

## Case 7 · Python defaults are not scientific defaults

This is valid Python:

```python
ConclusionRule(
    absolute_tolerance=1.0,
)
```

The dataclass currently supplies:

```text
require_sign = True
minimum_recovery_fraction = 0.90
```

Those are software defaults.

They are not universal methodological recommendations.

For a governed analysis, prefer explicit code:

```python
rule = ConclusionRule(
    relative_tolerance=None,
    absolute_tolerance=1.0,
    require_sign=True,
    minimum_recovery_fraction=0.80,
)
```

and preserve the study-specific rationale for every scientific argument.

The [Conclusion Rule Design Center]({{ '/docs/conclusion-rule/' | relative_url }}) intentionally requires those choices rather than inheriting them.

## Case 8 · A circular real-data reference invalidates the interpretation

Suppose eight robustness estimates are already visible.

Bad workflow:

1. compute their median;
2. call that median the reference effect;
3. evaluate whether the same eight estimates recover that reference;
4. label the result robust.

This is circular.

The evaluated evidence has defined its own target.

Better options:

- remain descriptive;
- use known truth in a simulation;
- use an independently justified reference fixed before result inspection;
- label a later reviewer-requested rule explicitly as a post-result amendment.

The package can make the circular workflow reproducible.

Reproducibility does not make it scientifically valid.

## Case 9 · Incomplete execution comes before classification

Suppose the specification declaration contains:

```text
8 valid branches
```

but only:

```text
7 successful finite endpoint estimates
```

A recovery summary computed on the seven available rows describes those seven rows.

It does not make the missing eighth valid branch disappear.

Preferred reporting:

> Seven of eight valid specifications yielded finite endpoints. Six of the seven represented estimates satisfied the declared recovery rule. Because one valid branch remained unresolved, the original valid specification space was incompletely represented.

Do not report only:

> Six of seven specifications recovered the target.

That silently changes the scientific denominator.

## Compact edge-case table

| Situation | Runtime consequence | Scientific reporting rule |
|---|---|---|
| no tolerance | rule construction fails | define at least one justified tolerance |
| negative/non-finite tolerance | rule construction fails | preserve valid finite non-negative threshold |
| both tolerances | both must pass | report both criteria |
| sign required | opposite sign can fail despite tolerance | report sign criterion separately |
| zero reference + relative tolerance | recovery evaluation fails | use justified absolute tolerance |
| recovery exactly equals minimum | `robust` | state equality to declared cutoff |
| same evidence, higher cutoff | can become `fragile` | threshold choice must predate results |
| hidden Python defaults | code runs | make scientific choices explicit |
| circular real-data reference | code can run | interpretation remains scientifically circular |
| unresolved valid branch | represented set incomplete | report execution completeness first |

## Methods example

> The recovery target was fixed before robustness inspection at 10 endpoint units using an independently defined synthetic truth. Branch recovery required an absolute error no greater than 1 unit and matching effect direction. The summary rule required at least 80% of represented valid specifications to recover the target.

## Results example

> Four of five represented synthetic specifications satisfied the branch-level recovery rule (recovery fraction = 0.80), exactly meeting the declared minimum of 0.80. The rule-based summary therefore returned `robust` for the supplied five-row recovery table.

## Limitation example

> The `robust` classification is conditional on the synthetic reference effect, absolute tolerance, sign rule, 80% minimum recovery fraction, and represented specification set. It is not a statistical-significance statement or a transferable threshold for an empirical study.

## API links

- [`ConclusionRule`]({{ '/docs/reference/api-pathways/#api-conclusionrule' | relative_url }})
- [`summarize_conclusion_recovery()`]({{ '/docs/reference/api-pathways/#api-summarize-conclusion-recovery' | relative_url }})
- [`build_conclusion_audit_bundle()`]({{ '/docs/reference/api-pathways/#api-build-conclusion-audit-bundle' | relative_url }})
- [Conclusion Rule Design Center]({{ '/docs/conclusion-rule/' | relative_url }})
- [Design conclusion-recovery rules]({{ '/docs/guides/conclusion-rule-design/' | relative_url }})

## Reuse boundary

Reuse:

- the validation sequence;
- zero-reference handling;
- dual-tolerance AND semantics;
- sign-versus-tolerance separation;
- recovery-threshold equality logic;
- completeness-first reporting.

Rebuild:

- reference effect;
- reference provenance;
- tolerances;
- sign rule;
- minimum recovery fraction;
- endpoint;
- execution denominator;
- scientific interpretation.
