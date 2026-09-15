from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CHOICES = {
    "incoming-data",
    "external-source",
    "aoi-boundary",
    "analysis-choices",
    "sampling-risk",
    "missingness-risk",
    "spatial-error-risk",
    "known-truth",
    "publication-record",
}


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _planner_ids(source: str) -> set[str]:
    return set(re.findall(r"^- id: ([a-z0-9-]+)$", source, flags=re.MULTILINE))


def _planner_method_ids(source: str) -> set[str]:
    methods: set[str] = set()
    in_methods = False
    for line in source.splitlines():
        if line == "  methods:":
            in_methods = True
            continue
        if in_methods and line.startswith("    - "):
            methods.add(line.removeprefix("    - ").strip())
            continue
        if in_methods and not line.startswith("    "):
            in_methods = False
    return methods


def _catalog_ids(source: str) -> set[str]:
    return set(re.findall(r"^- id: ([a-z0-9-]+)$", source, flags=re.MULTILINE))


def test_planner_has_nine_unique_explicit_rules() -> None:
    source = _text("_data/planner.yml")
    assert _planner_ids(source) == EXPECTED_CHOICES
    assert len(re.findall(r"^- id:", source, flags=re.MULTILINE)) == 9
    assert source.count("  reason:") == 9


def test_every_planner_method_exists_in_governed_method_catalog() -> None:
    planner_methods = _planner_method_ids(_text("_data/planner.yml"))
    catalog_methods = _catalog_ids(_text("_data/methods.yml"))
    assert planner_methods
    assert planner_methods <= catalog_methods


def test_planner_page_keeps_navigation_and_judgement_separate() -> None:
    page = _text("docs/planner/index.md")
    assert "page_type: planner" in page
    assert "Navigation, not scientific judgement" in page
    assert "does not choose thresholds" in page
    assert "does not automatically add missingness sensitivity" in page
    assert "does not copy that case's outcome onto your study" in page
    assert "site.data.planner" in page


def test_planner_interactions_are_shareable_and_deduplicated() -> None:
    script = _text("assets/js/planner.js")
    assert "Promise.all([fetch(plannerUrl)" in script
    assert "new Set()" in script
    assert "new URLSearchParams(window.location.search)" in script
    assert "window.history.replaceState" in script
    assert "navigator.clipboard.writeText(window.location.href)" in script
    assert "root.dataset.catalogState = 'verified'" in script
    assert "method-${method.id}" in script


def test_method_explorer_exposes_stable_method_anchors() -> None:
    page = _text("docs/methods/index.md")
    assert 'id="method-{{ method.id }}"' in page


def test_layout_wires_planner_only_on_planner_pages() -> None:
    layout = _text("_layouts/default.html")
    assert "'/docs/planner/' | relative_url" in layout
    assert "page.page_type == 'planner'" in layout
    assert "'/assets/css/planner.css' | relative_url" in layout
    assert "'/assets/js/planner.js' | relative_url" in layout


def test_planner_index_is_generated_from_governed_rules() -> None:
    source = _text("assets/planner-index.json")
    assert "layout: null" in source
    assert "site.data.planner | jsonify" in source


def test_planner_is_discoverable_from_docs_and_search() -> None:
    docs = _text("docs/index.md")
    search = _text("assets/search-index.json")
    assert "[Audit planner](planner/)" in docs
    assert '"title":"Audit planner"' in search
    assert '"url":"/docs/planner/"' in search


def test_generated_site_verifier_governs_planner_assets_and_routes() -> None:
    verifier = _text("tools/check_docs_site.py")
    assert "def _verify_planner_index" in verifier
    assert '"docs/planner/index.html"' in verifier
    assert '"assets/planner-index.json"' in verifier
    assert '"assets/css/planner.css"' in verifier
    assert '"assets/js/planner.js"' in verifier
    assert "planner methods missing from governed catalog" in verifier
