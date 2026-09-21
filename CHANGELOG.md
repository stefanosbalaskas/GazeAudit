# Changelog

All notable user-facing changes to GazeAudit are documented here.

The `0.1.0` entry below defines the first stable release candidate metadata. A repository
state containing this entry is not, by itself, evidence that `v0.1.0` has been tagged or
that a GitHub Release, PyPI distribution, DOI, or archival deposit exists. Those are
separate publication actions performed only after the release-candidate gate succeeds.

## 0.2.0 — 2026-09-21

### Scientific and software qualification

- Reach 100% executable statement coverage across the GazeAudit Python package.
- Qualify the complete test matrix on Python 3.10, 3.11, 3.12, and 3.13.
- Expand deterministic fail-closed tests for source intake, provenance, archive
  verification, execution contracts, missingness, AOI uncertainty, freeze records,
  reporting, readiness, and publication infrastructure.
- Preserve the frozen GazeBase, Korthals, and Pedrotti scientific outcomes without
  changing estimators, cohorts, thresholds, endpoints, protocols, or interpretation
  rules.
- Normalize Korthals v2 companion paths for portable Windows/POSIX execution.

### Release engineering

- Generalize GitHub Release and PyPI workflows so new releases are version-driven
  rather than hard-coded to the historical 0.1.0 publication files.
- Preserve exact-tag rebuilding, checksum verification, clean-wheel installation,
  GitHub Release round-trip verification, and PyPI Trusted Publishing.
- Require one source distribution and one universal wheel for the qualified payload.

## 0.1.0 — 2026-09-14

### Scientific MVP

- Validate GazeAudit against known-truth tests and three canonical real-data cases.
- Preserve the GazeBase multi-detector audit as `incomplete` after its frozen
  completeness gate failed rather than removing failing detectors post hoc.
- Preserve the Korthals target-tracking AOI audit as `robust_negative` under the frozen
  measurement-error propagation protocol.
- Preserve the Pedrotti/de Chambrier sampling/missingness audit as
  `materially_fragile` under the frozen recovery rule.
- Bind protocols, source identities/source locks, controlled executions, fingerprints,
  checksums, and archived artifacts with archive-before-reveal provenance.

### Reproducibility and publication support

- Add an authoritative validation matrix linking all three canonical real-data cases.
- Add the archived Pedrotti/de Chambrier sampling/missingness result record.
- Add a publication-facing validation summary and machine-readable reproducibility
  index.
- Add citation, reporting, interpretation-boundary, and reuse guidance.
- Add repository citation metadata through `CITATION.cff`.
- Add regression tests binding canonical scientific identities and indexed repository
  paths.

### Packaging and release engineering

- Mark the package as Alpha.
- Qualify clean source and wheel distributions in CI with metadata/content validation.
- Install the built wheel in a fresh environment and verify bundled scientific data.
- Add a fail-closed stable metadata/tag/changelog release gate.
- Add a release-candidate workflow that rebuilds and archives candidate distributions
  without automatically publishing them.
- Require exact-head PR qualification followed by exact-main tests, live
  interoperability, distribution, and Pages certification before tagging.

## Scientific MVP baseline — 2026-09-14

The scientific MVP was completed before stable-release preparation.

- GazeBase multi-detector audit: canonical classification `incomplete`.
- Korthals target-tracking AOI measurement-error audit: canonical classification
  `robust_negative`.
- Pedrotti/de Chambrier sampling/missingness audit: canonical classification
  `materially_fragile`.

These scientific outcomes are post-outcome frozen. Later documentation, packaging,
release, or publication work must not change the underlying protocols or reinterpret
classifications by altering the predeclared decision rules.
