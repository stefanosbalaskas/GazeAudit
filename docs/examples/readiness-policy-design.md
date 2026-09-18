---
title: Readiness policy design
description: A fully synthetic worked example for declaring a primary and alternative GazeAudit readiness policy, previewing trial- versus participant-scope cohort consequences, interpreting policy-relative status, and writing bounded Methods, Results, and limitations text.
kicker: Example · Readiness governance
page_type: example
permalink: /docs/examples/readiness-policy-design/
search_category: Example
search_keywords: readiness policy thresholds cohort impact primary alternative trial participant ReadinessThresholds evaluate_analysis_readiness readiness_policy_table reporting synthetic
example_data: "Synthetic"
example_focus: "Data & QC"
example_reuse: "Readiness-policy declaration, comparison, denominator, and reporting pattern"
example_output: "Primary/alternative readiness policies with policy-relative status and trial/participant cohort-impact interpretation"
example_boundary: "All threshold values are teaching choices for this synthetic fixture; they are not recommended eye-tracking cutoffs."
---

# Readiness policy design

This is a **fully synthetic policy-governance exercise**. It uses the same deterministic study shape as the repository's executable `examples/analysis_readiness.py` example, but focuses on the decisions around a readiness policy rather than treating the threshold values as reusable defaults.

<div class="callout warning">
<strong>Do not copy the thresholds.</strong>
The numerical values below were chosen to make trial- and participant-scope consequences visible in a small synthetic fixture. They are not package recommendations, device specifications, or empirical quality cutoffs.
</div>

## Scenario

The synthetic study contains:

- 3 participants;
- 2 trials per participant;
- 24 rows per trial;
- 144 total rows.

Three structural conditions are inserted deliberately:

1. one trial has 2 non-finite x coordinates;
2. one trial has 2 rows participating in a duplicate timestamp key;
3. one trial has decreasing finite time in observed row order.

Each condition occurs in a different participant.

## Build the study

```python
import numpy as np
import pandas as pd

from gazeaudit import GazeStudy

rows = []
for participant_index, participant in enumerate(("P01", "P02", "P03")):
    for trial in (1, 2):
        for sample in range(24):
            rows.append(
                {
                    "participant": participant,
                    "trial": trial,
                    "timestamp": sample * (1000.0 / 60.0),
                    "x": 0.25 + 0.045 * sample + 0.04 * participant_index,
                    "y": 0.55 + 0.12 * np.sin(sample / 4.0 + trial),
                }
            )

data = pd.DataFrame(rows)

data.loc[
    (data["participant"] == "P02")
    & (data["trial"] == 2)
    & (data.index % 11 == 0),
    "x",
] = np.nan

duplicate_mask = (data["participant"] == "P03") & (data["trial"] == 1)
duplicate_rows = data.loc[duplicate_mask].index[:2]
data.loc[duplicate_rows[1], "timestamp"] = data.loc[
    duplicate_rows[0], "timestamp"
]

disorder = data.index[
    (data["participant"] == "P01") & (data["trial"] == 2)
][10:12]
data.loc[disorder, "timestamp"] = data.loc[
    disorder[::-1], "timestamp"
].to_numpy()

study = GazeStudy(data)
```

## First inspect structural QC

Do not jump directly to thresholds.

```python
from gazeaudit import audit_study_qc, study_qc_diagnostics

qc = audit_study_qc(study)
diagnostics = study_qc_diagnostics(study)

print(qc.status)
print(qc.issue_codes)
print(diagnostics)
```

The fixture is intentionally a `review` state.

The policy step below assumes that the structural conditions have already been understood as part of this synthetic exercise.

## Declare the primary teaching policy

```python
from gazeaudit import ReadinessThresholds

primary = ReadinessThresholds(
    max_coordinate_issue_fraction=0.05,
    max_duplicate_timestamp_fraction=0.05,
    max_flagged_trial_fraction=0.50,
    min_rows_per_trial=20,
    require_monotonic_time=True,
)
```

For this fixture only:

