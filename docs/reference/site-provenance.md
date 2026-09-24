---
title: Documentation provenance
description: Distinguish stable GazeAudit v0.2.0 from continuously updated development documentation and identify the exact Pages build revision.
kicker: Reference
permalink: /docs/reference/site-provenance/
---

# Documentation provenance

The public GazeAudit site follows the repository's default branch and therefore can document **post-release development** as well as the stable v0.2.0 package. Scientific validation records that are explicitly frozen remain governed by their protocol/source fingerprints and are not rewritten by documentation updates.

## Stable software release

- Stable package release: **v0.2.0**
- GitHub release: [v0.2.0](https://github.com/stefanosbalaskas/GazeAudit/releases/tag/v0.2.0)
- PyPI: [gazeaudit 0.2.0](https://pypi.org/project/gazeaudit/0.2.0/)
- External publication verification: [release/0.2.0-external-publication-verification.json](https://github.com/stefanosbalaskas/GazeAudit/blob/main/release/0.2.0-external-publication-verification.json)
- Archived v0.1.0 Zenodo DOI: [10.5281/zenodo.22757340](https://doi.org/10.5281/zenodo.22757340)

The v0.2.0 publication record verifies the GitHub Release and PyPI Trusted Publishing payload. It explicitly records that Zenodo was **not published in the v0.2.0 release tranche**, so the v0.1.0 DOI must not be presented as a version-specific DOI for v0.2.0.

When reproducing an analysis, cite and install the release/version actually used rather than assuming that current `main` is equivalent to v0.2.0.

## Current documentation build

{% assign revision = site.github.build_revision | default: 'local-build' %}

This page was built from repository revision **`{{ revision }}`**.

{% if site.github.build_revision %}
[Inspect this exact revision on GitHub](https://github.com/stefanosbalaskas/GazeAudit/commit/{{ site.github.build_revision }}).
{% endif %}

The documentation site can therefore move ahead of the stable package release while preserving an inspectable source revision for every GitHub Pages deployment.

## What remains immutable

The protocol-bound validation outcomes `incomplete`, `robust_negative`, and `materially_fragile` remain tied to their authoritative frozen protocols, source identities, decision rules, and evidence artifacts. Documentation, navigation, examples, or later package releases do not retroactively change those scientific records.

The archived v0.1.0 Zenodo deposit also remains a version-specific software archive for that release.

## Recommended citation practice

For manuscripts or archived analyses, record all three when applicable:

1. the installed GazeAudit package version;
2. the Git commit used for development functionality not represented by the installed release;
3. the DOI or frozen validation artifact when relying on a protocol-bound archived record.

This separates software identity, documentation identity, and scientific-evidence identity rather than collapsing them into one version label.
