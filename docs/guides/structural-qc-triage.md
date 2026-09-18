---
title: Structural-QC triage
description: Inspect GazeAudit structural-QC flags, trace them to source and mapping provenance, record researcher-owned decisions, repair representations safely, rerun preflight, and report the evidence without treating flags as universal exclusions.
kicker: Guide · Structural QC
permalink: /docs/guides/structural-qc-triage/
search_category: Guide
search_keywords: structural qc triage issue code diagnostics decision repair rerun reporting limitation coordinate timestamp identifier duplicate decreasing review
---

# Structural-QC triage

Use this guide when structural preflight returns `status == "review"`.

The goal is not to make the warning disappear. The goal is to determine **what the observed condition means in the source representation, what the study team decided, and which evidence must be rebuilt if the representation changes**.

Start with the [Structural QC Issue Clinic]({{ '/docs/reference/qc-issue-clinic/' | relative_url }}) when you need to look up a specific issue or detail code.

## 1. Freeze the representation you are reviewing

Before changing rows, sorting, converting units, filling missing values, or redefining identifiers, bind the current representation.

At minimum record:

- source identity;
- participant/trial/timestamp/x/y mappings;
- coordinate and timestamp units;
- coordinate convention;
- transformations applied before the canonical table;
- exact software identity.

The [data-mapping provenance guide]({{ '/docs/guides/data-mapping-provenance/' | relative_url }}) provides a compact record for these fields.

A structural flag is meaningful only relative to the representation that produced it.

## 2. Run the summary and diagnostics together

```python
from gazeaudit import audit_study_qc, study_qc_diagnostics

report = audit_study_qc(study)
diagnostics = study_qc_diagnostics(study)

print(report.status)
print(report.issue_codes)
print(diagnostics)
```

The summary answers **which issue families were observed and how many rows/groups were affected**.

The diagnostic table answers **where the condition occurred and which detail code describes it**.

Do not infer row identities from counts alone.

## 3. Classify the condition before deciding

A useful triage distinction is:

| Classification | Question | Example |
|---|---|---|
| valid representation feature | Is the flag expected under the declared source structure? | simultaneous channel rows can share a timestamp |
| repairable representation problem | Can authoritative source information reconstruct the intended table? | concatenated trial blocks are out of order |
| study-specific analysis limitation | Is the condition real but unresolved for the intended endpoint? | timestamps are missing for some retained observations |
| scientific exclusion question | Does a predeclared or defensible study rule require excluding an affected unit? | a trial cannot support a time-based endpoint after source review |
| unknown | Is the cause still unresolved? | duplicate timestamps with no acquisition provenance |

“Unknown” is an acceptable interim classification. Guessing is not.

## 4. Trace every flag to source evidence

### Non-finite coordinates

Check:

- tracker validity/missingness flags;
- whether one or both eye channels were combined;
- coordinate transformations;
- off-screen conventions;
- source export encoding.

Do not silently interpolate or replace missing coordinates with zero.

### Non-finite timestamps

Check:

- raw timestamp field;
- event joins;
- timestamp unit/origin;
- failed conversions;
- row provenance.

Do not reinterpret a missing timestamp as trial onset.

### Missing identifiers

Check:

- merge keys;
- event segmentation;
- source trial labels;
- participant normalization;
- whether the row belongs outside the intended analysis unit.

Do not invent participant/trial IDs from neighbouring rows unless the reconstruction rule is independently justified and recorded.

### Duplicate timestamps

Check:

- binocular/multi-channel representation;
- acquisition precision;
- non-time columns under the same participant × trial × timestamp key;
- repeated exports;
- preprocessing duplication.

Do not deduplicate simply because timestamps are equal.

### Decreasing timestamps

Check:

- source row order;
- append/concatenation history;
- event segmentation;
- whether sorting would restore a documented source order.

Do not sort solely to make `timestamp_decreasing` disappear.

## 5. Record the decision

`StudyQCDecision` stores the researcher-owned action and rationale without prescribing the action.

```python
from gazeaudit import StudyQCDecision, build_study_qc_audit

decision = StudyQCDecision(
    issue_code="timestamp_duplicate",
    action="retain after representation review",
    rationale=(
        "The repeated timestamps correspond to simultaneous channel rows "
        "in the documented export representation."
    ),
    diagnostic_ids=("D000001", "D000002"),
)

audit = build_study_qc_audit(study, decisions=(decision,))
```

A good decision record states:

- what was observed;
- what source evidence was inspected;
- what action was taken;
- why that action follows from the study design or representation;
- which diagnostics the decision applies to;
- whether the representation changed.

Avoid generic rationales such as “bad data removed.”

## 6. If you repair the representation, create a new audit state

A repair may change:

- mapped values;
- row order;
- participant/trial grouping;
- timestamp unit;
- coordinate system;
- source version.

After any such change:

