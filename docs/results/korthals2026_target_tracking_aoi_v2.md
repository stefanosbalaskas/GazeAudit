# Korthals 2026 target-tracking AOI — protocol v2 authoritative result

## Status

This document records the **first scientific execution** of the frozen Korthals target-tracking AOI protocol v2. The outcome is authoritative for this case study. It was executed only after the protocol, public-source identity, source-readiness missingness amendment, source freeze, source lock, and archive-before-reveal workflow had been fixed and certified.

No scientific choice in this record was selected or changed after observing the outcome.

## Immutable provenance

| Field | Value |
|---|---|
| Scientific workflow | `korthals-scientific-execution #1` |
| GitHub run | `34721629856` |
| GitHub job | `103628488961` |
| Execution commit | `3312423cb43b1d9da3877914455dd471aba81174` |
| Execution tree | `06d5d5f9adf6114464208fd428e3f572579a44a1` |
| Protocol-v2 fingerprint | `1cd4150c9341db145b8f6aee544f9634c67c46116e61e7e675ae3c50282d2d55` |
| Source-lock fingerprint | `8bcd9e1dfc8d6ca07c6222a20f563bf8b3bd67aed0de0d3b0e97628799de3a08` |
| Source-manifest fingerprint | `04dd531fb5e0eaa8aa77cb3743d7dadfd4c218895f7edf8186cc3ff9362b7541` |
| Companion commit | `1d7ebec23e3fe20f6db952eefda1a0dd58ae09da` |

The exact critical execution environment was Python 3.12.14, NumPy 2.5.3, pandas 2.3.3, and SciPy 1.18.1.

## Scientific archive

The workflow successfully verified the execution payload, uploaded the artifact, and only then executed the reveal step.

| Field | Value |
|---|---|
| Artifact ID | `10306308440` |
| Artifact name | `korthals-scientific-v2-3312423cb43b1d9da3877914455dd471aba81174` |
| Artifact size | 10,370,491 bytes |
| GitHub artifact SHA256 | `2eaab8171d9d5f70e138eb929554648cb6bed10b21646ab0acd7cfae4d607d11` |
| Independently recomputed ZIP SHA256 | `2eaab8171d9d5f70e138eb929554648cb6bed10b21646ab0acd7cfae4d607d11` |
| Execution fingerprint | `2db2b92fea136ba516f38a87a3c218cf90c9a2a69c55e8ea37b63cad8febb51b` |
| Audit scientific fingerprint | `aa4c04af9c011fe997ef107c8250b20d6a20824b180abdeb16871b5b5a2fc768` |
| Artifact-manifest fingerprint | `c55dbeb476197196a36d1c1af857bd6424e2db6fb1c7c5e5bdc94169bd380de0` |

The outer archive `SHA256SUMS` and the nested audit `SHA256SUMS` were independently verified. Every declared file matched its checksum. The GitHub-provided artifact digest and the independently recomputed ZIP digest are identical.

## Frozen source-readiness facts

The source lock admitted 15 participants. The published source inventory contains 112 files. After the already-declared protocol-v2 missingness rule, the prepared analysis contains 448,336 rows and 999 retained trials.

Exactly one scheduled trial had zero finite gaze samples after the frozen 50-Hz selection: participant `5c363694`, trial 59. Protocol v2 therefore removed the entire corresponding matched cell without imputation or replacement: participant `5c363694`, repetition 1, target speed 16, west trajectory, trials 59 and 68. These facts were known and locked before the scientific AOI endpoint was run.

## Frozen estimand and uncertainty model

The AOI is a target-centred circle with radius 1 dva. The endpoint is **jumping-circle occupancy minus moving-circle occupancy**. Complete matched-cell contrasts are averaged without weighting within participants, and participant estimates are then averaged without weighting at the study level.

Measurement uncertainty is propagated using the predeclared grouped isotropic Gaussian gaze-error model based on validation `error_avg`, with `sigma = error_avg / sqrt(pi / 2)`, zero bias, 2,000 Monte Carlo draws, batch size 8, seed `20260316`, a 95% interval, and zero as the reference.

## Authoritative scientific result

**Classification: `robust_negative`.**

| Quantity | Result |
|---|---:|
| Observations | 448,336 |
| Monte Carlo draws | 2,000 |
| Hard effect | -0.09864087564504398 |
| Expected membership effect | -0.07400756743578296 |
| Monte Carlo mean | -0.0740075674357833 |
| Monte Carlo median | -0.07397267112249165 |
| Monte Carlo SD | 0.0013013516924452913 |
| 95% measurement-model interval, lower | -0.07652491273093086 |
| 95% measurement-model interval, upper | -0.07146159624178107 |
| Probability below zero | 1.0 |
| Probability above zero | 0.0 |
| Probability equal to zero | 0.0 |

The predeclared classification rule assigns `robust_negative` when the hard effect is negative and at least 95% of measurement-error draws fall below zero. Here the hard effect is negative and **all 2,000 draws are below zero**.

Because the contrast is jumping minus moving, the scientific interpretation is narrowly stated as follows:

> Under the frozen paired AOI estimand, target-centred 1-dva occupancy was lower for jumping circles than for moving circles, and the negative direction remained stable under the prespecified measurement-error propagation model.

The hard binary-membership effect (-0.09864) and the measurement-error-propagated expected effect (-0.07401) differ in magnitude, but both have the same negative direction and the frozen robustness classification remains negative.

## Inferential boundary

The 95% interval reported here is a **measurement-model-induced uncertainty interval**. It is **not** a population confidence interval and is **not** a Bayesian posterior interval. The Monte Carlo sign probabilities describe uncertainty induced by the prespecified measurement model; they are not population p-values. This case-study execution does not establish a causal effect.

## Post-outcome scientific freeze

This result establishes the permanent post-outcome boundary for the Korthals case study. The following may not be changed in response to this outcome: protocol; AOI geometry or radius; endpoint or contrast direction; source cohort or author-directed exclusion; missingness policy; validation mapping or metric; Monte Carlo draw count, batch size, or seed; measurement-error family or bias; cell, participant, or study weighting; classification thresholds; or the scientific interpretation rule.

Permitted follow-up is limited to independent artifact verification, deterministic reproducibility checking without selecting among outcomes, archival/provenance work, publication reporting, and non-scientific infrastructure maintenance.

The machine-readable companion record is `docs/results/korthals2026_target_tracking_aoi_v2.json`.
