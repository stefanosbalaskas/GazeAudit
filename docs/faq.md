---
title: FAQ
description: Common questions about GazeAudit installation, scientific scope, uncertainty, robustness, validation, and reproducibility.
kicker: Reference
permalink: /docs/faq/
---

# FAQ

## What problem does GazeAudit solve?

GazeAudit asks whether an eye-tracking scientific conclusion survives plausible **measurement uncertainty** and **analytical choices**. It provides uncertainty-aware AOI calculations, specification-space execution, sensitivity diagnostics, and reproducible publication evidence.

## Does GazeAudit replace preprocessing software or fixation detectors?

No. GazeAudit is designed to sit above existing parsing, preprocessing, and detector ecosystems. It can ingest or adapt outputs from Eye-Tracking-BIDS, pymovements, pEYES, and user-defined backends while retaining those tools' methodological responsibility.

## Which Python versions are supported by release 0.1.0?

The release metadata requires Python 3.10 or newer and the repository test matrix covers Python 3.10–3.13. The current pEYES optional dependency is restricted to Python 3.12+.

## How do I install it?

```bash
python -m pip install gazeaudit==0.1.0
```

For pymovements integration:

```bash
python -m pip install "gazeaudit[pymovements]==0.1.0"
```

For pEYES integration on Python 3.12+:

```bash
python -m pip install "gazeaudit[peyes]==0.1.0"
```

## `audit_study_qc()` returned `review`. Does that mean I should exclude data?

No. `review` means that at least one implemented structural condition was detected. Inspect the row/group diagnostics and trace them to source/mapping provenance before deciding what they mean for the study. Use the [Structural QC Issue Clinic]({{ '/docs/reference/qc-issue-clinic/' | relative_url }}) for exact issue/detail-code lookup and [Structural-QC triage]({{ '/docs/guides/structural-qc-triage/' | relative_url }}) for the decision workflow.

A flag is not an automatic imputation, sorting, deduplication, or row/trial/participant exclusion rule.

## Does GazeAudit provide recommended readiness thresholds?

No. Every field in `ReadinessThresholds` is optional and the package deliberately supplies no universal scientific cutoff. Use the [Readiness Policy Design Center]({{ '/docs/readiness-policy/' | relative_url }}) to assemble only criteria justified by your study, and preview the trial/participant cohort consequence before any filtering step.

`ready_under_policy` means the data satisfy the policy you declared; it does not mean universally valid or high-quality data.

## Can I call a result “robust” if most specifications have the same sign?

Not automatically. Direction and magnitude are different properties, and execution completeness comes first. Use the [Results Interpretation & Reporting Center]({{ '/docs/reporting-center/' | relative_url }}) and [claim-boundary reporting guide]({{ '/docs/guides/claim-boundary-reporting/' | relative_url }}) to preserve the valid/successful denominator, describe sign and magnitude separately, and avoid turning descriptive sign fractions into posterior probabilities.

## Is probabilistic AOI membership the probability that the fixation was truly in that AOI?

It is a **model-conditional marginal membership probability**. It describes the fraction of latent true positions sampled under the declared measurement-error model that fall inside the AOI. It should not be interpreted as model-free certainty about the true gaze position.

## Can AOI probabilities sum to more than one?

Yes. GazeAudit allows overlapping AOIs and reports marginal membership probabilities. A latent point can therefore belong to more than one AOI. The optional `outside` column is the probability that a point belongs to none of the supplied AOIs.

## What does `boundary_risk` mean?

In `compare_hard_probabilistic()`, boundary risk rescales binary AOI membership ambiguity to `[0, 1]`. Values near zero indicate membership is essentially certain in or out under the model; values near one correspond to membership probability near 0.5.

Boundary risk is a diagnostic, not a universal exclusion criterion.

## Should I always use a grouped error model?

No. Grouping is appropriate when the study design and validation evidence justify different error models across participants, sessions, calibration blocks, devices, or other predeclared groups. A grouped model also requires complete group mapping; GazeAudit fails closed rather than silently falling back to a pooled model.

## Does using more Monte Carlo draws make the error model more valid?

No. More draws reduce Monte Carlo simulation error under a fixed model. They do not validate the scientific assumptions of that model.

## What is a `PipelineSpace`?