1. preserve the old mapping/QC record if it supported prior outputs;
2. update data-mapping provenance;
3. reconstruct `GazeStudy`;
4. rerun `audit_study_qc()`;
5. rerun `study_qc_diagnostics()`;
6. recreate the decision/audit record;
7. rerun downstream analyses affected by the changed representation.

Use `compare_qc_states()` when you need a provenance-bound before/after structural comparison.

A reduced issue count is descriptive. It does not prove that the repair was scientifically appropriate.

## 7. Keep structural QC separate from readiness policy

Structural preflight describes observed conditions.

Readiness governance evaluates researcher-declared thresholds.

```python
from gazeaudit import ReadinessThresholds, evaluate_analysis_readiness

thresholds = ReadinessThresholds(
    max_coordinate_issue_fraction=declared_coordinate_limit,
    require_monotonic_time=True,
)

readiness = evaluate_analysis_readiness(
    study,
    thresholds,
    policy_name="preregistered_primary",
    qc_audit=audit,
)
```

The threshold values above are placeholders. Replace them with values justified by your study.

Do not convert the mere presence of an issue code into a hidden readiness threshold.

## 8. Check endpoint dependence

A structural condition can matter differently for different endpoints.

Examples:

- a missing coordinate affects spatial/AOI endpoints directly;
- a missing timestamp may be critical for duration or sampling analyses;
- a missing trial identifier changes grouping semantics;
- duplicate timestamps can affect algorithms that assume one row per time point;
- decreasing timestamps can invalidate time-order-dependent processing.

Therefore, “retained after structural review” is not the end of the scientific reasoning. Document whether the downstream endpoint can validly consume the retained representation.

## 9. Preserve the denominator

When reporting structural QC, distinguish:

- total rows;
- total participant × trial units;
- affected rows;
- affected groups;
- issue families;
- diagnostic records;
- any subsequently excluded rows/trials/participants.

Do not describe “2 duplicate timestamp rows” as “2 duplicate trials.”

The [Issue Clinic]({{ '/docs/reference/qc-issue-clinic/' | relative_url }}) states the counting scope for every issue family.

## 10. Reporting examples

### Methods

A compact bounded statement:

> Structural preflight assessed non-finite coordinates and timestamps, missing participant/trial identifiers, duplicate participant × trial timestamps, and decreasing within-unit time. Row/group diagnostics were inspected against source and preprocessing provenance. Repairs, retention decisions, and exclusions were recorded explicitly; no structural flag was converted automatically into an exclusion.

### Results — no implemented issue observed

> Structural preflight returned `pass`; none of the implemented structural conditions was detected in the canonical representation. This status was treated as a structural check only and not as evidence of calibration, detector, AOI, missingness, or inferential validity.

### Results — review state

> Structural preflight returned `review` because [issue families] were observed across [row/group denominator]. The affected observations/units were inspected using diagnostic records, and [repair/retain/exclude/unresolved] decisions were preserved in the QC audit.

### Limitation

> Structural preflight evaluates a bounded set of representation-level conditions. It does not establish calibration accuracy, sampling adequacy, fixation/event validity, AOI validity, ignorable missingness, or inferential robustness.

Use the actual study record and denominator. Do not copy synthetic counts.

## 11. What not to report

Avoid wording such as:

- “GazeAudit confirmed the data were high quality.”
- “Rows flagged by QC were invalid.”
- “Duplicate timestamps were errors” without source evidence.
- “The dataset passed validation” when only structural preflight passed.
- “All missing values were removed” without the declared rule and denominator.
- “Sorting fixed the data” without documenting why the sorted order is authoritative.

## 12. When not to use structural QC as the decision layer

Structural preflight is not the right tool for deciding:

- calibration acceptance thresholds;
- event detector parameters;
- AOI geometry;
- pupil artifact handling;
- missingness mechanism assumptions;
- inferential model choice;
- specification-space membership.

Use the corresponding measurement, preprocessing, robustness, or study-protocol evidence instead.

## API links

- [`GazeStudy`]({{ '/docs/reference/api-pathways/#api-gazestudy' | relative_url }})
- [`audit_study_qc()`]({{ '/docs/reference/api-pathways/#api-audit-study-qc' | relative_url }})
- [`study_qc_diagnostics()`]({{ '/docs/reference/api-pathways/#api-study-qc-diagnostics' | relative_url }})
- [`build_study_qc_audit()`]({{ '/docs/reference/api-pathways/#api-build-study-qc-audit' | relative_url }})
- [Structural-QC method pathway]({{ '/docs/reference/api-pathways/#path-structural-qc' | relative_url }})
- [Analysis-readiness guide]({{ '/docs/guides/analysis-readiness/' | relative_url }})

## Worked exercise

Continue to [All structural-QC issues in one synthetic table]({{ '/docs/examples/all-structural-qc-issues/' | relative_url }}) to inspect all five issue families and all ten current detail codes in one deterministic fixture.
