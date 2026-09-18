---
title: Project lifecycle walkthrough
description: A fully synthetic five-stage GazeAudit walkthrough from planning and audit execution through interpretation, peer-review amendment, and final handoff.
kicker: Example
page_type: example
permalink: /docs/examples/project-lifecycle-walkthrough/
search_category: Example
search_keywords: project lifecycle walkthrough what next onboarding plan audit interpret peer review revision amendment resubmission handoff synthetic example
example_data: "Synthetic"
example_focus: "Project lifecycle"
example_reuse: "Project-stage workflow"
example_output: "Five-stage project record from planning through final handoff"
example_boundary: "Synthetic project decisions are teaching choices, not a protocol."
---

# Project lifecycle walkthrough

This worked example follows one **fully synthetic teaching project** through the five project stages used by the GazeAudit homepage and the [What should I do next?]({{ '/docs/guides/what-next/' | relative_url }}) guide.

Nothing below is empirical validation evidence. The numbers, reviewer comments, endpoint values, branch counts, manuscript text, and file names are teaching material designed to show how the **research record changes over time**.

<div class="callout warning">
<strong>Do not transfer these choices into a real study.</strong>
The QC policies, specification factors, thresholds, endpoint, reviewer amendment, and reporting language below are illustrative. A real project needs study-specific scientific justification.
</div>

## Synthetic project

A fictional experiment measures attention to a claim region and a comparison region in a set of visual stimuli.

The synthetic endpoint is:

> participant-level difference in dwell time between the claim AOI and comparison AOI, in milliseconds.

For teaching purposes, the team declares three binary analytical factors before inspecting the endpoint:

| Factor | Level 1 | Level 2 |
|---|---|---|
| gaze assignment | hard AOI membership | uncertainty-aware AOI membership |
| trial summary | arithmetic mean | trimmed mean |
| minimum-valid-sample policy | policy A | policy B |

The cross-product contains **8 valid submitted specifications**.

The example deliberately keeps the endpoint fixed across those eight branches. A later peer-review request will add post-review work without pretending that it was part of this original declaration.

## Stage 1 — plan the record

Before running the endpoint analysis, the fictional team writes a compact decision record.

```text
project_id: synthetic_claim_attention
canonical_source: data/canonical_gaze.csv
endpoint_id: E1_claim_minus_comparison_dwell_ms
unit_of_analysis: participant
submitted_specifications: 8
outcomes_inspected: false
```

The team also records the three factors above, the planned structural preflight, and the intended output directory.

### What this stage establishes

The record shows what the team intended to vary and what it intended to hold fixed **before the teaching endpoint was inspected**.

### What it does not establish

It does not prove that the endpoint is scientifically important, that the factor levels are appropriate for another dataset, or that eight specifications are sufficient for any general robustness claim.

### Where the site sends the researcher

- [Audit planner]({{ '/docs/planner/' | relative_url }})
- [Project starter]({{ '/docs/guides/project-starter/' | relative_url }})
- [Researcher audit checklist]({{ '/docs/guides/researcher-audit-checklist/' | relative_url }})

## Stage 2 — audit the canonical data

The canonical table is mapped explicitly into a `GazeStudy`-style record and receives structural preflight before downstream execution.

The synthetic preflight finds no unresolved source-shape condition that blocks the teaching analysis. The team then executes all eight declared valid specifications.

Synthetic execution record:

| specification | assignment | summary | sample policy | status | estimate_ms |
|---|---|---|---|---|---:|
| S01 | hard | mean | A | success | -31 |
| S02 | hard | mean | B | success | -27 |
| S03 | hard | trimmed | A | success | -24 |
| S04 | hard | trimmed | B | success | -20 |
| S05 | uncertainty-aware | mean | A | success | -22 |
| S06 | uncertainty-aware | mean | B | success | -18 |
| S07 | uncertainty-aware | trimmed | A | success | -16 |
| S08 | uncertainty-aware | trimmed | B | success | -13 |

