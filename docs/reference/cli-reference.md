---
title: CLI reference
description: Installed GazeAudit console commands, their intended scope, exact reviewer-revision package syntax, exit behavior, and validation-programme boundaries.
kicker: Reference · CLI
page_type: reference
permalink: /docs/reference/cli-reference/
search_category: Reference
search_keywords: cli command console script help revision package init validate gazebase korthals pedrotti source intake freeze
---

# CLI reference

GazeAudit exposes console commands through the package's `[project.scripts]` table. This page records **what is installed and what each command is for**. It is reference material, not a recommendation to run validation-infrastructure commands on unrelated data.

## Installed console scripts

| Command | Entry point | Intended scope |
|---|---|---|
| `gazeaudit-revision-package` | `gazeaudit.revision_package_cli:main` | general reviewer-revision provenance scaffold and structural validation |
| `gazeaudit-gazebase-run` | `gazeaudit.gazebase_cli:main` | GazeBase validation execution |
| `gazeaudit-korthals-source-intake` | `gazeaudit.korthals_source_cli:main` | Korthals validation source intake |
| `gazeaudit-korthals-source-freeze` | `gazeaudit.korthals_freeze_cli:main` | Korthals validation source freeze |
| `gazeaudit-korthals-source-intake-v2` | `gazeaudit.korthals_source_v2_cli:main` | Korthals v2 validation source intake |
| `gazeaudit-korthals-source-freeze-v2` | `gazeaudit.korthals_freeze_v2_cli:main` | Korthals v2 validation source freeze |
| `gazeaudit-pedrotti-source-intake` | `gazeaudit.pedrotti_source_cli:main` | Pedrotti/de Chambrier validation source intake |
| `gazeaudit-pedrotti-source-freeze` | `gazeaudit.pedrotti_freeze_cli:main` | Pedrotti/de Chambrier validation source freeze |

The seven case-specific commands are validation infrastructure. Their scientific meaning is tied to frozen source/protocol contracts. Start with the [validation matrix]({{ '/docs/VALIDATION_MATRIX.html' | relative_url }}) before using them.

## General reviewer-revision command

### Show help

```bash
gazeaudit-revision-package --help
gazeaudit-revision-package init --help
gazeaudit-revision-package validate --help
```

### Create a scaffold

```bash
gazeaudit-revision-package init \
  --output-dir revision-package \
  --project-slug my-study \
  --review-round 1
```

Required arguments:

| Argument | Meaning |
|---|---|
| `--output-dir` | directory in which the governed revision scaffold is created |
| `--project-slug` | project identifier recorded in the package |
| `--review-round` | integer review round; defaults to `1` when omitted |
| `--overwrite` | optional; replaces only known scaffold files and does not delete unrelated files |

The command writes a canonical JSON summary to standard output containing the action, output directory, schema, manifest fingerprint, and required-file count.

### Validate an existing scaffold

```bash
gazeaudit-revision-package validate --root revision-package
```

`--root` is required and points to the package root.

Validation is **structural**. It checks the governed package structure and manifest integrity; it does not decide whether an analysis is scientifically valid, whether a reviewer request is justified, or whether a manuscript is ready for acceptance.

### Exit behavior

- `init` returns exit status **0** after successfully writing the scaffold.
- `validate` returns **0** when the structural result is valid.
- `validate` returns **2** when structural validation completes but reports `valid: false`.
- argument/parser errors follow normal `argparse` command-line behavior.

## Validation-programme commands

The remaining installed commands exist to reproduce or freeze specific validation pipelines. They are intentionally not presented as general-purpose research-data importers.

| Family | Commands | Boundary |
|---|---|---|
| GazeBase | `gazeaudit-gazebase-run` | protocol-bound GazeBase execution |
| Korthals | source-intake/source-freeze, including v2 | protocol-bound Korthals source and execution provenance |
| Pedrotti/de Chambrier | source-intake/source-freeze | protocol-bound Pedrotti/de Chambrier source and execution provenance |

Use each command's `--help` output and the matching frozen protocol/result record together. Do not infer a reusable scientific threshold from a case-specific CLI default or argument.

## Installation identity

For the stable release:

```bash
python -m pip install gazeaudit==0.2.0
```

When using unreleased functionality from `main`, record the exact Git commit. The [documentation provenance page]({{ '/docs/reference/site-provenance/' | relative_url }}) explains why the site revision and installed package version must not be conflated.

## Runnable companion

The [revision-package quickstart]({{ '/docs/examples/revision-package-quickstart/' | relative_url }}) is the runnable how-to companion to this reference. The [reference lookup walkthrough]({{ '/docs/examples/reference-lookup-workflow/' | relative_url }}) shows when to consult this page rather than a longer workflow guide.