- 2/24 coordinate-issue rows is approximately 0.083, which exceeds 0.05;
- 2/24 duplicate-timestamp rows is approximately 0.083, which exceeds 0.05;
- every trial has at least 20 rows;
- one participant × trial unit has decreasing time.

These values are selected to create visible failures in the teaching data.

## Evaluate without filtering

```python
from gazeaudit import evaluate_analysis_readiness

primary_report = evaluate_analysis_readiness(
    study,
    primary,
    policy_name="synthetic_primary",
)

print(primary_report.status)
print(primary_report.trial_summary)
print(primary_report.participant_summary)
print(primary_report.cohort_impact)
```

The expected status is:

```text
review_under_policy
```

That status means at least one evaluated unit fails the declared teaching policy. It does not mean the study is universally invalid.

## Understand the trial-level result

Under the synthetic primary policy:

| Participant | Trial | Main reason for readiness failure |
|---|---:|---|
| P01 | 1 | passes active rules |
| P01 | 2 | decreasing finite time |
| P02 | 1 | passes active rules |
| P02 | 2 | coordinate-issue fraction > 0.05 |
| P03 | 1 | duplicate-timestamp fraction > 0.05 |
| P03 | 2 | passes active rules |

So trial-scope preview retains:

- **72 / 144 rows**;
- **3 / 6 trial units**;
- **3 / 3 participants represented by at least one retained trial**.

This is why “50% retained” is incomplete reporting: row/trial retention is 50%, while participant representation is 100% at trial scope.

## Understand the participant-level result

Participant aggregation changes the logic.

### P01

One of two trials is flagged, so `flagged_trial_fraction == 0.50` and does **not** exceed the declared maximum of 0.50.

However, `require_monotonic_time=True` also operates at participant scope: P01 has one decreasing-time trial, so P01 fails the participant policy.

### P02

Its 2 coordinate-issue rows are aggregated over 48 participant rows:

```text
2 / 48 ≈ 0.0417
```

That does not exceed 0.05. Its flagged-trial fraction is 0.50, which also does not exceed 0.50.

P02 therefore passes the participant policy.

### P03

Its 2 duplicate-timestamp rows are also 2/48 ≈ 0.0417 at participant scope, and its flagged-trial fraction is 0.50.

P03 passes the participant policy.

Participant-scope preview therefore retains:

- **96 / 144 rows**;
- **4 / 6 trial units**;
- **2 / 3 participants**.

Again, trial and participant filtering are different scientific actions.

## Declare an alternative teaching policy

Now loosen only the two row-fraction limits and the flagged-trial limit while keeping the time and minimum-row requirements unchanged:

```python
alternative = ReadinessThresholds(
    max_coordinate_issue_fraction=0.10,
    max_duplicate_timestamp_fraction=0.10,
    max_flagged_trial_fraction=0.75,
    min_rows_per_trial=20,
    require_monotonic_time=True,
)
```

Under this synthetic alternative:

- the P02 coordinate trial now passes;
- the P03 duplicate-timestamp trial now passes;
- the P01 decreasing-time trial still fails.

Trial-scope preview therefore retains:

- **120 / 144 rows**;
- **5 / 6 trial units**;
- **3 / 3 participants represented**.

Participant scope still excludes P01 because monotonic time is required, so participant-scope retention remains:

- **96 / 144 rows**;
- **4 / 6 trial units**;
- **2 / 3 participants**.

The policy change materially alters **trial-scope retention** but not **participant-scope retention** in this fixture.

## Compare policies directly

```python
from gazeaudit import readiness_policy_table

comparison = readiness_policy_table(
    study,
    {
        "synthetic_primary": primary,
        "synthetic_alternative": alternative,
    },
)

print(comparison)
```

The comparison is a governance/sensitivity record.

Do not choose the alternative merely because it retains more data.

A real policy comparison should be declared from defensible rationale sources before inspecting substantive outcome differences wherever possible.

## Why `max_flagged_trial_fraction` changes

Under the primary policy, P02 trial 2 and P03 trial 1 fail trial-level criteria.

