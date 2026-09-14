---
title: From one pipeline to a robustness audit
description: Why a reasonable single analysis pipeline is not the same thing as evidence that a conclusion is robust.
kicker: Article · Robustness
---

# From one pipeline to a robustness audit

A conventional analysis often produces one path from raw or processed gaze data to one scientific estimate. Every decision in that path may be defensible. The problem is that **defensible does not mean unique**.

If another equally defensible detector, QC threshold, AOI rule, missing-data treatment, or preprocessing branch would have produced a meaningfully different endpoint, then the scientific conclusion depends partly on analytical choice.

A robustness audit makes that dependence visible.

## One pipeline answers a narrower question

A single pipeline can answer:

> What estimate do I obtain under this declared analysis?

It cannot, by itself, answer:

> Would the conclusion survive other reasonable analyses?

That second question requires an explicit comparison set.

## The specification space is a scientific object

GazeAudit represents the comparison set with `PipelineSpace`. The important part is not the Cartesian product machinery. The important part is that each factor and level becomes an auditable declaration.

For example:

```python
from gazeaudit import PipelineSpace

space = (
    PipelineSpace()
    .add_choice("detector", ["ivt", "idt"])
    .add_choice("qc", ["moderate", "strict"])
    .add_choice("aoi_mode", ["hard", "probabilistic"])
)
```

The scientific work happens before execution:

- Why are both detector families defensible?
- Why are those QC levels plausible?
- Is probabilistic AOI membership justified by validation evidence?
- Are all combinations meaningful?
- What endpoint has the same interpretation in every branch?

## Invalid combinations belong in the design, not the cleanup

A large multiverse can contain combinations that are methodologically incoherent. GazeAudit therefore supports a `valid_if` rule before execution.

This matters because excluding a combination after seeing its estimate creates a different scientific process from declaring in advance that the combination is invalid.

The first is outcome-sensitive filtering. The second is specification design.

## The common endpoint is the anchor

Robustness requires a stable scientific target.

If one specification returns dwell difference, another returns fixation count, and another returns a model coefficient with a different meaning, the resulting table does not isolate analytical sensitivity. It mixes different questions.

`run_specs()` therefore expects every valid branch to produce one scalar endpoint with the same scientific interpretation.

## A specification curve shows the shape of the decision space

Once one estimate exists per valid specification, ordering the estimates reveals information that one preferred pipeline hides.

<figure class="plot-card">
  <img src="{{ '/assets/images/specification-curve.svg' | relative_url }}" alt="Synthetic specification curve">
  <figcaption>Synthetic illustration. The scientific value of the curve is the complete pattern across declared specifications, not the identity of the most favourable point.</figcaption>
</figure>

A curve can show:

- invariant direction with modest magnitude variation;
- broad magnitude instability without sign reversal;
- distinct clusters associated with methods;
- a small subset of specifications that reverse the conclusion;
- complete directional instability.

Those patterns support different scientific interpretations.

## Robustness is not a search algorithm

The most important boundary is procedural.

A specification-space analysis should not become a larger menu from which the analyst selects the estimate they like best. GazeAudit's design principle is the opposite:

> define the defensible choices first, then quantify what those choices do to the conclusion.

A robust result is informative because it survives the declared alternatives. A fragile result is informative because it does not.

## Descriptive diagnostics localise instability

`effect_stability()` describes the overall estimate distribution and sign fractions.

`marginal_sensitivity()` asks which single declared factors are associated with the largest between-level differences.

`pairwise_interaction_sensitivity()` screens whether factor combinations depart strongly from an additive expectation.

These tools are not causal variance decompositions. Their role is diagnostic: they help explain **where** the decision space changes the endpoint.

## Controlled perturbations are related but distinct

Some uncertainty dimensions are more naturally represented as perturbation curves than categorical pipeline choices:

- spatial-error magnitude;
- target sampling rate;
- added missingness.

<figure class="plot-card">
  <img src="{{ '/assets/images/sensitivity-curves.svg' | relative_url }}" alt="Synthetic sensitivity curves">
  <figcaption>Keeping perturbation families explicit helps distinguish measurement sensitivity from ordinary analytical decision sensitivity.</figcaption>
</figure>

A strong robustness analysis can contain both a categorical specification space and controlled sensitivity curves, provided their scientific meanings remain distinct.

## What counts as “robust” depends on the claim

There is no universal rule that every estimate must remain numerically identical.

For one study, preserving direction may be sufficient for the substantive claim. For another, a 20% magnitude shift may invalidate a policy interpretation even though the sign remains stable. A known-truth benchmark may have an explicit recovery tolerance. A real-data analysis may need a narrower qualitative conclusion.

The robustness criterion should therefore be aligned with the scientific claim and, when formalised as a `ConclusionRule`, justified before final outputs are inspected.

## A fragile result can improve the science

If the conclusion changes materially across defensible choices, the robustness audit has discovered information that the single-pipeline analysis could not reveal.

That finding can motivate:

- narrower claims;
- better validation data;
- improved measurement design;
- stronger preprocessing justification;
- reporting of method-dependent estimates;
- targeted replication or sensitivity work.

Robustness analysis is therefore not only a confirmatory hurdle. It is a way to identify which parts of an analysis carry the scientific conclusion.

Continue with the [specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }}) or the [robustness audit workflow]({{ '/docs/workflows/robustness-audit/' | relative_url }}).
