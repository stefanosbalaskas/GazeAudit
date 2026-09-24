---
title: First real audit with your own data
description: A practical, end-to-end guide for taking a canonical eye-tracking CSV through structural preflight, declared robustness analysis, diagnostics, and reproducible outputs with GazeAudit.
kicker: Guide · Start with your data
permalink: /docs/guides/first-real-audit/
search_category: Guides
search_keywords: own data csv practical tutorial first audit gaze study preflight qc robustness pipeline specification output provenance project starter
---

# First real audit with your own data

This is the **practical starting guide** for a researcher who has an eye-tracking table and wants to use GazeAudit on that study rather than only read API pages.

It connects one concrete path:

**CSV → `GazeStudy` → structural preflight → researcher decisions → declared specification space → robustness summaries → saved evidence**.

<div class="callout info">
<strong>GazeAudit does not choose your scientific rules.</strong>
The thresholds, AOIs, detector choices, exclusions, perturbation levels, endpoint, and interpretation remain study-specific decisions. The values below are a worked API pattern, not recommended universal cutoffs.
</div>

The companion executable is [`examples/first_real_audit.py`](https://github.com/stefanosbalaskas/GazeAudit/blob/main/examples/first_real_audit.py). Run its built-in deterministic demo first, then point the same script at a canonical CSV.

## Runbook: prepare, run, verify

<div class="first-audit-runbook" aria-label="Three-stage first real audit runbook">
  <div class="runbook-step">
    <span>01 · Prepare</span>
    <strong>Make the input contract explicit</strong>
    <p>Confirm the seven worked-example columns or map your source schema deliberately before analysis.</p>
    <code>participant · trial · timestamp · x · y · condition · quality</code>
  </div>
  <div class="runbook-step">
    <span>02 · Run</span>
    <strong>Verify demo, then use your CSV</strong>
    <p>Exercise the deterministic workflow first so environment and output-writing problems are separated from study-specific problems.</p>
    <code>python examples/first_real_audit.py --csv …</code>
  </div>
  <div class="runbook-step">
    <span>03 · Verify</span>
    <strong>Inspect the complete evidence bundle</strong>
    <p>Check structural-QC provenance, all declared specifications, robustness summaries, and software identity before interpretation.</p>
    <code>analysis-output/study-qc/ + specifications.csv + summaries</code>
  </div>
</div>

<div class="workspace-boundary-bar">
  <div><strong>Starting a new study folder?</strong> <span>Use the project starter to separate data, analysis code, decisions, environment, and generated evidence before adapting the example.</span></div>
  <a href="{{ '/docs/guides/project-starter/' | relative_url }}">Open project starter →</a>
</div>

### Quick input check

The worked executable expects:

<div class="schema-chip-grid" aria-label="Canonical first-audit CSV columns">
  <code>participant</code>
  <code>trial</code>
  <code>timestamp</code>
  <code>x</code>
  <code>y</code>
  <code>condition</code>
  <code>quality</code>
</div>

These are **example-level canonical names**, not universal vendor fields. If your table differs, use the [Data Contract & Schema Mapping Center]({{ '/docs/data-contract/' | relative_url }}) to map the real participant, trial, timestamp, x, and y columns explicitly rather than guessing; renaming the source columns is not required.

### Quick commands

Verify the deterministic path:

```bash
python examples/first_real_audit.py --output-dir demo-audit
```

Then run the canonical study table:

```bash
python examples/first_real_audit.py \
  --csv path/to/my_gaze.csv \
  --output-dir analysis-output
```

A successful practical run should preserve the complete evidence bundle rather than one preferred branch:

<div class="artifact-grid" aria-label="Expected practical audit evidence">
  <div><code>study-qc/</code><span>structural report, diagnostics, decisions, fingerprints, manifest</span></div>
  <div><code>specifications.csv</code><span>every evaluated analytical branch</span></div>
  <div><code>specification-curve.csv</code><span>ordered estimates across the declared space</span></div>
  <div><code>effect-stability.csv</code><span>descriptive stability summary</span></div>
  <div><code>marginal-sensitivity.csv</code><span>one-factor descriptive screening</span></div>
  <div><code>pairwise-sensitivity.csv</code><span>pairwise non-additivity screening</span></div>
</div>

The sections below explain why each stage exists and where researcher judgement enters.

## 1. Install the release you intend to report

For the stable public release:

```bash
python -m pip install "gazeaudit==0.2.0"
```

Record the exact package version or commit used in the analysis. The website may document newer development features on `main` than the stable release contains.

## 2. Put the study into one explicit table

For the companion example, use these canonical columns:

| Column | Meaning | Example |
|---|---|---|
| `participant` | participant identifier | `P014` |
| `trial` | trial or stimulus identifier | `burger_ad_03` |
| `timestamp` | within-trial time in a consistent unit | `1.483` |
| `x` | horizontal gaze coordinate in one declared coordinate system | `0.524` |
| `y` | vertical gaze coordinate in the same system | `0.417` |
| `condition` | condition needed by the worked endpoint | `treatment` |
| `quality` | study-defined sample quality variable used by the worked specification space | `0.91` |

If your export uses different names, rename them explicitly before constructing the study. Do not silently guess column meaning.

```python
import pandas as pd
from gazeaudit import GazeStudy

frame = pd.read_csv("my_gaze.csv")
frame = frame.rename(
    columns={
        "ParticipantName": "participant",
        "TrialName": "trial",
        "Time": "timestamp",
        "GazeX": "x",
        "GazeY": "y",
    }
)

study = GazeStudy(frame)
```

If you prefer to preserve vendor names, map them directly:

```python
study = GazeStudy(
    frame,
    x="GazeX",
    y="GazeY",
    timestamp="Time",
    participant="ParticipantName",
    trial="TrialName",
)
```

## 3. Run structural preflight before substantive analysis

```python
from gazeaudit import build_study_qc_audit

qc = build_study_qc_audit(study)
print(qc.report.to_dict())
print(qc.diagnostics)
print(qc.study_fingerprint)
print(qc.audit_fingerprint)
```

The preflight checks structural conditions such as non-finite coordinates/timestamps, missing identifiers, duplicate participant × trial timestamps, and decreasing time order.

**Structural QC is not scientific validity.** A flag tells you what needs review. It does not automatically mean a participant, trial, or dataset should be excluded.

## 4. Record decisions after investigating flags

When a diagnostic needs an explicit decision, record the action and rationale rather than silently editing the data.

```python
from gazeaudit import StudyQCDecision, build_study_qc_audit

reviewed = (
    StudyQCDecision(
        issue_code="timestamp_duplicate",
        action="retain after acquisition review",
        rationale=(
            "The duplicate timestamp is a documented representation feature "
            "and is retained for the declared downstream analysis."
        ),
        diagnostic_ids=("D000001",),
    ),
)

qc = build_study_qc_audit(study, decisions=reviewed)
```

Use the actual diagnostic IDs produced by your study. The text above is only an example of the provenance mechanism.

## 5. Declare the alternative analytical choices before interpreting results

The companion workflow varies three deliberately simple decisions:

```python
from gazeaudit import PipelineSpace

space = (
    PipelineSpace()
    .add_choice("min_quality", [0.70, 0.80])
    .add_choice("sample_stride", [1, 2])
    .add_choice("aoi_radius", [0.16, 0.20, 0.24])
)
```

This creates 12 specifications. Replace these levels with alternatives that are defensible for **your** acquisition, preprocessing, AOI construction, and analysis plan.

Do not expand the space after seeing which choices produce a preferred result.

## 6. Keep preprocessing choices and the scientific endpoint separate

The processor applies declared data-handling choices. The endpoint always returns the same scientific quantity.

```python
def process_specification(study, spec):
    frame = study.data.copy()
    frame["sample_rank"] = frame.groupby(
        [study.participant, study.trial], sort=False
    ).cumcount()

    keep = (frame["quality"] >= float(spec["min_quality"])) & (
        frame["sample_rank"] % int(spec["sample_stride"]) == 0
    )
    return study.copy_with(frame.loc[keep].drop(columns="sample_rank"))
```

The worked endpoint is treatment minus control occupancy in a circular AOI. It is pedagogical; substitute the prespecified endpoint for your study.

## 7. Execute the complete declared space

```python
from gazeaudit import run_specs

results = run_specs(
    study,
    space,
    endpoint=condition_aoi_occupancy_effect,
    processor=process_specification,
)
```

`run_specs()` returns one row per evaluated specification. Preserve the complete table; do not retain only the branch you prefer.

## 8. Inspect robustness without turning diagnostics into inferential tests

```python
from gazeaudit import (
    effect_stability,
    marginal_sensitivity,
    pairwise_interaction_sensitivity,
    specification_curve,
)

curve = specification_curve(results)
stability = effect_stability(results)

factors = ["min_quality", "sample_stride", "aoi_radius"]
marginal = marginal_sensitivity(results, factors=factors)
pairwise = pairwise_interaction_sensitivity(results, factors=factors)
```

Read these outputs descriptively:

- the specification curve shows the spread of the declared estimates;
- `effect_stability()` reports empirical summaries across specifications;
- marginal sensitivity screens how estimates vary across levels of one factor;
- pairwise sensitivity highlights non-additive patterns between declared choices.

Empirical specification quantiles are **not confidence intervals**, and sensitivity ratios are **not causal variance decompositions**.

## 9. Save the audit trail, not only the final figure

```python
from gazeaudit import write_study_qc_artifacts

write_study_qc_artifacts(qc, "analysis-output/study-qc")
results.to_csv("analysis-output/specifications.csv", index=False)
curve.to_csv("analysis-output/specification-curve.csv", index=False)
```

The companion script also saves stability, marginal-sensitivity, and pairwise-sensitivity tables. Keep these with your analysis code and study-specific decision log.

## 10. Run the companion script on your file

First verify the workflow with deterministic demo data:

```bash
python examples/first_real_audit.py --output-dir demo-audit
```

Then run your canonical table:

```bash
python examples/first_real_audit.py \
  --csv path/to/my_gaze.csv \
  --output-dir analysis-output
```

The script fails clearly if the seven canonical columns required by the worked example are missing. That is preferable to guessing how your study is encoded.

## 11. Adapt the workflow to your actual research question

Before treating the example as your analysis, replace all demonstration-specific choices:

1. **coordinate system and units** — document whether coordinates are pixels, normalized display coordinates, degrees, or another representation;
2. **quality variable** — define what it means and why any threshold levels are defensible;
3. **AOI geometry** — use the study's real AOIs rather than the demonstration circle;
4. **condition coding** — verify that every specification retains the groups required by the endpoint;
5. **endpoint** — use one prespecified scientific quantity across all branches;
6. **decision space** — include only analytically defensible alternatives;
7. **reporting rule** — decide in advance what stability, fragility, or unresolved evidence means for the study.

## 12. Continue into the appropriate governed layer

- Need a clean study directory first? Use the [reproducible project starter]({{ '/docs/guides/project-starter/' | relative_url }}).
- Need participant/trial retention policies? Use [analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}).
- Need gaze-position uncertainty at AOI boundaries? Use [AOI uncertainty]({{ '/docs/guides/aoi-uncertainty/' | relative_url }}).
- Need a broader multiverse? Use [specification spaces]({{ '/docs/guides/specification-space/' | relative_url }}).
- Need manuscript wording? Use [reporting robustness]({{ '/docs/guides/reporting-robustness/' | relative_url }}).
- Need deterministic publication evidence? Use [publication audits]({{ '/docs/guides/publication-audits/' | relative_url }}).

For the project-level sequence, continue with the [first-study audit workflow]({{ '/docs/workflows/first-study-audit/' | relative_url }}).
