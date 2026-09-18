from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPASS = ROOT / "docs" / "documentation-map.md"
AUTHORING = ROOT / "docs" / "guides" / "documentation-authoring.md"
EXAMPLE = ROOT / "docs" / "examples" / "documentation-intent-routing.md"
DOCS = ROOT / "docs" / "index.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
EXAMPLES = ROOT / "docs" / "examples" / "index.md"
REFERENCE = ROOT / "docs" / "reference" / "index.md"
ARTICLES = ROOT / "docs" / "articles" / "index.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "enhancements.css"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_documentation_compass_has_four_distinct_reader_intents() -> None:
    text = _text(COMPASS)

    assert "permalink: /docs/documentation-map/" in text
    for label in ("Learn", "Do", "Look up", "Understand"):
        assert f'>{label}<' in text

    for route in (
        "/docs/getting-started/",
        "/docs/guides/",
        "/docs/reference/",
        "/docs/articles/",
        "/docs/case-studies/",
        "/docs/VALIDATION_MATRIX.html",
    ):
        assert route in text

    assert "navigation support, not a scientific decision rule" in text
    assert "The pages are related, but they should not collapse into one giant page" in text


def test_documentation_authoring_standard_protects_content_and_scientific_boundaries() -> None:
    text = _text(AUTHORING)

    assert "permalink: /docs/guides/documentation-authoring/" in text
    for contract in (
        "one dominant user intent",
        "Use predictable heading structure",
        "Write code examples for copying and adaptation",
        "Make examples reconstructable",
        "Keep reference material factual",
        "Keep procedures goal-oriented",
        "Prefer semantic HTML and native controls",
        "Provide more than one discovery route",
        "Use front matter consistently",
        "Link instead of duplicating authority",
        "Run the documentation gates",
    ):
        assert contract in text

    for boundary in (
        "software default ≠ scientific recommendation",
        "Python-required argument ≠ scientifically mandatory construct",
        "synthetic demonstration ≠ empirical validation",
        "successful execution ≠ valid inference",
        "structural provenance ≠ scientific validity",
        "navigation ranking ≠ method ranking",
        "frozen case outcome ≠ universal property",
    ):
        assert boundary in text


def test_documentation_intent_example_keeps_purposes_separate() -> None:
    text = _text(EXAMPLE)

    assert "fully synthetic documentation-navigation exercise" in text
    assert "Learn the workflow" in text
    assert "Do the real task" in text
    assert "Look up the exact contract" in text
    assert "Understand the rationale" in text
    assert "Check the evidence boundary" in text
    assert "run_specs(study, space, endpoint)" in text
    assert "The topic stayed the same. The **reader's intent changed**." in text
    assert "Search ranking is navigation support" in text


def test_compass_routes_are_visible_from_hubs_and_navigation() -> None:
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    articles = _text(ARTICLES)
    layout = _text(LAYOUT)

    assert 'href="documentation-map/">Open the full Documentation compass →</a>' in docs
    assert 'href="documentation-authoring/">Documentation authoring standard →</a>' in guides
    assert 'href="documentation-intent-routing/">Documentation intent routing →</a>' in examples
    assert "Documentation compass" in reference
    assert "Documentation compass" in articles

    assert layout.count("/docs/documentation-map/") >= 3
    assert "/docs/guides/documentation-authoring/" in layout
    assert "/docs/examples/documentation-intent-routing/" in layout


def test_documentation_compass_has_responsive_and_forced_colour_styles() -> None:
    css = _text(CSS)

    for contract in (
        ".documentation-compass",
        ".documentation-compass-card",
        ".documentation-compass-mode",
        "@media (max-width: 760px)",
        "@media (forced-colors: active)",
        "focus-within",
    ):
        assert contract in css


def test_generated_site_requires_documentation_architecture_routes() -> None:
    text = _text(SITE_CHECK)

    for path in (
        "docs/documentation-map/index.html",
        "docs/guides/documentation-authoring/index.html",
        "docs/examples/documentation-intent-routing/index.html",
    ):
        assert f'"{path}"' in text
