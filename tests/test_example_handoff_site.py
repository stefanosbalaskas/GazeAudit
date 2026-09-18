from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "enhancements.css"
GUIDE = ROOT / "docs" / "guides" / "adapt-examples-to-study.md"
EXAMPLE = ROOT / "docs" / "examples" / "example-to-study-handoff.md"
AUTHORING = ROOT / "docs" / "guides" / "documentation-authoring.md"
COMPASS = ROOT / "docs" / "documentation-map.md"
DOCS = ROOT / "docs" / "index.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
EXAMPLES = ROOT / "docs" / "examples" / "index.md"
README = ROOT / "README.md"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_shared_layout_exposes_documentation_intent_cues() -> None:
    text = _text(LAYOUT)

    for mapping in (
        "when 'Example'",
        "assign page_intent = 'Learn'",
        "when 'Guide'",
        "when 'Workflow'",
        "assign page_intent = 'Do'",
        "when 'Reference'",
        "assign page_intent = 'Look up'",
        "when 'Article'",
        "assign page_intent = 'Understand'",
        "when 'Case study'",
        "when 'Evidence'",
        "assign page_intent = 'Evidence'",
    ):
        assert mapping in text

    for contract in (
        'class="page-intent-cue"',
        'role="note"',
        'aria-label="Documentation intent"',
        'class="page-intent-badge"',
        'class="page-intent-note"',
        "/docs/documentation-map/",
    ):
        assert contract in text

    assert "Teaching example; adapt the workflow, not demonstration values." in text
    assert "reference is not a scientific recommendation" in text
    assert "outcomes are not universal properties" in text


def test_page_intent_cues_have_responsive_and_forced_colour_styles() -> None:
    text = _text(CSS)

    for contract in (
        ".page-intent-cue",
        ".page-intent-badge",
        ".page-intent-note",
        "@media (max-width: 620px)",
        "@media (forced-colors: active)",
        "focus-within",
    ):
        assert contract in text


def test_example_adaptation_guide_separates_structure_decisions_and_evidence() -> None:
    text = _text(GUIDE)

    assert "permalink: /docs/guides/adapt-examples-to-study/" in text
    assert "**Copy the workflow shape. Rebuild the scientific decisions.**" in text

    for concept in (
        "**software structure**",
        "**teaching value**",
        "**study decision**",
        "**evidence statement**",
        "Inventory every demonstration value",
        "Rebuild the endpoint from the research question",
        "Rebuild the specification space",
        "Rebuild AOIs and measurement assumptions",
        "Treat software defaults as interface behavior",
        "Run structural preflight before the scientific audit",
        "Preserve the handoff in a decision record",
        "Verify the complete execution record",
    ):
        assert concept in text

    for boundary in (
        "Do not promote demonstration values into study defaults",
        "A new endpoint is a new scientific record",
        "A successful run establishes execution, not scientific validity",
        "no synthetic output is being cited as empirical evidence",
    ):
        assert boundary in text


def test_example_to_study_walkthrough_is_explicitly_synthetic_and_nonprescriptive() -> None:
    text = _text(EXAMPLE)

    assert "permalink: /docs/examples/example-to-study-handoff/" in text
    assert "fully synthetic adaptation exercise" in text
    assert "Nothing on this page selects an AOI, threshold, endpoint, exclusion" in text
    assert "teaching_choices" in text
    assert '"levels": None' in text
    assert "The empty dictionary shown here is deliberate" in text
    assert "valid_if is not a tool for removing inconvenient results" in text
    assert "Keep the tutorial outside the evidence record" in text

    for item in (
        "declared specifications",
        "valid specifications",
        "valid successful specifications",
        "valid technical failures",
    ):
        assert item in text


def test_handoff_routes_are_discoverable_from_hubs_navigation_compass_and_readme() -> None:
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    layout = _text(LAYOUT)
    compass = _text(COMPASS)
    readme = _text(README)

    assert "[Adapt examples to your study](guides/adapt-examples-to-study/)" in docs
    assert "[Example → study handoff](examples/example-to-study-handoff/)" in docs
    assert 'href="adapt-examples-to-study/">Adapt examples to your study →</a>' in guides
    assert 'href="example-to-study-handoff/">Example → study handoff →</a>' in examples
    assert "/docs/guides/adapt-examples-to-study/" in layout
    assert "/docs/examples/example-to-study-handoff/" in layout
    assert "/docs/guides/adapt-examples-to-study/" in compass
    assert "/docs/guides/adapt-examples-to-study/" in readme


def test_authoring_standard_documents_intent_cue_governance() -> None:
    text = _text(AUTHORING)

    assert "page-intent cue" in text
    assert "`Example` → **Learn**" in text
    assert "`Guide` or `Workflow` → **Do**" in text
    assert "`Reference` → **Look up**" in text
    assert "`Article` → **Understand**" in text
    assert "`Case study` or `Evidence` → **Evidence**" in text
    assert "Do not select a category merely to obtain a preferred visual badge" in text


def test_generated_site_requires_example_handoff_routes() -> None:
    text = _text(SITE_CHECK)

    for path in (
        "docs/guides/adapt-examples-to-study/index.html",
        "docs/examples/example-to-study-handoff/index.html",
    ):
        assert f'"{path}"' in text
