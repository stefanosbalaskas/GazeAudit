from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_manuscript_readiness_uses_reconstruction_not_auto_validity() -> None:
    guide = _text("docs/guides/manuscript-readiness.md")

    for contract in (
        "Readiness is not an automatic validity decision.",
        "The six manuscript-readiness gates",
        "The scientific endpoint is reconstructable",
        "The execution denominator is explicit",
        "Researcher-owned decisions are distinguishable from diagnostics",
        "The Results wording matches the complete pattern",
        "The manuscript and archive tell the same story",
        "The claim survives a reviewer reconstruction test",
    ):
        assert contract in guide

    assert "These are reporting patterns, not automatic classification rules." in guide


def test_reviewer_example_keeps_failed_valid_branch_in_denominator() -> None:
    example = _text("docs/examples/reviewer-reconstruction.md")

    for contract in (
        "8 declared combinations",
        "valid execution denominator is **7**, not 8",
        "successful valid branches: **6**",
        "technically failed valid branches: **1**",
        "not a complete seven-branch execution",
        "Do **not** convert six positive estimates into “100% robust.”",
        "keep S06 in the valid denominator",
    ):
        assert contract in example


def test_reviewer_example_is_explicitly_synthetic_and_boundary_safe() -> None:
    example = _text("docs/examples/reviewer-reconstruction.md")

    assert "Illustrative evidence only." in example
    assert "synthetic teaching material" in example
    assert "Nothing on this page changes GazeAudit's frozen empirical" in example
    assert "validation records" in example
    assert "not an automatic judgement" in example


def test_manuscript_readiness_is_discoverable_across_learning_surfaces() -> None:
    guide_hub = _text("docs/guides/index.md")
    example_hub = _text("docs/examples/index.md")
    article_hub = _text("docs/articles/index.md")
    workflow = _text("docs/workflows/reproducible-publication.md")

    guide_route = "manuscript-readiness/"
    example_route = "reviewer-reconstruction/"

    assert guide_route in guide_hub
    assert "Check manuscript readiness" in guide_hub
    assert example_route in example_hub
    assert "Review the manuscript record" in example_hub
    assert "../guides/manuscript-readiness/" in article_hub
    assert "../examples/reviewer-reconstruction/" in article_hub
    assert "/docs/guides/manuscript-readiness/" in workflow
    assert "/docs/examples/reviewer-reconstruction/" in workflow


def test_workspace_review_path_connects_interpretation_to_archive() -> None:
    guide = _text("docs/guides/manuscript-readiness.md")
    path = _text("docs/workspace/manuscript-review-path.md")

    assert "/docs/workspace/manuscript-review-path/" in guide
    for contract in (
        "result interpretation → manuscript wording → reviewer reconstruction",
        "1 · Interpret",
        "2 · Draft",
        "3 · Reconstruct",
        "4 · Archive",
        "/docs/guides/manuscript-readiness/",
        "/docs/examples/reviewer-reconstruction/",
        "The route does not classify your study.",
    ):
        assert contract in path


def test_publication_workflow_requires_outsider_reconstruction() -> None:
    workflow = _text("docs/workflows/reproducible-publication.md")

    for contract in (
        "Run the manuscript-readiness gate",
        "without private lab context",
        "full declared/valid/successful/failed denominator",
        "Use an outsider test.",
        "execution denominator and unresolved valid failures",
    ):
        assert contract in workflow
