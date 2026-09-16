---
title: Understanding the audit output bundle
description: A practical guide to the files produced by the first GazeAudit workflow, what each artifact answers, and how to keep descriptive robustness evidence separate from scientific interpretation.
kicker: Guide · Read the outputs
permalink: /docs/guides/audit-output-bundle/
search_category: Guides
search_keywords: output bundle artifacts csv study qc specification curve effect stability marginal sensitivity pairwise provenance first audit
---

<link rel="stylesheet" href="{{ '/assets/css/output-bundle.css' | relative_url }}">
<script src="{{ '/assets/js/output-bundle.js' | relative_url }}" defer></script>

# Understanding the audit output bundle

A useful audit should leave behind more than one preferred estimate or figure. The [first real audit]({{ '/docs/guides/first-real-audit/' | relative_url }}) is designed to save the structural record, the complete specification table, and multiple descriptive views of sensitivity together.

This page explains **what each output is for, what question it answers, and what it does not establish**.

<div class="callout info">
<strong>The bundle is an audit record, not an automatic verdict.</strong>
GazeAudit preserves researcher-defined decisions and their consequences. It does not decide whether an effect is scientifically valid, choose exclusions, or convert descriptive sensitivity summaries into causal evidence.
</div>

## Explore the bundle interactively

Use the artifact map to move through the output contract before reading the detailed sections below. The ordering follows a practical review path: provenance first, then the complete specification set, then progressively more compact sensitivity views.

