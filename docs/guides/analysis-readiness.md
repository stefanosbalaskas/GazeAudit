---
title: Analysis-readiness governance
kicker: Guide
---

# Analysis-readiness governance

GazeAudit can turn structural QC findings into an **auditable readiness policy**, without pretending that one package-wide threshold defines a scientifically valid eye-tracking dataset.

The design is deliberately two-stage:

1. **evaluate and preview** — declare thresholds, summarize participant/trial QC, and inspect the cohort that would remain;
2. **apply explicitly** — filter only when your analysis protocol actually requires that declared policy.

A readiness result is therefore always **policy-relative**. `ready_under_policy` means the observed table satisfies the thresholds you declared. It does **not** mean “validated experiment,” “good data,” or “safe to publish.”

## 1. Declare thresholds

```python
from gazeaudit import ReadinessThresholds

policy = ReadinessThresholds(
    max_coordinate_issue_fraction=0.05,
    max_duplicate_timestamp_fraction=0.02,
    max_flagged_trial_fraction=0.20,
    min_rows_per_trial=100,
    min_trials_per_participant=6,
    require_monotonic_time=True,
)
```

There are no universal defaults. An omitted criterion is not evaluated. The complete threshold mapping receives a deterministic `policy_fingerprint` so a later analysis can prove which rule set was used.

## 2. Summarize before excluding

```python
from gazeaudit import evaluate_analysis_readiness

readiness = evaluate_analysis_readiness(
    study,
    policy,
    policy_name="preregistered_primary",
)

readiness.trial_summary
readiness.participant_summary
readiness.cohort_impact
```

The trial and participant tables expose counts, issue fractions, failed rule names, and `passes_thresholds`. `cohort_impact` shows the **counterfactual filtering consequence** at trial and participant scope while leaving the original `GazeStudy` unchanged.

## 3. Apply only when intended

```python
from gazeaudit import filter_study_by_readiness

analysis_study = filter_study_by_readiness(
    study,
    readiness,
    scope="trial",
)
```

The explicit filter function refuses an unassessed policy and refuses to produce an empty study. Previewing never filters automatically.

## 4. Compare alternative policies

```python
from gazeaudit import readiness_policy_table

policy_table = readiness_policy_table(
    study,
    {
        "lenient": ReadinessThresholds(max_coordinate_issue_fraction=0.10),
        "primary": policy,
        "strict": ReadinessThresholds(max_coordinate_issue_fraction=0.01),
    },
)
```

This makes researcher degrees of freedom visible before they alter the cohort.

## 5. Bind readiness into a specification space

A QC threshold can be a declared multiverse factor rather than a hidden preprocessing choice.

```python
from gazeaudit import PipelineSpace, readiness_pipeline_processor, run_specs

policies = {"primary": policy, "strict": strict_policy}
space = PipelineSpace().add_choice("readiness_policy", policies)
processor = readiness_pipeline_processor(policies, scope="trial")

results = run_specs(
    study,
    space,
    endpoint,
    processor=processor,
)
```

Each specification names the readiness policy that produced its cohort.

## 6. Compare before/after repair

```python
from gazeaudit import compare_qc_states

comparison = compare_qc_states(before, after)
comparison.metrics
```

The comparison binds both study fingerprints and both QC audit fingerprints. A negative delta means a structural count decreased; it is **not** automatically evidence that the repair was scientifically appropriate.

## 7. Export machine-readable evidence

```python
from gazeaudit import write_analysis_readiness_artifacts

write_analysis_readiness_artifacts(
    readiness,
    "analysis-readiness",
    repair_comparison=comparison,
)
```

The bundle contains thresholds, trial/participant readiness tables, cohort impact, optional repair comparison, a readiness manifest, and a SHA-256 integrity manifest. Use `verify_analysis_readiness_artifacts()` before reuse.

## Visual diagnostics

The [plot gallery]({{ '/docs/plots/' | relative_url }}) contains code-generated examples for readiness profiles, cohort impact, repair comparison, threshold sweeps, policy trade-offs, and downstream robustness plots. Every gallery image links to executable source and includes a text alternative.

## Interpretation boundary

Structural readiness is a **governance layer**, not a universal quality score. Thresholds should come from the acquisition protocol, preregistration, device characteristics, task demands, sensitivity analysis, or another defensible study-specific rationale. Report the policy, the cohort impact, and any alternative policies that materially change the analysis sample.
