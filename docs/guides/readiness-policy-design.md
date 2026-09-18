---
title: Design and audit readiness policies
description: Methodological guidance for declaring GazeAudit structural-readiness thresholds, separating trial and participant consequences, previewing cohort impact, comparing defensible alternatives, preserving timing and denominator provenance, and reporting policy-relative readiness without turning it into a universal quality score.
kicker: Guide · Readiness governance
permalink: /docs/guides/readiness-policy-design/
search_category: Guide
search_keywords: readiness policy thresholds rationale preregistration trial participant cohort impact sensitivity policy fingerprint reporting limitations ReadinessThresholds
---

# Design and audit readiness policies

Use this guide when structural QC has already been understood and you now need a **declared rule for deciding whether trial or participant units satisfy the structural requirements of a particular analysis**.

The core principle is:

> A readiness policy is a study-owned decision layer applied to observed structural metrics. It is not a package-owned definition of good eye-tracking data.

Start with the [Readiness Policy Design Center]({{ '/docs/readiness-policy/' | relative_url }}) when you want to assemble the policy interactively without hidden threshold values.

## 1. Separate observation from decision

Structural QC reports what was observed:

- non-finite coordinate fractions;
- non-finite timestamp fractions;
- missing-identifier fractions;
- duplicate-timestamp fractions;
- decreasing within-trial time;
- row/trial counts.

`ReadinessThresholds` records what the study team decides those metrics must satisfy for a declared analysis.

Do not turn an issue code directly into an exclusion.

A defensible sequence is:

1. inspect the structural condition;
2. establish its source/representation meaning;
3. decide whether the intended endpoint requires a readiness rule;
4. justify the threshold independently of the desired outcome;
5. preview the cohort consequence;
6. only then consider applying the policy.

## 2. Give every active threshold a rationale source

A readiness value should point to something outside the observed substantive result.

Possible rationale sources include:

- preregistration or registered protocol;
- acquisition protocol;
- task design;
- device or laboratory validation;
- endpoint-specific minimum information requirements;
- external methodological evidence;
- a deliberately declared sensitivity range;
- a documented revision request, labelled as post-review rather than predeclared.

Record the source beside the threshold.

Avoid rationales such as:

- “this kept enough participants”;
- “this produced the expected direction”;
- “this is the package default”;
- “this looked strict”;
- “this matched the example.”

GazeAudit deliberately supplies no scientific defaults.

## 3. Understand which unit each rule evaluates

The eight `ReadinessThresholds` fields do not all operate at the same level.

| Rule | Trial evaluation | Participant evaluation | Important consequence |
|---|---:|---:|---|
| `max_coordinate_issue_fraction` | yes | yes | same named metric is calculated within both scopes |
| `max_timestamp_issue_fraction` | yes | yes | same named metric is calculated within both scopes |
| `max_identifier_issue_fraction` | yes | yes | participant/trial identifier problems can affect grouping semantics |
| `max_duplicate_timestamp_fraction` | yes | yes | equality of timestamps still requires source interpretation |
| `max_flagged_trial_fraction` | no | yes | depends on which trials fail the active trial rules |
| `min_rows_per_trial` | yes | no | row count is not equivalent to duration across sampling schemes |
| `min_trials_per_participant` | no | yes | must be tied to design/endpoint requirements |
| `require_monotonic_time=True` | yes | yes | participant fails when at least one trial has decreasing finite time |

The [machine-readable threshold reference]({{ '/assets/readiness-threshold-reference.json' | relative_url }}) exposes the same governed catalog.

## 4. Treat `max_flagged_trial_fraction` as a second-order rule

This criterion is easy to misread.

A trial is first evaluated against the active trial-level rules. The participant summary then calculates:

```text
flagged_trial_fraction =
    participant trial units failing active trial rules
    ------------------------------------------------
                 participant trial units
```

Changing a trial threshold can therefore change `flagged_trial_fraction` even when the source data do not change.

When reporting this rule, state which trial-level policy generated the flagged-trial denominator.

## 5. Declare timing

For every policy, record when it was fixed relative to:

- outcome inspection;
- primary-model fitting;
- robustness analysis;
- reviewer requests;
- manuscript submission.

Useful labels include:

- preregistered;
- protocol-specified before analysis;
- analyst-declared before outcome inspection;
- post hoc sensitivity policy;
- reviewer-requested amendment.

