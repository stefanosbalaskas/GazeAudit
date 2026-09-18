from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "guides" / "find-information-fast.md"
EXAMPLE = ROOT / "docs" / "examples" / "search-to-contract.md"
REFERENCE = ROOT / "docs" / "reference" / "index.md"
GUIDES_INDEX = ROOT / "docs" / "guides" / "index.md"
EXAMPLES_INDEX = ROOT / "docs" / "examples" / "index.md"
DOCS_INDEX = ROOT / "docs" / "index.md"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_information_finding_guide_has_searchable_stable_route() -> None:
    text = _read(GUIDE)

    assert "permalink: /docs/guides/find-information-fast/" in text
    assert "search_category: Guide" in text
    assert "Ctrl/Cmd + K" in text
    assert "**/** when focus is not already inside a text field" in text


def test_guide_teaches_documentation_types_without_scientific_ranking() -> None:
    text = _read(GUIDE)

    for label in (
        "Guides",
        "Examples",
        "Reference",
        "Articles",
        "Workflows",
        "Validation matrix",
    ):
        assert label in text

    assert "does **not** decide which threshold" in text
    assert "top result is a scientific recommendation" in text


def test_guide_documents_grouped_search_and_type_filters() -> None:
    text = _read(GUIDE)

    assert "Search results are grouped by documentation type" in text
    assert "Use the type filter when the intent is already clear" in text
    assert "`run_specs` + **Reference**" in text
    assert "`revision package` + **Guide**" in text


def test_search_to_contract_example_is_explicitly_synthetic() -> None:
    text = _read(EXAMPLE)

    assert "fully synthetic documentation-navigation exercise" in text
    assert "does not validate an analysis" in text
    for query in ("run_specs NaN", "revision package", "AOI uncertainty", "robust_negative"):
        assert query in text


def test_search_to_contract_keeps_reference_and_procedure_distinct() -> None:
    text = _read(EXAMPLE)

    assert "**Reference** answers “what is the command?”" in text
    assert "**Example** answers “how does the workflow fit together?”" in text
    assert "There is no universal “best” result" in text


def test_reference_hub_exposes_copy_ready_routes() -> None:
    text = _read(REFERENCE)

    for route in (
        "GazeStudy → audit_study_qc → study_qc_diagnostics → build_study_qc_audit",
        "PipelineSpace → run_specs → specification_curve → effect_stability",
        "GaussianGazeErrorModel → aoi_probabilities",
        "gazeaudit-revision-package validate --root revision-package",
    ):
        assert route in text

    assert "automatically adds a **Copy** control to code blocks" in text
    assert "copying a route does not make its scientific choices appropriate" in text


def test_learning_routes_are_discoverable_from_hubs() -> None:
    guides = _read(GUIDES_INDEX)
    examples = _read(EXAMPLES_INDEX)
    docs = _read(DOCS_INDEX)

    assert 'href="find-information-fast/">Find information fast →</a>' in guides
    assert "Search → contract walkthrough" in guides
    assert 'href="search-to-contract/">Search → contract →</a>' in examples
    assert "[Find information fast](guides/find-information-fast/)" in docs
    assert "[Search → contract walkthrough](examples/search-to-contract/)" in docs


def test_generated_site_verifier_requires_new_learning_routes() -> None:
    text = _read(SITE_CHECK)

    for path in (
        "docs/reference/index.html",
        "docs/reference/cli-reference/index.html",
        "docs/reference/evidence-vocabulary/index.html",
        "docs/guides/find-information-fast/index.html",
        "docs/examples/search-to-contract/index.html",
    ):
        assert f'"{path}"' in text
