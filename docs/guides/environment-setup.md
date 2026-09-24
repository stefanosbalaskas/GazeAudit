---
title: Environment setup & reproducibility
description: Set up a GazeAudit environment that is isolated, explicit about extras, reproducible, and separable from scientific decision records.
kicker: Guide · Environment
permalink: /docs/guides/environment-setup/
search_category: Guide
search_keywords: environment setup reproducibility venv pip extras lock freeze version commit dependency python install
---

# Environment setup & reproducibility

A reproducible analysis starts before the first model is fit. The software environment should make it possible to answer:

- which GazeAudit release or source commit was used;
- which Python interpreter ran the analysis;
- which optional extras were installed;
- which concrete dependency versions resolved;
- whether the environment was isolated from unrelated projects.

This guide is about **software identity and reproducibility**. It does not decide scientific thresholds, exclusions, endpoints, or interpretation.

## 1. Use an isolated environment

PyPA recommends virtual environments for third-party packages because they isolate project dependencies from other Python installations.

Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Then confirm that the active interpreter and `pip` belong to the environment:

```bash
python --version
python -m pip --version
```

## 2. Choose release or source identity deliberately

For the public release:

```bash
python -m pip install gazeaudit==0.2.0
```

For a repository checkout used in development or review:

```bash
python -m pip install -e .
git rev-parse HEAD
```

The release version and source commit answer different provenance questions. Record whichever identity actually produced the analysis.

The [Install & environment center]({{ '/docs/install/' | relative_url }}) generates the exact release/source command from package metadata.

## 3. Install only the optional capability you need

GazeAudit uses packaging extras for optional dependency families. Examples include plotting, pymovements, pEYES, combined interoperability, tests, development tooling, and the pinned GazeBase reproduction environment.

A packaging extra means “install these additional software dependencies.” It does **not** mean the corresponding scientific method is automatically appropriate.

Examples:

```bash
python -m pip install "gazeaudit[plot]==0.2.0"
python -m pip install "gazeaudit[pymovements]==0.2.0"
python -m pip install "gazeaudit[peyes]==0.2.0"
```

The pEYES dependency currently carries a Python 3.12+ environment marker. That marker is a software compatibility rule, not a research recommendation.

## 4. Record both declared and resolved software identity

The package declaration describes allowed dependency ranges. Your environment resolves those ranges to concrete versions.

Preserve both views:

```bash
python -m pip show gazeaudit
python -m pip freeze > requirements-lock.txt
```

For a source checkout also preserve:

```bash
git rev-parse HEAD > gazeaudit-commit.txt
```

A resolved environment record improves reproducibility, but it does not establish that every package was scientifically necessary.

## 5. Keep environment evidence separate from scientific decisions

A useful project structure is:

```text
project/
├── environment/
│   ├── requirements-lock.txt
│   ├── gazeaudit-version.txt
│   └── gazeaudit-commit.txt
├── decisions/
│   └── audit-decision-log.md
├── data/
└── analysis/
```

The environment folder answers **what software ran**. The decision log answers **why the analysis choices were made**. Mixing those records makes both harder to audit.

## 6. Verify the installed interface before analysis

A minimal check:

```bash
python -c "import gazeaudit; print(gazeaudit.__version__)"
```

Then verify the specific public symbol needed by the workflow:

```python
from gazeaudit import GazeStudy, PipelineSpace

print(GazeStudy)
print(PipelineSpace)
```

For source-level signatures and revision-pinned implementation links, use [API pathways]({{ '/docs/reference/api-pathways/' | relative_url }}).

## 7. Distinguish compatibility from validation

These statements mean different things:

- **Package supports Python >=3.10** — declared installation requirement.
- **Repository tests Python 3.10–3.13** — current CI coverage.
- **An extra installs successfully** — dependency compatibility.
- **A CLI command starts** — software entry point exists.
- **A scientific result is robust** — a protocol-bound analytical conclusion.

Do not substitute one for another.

## 8. Update environments intentionally

When changing Python, GazeAudit, or optional dependencies:

1. create or refresh an isolated environment;
2. reinstall the intended release/source identity;
3. rerun import and workflow smoke checks;
4. regenerate the resolved dependency record;
5. rerun the analysis gates that depend on the changed environment;
6. preserve the previous environment record when it is part of a submitted or frozen analysis.

For reviewer-requested amendments, connect environment changes to the [peer-review revision checklist]({{ '/docs/guides/peer-review-revision-checklist/' | relative_url }}).

## Authoritative packaging guidance

The setup pattern follows PyPA guidance on virtual environments, extras, project metadata, and console entry points:

- [Install packages in a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
- [Installing extras](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-extras)
- [pyproject.toml specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [Entry points specification](https://packaging.python.org/en/latest/specifications/entry-points/)

For a runnable verification sequence, continue to [Install → verify → first import]({{ '/docs/examples/install-smoke-check/' | relative_url }}).
