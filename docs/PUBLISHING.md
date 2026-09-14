# Publishing GazeAudit

GazeAudit separates release qualification from public publication.

## GitHub Release publication

The `publish-github-release` workflow is manual-only and must be dispatched from `main` after the target tag has already passed the tag-bound `release-candidate` workflow.

For `0.1.0`, the publication control plane is `release/0.1.0-publication.json`. It binds:

- exact stable version and tag;
- annotated tag object;
- certified source commit and tree;
- canonical wheel and source-distribution names, sizes, and SHA-256 digests;
- exact-main, pre-tag, and tag-bound qualification run/artifact identities;
- the frozen three-case scientific validation labels; and
- the publication scope.

The workflow does not build release assets from post-tag `main`. It checks out the immutable release tag into a separate source directory, rebuilds the distributions under Python 3.12.14, runs `twine check` and the repository distribution verifier, and requires byte-for-byte agreement with the publication manifest.

A GitHub Release is created as a **draft** first. The workflow downloads the draft assets back from GitHub and verifies their names, sizes, and SHA-256 digests against the manifest. Only after that round-trip verification succeeds is the draft converted into a public, non-prerelease GitHub Release.

The workflow refuses to overwrite an existing release for the same tag.

## Publication boundaries

The GitHub publication workflow authorizes only a GitHub Release. It does not request an OpenID Connect token, does not publish to PyPI, does not create or modify a DOI, and does not deposit content in an archival registry.

PyPI and archival publication must use separate explicit gates because they have different credentials, immutability properties, and external metadata requirements.

## Scientific immutability

Publication work must not modify the post-outcome frozen GazeBase, Korthals, or Pedrotti protocols, source locks, execution records, endpoints, thresholds, seeds, or canonical classifications. The publication manifest records those existing outcomes only as provenance anchors.