Submitted execution denominator:

```text
E1 submitted: 8 successful / 8 valid
```

### Preserve the complete table

The evidence bundle keeps all eight rows. It does not retain only the branch with the smallest p-value, largest magnitude, or most convenient narrative.

### Where the site sends the researcher

- [First real audit]({{ '/docs/guides/first-real-audit/' | relative_url }})
- [Data onboarding]({{ '/docs/guides/data-onboarding/' | relative_url }})
- [Audit output bundle]({{ '/docs/guides/audit-output-bundle/' | relative_url }})

## Stage 3 — interpret the complete pattern

All eight synthetic estimates are negative, but their magnitude varies from `-31 ms` to `-13 ms`.

A bounded teaching interpretation is therefore:

> Across the eight declared and successfully executed synthetic specifications, the endpoint remained negative, while its estimated magnitude varied across analytical choices.

The record does **not** turn `8 / 8` negative estimates into a posterior probability, confidence interval, causal mechanism, or universal robustness score.

### Interpretation worksheet

| Question | Synthetic record |
|---|---|
| Was the valid execution denominator complete? | yes, 8 / 8 |
| Was the endpoint held fixed? | yes, E1 |
| Did direction change? | no in this teaching example |
| Did magnitude change? | yes, -31 to -13 ms |
| Are factor-sensitivity summaries causal? | no |
| Are important uncertainty dimensions still untested? | potentially; the exercise varies only three declared factors |

### Draft manuscript wording

```text
Across eight predeclared synthetic specifications, the E1 estimate remained
negative. Magnitude varied across the declared analytical choices, so the
result is described as directionally stable within this specification set
rather than invariant to analysis decisions.
```

### Where the site sends the researcher

- [Interpret an audit result]({{ '/docs/guides/interpret-audit-result/' | relative_url }})
- [Result-pattern reporting]({{ '/docs/examples/result-patterns/' | relative_url }})
- [Reporting robustness]({{ '/docs/guides/reporting-robustness/' | relative_url }})
- [Manuscript readiness]({{ '/docs/guides/manuscript-readiness/' | relative_url }})

## Stage 4 — peer review adds new work

A fictional reviewer asks:

> Please repeat the E1 analysis using a stricter trial-readiness policy and show whether the conclusion changes.

This request arrives **after the submitted endpoint has been inspected**. The team therefore does not edit the original eight-specification declaration.

It classifies the request as a post-review sensitivity amendment and declares four valid amendment branches before executing them.

```text
reviewer_item: R2.3
category: sensitivity_amendment
endpoint: E1_claim_minus_comparison_dwell_ms
results_already_seen: true
post_review_valid_branches: 4
```

### Amendment execution

Three amendment branches succeed. One valid branch fails because its estimator does not return a finite result under the stricter synthetic readiness policy.

| amendment branch | status | estimate_ms |
|---|---|---:|
| A01 | success | -19 |
| A02 | success | -14 |
| A03 | success | -11 |
| A04 | technical failure | — |

The record is:

```text
E1 submitted: 8 / 8
E1 post-review sensitivity amendment: 3 successful / 4 valid
```

It is **not**:

```text
11 / 11 analyses
```

and it is not:

```text
3 / 3 post-review analyses
```

The valid technical failure stays in the post-review denominator.

### Response-letter unit

```text
Reviewer item R2.3 was addressed with a post-review sensitivity amendment.
The submitted E1 record remains 8/8. Four additional branches were declared
for the stricter readiness policy after review; three executed successfully
and one valid branch remained technically unresolved. The revised manuscript
reports the amendment as 3 successful / 4 valid and does not relabel it as
part of the submitted specification set.
```

### A second reviewer request changes the endpoint

A fictional second request asks for a different endpoint, E2. The team records E2 separately rather than adding it to the E1 denominator.

```text
E2 post-review endpoint amendment: separate endpoint record
```