Do not relabel a later sensitivity threshold as though it had been the original primary policy.

## 6. Preview cohort impact before filtering

`evaluate_analysis_readiness()` does not mutate the study.

```python
from gazeaudit import evaluate_analysis_readiness

readiness = evaluate_analysis_readiness(
    study,
    policy,
    policy_name="preregistered_primary",
)

print(readiness.trial_summary)
print(readiness.participant_summary)
print(readiness.cohort_impact)
```

Before applying anything, inspect:

- baseline rows;
- retained/excluded rows;
- baseline trial units;
- retained/excluded trial units;
- baseline participant units;
- retained/excluded participant units;
- retained fractions at each denominator.

The same policy can have different consequences under trial versus participant filtering.

## 7. Keep filter scope as a separate decision

A policy can be evaluated at both trial and participant level, but application scope is explicit:

```python
from gazeaudit import filter_study_by_readiness

trial_filtered = filter_study_by_readiness(
    study,
    readiness,
    scope="trial",
)

participant_filtered = filter_study_by_readiness(
    study,
    readiness,
    scope="participant",
)
```

These are not interchangeable.

Trial filtering can retain other trials from a participant whose one unit failed.

Participant filtering removes all rows/trials belonging to a participant who fails the participant-level policy.

Record the scope in the decision log and manuscript.

## 8. Compare nearby defensible alternatives without choosing the winner after outcomes

When more than one policy can be justified, compare them explicitly:

```python
from gazeaudit import readiness_policy_table

comparison = readiness_policy_table(
    study,
    {
        "primary": primary_policy,
        "alternative_a": alternative_a,
        "alternative_b": alternative_b,
    },
)
```

The comparison exposes:

- policy name;
- deterministic policy fingerprint;
- status;
- active-rule set;
- retained row/trial/participant fractions at trial scope;
- retained row/trial/participant fractions at participant scope.

Use this as a sensitivity/governance record, not as a search for the policy that yields the most desirable endpoint.

## 9. If readiness itself is uncertain, put it in the specification space

When multiple policies are scientifically defensible and materially affect the cohort, readiness can be a declared multiverse factor:

```python
from gazeaudit import PipelineSpace, readiness_pipeline_processor, run_specs

policies = {
    "primary": primary_policy,
    "alternative": alternative_policy,
}

space = PipelineSpace().add_choice("readiness_policy", policies)
processor = readiness_pipeline_processor(
    policies,
    scope="trial",
)

results = run_specs(
    study,
    space,
    endpoint,
    processor=processor,
)
```

This keeps the policy choice visible inside the specification record.

Do not add arbitrary threshold levels merely to make a specification grid larger.

## 10. Read `active_rules` correctly

Inactive fields are `None`.

```python
policy = ReadinessThresholds(
    max_coordinate_issue_fraction=declared_limit,
)

print(policy.active_rules)
```

Only declared criteria participate.

For `require_monotonic_time`, the runtime treats `True` as an active rule. `False` is not counted as an active restriction. The design center therefore exposes “require monotonic time” as an explicit opt-in rather than pretending that unchecked means a second scientific policy.

## 11. Interpret the three readiness statuses

### `unassessed`

No active rule participated.

This does not mean all units passed.

### `ready_under_policy`

All evaluated trial and participant units satisfy the active declared policy.

This does not establish broader measurement or inferential validity.

### `review_under_policy`

At least one evaluated trial or participant unit fails one or more active rules.

This does not automatically imply exclusion.

Inspect `failed_rules` and the cohort preview.

## 12. Preserve provenance

A readiness report includes:

- `policy_name`;
- threshold values;
- active rules;
- policy fingerprint;
- structural-QC audit identity;
- trial summary;
- participant summary;
- cohort-impact table;
- readiness fingerprint;
- software-bound manifest fingerprint.

For durable evidence:

```python
from gazeaudit import write_analysis_readiness_artifacts

write_analysis_readiness_artifacts(
    readiness,
    "analysis-readiness",
)
```

Use the verification function before reuse.

A valid fingerprint proves identity/integrity of the recorded state. It does not prove the threshold rationale was scientifically appropriate.

## 13. If the source representation changes, rebuild readiness

A change to mapped values, identifiers, timestamps, row order, or source version can change:

