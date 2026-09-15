from __future__ import annotations

import re
from pathlib import Path

import gazeaudit

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_IDS = {
    "structural-qc",
    "readiness-governance",
    "aoi-uncertainty",
    "specification-robustness",
    "sampling-sensitivity",
    "missingness-sensitivity",
    "spatial-sensitivity",
    "known-truth-recovery",
    "publication-provenance",
    "interoperability",
}
EXPECTED_PHASES = {
    "preflight",
    "governance",
    "measurement",
    "robustness",
    "sensitivity",
    "benchmarking",
    "evidence",
    "integration",
}


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _catalog_ids(catalog: str) -> set[str]:
    return set(re.findall(r"^- id: ([a-z0-9-]+)$", catalog, flags=re.MULTILINE))


def _phase_keys(catalog: str) -> set[str]:
    return set(re.findall(r"^  phase_key: ([a-z]+)$", catalog, flags=re.MULTILINE))


def _catalog_functions(catalog: str) -> set[str]:
    functions: set[str] = set()
    in_functions = False
    for line in catalog.splitlines():
        if line == "  functions:":
            in_functions = True
            continue
        if in_functions and line.startswith("    - "):
            functions.add(line.removeprefix("    - ").strip())
            continue
        if in_functions and not line.startswith("    "):
            in_functions = False
    return functions


def test_method_catalog_has_ten_unique_families_and_eight_phases() -> None:
    catalog = _text("_data/methods.yml")
    assert _catalog_ids(catalog) == EXPECTED_IDS
    assert len(re.findall(r"^- id:", catalog, flags=re.MULTILINE)) == 10
    assert _phase_keys(catalog) == EXPECTED_PHASES


def test_method_catalog_names_only_public_package_api() -> None:
    functions = _catalog_functions(_text("_data/methods.yml"))
    assert functions
    missing = sorted(name for name in functions if not hasattr(gazeaudit, name))
    assert missing == []


def test_method_explorer_page_has_progressive_filters_and_exact_phase_count() -> None:
    page = _text("docs/methods/index.md")
    assert 'page_type: methods' in page
    assert 'data-method-explorer' in page
    assert 'data-method-controls hidden' in page
    assert 'data-method-search' in page
    assert '<strong>8</strong><span>research phases</span>' in page
    assert '{% for method in site.data.methods %}' in page
    for phase in EXPECTED_PHASES:
        assert f'data-method-filter="{phase}"' in page


def test_method_explorer_preserves_evidence_type_boundaries() -> None:
    catalog = _text("_data/methods.yml")
    page = _text("docs/methods/index.md")
    assert "Synthetic known-truth benchmark by design" in catalog
    assert "live contract CI" in catalog
    assert "not a generic spatial-sensitivity benchmark" in catalog
    assert "Evidence is not filled in for appearance" in page
    assert "`incomplete`" in page
    assert "`robust_negative`" in page
    assert "`materially_fragile`" in page
    assert "Synthetic benchmarks and CI interoperability checks are not silently promoted" in page


def test_method_explorer_interactions_preserve_url_state_and_catalog_identity() -> None:
    script = _text("assets/js/methods.js")
    assert "new URLSearchParams(window.location.search)" in script
    assert "window.history.replaceState" in script
    assert "navigator.clipboard" in script
    assert "root.dataset.catalogState" in script
    assert "fetch(indexUrl)" in script
    assert "sameIds" in script


def test_layout_wires_method_explorer_only_on_method_pages() -> None:
    layout = _text("_layouts/default.html")
    assert "'/docs/methods/' | relative_url" in layout
    assert "page.page_type == 'methods'" in layout
    assert "'/assets/css/methods.css' | relative_url" in layout
    assert "'/assets/js/methods.js' | relative_url" in layout


def test_method_index_is_generated_from_the_governed_catalog() -> None:
    source = _text("assets/method-index.json")
    assert "layout: null" in source
    assert "site.data.methods | jsonify" in source


def test_method_explorer_is_discoverable_from_docs_and_search() -> None:
    docs = _text("docs/index.md")
    search = _text("assets/search-index.json")
    assert "[Method explorer](methods/)" in docs
    assert '"title":"Method explorer"' in search
    assert '"url":"/docs/methods/"' in search


def test_generated_site_verifier_governs_method_catalog_and_assets() -> None:
    verifier = _text("tools/check_docs_site.py")
    assert "def _verify_method_index" in verifier
    assert '"docs/methods/index.html"' in verifier
    assert '"assets/method-index.json"' in verifier
    assert '"assets/css/methods.css"' in verifier
    assert '"assets/js/methods.js"' in verifier
    assert "len(methods) != 10" in verifier
    assert "phases != expected_phases" in verifier