A `PipelineSpace` is a deterministic declaration of analytical choices and their levels. It can represent detector families, QC rules, AOI approaches, missing-data rules, or other defensible decisions. `run_specs()` executes the valid combinations against one common scalar endpoint.

## Does `run_specs()` reject NaN or infinite endpoint values?

No. `run_specs()` converts the endpoint result with `float(...)`, and Python permits `NaN` and infinity as floating-point values. A non-finite endpoint is therefore not automatically rejected, is not a zero/null effect, and should remain visible in the audit record.

If the declared endpoint contract requires finite estimates, enforce that explicitly in the endpoint or audited wrapper. Use the [Endpoint Definition & Handoff Center]({{ '/docs/endpoint-contract/' | relative_url }}) and [endpoint definition guide]({{ '/docs/guides/endpoint-definition/' | relative_url }}) to record that policy before execution.

## Is a specification curve a way to choose the best pipeline?

No. The curve is intended to expose how estimates vary across the complete declared decision space. Selecting the most favourable specification after seeing the curve would undermine the robustness audit.

## What does `effect_stability()` tell me?

It provides descriptive summaries of estimates across specifications: count, mean, median, range, empirical 2.5%/97.5% quantiles, positive/negative/exact-null fractions, and descriptive sign stability. It does not replace a formal inferential model and the sign fractions are not posterior probabilities.

## Are marginal and pairwise sensitivity ratios causal variance decompositions?

No. They are descriptive screening diagnostics. In dependent, incomplete, or unbalanced multiverses, ratios can overlap and need not sum to one.

## What is the difference between a specification space and a sensitivity curve?

A specification space usually represents discrete, scientifically defensible analysis decisions. A sensitivity curve often represents a controlled perturbation dimension such as spatial-error scale, target sampling rate, or added missingness. Keeping those meanings separate makes instability easier to interpret.

## Does `downsample_gaze()` simulate a lower-frequency eye tracker?

No. It retains existing samples nearest an ideal target grid and does not interpolate coordinates. It is a controlled representation perturbation of the recorded stream, not a physical simulation of how another device would have measured the trial.

## What is a `ConclusionRule`?

A `ConclusionRule` is a predeclared recovery criterion that can combine effect-error tolerance, direction recovery, and a minimum across-specification recovery fraction. It is most straightforward in known-truth benchmarks. For real-data analyses, any reference effect must be independently defined and justified; GazeAudit does not infer it.

## What are the three canonical validation outcomes?

Under their frozen protocols:

- GazeBase multi-detector audit: `incomplete`;
- Korthals target-tracking AOI audit: `robust_negative`;
- Pedrotti/de Chambrier sampling + missingness audit: `materially_fragile`.

These labels are **protocol-bound scientific records**, not generic claims about the underlying datasets or every possible endpoint. See the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) for authoritative scope and provenance.

## Is a fragile result a failure?

No. A fragile result shows that the conclusion depends materially on at least one declared uncertainty or analytical dimension. The appropriate response is to localise that dependence, narrow claims when needed, and identify what should be measured or validated next.

## What does `incomplete` mean for GazeBase?

It means the frozen detector specification space did not satisfy its predeclared completeness gate. It should not be rewritten as a generic negative verdict about GazeBase.

## How should I cite GazeAudit 0.1.0?

Use the version-specific Zenodo DOI for a reproducible release citation:

`10.5281/zenodo.22757340`

The concept DOI `10.5281/zenodo.22757339` follows all archived versions and resolves to the latest version.

## Should I cite a version or a Git commit?

For a published release, cite the version DOI and record the exact version used. If your analysis depends on post-release development code, record the exact Git commit as well.

## Does the documentation describe only the immutable 0.1.0 tag?

No. The public site is built from the repository's current `main` branch, so documentation may describe post-release development in addition to the released API. Pages that demonstrate the public release explicitly use `0.1.0`; reproducible research should always record the exact version or commit actually executed.

## Does GazeAudit upload participant data anywhere?

The Python package operates on data in the user's analysis environment. The documentation and repository do not require participant data to be uploaded. Researchers remain responsible for their own data governance, consent, security, and sharing restrictions.

## Where should I start?

Use the [getting-started guide]({{ '/docs/getting-started/' | relative_url }}) for the smallest runnable analysis, then choose a [research workflow]({{ '/docs/workflows/' | relative_url }}) based on whether your main question concerns measurement uncertainty, analytical robustness, or publication provenance.
