---
title: Decision-to-report worked example
description: Use the deterministic synthetic robustness demo to practice declaring analytical choices, reading the complete 12-specification pattern, and translating it into bounded reporting language.
kicker: Example · Interpretation
permalink: /docs/examples/decision-to-report/
search_category: Examples
search_keywords: worked example interpretation reporting decision log specification robustness sign magnitude manuscript results synthetic audit
---

# Decision-to-report worked example

This example uses the repository's deterministic [`examples/end_to_end_robustness.py`](https://github.com/stefanosbalaskas/GazeAudit/blob/main/examples/end_to_end_robustness.py) demo to practice a part of robustness work that code alone cannot solve: **moving from researcher-owned decisions to a complete result pattern and then to appropriately scoped reporting language**.

<div class="callout info">
<strong>All values on this page are synthetic.</strong>
They exist only to demonstrate GazeAudit's workflow and interpretation boundaries. They are not empirical evidence about eye tracking, AOIs, quality thresholds, treatment effects, or any real dataset.
</div>

## The exercise

The synthetic study compares treatment-minus-control AOI occupancy while varying three declared analytical choices:

| Factor | Declared synthetic values | Teaching purpose |
|---|---|---|
| minimum quality | `0.70`, `0.80` | demonstrate a preprocessing/QC choice |
| sample stride | `1`, `2` | demonstrate sample-retention variation |
| AOI radius | `0.16`, `0.20`, `0.24` | demonstrate a measurement/geometry choice |

The Cartesian product contains **12 specifications**. The endpoint remains treatment-minus-control AOI occupancy in every branch.

These numbers are demonstration choices, not recommended thresholds or AOI sizes.

## 1. Write the decision record before reading the estimates

A minimal decision log for this teaching example would say:

```markdown
Endpoint:
  treatment-minus-control AOI occupancy

Held fixed:
  condition contrast
  AOI centre
  endpoint definition
  synthetic source generator

Declared factors:
  min_quality = [0.70, 0.80]
  sample_stride = [1, 2]
  aoi_radius = [0.16, 0.20, 0.24]

Valid combinations:
  all 12 Cartesian combinations

Failure policy:
  preserve every attempted branch and expose failures

Interpretation plan:
  inspect direction and magnitude across the complete declared space;
  do not select one branch as the preferred result after seeing outcomes
```

For a real study, the rationale for every value would need to come from the acquisition context, measurement model, design, prior evidence, protocol, or other scientifically defensible source.

Use the [audit decision-log template]({{ '/docs/guides/audit-decision-log-template/' | relative_url }}) for a complete project record.

## 2. Run the existing deterministic example

```bash
python examples/end_to_end_robustness.py
```

The script builds a synthetic `GazeStudy`, executes the complete `PipelineSpace`, and prints the specification results plus effect-stability, marginal-sensitivity, and pairwise-sensitivity summaries.

The underlying sequence is:

```python
space = (
    PipelineSpace()
    .add_choice("min_quality", [0.70, 0.80])
    .add_choice("sample_stride", [1, 2])
    .add_choice("aoi_radius", [0.16, 0.20, 0.24])
)

results = run_specs(
    study,
    space,
    endpoint=condition_aoi_occupancy_effect,
    processor=process_specification,
)
```

## 3. Read the complete specification pattern

For the deterministic synthetic data, the 12 estimates are:

| Minimum quality | Sample stride | AOI radius | Synthetic estimate |
|---:|---:|---:|---:|
| 0.70 | 1 | 0.16 | +0.0085 |
| 0.70 | 1 | 0.20 | -0.0325 |
| 0.70 | 1 | 0.24 | 0.0000 |
| 0.70 | 2 | 0.16 | +0.0075 |
| 0.70 | 2 | 0.20 | -0.0362 |
| 0.70 | 2 | 0.24 | 0.0000 |
| 0.80 | 1 | 0.16 | +0.0133 |
| 0.80 | 1 | 0.20 | -0.0339 |
| 0.80 | 1 | 0.24 | 0.0000 |
| 0.80 | 2 | 0.16 | +0.0210 |
| 0.80 | 2 | 0.20 | -0.0404 |
| 0.80 | 2 | 0.24 | 0.0000 |

The complete pattern contains:

- **4 positive** estimates;
- **4 negative** estimates;
- **4 zero** estimates;
- an observed synthetic range of approximately **-0.0404 to +0.0210**;
- a median of **0.0000** across the 12 declared branches.

No single row represents the robustness result. The result is the pattern across the declared space.

## 4. What changes the pattern most visibly?

In this synthetic exercise, the AOI-radius choice aligns with a conspicuous directional pattern:

- radius `0.16` produces positive estimates;
- radius `0.20` produces negative estimates;
- radius `0.24` produces zero estimates.

That observation is a **descriptive property of this synthetic specification table**. It does not establish that AOI radius is a causal mechanism, that one radius is scientifically correct, or that a similar pattern should occur in real data.

The package's marginal and pairwise sensitivity functions help summarise such movement systematically, but their outputs remain descriptive summaries of the declared analysis space.

## 5. Reporting language that matches the evidence

### Too strong

> The treatment effect was robust across analytical choices.

Why it fails: the synthetic estimate changes sign and reaches zero across the declared space.

### Also too strong

> AOI radius caused the instability in the treatment effect.

Why it fails: the specification table describes how estimates move with declared analytical choices; it does not identify a causal mechanism for that movement.

### Better bounded wording

> Across the 12 prespecified synthetic analysis branches, the treatment-minus-control occupancy estimate ranged from approximately -0.040 to +0.021. Four branches were positive, four were negative, and four were zero. The largest visible separation corresponded to the declared AOI-radius alternatives, indicating substantial analytical sensitivity within this demonstration space.

This wording reports what the table shows without turning descriptive robustness evidence into a population, posterior, significance, or causal claim.

## 6. Methods language for the same example

A compact Methods-style description could be:

> We evaluated a 12-branch synthetic specification space defined by two minimum-quality thresholds, two sample-retention strides, and three AOI radii while holding the treatment-minus-control occupancy endpoint fixed. All declared combinations were executed, and endpoint behaviour was summarised across the complete specification set using the specification curve, effect-stability, marginal-sensitivity, and pairwise-sensitivity outputs.

For a real manuscript, replace the synthetic values with the study's actual scientific rationale, preprocessing definitions, endpoint, and prespecified analytical alternatives.

## 7. What this exercise does not justify

Do **not** infer from this page that:

- `0.70` or `0.80` are recommended quality thresholds;
- `0.16`, `0.20`, or `0.24` are recommended AOI radii;
- sign changes are expected in empirical eye-tracking studies;
- the synthetic range is a confidence interval;
- the positive/negative fractions are posterior probabilities;
- marginal or pairwise sensitivity identifies causal importance;
- one branch should be selected as the final result.

## 8. Turn the example into your own audit

<div class="card-grid">
  <article class="card">
    <div class="card-icon" aria-hidden="true">1</div>
    <h3>Replace demonstration decisions</h3>
    <p>Use the real endpoint, scientifically defensible alternatives, invalid combinations, and uncertainty dimensions for the study.</p>
    <p><a href="{{ '/docs/guides/researcher-audit-checklist/' | relative_url }}">Researcher checklist →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">2</div>
    <h3>Run the full declared space</h3>
    <p>Preserve all valid branches and failures instead of narrowing the analysis after estimates are visible.</p>
    <p><a href="{{ '/docs/guides/specification-space/' | relative_url }}">Specification-space guide →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">3</div>
    <h3>Report the pattern you actually observed</h3>
    <p>Match wording to the generated evidence object and preserve the difference between robustness description and statistical inference.</p>
    <p><a href="{{ '/docs/guides/reporting-robustness/' | relative_url }}">Reporting guide →</a></p>
  </article>
</div>

## Next steps

- [End-to-end robustness audit]({{ '/docs/examples/end-to-end-robustness/' | relative_url }}) — executable API-focused companion example.
- [Researcher audit checklist]({{ '/docs/guides/researcher-audit-checklist/' | relative_url }}) — before/during/after governance checks.
- [Audit decision-log template]({{ '/docs/guides/audit-decision-log-template/' | relative_url }}) — copy-ready project record.
- [Audit output bundle]({{ '/docs/guides/audit-output-bundle/' | relative_url }}) — map saved artifacts to interpretation boundaries.
- [Reproducible publication]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) — bind the final archive and manuscript record.
