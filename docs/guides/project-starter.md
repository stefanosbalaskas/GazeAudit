---
title: Start a reproducible GazeAudit project
description: A compact project scaffold for taking one eye-tracking CSV from explicit schema mapping to a preserved GazeAudit evidence bundle without treating demonstration choices as scientific defaults.
kicker: Guide · Project starter
permalink: /docs/guides/project-starter/
search_category: Guides
search_keywords: project starter scaffold own data csv first audit reproducible folder structure commands schema output evidence decisions provenance
---

# Start a reproducible GazeAudit project

Use this page when you already have—or are about to receive—a study table and want a **clean project structure before analysis begins**.

The scaffold is deliberately small. It does not prescribe thresholds, AOIs, exclusions, detector settings, perturbation levels, endpoints, or interpretation rules. Those remain study-specific scientific decisions.

<div class="callout info">
<strong>Project structure is not a scientific protocol.</strong>
This guide organizes inputs, code, decisions, and outputs so that the analysis can be reconstructed. It does not make the analysis scientifically appropriate by itself.
</div>

## The 60-second route

<div class="first-audit-runbook" aria-label="Three-stage GazeAudit project starter">
  <div class="runbook-step">
    <span>01 · Prepare</span>
    <strong>Create one explicit project</strong>
    <p>Keep the canonical study table, analysis code, researcher decisions, software record, and generated evidence separate.</p>
    <code>project/data → analysis → decisions → evidence</code>
  </div>
  <div class="runbook-step">
    <span>02 · Run</span>
    <strong>Start from the governed example</strong>
    <p>Verify the deterministic demo first, then point the same workflow at your canonical CSV.</p>
    <code>python analysis/run_audit.py --csv data/my_gaze.csv</code>
  </div>
  <div class="runbook-step">
    <span>03 · Verify</span>
    <strong>Inspect the complete evidence bundle</strong>
    <p>Confirm structural-QC provenance, every declared specification, robustness summaries, and the exact software identity are preserved.</p>
    <code>evidence/study-qc/ + specifications.csv + summaries</code>
  </div>
</div>

## 1. Use a project layout that makes provenance visible

A minimal study directory can look like this:

```text
my-study/
├── data/
│   └── my_gaze.csv
├── analysis/
│   └── run_audit.py
├── decisions/
│   └── audit-decisions.md
├── environment/
│   └── requirements.txt
└── evidence/
```

What matters is the separation of responsibilities:

| Location | Purpose | Keep with the analysis record? |
|---|---|---|
| `data/` | the canonical table supplied to the audit | according to your data-governance policy |
| `analysis/` | executable study-specific analysis code | yes |
| `decisions/` | researcher rationale for flagged QC conditions and analytical alternatives | yes |
| `environment/` | package/version record | yes |
| `evidence/` | deterministic QC artifacts and robustness outputs | yes |

Do not publicly commit identifiable, confidential, licensed, or otherwise restricted study data merely to reproduce this folder structure. Preserve restricted inputs using the storage and access controls appropriate to your project.

## 2. Start from the maintained executable example