<div class="bundle-explorer" data-bundle-explorer>
  <div class="bundle-explorer-files" role="tablist" aria-label="Audit output artifacts" aria-orientation="vertical">
    <p class="bundle-explorer-label">Audit bundle</p>
    <button class="bundle-item" type="button" role="tab" id="bundle-tab-qc" aria-selected="true" aria-controls="bundle-artifact-panel" tabindex="0" data-bundle-item data-bundle-name="study-qc/" data-bundle-stage="01 · Provenance" data-bundle-purpose="Records structural diagnostics, researcher decisions, and fingerprints for the audited study representation." data-bundle-inspect="Check diagnostic IDs, recorded decisions and rationales, and the study/audit fingerprints before interpreting downstream robustness outputs." data-bundle-boundary="A structural flag is a prompt for investigation. This directory does not define universal exclusion rules or decide scientific validity." data-bundle-route="{{ '/docs/guides/data-onboarding/' | relative_url }}" data-bundle-route-label="Open structural preflight guide →">
      <span class="bundle-item-index">01</span><span class="bundle-item-copy"><strong>study-qc/</strong><small>diagnostics · decisions · fingerprints</small></span>
    </button>
    <button class="bundle-item" type="button" role="tab" id="bundle-tab-specifications" aria-selected="false" aria-controls="bundle-artifact-panel" tabindex="-1" data-bundle-item data-bundle-name="specifications.csv" data-bundle-stage="02 · Complete results" data-bundle-purpose="Preserves one row per evaluated analytical specification and acts as the audit backbone for every downstream summary." data-bundle-inspect="Verify that every prespecified branch is represented, factor values match the declared decision space, failures remain visible, and the endpoint meaning is stable across branches." data-bundle-boundary="The complete table does not identify a preferred specification. Do not filter it after observing results to recover a convenient narrative." data-bundle-route="{{ '/docs/guides/specification-space/' | relative_url }}" data-bundle-route-label="Open specification-space guide →">
      <span class="bundle-item-index">02</span><span class="bundle-item-copy"><strong>specifications.csv</strong><small>every declared analytical branch</small></span>
    </button>
    <button class="bundle-item" type="button" role="tab" id="bundle-tab-curve" aria-selected="false" aria-controls="bundle-artifact-panel" tabindex="-1" data-bundle-item data-bundle-name="specification-curve.csv" data-bundle-stage="03 · Distribution view" data-bundle-purpose="Orders endpoint estimates across the declared specification space so their spread, sign pattern, and relative position can be inspected." data-bundle-inspect="Look for clustering, sign changes, broad magnitude shifts, and where any headline estimate sits within the complete declared result set." data-bundle-boundary="Empirical quantiles are not confidence intervals, and the curve does not imply that every specification is equally plausible for the study." data-bundle-route="{{ '/docs/examples/specification-curve/' | relative_url }}" data-bundle-route-label="Open specification-curve example →">
      <span class="bundle-item-index">03</span><span class="bundle-item-copy"><strong>specification-curve.csv</strong><small>ordered endpoint estimates</small></span>
    </button>
    <button class="bundle-item" type="button" role="tab" id="bundle-tab-stability" aria-selected="false" aria-controls="bundle-artifact-panel" tabindex="-1" data-bundle-item data-bundle-name="effect-stability.csv" data-bundle-stage="04 · Stability summary" data-bundle-purpose="Compresses the declared result set into descriptive sign and empirical magnitude summaries for a concise robustness overview." data-bundle-inspect="Read the summary together with the number of evaluated specifications and the decision space that generated it." data-bundle-boundary="Stability summaries are descriptive properties of the declared specification set. They are not posterior probabilities, confidence statements, or causal evidence." data-bundle-route="{{ '/docs/guides/reporting-robustness/' | relative_url }}" data-bundle-route-label="Open robustness-reporting guide →">
      <span class="bundle-item-index">04</span><span class="bundle-item-copy"><strong>effect-stability.csv</strong><small>sign · magnitude · compact summary</small></span>
    </button>
    <button class="bundle-item" type="button" role="tab" id="bundle-tab-marginal" aria-selected="false" aria-controls="bundle-artifact-panel" tabindex="-1" data-bundle-item data-bundle-name="marginal-sensitivity.csv" data-bundle-stage="05 · One-factor view" data-bundle-purpose="Groups endpoint estimates by levels of one declared analytical factor to locate choices associated with visible sensitivity." data-bundle-inspect="Compare factor levels for systematic shifts, sign changes, or magnitude differences that deserve closer inspection in the full specification table." data-bundle-boundary="These are descriptive comparisons across the declared audit space, not causal variance decompositions or experimental factor effects." data-bundle-route="{{ '/docs/examples/sampling-sensitivity/' | relative_url }}" data-bundle-route-label="Open sampling-sensitivity example →">
      <span class="bundle-item-index">05</span><span class="bundle-item-copy"><strong>marginal-sensitivity.csv</strong><small>one declared factor at a time</small></span>
    </button>
    <button class="bundle-item" type="button" role="tab" id="bundle-tab-pairwise" aria-selected="false" aria-controls="bundle-artifact-panel" tabindex="-1" data-bundle-item data-bundle-name="pairwise-sensitivity.csv" data-bundle-stage="06 · Joint-factor view" data-bundle-purpose="Surfaces joint patterns between pairs of declared analytical factors that can be missed by one-factor summaries." data-bundle-inspect="Trace strong pairwise patterns back to the corresponding specifications and the scientific assumptions that make those combinations defensible." data-bundle-boundary="A pairwise pattern inside the declared audit space does not by itself establish a generalisable interaction or a causal mechanism." data-bundle-route="{{ '/docs/examples/end-to-end-robustness/' | relative_url }}" data-bundle-route-label="Open complete robustness audit →">
      <span class="bundle-item-index">06</span><span class="bundle-item-copy"><strong>pairwise-sensitivity.csv</strong><small>joint patterns across choices</small></span>
    </button>
  </div>

  <section class="bundle-explorer-panel" id="bundle-artifact-panel" role="tabpanel" aria-labelledby="bundle-tab-qc" data-bundle-panel>
    <div class="bundle-panel-head">
      <div><span class="bundle-panel-stage" data-bundle-stage>01 · Provenance</span><h3 data-bundle-name>study-qc/</h3></div>
      <button class="bundle-copy-button" type="button" data-bundle-copy data-copy-value="study-qc/">Copy artifact name</button>
    </div>
    <div class="bundle-panel-grid">
      <div class="bundle-panel-block"><h4>What it is for</h4><p data-bundle-purpose>Records structural diagnostics, researcher decisions, and fingerprints for the audited study representation.</p></div>
      <div class="bundle-panel-block"><h4>What to inspect</h4><p data-bundle-inspect>Check diagnostic IDs, recorded decisions and rationales, and the study/audit fingerprints before interpreting downstream robustness outputs.</p></div>
      <div class="bundle-panel-block bundle-panel-block-wide bundle-panel-block-boundary"><h4>Scientific boundary</h4><p data-bundle-boundary>A structural flag is a prompt for investigation. This directory does not define universal exclusion rules or decide scientific validity.</p></div>
    </div>
    <div class="bundle-panel-footer"><span>Continue from this artifact</span><a data-bundle-route href="{{ '/docs/guides/data-onboarding/' | relative_url }}">Open structural preflight guide →</a></div>
    <span class="sr-only" role="status" aria-live="polite" data-bundle-status>study-qc/ selected.</span>
  </section>
</div>

The explorer is a navigation and interpretation aid. It does not rank artifacts by scientific importance or replace the complete bundle. Keep the outputs together rather than retaining only the file that supports the most convenient narrative.

## Run the deterministic companion first

From a repository checkout with the package installed:

```bash
python examples/first_real_audit.py --output-dir demo-audit
```

The no-`--csv` path uses deterministic synthetic demonstration data. It is useful for learning the file contract and checking that the workflow executes; it is **not validation evidence for a real study**.

For a canonical study table:

```bash
python examples/first_real_audit.py \
  --csv path/to/my_gaze.csv \
  --output-dir analysis-output
```

The worked example expects the seven documented canonical columns. Its demonstration AOI, quality levels, sampling stride, and endpoint must be replaced by study-specific choices before the pattern is treated as a substantive analysis.

## Output map

