from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "guides" / "peer-review-revision-checklist.md"
EXAMPLE = ROOT / "docs" / "examples" / "revision-package-quickstart.md"
TOOLKIT = ROOT / "docs" / "workspace" / "revision-toolkit.md"
GUIDES_INDEX = ROOT / "docs" / "guides" / "index.md"
EXAMPLES_INDEX = ROOT / "docs" / "examples" / "index.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_peer_review_checklist_classifies_revision_work_without_rewriting_history() -> None:
    text = _read(GUIDE)
    for category in (
        "`documentation_clarification`",
        "`sensitivity_amendment` or `analytical_amendment`",
        "`endpoint_amendment`",
        "`measurement_amendment`",
        "`correction`",
    ):
        assert category in text

    assert "8 / 8 submitted + 4 / 4 post-review" in text
    assert "Do not rewrite it as “12 pre-specified analyses.”" in text
    assert "3 / 4 with one unresolved valid failure" in text
    assert "Do not silently reduce the denominator to `3 / 3`" in text


def test_peer_review_checklist_exposes_cli_and_structural_scope_boundary() -> None:
    text = _read(GUIDE)
    assert "gazeaudit-revision-package init" in text
    assert "gazeaudit-revision-package validate" in text
    assert "structural provenance only" in text
    assert "does not establish analytical validity, robustness, manuscript quality, or publication readiness" in text
    assert "not a scientific scoring system" in text


def test_revision_package_quickstart_uses_governed_schema_and_temporal_layers() -> None:
    text = _read(EXAMPLE)
    for contract in (
        "reviewer_item,category,results_already_seen,action,submitted_denominator,post_review_denominator,manuscript_location,archive_location,status",
        "change_id,category,results_already_seen,submitted_location,revised_location,evidence_added_or_regenerated,denominator_effect,claim_impact,status",
        "claim_id,claim_component,temporal_status,supporting_evidence,manuscript_location,verification_status",
        "E1 submitted: 8 / 8",
        "E1 post-review sensitivity amendment: 4 / 4",
        "E2 post-review endpoint amendment: separate endpoint record",
        "amendment execution: 3 / 4",
        '"scope": "structural_provenance_only"',
    ):
        assert contract in text


def test_revision_package_quickstart_is_explicitly_synthetic_and_non_empirical() -> None:
    text = _read(EXAMPLE)
    assert "synthetic teaching material" in text
    assert "does not create empirical validation evidence" in text
    assert "does not establish that any analysis or manuscript claim is scientifically valid" in text
    assert "GazeBase `incomplete`" in text
    assert "Korthals `robust_negative`" in text
    assert "Pedrotti/de Chambrier `materially_fragile`" in text


def test_revision_discovery_surfaces_short_route_from_toolkit_and_hubs() -> None:
    toolkit = _read(TOOLKIT)
    guides = _read(GUIDES_INDEX)
    examples = _read(EXAMPLES_INDEX)

    checklist_route = "/docs/guides/peer-review-revision-checklist/"
    quickstart_route = "/docs/examples/revision-package-quickstart/"

    assert checklist_route in toolkit
    assert quickstart_route in toolkit
    assert "Need the shortest route?" in toolkit
    assert "structural provenance only" in toolkit

    assert "Peer-review revision checklist" in guides
    assert "peer-review-revision-checklist/" in guides
    assert "revision-package-quickstart/" in guides

    assert "Revision-package quickstart" in examples
    assert "revision-package-quickstart/" in examples
    assert "peer-review-revision-checklist/" in examples
