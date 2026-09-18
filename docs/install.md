---
title: Install & environment center
description: Install GazeAudit from the public release or a source checkout, choose optional extras, verify the environment, and understand Python/CLI compatibility from generated package metadata.
kicker: Start · Install
page_type: install
permalink: /docs/install/
search_category: Start
search_keywords: install installation pip venv virtual environment python version extras pymovements peyes plot interop gazebase setup compatibility command
---

# Install & environment center

Use this page to answer four setup questions before starting an analysis:

1. **Which GazeAudit version am I installing?**
2. **Which Python versions are supported and currently tested?**
3. **Which optional dependency set do I actually need?**
4. **How do I verify that the installed environment matches what I intended?**

{% assign install = site.data.install_reference %}

<div class="callout info">
<strong>Generated from package metadata.</strong>
The version, Python requirement, base dependencies, extras, tested Python matrix, and console scripts on this page come from <code>pyproject.toml</code> and the repository test workflow. CI regenerates the metadata and fails if this reference drifts.
</div>

## Current compatibility snapshot

<div class="install-summary-grid">
  <article>
    <span>Public release</span>
    <strong>{{ install.version }}</strong>
  </article>
  <article>
    <span>Declared Python</span>
    <strong>{{ install.requires_python }}</strong>
  </article>
  <article>
    <span>CI-tested Python</span>
    <strong>{{ install.tested_python_versions | join: ', ' }}</strong>
  </article>
  <article>
    <span>Base dependencies</span>
    <strong>{{ install.dependencies | size }}</strong>
  </article>
</div>

The site documents the current `main` branch as well as release **{{ install.version }}**. If reproducibility matters, record the installed package version and, for source checkouts, the exact Git commit. The [Docs provenance reference]({{ '/docs/reference/site-provenance/' | relative_url }}) explains the distinction.

## 1. Create an isolated environment

PyPA recommends using a virtual environment for third-party packages so project dependencies do not interfere with other Python environments.

<div class="install-platform-grid">
  <section>
    <h3>Windows</h3>
    <pre><code class="language-powershell">py -m venv .venv
.venv\Scripts\activate
py -m pip install --upgrade pip</code></pre>
  </section>
  <section>
    <h3>macOS / Linux</h3>
    <pre><code class="language-bash">python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip</code></pre>
  </section>
</div>

After activation, `python -m pip` should point into the new environment.

## 2. Build the install command

The controls below only build a package-install command. They do not choose a scientific method, detector, threshold, AOI definition, or analysis pipeline.

<p id="install-builder-help">Choose the source and optional capability. The command updates immediately; all controls have labels and the generated command is also announced as status text.</p>

<form class="install-builder" data-install-builder
      data-package="{{ install.name }}"
      data-version="{{ install.version }}"
      aria-describedby="install-builder-help">
  <fieldset>
    <legend>Installation source</legend>
    <label>
      <input type="radio" name="install-source" value="release" checked>
      Public release {{ install.version }}
    </label>
    <label>
      <input type="radio" name="install-source" value="source">
      Current source checkout (editable)
    </label>
  </fieldset>

  <div class="install-field">
    <label for="install-extra">Optional capability</label>
    <select id="install-extra" data-install-extra>
      <option value="">Core package only</option>
      {% for extra in install.extras %}
      <option value="{{ extra[0] }}">{{ extra[0] }}</option>
      {% endfor %}
    </select>
    <span>Choose only the extra required by the software capability you plan to use.</span>
  </div>

  <div class="install-command" aria-labelledby="install-command-title">
    <div class="install-command-head">
      <strong id="install-command-title">Generated install command</strong>
      <button type="button" data-copy-install>Copy command</button>
    </div>
    <pre><code data-install-command>python -m pip install {{ install.name }}=={{ install.version }}</code></pre>
    <p data-install-status role="status" aria-live="polite" aria-atomic="true">Core public release command selected.</p>
  </div>
</form>

Without JavaScript, use the static commands and dependency tables below.

## 3. Choose the smallest relevant extra

PyPA extras add optional dependencies to the base package; they do not replace the base dependencies.

