---
title: Troubleshooting GazeAudit
description: Diagnose blocked or failed GazeAudit workflows by symptom, preserve the relevant evidence, and choose the smallest safe repair without rewriting the scientific record.
kicker: Guide · Troubleshooting
page_type: guide
permalink: /docs/guides/troubleshooting/
search_category: Troubleshooting
search_keywords: troubleshoot troubleshooting error exception failed branch failure non finite empty result missing column schema timestamp duplicate import installation dependency AOI grouped model pipeline run_specs revision package validate recovery blocked audit
---

# Troubleshooting GazeAudit

Use this page when a GazeAudit workflow is **blocked, errors, returns an unusable result, or cannot be reconstructed**. Start from the symptom, identify the layer that failed, preserve the evidence, and make the smallest repair that restores the declared analysis.

If the analysis ran but the **decision trail, denominator, interpretation, or archive is scientifically weak**, use [Common audit mistakes and repairs]({{ '/docs/guides/common-audit-mistakes/' | relative_url }}) instead.

<div class="callout warning">
<strong>Repair the failure, not the scientific conclusion.</strong>
Troubleshooting can identify software, schema, execution, and provenance problems. It must not invent a threshold, exclusion, endpoint, specification, or interpretation because the observed result is inconvenient.
</div>

## Fast symptom router

| Symptom | Inspect first | Safe next action | Preserve |
|---|---|---|---|
| `import gazeaudit` fails | Python environment, installed version, interpreter | verify the active interpreter and installation; reinstall the intended release/environment if needed | Python version, GazeAudit version/commit, complete error text |
| A source table cannot be mapped | column names, data types, semantic mapping | correct the import/mapping layer before analysis | original source identity, mapping, corrected canonical representation |
| Structural preflight flags timestamps, identifiers, or coordinates | `audit_study_qc()` issue codes and affected rows/trials | determine whether this is a representation error or a researcher-owned eligibility decision | QC report, source evidence, any repair decision |
| Grouped AOI/error modelling cannot resolve a group | grouping key and validation-model coverage | repair the group mapping or validation evidence; do not silently pool groups | group key, missing groups, model provenance |
| `run_specs()` stops on one branch | declared specification, `valid_if`, traceback, endpoint inputs | classify whether the branch was invalid before execution or a valid technical failure | full declared space, valid denominator, failing spec, traceback |
| Endpoint returns `NaN`, `inf`, or cannot produce a scalar | endpoint inputs, empty groups/cells, preprocessing output | diagnose why the declared endpoint is undefined; do not reinterpret it as zero | branch identity, intermediate counts, non-finite value/error |
| Fewer result rows exist than expected | declared space size, validity predicate, execution log | reconcile **declared → valid → successful** counts | rejected combinations, failed valid branches, successful rows |
| A robustness summary looks surprising | complete results, endpoint identity, branch statuses | inspect completeness and endpoint consistency before interpretation | branch-level results and failure ledger |
| Revision-package validation fails | validator message and named file/schema | repair the structural package field/file named by the validator | original validation output, corrected file, software identity |
| The analysis ran but the manuscript/archive is hard to defend | decision log, output bundle, denominator, claims | switch to the research-record troubleshooting guide | original decisions, amendments, complete evidence bundle |

## First identify the failure layer

A useful diagnostic order is:

1. **environment** — can the intended Python/GazeAudit installation be imported?
2. **source and schema** — is the canonical table identifiable and mapped correctly?
3. **structural preflight** — are there non-finite values, missing identifiers, duplicate/decreasing timestamps, or similar data-shape conditions?
4. **measurement layer** — are AOIs, error models, validation groups, and required mappings defined for the observations being analysed?
5. **specification execution** — which declared combinations are valid, and which valid branches actually execute?
6. **endpoint** — does every successful branch return the same finite scalar scientific quantity?
7. **interpretation** — is the complete denominator known before summarising direction or magnitude?
8. **revision/publication provenance** — can the evidence package be structurally reconstructed?

Do not jump directly from an exception to a new scientific rule. First determine **which layer failed**.

## 1. Installation or import failure

Record the interpreter and package identity before changing the environment:

```bash
python --version
python -m pip show gazeaudit
python -c "import sys; print(sys.executable)"
python -c "import gazeaudit; print(gazeaudit.__version__)"
```

For the archived public release:

