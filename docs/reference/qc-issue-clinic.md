---
title: Structural QC Issue Clinic
description: Look up every implemented GazeAudit structural-QC issue code, diagnostic detail code, inspection route, interpretation boundary, and next-step guidance without turning flags into automatic exclusions.
kicker: Reference · Structural QC
page_type: qc-issue-clinic
permalink: /docs/reference/qc-issue-clinic/
search_category: Reference
search_keywords: structural qc issue clinic coordinate_nonfinite timestamp_nonfinite identifier_missing timestamp_duplicate timestamp_decreasing diagnostics detail codes review exclusion
---

# Structural QC Issue Clinic

Use this page after `audit_study_qc()` returns `status == "review"` or when you need to interpret a row/group emitted by `study_qc_diagnostics()`.

<div class="callout warning">
<strong>An issue code is an observation, not a verdict.</strong>
GazeAudit reports structural conditions that deserve inspection. It does not infer their cause, silently repair them, assign a universal severity score, or convert them into automatic row/trial/participant exclusions.
</div>

The governed catalog below is the documentation authority for the five currently implemented issue families. CI regression tests bind it to the live diagnostic output so a runtime change cannot silently leave the clinic stale.

<div class="qc-clinic-summary">
  <strong>{{ site.data.qc_issues | size }} structural issue families</strong>
  <span>All cards remain visible when JavaScript is unavailable.</span>
</div>

<form class="qc-clinic-controls" data-qc-clinic-controls role="search" aria-label="Filter structural QC issue clinic">
  <label>
    <span>Search issue codes and guidance</span>
    <input
      type="search"
      autocomplete="off"
      placeholder="Try “duplicate”, “x_missing”, or “trial”…"
      data-qc-clinic-search
    >
  </label>
  <label>
    <span>Diagnostic scope</span>
    <select data-qc-clinic-scope>
      <option value="">All scopes</option>
      <option value="row">Row-level</option>
      <option value="group">Group-level</option>
    </select>
  </label>
  <button type="button" data-qc-clinic-clear>Clear filters</button>
</form>

<p class="qc-clinic-status" data-qc-clinic-status role="status" aria-live="polite" aria-atomic="true">
  Showing all {{ site.data.qc_issues | size }} issue families.
</p>

