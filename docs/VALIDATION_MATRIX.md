# GazeAudit authoritative validation matrix

This document is the publication-facing index of GazeAudit's canonical scientific-MVP
validation outcomes. It does **not** replace the protocol, source-lock, execution, or
artifact records for any case study.

All three real-data cases were governed by the same integrity rule: scientific choices
were fixed before outcome inspection, the controlled execution produced a checksummed
artifact, the artifact was archived before reveal, and post-outcome changes are limited
to verification, documentation, archival, reproducibility, and non-scientific
infrastructure maintenance.

| Case | Validation purpose | Canonical classification | What it demonstrates |
|---|---|---|---|
| GazeBase | multi-detector inferential robustness with a predeclared completeness gate | `incomplete` | GazeAudit does not drop failed detector specifications or manufacture a robustness claim when the declared specification space is incomplete |
| Korthals et al. | propagation of AOI measurement uncertainty into a paired scientific endpoint | `robust_negative` | a real-data scientific direction can remain stable under the frozen measurement-error model |
| Pedrotti/de Chambrier | sensitivity of a gaze-path-rate contrast to sampling and added missingness | `materially_fragile` | a scientific endpoint can retain direction yet fail the predeclared magnitude-recovery requirement |

## 1. GazeBase multi-detector audit

- Frozen protocol fingerprint:
  `3f64122f62cbc9762b0bd0e0b95c7fef6ff40c4700215ee4b90f005af77003b1`.
- Exact scientific commit:
  `609203dfc37f2ef4984de82b888660e7cc30675c`.
- Final artifact ID: `10284017265`.
- Artifact name: `gazebase-partitioned-final-609203df`.
- ZIP SHA-256:
  `2fae4e99243e6738047a34b8dc24a183e8fb98606e4873723d43b8baa4ae937b`.
- Execution fingerprint:
  `35975d89dea728bd3aa146739dc58ea2bcb9322e357a44856b424fffb4183632`.
- Artifact-manifest fingerprint:
  `965ba4b83b06bd3da549b9ca9e36e79443e33b2bbde76d81f87ed7767f94f71d`.
- Fixed cohort: `n=322`.
- IVT, IVVT, IDT, IDVT, and Engbert: 322/322 finite participant estimates.
- NH and REMoDNaV: 0/322 under the already-frozen NaN-preserving/no-interpolation
  policy.
- Canonical classification: **`incomplete`** because the 95% completeness gate failed.

The five computable detector estimates are descriptive archived outputs only. The
canonical analysis does not silently remove NH or REMoDNaV.

See `docs/case_studies/GAZEBASE_MULTIDETECTOR_PROTOCOL.md` and
`docs/case_studies/gazebase_real_data_execution.md`.

## 2. Korthals target-tracking AOI audit

- Scientific workflow: `korthals-scientific-execution #1`.
- GitHub run: `34721629856`.
- Execution commit:
  `3312423cb43b1d9da3877914455dd471aba81174`.
- Protocol-v2 fingerprint:
  `1cd4150c9341db145b8f6aee544f9634c67c46116e61e7e675ae3c50282d2d55`.
- Source-lock fingerprint:
  `8bcd9e1dfc8d6ca07c6222a20f563bf8b3bd67aed0de0d3b0e97628799de3a08`.
- Artifact ID: `10306308440`.
- ZIP SHA-256:
  `2eaab8171d9d5f70e138eb929554648cb6bed10b21646ab0acd7cfae4d607d11`.
- Execution fingerprint:
  `2db2b92fea136ba516f38a87a3c218cf90c9a2a69c55e8ea37b63cad8febb51b`.
- Audit scientific fingerprint:
  `aa4c04af9c011fe997ef107c8250b20d6a20824b180abdeb16871b5b5a2fc768`.
- Artifact-manifest fingerprint:
  `c55dbeb476197196a36d1c1af857bd6424e2db6fb1c7c5e5bdc94169bd380de0`.
- Hard effect: `-0.09864087564504398`.
- Measurement-error expected effect: `-0.07400756743578296`.
- 95% measurement-model-induced interval:
  `[-0.07652491273093086, -0.07146159624178107]`.
- All 2,000 prespecified draws were below zero.
- Canonical classification: **`robust_negative`**.

The interval is induced by the frozen measurement model. It is not a population
confidence interval or Bayesian posterior interval.

See `docs/results/korthals2026_target_tracking_aoi_v2.md`.

## 3. Pedrotti/de Chambrier sampling + missingness audit

- Scientific workflow: `pedrotti-scientific-execution #1`.
- GitHub run: `34793103977`.
- Execution commit:
  `270d444c599363ebd25f25e8a95f5f3c78e55b02`.
- Protocol fingerprint:
  `efb194ad2c492768962320198d281c98574eb2dc22291279bfd176a15606a0d5`.
- Source-lock fingerprint:
  `d71949f035ecdf14b9e225b8ca441d291625767dc4a07fa4854882ff2dcae898`.
- Source-manifest fingerprint:
  `ca676426a01c1d57dda93b62709d4e9040369e4193c0b44353be78d644a33b1f`.
- Artifact ID: `10328414078`.
- Artifact name:
  `pedrotti-scientific-execution-v1-270d444c599363ebd25f25e8a95f5f3c78e55b02`.
- ZIP SHA-256:
  `b411fe6a5f4ad7035ac606d60a952306c0b818d956f7b4930827b8cbe10ae8d5`.
- Results fingerprint:
  `5bafe0d1d1d0d054a681cb7136fc4e259c0f75e07d51653acde472c7c6e4dce9`.
- Execution fingerprint:
  `35dd53da10646400aca657c388f8b77a6a974c555de7efbd6f83faeb970b1eb6`.
- Artifact-manifest fingerprint:
  `05a986abe8a7be7a7ccbf2bf24b7467a3c623381d05d2dab8f4ae81b0618d661`.
- Reference long-minus-short gaze-path-rate effect:
  `-75.37814047218419` pixels/second.
- Sampling-family recovery: `0.4`.
- Canonical classification: **`materially_fragile`**.

Sampling estimates remained negative at all five target rates, but only 500 Hz and
250 Hz met the frozen 20% relative-deviation tolerance. At 125, 100, and 50 Hz,
relative deviations were approximately 37.0%, 38.7%, and 72.7%, respectively.
Recovery under added missingness also fell to 0.4 or lower for several 10%/20% families,
which satisfies the predeclared material-fragility rule.

See `docs/results/pedrotti_sampling_missingness_v1.md`.

## Interpretation boundary

These three outcomes intentionally cover different scientific states:

1. **incomplete** — the declared specification space cannot support a robustness
   classification;
2. **robust** — the prespecified scientific direction remains stable under the declared
   uncertainty model;
3. **materially fragile** — the endpoint fails the prespecified recovery criterion under
   defensible perturbations.

This is the scientific-MVP validation claim. GazeAudit is not validated merely because
it produces a preferred or statistically significant result.
