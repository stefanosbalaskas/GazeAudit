---
title: Data Contract & Schema Mapping Center
description: Map an eye-tracking table into GazeStudy safely, understand constructor versus structural-preflight requirements, and generate a copyable semantic column mapping without renaming vendor columns.
kicker: Reference · Data contract
page_type: data-contract
permalink: /docs/data-contract/
search_category: Reference
search_keywords: GazeStudy data contract schema mapping columns x y timestamp participant trial csv units numeric long form preflight constructor
---

# Data Contract & Schema Mapping Center

Use this page when you have a gaze or fixation table and need to answer:

> **What does GazeAudit require before I can create a canonical `GazeStudy`?**

The runtime authority is the public [`GazeStudy` contract]({{ '/docs/reference/api-pathways/' | relative_url }}#api-gazestudy). This page turns that contract into a practical schema-mapping workflow without imposing a vendor-specific export format.

<div class="callout info">
<strong>Semantic mapping, not automatic interpretation.</strong>
GazeAudit does not infer coordinate units, timestamp units, screen geometry, event semantics, participant meaning, trial meaning, exclusions, or calibration quality from column names. You supply the semantic mapping; downstream scientific decisions remain explicit.
</div>

<figure class="plot-card">
  <img src="{{ '/assets/images/data-contract-flow.svg' | relative_url }}" alt="Flow from an original vendor or analysis table through explicit x, y, timestamp, participant, and trial mappings into GazeStudy, followed by structural preflight and downstream analysis">
  <figcaption>The source table keeps its original columns. `GazeStudy` records which five columns carry the canonical semantics; structural preflight is a separate review step.</figcaption>
</figure>

## Constructor contract

The current public signature is:

```python
GazeStudy(
    data,
    x="x",
    y="y",
    timestamp="timestamp",
    participant="participant",
    trial="trial",
)
```

Those default names are **software defaults**, not a requirement to rename your data.

| Contract | Constructor behavior |
|---|---|
| input object | `data` must be a pandas `DataFrame` |
| table length | at least one observation is required |
| mapped columns | x, y, timestamp, participant, and trial source columns must exist |
| x / y | mapped columns must have a numeric pandas dtype |
| timestamp | mapped column must have a numeric pandas dtype |
| participant / trial values | column existence is required; missing identifier values are handled by structural preflight rather than rejected by the constructor |
| additional columns | preserved unchanged in `study.data` |
| time ordering | not enforced at construction; use structural preflight or `validate_time_order()` |
| units | not inferred or converted |

<div class="callout warning">
<strong>Numeric does not mean unitless.</strong>
A coordinate column can be numeric in pixels, normalized screen coordinates, degrees, or another documented space. A timestamp can be numeric in seconds, milliseconds, sample indices, or another scale. GazeAudit does not silently convert those units.
</div>

## Map your existing column names

This builder generates only the semantic `GazeStudy(...)` mapping. It does **not** upload or inspect your data, infer units, or choose any QC rule.

<form class="schema-mapper" data-schema-mapper aria-describedby="schema-mapper-help">
  <p id="schema-mapper-help" class="schema-mapper-help">
    Enter the exact source-column names that carry each semantic role. All five mappings are required to generate the snippet.
  </p>

  <div class="schema-mapper-grid">
    <label for="schema-data-var">
      <span>DataFrame variable</span>
      <input id="schema-data-var" type="text" value="frame" autocomplete="off" data-schema-data-var>
      <small>Python variable holding your pandas DataFrame; this is code structure, not a source-column name.</small>
    </label>

    <label for="schema-participant">
      <span>Participant column</span>
      <input id="schema-participant" type="text" autocomplete="off" placeholder="e.g. participant_id" data-schema-participant>
      <small>Stable participant identifier in your source table.</small>
    </label>

    <label for="schema-trial">
      <span>Trial column</span>
      <input id="schema-trial" type="text" autocomplete="off" placeholder="e.g. trial_id" data-schema-trial>
      <small>Identifier for the within-participant trial or analysis unit.</small>
    </label>

    <label for="schema-timestamp">
      <span>Timestamp column</span>
      <input id="schema-timestamp" type="text" autocomplete="off" placeholder="e.g. time_ms" data-schema-timestamp>
      <small>Numeric time-like column. Record its unit separately.</small>
    </label>

    <label for="schema-x">
      <span>Horizontal coordinate column</span>
      <input id="schema-x" type="text" autocomplete="off" placeholder="e.g. gaze_x_px" data-schema-x>
      <small>Numeric horizontal coordinate in your documented coordinate system.</small>
    </label>

    <label for="schema-y">
      <span>Vertical coordinate column</span>
      <input id="schema-y" type="text" autocomplete="off" placeholder="e.g. gaze_y_px" data-schema-y>
      <small>Numeric vertical coordinate in the same documented spatial convention.</small>
    </label>
  </div>

  <div class="schema-mapper-actions">
    <button type="button" data-schema-clear>Clear mapping</button>
  </div>
</form>

<div class="schema-mapper-output" aria-labelledby="schema-output-title">
  <div class="schema-mapper-output-head">
    <div>
      <span class="eyebrow">Generated mapping</span>
      <h2 id="schema-output-title">Canonical constructor snippet</h2>
    </div>
    <button type="button" data-schema-copy disabled>Copy mapping</button>
  </div>
  <pre><code data-schema-code>Complete all five semantic column mappings to generate code.</code></pre>
  <p data-schema-status role="status" aria-live="polite" aria-atomic="true">No mapping generated yet.</p>
</div>

## Construction failure versus structural review

Not every data problem belongs at the same layer.

| Condition | `GazeStudy(...)` | Structural preflight |
|---|---|---|
| mapped column absent | **fails** | not reached |
| x, y, or timestamp column nonnumeric | **fails** | not reached |
| zero rows | **fails** | not reached |
| missing x/y values in a numeric column | constructs | **review** |
| infinite x/y values | constructs | **review** |
| missing/infinite timestamps in a numeric column | constructs | **review** |
| missing participant/trial values | constructs | **review** |
| duplicate finite timestamps within participant × trial | constructs | **review** |
| decreasing finite timestamps within participant × trial | constructs | **review**; `validate_time_order()` can also fail fast |

This separation is intentional. The constructor validates the canonical representation; structural preflight reports conditions that require contextual inspection rather than silently converting them into exclusions.

## Minimal valid synthetic table

A table can be small and still satisfy the constructor contract:

```python
import pandas as pd

from gazeaudit import GazeStudy

frame = pd.DataFrame(
    {
        "participant_id": ["P01", "P01"],
        "trial_id": ["T01", "T01"],
        "time_ms": [0.0, 16.7],
        "gaze_x_px": [520.0, 523.0],
        "gaze_y_px": [410.0, 412.0],
    }
)

study = GazeStudy(
    frame,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)
```

This proves only that the canonical constructor contract is satisfied. It does not establish calibration quality, AOI validity, detector validity, adequate sampling, or inferential robustness.

## Unit record

Record the units and coordinate convention alongside the mapping. A compact project note can be enough:

```text
x: gaze_x_px — pixels, stimulus coordinate system
y: gaze_y_px — pixels, stimulus coordinate system
timestamp: time_ms — milliseconds from trial onset
participant: participant_id — anonymized participant key
trial: trial_id — within-participant stimulus presentation
```

If you transform units before construction, record that transformation as preprocessing provenance rather than relying on the canonical object to remember an unrecorded conversion.

## What happens next

<div class="workflow-steps">
  <div class="workflow-step"><strong>1 · Map</strong><p>Bind the five semantic roles to the actual source columns.</p></div>
  <div class="workflow-step"><strong>2 · Record units</strong><p>Document coordinate and timestamp units plus any preprocessing transformation.</p></div>
  <div class="workflow-step"><strong>3 · Construct</strong><p>Create `GazeStudy` and handle hard schema errors explicitly.</p></div>
  <div class="workflow-step"><strong>4 · Preflight</strong><p>Run structural QC; inspect review conditions rather than treating them as automatic exclusions.</p></div>
  <div class="workflow-step"><strong>5 · Decide</strong><p>Record researcher-owned repairs, retention, exclusion, or representation decisions.</p></div>
</div>

Continue with [Map your table into GazeStudy]({{ '/docs/guides/map-your-table/' | relative_url }}) for the task-oriented procedure, or [Valid, invalid, and reviewable tables]({{ '/docs/examples/data-contract-valid-invalid/' | relative_url }}) for a synthetic failure-case walkthrough.
