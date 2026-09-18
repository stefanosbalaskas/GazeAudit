from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_INDEX = ROOT / "docs" / "reference" / "index.md"
CLI_REFERENCE = ROOT / "docs" / "reference" / "cli-reference.md"
VOCABULARY = ROOT / "docs" / "reference" / "evidence-vocabulary.md"
LOOKUP = ROOT / "docs" / "examples" / "reference-lookup-workflow.md"
DOCS_INDEX = ROOT / "docs" / "index.md"
EXAMPLES_INDEX = ROOT / "docs" / "examples" / "index.md"
LAYOUT = ROOT / "_layouts" / "default.html"
PYPROJECT = ROOT / "pyproject.toml"
MULTIVERSE = ROOT / "src" / "gazeaudit" / "multiverse.py"
REVISION_CLI = ROOT / "src" / "gazeaudit" / "revision_package_cli.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_reference_hub_has_directory_route_and_task_lookup() -> None:
    text = _read(REFERENCE_INDEX)
    assert "permalink: /docs/reference/" in text
    assert "search_category: Reference" in text
    assert "Use Reference when you already know **what you are trying to do**" in text
    for route in (
        "/docs/reference/api-map/",
        "/docs/reference/core-api-inventory/",
        "/docs/reference/cli-reference/",
        "/docs/reference/evidence-vocabulary/",
        "/docs/reference/site-provenance/",
        "/docs/VALIDATION_MATRIX.html",
    ):
        assert route in text


def test_cli_reference_covers_every_installed_console_script() -> None:
    pyproject = _read(PYPROJECT)
    reference = _read(CLI_REFERENCE)
    commands = (
        "gazeaudit-revision-package",
        "gazeaudit-gazebase-run",
        "gazeaudit-korthals-source-intake",
        "gazeaudit-korthals-source-freeze",
        "gazeaudit-korthals-source-intake-v2",
        "gazeaudit-korthals-source-freeze-v2",
        "gazeaudit-pedrotti-source-intake",
        "gazeaudit-pedrotti-source-freeze",
    )
    for command in commands:
        assert f"{command} =" in pyproject
        assert f"`{command}`" in reference


def test_revision_cli_reference_matches_source_contract() -> None:
    reference = _read(CLI_REFERENCE)
    source = _read(REVISION_CLI)
    for argument in (
        "--output-dir",
        "--project-slug",
        "--review-round",
        "--overwrite",
        "--root",
    ):
        assert argument in reference
        assert argument in source
    assert 'return 0 if result["valid"] else 2' in source
    assert "returns **2** when structural validation completes" in reference
    assert "structural" in reference.lower()
    assert "scientifically valid" in reference


def test_vocabulary_distinguishes_runtime_fields_from_audit_terms() -> None:
    text = _read(VOCABULARY)
    source = _read(MULTIVERSE)
    assert "technical failure | audit/recovery vocabulary" in text
    assert "**not a `run_specs()` enum**" in text
    assert "estimate = float(endpoint(processed, spec))" in source
    assert "math.isfinite" not in source
    assert "does **not** enforce finiteness" in text
    assert "non-finite endpoint" in text
    assert "not evidence of a zero/null effect" in text


def test_vocabulary_preserves_declared_valid_success_denominators() -> None:
    text = _read(VOCABULARY)
    for phrase in (
        "8 declared",
        "7 valid",
        "6 initially successful",
        "1 valid technical failure",
        "1 invalid-before-execution combination",
        "**6 successful / 7 valid**",
    ):
        assert phrase in text
    assert "The invalid-before-execution combination remains documented" in text


def test_reference_lookup_is_synthetic_and_uses_real_contracts() -> None:
    text = _read(LOOKUP)
    source = _read(MULTIVERSE)
    assert "fully synthetic teaching exercise" in text
    assert "No value, status, or outcome on this page is empirical validation evidence" in text
    assert "declared_count = space.size" in text
    assert "valid_specs = space.enumerate_specs(valid_if=valid_if)" in text
    assert "gazeaudit-revision-package init" in text
    assert "--output-dir revision-package" in text
    assert "gazeaudit-revision-package validate --root revision-package" in text
    assert "def run_specs(" in source


def test_reference_routes_are_available_without_navigation_javascript() -> None:
    layout = _read(LAYOUT)
    for route in (
        "/docs/reference/",
        "/docs/reference/api-map/",
        "/docs/reference/cli-reference/",
        "/docs/reference/evidence-vocabulary/",
    ):
        assert layout.count(route) >= 3
    assert "<span>Reference</span>" in layout
    assert '<p class="nav-label">Reference</p>' in layout


def test_documentation_and_examples_hubs_expose_reference_route() -> None:
    docs = _read(DOCS_INDEX)
    examples = _read(EXAMPLES_INDEX)
    assert "[Reference hub](reference/)" in docs
    assert "[CLI reference](reference/cli-reference/)" in docs
    assert "[Evidence vocabulary](reference/evidence-vocabulary/)" in docs
    assert "[Reference lookup walkthrough](examples/reference-lookup-workflow/)" in docs
    assert 'href="../reference/">Reference hub</a>' in examples
    assert "[Reference lookup walkthrough](reference-lookup-workflow/)" in examples


def test_reference_material_keeps_frozen_labels_protocol_bound() -> None:
    for text in (_read(REFERENCE_INDEX), _read(VOCABULARY), _read(LOOKUP)):
        assert "GazeBase" in text and "`incomplete`" in text
        assert "Korthals" in text and "`robust_negative`" in text
        assert "Pedrotti/de Chambrier" in text and "`materially_fragile`" in text
    lookup = _read(LOOKUP)
    assert "Those labels belong to their protocol-bound records" in lookup
    assert "synthetic exercise remains simply a synthetic reference exercise" in lookup
