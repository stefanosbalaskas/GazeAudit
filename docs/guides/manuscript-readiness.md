---
title: Manuscript readiness checklist
description: Verify that a GazeAudit robustness claim can be reconstructed from the declared analysis, complete execution record, interpretation boundary, and archived evidence before manuscript submission.
kicker: Guide · Reporting
permalink: /docs/guides/manuscript-readiness/
search_category: Guide
search_keywords: manuscript readiness reviewer checklist methods results robustness archive reporting reconstruction evidence denominator endpoint limitations
---

# Manuscript readiness checklist

Use this checklist **after the audit has been interpreted but before the manuscript claim is treated as submission-ready**. It is designed to answer one practical question:

> Could a coauthor, reviewer, editor, or future analyst reconstruct exactly what was declared, what ran, what changed, and why the manuscript wording is no stronger than the evidence?

<div class="callout info">
<strong>Readiness is not an automatic validity decision.</strong>
GazeAudit can help expose missing records, incomplete branch accounting, provenance gaps, and reporting overreach. Researchers remain responsible for the scientific justification of the endpoint, alternatives, exclusions, uncertainty model, and final claim.
</div>

## The six manuscript-readiness gates

### 1. The scientific endpoint is reconstructable

A reviewer should be able to recover:

- the exact endpoint definition;
- its units and direction;
- the population/unit of analysis represented by each estimate;
- what remained fixed across specifications;
- any endpoint amendment and when it occurred.

**Not ready:** the manuscript reports one outcome label while different branches estimate materially different quantities.

**Repair:** bind the endpoint definition to the decision log and specification table, then separate genuinely different endpoints into different audits.

### 2. The execution denominator is explicit

Report the number of:

- declared combinations;
- invalid combinations excluded by rule;
- valid combinations expected to execute;
- successful valid branches;
- technically failed valid branches;
- unresolved branches.

A manuscript should never make a complete-space claim from an unknown or selectively reduced denominator.

**Minimum sentence structure:**

> The declared space contained **N** combinations; **I** were invalid by pre-specified rule, leaving **V** valid branches. **S** completed successfully and **F** valid branches failed technically.

Do not replace those quantities with “multiple specifications were tested.”

### 3. Researcher-owned decisions are distinguishable from diagnostics

The record should separate:

- structural-QC findings from scientific exclusions;
- software warnings from researcher decisions;
- observed missingness from chosen repair/interpolation policy;
- descriptive sensitivity summaries from causal explanations;
- demonstration defaults from study-specific thresholds.

If a threshold, exclusion, interpolation rule, AOI geometry, perturbation level, or conclusion rule changed after outcome inspection, preserve the amendment rather than rewriting the earlier record.

### 4. The Results wording matches the complete pattern

Before final prose, verify separately:

- **direction:** did estimates keep or change sign?
- **magnitude:** did effect size vary enough to alter substantive interpretation?
- **completeness:** are all declared valid branches accounted for?
- **sensitivity alignment:** which declared factors align descriptively with variation?
- **untested uncertainty:** which plausible dimensions were not included?

Use the [result interpretation guide](interpret-audit-result/) and [result-pattern example](../examples/result-patterns/) before reducing these dimensions to one label.

### 5. The manuscript and archive tell the same story

The manuscript, decision log, output bundle, and archive manifest should agree on:

| Record | Must agree on |
|---|---|
| Methods | endpoint, specification factors, exclusions, perturbations, software identity |
| Results | execution denominator, failures, complete observed pattern |
| Limitations | unresolved failures and untested uncertainty dimensions |
| Decision log | original choices, amendments, timing relative to result inspection |
| Archive manifest | exact files, source identity, software/provenance records, fingerprints |

A polished manuscript is not ready if the archive reconstructs a materially different analysis.

### 6. The claim survives a reviewer reconstruction test

Give the archive to someone who was not involved in the analysis and ask them to answer these questions without private context:

1. What was the declared scientific endpoint?
2. What was the complete valid specification denominator?
3. Which branches failed, and why?
4. Which decisions were researcher-owned?
5. Did direction and magnitude tell the same stability story?
6. Which uncertainty dimensions were tested, and which were not?
7. Which exact software release or commit generated the evidence?
8. Which files support the main manuscript claim?

If those answers require oral explanation, private notes, or inference from file names, improve the archive before submission.

## Claim-strength check

Use the weakest evidence boundary that is accurate.

| Evidence pattern | Bounded wording direction |
|---|---|
| Complete execution; direction and magnitude comparatively stable | Describe stability **within the declared space** and state what was varied. |
| Complete execution; direction stable, magnitude sensitive | Report directional consistency while explicitly describing material magnitude variation. |
| Complete execution; sign changes | Report sign sensitivity across the declared alternatives rather than selecting a preferred branch. |
| Incomplete valid execution | Report the audit as incomplete for the unresolved denominator; do not promote the successful subset to a complete-space conclusion. |

These are reporting patterns, not automatic classification rules.

## Submission packet

A compact reviewer-ready handoff should normally contain:

```text
manuscript-readiness/
  README.md
  decision-log.md
  endpoint-definition.md
  execution-status.csv
  specifications.csv
  robustness-summary.csv
  sensitivity-summary.csv
  methods.md
  results.md
  limitations.md
  source-provenance.json
  software-versions.txt
  manifest.json
  fingerprints.txt
```

The exact filenames are illustrative. The important requirement is that the evidence chain is explicit and internally consistent.

## Final pre-submission questions

- Can every number in the robustness claim be traced to a preserved output?
- Can every exclusion or invalid combination be traced to a rule or amendment?
- Can every failed valid branch be found in the execution record?
- Does the Results wording describe the complete pattern rather than a selected branch?
- Are descriptive sensitivity summaries clearly distinguished from causal or probabilistic claims?
- Are limitations explicit about unresolved failures and untested uncertainty?
- Is the exact software identity recoverable?
- Can the archive be understood without private lab knowledge?

If any answer is **no**, the manuscript record is not yet ready for handoff.

## Continue with

- [Manuscript review path](../workspace/manuscript-review-path/) — use one compact Workspace route from interpretation through archive verification.
- [Reviewer reconstruction worked example](../examples/reviewer-reconstruction/) — practise the checklist on an illustrative archive.
- [Publication/archive handoff](../examples/publication-archive-handoff/) — see the broader archive structure.
- [Reproducible publication workflow](../workflows/reproducible-publication/) — build and verify the durable publication record.
- [Common audit mistakes](common-audit-mistakes/) — repair decision-trail and execution-accounting problems before submission.