This preserves the distinction between **new branches of the same endpoint** and **a different scientific endpoint**.

### Where the site sends the researcher

- [Revision route map]({{ '/docs/guides/revision-route-map/' | relative_url }})
- [Peer-review revision checklist]({{ '/docs/guides/peer-review-revision-checklist/' | relative_url }})
- [Revision toolkit]({{ '/docs/workspace/revision-toolkit/' | relative_url }})
- [Revision-round scenarios]({{ '/docs/examples/revision-round-scenarios/' | relative_url }})
- [Revision-package quickstart]({{ '/docs/examples/revision-package-quickstart/' | relative_url }})

## Build the structural revision package

For this teaching round, the real package CLI can scaffold the revision-provenance directories:

```bash
gazeaudit-revision-package init --root revision-package
gazeaudit-revision-package validate --root revision-package
```

The validation establishes **structural provenance only**. It does not decide whether the fictional reviewer request is scientifically justified or whether the synthetic manuscript conclusion is valid.

A compact teaching archive might contain:

```text
revision-package/
├── reviewer-response/
│   └── response-matrix.csv
├── changes/
│   └── version-change-manifest.csv
├── amendments/
│   └── R2.3-e1-readiness-sensitivity/
├── endpoint-amendments/
│   └── E2/
├── software/
│   └── software-identity.json
└── evidence-map/
    └── editor-evidence-map.csv
```

## Stage 5 — resubmission and final handoff

Before handoff, the fictional team reconstructs the record from the outside.

### Temporal evidence summary

| Layer | Endpoint | Denominator | Timing |
|---|---|---:|---|
| submitted evidence | E1 | 8 / 8 | before peer review |
| sensitivity amendment | E1 | 3 successful / 4 valid | after reviewer request R2.3 |
| endpoint amendment | E2 | separate record | after peer review |

### Final consistency checks

The team verifies that:

- R2.3 is linked to its response, amendment folder, revised Results location, and limitation text;
- the unresolved A04 failure remains visible;
- E2 is not merged into the E1 branch denominator;
- the version-change manifest explains every material v1 → v2 change;
- the software identity matches the execution record;
- the editor-facing evidence map points to the same temporal layers described in the response letter;
- final manuscript wording does not call post-review work pre-specified.

### Where the site sends the researcher

- [Resubmission readiness]({{ '/docs/guides/resubmission-readiness/' | relative_url }})
- [Version-change manifest]({{ '/docs/guides/version-change-manifest/' | relative_url }})
- [Submission-to-accepted-record]({{ '/docs/examples/submission-to-accepted-record/' | relative_url }})
- [Publication/archive handoff]({{ '/docs/examples/publication-archive-handoff/' | relative_url }})
- [Reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }})

## What changed across the five stages?

| Stage | Primary record | Key denominator question |
|---|---|---|
| Plan | declared route | what was intended before outcome inspection? |
| Audit | execution evidence | how many branches were valid and how many succeeded? |
| Interpret | bounded claim | what does the complete pattern support without over-reading it? |
| Peer review | temporal amendment record | what is submitted evidence versus post-review evidence? |
| Handoff | reconciled archive | can an outsider trace each final claim through the correct evidence layer? |

The point of the lifecycle is not to accumulate more files. It is to preserve **which decision existed when, which endpoint each analysis belongs to, which denominator is valid, and which manuscript claim each evidence layer supports**.

## Frozen validation outcomes are not part of this example

This walkthrough does not alter or reuse the scientific labels of the frozen real-data programme. Those remain:

- GazeBase `incomplete`;
- Korthals `robust_negative`;
- Pedrotti/de Chambrier `materially_fragile`.

Those outcomes are protocol-bound records. The synthetic lifecycle above receives **no GazeAudit case-study label**.

## Continue

Return to [What should I do next?]({{ '/docs/guides/what-next/' | relative_url }}) and choose the stage that matches the real project. Replace every teaching choice here with a study-specific, provenance-preserved decision.