Use [`examples/first_real_audit.py`](https://github.com/stefanosbalaskas/GazeAudit/blob/main/examples/first_real_audit.py) as the starting implementation for `analysis/run_audit.py`.

The example already demonstrates:

- explicit CSV loading;
- fail-closed canonical-column checks;
- `GazeStudy` construction;
- structural-QC provenance and fingerprints;
- one finite declared `PipelineSpace`;
- complete specification execution;
- specification-curve, effect-stability, marginal-sensitivity, and pairwise-sensitivity outputs;
- deterministic evidence writing.

Run the unmodified deterministic demo before adapting it:

```bash
python analysis/run_audit.py --output-dir evidence/demo-audit
```

Then run the canonical study table:

```bash
python analysis/run_audit.py \
  --csv data/my_gaze.csv \
  --output-dir evidence/main-audit
```

## 3. Make the input contract explicit before running anything

The worked executable expects these **example-level canonical columns**:

<div class="schema-chip-grid" aria-label="Canonical first-audit CSV columns">
  <code>participant</code>
  <code>trial</code>
  <code>timestamp</code>
  <code>x</code>
  <code>y</code>
  <code>condition</code>
  <code>quality</code>
</div>

A quick local schema check is useful before executing the whole audit:

```python
import pandas as pd

frame = pd.read_csv("data/my_gaze.csv", nrows=5)
required = {
    "participant",
    "trial",
    "timestamp",
    "x",
    "y",
    "condition",
    "quality",
}
missing = sorted(required.difference(frame.columns))
if missing:
    raise SystemExit(f"Map these columns explicitly before analysis: {missing}")
print(frame.dtypes)
```

If your source uses different names, either rename them deliberately or construct `GazeStudy` with explicit semantic mappings. Do not infer column meaning from position or similar-looking labels.

## 4. Freeze the software identity you intend to report

For the current stable public release:

```text
# environment/requirements.txt
gazeaudit==0.1.0
```

Install that environment with:

```bash
python -m pip install -r environment/requirements.txt
```

If the study intentionally uses development `main`, record the exact commit instead of describing the environment only as “latest”. The documentation site can contain features newer than the stable public release.

## 5. Write down researcher-owned decisions next to the code

A compact `decisions/audit-decisions.md` can use a simple structure:

```markdown
# Audit decisions

## Study representation
- Coordinate system / units:
- Timestamp units:
- Participant / trial unit:

## Structural-QC review
- Diagnostic ID:
- Decision:
- Rationale:

## Declared analytical alternatives
- Factor:
- Levels:
- Scientific justification:

## Endpoint
- Prespecified quantity:
- Why it is held constant across specifications:
```

This human-readable record complements the machine-generated QC decision artifacts. It should explain **why** the study-specific choices were defensible, not merely repeat parameter values.

## 6. Replace every demonstration-specific choice before interpreting real results

The maintained example deliberately uses simple demonstration values for quality thresholds, sample stride, AOI radius, condition labels, and an occupancy-difference endpoint.

Before treating a run as your study analysis, replace them with choices that were defensible for the actual acquisition and research question.

<div class="workspace-boundary-bar">
  <div><strong>Do not inherit demo defaults by convenience.</strong> <span>The starter organizes work; it does not convert demonstration values into recommended thresholds or validated study rules.</span></div>
  <a href="{{ '/docs/guides/first-real-audit/' | relative_url }}">Adapt the full workflow →</a>
</div>

## 7. Verify the evidence directory before interpretation

After a successful run, the audit directory should contain the structural-QC evidence plus the complete robustness outputs:

<div class="artifact-grid" aria-label="Expected practical audit evidence">
  <div><code>study-qc/</code><span>report, diagnostics, decisions, fingerprints, manifest</span></div>
  <div><code>specifications.csv</code><span>every evaluated analytical branch</span></div>
  <div><code>specification-curve.csv</code><span>ordered estimates across the declared space</span></div>
  <div><code>effect-stability.csv</code><span>descriptive stability summaries</span></div>
  <div><code>marginal-sensitivity.csv</code><span>one-factor descriptive screening</span></div>
  <div><code>pairwise-sensitivity.csv</code><span>pairwise non-additivity screening</span></div>
</div>

Preserve the whole bundle. Do not keep only the branch or summary that is easiest to report.

Empirical specification quantiles are not confidence intervals, and marginal or pairwise sensitivity summaries are not causal variance decompositions.

## 8. Continue only when the next layer answers a real question

Once the basic project is running:

- use [data onboarding]({{ '/docs/guides/data-onboarding/' | relative_url }}) when source-column mapping or structural-QC interpretation needs more detail;
- use [analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}) when participant/trial retention rules need to be declared;
- use [AOI uncertainty]({{ '/docs/guides/aoi-uncertainty/' | relative_url }}) when gaze-position uncertainty at boundaries matters;
- use [specification spaces]({{ '/docs/guides/specification-space/' | relative_url }}) when the analytical decision space needs to expand beyond the compact example;
- use [publication audits]({{ '/docs/guides/publication-audits/' | relative_url }}) when the final evidence package must be fingerprinted and archived.

For a linear walkthrough, continue with [First real audit with your own data]({{ '/docs/guides/first-real-audit/' | relative_url }}). For the study-level sequence, use the [first-study audit workflow]({{ '/docs/workflows/first-study-audit/' | relative_url }}).
