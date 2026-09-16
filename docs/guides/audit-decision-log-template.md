---
title: Audit decision log template
description: A copy-ready Markdown template for recording source identity, endpoints, QC policy, exclusions, specification factors, perturbations, deviations, failure handling, software identity, and reporting boundaries.
kicker: Template · Research record
permalink: /docs/guides/audit-decision-log-template/
search_category: Template
search_keywords: decision log template audit plan protocol preregistration source endpoint exclusions qc specification factors perturbations deviations reporting reproducibility
---

# Audit decision log template

Copy this template into the study repository **before interpreting the main robustness outputs**. The purpose is to preserve researcher-owned decisions and later deviations in a form that can be reviewed alongside the generated audit bundle.

<div class="callout info">
<strong>A decision log is not a preregistration by itself.</strong>
It can support preregistration, protocol documentation, internal review, or manuscript provenance, but the authority of any formal preregistration depends on where and when it is registered.
</div>

## Copy-ready template

```markdown
# GazeAudit decision log

## Study identity

- Study/project:
- Analysis owner:
- Canonical source file or immutable source reference:
- Source version / checksum / retrieval identifier:
- Coordinate system and units:
- Sampling information relevant to this audit:
- Participant identifier:
- Trial identifier:
- Condition/group variables:

## Scientific endpoint

- Endpoint name:
- Plain-language definition:
- Code-level definition:
- Direction/contrast convention:
- Unit of the endpoint:
- Why this endpoint answers the study question:

## Structural-QC policy

| QC condition / issue code | Human review required? | Scientific action if triggered | Rationale |
|---|---|---|---|
| | | | |

Notes:
- Structural diagnostics are not automatic exclusions.
- Record any study-specific threshold and its justification explicitly.

## Exclusions

| Exclusion rule | Applied at which level? | Timing of declaration | Scientific rationale |
|---|---|---|---|
| | participant / trial / sample / other | before execution / amendment | |

## Declared specification space

| Factor | Allowed values / levels | Why these alternatives are defensible | Held fixed elsewhere? |
|---|---|---|---|
| | | | |

### Invalid combinations

| Combination | Why invalid / uninterpretable |
|---|---|
| | |

## Perturbation / sensitivity plan

| Uncertainty dimension | Reference condition | Perturbation grid / family | Recovery rule | Rationale |
|---|---|---|---|---|
| | | | | |

## Technical failure policy

- What counts as a technical failure:
- How failed branches remain visible:
- Whether retry/recovery is allowed:
- How recovered runs are identified:
- How incomplete families affect interpretation:

## Interpretation rule

Before inspecting the main robustness summaries, state:

- What would count as directionally stable:
- What would count as materially stable in magnitude:
- What would count as fragile:
- What would remain unresolved rather than labelled stable/fragile:
- Whether the analysis is descriptive only or paired with a separate inferential model:

## Software and execution identity

- GazeAudit release:
- Exact commit, if required:
- Python version:
- Environment / lockfile / container reference:
- Analysis script or notebook:
- Random seed(s), if applicable:

## Deviations and amendments

Record every change made after execution begins.

| Time/order | Original declaration | Amendment | Why the amendment was necessary | Results already inspected? | Effect on interpretation |
|---|---|---|---|---|---|
| | | | | yes / no | |

## Generated evidence

- Structural-QC record:
- Complete specification table:
- Specification curve:
- Effect-stability summary:
- Marginal sensitivity:
- Pairwise sensitivity:
- Perturbation/recovery outputs:
- Manifest / fingerprints:
- Figures used in reporting:

## Reporting boundary

### Supported by this audit

- 

### Not established by this audit

- 

### Uncertainty dimensions not tested

- 

## Publication/archive handoff

- Methods text checked against the decision log: yes / no
- Results text checked against complete outputs: yes / no
- Failed/incomplete branches disclosed where relevant: yes / no
- Exact software identity recorded: yes / no
- Complete audit bundle archived: yes / no
- Source/provenance record archived: yes / no
```

## How to use it

### Before execution

Fill in study identity, endpoint, QC policy, exclusions, specification factors, invalid combinations, perturbations, failure handling, and the intended interpretation rule.

### During execution

Append deviations instead of rewriting the original declaration. The distinction between **what was planned** and **what changed** is part of the research record.

### Before reporting

Complete the reporting boundary using the generated evidence. Separate what the audit supports from what remains outside scope.

### Before archiving

Check that the decision log, output bundle, exact software identity, source/provenance record, and manuscript wording agree.

## What not to put in the log

Do not use the decision log to retroactively make a result-driven choice look predeclared. If a decision changed after estimates were visible, record that timing explicitly.

## Related pages

- [Researcher audit checklist]({{ '/docs/guides/researcher-audit-checklist/' | relative_url }}) — before/during/after governance checks.
- [Audit record map]({{ '/docs/guides/audit-record-map/' | relative_url }}) — how the decision record connects to QC, robustness evidence, provenance, and publication claims.
- [Decision-to-report example]({{ '/docs/examples/decision-to-report/' | relative_url }}) — worked synthetic example of bounded interpretation.
- [Reproducible publication]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) — archive-level workflow.