- structural-QC metrics;
- trial grouping;
- participant grouping;
- readiness failures;
- retained denominators.

After a representation repair:

1. preserve the old readiness record if it supported prior outputs;
2. update mapping/QC provenance;
3. rebuild `GazeStudy`;
4. rerun structural QC;
5. rerun readiness evaluation;
6. compare before/after state;
7. rerun affected downstream analyses.

Do not carry an old policy result onto a new canonical study merely because the threshold values are unchanged.

## 14. Interpretation checklist

Before calling a cohort “ready under policy”, verify:

- [ ] every active threshold has an explicit rationale source;
- [ ] threshold timing is recorded;
- [ ] trial versus participant scope is understood;
- [ ] the policy name is stable and meaningful;
- [ ] inactive criteria remain explicit rather than silently defaulted;
- [ ] cohort impact is inspected before filtering;
- [ ] filter scope is recorded separately;
- [ ] participant-level flagged-trial logic is understood;
- [ ] alternative defensible policies have been considered where relevant;
- [ ] any post hoc or reviewer-requested policy is labelled honestly;
- [ ] the readiness status is not described as universal data quality.

## 15. Reporting examples

### Methods — primary policy

> Structural analysis readiness was evaluated using the predeclared `[policy name]` policy. Active criteria were [rules and values with rationale/source]. Trial- and participant-level summaries and no-mutation cohort-impact previews were inspected before applying the policy. The primary analysis used [trial/participant] scope; criteria omitted from the policy were not evaluated.

### Methods — multiple defensible policies

> Because more than one structural-readiness policy was defensible, the primary policy and [n] declared alternatives were evaluated separately. Policy-specific cohort retention was recorded before endpoint estimation, and readiness policy was included as a sensitivity/specification factor rather than selected after observing the substantive result.

### Results

> Under `[policy name]`, readiness status was `[status]`. At trial scope, [x/y] trial units and [rows] rows were retained; at participant scope, [x/y] participants, [trials], and [rows] would have been retained. The primary analysis used [scope], as declared before [timing event].

### Limitation

> The readiness assessment is policy-relative and evaluates only declared structural criteria. It does not establish calibration accuracy, event-detection validity, AOI validity, missingness mechanism, measurement-error adequacy, or inferential robustness.

## 16. Reporting mistakes to avoid

Do not write:

- “participants failing GazeAudit QC were removed” when the actual rule was a researcher-declared readiness policy;
- “GazeAudit recommended a 5% cutoff”;
- “the final sample passed quality control” without naming the policy and scope;
- “strict QC confirmed robustness” when only cohort retention was inspected;
- “no missing-data criterion” when the criterion was simply inactive;
- “participant exclusion” when trial-level filtering was applied.

## 17. Limitations of readiness governance

Readiness thresholds are useful for making structural decisions explicit, but they do not solve:

- uncertainty in calibration accuracy;
- model misspecification;
- AOI boundary uncertainty;
- detector validity;
- informative missingness;
- dependence among QC metrics;
- causal interpretation of cohort changes;
- outcome-informed policy choice.

A complete analysis may need readiness governance **plus** measurement-uncertainty, missingness, sampling, or specification-space sensitivity.

## API links

- [`ReadinessThresholds`]({{ '/docs/reference/api-pathways/#api-readinessthresholds' | relative_url }})
- [`evaluate_analysis_readiness()`]({{ '/docs/reference/api-pathways/#api-evaluate-analysis-readiness' | relative_url }})
- [`cohort_impact_preview()`]({{ '/docs/reference/api-pathways/#api-cohort-impact-preview' | relative_url }})
- [`readiness_policy_table()`]({{ '/docs/reference/api-pathways/#api-readiness-policy-table' | relative_url }})
- [Analysis-readiness API pathway]({{ '/docs/reference/api-pathways/#path-readiness-governance' | relative_url }})
- [Readiness Policy Design Center]({{ '/docs/readiness-policy/' | relative_url }})
- [Machine-readable threshold reference]({{ '/assets/readiness-threshold-reference.json' | relative_url }})

## Worked exercise

Continue to [Readiness policy design]({{ '/docs/examples/readiness-policy-design/' | relative_url }}) for a fully synthetic primary/alternative policy exercise that preserves policy timing, cohort denominators, interpretation, and reporting boundaries.
