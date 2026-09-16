---
title: Common audit mistakes and repairs
description: Recognise common robustness-audit failure patterns, understand why they weaken the record, and repair the workflow without hiding inconvenient evidence.
kicker: Guide · Research practice
permalink: /docs/guides/common-audit-mistakes/
search_category: Guide
search_keywords: mistakes pitfalls repair specification cherry picking failures endpoint drift exclusions interpolation reporting archive provenance
---

# Common audit mistakes and repairs

A technically reproducible analysis can still have a weak scientific record. The most damaging failures usually occur **around** execution: choices are declared too late, failed branches disappear, endpoints drift, QC decisions become undocumented exclusions, or a descriptive robustness summary is reported as if it were inferential uncertainty.

This guide is a troubleshooting layer for those situations. It does not decide which scientific choices are defensible. It shows how to keep the decision trail, executed evidence, and reporting boundary inspectable.

<div class="callout warning">
<strong>Repair the record, not the result.</strong>
A repair should make the history more explicit. It should not retroactively redefine the specification space, endpoint, exclusions, or interpretation rule to make the observed pattern look stronger.
</div>

## Fast diagnostic

| Failure pattern | Why it weakens the audit | Repair | Preserve |
|---|---|---|---|
| Specification space defined after results are inspected | Outcome knowledge can shape which alternatives appear “defensible” | Freeze the original set; add any later choices as dated amendments | Decision log + original specification declaration |
| Failed branches silently disappear | Completeness becomes unknowable and surviving branches may be selective | Keep a failure record with branch identity and reason | Full specification inventory + failure status |
| Endpoint changes across branches | Estimates no longer answer the same scientific question | Hold the endpoint fixed or define endpoint variation as an explicit factor before execution | Endpoint definition + factor table |
| QC flags become undocumented exclusions | Structural diagnostics are confused with scientific eligibility decisions | Record the researcher decision separately from the diagnostic | QC artifact + decision log + cohort impact |
| Interpolation or missingness repair is implicit | The analysis hides a consequential preprocessing choice | Declare the rule, scope, timing, and sensitivity check where relevant | Repair rule + provenance + sensitivity output |
| Robustness summaries are called confidence intervals or probabilities | Descriptive across-specification variation is given an inferential meaning it does not have | Report exactly what the summary measures | Complete results + reporting rule |
| Decision history is rewritten | Readers cannot distinguish pre-result decisions from later amendments | Append amendments; do not overwrite the original declaration | Original record + dated amendment |
| Only a preferred branch is archived | The publication record cannot show the declared analytical space | Archive complete branch-level evidence and summaries | Specification table + bundle + fingerprints |
| A case-study label is transferred to a new dataset | A protocol-bound result is treated as a universal method property | Describe the new audit on its own evidence and protocol | New-data results + protocol boundary |

## 1. Defining the specification space after seeing the outcome

### Problem

A researcher inspects one or more estimates, then decides which alternative thresholds, preprocessing choices, AOI settings, or model variants count as the “reasonable” robustness set.

The problem is not that a later idea can never be scientifically useful. The problem is that the timing becomes invisible, so the final specification space can look predeclared when it was outcome-informed.

### Repair

1. Preserve the original declaration unchanged.
2. Mark the later choice as an amendment.
3. Record whether results had already been inspected.
4. Explain why the amendment was scientifically necessary.
5. Keep original and amended analyses distinguishable in reporting.

Use the [audit decision log template]({{ '/docs/guides/audit-decision-log-template/' | relative_url }}) rather than rewriting history.

## 2. Silently removing failed specifications

### Problem

A branch errors, returns non-finite output, violates a predeclared validity rule, or cannot be executed. It is then removed from the results table with no retained trace.

That turns a computational event into invisible selection. A reader cannot tell whether the reported robustness pattern covers the declared space or only the branches that happened to survive.

### Repair

Keep branch identity and status separate from the effect estimate. Distinguish at least:

- valid and executed;
- invalid by a **predeclared** rule;
- technical failure;
- unavailable because required data were absent;
- not run, with an explicit reason.

Do not backfill a missing result with a favourable neighbouring branch. If completeness matters to the scientific rule, evaluate completeness explicitly.

## 3. Letting the scientific endpoint drift

### Problem

One branch reports dwell-time difference, another reports fixation count, and a third changes the comparison population. They are then placed on one “robustness” curve as if they were alternative estimates of the same target.

### Repair

