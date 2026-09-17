from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_resubmission_guide_preserves_temporal_evidence_layers() -> None:
    guide = _text("docs/guides/resubmission-readiness.md")

    for contract in (
        "The seven final-handoff gates",
        "8 / 8 submitted + 4 / 4 post-review",
        "Do not rewrite this as “12 pre-specified analyses.”",
        "The version-change manifest is complete",
        "The final archive can reproduce the revised claim",
        "An outsider can follow the editor-facing evidence map",
        "Resubmission readiness is not an acceptance prediction or validity score.",
    ):
        assert contract in guide


def test_version_manifest_distinguishes_corrections_and_amendments() -> None:
    guide = _text("docs/guides/version-change-manifest.md")

    for contract in (
        "A tracked-changes manuscript shows **where text changed**.",
        "documentation_clarification",
        "sensitivity_amendment",
        "endpoint_amendment",
        "measurement_amendment",
        "Corrections require a supersession trail",
        "Endpoint changes stay endpoint-specific",
        "relabel post-review analyses as pre-specified",
    ):
        assert contract in guide


def test_accepted_record_example_is_synthetic_and_reconstructable() -> None:
    example = _text("docs/examples/submission-to-accepted-record.md")

    for contract in (
        "Illustrative evidence only.",
        "8 / 8 valid specifications completed at submission",
        "8 / 8 submitted + 4 / 4 post-review",
        "It is not **“12 pre-specified analyses.”**",
        "did not merge into the original E1 robustness denominator",
        "final editor-facing evidence map",
        "3 successful / 4 valid",
        "Publication status is not scientific validation.",
    ):
        assert contract in example


def test_final_handoff_is_discoverable_from_review_path() -> None:
    path = _text("docs/workspace/manuscript-review-path.md")

    for contract in (
        "Final resubmission handoff",
        "/docs/guides/version-change-manifest/",
        "/docs/guides/resubmission-readiness/",
        "/docs/examples/submission-to-accepted-record/",
        "Record what changed",
        "Run the final consistency gate",
        "Trace the accepted record",
    ):
        assert contract in path


def test_handoff_material_does_not_create_validation_evidence() -> None:
    example = _text("docs/examples/submission-to-accepted-record.md")
    guide = _text("docs/guides/resubmission-readiness.md")

    assert "does not create or modify GazeAudit's frozen empirical" in example
    assert "validation records" in example
    assert "does not create a new empirical validation result for GazeAudit" in guide
