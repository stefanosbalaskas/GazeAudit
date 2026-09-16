from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_interpretation_guide_starts_with_completeness_and_endpoint() -> None:
    page = _text("docs/guides/interpret-audit-result.md")

    for contract in (
        "permalink: /docs/guides/interpret-audit-result/",
        "Interpretation starts with completeness, not with the most attractive estimate.",
        "Start from the **declared** specification space",
        "invalid_predeclared",
        "technical_failure",
        "data_unavailable",
        "not_run",
        "different branches estimate different scientific endpoints",
        "Separate direction from magnitude",
        "Describe the pattern before explaining it",
        "Descriptive sensitivity is not causal attribution.",
        "Check what the audit did not vary",
    ):
        assert contract in page


def test_interpretation_guide_preserves_researcher_ownership() -> None:
    page = _text("docs/guides/interpret-audit-result.md")

    assert "does **not** assign a universal robustness label" in page
    assert "should not be used to relabel the frozen GazeAudit case studies" in page
    assert "The researcher remains responsible" in page
    assert "The audit does not by itself establish that the factor caused the change." in page

    for unsupported_claim in (
        "causal effects of preprocessing choices",
        "posterior probabilities that one pipeline is correct",
        "evidence that the largest estimate is the best estimate",
        "permission to prune specifications after inspecting outcomes",
    ):
        assert unsupported_claim in page


def test_result_pattern_example_covers_four_distinct_synthetic_cases() -> None:
    page = _text("docs/examples/result-patterns.md")

    for contract in (
        "permalink: /docs/examples/result-patterns/",
        "Synthetic teaching material only.",
        "## Pattern A · Direction and magnitude both relatively stable",
        "## Pattern B · Direction stable, magnitude materially variable",
        "## Pattern C · Direction changes across defensible specifications",
        "## Pattern D · Execution incomplete",
        "-0.052",
        "+0.091",
        "technical_failure",
        "not_run",
        "The missing branches cannot be silently removed from the denominator.",
        "The table is an interpretation aid, not a classifier.",
    ):
        assert contract in page


def test_result_pattern_example_teaches_bounded_reporting() -> None:
    page = _text("docs/examples/result-patterns.md")

    assert "Direction is more stable than magnitude" in page
    assert "a single-direction summary would not represent the complete pattern" in page
    assert "the robustness audit remains incomplete relative to the original specification declaration" in page
    assert "Across-specification summaries were interpreted descriptively" in page

    for error in (
        "calling a result “robust” because most branches share one sign",
        "ignoring large magnitude variation when the sign is stable",
        "selecting one preferred branch from a sign-changing pattern",
        "deleting failed or unexecuted branches from the denominator",
        "treating a synthetic teaching pattern as a real-data case classification",
    ):
        assert error in page


def test_interpretation_routes_are_discoverable_across_site_hubs() -> None:
    guides = _text("docs/guides/index.md")
    examples = _text("docs/examples/index.md")
    workspace = _text("docs/workspace/index.md")
    articles = _text("docs/articles/index.md")

    assert "interpret-audit-result/" in guides
    assert "../examples/result-patterns/" in guides

    assert "result-patterns/" in examples
    assert "../guides/interpret-audit-result/" in examples

    for route in (
        "/docs/guides/interpret-audit-result/",
        "/docs/examples/result-patterns/",
    ):
        assert route in workspace

    assert "Already have completed robustness outputs?" in workspace
    assert "I already have robustness outputs:" in workspace

    assert "I already have outputs. What next?" in articles
    assert "../guides/interpret-audit-result/" in articles
    assert "../examples/result-patterns/" in articles
    assert "Synthetic teaching patterns and general methodological articles do not create or modify case-study classifications." in articles