```bash
python -m pip install "gazeaudit==0.1.0"
```

Optional integrations have their own dependency requirements. Do not diagnose a missing optional package as a failure of the core package. See [Interoperability]({{ '/docs/guides/interoperability/' | relative_url }}) for the responsibility boundary.

### Preserve

- exact Python version;
- exact GazeAudit version or Git commit;
- interpreter path;
- installation command;
- complete exception text.

## 2. Canonical-table or schema failure

Map source columns explicitly rather than renaming blindly until the code runs:

```python
import pandas as pd
from gazeaudit import GazeStudy, audit_study_qc

frame = pd.read_csv("my_eye_tracking_export.csv")
study = GazeStudy(
    frame,
    x="gaze_x_px",
    y="gaze_y_px",
    timestamp="time_ms",
    participant="participant_id",
    trial="trial_id",
)
report = audit_study_qc(study)
print(report.status, report.issue_codes)
```

A mapping error is a representation problem. A scientifically motivated exclusion is a researcher decision. Keep those layers separate.

Continue with [Data onboarding and structural preflight]({{ '/docs/guides/data-onboarding/' | relative_url }}).

## 3. Structural-QC flag does not automatically mean “exclude”

A structural preflight can identify conditions such as non-finite coordinates, missing identifiers, duplicate timestamps, or decreasing within-trial time. The diagnostic says **what was observed**, not whether the participant or trial is scientifically unusable.

When a repair is genuinely a source-representation correction:

1. preserve the original source identity;
2. record the affected rows/trials;
3. document the transformation;
4. create a new canonical representation rather than silently mutating the archived source;
5. rerun structural preflight;
6. preserve before/after provenance.

If the proposed action changes scientific eligibility, use [Analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}) rather than treating it as a technical fix.

## 4. Grouped measurement model cannot resolve a group

Grouped models require the observations being analysed to map to the declared grouping information. A missing group should not silently fall back to a pooled model simply because pooling produces output.

Check:

- exact group-key values on the analysis rows;
- exact group-key values in the validation/model record;
- missing or inconsistent labels;
- whether the scientific design really supports grouping at that level.

If coverage is incomplete, repair the mapping/evidence or stop the grouped analysis. Do not alter the grouping strategy merely to recover a preferred estimate.

See [AOI uncertainty]({{ '/docs/guides/aoi-uncertainty/' | relative_url }}).

## 5. A declared specification fails during execution

`PipelineSpace.enumerate_specs()` can reject combinations with a `valid_if` predicate **before execution**. `run_specs()` then evaluates the remaining specifications. If a valid branch raises while executing, `run_specs()` propagates that failure rather than silently deleting the branch.

That distinction is important:

| Status | Denominator treatment |
|---|---|
| invalid by a predeclared scientific/structural rule | not in the valid execution denominator |
| valid and successful | in the valid denominator and successful count |
| valid but technical failure | **in the valid denominator**, not in the successful count |
| not run for an external reason | preserve explicitly; do not silently classify as invalid |

For diagnosis, first enumerate the valid space:

```python
valid_specs = space.enumerate_specs(valid_if=valid_if)
print("valid denominator:", len(valid_specs))
```

Then record the exact failing specification and exception before changing code.

The companion [failed-audit recovery example]({{ '/docs/examples/failed-audit-recovery/' | relative_url }}) shows a synthetic `6 successful / 7 valid` run and a provenance-preserving repair. Use the [Execution Ledger & Recovery Center]({{ '/docs/execution-ledger/' | relative_url }}) when you need a stable documentation-side state vocabulary and linked attempt records across failure, repair, and rerun.

## 6. Endpoint is non-finite or undefined

A non-finite endpoint is **not a null effect**.

Inspect the endpoint inputs for the failing branch:

- did filtering produce an empty group or condition?
- is a required contrast absent?
- did a denominator become zero?
- did an earlier transformation introduce non-finite values?
- is the returned object actually the same scalar endpoint used by other branches?

Preserve the branch status as failed/undefined until the cause is understood. Do not replace `NaN` with zero unless zero is independently the scientifically defined value—which is a different decision and must be justified as such.

## 7. Expected and observed specification counts differ

Reconcile three numbers explicitly:

```text
declared combinations
→ valid combinations after predeclared validity rules
→ successful endpoint estimates after execution
```

Example:

```text
8 declared
7 valid
6 successful
```

