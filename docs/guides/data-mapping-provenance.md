---
title: Record data-mapping provenance
description: Preserve source identity, semantic column mappings, units, coordinate conventions, preprocessing transformations, and mapping changes without treating documentation provenance as scientific validation.
kicker: Guide · Data provenance
permalink: /docs/guides/data-mapping-provenance/
search_category: Guide
search_keywords: data mapping provenance manifest source identity units coordinate convention timestamp transformation rename schema GazeStudy record audit
---

# Record data-mapping provenance

Use this guide after you know which source columns map to `GazeStudy` and before the mapping becomes an undocumented assumption inside analysis code.

The [Data Contract & Schema Mapping Center]({{ '/docs/data-contract/' | relative_url }}) can generate a compact JSON record alongside the constructor snippet. That record is intentionally **documentation-side provenance**. It does not become a new GazeAudit runtime object, inspect the source file, or certify the scientific meaning of the mapping.

## 1. Record the source identity you actually control

Use a source identifier that another project member can resolve later. Depending on your workflow this may be:

- a project-relative path;
- an immutable dataset identifier;
- a release/archive identifier;
- a checksum label generated elsewhere;
- a database extract/version identifier;
- another stable project-local reference.

Do not fabricate a checksum merely because a field labelled “source identity” sounds stronger with one.

A useful record might contain:

```json
{
  "source_id": "exports/session_level_long.csv"
}
```

If your project already has a stronger immutable source ledger, reference that ledger rather than duplicating its authority.

## 2. Bind semantic roles to source columns

The core mapping is:

```json
{
  "columns": {
    "participant": "participant_code",
    "trial": "stimulus_trial",
    "timestamp": "recording_time_ms",
    "x": "screen_x_px",
    "y": "screen_y_px"
  }
}
```

This is the bridge between the source schema and GazeAudit's vendor-neutral representation.

A source-column rename can leave the scientific semantics unchanged, but the mapping record still changes because the source contract changed.

## 3. Record units independently of column names

Do not infer units from suffixes such as `_px` or `_ms` unless those suffixes are themselves governed by your source specification.

Record the unit from acquisition/export/preprocessing documentation:

```json
{
  "units": {
    "coordinates": "pixels",
    "timestamp": "milliseconds from trial onset"
  }
}
```

If x and y use different units—which would be unusual but possible—do not force them into a misleading single unit field. Record the exception in the coordinate-convention or transformation note and consider using a richer project-level provenance record.

## 4. Record coordinate convention

A spatial value is incomplete without its reference system when geometry matters.

Useful details can include:

- origin location;
- x-axis direction;
- y-axis direction;
- display versus stimulus coordinates;
- normalization convention;
- pixel dimensions used in an earlier transformation;
- whether coordinates were already corrected or recalibrated.

Example:

```json
{
  "coordinate_convention": "origin top-left; x increases right; y increases down; stimulus pixels"
}
```

This record describes the table; it does not validate the coordinate system.

## 5. Record transformations before canonical mapping

Examples include:

- combining left/right eye channels;
- selecting one eye;
- converting seconds to milliseconds;
- converting normalized coordinates to pixels;
- deriving a trial ID from event markers;
- repairing a documented export concatenation problem;
- sorting after an identified source-order defect.

Record what happened and, where relevant, point to the script or decision record that performed it.

Do not write:

```text
cleaned data
```

when the actual operation was:

```text
converted timestamp seconds to milliseconds; combined binocular coordinates by the predeclared project rule in scripts/build_analysis_table.py
```

The second statement is reconstructable; the first is not.

## 6. Classify mapping changes

When the mapping record changes, ask what kind of change occurred.

| Change | Example | Consequence |
|---|---|---|
| source-label change | `gaze_x_px` renamed to `x_screen_px` with identical values/meaning | mapping provenance changes; scientific semantics may remain unchanged |
| source-version change | new corrected export | source identity changes; rerun construction and structural preflight |
| unit-label clarification | undocumented “time” confirmed as milliseconds without data transformation | provenance improves; verify that prior interpretation used the same unit |
| actual unit conversion | seconds multiplied by 1000 | preprocessing record changes; rebuild downstream provenance |
| coordinate transform | normalized coordinates converted to pixels | spatial representation changes; rerun geometry-dependent analyses |
| participant/trial remapping | analysis-unit identifier redefined | canonical grouping semantics change; rerun structural and downstream analyses |
| row-order repair | rows sorted after documented concatenation defect | canonical study representation changes; rerun structural preflight |
| scientific exclusion | rows/trials/participants removed | not merely mapping provenance; record separately as a researcher decision |

A “small” code diff can be a substantive analytical change. Classify by semantics, not line count.

## 7. Keep mapping provenance separate from QC decisions

The mapping record answers:

> Which source fields and transformations produced this canonical representation?

A structural-QC decision answers:

> What did the researcher decide after observing a flagged structural condition?

Do not collapse these into one field.

For example:

```text
mapping provenance:
  binocular channels combined before canonical table

structural-QC decision:
  repeated timestamp rows retained after confirming simultaneous channel representation
```

The first documents representation construction. The second documents a researcher response to observed evidence.

## 8. Treat missing provenance as missing, not as a guess

The browser builder permits optional source/unit/transformation fields to remain empty.

That is preferable to inventing:

- “pixels” because the numbers look large;
- “milliseconds” because timestamps increase by about 16;
- “trial onset” because time begins near zero;
- a vendor coordinate orientation from memory;
- an acquisition rate from row spacing alone.

Unknown provenance is a limitation to resolve or report.

## 9. Store the record beside the analysis inputs

A practical project layout can be:

```text
data/
  canonical-analysis-table.csv
provenance/
  data-mapping.json
  environment.txt
analysis/
  run_audit.py
evidence/
  study-qc/
  specifications.csv
```

The filename is not prescribed. What matters is that the mapping record is versioned with the analysis and points unambiguously to the canonical source identity.

## 10. Review changes before rerunning downstream work

When a mapping record changes:

1. compare the old and new records;
2. identify whether semantics, units, grouping, coordinate system, or row order changed;
3. update the preprocessing/decision record;
4. reconstruct `GazeStudy`;
5. rerun structural preflight;
6. rerun any downstream analysis affected by the changed semantics;
7. do not overwrite the historical record if the old analysis has already supported a manuscript or review response.

The worked [Mapping change audit]({{ '/docs/examples/data-mapping-change-audit/' | relative_url }}) demonstrates these distinctions on synthetic records.

## Mapping-provenance checklist

Before declaring the canonical table stable:

- [ ] source identity is recorded;
- [ ] participant, trial, timestamp, x, and y mappings are explicit;
- [ ] coordinate units are recorded or explicitly unknown;
- [ ] timestamp unit/origin is recorded or explicitly unknown;
- [ ] coordinate convention is recorded when geometry matters;
- [ ] transformations before mapping are described;
- [ ] source-column renames are distinguishable from semantic transformations;
- [ ] structural-QC decisions are stored separately;
- [ ] changes trigger the appropriate reconstruction/preflight/downstream rerun;
- [ ] historical mapping records are preserved when they supported prior outputs.

A complete provenance record improves reconstruction. It does **not** establish that the mapping, preprocessing, or scientific analysis was valid.
