from __future__ import annotations

import json
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "docs" / "install.md"
GUIDE = ROOT / "docs" / "guides" / "environment-setup.md"
EXAMPLE = ROOT / "docs" / "examples" / "install-smoke-check.md"
DATA = ROOT / "_data" / "install_reference.json"
SCRIPT = ROOT / "assets" / "js" / "install-builder.js"
CSS = ROOT / "assets" / "css" / "install.css"
LAYOUT = ROOT / "_layouts" / "default.html"
DOCS_INDEX = ROOT / "docs" / "index.md"
GUIDES_INDEX = ROOT / "docs" / "guides" / "index.md"
EXAMPLES_INDEX = ROOT / "docs" / "examples" / "index.md"
REFERENCE = ROOT / "docs" / "reference" / "index.md"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"
GOVERNANCE = ROOT / "tools" / "check_site_governance.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _metadata() -> dict[str, object]:
    return json.loads(_text(DATA))


def test_generated_install_metadata_has_expected_package_contract() -> None:
    metadata = _metadata()

    assert metadata["schema"] == "gazeaudit-install-reference-v1"
    assert metadata["name"] == "gazeaudit"
    assert metadata["version"] == version("gazeaudit")
    assert metadata["requires_python"] == ">=3.10"
    assert metadata["tested_python_versions"] == ["3.10", "3.11", "3.12", "3.13"]
    assert metadata["dependencies"] == [
        "numpy>=1.24",
        "packaging>=23",
        "pandas>=2.0",
    ]


def test_generated_install_metadata_covers_all_extras_and_scripts() -> None:
    metadata = _metadata()
    extras = metadata["extras"]
    scripts = metadata["scripts"]

    assert set(extras) == {
        "test",
        "dev",
        "plot",
        "pymovements",
        "peyes",
        "interop",
        "gazebase",
    }
    assert len(scripts) == 8
    assert scripts["gazeaudit-revision-package"] == "gazeaudit.revision_package_cli:main"
    assert "python_version >= '3.12'" in " ".join(extras["peyes"])


def test_install_page_uses_generated_metadata_and_static_fallbacks() -> None:
    text = _text(INSTALL)

    assert "site.data.install_reference" in text
    assert "data-install-builder" in text
    assert "data-package=\"{{ install.name }}\"" in text
    assert "data-version=\"{{ install.version }}\"" in text
    assert "Without JavaScript, use the static commands" in text
    assert "{{ install.dependencies | size }}" in text
    assert "{{ install.scripts | size }}" in text


def test_install_builder_has_labels_status_and_exact_command_shapes() -> None:
    page = _text(INSTALL)
    script = _text(SCRIPT)

    for token in (
        "<fieldset>",
        "<legend>Installation source</legend>",
        'label for="install-extra"',
        'role="status"',
        'aria-live="polite"',
        'aria-atomic="true"',
        "data-copy-install",
    ):
        assert token in page

    for token in (
        "python -m pip install -e .",
        'python -m pip install -e ".[${selectedExtra}]"',
        'python -m pip install "${target}==${version}"',
        "navigator.clipboard",
        "Clipboard access is unavailable",
    ):
        assert token in script


def test_install_builder_styles_cover_responsive_and_forced_colour_modes() -> None:
    css = _text(CSS)

    for selector in (
        ".install-summary-grid",
        ".install-platform-grid",
        ".install-builder",
        ".install-command",
        ".install-command-head",
    ):
        assert selector in css

    assert "@media (max-width: 680px)" in css
    assert "@media (forced-colors: active)" in css


def test_environment_guidance_separates_software_from_scientific_decisions() -> None:
    page = _text(INSTALL)
    guide = _text(GUIDE)
    example = _text(EXAMPLE)

    assert "do not choose a scientific method" in page
    assert "Passing installation or import checks establishes software availability" in page
    assert "Keep environment evidence separate from scientific decisions" in guide
    assert "A packaging extra means" in guide
    assert "This example checks **software installation only**" in example
    assert "It does not establish:" in example


def test_install_routes_are_discoverable_across_navigation_and_hubs() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS_INDEX)
    guides = _text(GUIDES_INDEX)
    examples = _text(EXAMPLES_INDEX)
    reference = _text(REFERENCE)

    assert layout.count("/docs/install/") >= 3
    assert "/assets/css/install.css" in layout
    assert "/assets/js/install-builder.js" in layout
    assert "[Install & environment center](install/)" in docs
    assert 'href="environment-setup/">Environment setup →</a>' in guides
    assert 'href="install-smoke-check/">Install smoke check →</a>' in examples
    assert "[Install & environment center]" in reference


def test_install_routes_and_assets_are_ci_governed() -> None:
    check = _text(SITE_CHECK)
    governance = _text(GOVERNANCE)

    for path in (
        "docs/install/index.html",
        "docs/guides/environment-setup/index.html",
        "docs/examples/install-smoke-check/index.html",
        "assets/js/install-builder.js",
        "assets/css/install.css",
    ):
        assert f'"{path}"' in check

    assert '"/docs/install/"' in governance
    assert 'ROOT / "docs" / "install.md"' in governance
