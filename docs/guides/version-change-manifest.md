---
title: Version-change manifest guide
description: Build a reconstructable submitted-to-revised manuscript manifest that separates editorial edits, clarifications, corrections, and post-review analytical amendments without rewriting study history.
kicker: Guide · Revision provenance
permalink: /docs/guides/version-change-manifest/
search_category: Guides
search_keywords: version change manifest revision manuscript diff reviewer response correction amendment provenance archive editor resubmission
---

# Version-change manifest guide

A tracked-changes manuscript shows **where text changed**. A version-change manifest explains **why a material change occurred, when its supporting evidence entered the study, what files changed, and whether the scientific claim changed**.

Use this guide for the transition from a submitted manuscript to a revised or final version. The manifest complements the reviewer response letter; it does not replace it.

<div class="callout info">
<strong>The manifest is a provenance layer.</strong>
It should make the revision reconstructable without implying that every textual edit is scientifically important or that every reviewer request required new analysis.
</div>

## Use stable change categories

Classify each material change as one of the following:

| Category | Meaning | Typical evidence impact |
|---|---|---|
| `editorial_text` | wording, grammar, organization, or presentation only | none |
| `documentation_clarification` | existing method/result made more explicit | no new analysis |
| `correction` | defect found in data, code, import, analysis, or reporting | affected evidence regenerated; superseded record preserved |
| `sensitivity_amendment` | reviewer-requested or author-added robustness/sensitivity branch | new post-review evidence |
| `analytical_amendment` | new defensible analysis under the same broad research question | new post-review evidence |
| `endpoint_amendment` | a different scientific endpoint is added | separate endpoint record |
| `measurement_amendment` | measurement, AOI, detector, uncertainty, or preprocessing assumption is added or changed | new post-review evidence |
| `reporting_boundary` | claim narrowed, limitation added, or unsupported interpretation removed | claim scope changes without necessarily changing data |

Do not use a generic label such as `major_change` when a more specific provenance category is available.

## Required fields

Each material change should contain at least:

1. `change_id` — stable identifier such as `R1-C4-A1`;
2. `source` — reviewer item, editor request, coauthor request, or author-initiated reason;
3. `category` — one of the stable categories above;
4. `results_already_seen` — `yes`, `no`, or `not_applicable`;
5. `submitted_location` — manuscript v1 location;
6. `revised_location` — manuscript v2/final location;
7. `action` — concise description of what changed;
8. `evidence_added_or_regenerated` — files or evidence layer affected;
9. `denominator_effect` — unchanged, separately added, corrected/recomputed, or different endpoint;
10. `claim_impact` — none, clarification, narrowed, expanded with new evidence, corrected, or endpoint-specific;
11. `archive_location` — where the supporting revision record lives;
12. `status` — complete, unresolved, or not applicable.

## Copy-ready YAML template

```yaml
change_id: R1-C4-A1
source: "Reviewer 1, comment 4"
category: sensitivity_amendment
results_already_seen: yes
submitted_location: "Results, paragraph 3"
revised_location: "Results, paragraph 4; Supplementary Table S5"
action: "Added the stricter quality-threshold sensitivity requested during review."
evidence_added_or_regenerated:
  - revision/round-1/amendments/R1-C4/specifications.csv
  - revision/round-1/amendments/R1-C4/effect-stability.csv
denominator_effect: "4 / 4 post-review branches added separately"
claim_impact: "expanded with new post-review evidence; submitted 8 / 8 denominator retained"
archive_location: revision/round-1/amendments/R1-C4/
status: complete
```

The field `results_already_seen: yes` is not an admission of error. It records the temporal fact that the amendment was chosen after the submitted outcomes existed.

## Recommended tabular manifest

A CSV or Markdown table can provide a compact editor-facing view:

| Change ID | Source | Category | Timing | v1 location | v2 location | Evidence | Denominator effect | Claim impact | Status |
|---|---|---|---|---|---|---|---|---|---|
| R1-C2-D1 | Reviewer 1 comment 2 | documentation clarification | N/A | Methods ¶2 | Methods ¶2 | none | unchanged | clarification | complete |
| R1-C4-A1 | Reviewer 1 comment 4 | sensitivity amendment | outcomes seen | Results ¶3 | Results ¶4 + Table S5 | 4 added branches | separate 4/4 amendment | expanded with post-review evidence | complete |
| R1-C6-E1 | Reviewer 1 comment 6 | endpoint amendment | outcomes seen | not present | Supplement §S7 | new endpoint analysis | outside original denominator | endpoint-specific | complete |

The table should remain useful even when the reviewer response letter is read separately.

## Corrections require a supersession trail

A correction is different from an ordinary amendment because previously reported evidence becomes materially wrong or incomplete.

For corrections, add:

```yaml
supersedes:
  manuscript_version: v1
  evidence_path: submission/submitted-analysis/specifications.csv
correction_reason: "describe the defect"
materially_affected_claims:
  - "identify affected claim"
regenerated_record:
  evidence_path: revision/round-1/corrections/C1/specifications.csv
```

Keep the superseded record available. The final archive should show what changed rather than presenting the corrected result as though it had always been the submitted result.

## Endpoint changes stay endpoint-specific

If review requests a different endpoint, record the new endpoint separately. Do not silently combine its branches with the original endpoint's robustness denominator.

A useful manifest statement is:

> Added endpoint E2 during review in response to R1-C6. E2 is archived and reported separately from the submitted E1 robustness denominator.

This keeps temporal and scientific denominators interpretable.

## Text-only edits do not need false analytical provenance

Do not manufacture analysis metadata for grammar, formatting, citation, or organizational changes. For a purely editorial revision:

```yaml
change_id: R1-C1-T1
category: editorial_text
results_already_seen: not_applicable
evidence_added_or_regenerated: []
denominator_effect: unchanged
claim_impact: none
status: complete
```

The purpose of the manifest is clarity, not bureaucratic inflation.

## Suggested archive layout

```text
revision/round-1/
  reviewer-response/
    response-matrix.csv
  change-manifest/
    version-change-manifest.csv
    version-change-manifest.yaml
  amendments/
    R1-C4/
  endpoint-amendments/
    R1-C6/
  corrections/
  manuscript/
    manuscript-v2.pdf
    tracked-changes-v1-to-v2.pdf
```

This layout is illustrative rather than required.

## Manifest consistency checks

Before final handoff, verify:

- every analytical reviewer item appears in both the response matrix and version-change manifest;
- every manifest entry points to a real revised manuscript location;
- every added or regenerated evidence file exists in the revision archive;
- submitted and post-review denominators remain distinguishable;
- corrections identify the superseded record;
- endpoint amendments remain outside the original endpoint denominator;
- unresolved items are not marked complete;
- the final manuscript does not contain material changes missing from the manifest.

## What not to do

Do not:

- reconstruct the manifest from memory only after acceptance;
- relabel post-review analyses as pre-specified;
- delete superseded evidence after a correction;
- merge different endpoints into one denominator;
- treat tracked changes as a substitute for evidence provenance;
- imply that a journal decision validates the scientific conclusion.

Use the [resubmission readiness guide]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) for the final consistency gate, then compare your record with the [submission-to-accepted-record worked example]({{ '/docs/examples/submission-to-accepted-record/' | relative_url }}).
