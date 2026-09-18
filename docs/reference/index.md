---
title: Reference
description: Exact GazeAudit API, CLI, evidence-vocabulary, release, validation, and documentation-provenance contracts for users who already know the task they need to perform.
kicker: Reference
page_type: reference
permalink: /docs/reference/
search_category: Reference
search_keywords: reference api cli commands status glossary vocabulary denominator provenance validation release exact contract lookup
---

# Reference

Use Reference when you already know **what you are trying to do** and need the exact contract, command, term, provenance rule, or authoritative record. If you need a sequence of actions instead, use the [Guides]({{ '/docs/guides/' | relative_url }}); if you want to learn by doing, use the [Examples]({{ '/docs/examples/' | relative_url }}).

<div class="callout info">
<strong>Reference states contracts; it does not choose research decisions.</strong>
These pages describe public APIs, installed commands, status vocabulary, software/documentation identity, and frozen evidence labels. They do not choose thresholds, exclusions, endpoints, validity rules, reviewer amendments, or manuscript conclusions.
</div>

## Choose by question

| I need to know… | Open | What it is authoritative for |
|---|---|---|
| which public function fits a task | [API map]({{ '/docs/reference/api-map/' | relative_url }}) | task → public API mapping and bounded purpose |
| every core public symbol in one compact inventory | [Core API inventory]({{ '/docs/reference/core-api-inventory/' | relative_url }}) | compact public-surface lookup |
| which command is actually installed and what its boundary is | [CLI reference]({{ '/docs/reference/cli-reference/' | relative_url }}) | console entry points declared by the package |
| what “declared”, “valid”, “technical failure”, or a frozen outcome label means | [Evidence vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }}) | terminology and denominator semantics |
| which repository revision built the documentation | [Documentation provenance]({{ '/docs/reference/site-provenance/' | relative_url }}) | release vs development-doc identity |
| what the canonical empirical validation outcome is | [Validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) | protocol-bound validation records |
| how to cite or reuse GazeAudit | [Citation & reuse]({{ '/docs/CITATION_AND_REUSE.html' | relative_url }}) | citation and reuse instructions |
| what shipped in v0.1.0 | [Release notes]({{ '/docs/RELEASE_NOTES_0.1.0.html' | relative_url }}) | stable-release scope |

## Public API

The [API map]({{ '/docs/reference/api-map/' | relative_url }}) is the practical entry point. It groups the public surface by canonical study representation, structural QC, readiness governance, AOI uncertainty, specification spaces, controlled sensitivity, publication provenance, plotting, BIDS, pymovements, pEYES, and validation-specific tooling.

The [core API inventory]({{ '/docs/reference/core-api-inventory/' | relative_url }}) is intentionally denser. Use it when you already know the symbol family and need a compact lookup rather than workflow guidance.

## Command line

The [CLI reference]({{ '/docs/reference/cli-reference/' | relative_url }}) is generated conceptually from the console scripts declared in `pyproject.toml`. It separates the general reviewer-revision package command from the specialised source-intake/freeze commands used by frozen validation programmes.

For a runnable reviewer-revision exercise, use the [revision-package quickstart]({{ '/docs/examples/revision-package-quickstart/' | relative_url }}).

## Evidence and denominator vocabulary

The [evidence vocabulary]({{ '/docs/reference/evidence-vocabulary/' | relative_url }}) distinguishes:

- the declared Cartesian specification space from the subset accepted by `valid_if`;
- a valid branch that executes successfully from a valid branch that fails technically;
- documentation-ledger terms from actual `run_specs()` return fields;
- non-finite endpoint values from scientific null effects;
- submitted evidence from later reviewer-requested amendments;
- general audit language from frozen, case-specific outcome labels.

Use the [reference lookup walkthrough]({{ '/docs/examples/reference-lookup-workflow/' | relative_url }}) for one synthetic example that moves between these references without turning them into scientific decision rules.

## Provenance and version identity

The stable public package release and the continuously updated documentation are different identities. The [documentation provenance page]({{ '/docs/reference/site-provenance/' | relative_url }}) records the exact GitHub Pages build revision and explains when to record the package version, development commit, and DOI or frozen artifact.

## Source-of-truth hierarchy

| Question | Primary authority |
|---|---|
| What does the installed public Python function do? | package source/docstring for the exact version or commit used |
| Which console command is installed? | `[project.scripts]` in `pyproject.toml` for the exact version or commit |
| What does a current reference page say? | this site at its displayed build revision |
| What did v0.1.0 ship? | the v0.1.0 release/tag and release notes |
| What is a frozen scientific validation outcome? | the validation matrix plus the case-specific frozen protocol/result record |

Reference pages can move forward on `main`; they do not rewrite frozen release assets or protocol-bound evidence.

## Frozen outcome boundary

The canonical validation outcomes remain:

- GazeBase: `incomplete`
- Korthals: `robust_negative`
- Pedrotti/de Chambrier: `materially_fragile`

These labels are **protocol-bound records**, not generic statuses to assign to a synthetic example, a new dataset, or an unrelated manuscript.

For action-oriented help, return to the [Documentation hub]({{ '/docs/' | relative_url }}) or [What should I do next?]({{ '/docs/guides/what-next/' | relative_url }}).