Under the alternative policy, those trials pass.

Their participant-level `flagged_trial_fraction` therefore changes from 0.50 to 0.00 even though no source row has changed.

This demonstrates that `max_flagged_trial_fraction` is downstream of the active trial policy.

## Keep application scope explicit

Previewing has not filtered anything.

If the synthetic protocol had independently declared trial-scope filtering:

```python
from gazeaudit import filter_study_by_readiness

analysis_study = filter_study_by_readiness(
    study,
    primary_report,
    scope="trial",
)
```

If participant scope had been declared instead, the resulting cohort would be different.

Do not switch scope after seeing which version produces the preferred endpoint.

## Optional: make policy uncertainty part of robustness analysis

If both policies were genuinely defensible:

```python
from gazeaudit import (
    PipelineSpace,
    readiness_pipeline_processor,
    run_specs,
)

policies = {
    "synthetic_primary": primary,
    "synthetic_alternative": alternative,
}

space = PipelineSpace().add_choice(
    "readiness_policy",
    policies,
)

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

This exposes readiness policy as a declared analytical factor instead of hiding it inside preprocessing.

The synthetic values still do not become scientifically defensible merely because they are placed in a multiverse.

## Interpretation

This exercise shows four distinct facts:

1. `review_under_policy` is relative to the declared policy.
2. The same row-level issue can have different fractions at trial and participant scope.
3. Trial-scope and participant-scope filtering produce different denominators.
4. Changing trial rules can alter participant `flagged_trial_fraction` without changing the source data.

None of these facts establishes which policy a real study should use.

## Reporting example

### Methods

> Structural readiness was evaluated under a prespecified primary policy comprising maximum coordinate-issue and duplicate-timestamp fractions, a maximum flagged-trial fraction, a minimum rows-per-trial requirement, and monotonic-time requirement. Trial- and participant-level summaries and cohort-impact previews were inspected before the declared trial-level filter was applied. A separately declared alternative policy was retained as a sensitivity analysis.

### Results for this synthetic fixture

> The synthetic primary policy returned `review_under_policy`. Trial-scope preview retained 72/144 rows and 3/6 trial units while preserving at least one trial from all 3 participants. Participant-scope preview retained 96/144 rows, 4/6 trial units, and 2/3 participants. Under the synthetic alternative policy, trial-scope retention increased to 120/144 rows and 5/6 trial units, whereas participant-scope retention remained 2/3 participants.

These numbers belong only to this deterministic teaching fixture.

### Limitation

> Readiness status and cohort retention are conditional on the declared structural policy and filter scope. They do not establish calibration quality, event-detection validity, AOI validity, missingness ignorability, or robustness of the substantive endpoint.

## API links

- [`ReadinessThresholds`]({{ '/docs/reference/api-pathways/#api-readinessthresholds' | relative_url }})
- [`evaluate_analysis_readiness()`]({{ '/docs/reference/api-pathways/#api-evaluate-analysis-readiness' | relative_url }})
- [`cohort_impact_preview()`]({{ '/docs/reference/api-pathways/#api-cohort-impact-preview' | relative_url }})
- [`readiness_policy_table()`]({{ '/docs/reference/api-pathways/#api-readiness-policy-table' | relative_url }})
- [Analysis-readiness method pathway]({{ '/docs/reference/api-pathways/#path-readiness-governance' | relative_url }})
- [Readiness Policy Design Center]({{ '/docs/readiness-policy/' | relative_url }})
- [Design and audit readiness policies]({{ '/docs/guides/readiness-policy-design/' | relative_url }})

## Reuse boundary

Reuse:

- the sequence from structural evidence → declared policy → no-mutation preview → scope decision → application → sensitivity/reporting;
- denominator discipline;
- policy timing/provenance;
- the separation between primary and alternative policies.

Rebuild for every real study:

- threshold values;
- rationale sources;
- filter scope;
- timing classification;
- alternative policy set;
- endpoint sensitivity;
- manuscript claims.
