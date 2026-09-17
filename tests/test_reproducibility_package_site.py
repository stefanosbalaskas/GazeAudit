from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_reproducibility_package_guide_documents_real_cli_contract() -> None:
    guide = _text("docs/guides/reproducibility-package.md")

    for contract in (
        "gazeaudit-revision-package init",
        "gazeaudit-revision-package validate",
        "response-matrix.csv",
        "version-change-manifest.csv",
        "editor-facing-evidence-map.csv",
        '"scope": "structural_provenance_only"',
        "8 / 8 submitted + 4 / 4 post-review",
        "Do not rewrite it as **12 pre-specified analyses**.",
        "Corrections need a supersession trail",
        "Keep failed valid branches visible",
        "does **not** prove",
    ):
        assert contract in guide


def test_reproducibility_package_example_is_synthetic_and_failure_aware() -> None:
    example = _text("docs/examples/reproducibility-package-cli.md")

    for contract in (
        "Illustrative evidence only.",
        "8 / 8 submitted + 4 / 4 post-review",
        "It is not **12 pre-specified analyses**.",
        "Step 8 — deliberately break the governed structure",
        '"revision/round-1/amendments/README.md"',
        '"valid": false',
        "3 successful / 4 valid",
        "Structure and scientific completeness are different questions.",
        "Correction variant",
    ):
        assert contract in example


def test_review_path_exposes_executable_revision_package_stage() -> None:
    path = _text("docs/workspace/manuscript-review-path.md")

    for contract in (
        "executable revision package",
        "/docs/guides/reproducibility-package/",
        "/docs/examples/reproducibility-package-cli/",
        "Build the reproducibility package",
        "Structural validation is not scientific validation.",
    ):
        assert contract in path


def test_cli_entry_point_and_executable_example_are_present() -> None:
    pyproject = _text("pyproject.toml")
    example = _text("examples/revision_package_workflow.py")

    assert (
        'gazeaudit-revision-package = "gazeaudit.revision_package_cli:main"'
        in pyproject
    )
    assert "write_revision_package_skeleton" in example
    assert "validate_revision_package" in example
    assert "governed_marker.unlink()" in example
    assert "overwrite=True" in example


def test_new_material_does_not_modify_frozen_validation_authority() -> None:
    guide = _text("docs/guides/reproducibility-package.md")
    example = _text("docs/examples/reproducibility-package-cli.md")

    assert "does not establish scientific validity" in guide
    assert "does not create empirical validation evidence for GazeAudit" in example
