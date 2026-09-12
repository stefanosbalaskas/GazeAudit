# Korthals protocol-v2 public-source lock

## Status

The first successful endpoint-blind Korthals protocol-v2 source freeze is now bound as
an immutable repository source lock **before any scientific AOI endpoint execution**.
The lock fingerprint is
`8bcd9e1dfc8d6ca07c6222a20f563bf8b3bd67aed0de0d3b0e97628799de3a08`.

## Certified source-freeze evidence

Source-freeze run `34719412734` was manually dispatched on exact certified `main`
`50ca8239006cdf8d0771b7209dc85acf366ade31`. Job `103622387211` completed
successfully. The workflow verified the exact GazeAudit commit, companion commit,
complete OSF download, protocol-v2 endpoint-blind intake, dependency environment and
nested checksums, then uploaded the freeze artifact before revealing source identity.

The archived artifact is:

- artifact ID `10305414874`;
- name `korthals-source-freeze-v2-50ca8239006cdf8d0771b7209dc85acf366ade31`;
- size 23,657 bytes;
- GitHub digest
  `sha256:ae68ad62e148cf101730e7b73923fe694694f6616cae3432c8c15a164d21adcb`;
- independently downloaded ZIP SHA-256
  `ae68ad62e148cf101730e7b73923fe694694f6616cae3432c8c15a164d21adcb`.

The GitHub digest and independently recomputed ZIP hash are identical. All outer and
nested `SHA256SUMS` entries were independently recomputed successfully.

## Locked public-source identity

The lock binds:

- OSF DOI `10.17605/OSF.IO/ZX7HC`, project `zx7hc`;
- download contract `raw_clean=both`, `train_test=both`, `participants=all`;
- companion commit `1d7ebec23e3fe20f6db952eefda1a0dd58ae09da`;
- protocol-v2 fingerprint
  `1cd4150c9341db145b8f6aee544f9634c67c46116e61e7e675ae3c50282d2d55`;
- source-manifest fingerprint
  `04dd531fb5e0eaa8aa77cb3743d7dadfd4c218895f7edf8186cc3ff9362b7541`;
- 110 checksummed source-manifest files and 10 participants;
- participant-split fingerprint
  `ebd3721064e434e6c948d8696b72761604ddf2f92949639ed680c688d8e7580b`;
- 448,336 prepared 50-Hz rows, 914 retained participant-trials and 12 validation groups;
- the protocol-v2 zero-finite rule outcome from endpoint-blind preparation: participant
  `88878fe6`, trial 27 has zero finite scheduled gaze samples, therefore the complete
  matched cell for repetition 1, target speed 3.0, northeast trajectory, trials 27 and
  34 is removed symmetrically without replacement;
- freeze-manifest fingerprint
  `fe6930010d31c0c4f920818a3ac31020b97c2f739aea8e00ebcaee5352355cb8`;
- intake artifact-manifest fingerprint
  `ed4d99db1f977dacf671dac129980ded5f071ab0ed7e4420316c59e4bd61e359`;
- Python 3.12.14, pandas 2.3.3, NumPy 2.5.3 and SciPy 1.18.1 as the archived
  source-freeze execution environment identities.

## Fail-closed semantics

`verify_korthals_locked_source_manifest()` first requires a structurally valid
protocol-v2 source manifest and then requires exact equality of the locked source
fingerprint, counts, participant identities, OSF contract, companion commit and
protocol identity. Any public-source byte change therefore changes the manifest
fingerprint and blocks scientific execution.

`verify_korthals_locked_prepared()` separately requires endpoint-blind preprocessing to
reproduce the locked source fingerprint, participant/split identity, prepared-row and
validation-group counts, retained-trial count, target types, missingness policy, and
exact zero-finite/matched-cell records before a future endpoint call can be admitted.

## Scientific boundary

This source-lock tranche does not call the Korthals AOI endpoint, construct AOI
membership, run the 2,000-draw Monte Carlo analysis, inspect an effect estimate,
calculate sign probability, or classify the scientific result. No protocol, cohort,
AOI, endpoint, validation, error-model, seed, sampling, missingness, or interpretation
choice is changed by this lock. The first scientific execution remains a later,
separately controlled archive-before-reveal gate.
