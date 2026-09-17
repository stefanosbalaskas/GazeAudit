---
title: Peer-review revision checklist
description: Compact reviewer-revision checklist for classifying requests, preserving submitted and post-review evidence, aligning manuscript and response records, validating the revision package, and completing the final handoff.
kicker: Guide · Peer review
permalink: /docs/guides/peer-review-revision-checklist/
search_category: Guides
search_keywords: reviewer revision checklist response amendment correction endpoint reanalysis provenance denominator package resubmission handoff
---

# Peer-review revision checklist

Use this checklist when a manuscript has entered peer review and you need a **compact operational gate** before changing analyses, editing the response letter, or assembling the final resubmission package.

<div class="callout warning">
<strong>Revision extends the evidence history; it does not rewrite submission history.</strong>
A reviewer-requested analysis performed after outcomes were inspected remains post-review evidence. Keep the submitted denominator, post-review denominator, endpoint, timing, failures, and superseded records identifiable throughout the revision.
</div>

## 1. Classify the reviewer request before acting

| Reviewer request | Record it as | Minimum provenance to preserve |
|---|---|---|
| Clarify wording, denominator, method, or interpretation without rerunning analysis | `documentation_clarification` | reviewer item, response text, manuscript location, archive location |
| Repeat or extend analysis under another defensible threshold, exclusion, specification, or sensitivity setting | `sensitivity_amendment` or `analytical_amendment` | timing, submitted denominator, post-review denominator, specification set, execution status |
| Add a different scientific outcome | `endpoint_amendment` | original endpoint record, new endpoint identity, separate denominator, manuscript location |
| Change a measurement model or measurement assumption | `measurement_amendment` | prior measurement record, new assumption/model, timing, affected endpoint evidence |
| Repair a coding, import, data-processing, or analytical defect | `correction` | superseded evidence, defect description, regenerated outputs, affected claims, replacement evidence |

Do not classify a new analysis as a clarification merely because its result agrees with the submitted analysis.

## 2. Before touching the analysis

- [ ] Give the reviewer item a stable identifier such as `R1-C4`.
- [ ] Record whether the relevant outcomes had already been inspected.
- [ ] Preserve the submitted endpoint and execution denominator exactly as they stood at submission.
- [ ] State the reviewer-requested change before running the new analysis.
- [ ] Keep endpoint changes outside the submitted endpoint denominator.
- [ ] Decide how valid technical failures will be represented before execution.
- [ ] Record the GazeAudit version or exact commit used for the amendment.

A submitted `8 / 8` audit followed by a reviewer-requested `4 / 4` amendment remains **8 / 8 submitted + 4 / 4 post-review**. Do not rewrite it as “12 pre-specified analyses.”

## 3. While running a post-review amendment

For every amendment, preserve:

1. the reviewer item that triggered it;
2. the amendment category;
3. whether outcomes were already seen;
4. the endpoint being estimated;
5. the valid amendment denominator;
6. successful and failed valid branches;
7. the amendment-specific execution status;
8. the generated evidence location;
9. the software identity used for execution.

If four amendment branches are valid and only three execute successfully, report **3 / 4 with one unresolved valid failure**. Do not silently reduce the denominator to `3 / 3`.

## 4. If review exposes a correction

A correction requires a supersession trail rather than a clean replacement.

- [ ] Keep the superseded evidence available.
- [ ] Record the defect and when it was discovered.
- [ ] Identify every affected file and manuscript claim.
- [ ] Regenerate materially affected outputs.
- [ ] Link superseded and corrected evidence in the version-change manifest.
- [ ] State which conclusions changed and which did not.
- [ ] Do not use package validation as evidence that the corrected scientific analysis is valid.

The archive should explain **why** the corrected record exists.

## 5. Align response letter, manuscript, and archive

For each reviewer item, verify that all three surfaces agree on:

| Check | Response letter | Revised manuscript | Archive |
|---|---|---|---|
| Request category | named explicitly | reflected in wording/method | encoded in response/change records |
| Timing | submitted vs post-review stated | no retrospective pre-specification language | temporal layer preserved |
| Endpoint | same endpoint name | same endpoint interpretation | endpoint-specific evidence path |
| Denominator | submitted and post-review separated | matching execution statement | matching response/amendment records |
| Failures | unresolved failures visible | limitations/results consistent | failed valid branches retained |
| Correction | supersession explained | corrected claims identified | superseded evidence preserved |

If those records disagree, stop the handoff and repair the inconsistency before final submission.

## 6. Build and validate the revision package

Create the governed scaffold:

```bash
gazeaudit-revision-package init \
  --output-dir revision-package \
  --project-slug my-study \
  --review-round 1
```

Populate the reviewer-response matrix, version-change manifest, amendment folders, endpoint-amendment folders, editor-facing evidence map, and software identity. Then run:

```bash
gazeaudit-revision-package validate --root revision-package
```

A successful validation confirms **structural provenance only**: required scaffold paths are present and the deterministic package manifest remains internally consistent. It does not establish analytical validity, robustness, manuscript quality, or publication readiness.

For a short runnable walkthrough, use the [revision-package quickstart]({{ '/docs/examples/revision-package-quickstart/' | relative_url }}). For the deliberate break → detect → repair exercise, use the [full CLI worked example]({{ '/docs/examples/reproducibility-package-cli/' | relative_url }}).

## 7. Five final resubmission questions

Before handing the revision to a coauthor, editor, or archive, answer **yes** to all five:

1. Can an outsider distinguish what existed at submission from what was added after review?
2. Can every analytical reviewer item be traced to its own denominator and evidence location?
3. Do the response letter and revised manuscript use the same endpoint, timing, and execution language?
4. Are corrections, failures, and superseded evidence still visible rather than cleaned away?
5. Does the final evidence map point from the revised claim back to the correct temporal evidence layer?

If not, continue with [resubmission readiness and editor handoff]({{ '/docs/guides/resubmission-readiness/' | relative_url }}).

## Recommended revision route

1. [Peer-review revision toolkit]({{ '/docs/workspace/revision-toolkit/' | relative_url }}) — choose the task.
2. **Peer-review revision checklist** — classify and preserve the revision record.
3. [Reviewer-requested amendments]({{ '/docs/guides/reviewer-requested-amendments/' | relative_url }}) — govern new analysis.
4. [Reviewer response letter]({{ '/docs/guides/reviewer-response-letter/' | relative_url }}) — bind response wording to evidence.
5. [Revision reproducibility package]({{ '/docs/guides/reproducibility-package/' | relative_url }}) — scaffold and structurally validate the record.
6. [Resubmission readiness]({{ '/docs/guides/resubmission-readiness/' | relative_url }}) — run the final handoff gate.

## Evidence boundary

This checklist is **revision-governance guidance**, not a scientific scoring system. It does not decide whether a reviewer request is justified, whether a model is appropriate, whether an effect is robust, whether a manuscript should be accepted, or whether editorial acceptance validates the underlying result. The frozen GazeAudit case-study outcomes remain unchanged and protocol-bound.