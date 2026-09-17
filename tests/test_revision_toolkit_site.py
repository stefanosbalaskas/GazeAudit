from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLKIT = ROOT / "docs" / "workspace" / "revision-toolkit.md"
WORKFLOWS = ROOT / "docs" / "workflows" / "index.md"
REVIEW_PATH = ROOT / "docs" / "workspace" / "manuscript-review-path.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_revision_toolkit_routes_the_review_round_by_task() -> None:
    text = _read(TOOLKIT)
    assert "# Peer-review revision toolkit" in text
    for heading in (
        "Classify the reviewer request",
        "Run and preserve new analysis",
        "Write the response letter",
        "Record what changed",
        "Build the revision package",
        "Run the final handoff check",
    ):
        assert heading in text


def test_revision_toolkit_preserves_temporal_denominators_and_failures() -> None:
    text = _read(TOOLKIT)
    assert "8 / 8 submitted + 4 / 4 post-review" in text
    assert "not “12 pre-specified analyses.”" in text
    assert "relabel `3 / 4` as `3 / 3`" in text
    assert "endpoint amendments remain endpoint-specific" in text
    assert "corrections retain superseded evidence" in text


def test_revision_toolkit_exposes_real_cli_and_scope_boundary() -> None:
    text = _read(TOOLKIT)
    assert "gazeaudit-revision-package init" in text
    assert "gazeaudit-revision-package validate" in text
    assert "structural provenance only" in text
    assert "It does not decide whether a reviewer request is scientifically justified" in text
    assert "GazeBase `incomplete`" in text
    assert "Korthals `robust_negative`" in text
    assert "Pedrotti/de Chambrier `materially_fragile`" in text


def test_workflow_hub_surfaces_revision_toolkit() -> None:
    text = _read(WORKFLOWS)
    assert "Peer-review revision toolkit" in text
    assert "/docs/workspace/revision-toolkit/" in text
    assert "preserve the submitted evidence and its original denominator" in text
    assert "reviewer-requested extensions" in text


def test_manuscript_review_path_offers_short_revision_route() -> None:
    text = _read(REVIEW_PATH)
    assert "Already in a revision round?" in text
    assert "/docs/workspace/revision-toolkit/" in text
    assert "result interpretation → manuscript wording → reviewer reconstruction" in text
    assert "The route does not classify your study." in text
