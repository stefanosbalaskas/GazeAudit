---
title: Mapping change audit
description: A fully synthetic provenance exercise showing how source-column renames, source-version changes, unit conversions, coordinate transforms, grouping changes, and exclusions affect the data-mapping record.
kicker: Example · Data provenance
page_type: example
permalink: /docs/examples/data-mapping-change-audit/
search_category: Example
search_keywords: data mapping change audit provenance rename units conversion coordinate transform participant trial source version preprocessing synthetic
example_data: "Synthetic"
example_focus: "Data & QC"
example_reuse: "Mapping-change classification pattern"
example_output: "A before/after mapping comparison with an explicit rerun decision"
example_boundary: "A mapping-provenance record improves reconstruction but does not certify preprocessing or scientific validity."
---

# Mapping change audit

This is a **fully synthetic provenance exercise**. It shows how to decide whether a change is merely a source-schema update or whether it changes the canonical representation enough to require renewed structural or downstream analysis.

The exercise uses documentation records only. It does not claim that JSON comparison can determine scientific validity automatically.

## Baseline record

Assume the submitted analysis used:

```json
{
  "schema": "gazeaudit-data-mapping-record-v1",
  "source_id": "exports/session_level_long_v1.csv",
  "columns": {
    "participant": "participant_code",
    "trial": "stimulus_trial",
    "timestamp": "recording_time_ms",
    "x": "screen_x_px",
    "y": "screen_y_px"
  },
  "units": {
    "coordinates": "pixels",
    "timestamp": "milliseconds from trial onset"
  },
  "coordinate_convention": "origin top-left; x right; y down; stimulus pixels",
  "pre_mapping_transformations": "binocular channels combined by scripts/build_analysis_table.py"
}
```

This describes the table presented to `GazeStudy`. It does not certify that the binocular-combination rule or spatial representation was scientifically justified.

## Change A — source column renamed, semantics unchanged

A refactored export changes:

```text
screen_x_px → x_screen_px
screen_y_px → y_screen_px
```

The values, units, coordinate convention, participant/trial semantics, and source rows are otherwise unchanged.

Updated mapping:

```json
{
  "columns": {
    "participant": "participant_code",
    "trial": "stimulus_trial",
    "timestamp": "recording_time_ms",
    "x": "x_screen_px",
    "y": "y_screen_px"
  }
}
```

Classification:

- **mapping record changes** — yes;
- **source schema changes** — yes;
- **scientific spatial semantics change** — not by the rename alone;
- **construct `GazeStudy` again** — yes, because code points to new source fields;
- **structural preflight** — rerun on the canonical source used for the new analysis;
- **geometry-dependent result expected to change solely because of the rename** — no, if values and semantics truly remained identical.

The last conclusion depends on verifying identity elsewhere; the mapping record itself does not compare data values.

## Change B — corrected source export

Suppose a corrected export becomes:

```text
exports/session_level_long_v2.csv
```

Even if the column names are identical, the source identity changed.

Classification:

- bind the new source ID;
- reconstruct the canonical study;
- rerun structural preflight;
- rerun downstream analyses that use changed observations;
- preserve the v1 record if v1 supported an earlier manuscript, review response, or archive.

Do not reuse a v1 QC fingerprint merely because the schema looks the same.

## Change C — timestamp unit conversion

The source originally stores seconds:

```text
0.000
0.0167
0.0334
```

A preprocessing step multiplies the values by 1000 and the canonical table stores milliseconds.

The new record should state both the unit and transformation:

```json
{
  "units": {
    "coordinates": "pixels",
    "timestamp": "milliseconds from trial onset"
  },
  "pre_mapping_transformations": "timestamp_seconds multiplied by 1000 before canonical table"
}
```

This is **not** merely a label change. Values changed under a declared transformation.

The appropriate rerun scope depends on downstream operations. Anything using timestamp magnitude, ordering, sampling interval, duration, or rate must be checked against the new representation.

## Change D — coordinate conversion

Normalized coordinates are converted to stimulus pixels before mapping.

That changes the numerical spatial representation, even if every point refers to the same conceptual gaze location.

Classification:

- mapping provenance changes;
- coordinate unit/convention changes;
- preprocessing changes;
- reconstruct the study;
- rerun structural preflight;
- rerun AOI/geometry/error-model operations whose inputs changed;
- preserve the conversion rule and any display/stimulus dimensions needed to reconstruct it.

Do not describe this only as “renamed x/y columns.”

## Change E — trial identifier redefined

Suppose `trial` changes from presentation-level IDs to blocks.

That alters the grouping semantics used by:

- participant × trial counts;
- timestamp duplicate detection;
- decreasing-time detection;
- downstream operations that group by trial.

This is a substantive canonical-representation change.

The new mapping record should make the new source field explicit, while the decision/preprocessing record explains *why* the analysis unit changed.

## Change F — rows excluded after QC

Suppose a reviewer asks for an exclusion and a new canonical table removes some trials.

That is not adequately represented by:

```json
{
  "source_id": "analysis_table_v2.csv"
}
```

The source identity should change, but the exclusion itself belongs in the researcher decision/revision record because it is an analytical action, not just a schema mapping.

Mapping provenance and scientific decision provenance are complementary.

## Compare records mechanically, interpret changes scientifically

A simple project script can compare documentation records:

```python
import json
from pathlib import Path

before = json.loads(Path("provenance/data-mapping-v1.json").read_text())
after = json.loads(Path("provenance/data-mapping-v2.json").read_text())

for key in sorted(set(before) | set(after)):
    if before.get(key) != after.get(key):
        print(key, "changed")
```

This can identify changed fields. It cannot decide whether a change is harmless, required, scientifically material, or outcome-informed.

## Rerun matrix

| Change | Reconstruct study | Structural preflight | Downstream rerun |
|---|---:|---:|---|
| source column rename only | yes | yes for the new canonical source | only if values/semantics changed |
| corrected source export | yes | yes | affected analyses |
| timestamp unit conversion | yes | yes | time-dependent analyses |
| coordinate conversion | yes | yes | spatial/geometry-dependent analyses |
| trial semantic change | yes | yes | grouping-dependent analyses |
| scientific exclusion | yes | yes | full affected scientific record + decision provenance |

The table is a provenance-oriented routing aid, not a universal causal rule. When uncertainty remains about whether a downstream result is affected, rerun rather than assume equivalence.

## Historical integrity

If the earlier mapping already supported a frozen or submitted result:

- keep the old mapping record;
- create a new record for the new source/representation;
- connect the new record to the revision or correction history;
- do not rewrite the old record to make the project appear as though the new mapping had always been used.

Return to [Record data-mapping provenance]({{ '/docs/guides/data-mapping-provenance/' | relative_url }}) for the general rules or the [Data Contract & Schema Mapping Center]({{ '/docs/data-contract/' | relative_url }}) to generate a fresh mapping record.
