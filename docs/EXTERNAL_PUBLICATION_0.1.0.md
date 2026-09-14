# GazeAudit 0.1.0 — PyPI and Zenodo publication

This document is the operator record for publishing the already-frozen `v0.1.0` release to PyPI and Zenodo. It does not authorize any modification of the tag, scientific protocols, source locks, endpoints, decision rules, or canonical validation outcomes.

## Frozen release identity

- version: `0.1.0`
- tag: `v0.1.0`
- source commit: `fdade23c12b3c2a2f26a1ca8398034b6f8d0213f`
- source tree: `938007cda6051d50243fff27a892870f7128d407`
- GitHub Release: `https://github.com/stefanosbalaskas/GazeAudit/releases/tag/v0.1.0`
- wheel: `gazeaudit-0.1.0-py3-none-any.whl`
  - SHA-256: `51fa1f0a0388dfe337fad0d6564df802ae8464f01d5ce666cc96ce2e144271a1`
  - size: 192027 bytes
- sdist: `gazeaudit-0.1.0.tar.gz`
  - SHA-256: `8c449e2fc469c2b91f1c2471b674b5d6b16b6e6aa883289069ffb0a679517173`
  - size: 242029 bytes

The machine-readable pre-publication control record is `release/0.1.0-external-publication.json`. The completed external-publication evidence is recorded separately in `release/0.1.0-external-publication-verification.json` so the fail-closed authorization plan remains unchanged after publication.

## PyPI — Trusted Publishing

GazeAudit uses PyPI Trusted Publishing through GitHub Actions OIDC. No long-lived PyPI API token is required or stored in GitHub.

The initial Trusted Publisher tuple was configured as:

- PyPI project name: `gazeaudit`
- GitHub owner: `stefanosbalaskas`
- GitHub repository: `GazeAudit`
- workflow filename: `publish-pypi.yml`
- GitHub environment: `pypi`

The repository workflow is `.github/workflows/publish-pypi.yml`. It was dispatched from `main` with:

- `expected_version = 0.1.0`
- `expected_tag = v0.1.0`

The preparation job had read-only repository permissions. It verified current `main`, resolved the immutable tag to the frozen source commit, rebuilt the distributions from that tag, checked the canonical hashes, downloaded the already-public GitHub Release assets, and required byte-for-byte equality before archiving the PyPI payload.

Only the second job could request an OIDC token. It ran in the `pypi` GitHub environment, downloaded the exact preparation artifact, re-verified the payload, and invoked `pypa/gh-action-pypi-publish@release/v1` with `skip-existing: false`.

Publication completed in workflow run `34887345589`, publish job `104121447203`. Both canonical distributions were accepted by PyPI with HTTP 200 responses and PyPI publish attestations:

- `gazeaudit-0.1.0-py3-none-any.whl` — SHA-256 `51fa1f0a0388dfe337fad0d6564df802ae8464f01d5ce666cc96ce2e144271a1`
- `gazeaudit-0.1.0.tar.gz` — SHA-256 `8c449e2fc469c2b91f1c2471b674b5d6b16b6e6aa883289069ffb0a679517173`

The public package record is `https://pypi.org/project/gazeaudit/0.1.0/`.

## Zenodo — archived v0.1.0 release

The `v0.1.0` GitHub Release existed before Zenodo publication was configured, so version `0.1.0` was deposited manually while the repository integration was enabled for future releases.

The manual Zenodo software deposit used `CITATION.cff@v0.1.0` as the authoritative frozen metadata source. No `.zenodo.json` was introduced for the historical release.

Verified record metadata:

- record ID: `22757340`
- resource type: Software
- title: `GazeAudit: Measurement uncertainty and inferential robustness for eye-tracking research`
- creator: Stefanos Balaskas
- version: `0.1.0`
- publication date: `2026-09-14`
- license: MIT
- repository: `https://github.com/stefanosbalaskas/GazeAudit`
- keywords: eye tracking; gaze; measurement uncertainty; inferential robustness; multiverse analysis; area of interest
- version DOI: `10.5281/zenodo.22757340`
- concept DOI: `10.5281/zenodo.22757339`

Exactly one file is archived in the record:

- `gazeaudit-0.1.0.tar.gz`
- size: 242029 bytes
- Zenodo-displayed MD5: `7550c722e9ad18e4dd288c7e1aad7f05`
- independently reproduced SHA-256: `8c449e2fc469c2b91f1c2471b674b5d6b16b6e6aa883289069ffb0a679517173`

The independent checksum verification was performed from GitHub-hosted Ubuntu 24.04 in workflow run `34889732485`, job `104129090621`. That runner downloaded the file directly from `https://zenodo.org/records/22757340/files/gazeaudit-0.1.0.tar.gz?download=1` and reproduced both the expected byte size and frozen SHA-256.

## Citation

For a specific reproducible release, cite the version DOI:

`10.5281/zenodo.22757340`

For a reference intended to follow the latest Zenodo version of GazeAudit, use the concept DOI:

`10.5281/zenodo.22757339`

The post-publication `main` branch adds the verified version DOI to `CITATION.cff`; the immutable `v0.1.0` tag and its original `CITATION.cff` remain unchanged.

## Scientific boundary

The external publication step transported an already-qualified software release. It did not modify the canonical GazeBase (`incomplete`), Korthals (`robust_negative`), or Pedrotti (`materially_fragile`) scientific records.
