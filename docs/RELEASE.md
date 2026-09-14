# GazeAudit release qualification

GazeAudit now carries **stable `0.1.0` candidate metadata** in the release-preparation
branch. That metadata does not, by itself, mean that `v0.1.0` has been tagged or that a
GitHub Release, PyPI upload, DOI, or archival publication exists. Formal release status
begins only after the exact stable candidate has passed the release-candidate gate and a
separate publication action has been explicitly authorized.

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

## Stable `0.1.0` metadata gate

The dedicated release-preparation change must keep all release identities synchronized:

1. `[project].version` in `pyproject.toml` must equal `0.1.0`;
2. `CITATION.cff` must report the same `0.1.0` version;
3. `CHANGELOG.md` must contain a level-2 `0.1.0` release entry;
4. the canonical GazeBase, Korthals, and Pedrotti scientific records must remain
   unchanged;
5. the release-preparation pull request must pass the full standard tests, live
   interoperability, and distribution workflow;
6. the pull request must be merged pinned to its exact qualified head and the merge must
   then pass exact-main tests, interoperability, distribution, and Pages certification.

On that exact certified `main`, the stable metadata gate must pass:

```bash
python tools/release_gate.py \
  --expected-version 0.1.0 \
  --require-stable \
  --require-changelog-entry
```

A mismatch between project version, citation version, expected version, changelog entry,
or tag remains a hard failure.

## Pre-tag candidate qualification

After stable `0.1.0` metadata is merged and exact-main certified, run the manual
`workflow_dispatch` path of `.github/workflows/release-candidate.yml` from `main` with
`expected_version=0.1.0`. This pre-tag qualification does not create a tag or publish a
release. It reruns the stable metadata gate, rebuilds the candidate distributions,
validates them, installs the candidate wheel in a fresh environment, and archives the
candidate artifacts for review.

Only after that exact-main candidate artifact has been reviewed should `v0.1.0` be
created.

## Tag-bound candidate qualification

Create the tag `v0.1.0` **only on the exact certified main commit that passed the
pre-tag candidate qualification**. A tag push triggers
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
environment, and archives the tag-bound candidate artifacts.

## Publication boundary

A successful release-candidate workflow means only that the candidate source and built
distributions satisfy the repository's release contract. Actual publication—PyPI,
GitHub Release creation, archival deposition, or DOI registration—requires a separate,
explicitly authorized action after reviewing:

- the exact tag and commit;
- sdist and wheel SHA-256 digests;
- package metadata and contents;
- citation/changelog identity;
- exact-main CI evidence;
- pre-tag and tag-bound release-candidate evidence; and
- the unchanged authoritative scientific validation records.

No scientific protocol, cohort, endpoint, perturbation, threshold, seed, or canonical
classification may be altered as part of release preparation or publication.
