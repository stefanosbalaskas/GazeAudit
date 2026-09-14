# Changelog

All notable user-facing changes to GazeAudit will be documented here.

This repository has not yet made a formal tagged release. The entries below describe
development milestones and must not be interpreted as PyPI or archival releases.

## Unreleased

### 0.1.0.dev20 — post-MVP release hardening

- Mark the package as alpha rather than pre-alpha.
- Add repository citation metadata.
- Add an authoritative validation matrix linking the three canonical real-data cases.
- Add the archived Pedrotti/de Chambrier sampling/missingness result record.
- Replace stale README roadmap language with the completed scientific-MVP status.
- Add regression tests binding package version, citation metadata, and canonical
  validation identities.

## Scientific MVP baseline — 2026-09-14

The scientific MVP was completed before this release-hardening tranche.

- GazeBase multi-detector audit: canonical classification `incomplete`.
- Korthals target-tracking AOI measurement-error audit: canonical classification
  `robust_negative`.
- Pedrotti/de Chambrier sampling/missingness audit: canonical classification
  `materially_fragile`.

These scientific outcomes are post-outcome frozen. Later documentation, packaging, or
release work must not change the underlying protocols or reinterpret classifications by
altering the predeclared decision rules.
