---
title: Articles
description: Conceptual articles on measurement uncertainty, analytical robustness, fragility, interpretation, manuscript readiness, and peer-review revision in GazeAudit, with direct routes into practical guides and examples.
kicker: Articles
---

# Articles

These articles explain the methodological ideas behind GazeAudit. They are not substitutes for the API guides, researcher-owned study decisions, manuscript-readiness checks, reviewer-amendment provenance, or the frozen validation records. If the need is procedural, factual, or learning-oriented rather than explanatory, use the [Documentation compass]({{ '/docs/documentation-map/' | relative_url }}).

## Choose by question

<div class="card-grid">
  <article class="card">
    <div class="card-icon" aria-hidden="true">1</div>
    <h3>Why treat gaze as uncertain?</h3>
    <p>Understand why measured gaze coordinates are not automatically known true points and why AOI boundaries can amplify spatial error.</p>
    <p><a href="measurement-uncertainty-is-a-modeling-problem/">Measurement uncertainty →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">2</div>
    <h3>Why audit more than one pipeline?</h3>
    <p>See how defensible analytical alternatives become a declared, inspectable specification space rather than a sequence of post-hoc choices.</p>
    <p><a href="from-one-pipeline-to-a-robustness-audit/">From one pipeline to an audit →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">3</div>
    <h3>What does fragility mean?</h3>
    <p>Learn why sensitivity is evidence about the scope of a conclusion rather than a software defect or a reason to search for a preferred branch.</p>
    <p><a href="how-to-read-a-fragile-result/">Read a fragile result →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">4</div>
    <h3>I already have outputs. What next?</h3>
    <p>Move from the complete execution record to bounded interpretation by checking denominator, endpoint, direction, magnitude, sensitivity, and untested uncertainty.</p>
    <p><a href="../guides/interpret-audit-result/">Interpret an audit result →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">5</div>
    <h3>Can a reviewer reconstruct the claim?</h3>
    <p>Check whether the manuscript, decision log, execution denominator, failures, limitations, archive manifest, and software identity tell one recoverable story.</p>
    <p><a href="../guides/manuscript-readiness/">Manuscript readiness →</a></p>
  </article>
  <article class="card">
    <div class="card-icon" aria-hidden="true">6</div>
    <h3>The reviewer asked for another analysis. Now what?</h3>
    <p>Extend the record transparently: keep the submitted audit recoverable, record outcome-inspection timing, and give post-review evidence its own denominator and provenance.</p>
    <p><a href="../guides/reviewer-requested-amendments/">Reviewer amendments →</a></p>
  </article>
</div>

## [Measurement uncertainty is a modelling problem](measurement-uncertainty-is-a-modeling-problem/)

Why a gaze coordinate should not automatically be treated as a known true point, why AOI boundaries magnify small spatial errors, and why Monte Carlo propagation is an assumption-aware representation rather than a claim of certainty.

**Continue with:** the [AOI uncertainty guide](../guides/aoi-uncertainty/) and [AOI boundary example](../examples/aoi-boundary/).

## [From one pipeline to a robustness audit](from-one-pipeline-to-a-robustness-audit/)

Why a single reasonable pipeline does not answer whether a conclusion depends on other reasonable pipelines, and how specification spaces turn analytical choice into an auditable object.

**Continue with:** the [specification-space guide](../guides/specification-space/) and [end-to-end robustness example](../examples/end-to-end-robustness/).

## [How to read a fragile result](how-to-read-a-fragile-result/)

Why fragility is not a software error, how to localise its source, and how to narrow scientific claims without turning robustness analysis into post-hoc optimisation.

**Continue with:** [Interpret an audit result](../guides/interpret-audit-result/) and the four synthetic [result-pattern reporting examples](../examples/result-patterns/).

## From concept to action

If you are no longer asking *why* robustness or uncertainty matters and instead need to decide what a completed result licenses you to say, use this practical sequence:

1. [Interpret an audit result](../guides/interpret-audit-result/) — verify completeness, endpoint consistency, direction, magnitude, sensitivity, and unresolved uncertainty.
2. [Result-pattern reporting example](../examples/result-patterns/) — compare complete/stable, magnitude-sensitive, sign-sensitive, and incomplete synthetic patterns.
3. [Reporting robustness](../guides/reporting-robustness/) — turn the bounded interpretation into precise Methods and Results language.
4. [Manuscript readiness](../guides/manuscript-readiness/) — test whether an independent reader can reconstruct endpoint, denominator, failures, decisions, wording, limitations, and software identity.
5. [Reviewer reconstruction](../examples/reviewer-reconstruction/) — practise finding an incomplete valid denominator and repairing an over-strong claim from outside the analysis team.
6. [Reviewer-requested amendments](../guides/reviewer-requested-amendments/) — preserve the submitted record when revision adds exclusions, thresholds, endpoints, measurement assumptions, or sensitivity analyses.
7. [Reviewer-requested reanalysis](../examples/reviewer-requested-reanalysis/) — practise keeping a synthetic submitted 8/8 audit separate from a post-review 4/4 amendment.
8. [Publication/archive handoff](../examples/publication-archive-handoff/) — preserve the decision trail, branch accountability, provenance, limitations, revision evidence, and manuscript record.

## Relationship to the validation records

The articles discuss general methodology. The canonical GazeBase, Korthals, and Pedrotti/de Chambrier outcomes remain defined by their frozen protocols and evidence. Use the [validation matrix](../VALIDATION_MATRIX.html) for those claims. Synthetic teaching patterns and general methodological articles do not create or modify case-study classifications. Reviewer reconstruction and reviewer-requested reanalysis exercises are also synthetic teaching material and do not create or modify case-study classifications.