<div class="table-wrap">
<table>
  <thead>
    <tr>
      <th scope="col">Extra</th>
      <th scope="col">Adds</th>
      <th scope="col">Typical software purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>plot</code></td>
      <td>{{ install.extras.plot | join: '<br>' }}</td>
      <td>Generate GazeAudit figures with Matplotlib.</td>
    </tr>
    <tr>
      <td><code>pymovements</code></td>
      <td>{{ install.extras.pymovements | join: '<br>' }}</td>
      <td>Use the pymovements adapter.</td>
    </tr>
    <tr>
      <td><code>peyes</code></td>
      <td>{{ install.extras.peyes | join: '<br>' }}</td>
      <td>Use the pEYES detector bridge; its dependency marker currently requires Python 3.12+.</td>
    </tr>
    <tr>
      <td><code>interop</code></td>
      <td>{{ install.extras.interop | join: '<br>' }}</td>
      <td>Install both supported interoperability dependency families where environment markers permit.</td>
    </tr>
    <tr>
      <td><code>gazebase</code></td>
      <td>{{ install.extras.gazebase | join: '<br>' }}</td>
      <td>Reproduce the repository's pinned GazeBase software environment.</td>
    </tr>
    <tr>
      <td><code>test</code></td>
      <td>{{ install.extras.test | join: '<br>' }}</td>
      <td>Run the test suite and coverage locally.</td>
    </tr>
    <tr>
      <td><code>dev</code></td>
      <td>{{ install.extras.dev | join: '<br>' }}</td>
      <td>Run development tests, coverage, and Ruff.</td>
    </tr>
  </tbody>
</table>
</div>

Examples for release {{ install.version }}:

```bash
python -m pip install "{{ install.name }}[plot]=={{ install.version }}"
python -m pip install "{{ install.name }}[pymovements]=={{ install.version }}"
python -m pip install "{{ install.name }}[peyes]=={{ install.version }}"
python -m pip install "{{ install.name }}[interop]=={{ install.version }}"
```

For a local repository checkout:

```bash
python -m pip install -e .
python -m pip install -e ".[plot]"
python -m pip install -e ".[dev]"
```

## 4. Know what is always installed

The base package declares:

{% for dependency in install.dependencies %}
- `{{ dependency }}`
{% endfor %}

These are package dependencies, not scientific-method endorsements. Dependency versions describe software compatibility constraints.

## 5. Verify the environment

Check the interpreter and installed release:

```bash
python --version
python -m pip show {{ install.name }}
python -c "import gazeaudit; print(gazeaudit.__version__)"
```

Then run a minimal import check:

```python
from gazeaudit import GazeStudy, PipelineSpace, aoi_probabilities

print("GazeAudit public imports are available.")
```

For a more structured verification exercise, use [Install → verify → first import]({{ '/docs/examples/install-smoke-check/' | relative_url }}).

## 6. Installed console commands

The package declares {{ install.scripts | size }} console-script entry points. Packaging tools create command wrappers for these names when the distribution is installed.

<div class="table-wrap">
<table>
  <thead>
    <tr>
      <th scope="col">Command</th>
      <th scope="col">Entry point</th>
    </tr>
  </thead>
  <tbody>
  {% for script in install.scripts %}
    <tr>
      <td><code>{{ script[0] }}</code></td>
      <td><code>{{ script[1] }}</code></td>
    </tr>
  {% endfor %}
  </tbody>
</table>
</div>

For the user-facing behavior of those commands, use the [CLI reference]({{ '/docs/reference/cli-reference/' | relative_url }}).

## 7. Record the environment for reproducibility

At minimum, preserve:

```bash
python --version
python -m pip show gazeaudit
python -m pip freeze > requirements-lock.txt
```

For a source checkout, also record:

```bash
git rev-parse HEAD
```

A freeze file records the resolved environment; it does not prove that every resolved dependency was scientifically necessary. Keep the environment record separate from the scientific decision log.

## Compatibility boundaries

- The package declares Python **{{ install.requires_python }}**.
- Repository CI currently tests Python **{{ install.tested_python_versions | join: ', ' }}**.
- A dependency's own environment marker can further narrow one optional feature. For example, the current pEYES dependency is conditional on Python 3.12+.
- Passing installation or import checks establishes software availability, not measurement validity or inferential robustness.
- The current documentation may describe post-release development on `main`; do not assume every `main` feature exists in PyPI release {{ install.version }}.

## Authoritative packaging references

- [PyPA: Install packages in a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
- [PyPA: Installing extras](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-extras)
- [PyPA: `pyproject.toml` project metadata](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [PyPA: Entry points specification](https://packaging.python.org/en/latest/specifications/entry-points/)

For GazeAudit-specific setup decisions, continue to [Environment setup & reproducibility]({{ '/docs/guides/environment-setup/' | relative_url }}).
