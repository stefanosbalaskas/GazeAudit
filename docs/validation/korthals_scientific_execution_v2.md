# Korthals protocol-v2 first-scientific-execution gate

## Scope

This tranche prepares, but does **not run**, the first scientific AOI execution for the
Korthals target-tracking case study. It is built only after the public source was
successfully frozen and independently verified and after the resulting source identity
was merged as an exact-main-certified repository lock.

At qualification time no Korthals hard AOI effect, Monte Carlo distribution, sign
probability, or scientific classification has been executed or inspected.

## Certified prerequisites

The execution workflow is anchored to:

- protocol-v2 fingerprint
  `1cd4150c9341db145b8f6aee544f9634c67c46116e61e7e675ae3c50282d2d55`;
- source-lock fingerprint
  `8bcd9e1dfc8d6ca07c6222a20f563bf8b3bd67aed0de0d3b0e97628799de3a08`;
- source-manifest fingerprint
  `04dd531fb5e0eaa8aa77cb3743d7dadfd4c218895f7edf8186cc3ff9362b7541`;
- companion commit `1d7ebec23e3fe20f6db952eefda1a0dd58ae09da`;
- successful source-freeze run `34719412734`, artifact `10305414874`;
- source-freeze critical environment Python 3.12.14, NumPy 2.5.3,
  pandas 2.3.3 and SciPy 1.18.1.

## Fail-closed execution order

The manual-only `korthals-scientific-execution` workflow runs on `main` only and uses
this order:

1. checkout and verify the exact `GITHUB_SHA`;
2. checkout the exact frozen companion commit;
3. recreate and assert the source-freeze-matched critical Python stack;
4. download the complete public OSF source using the already-certified resumable
   transfer path;
5. checksum the current source and require exact equality with the packaged source
   lock **before companion preprocessing**;
6. run memory-bounded companion preprocessing and protocol-v2 preparation;
7. require exact reproduction of the locked participant/split identity, 448,336
   prepared rows, 914 retained trials, 12 validation groups, missingness policy and
   the exact zero-finite/matched-cell records **before the endpoint call**;
8. evaluate the unchanged frozen AOI endpoint and 2,000-draw measurement-error Monte
   Carlo audit without printing scientific results;
9. write a checksummed execution archive bound to the source lock, exact execution
   commit, run ID and dependency snapshot;
10. verify both archive integrity and the locked endpoint-blind intake facts;
11. upload the scientific artifact with compression disabled; and
12. only after successful upload, verify again and reveal the archived classification,
   summary and scientific fingerprints.

Thus source identity is checked twice before scientific evaluation: once against the
fresh byte manifest and once against the fully prepared endpoint-blind representation.

## Scientific invariants

The protocol-v2 execution reuses the frozen endpoint semantics without modification:
target-centered circular AOI radius 1 dva; jumping-minus-moving matched-cell contrast;
unweighted averaging over complete cells within participant and participants within
study; validation-block `error_avg` converted to isotropic Gaussian sigma by the
frozen model; zero bias; 2,000 Monte Carlo draws in batches of eight; seed `20260316`;
95% measurement-model interval; reference zero; and the predeclared robust-positive,
robust-negative, or measurement-sensitive interpretation rule.

No interpolation, sample recovery, phase shift, cohort change, matched-cell change,
validation filtering, seed change, error-model change, AOI change, endpoint change or
post-outcome adaptation is introduced.

## Qualification boundary

CI may execute the protocol-v2 scientific functions only on synthetic fixtures whose
known construction exercises the existing endpoint semantics. The real OSF workflow
has `workflow_dispatch` as its only trigger; opening or merging this tranche cannot
start the real scientific execution. A separate manual action on a subsequently
exact-main-certified commit is therefore required for the first public-data outcome.
