---
title: First real audit example
description: Run one practical GazeAudit script on deterministic demo data or a canonical eye-tracking CSV and save structural-QC provenance plus robustness tables.
kicker: Example · Own data
permalink: /docs/examples/first-real-audit/
search_category: Example
search_keywords: csv own data practical executable tutorial audit qc robustness pipeline output
page_type: example
example_data: "Demo or user data"
example_focus: "Data & QC"
example_reuse: "Project template"
example_output: "Structural-QC provenance and robustness tables"
example_boundary: "Demo choices must be replaced or justified before use on a real study."
---

# First real audit example

This example is the shortest route from **“I have a gaze table”** to a complete, inspectable GazeAudit output folder.

The executable source is [`examples/first_real_audit.py`](https://github.com/stefanosbalaskas/GazeAudit/blob/main/examples/first_real_audit.py).

<div class="callout info">
<strong>Demo mode is synthetic.</strong>
Running the script without <code>--csv</code> creates deterministic synthetic data so you can verify the workflow before pointing it at a research file. Supplying your own CSV does not turn the example into validation evidence; the scientific interpretation remains study-specific.
</div>

## What the script does

1. loads a canonical CSV or builds deterministic demo data;
2. constructs `GazeStudy`;
3. builds a structural `StudyQCAudit` with study/audit fingerprints;
4. declares a 12-specification `PipelineSpace`;
5. executes one common treatment-minus-control AOI occupancy endpoint;
6. calculates the specification curve, effect stability, marginal sensitivity, and pairwise sensitivity;
7. writes deterministic structural-QC artifacts plus the robustness tables.

## Expected CSV columns

The worked example expects:

```text
participant,trial,timestamp,x,y,condition,quality
```

These are **example-level canonical names**, not a claim that every eye tracker exports the same schema. Rename or map your source columns explicitly before using the workflow.

## Run the built-in demo

```bash
python examples/first_real_audit.py --output-dir demo-audit
```

The script prints the row count, structural-QC status, issue codes, number of evaluated specifications, stability summary, and generated file paths.

## Run your own table

```bash
python examples/first_real_audit.py \
  --csv path/to/my_gaze.csv \
  --output-dir analysis-output
```

If a required canonical column is missing, the script stops with a clear error instead of guessing how the study is encoded.

## Output folder

The workflow writes:

- deterministic study-QC JSON/CSV artifacts and integrity manifest under `study-qc/`;
- `specifications.csv` — every evaluated branch;
- `specification-curve.csv` — ordered estimates;
- `effect-stability.csv` — descriptive stability summary;
- `marginal-sensitivity.csv` — one-factor screening;
- `pairwise-sensitivity.csv` — pairwise non-additivity screening.

Keep the complete specification table. A robustness audit is not reproducible if only one preferred branch survives into the analysis archive.

## What you must change for a real study

The script deliberately exposes its assumptions in code. Replace the demonstration values rather than treating them as defaults:

| Component | Demo value | Researcher responsibility |
|---|---|---|
| quality thresholds | `0.70`, `0.80` | justify levels from acquisition/QC context |
| sample stride | `1`, `2` | decide whether temporal thinning is scientifically relevant |
| AOI radius | `0.16`, `0.20`, `0.24` | use the study's real AOI geometry/uncertainty logic |
| conditions | `control`, `treatment` | map the actual design |
| endpoint | occupancy difference | prespecify the scientific quantity |

## Why this example is different from the synthetic tutorial

The [end-to-end robustness audit]({{ '/docs/examples/end-to-end-robustness/' | relative_url }}) teaches the core specification API from a self-contained synthetic study.

This page is **operational**: it adds CSV loading, canonical-column checks, structural-QC provenance, output writing, and a command-line path intended to be adapted to a real project directory.

For the reasoning behind each step, read [First real audit with your own data]({{ '/docs/guides/first-real-audit/' | relative_url }}). For the study-level sequence around the code, use the [first-study audit workflow]({{ '/docs/workflows/first-study-audit/' | relative_url }}).
