# GazeAudit publication and validation summary

GazeAudit is a methods-first Python package for auditing how eye-tracking conclusions
change under measurement uncertainty and defensible analytical choices. The scientific
MVP is validated by known-truth tests plus three deliberately different real-data
outcomes. These outcomes are canonical, post-outcome frozen records; this document
summarizes them but does not replace their protocols, source locks, execution records,
or archived artifacts.

## Scientific validation claim

The validation programme demonstrates that GazeAudit can represent three distinct
scientific states without optimizing for a preferred result:

| Case | Methodological stress test | Canonical outcome |
|---|---|---|
| GazeBase | seven-detector specification-space completeness | `incomplete` |
| Korthals target tracking | propagation of gaze measurement error into a paired AOI endpoint | `robust_negative` |
| Pedrotti/de Chambrier reading numerals | sampling-rate and added-missingness sensitivity of gaze-path rate | `materially_fragile` |

The common integrity rule was protocol/source control before outcome inspection,
checksummed execution artifacts, archive before reveal, and no post-outcome scientific
tuning.

## Canonical fingerprints

### GazeBase multi-detector audit

- protocol fingerprint: `3f64122f62cbc9762b0bd0e0b95c7fef6ff40c4700215ee4b90f005af77003b1`;
- scientific commit: `609203dfc37f2ef4984de82b888660e7cc30675c`;
- execution fingerprint: `35975d89dea728bd3aa146739dc58ea2bcb9322e357a44856b424fffb4183632`;
- artifact-manifest fingerprint: `965ba4b83b06bd3da549b9ca9e36e79443e33b2bbde76d81f87ed7767f94f71d`;
- archived artifact ID: `10284017265`;
- artifact ZIP SHA-256: `2fae4e99243e6738047a34b8dc24a183e8fb98606e4873723d43b8baa4ae937b`;
- canonical outcome: **`incomplete`**.

GazeBase does not have a separate source-freeze workflow. Its selected source-file byte
identity is hashed and bound within the controlled execution/source identity. The
failed completeness gate is retained as the scientific result; NH and REMoDNaV are not
silently removed.

### Korthals target-tracking AOI audit

- protocol-v2 fingerprint: `1cd4150c9341db145b8f6aee544f9634c67c46116e61e7e675ae3c50282d2d55`;
- source-lock fingerprint: `8bcd9e1dfc8d6ca07c6222a20f563bf8b3bd67aed0de0d3b0e97628799de3a08`;
- scientific execution commit: `3312423cb43b1d9da3877914455dd471aba81174`;
- execution fingerprint: `2db2b92fea136ba516f38a87a3c218cf90c9a2a69c55e8ea37b63cad8febb51b`;
- audit scientific fingerprint: `aa4c04af9c011fe997ef107c8250b20d6a20824b180abdeb16871b5b5a2fc768`;
- artifact-manifest fingerprint: `c55dbeb476197196a36d1c1af857bd6424e2db6fb1c7c5e5bdc94169bd380de0`;
- source-freeze artifact ID: `10305414874`;
- scientific artifact ID: `10306308440`;
- scientific artifact ZIP SHA-256: `2eaab8171d9d5f70e138eb929554648cb6bed10b21646ab0acd7cfae4d607d11`;
- canonical outcome: **`robust_negative`**.

The 95% interval reported for this case is induced by the frozen measurement-error
model. It is not a population confidence interval or Bayesian posterior interval.

### Pedrotti/de Chambrier sampling + missingness audit

- protocol fingerprint: `efb194ad2c492768962320198d281c98574eb2dc22291279bfd176a15606a0d5`;
- source-lock fingerprint: `d71949f035ecdf14b9e225b8ca441d291625767dc4a07fa4854882ff2dcae898`;
- source-manifest fingerprint: `ca676426a01c1d57dda93b62709d4e9040369e4193c0b44353be78d644a33b1f`;
- scientific execution commit: `270d444c599363ebd25f25e8a95f5f3c78e55b02`;
- results fingerprint: `5bafe0d1d1d0d054a681cb7136fc4e259c0f75e07d51653acde472c7c6e4dce9`;
- execution fingerprint: `35dd53da10646400aca657c388f8b77a6a974c555de7efbd6f83faeb970b1eb6`;
- artifact-manifest fingerprint: `05a986abe8a7be7a7ccbf2bf24b7467a3c623381d05d2dab8f4ae81b0618d661`;
- source-freeze artifact ID: `10326523152`;
- scientific artifact ID: `10328414078`;
- scientific artifact ZIP SHA-256: `b411fe6a5f4ad7035ac606d60a952306c0b818d956f7b4930827b8cbe10ae8d5`;
- canonical outcome: **`materially_fragile`**.

The reference effect remained directionally negative across all frozen sampling rates,
but recovery failed the predeclared magnitude criterion at lower rates and in several
added-missingness families. The classification therefore reflects the frozen recovery
rule rather than a significance threshold.

## Reproducibility map

The machine-readable evidence map is
[`REPRODUCIBILITY_INDEX.json`](REPRODUCIBILITY_INDEX.json). The authoritative
publication-facing matrix remains [`VALIDATION_MATRIX.md`](VALIDATION_MATRIX.md).
Protocol, source-lock, execution, and result paths in the JSON index are repository
paths and are regression-tested for existence and canonical identity.

## Release-readiness evidence

This publication bundle was prepared from certified pre-release main
`c5f85d6f58ec058c29953b4513dbf3995f390f06`, package `0.1.0.dev20`. Exact-main
tests #340, interoperability #255, distribution #2, and Pages #17 were green. The
clean distribution build reproduced:

- wheel SHA-256 `debd6f6dcbdb337f15890d6124c73274e78db84ac36a79504b03297c4d56c9d0`;
- sdist SHA-256 `3118d6b219be7ed549dc8689eb167cd9ecb3a96f30ce38b21acdad42fc310361`;
- distribution artifact ID `10341022917`;
- artifact archive digest `sha256:c8ff5245ca6ce2a79c409257bf605acb4f7f1afa90c7705058c8cbe3ba3858f9`.

These are pre-release qualification records, not a claim that `0.1.0` has been tagged
or published.

## Interpretation boundary

The real-data cases demonstrate behavior under their declared protocols and source
identities. They do not establish universal robustness of every eye-tracking endpoint,
tracker, population, preprocessing pipeline, or uncertainty model. Post-MVP additions
must be validated separately and must not retroactively alter these canonical results.
