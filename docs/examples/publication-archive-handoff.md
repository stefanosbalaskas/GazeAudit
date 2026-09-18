---
title: Publication and archive handoff example
description: Walk through an illustrative manuscript and archive handoff that connects a decision record, complete robustness evidence, scoped wording, provenance, and reproducibility metadata.
kicker: Example · Publication handoff
permalink: /docs/examples/publication-archive-handoff/
search_category: Example
search_keywords: publication archive handoff manuscript methods results robustness provenance fingerprints reviewer reproducibility example
page_type: example
example_data: "Synthetic"
example_focus: "Peer review & publication"
example_reuse: "Publication handoff pattern"
example_output: "Manuscript/archive evidence map and reproducibility handoff"
example_boundary: "Archive completeness does not by itself establish scientific validity."
---

# Publication and archive handoff example

This example shows what a **reviewable end state** can look like after a robustness audit. It continues the same deterministic synthetic exercise used in the [decision-to-report example]({{ '/docs/examples/decision-to-report/' | relative_url }}): 12 declared specifications, with four positive estimates, four negative estimates, and four exactly zero, ranging from approximately `-0.0404` to `+0.0210` with a median of `0.0000`.

<div class="callout warning">
<strong>Illustrative only.</strong>
All effect values and manuscript wording on this page are synthetic teaching material. This page is not validation evidence, does not classify a real dataset, and does not alter any frozen GazeAudit case-study outcome.
</div>

The objective is not to prescribe one filesystem. It is to demonstrate the information a coauthor, reviewer, editor, or future analyst should be able to recover from the publication handoff.

## Starting point

Assume the project has already preserved:

- a canonical source identity;
- a researcher decision log created before outcome inspection;
- one fixed scientific endpoint;
- a 12-branch declared specification space;
- complete branch-level results, including any execution status;
- robustness and sensitivity summaries;
- the exact GazeAudit release or commit used.

The synthetic pattern is intentionally mixed. It is therefore a useful test of whether the handoff reports the **complete evidence** rather than selecting one attractive branch.

## 1. Create a compact handoff root

One reasonable project-level structure is:

```text
publication-handoff/
  README.md
  decisions/
    audit-decision-log.md
  source/
    source-identity.md
    source-checksums.txt
  qc/
    study-qc/
  analysis/
    specifications.csv
    specification-curve.csv
    effect-stability.csv
    marginal-sensitivity.csv
    pairwise-sensitivity.csv
    execution-status.csv
  manuscript/
    methods-robustness.md
    results-robustness.md
    limitations.md
  provenance/
    software-identity.txt
    environment.txt
    fingerprints.txt
  manifest.md
```

This is an **illustrative archive layout**, not a required GazeAudit filesystem schema. Use the actual deterministic outputs produced by your workflow and record external source locks or checksums in the form appropriate to the study.

## 2. Make the top-level README answer five questions

A useful archive should be understandable before a reader opens individual CSV files.

```markdown
# Robustness audit handoff

Scientific endpoint:
  treatment-minus-control synthetic effect

Fixed across branches:
  endpoint definition, contrast direction, analysis population

Varied across branches:
  the predeclared demonstration factors in the 12-specification space

Execution:
  12/12 declared demonstration branches represented in the result set

Observed descriptive pattern:
  4 positive, 4 negative, 4 zero; range -0.0404 to +0.0210

Interpretation boundary:
  the pattern describes this synthetic specification set; it is not a
  confidence interval, posterior distribution, or causal decomposition.
```

For real research, replace every demonstration statement with the actual study definition and preserve the supporting artifact rather than relying on prose alone.

## 3. Keep the decision record beside the evidence

The archive should let a reviewer distinguish **pre-result choices** from **later amendments**.

A concise decision record might state:

```markdown
Decision ID: SPEC-01
Timing: before robustness-result inspection
Decision: retain all 12 predeclared valid specifications
Rationale: each combination was judged scientifically plausible in advance
Outcome-dependent change: none

Amendments: none
```

If an amendment occurred, retain the original entry and append the amendment. Do not rewrite the original record so that later knowledge disappears.

Use the [audit decision log template]({{ '/docs/guides/audit-decision-log-template/' | relative_url }}) for a fuller structure.

## 4. Preserve complete execution status

A publication handoff should make every declared branch accountable.

For this synthetic teaching case, all 12 demonstration specifications are represented. In a real audit, `execution-status.csv` can distinguish:

| Status | Meaning | Publication handling |
|---|---|---|
| `executed` | Valid declared branch completed | Preserve estimate and metadata |
| `invalid_predeclared` | Excluded by a rule fixed before execution | Preserve identity and rule |
| `technical_failure` | Valid branch failed computationally | Preserve identity and failure reason |
| `data_unavailable` | Required source content absent | Preserve identity and reason |
| `not_run` | Branch was not executed | Explain explicitly; do not silently omit |

