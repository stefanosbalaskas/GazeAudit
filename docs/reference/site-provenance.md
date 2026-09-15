---
title: Documentation provenance
description: Distinguish stable GazeAudit v0.1.0 from the continuously updated development documentation and identify the exact Pages build revision.
kicker: Reference
permalink: /docs/reference/site-provenance/
---

# Documentation provenance

The public GazeAudit site follows the repository's default branch and therefore documents **post-release development** as well as the frozen v0.1.0 release. Scientific validation records that are explicitly frozen remain governed by their protocol/source fingerprints and are not rewritten by documentation updates.

## Stable software release

- Stable package release: **v0.1.0**
- GitHub release: [v0.1.0](https://github.com/stefanosbalaskas/GazeAudit/releases/tag/v0.1.0)
- PyPI: [gazeaudit 0.1.0](https://pypi.org/project/gazeaudit/0.1.0/)
- Zenodo DOI: [10.5281/zenodo.22757340](https://doi.org/10.5281/zenodo.22757340)

When reproducing a published analysis, cite and install the release/version actually used rather than assuming that current `main` is equivalent to v0.1.0.

## Current documentation build

{% assign revision = site.github.build_revision | default: 'local-build' %}

This page was built from repository revision **`{{ revision }}`**.

{% if site.github.build_revision %}
[Inspect this exact revision on GitHub](https://github.com/stefanosbalaskas/GazeAudit/commit/{{ site.github.build_revision }}).
{% endif %}

The documentation site can therefore move ahead of the stable package release while preserving an inspectable source revision for every GitHub Pages deployment.

## What remains immutable

The frozen v0.1.0 release/tag assets and the protocol-bound validation outcomes `incomplete`, `robust_negative`, and `materially_fragile` are not development-document labels. Their meaning remains tied to the authoritative validation records and fingerprints described in the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}).

## Recommended citation practice

For manuscripts or archived analyses, record all three when applicable:

1. the installed GazeAudit package version;
2. the Git commit used for unreleased development functionality;
3. the DOI or frozen validation artifact when relying on a protocol-bound case study.

This separates software identity, documentation identity, and scientific-evidence identity rather than collapsing them into one version label.
