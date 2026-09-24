---
title: GazeAudit 0.2.0 external publication record
description: Human-readable verification record for the GazeAudit v0.2.0 GitHub Release and PyPI publication, including exact payload hashes and the Zenodo boundary.
kicker: Reference · Release provenance
permalink: /docs/EXTERNAL_PUBLICATION_0.2.0.html
search_category: Reference
search_keywords: 0.2.0 release PyPI GitHub trusted publishing hash checksum Zenodo provenance publication
---

# GazeAudit 0.2.0 — verified GitHub Release and PyPI publication

This page is the human-readable companion to the machine-readable [`release/0.2.0-external-publication-verification.json`](https://github.com/stefanosbalaskas/GazeAudit/blob/main/release/0.2.0-external-publication-verification.json).

It records **publication verification**, not a new scientific analysis. The protocol-bound GazeBase, Korthals, and Pedrotti/de Chambrier scientific outcomes remain unchanged.

## Release identity

- version: `0.2.0`
- tag: `v0.2.0`
- qualified source commit: `8820ba5242b28d270571da1121b86f74f316b764`
- qualified source tree: `0c441bebe03c398a5fe8d0df42e27234d83524b9`
- verification date: `2026-09-21`

## GitHub Release

Status: **published and verified**

[Open the v0.2.0 GitHub Release](https://github.com/stefanosbalaskas/GazeAudit/releases/tag/v0.2.0).

The verified release payload contains exactly:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `gazeaudit-0.2.0-py3-none-any.whl` | 216,463 | `8dc971d1fa50b6ccb756b2ab37dfb83133a460282b286db97d2b8514b0a72f2f` |
| `gazeaudit-0.2.0.tar.gz` | 918,267 | `df89592e6cdc6c2c322fa7ccf075b58b813dac35f19bf2bd68c64d64c29343b4` |

The preserved GitHub publication payload artifact has SHA-256 `81085c379597b60fc81b207ed6a89e868caf1049d084a89d6287e0abae1d15e8`.

## PyPI

Status: **published and verified**

[Open gazeaudit 0.2.0 on PyPI](https://pypi.org/project/gazeaudit/0.2.0/).

Publication used **GitHub OIDC Trusted Publishing**. The preserved PyPI payload artifact has SHA-256 `dbcf991910860779ed9c9a11d52df28c7c9b1330a6632e965c3cec78e7d3661a`.

A clean-install verification on Python 3.12 installed the package from public PyPI, imported `gazeaudit` successfully, and reported installed version `0.2.0`.

The wheel and source-distribution hashes verified from PyPI are identical to the GitHub Release hashes above.

## Zenodo boundary

The v0.2.0 publication record states `not_published_in_this_tranche` for Zenodo.

Therefore GazeAudit **does not claim a version-specific Zenodo DOI for v0.2.0**.

The DOI `10.5281/zenodo.22757340` remains the version-specific archive for **v0.1.0**, not v0.2.0.

## Scientific-record boundary

The publication verification record preserves these existing protocol-bound outcomes:

- GazeBase: `incomplete`
- Korthals: `robust_negative`
- Pedrotti/de Chambrier: `materially_fragile`

Those labels are scientific records governed by their own protocols and evidence. Successful software publication does not strengthen, weaken, or reinterpret them.

## Reproducibility use

When an analysis used v0.2.0:

1. record `gazeaudit==0.2.0`;
2. cite the software using the repository's current [`CITATION.cff`](https://github.com/stefanosbalaskas/GazeAudit/blob/main/CITATION.cff);
3. record the exact Git commit as well if the analysis relied on development code beyond the release;
4. do not attach the v0.1.0 Zenodo DOI to v0.2.0.

See [Documentation provenance]({{ '/docs/reference/site-provenance/' | relative_url }}) for the distinction between release, current documentation, and frozen scientific evidence.