| Output | Main question it answers | Keep it because… |
|---|---|---|
| `study-qc/` | What structural conditions and review decisions were recorded? | it binds diagnostics, decisions, and fingerprints to the audited study representation |
| `specifications.csv` | What happened in every declared analytical branch? | it prevents the audit from collapsing back to one selected pipeline |
| `specification-curve.csv` | How are endpoint estimates distributed across the declared space? | it provides the ordered data behind a specification-curve view |
| `effect-stability.csv` | How stable are sign and empirical magnitude summaries across specifications? | it gives a compact descriptive summary of the complete declared result set |
| `marginal-sensitivity.csv` | How do estimates vary across levels of one declared factor? | it helps identify which researcher-defined choices deserve closer inspection |
| `pairwise-sensitivity.csv` | Which pairs of declared factors show non-additive sensitivity patterns? | it surfaces interactions that one-factor summaries can hide |

Treat the directory as one evidence bundle. Do not retain only the file that gives the most convenient narrative.

## 1. Start with `study-qc/`

Read structural diagnostics before interpreting robustness outputs. A structural flag is a prompt for investigation, not an automatic exclusion instruction.

The QC layer is also where explicit decisions can be tied to diagnostic IDs. That separation matters: a data-shape observation and the researcher's response to it are different pieces of evidence.

When archiving the analysis, preserve the study and audit fingerprints alongside the decision log so later readers can tell which representation was audited.

## 2. Treat `specifications.csv` as the audit backbone

`specifications.csv` should contain one row per evaluated specification. This is the most important table to preserve because all downstream summaries are views of this declared result set.

Useful checks include:

- every prespecified branch is represented;
- the endpoint has the same scientific meaning in every branch;
- factor values correspond to the declared decision space;
- failures or undefined estimates are visible rather than silently removed;
- the table was not filtered after results were observed.

If the declared space changes, treat that as a new audit decision and record why it changed.

## 3. Read the specification curve as a map, not a test

`specification-curve.csv` orders the evaluated estimates so the spread and sign pattern can be inspected directly. It is useful for seeing whether a headline estimate sits inside a tight cluster or among materially different alternatives.

The curve does **not** make every specification equally plausible, and its empirical quantiles are **not confidence intervals**. Scientific interpretation still depends on why the included alternatives were defensible for the study.

Continue with the [specification-space guide]({{ '/docs/guides/specification-space/' | relative_url }}) for design principles and the [plot gallery]({{ '/docs/plots/' | relative_url }}) for the code-generated visual form.

## 4. Use effect stability as a compact descriptive summary

`effect-stability.csv` compresses the declared result set into empirical stability summaries. It is useful when a reader needs a concise account of whether estimates retain direction and how broadly their magnitude varies.

Report the underlying specification count and decision space with the summary. A stability statistic without the audited alternatives that generated it is difficult to interpret.

## 5. Use marginal sensitivity to locate consequential choices

`marginal-sensitivity.csv` groups estimates by levels of declared factors. It is a screening view for questions such as:

- do estimates move systematically across a quality-policy choice?
- does a sampling decision correspond to a noticeable magnitude shift?
- are AOI alternatives associated with materially different endpoint values?

These are descriptive comparisons across the declared specification set. They are **not causal variance decompositions** and should not be worded as if a factor experimentally caused the observed change.

## 6. Use pairwise sensitivity when one-factor summaries are insufficient

`pairwise-sensitivity.csv` helps reveal combinations of choices whose joint pattern is not obvious from marginal summaries alone.

A strong pairwise pattern is a reason to inspect the corresponding specifications and scientific assumptions. It is not, by itself, evidence that the same interaction generalises beyond the declared audit space.

## 7. Connect tables to visual diagnostics

GazeAudit's deterministic plot layer is intended to make these audit questions easier to inspect. Useful routes include:

- [specification curve]({{ '/docs/examples/specification-curve/' | relative_url }}) for the spread of declared estimates;
- [sampling sensitivity]({{ '/docs/examples/sampling-sensitivity/' | relative_url }}) when acquisition or resampling assumptions matter;
- [analysis readiness]({{ '/docs/examples/analysis-readiness/' | relative_url }}) for cohort-policy consequences;
- [AOI boundary uncertainty]({{ '/docs/examples/aoi-boundary/' | relative_url }}) for measurement sensitivity.

The public [plot gallery]({{ '/docs/plots/' | relative_url }}) uses deterministic synthetic demonstrations unless a figure is explicitly identified as frozen observed evidence.

## 8. Archive the bundle with the analysis definition

A reproducible record should preserve, together:

1. the package version or exact commit;
2. input-data identity or a privacy-safe fingerprinting strategy;
3. semantic column mappings;
4. researcher-owned QC/readiness decisions and rationales;
5. the declared specification space;
6. the processor and endpoint definitions;
7. all specification results and sensitivity summaries;
8. generated figures and manuscript-facing interpretation.

For publication packaging, continue to the [reproducible publication workflow]({{ '/docs/workflows/reproducible-publication/' | relative_url }}) and [publication audits guide]({{ '/docs/guides/publication-audits/' | relative_url }}).

## A compact reading order

When reviewing someone else's bundle, a defensible order is:

**QC/provenance → declared choices → complete specifications → curve/stability → marginal and pairwise sensitivity → figures → manuscript wording**.

That order keeps the evidence-generating decisions visible before the most polished result summary is read.
