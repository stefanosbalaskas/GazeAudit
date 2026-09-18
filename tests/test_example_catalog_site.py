import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "docs" / "examples"
CATALOG = EXAMPLES / "catalog.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "example-catalog.css"
ENHANCEMENTS = ROOT / "assets" / "css" / "enhancements.css"
JS = ROOT / "assets" / "js" / "example-catalog.js"
INDEX_SOURCE = ROOT / "assets" / "example-index.json"
EXAMPLES_HUB = EXAMPLES / "index.md"
DOCS_HUB = ROOT / "docs" / "index.md"
COMPASS = ROOT / "docs" / "documentation-map.md"
AUTHORING = ROOT / "docs" / "guides" / "documentation-authoring.md"
README = ROOT / "README.md"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"
SEARCH_INDEX = ROOT / "assets" / "search-index.json"

ALLOWED_DATA = {
    "Synthetic",
    "Demo or user data",
    "Software-only",
    "Documentation-only",
}

ALLOWED_FOCUS = {
    "Data & QC",
    "Measurement uncertainty",
    "Robustness & sensitivity",
    "Interpretation & reporting",
    "Documentation & API",
    "Environment",
    "Project lifecycle",
    "Peer review & publication",
    "Reproducibility",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _front_matter(path: Path) -> str:
    text = _text(path)
    match = re.match(r"^---\n(?P<front>.*?)\n---\n", text, flags=re.DOTALL)
    assert match, f"missing front matter: {path}"
    return match.group("front")


def _field(front: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", front, flags=re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip('"').strip("'")


def _governed_example_paths() -> list[Path]:
    return sorted(
        path
        for path in EXAMPLES.glob("*.md")
        if path.name not in {"index.md", "catalog.md"}
    )


def test_every_worked_example_has_one_governed_contract() -> None:
    paths = _governed_example_paths()
    assert len(paths) == 33

    for path in paths:
        front = _front_matter(path)
        assert _field(front, "search_category") == "Example", path
        assert _field(front, "page_type") == "example", path

        data = _field(front, "example_data")
        focus = _field(front, "example_focus")
        reuse = _field(front, "example_reuse")
        output = _field(front, "example_output")
        boundary = _field(front, "example_boundary")

        assert data in ALLOWED_DATA, (path, data)
        assert focus in ALLOWED_FOCUS, (path, focus)
        assert reuse, path
        assert output, path
        assert boundary, path


def test_catalog_is_generated_from_example_front_matter() -> None:
    text = _text(CATALOG)

    for contract in (
        'page_type: example-catalog',
        'permalink: /docs/examples/catalog/',
        'site.pages | where: "search_category", "Example" | sort: "title"',
        'data-example-card',
        'data-example-data="{{ example.example_data | escape }}"',
        'data-example-focus="{{ example.example_focus | escape }}"',
        '{{ example.example_reuse }}',
        '{{ example.example_output }}',
        '{{ example.example_boundary }}',
        'data-example-catalog-search',
        'data-example-data-filter',
        'data-example-focus-filter',
        'data-example-catalog-clear',
        'data-example-catalog-status',
        'data-example-catalog-empty',
    ):
        assert contract in text

    assert "Catalog filters are navigation, not scientific recommendations" in text
    assert "All remain visible when JavaScript is unavailable." in text


def test_machine_readable_example_index_reuses_same_source() -> None:
    text = _text(INDEX_SOURCE)

    assert 'permalink: /assets/example-index.json' in text
    assert 'site.pages | where: "search_category", "Example" | sort: "title"' in text
    for field in (
        '"title"',
        '"url"',
        '"description"',
        '"data"',
        '"focus"',
        '"reuse"',
        '"output"',
        '"boundary"',
    ):
        assert field in text


def test_shared_layout_renders_example_contract_and_catalog_assets() -> None:
    text = _text(LAYOUT)

    assert "page.search_category == 'Example'" in text
    for field in (
        "page.example_data",
        "page.example_focus",
        "page.example_reuse",
        "page.example_output",
        "page.example_boundary",
    ):
        assert field in text

    for contract in (
        'class="example-contract"',
        'aria-label="Example contract"',
        "Expected output",
        "Evidence boundary",
        "/docs/examples/catalog/",
        "example-catalog.css",
        "example-catalog.js",
    ):
        assert contract in text


def test_catalog_filtering_is_progressive_and_accessible() -> None:
    js = _text(JS)
    css = _text(CSS)
    shared_css = _text(ENHANCEMENTS)

    for contract in (
        "data-example-catalog",
        "data-example-card",
        "card.hidden = !show",
        "Showing all",
        "Showing ${visible} of ${total} examples.",
        "search.focus()",
        "empty.hidden = visible !== 0",
    ):
        assert contract in js

    for contract in (
        ".example-catalog-controls",
        ".example-catalog-grid",
        ".example-catalog-card",
        ".example-catalog-empty",
        "@media (max-width: 700px)",
        "@media (forced-colors: active)",
        ":focus-visible",
    ):
        assert contract in css

    for contract in (
        ".example-contract",
        ".example-contract-boundary",
        "@media (forced-colors: active)",
    ):
        assert contract in shared_css


def test_example_catalog_and_selection_walkthrough_are_discoverable() -> None:
    examples = _text(EXAMPLES_HUB)
    docs = _text(DOCS_HUB)
    compass = _text(COMPASS)
    readme = _text(README)
    layout = _text(LAYOUT)

    assert 'href="catalog/">Example catalog</a>' in examples
    assert 'href="choose-the-right-example/">Choose the right example →</a>' in examples
    assert "[Example catalog](examples/catalog/)" in docs
    assert "[Choose the right example](examples/choose-the-right-example/)" in docs
    assert "/docs/examples/catalog/" in compass
    assert "/docs/examples/catalog/" in readme
    assert layout.count("/docs/examples/catalog/") >= 3


def test_authoring_standard_governs_example_contract_fields() -> None:
    text = _text(AUTHORING)

    for contract in (
        "Example contract metadata",
        "example_data:",
        "example_focus:",
        "example_reuse:",
        "example_output:",
        "example_boundary:",
        "The governed values for `example_data`",
        "The governed `example_focus` vocabulary",
        "Do not add an example to a separate manual taxonomy",
    ):
        assert contract in text


def test_example_contract_metadata_feeds_site_search() -> None:
    text = _text(SEARCH_INDEX)

    for field in (
        "item.example_data",
        "item.example_focus",
        "item.example_reuse",
        "item.example_output",
        "item.example_boundary",
    ):
        assert field in text


def test_generated_site_verifier_governs_example_catalog() -> None:
    text = _text(SITE_CHECK)

    for contract in (
        "def _verify_example_index",
        "invalid generated example index",
        "unexpected example catalog",
        "example catalog card count mismatch",
        "_verify_example_index(site_root, baseurl=baseurl)",
        '"docs/examples/catalog/index.html"',
        '"docs/examples/choose-the-right-example/index.html"',
        '"assets/example-index.json"',
        '"assets/css/example-catalog.css"',
        '"assets/js/example-catalog.js"',
    ):
        assert contract in text
