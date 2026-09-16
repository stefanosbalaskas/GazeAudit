from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_common_audit_mistakes_maps_failures_to_repairs() -> None:
    page = _text("docs/guides/common-audit-mistakes.md")

    for contract in (
        "permalink: /docs/guides/common-audit-mistakes/",
        "Repair the record, not the result.",
        "Defining the specification space after seeing the outcome",
        "Silently removing failed specifications",
        "Letting the scientific endpoint drift",
        "Turning structural QC into an undocumented exclusion rule",
        "Hiding interpolation, imputation, or missingness repair",
        "Treating descriptive robustness variation as inferential uncertainty",
        "Rewriting the decision history",
        "Archiving the preferred result instead of the audit",
        "Transferring a frozen case-study label to new data",
    ):
        assert contract in page

    for status in (
        "valid and executed",
        "invalid by a **predeclared** rule",
        "technical failure",
        "not run, with an explicit reason",
    ):
        assert status in page


def test_common_mistakes_preserves_scientific_boundaries() -> None:
    page = _text("docs/guides/common-audit-mistakes.md")

    assert "protocol-bound records, not reusable ratings" in page
    assert "do **not** by themselves quantify sampling uncertainty" in page
    assert "Append; do not overwrite." in page
    assert "A repair should make the history more explicit." in page

    for frozen_status in ("`incomplete`", "`robust_negative`", "`materially_fragile`"):
        assert frozen_status in page


def test_publication_handoff_is_explicitly_synthetic_and_complete() -> None:
    page = _text("docs/examples/publication-archive-handoff.md")

    for contract in (
        "permalink: /docs/examples/publication-archive-handoff/",
        "All effect values and manuscript wording on this page are synthetic teaching material.",
        "12 declared specifications",
        "four positive estimates, four negative estimates, and four exactly zero",
        "-0.0404",
        "+0.0210",
        "median of `0.0000`",
        "publication-handoff/",
        "execution-status.csv",
        "methods-robustness.md",
        "results-robustness.md",
        "limitations.md",
        "fingerprints.txt",
        "This is an **illustrative archive layout**, not a required GazeAudit filesystem schema.",
    ):
        assert contract in page

    assert "Do not invent fingerprints manually" in page
    assert "not a confidence interval, posterior distribution, or causal decomposition" in page


def test_publication_handoff_teaches_bounded_methods_results_and_review() -> None:
    page = _text("docs/examples/publication-archive-handoff.md")

    for heading in (
        "## 5. Write Methods from the decision record, not from the preferred result",
        "## 6. Write Results from the complete pattern",
        "## 7. Separate results from limitations",
        "## 8. Bind software and provenance",
        "## 9. Add a human-readable manifest",
        "## 10. Make reviewer handoff easy",
        "## 11. Final publication handoff checklist",
    ):
        assert heading in page

    assert "The effect was robust because at least one specification was positive." in page
    assert "The range from -0.0404 to +0.0210 is the 95% confidence interval." in page
    assert "All declared demonstration branches were retained" in page


def test_hubs_and_publication_workflow_link_practice_guidance() -> None:
    guides = _text("docs/guides/index.md")
    examples = _text("docs/examples/index.md")
    workflow = _text("docs/workflows/reproducible-publication.md")

    assert "common-audit-mistakes/" in guides
    assert "../examples/publication-archive-handoff/" in guides
    assert "publication-archive-handoff/" in examples
    assert "../guides/common-audit-mistakes/" in examples

    for route in (
        "/docs/guides/common-audit-mistakes/",
        "/docs/examples/publication-archive-handoff/",
    ):
        assert route in workflow

    assert "Before interpreting, audit the audit." in workflow
    assert "synthetic teaching material, not validation evidence" in workflow
