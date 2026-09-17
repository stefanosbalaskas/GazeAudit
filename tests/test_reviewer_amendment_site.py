from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_reviewer_amendment_guide_preserves_temporal_provenance() -> None:
    guide = _text("docs/guides/reviewer-requested-amendments.md")

    for contract in (
        "Do not rewrite the original audit",
        "documentation clarification",
        "correction",
        "sensitivity amendment",
        "analytical amendment",
        "endpoint amendment",
        "measurement amendment",
        "results_already_seen: yes",
        "submitted evidence",
        "post-review evidence",
    ):
        assert contract in guide

    assert "The category determines how the new evidence should be described." in guide
    assert "It does **not** decide whether the reviewer request is scientifically justified." in guide


def test_reviewer_amendment_guide_keeps_denominators_separate() -> None:
    guide = _text("docs/guides/reviewer-requested-amendments.md")

    for contract in (
        "submitted audit: `12 / 12` valid branches executed",
        "reviewer-requested amendment: `4 / 4` added branches executed",
        "Do not rewrite the original record as “16 specifications were predeclared.”",
        "the amendment has its own denominator and execution status",
        "failures remain visible",
    ):
        assert contract in guide


def test_reviewer_reanalysis_example_is_synthetic_and_not_retroactive() -> None:
    example = _text("docs/examples/reviewer-requested-reanalysis.md")

    for contract in (
        "Illustrative evidence only.",
        "synthetic teaching material",
        "Submitted denominator: **8 / 8 valid specifications completed**.",
        "Amendment denominator: **4 / 4 reviewer-requested branches completed**.",
        "Twelve pre-specified analyses were conducted.",
        "The original eight-specification audit is preserved unchanged.",
        "results_already_seen: yes",
        "one unresolved failure",
    ):
        assert contract in example

    assert "do not mix its branches into the original endpoint denominator" in example


def test_reviewer_amendment_route_is_discoverable_across_site_surfaces() -> None:
    guide_hub = _text("docs/guides/index.md")
    example_hub = _text("docs/examples/index.md")
    article_hub = _text("docs/articles/index.md")
    workspace = _text("docs/workspace/index.md")
    review_path = _text("docs/workspace/manuscript-review-path.md")
    workflow = _text("docs/workflows/reproducible-publication.md")

    for page in (guide_hub, article_hub, workspace, review_path, workflow):
        assert "reviewer-requested-amendments" in page

    for page in (example_hub, article_hub, workspace, review_path, workflow):
        assert "reviewer-requested-reanalysis" in page

    assert "Handle reviewer amendments" in guide_hub
    assert "Respond to a reanalysis request" in example_hub
    assert "The reviewer asked for another analysis. Now what?" in article_hub
    assert "Revising after peer review?" in workspace
    assert "4 · Amend" in review_path
    assert "Preserve reviewer-requested amendments" in workflow


def test_workspace_keeps_frozen_case_outcomes_unchanged() -> None:
    workspace = _text("docs/workspace/index.md")

    for outcome in (
        "GazeBase multi-detector audit | `incomplete`",
        "Korthals target-tracking AOI | `robust_negative`",
        "Pedrotti/de Chambrier sampling + missingness | `materially_fragile`",
    ):
        assert outcome in workspace

    assert "These are protocol-bound records." in workspace


def test_revision_workflow_distinguishes_correction_from_amendment() -> None:
    guide = _text("docs/guides/reviewer-requested-amendments.md")
    workflow = _text("docs/workflows/reproducible-publication.md")

    assert "When a correction is different" in guide
    assert "Corrections are not ordinary amendments." in workflow
    assert "preserve the superseded record" in workflow
    assert "identify which manuscript claims changed" in workflow
