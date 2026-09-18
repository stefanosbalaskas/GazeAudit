---
title: Install, verify, first import
description: A software-only GazeAudit smoke check for a fresh virtual environment, optional extras, package identity, public imports, and console commands.
kicker: Example · Setup
permalink: /docs/examples/install-smoke-check/
search_category: Example
search_keywords: install verify smoke check pip venv version import extras console command environment setup
page_type: example
example_data: "Software-only"
example_focus: "Environment"
example_reuse: "Installation verification workflow"
example_output: "Verified package identity, imports, CLI, and environment record"
example_boundary: "Successful installation does not establish scientific validity."
---

# Install → verify → first import

This example checks **software installation only**. Passing it means the requested package/interface is available in the environment; it does not validate a dataset, measurement model, detector, threshold, or scientific conclusion.

## 1. Create an isolated environment

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

Then upgrade `pip` inside the active environment:

```bash
python -m pip install --upgrade pip
```

## 2. Install the public release

Core installation:

```bash
python -m pip install gazeaudit==0.1.0
```

If this exercise also needs plotting:

```bash
python -m pip install "gazeaudit[plot]==0.1.0"
```

Use the [Install Center]({{ '/docs/install/' | relative_url }}) to generate other extras from the current package metadata instead of guessing their names.

## 3. Verify package identity

```bash
python --version
python -m pip show gazeaudit
python -c "import gazeaudit; print(gazeaudit.__version__)"
```

Record those outputs with the project if the environment will support a reproducible analysis.

## 4. Verify representative public imports

Create `smoke_check.py`:

```python
from gazeaudit import (
    GazeStudy,
    PipelineSpace,
    RectangleAOI,
    aoi_probabilities,
)

symbols = [
    GazeStudy,
    PipelineSpace,
    RectangleAOI,
    aoi_probabilities,
]

for symbol in symbols:
    print(f"{symbol.__name__}: available")
```

Run it:

```bash
python smoke_check.py
```

Expected structure:

```text
GazeStudy: available
PipelineSpace: available
RectangleAOI: available
aoi_probabilities: available
```

This verifies public import availability. It does not exercise a scientific workflow.

## 5. Inspect one exact signature

```python
import inspect

from gazeaudit import aoi_probabilities

print(inspect.signature(aoi_probabilities))
```

Compare it with the generated source-level card at [API pathways]({{ '/docs/reference/api-pathways/' | relative_url }}#api-aoi-probabilities).

## 6. Check an installed CLI entry point

After installation:

```bash
gazeaudit-revision-package --help
```

If the shell cannot find the command but the package is installed, confirm that the active environment's scripts directory is on `PATH`. Packaging tools create console-script wrappers in the environment's scripts directory; they do not control every shell's global `PATH`.

Use the [CLI reference]({{ '/docs/reference/cli-reference/' | relative_url }}) for command behavior.

## 7. Capture a minimal environment record

```bash
python --version > python-version.txt
python -m pip show gazeaudit > gazeaudit-package.txt
python -m pip freeze > requirements-lock.txt
```

For a source checkout:

```bash
git rev-parse HEAD > gazeaudit-commit.txt
```

## 8. Know what this smoke check cannot establish

A successful smoke check establishes:

- the interpreter launches;
- GazeAudit imports;
- representative public exports exist;
- requested optional dependencies can resolve in this environment;
- an installed console command can be located.

It does not establish:

- valid gaze coordinates;
- appropriate AOIs;
- acceptable missingness;
- justified exclusions;
- detector validity;
- robustness of a scientific conclusion.

Continue to [First real audit with your own data]({{ '/docs/guides/first-real-audit/' | relative_url }}) only after the environment is known and recorded.
