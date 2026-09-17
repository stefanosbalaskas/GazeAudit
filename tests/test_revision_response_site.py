from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_response_letter_guide_preserves_revision_provenance() -> None:
    guide = _text("docs/guides/reviewer-response-letter.md")

    for contract in (
        "Reviewer response letter guide",
        "This is a provenance guide, not a persuasion template.",
        "The response unit",
        "results_already_seen: yes",
        "submitted_execution: \"8 / 8 valid branches completed\"",
        "amendment_execution: \"4 / 4 added branches completed\"",
        "Do not collapse temporal layers",
        "Corrections preserve the superseded record",
        "Do not use the response letter to rewrite history.",
    ):
        assert contract in guide


def test_response_package_keeps_submitted_and_revision_layers_separate() -> None:
    example = _text("docs/examples/revision-response-package.md")

    for contract in (
        "Illustrative evidence only.",
        "8 / 8 valid specifications completed",
        "documentation clarification",
        "sensitivity amendment",
        "8 / 8 submitted + 4 / 4 post-review",
        "It is not “12 pre-specified analyses.”",
        "endpoint amendment",
        "do not merge it into the original robustness denominator",
        "Reviewer reconstruction test",
    ):
        assert contract in example


def test_response_package_explains_failed_amendment_branch() -> None:
    example = _text("docs/examples/revision-response-package.md")

    assert "3 successful / 4 valid" in example
    assert "one unresolved valid amendment branch retained in the archive" in example
    assert (
        "It should not say that the reviewer-requested sensitivity analysis was complete."
        in example
    )


def test_response_guidance_is_discoverable_from_hubs_and_review_path() -> None:
    guide_hub = _text("docs/guides/index.md")
    example_hub = _text("docs/examples/index.md")
    review_path = _text("docs/workspace/manuscript-review-path.md")

    assert "Write the reviewer response" in guide_hub
    assert "reviewer-response-letter/" in guide_hub
    assert "Assemble the response package" in example_hub
    assert "revision-response-package/" in example_hub
    assert "/docs/guides/reviewer-response-letter/" in review_path
    assert "/docs/examples/revision-response-package/" in review_path


def test_response_material_does_not_change_frozen_validation_authority() -> None:
    example = _text("docs/examples/revision-response-package.md")
    review_path = _text("docs/workspace/manuscript-review-path.md")

    assert "do not create or modify GazeAudit's frozen empirical validation records" in example
    assert "The route does not classify your study." in review_path