<div class="qc-clinic-grid" data-qc-clinic>
{% for issue in site.data.qc_issues %}
  {% capture detail_search %}{% for detail in issue.detail_codes %}{{ detail.code }} {{ detail.meaning }} {% endfor %}{% endcapture %}
  {% capture inspect_search %}{% for item in issue.inspect %}{{ item }} {% endfor %}{% endcapture %}
  {% capture cause_search %}{% for item in issue.possible_causes %}{{ item }} {% endfor %}{% endcapture %}
  <article
    class="qc-clinic-card"
    id="issue-{{ issue.issue_code }}"
    data-qc-issue
    data-qc-scope="{{ issue.scope }}"
    data-qc-search="{{ issue.issue_code }} {{ issue.label }} {{ issue.report_field }} {{ issue.summary }} {{ detail_search }} {{ inspect_search }} {{ cause_search }} {{ issue.not_infer }} {{ issue.next_step | downcase | escape }}"
  >
    <div class="qc-clinic-badges">
      <code>{{ issue.issue_code }}</code>
      <span>{{ issue.scope }} scope</span>
      <span>report: <code>{{ issue.report_field }}</code></span>
    </div>

    <h2>{{ issue.label }}</h2>
    <p>{{ issue.summary }}</p>

    <h3>Diagnostic details</h3>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Detail code</th>
            <th>Meaning</th>
          </tr>
        </thead>
        <tbody>
        {% for detail in issue.detail_codes %}
          <tr>
            <td><code>{{ detail.code }}</code></td>
            <td>{{ detail.meaning }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>

    <details>
      <summary>What to inspect</summary>
      <ul>
      {% for item in issue.inspect %}
        <li>{{ item }}</li>
      {% endfor %}
      </ul>
    </details>

    <details>
      <summary>Common representation causes</summary>
      <ul>
      {% for item in issue.possible_causes %}
        <li>{{ item }}</li>
      {% endfor %}
      </ul>
    </details>

    <div class="qc-clinic-boundary">
      <strong>Do not infer</strong>
      <p>{{ issue.not_infer }}</p>
    </div>

    <div class="qc-clinic-next">
      <strong>Researcher-owned next step</strong>
      <p>{{ issue.next_step }}</p>
    </div>
  </article>
{% endfor %}
</div>

<div class="qc-clinic-empty" data-qc-clinic-empty hidden>
  <h2>No issue family matches these filters</h2>
  <p>Clear the filters, use the site-wide search with <strong>Ctrl/Cmd + K</strong>, or inspect the complete structural-QC guide.</p>
</div>

## Read the layers in the right order

A structural preflight has several different outputs. They answer different questions:

| Layer | Example | What it tells you | What it does not tell you |
|---|---|---|---|
| status | `review` | at least one implemented structural condition was detected | that the dataset is invalid |
| issue family | `timestamp_duplicate` | which class of structural condition occurred | why it occurred |
| report field | `duplicate_timestamp_rows` | how many rows participate in that condition | how many scientific events are invalid |
| diagnostic detail | `x_missing` | the specific row/group condition | the appropriate repair or exclusion |
| researcher decision | free-text action + rationale | what the study team decided after inspection | a package-wide recommendation |
| readiness policy | researcher-declared thresholds | whether a table/cohort satisfies that declared policy | universal scientific quality |

Do not skip directly from `status == "review"` to filtering.

## Minimal inspection sequence

```python
from gazeaudit import audit_study_qc, study_qc_diagnostics

report = audit_study_qc(study)
diagnostics = study_qc_diagnostics(study)

print(report.status)
print(report.issue_codes)
print(
    diagnostics[
        [
            "diagnostic_id",
            "scope",
            "issue_code",
            "detail_code",
            "row_position",
            "participant",
            "trial",
            "timestamp",
        ]
    ]
)
```

Then connect each diagnostic back to the source/mapping provenance before deciding whether the condition is a valid representation, a repairable construction problem, a study-specific exclusion issue, or an unresolved limitation.

## Record the decision instead of deleting the evidence

When an issue has been inspected, `StudyQCDecision` and `build_study_qc_audit()` let you bind the action and rationale to the diagnostic record.

```python
from gazeaudit import StudyQCDecision, build_study_qc_audit

decision = StudyQCDecision(
    issue_code="timestamp_duplicate",
    action="retain after representation review",
    rationale="Rows are simultaneous channel records in the declared source representation.",
    diagnostic_ids=("D000001", "D000002"),
)

audit = build_study_qc_audit(study, decisions=(decision,))
```

The action above is an illustration, not a default. The correct action depends on the source representation, acquisition protocol, preprocessing history, endpoint, and study-owned decision rules.

## If you change the table

A repair that changes mapped coordinates, time, participant/trial identifiers, or row order changes the canonical study representation.

After a repair:

1. preserve the pre-repair evidence if it supported an earlier analysis;
2. update the [data-mapping provenance]({{ '/docs/guides/data-mapping-provenance/' | relative_url }});
3. rebuild `GazeStudy`;
4. rerun `audit_study_qc()` and `study_qc_diagnostics()`;
5. create a new decision/audit record;
6. rerun downstream analyses affected by the change.

Do not reuse old diagnostic IDs after changing the audited representation.

## Interpretation and reporting

A defensible Methods statement describes **what was checked and how decisions were governed**, not merely that “data quality was checked.”

> Structural preflight evaluated non-finite gaze coordinates and timestamps, missing canonical identifiers, duplicate participant × trial timestamps, and decreasing within-unit time. Flagged conditions were inspected against source and preprocessing provenance; any repair, retention, or exclusion decision was recorded explicitly rather than applied automatically.

A Results statement should report the observed scope and preserve the denominator. For example:

> Structural preflight returned `review` because duplicate timestamps and non-finite coordinates were present. The affected rows/units were inspected using row/group diagnostics, and the resulting decisions were retained in the structural-QC audit record.

Replace the issue families and counts with the study's actual record. Do **not** copy numerical values from synthetic examples.

If a condition remains unresolved, say so. An unresolved limitation is preferable to a fabricated repair or an unexplained exclusion.

## API routes

Use the source-level API pathways for exact current signatures and source links:

- [`GazeStudy`]({{ '/docs/reference/api-pathways/#api-gazestudy' | relative_url }})
- [`audit_study_qc()`]({{ '/docs/reference/api-pathways/#api-audit-study-qc' | relative_url }})
- [`study_qc_diagnostics()`]({{ '/docs/reference/api-pathways/#api-study-qc-diagnostics' | relative_url }})
- [`build_study_qc_audit()`]({{ '/docs/reference/api-pathways/#api-build-study-qc-audit' | relative_url }})
- [Structural-QC method pathway]({{ '/docs/reference/api-pathways/#path-structural-qc' | relative_url }})
- [Machine-readable QC issue catalog]({{ '/assets/qc-issue-reference.json' | relative_url }})

## Continue from here

- [Structural-QC triage guide]({{ '/docs/guides/structural-qc-triage/' | relative_url }}) — step-by-step inspection, decision, repair, rerun, and reporting workflow.
- [All structural-QC issues worked example]({{ '/docs/examples/all-structural-qc-issues/' | relative_url }}) — one synthetic fixture exercising all five issue families and all ten detail codes.
- [Data onboarding and structural preflight]({{ '/docs/guides/data-onboarding/' | relative_url }}) — full provenance and artifact workflow.
- [Analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}) — apply researcher-declared thresholds only after structural evidence is understood.