Report that as **6 successful / 7 valid**, with one invalid combination documented separately. Do not report `6 / 6` by deleting the failed valid branch and do not report `6 / 8` as though the predeclared invalid branch were an execution failure.

Use [Specification spaces]({{ '/docs/guides/specification-space/' | relative_url }}) for declaration/validity rules and [Common audit mistakes]({{ '/docs/guides/common-audit-mistakes/' | relative_url }}) for denominator-governance failures.

## 8. Revision-package validation fails

The `gazeaudit-revision-package` validator checks **structural provenance**, not scientific correctness. Run it directly so the failure message identifies the affected package component:

```bash
gazeaudit-revision-package validate --root revision-package
```

Repair the missing/invalid structural field or file named by the validator, retain the original validation output when useful for the audit trail, then validate again.

A successful validator result does **not** establish that the reviewer request, endpoint, analysis, interpretation, or manuscript is scientifically valid. See the [revision-package quickstart]({{ '/docs/examples/revision-package-quickstart/' | relative_url }}).

## Collect evidence before changing anything

For a reproducible troubleshooting record, capture as much of the following as applies:

```text
software:
  python: <version>
  gazeaudit: <release or commit>
source:
  canonical_file: <path or identifier>
  source_fingerprint: <if available>
analysis:
  endpoint_id: <stable endpoint name>
  declared_specifications: <count>
  valid_specifications: <count>
failure:
  spec_id: <if applicable>
  status: <technical_failure | non_finite | missing_data | not_run | ...>
  exception: <complete message>
  affected_counts: <rows/trials/participants/groups if relevant>
repair:
  change: <smallest technical correction>
  scientific_rule_changed: false
  rerun_scope: <which branch or workflow was rerun>
```

Do not include participant-level confidential data in a public bug report. Prefer schema, minimal synthetic reproductions, aggregate counts, version information, and redacted error traces when those are sufficient.

## Safe repair sequence

1. **Freeze the failure evidence.** Save the exception/status and exact branch/input identity.
2. **Classify the layer.** Environment, source/schema, QC, measurement, execution, endpoint, interpretation, or package structure.
3. **Separate validity from execution.** Was the branch invalid before execution, or valid but failed technically?
4. **Make the smallest causal fix.** Do not alter unrelated scientific choices.
5. **Rerun the affected scope.** Prefer the same declared branch/input when testing the repair.
6. **Retain history.** Keep the original failure record alongside the repaired execution record.
7. **Reconcile denominators.** Report declared, valid, successful, and failed counts consistently.
8. **Rebuild downstream summaries.** Only after the execution record is complete enough for the intended interpretation.

## When troubleshooting should stop

Stop and return to scientific governance when the “fix” would require deciding:

- which threshold is acceptable;
- which participant or trial should be excluded;
- which endpoint is preferable;
- which specification should count as defensible;
- which missing-data assumption is scientifically appropriate;
- whether a reviewer request should be accepted;
- what substantive conclusion the evidence supports.

Those are researcher-owned decisions. GazeAudit can preserve and audit them, but troubleshooting must not manufacture them.

## Related routes

- [Failed-audit recovery worked example]({{ '/docs/examples/failed-audit-recovery/' | relative_url }}) — synthetic break → diagnose → repair → reconcile exercise.
- [Common audit mistakes and repairs]({{ '/docs/guides/common-audit-mistakes/' | relative_url }}) — when execution ran but the research record is weak.
- [Data onboarding]({{ '/docs/guides/data-onboarding/' | relative_url }}) — source mapping and structural preflight.
- [Analysis readiness]({{ '/docs/guides/analysis-readiness/' | relative_url }}) — researcher-owned eligibility policy and cohort impact.
- [Specification spaces]({{ '/docs/guides/specification-space/' | relative_url }}) — valid combinations and common endpoint execution.
- [Audit output bundle]({{ '/docs/guides/audit-output-bundle/' | relative_url }}) — what evidence should survive execution.
- [What should I do next?]({{ '/docs/guides/what-next/' | relative_url }}) — return to the project-stage route after the block is resolved.

## Frozen evidence boundary

Troubleshooting does not change the frozen validation programme. GazeBase remains `incomplete`, Korthals remains `robust_negative`, and Pedrotti/de Chambrier remains `materially_fragile`. Those are protocol-bound records, not diagnostic labels for a new failed run.