The exact status vocabulary can be project-specific. The scientific requirement is that declared branches do not disappear without explanation.

## 5. Write Methods from the decision record, not from the preferred result

### Example bounded Methods wording

> We defined the scientific endpoint and 12 analytical specifications before inspecting the robustness outputs. The endpoint and contrast direction were held fixed across branches. All declared demonstration branches were retained in the specification-level evidence, and robustness summaries were calculated over the complete synthetic result table. Across-specification summaries were treated as descriptive sensitivity diagnostics rather than sampling-uncertainty intervals.

This wording establishes **timing, fixed elements, varied elements, completeness, and interpretation scope**. It does not claim that the demonstration specification space exhausts every possible analytical choice.

## 6. Write Results from the complete pattern

### Example bounded Results wording

> Across the 12 synthetic specifications, four estimates were positive, four were negative, and four were zero. Estimates ranged from approximately -0.0404 to +0.0210, with a median of 0.0000. The direction and magnitude therefore varied across the declared demonstration space. These values describe the executed synthetic specifications and should not be interpreted as a confidence interval, posterior distribution, or causal effect of any individual analytical choice.

### Wording to avoid

> The effect was robust because at least one specification was positive.

> The negative branches prove that one preprocessing choice caused the effect to reverse.

> The range from -0.0404 to +0.0210 is the 95% confidence interval.

Each statement gives the robustness exercise a meaning it does not establish.

## 7. Separate results from limitations

A compact `limitations.md` could record:

```markdown
- The audit covers the declared specification space, not every conceivable pipeline.
- Across-specification variation is descriptive and does not replace sampling uncertainty.
- The demonstration does not identify a causal mechanism for branch differences.
- Measurement dimensions not included in the declared space remain untested.
- This worked example uses synthetic values and is not empirical validation evidence.
```

In a real paper, replace generic items with study-specific untested uncertainty dimensions.

## 8. Bind software and provenance

A minimal `software-identity.txt` should record enough information to identify what executed the audit. For example:

```text
GazeAudit: exact release or Git commit used for the analysis
Python: exact interpreter version
Material interoperability packages: exact versions where scientifically relevant
Execution date/environment: recorded according to project policy
```

When a GazeAudit publication bundle is used, preserve its scientific and bundle fingerprints as described in the [publication audit guide]({{ '/docs/guides/publication-audits/' | relative_url }}). Do not invent fingerprints manually; archive the values produced by the actual executed bundle.

## 9. Add a human-readable manifest

The manifest is a map, not a substitute for the artifacts.

| Archive component | Question it answers | What it does not establish |
|---|---|---|
| `audit-decision-log.md` | What was decided, when, and why? | Whether the decision was scientifically correct |
| `source-identity.md` | Which source does this audit bind to? | Source validity by itself |
| `study-qc/` | What structural conditions and decisions were recorded? | Automatic scientific eligibility |
| `specifications.csv` | Which declared branches and estimates were represented? | Sampling uncertainty |
| robustness/sensitivity tables | How did the endpoint vary across declared choices? | Causal attribution to a choice |
| manuscript Markdown | What wording was handed into the paper? | Authority beyond the preserved evidence |
| software/provenance record | What execution identity produced the handoff? | Scientific validity by itself |
| fingerprints | Has bound content changed? | Whether the bound scientific design is appropriate |

## 10. Make reviewer handoff easy

A reviewer should not need to reverse-engineer the directory. The top-level README can point directly to:

1. **decision history** — what was fixed before result inspection;
2. **complete execution table** — what ran and what failed;
3. **robustness summaries** — what changed across the declared space;
4. **Methods/Results wording** — how the evidence entered the manuscript;
5. **provenance/fingerprints** — how the handoff is bound to software and content.

If those five links are clear, the archive is much easier to audit than a folder of unexplained outputs.

## 11. Final publication handoff checklist

Before depositing or submitting, verify that:

- [ ] source identity is stable enough for the claim;
- [ ] endpoint and contrast are explicit;
- [ ] original decisions and later amendments are distinguishable;
- [ ] every declared branch is accounted for;
- [ ] failed branches have not vanished;
- [ ] robustness summaries are described as the quantities they actually are;
- [ ] manuscript wording matches the preserved complete pattern;
- [ ] limitations name important untested dimensions;
- [ ] exact GazeAudit/software identity is recorded;
- [ ] generated fingerprints are preserved when publication-bundle tooling is used;
- [ ] the archive distinguishes illustrative/synthetic material from empirical validation evidence.

## Continue with the governed publication path

Use the [common audit mistakes guide]({{ '/docs/guides/common-audit-mistakes/' | relative_url }}) to diagnose a weak record, the [audit record map]({{ '/docs/guides/audit-record-map/' | relative_url }}) to trace artifact lineage, the [output-bundle guide]({{ '/docs/guides/audit-output-bundle/' | relative_url }}) to interpret generated evidence, and the [reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) for the formal end-to-end sequence.
