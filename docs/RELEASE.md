# GazeAudit release qualification

GazeAudit is currently an **unreleased alpha development package**. The active package
line is `0.1.0.dev20`; no Git tag, GitHub Release, PyPI upload, DOI, or archive should be
represented as a formal `0.1.0` release until the release-candidate gate below has been
satisfied on an exact certified `main` commit.

## Release-engineering principle

Release qualification is deliberately separated from publication. The repository may
build and archive candidate distributions automatically, but it must not publish them to
PyPI or create a GitHub Release implicitly. A human-controlled publication step comes
only after the candidate artifacts and their exact source commit have been reviewed.

The release workflows therefore request read-only repository contents permission and do
not request `id-token: write`, `packages: write`, registry credentials, or release-write
permissions.

## Ordinary distribution qualification

Every pull request and push to `main` runs `.github/workflows/distribution.yml`.
It must:

1. build one source distribution and one universal wheel from a clean `dist/`;
2. pass `twine check`;
3. verify package metadata and required frozen scientific JSON resources with
   `tools/verify_distribution.py`;
4. install the built wheel—not the checkout—in a fresh virtual environment;
5. import GazeAudit and verify a packaged scientific resource;
6. upload the two qualified distribution files as a GitHub Actions artifact.

The uploaded distribution artifact is CI evidence only. It is not a release.

## Preparing the first stable `0.1.0` candidate

A dedicated release-preparation pull request must make the release identity explicit.
At minimum it must:

1. change `[project].version` in `pyproject.toml` from `0.1.0.dev20` to `0.1.0`;
2. change `CITATION.cff` to the same `0.1.0` version;
3. promote the changelog to a level-2 stable release entry such as
   `## 0.1.0 — YYYY-MM-DD`;
4. preserve the canonical GazeBase, Korthals, and Pedrotti scientific records unchanged;
5. pass the full standard tests, live interoperability, Pages, and distribution workflow;
6. be merged pinned to its exact qualified head and then pass exact-main certification.

Before tagging, the stable metadata gate must pass from that exact certified `main`:

```bash
python tools/release_gate.py \
  --expected-version 0.1.0 \
  --require-stable \
  --require-changelog-entry
```

The current `0.1.0.dev20` line is expected to fail this stable gate. That failure is a
feature: development metadata must never be mistaken for a release candidate.

## Tag-bound candidate qualification

After stable `0.1.0` metadata is merged and exact-main certified, create the tag
`v0.1.0` **on that exact certified main commit**. A tag push triggers
`.github/workflows/release-candidate.yml`, which additionally requires:

```bash
python tools/release_gate.py \
  --expected-version 0.1.0 \
  --tag v0.1.0 \
  --require-stable \
  --require-changelog-entry
```

The tag must therefore equal `v{project_version}` exactly. The workflow then rebuilds the
sdist and wheel from the tagged commit, validates them, installs the wheel in a fresh
environment, and archives the candidate artifacts.

A manual `workflow_dispatch` path is also available from `main` for pre-tag stable
qualification. It accepts an `expected_version` but does not create a tag or publish any
artifact outside GitHub Actions.

## Publication boundary

A successful release-candidate workflow means only that the tagged source and the built
distributions satisfy the repository's release contract. Actual publication—PyPI,
GitHub Release creation, archival deposition, or DOI registration—requires a separate,
explicitly authorized action after reviewing:

- the exact tag and commit;
- sdist and wheel SHA-256 digests;
- package metadata and contents;
- citation/changelog identity;
- exact-main CI evidence;
- the unchanged authoritative scientific validation records.

No scientific protocol, cohort, endpoint, perturbation, threshold, seed, or canonical
classification may be altered as part of release preparation.
