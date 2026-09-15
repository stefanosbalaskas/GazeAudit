---
title: Analysis-readiness example
permalink: /docs/examples/analysis-readiness/
kicker: Example
---

# Analysis-readiness example

This runnable example shows the full sequence **QC → threshold policy → cohort preview → repair comparison → specification-space integration**.

```bash
python examples/analysis_readiness.py
```

The source is [`examples/analysis_readiness.py`](https://github.com/stefanosbalaskas/GazeAudit/blob/main/examples/analysis_readiness.py).

The example deliberately uses deterministic synthetic data. Its threshold values demonstrate the API; they are not recommended universal eye-tracking cutoffs.

## What to inspect

- `readiness.trial_summary`: one row per participant × trial unit;
- `readiness.participant_summary`: participant-level aggregation, including fraction of trials that fail the policy;
- `readiness.cohort_impact`: rows, trials, and participants retained under trial-level vs participant-level filtering;
- `policy_table`: side-by-side impact of multiple declared policies;
- `repair_comparison.metrics`: structural before/after deltas with both states provenance-bound;
- `specification_results`: an ordinary GazeAudit specification table where readiness policy is itself a declared analysis choice.

For visual versions of the same concepts, see the [plot gallery]({{ '/docs/plots/' | relative_url }}).
