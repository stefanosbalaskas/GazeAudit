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

The machine-readable control record is `release/0.1.0-external-publication.json`.

## PyPI — pending Trusted Publisher

GazeAudit uses PyPI Trusted Publishing through GitHub Actions OIDC. No long-lived PyPI API token should be created or stored in GitHub.

Before the first upload, create a **pending Trusted Publisher** in PyPI with exactly these values:

- PyPI project name: `gazeaudit`
- GitHub owner: `stefanosbalaskas`
- GitHub repository: `GazeAudit`
- workflow filename: `publish-pypi.yml`
- GitHub environment: `pypi`

A pending publisher does not reserve the package name. Immediately before configuring it, confirm that `gazeaudit` has not appeared on PyPI under an unrelated owner. If it has, stop rather than publishing under a different project identity.

The repository workflow is `.github/workflows/publish-pypi.yml`. It is manual-only and must be run from `main` with:

- `expected_version = 0.1.0`
- `expected_tag = v0.1.0`

The preparation job has read-only repository permissions. It verifies current `main`, resolves the immutable tag to the frozen source commit, rebuilds the distributions from that tag, checks the canonical hashes, downloads the already-public GitHub Release assets, and requires byte-for-byte equality before archiving the PyPI payload.

Only the second job can request an OIDC token. It runs in the `pypi` GitHub environment, downloads the exact preparation artifact, re-verifies the payload, and invokes `pypa/gh-action-pypi-publish@release/v1`. The action is configured with `skip-existing: false`; an unexpected existing `0.1.0` upload therefore fails closed instead of being silently ignored.

After a successful upload, independently verify:

1. the PyPI project is exactly `gazeaudit`;
2. version `0.1.0` is present;
3. exactly the intended wheel and sdist are listed;
4. their SHA-256 digests equal the canonical values above;
5. the project metadata identifies GazeAudit 0.1.0 and Python `>=3.10`;
6. PyPI shows Trusted Publishing/provenance for the upload when available.

Do not dispatch the workflow until the pending publisher is configured with the exact owner/repository/workflow/environment tuple above.

## Zenodo — archive the existing v0.1.0 release

The `v0.1.0` GitHub Release existed before Zenodo publication was configured. Do not assume that enabling the repository retroactively archives that already-published release.

First connect the GitHub account in Zenodo and enable `stefanosbalaskas/GazeAudit` so **future** GitHub releases can be ingested automatically.

For `0.1.0`, create a manual Zenodo software deposit using the tagged `CITATION.cff` as the authoritative metadata source. Do not add `.zenodo.json` for this historical release; doing so on post-tag `main` would not change the immutable tag and would introduce a second metadata authority.

Use these metadata values from `CITATION.cff@v0.1.0`:

- resource type: Software
- title: `GazeAudit: Measurement uncertainty and inferential robustness for eye-tracking research`
- creator: Stefanos Balaskas
- version: `0.1.0`
- publication date: `2026-09-14`
- license: MIT
- repository: `https://github.com/stefanosbalaskas/GazeAudit`
- keywords: eye tracking; gaze; measurement uncertainty; inferential robustness; multiverse analysis; area of interest

Use the GitHub Release notes as the descriptive release summary, preserving the protocol-bound wording of the three scientific validation outcomes.

Upload **exactly one file** to the Zenodo record:

- `gazeaudit-0.1.0.tar.gz`
- expected size: 242029 bytes
- expected SHA-256: `8c449e2fc469c2b91f1c2471b674b5d6b16b6e6aa883289069ffb0a679517173`

The source archive can be downloaded from the public GitHub Release. Do not upload the wheel, GitHub-generated source ZIP/TAR archives, CI artifact ZIPs, or a newly rebuilt source archive to this Zenodo version record.

Before pressing **Publish** in Zenodo, verify the title, creator, resource type, version, publication date, license, description, repository link, and single uploaded filename. After publication, record:

- Zenodo record ID;
- version DOI for `0.1.0`;
- concept DOI for GazeAudit;
- the Zenodo-hosted file checksum shown by the record;
- an independent SHA-256 of the downloaded Zenodo file.

The independently downloaded file must reproduce the canonical SHA-256 above before the DOI is added back to repository publication documentation.

## Scientific boundary

The external publication step transports an already-qualified software release. It must not modify the canonical GazeBase (`incomplete`), Korthals (`robust_negative`), or Pedrotti (`materially_fragile`) scientific records.