Hold the scientific endpoint fixed across branches. If endpoint choice itself is a legitimate uncertainty dimension, declare it as a factor and avoid interpreting the resulting estimates as directly interchangeable when their scales or scientific meanings differ.

Before execution, write down:

- outcome variable;
- unit/scale;
- contrast;
- population/unit of analysis;
- sign convention;
- aggregation level.

## 4. Turning structural QC into an undocumented exclusion rule

### Problem

A structural diagnostic flags missing coordinates, ordering problems, duplicate timestamps, or another data condition. Rows or participants are then removed automatically, even though the diagnostic itself did not establish scientific invalidity.

### Repair

Keep **diagnosis** and **researcher decision** separate. Preserve the structural-QC evidence, then record what action was taken and why. Where the decision changes the analyzable cohort, preserve cohort impact.

Use [data onboarding]({{ '/docs/guides/data-onboarding/' | relative_url }}) and [analysis-readiness governance]({{ '/docs/guides/analysis-readiness/' | relative_url }}) for the separation between structural conditions and scientific eligibility.

## 5. Hiding interpolation, imputation, or missingness repair

### Problem

Missing samples are interpolated or repaired because a downstream function requires complete input, but the rule is absent from the scientific record.

### Repair

Record:

- what was repaired;
- the algorithm/rule;
- limits on gap size or scope;
- whether the rule was fixed before result inspection;
- how much data were affected;
- any sensitivity analysis that tests whether the repair matters.

A convenient technical fix is still an analytical choice when it can change the endpoint.

## 6. Treating descriptive robustness variation as inferential uncertainty

### Problem

The range, sign fraction, specification curve, or marginal sensitivity across analytical choices is called a confidence interval, posterior probability, p-value, or causal effect of the choice.

### Repair

Name the quantity for what it is. For example:

- “Across the 12 declared specifications, estimates ranged from … to …”
- “Four of 12 specifications were positive, four negative, and four zero.”
- “Estimates differed across the declared factor levels.”

Those statements describe the executed specification set. They do **not** by themselves quantify sampling uncertainty, posterior uncertainty, or causal attribution.

Use the [decision-to-report example]({{ '/docs/examples/decision-to-report/' | relative_url }}) for a complete synthetic interpretation exercise.

## 7. Rewriting the decision history

### Problem

After an unexpected result, the project’s decision document is edited so the final choice appears to have been the original choice.

### Repair

Append; do not overwrite. A useful amendment records:

- date/version;
- original decision;
- new decision;
- reason;
- whether relevant outputs had been inspected;
- which analyses are affected.

A transparent amendment is stronger evidence than an artificially clean history.

## 8. Archiving the preferred result instead of the audit

### Problem

The final archive contains one selected result table or figure but not the specification inventory, failures, robustness summaries, decision record, source/provenance information, or software identity.

### Repair

Treat publication as a handoff of the **research record**, not a screenshot of the preferred result. At minimum, preserve the inputs needed to understand:

1. what was fixed;
2. what was allowed to vary;
3. what actually ran;
4. what failed;
5. what pattern was observed;
6. what reporting rule was used;
7. which software/source identities generated the evidence.

See the [publication/archive handoff example]({{ '/docs/examples/publication-archive-handoff/' | relative_url }}) for an illustrative end state.

## 9. Transferring a frozen case-study label to new data

### Problem

A new analysis uses the same method family as one of GazeAudit's frozen cases and inherits the case label (`incomplete`, `robust_negative`, or `materially_fragile`) without executing the corresponding protocol on the new evidence.

### Repair

Treat frozen case-study outcomes as **protocol-bound records**, not reusable ratings. A new dataset requires its own source binding, specification, execution, evidence, and scoped interpretation.

The authoritative frozen outcomes remain in the [evidence overview]({{ '/docs/case-studies/' | relative_url }}); this guide does not redefine or generalise them.

## Before calling the repair complete

Ask five questions:

- Can a collaborator see which decisions predated outcome inspection?
- Can every declared branch be accounted for, including failures?
- Is the scientific endpoint stable or explicitly factored?
- Can the manuscript wording be traced to preserved evidence?
- Could another researcher distinguish what the audit **showed** from what it **did not establish**?

If any answer is no, use the [researcher checklist]({{ '/docs/guides/researcher-audit-checklist/' | relative_url }}), [audit record map]({{ '/docs/guides/audit-record-map/' | relative_url }}), and [output-bundle guide]({{ '/docs/guides/audit-output-bundle/' | relative_url }}) before publication.
