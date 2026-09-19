from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "methods.yml"
PAGE = ROOT / "docs" / "reference" / "api-pathways.md"
EXAMPLE = ROOT / "docs" / "examples" / "function-to-evidence.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "api-pathways.css"
DOCS_INDEX = ROOT / "docs" / "index.md"
EXAMPLES_INDEX = ROOT / "docs" / "examples" / "index.md"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"
SITE_GOVERNANCE = ROOT / "tools" / "check_site_governance.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _catalog_functions(text: str) -> list[str]:
    functions: list[str] = []
    in_functions = False
    for line in text.splitlines():
        if line == "  functions:":
            in_functions = True
            continue
        if in_functions and line.startswith("    - "):
            functions.append(line.removeprefix("    - ").strip())
            continue
        if in_functions and line.startswith("  ") and not line.startswith("    "):
            in_functions = False
    return functions


def test_api_pathways_has_stable_reference_route_and_catalog_source() -> None:
    page = _read(PAGE)

    assert "permalink: /docs/reference/api-pathways/" in page
    assert "page_type: api-pathways" in page
    assert "search_category: Reference" in page
    assert "{% for method in site.data.methods %}" in page
    assert "{% assign symbol_id = function | downcase | replace: '_', '-' %}" in page
    assert 'id="api-{{ symbol_id }}"' in page
    assert 'href="#api-{{ symbol_id }}"' in page


def test_api_pathways_reuses_all_governed_method_context_fields() -> None:
    page = _read(PAGE)

    for field in (
        "method.question",
        "method.purpose",
        "method.functions",
        "method.guide_url",
        "method.guide_label",
        "method.example_url",
        "method.example_label",
        "method.plot_url",
        "method.plot_label",
        "method.evidence_url",
        "method.evidence_label",
        "method.evidence_note",
    ):
        assert field in page

    assert "does not maintain a second method taxonomy" in page
    assert "Navigation, not scientific recommendation" in page


def test_governed_catalog_symbols_are_unique_for_stable_fragments() -> None:
    functions = _catalog_functions(_read(CATALOG))

    assert len(functions) == 38
    assert len(functions) == len(set(functions))
    fragments = [f"api-{name.lower().replace('_', '-')}" for name in functions]
    assert len(fragments) == len(set(fragments))
    assert "api-run-specs" in fragments
    assert "api-aoi-probabilities" in fragments
    assert "api-read-bids-eyetrack" in fragments


def test_function_to_evidence_walkthrough_uses_real_symbol_fragments() -> None:
    text = _read(EXAMPLE)

    assert "fully synthetic documentation-navigation exercise" in text
    for fragment in (
        "#api-run-specs",
        "#api-aoi-probabilities",
        "#api-read-bids-eyetrack",
    ):
        assert fragment in text

    assert "GazeBase case stopped at completeness gate" in text
    assert "Korthals outcome is protocol-bound" in text
    assert "live software contract, not frozen empirical validation" in text


def test_api_pathways_is_static_first_and_responsive() -> None:
    layout = _read(LAYOUT)
    css = _read(CSS)

    assert layout.count("/docs/reference/api-pathways/") >= 3
    assert "page.page_type == 'api-pathways'" in layout
    assert "/assets/css/api-pathways.css" in layout

    for selector in (
        ".api-pathway-jumps",
        ".api-symbol-index",
        ".api-symbol-list",
        ".api-pathway-route-grid",
        ".api-pathway-evidence",
    ):
        assert selector in css

    assert "@media (max-width: 760px)" in css
    assert "@media (forced-colors: active)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css


def test_pathways_and_walkthrough_are_discoverable_and_ci_governed() -> None:
    docs = _read(DOCS_INDEX)
    examples = _read(EXAMPLES_INDEX)
    site_check = _read(SITE_CHECK)
    governance = _read(SITE_GOVERNANCE)

    assert "[API pathways](reference/api-pathways/)" in docs
    assert "[Function → evidence walkthrough](examples/function-to-evidence/)" in docs
    assert 'href="function-to-evidence/">Function → evidence →</a>' in examples

    assert '"docs/reference/api-pathways/index.html"' in site_check
    assert '"docs/examples/function-to-evidence/index.html"' in site_check
    assert '"assets/css/api-pathways.css"' in site_check
    assert '"/docs/reference/api-pathways/"' in governance
    assert 'ROOT / "docs" / "reference" / "api-pathways.md"' in governance
