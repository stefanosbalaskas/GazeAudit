# GazeAudit 0.2.0

GazeAudit 0.2.0 is the second stable release of GazeAudit for auditing measurement
uncertainty and inferential robustness in eye-tracking research.

## Scientific validation record

This release preserves the protocol-bound canonical validation outcomes established
before release preparation:

- **GazeBase multi-detector audit:** `incomplete`;
- **Korthals target-tracking AOI audit:** `robust_negative`;
- **Pedrotti/de Chambrier sampling and missingness audit:** `materially_fragile`.

These outcomes were not changed during 0.2.0 development or release qualification.

## Qualification

GazeAudit 0.2.0 includes:

- 100% executable statement coverage across the package;
- Python 3.10, 3.11, 3.12, and 3.13 CI qualification;
- deterministic fail-closed source, provenance, execution, archive, freeze, AOI,
  missingness, readiness, and publication contracts;
- portable Windows/POSIX handling for the Korthals v2 companion path;
- expanded scientific/API contract regression tests.

## Distribution integrity

The release consists of exactly:

- `gazeaudit-0.2.0-py3-none-any.whl`;
- `gazeaudit-0.2.0.tar.gz`.

The artifacts are rebuilt from the immutable `v0.2.0` tag, checked with Twine, verified
with GazeAudit's distribution verifier, installed in a clean environment, and compared
against the public GitHub Release payload before PyPI publication.

## Publication boundary

GitHub Release and PyPI publication remain separately gated actions. PyPI publication
uses GitHub OIDC Trusted Publishing and does not use a stored PyPI API token.

A new version-specific DOI is not claimed in the 0.2.0 metadata unless and until a
separate archival/Zenodo publication and verification step is completed.
