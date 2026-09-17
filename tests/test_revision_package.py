from __future__ import annotations

import json

import pytest

from gazeaudit.revision_package import (
    REVISION_PACKAGE_SCHEMA,
    REVISION_PACKAGE_VALIDATION_SCHEMA,
    build_revision_package_manifest,
    validate_revision_package,
    write_revision_package_skeleton,
)
from gazeaudit.revision_package_cli import main


def test_revision_package_manifest_preserves_temporal_safeguards() -> None:
    manifest = build_revision_package_manifest("synthetic-study", review_round=2)

    assert manifest["schema"] == REVISION_PACKAGE_SCHEMA
    assert manifest["review_round"] == 2
    assert manifest["temporal_safeguards"] == {
        "submitted_record_immutable": True,
        "post_review_work_separate": True,
        "endpoint_amendments_separate_from_original_denominator": True,
        "failed_valid_branches_remain_visible": True,
        "corrections_preserve_superseded_record": True,
    }
    assert "revision/round-2/reviewer-response/response-matrix.csv" in manifest["required_paths"]
    assert len(manifest["manifest_fingerprint"]) == 64


def test_revision_package_skeleton_round_trips_through_validator(tmp_path) -> None:
    root = tmp_path / "revision-package"
    manifest = write_revision_package_skeleton(
        root,
        project_slug="synthetic-study",
        review_round=2,
    )

    assert len(manifest["required_paths"]) == 9
    assert (root / "submission/README.md").is_file()
    assert (root / "revision/round-2/change-manifest/version-change-manifest.csv").is_file()
    assert (root / "final/editor-facing-evidence-map.csv").is_file()

    validation = validate_revision_package(root)
    assert validation["schema"] == REVISION_PACKAGE_VALIDATION_SCHEMA
    assert validation["valid"] is True
    assert validation["manifest_fingerprint_valid"] is True
    assert validation["missing_paths"] == []
    assert validation["scope"] == "structural_provenance_only"


def test_revision_package_validator_keeps_missing_files_visible(tmp_path) -> None:
    root = tmp_path / "revision-package"
    write_revision_package_skeleton(root, project_slug="synthetic-study")
    missing = root / "revision/round-1/amendments/README.md"
    missing.unlink()

    validation = validate_revision_package(root)
    assert validation["valid"] is False
    assert validation["missing_paths"] == ["revision/round-1/amendments/README.md"]
    assert "required package files are missing" in validation["problems"]


def test_revision_package_scaffold_refuses_implicit_overwrite(tmp_path) -> None:
    root = tmp_path / "revision-package"
    write_revision_package_skeleton(root, project_slug="synthetic-study")

    with pytest.raises(FileExistsError, match="revision package files already exist"):
        write_revision_package_skeleton(root, project_slug="synthetic-study")

    unrelated = root / "notes-from-editor.txt"
    unrelated.write_text("preserve me", encoding="utf-8")
    write_revision_package_skeleton(
        root,
        project_slug="synthetic-study",
        overwrite=True,
    )
    assert unrelated.read_text(encoding="utf-8") == "preserve me"


def test_revision_package_cli_init_and_validate(tmp_path, capsys) -> None:
    root = tmp_path / "revision-package"

    assert (
        main(
            [
                "init",
                "--output-dir",
                str(root),
                "--project-slug",
                "synthetic-study",
            ]
        )
        == 0
    )
    init_result = json.loads(capsys.readouterr().out)
    assert init_result["action"] == "init"
    assert init_result["required_file_count"] == 9

    assert main(["validate", "--root", str(root)]) == 0
    validation = json.loads(capsys.readouterr().out)
    assert validation["valid"] is True
    assert validation["scope"] == "structural_provenance_only"

    (root / "final/editor-facing-evidence-map.csv").unlink()
    assert main(["validate", "--root", str(root)]) == 2
    invalid = json.loads(capsys.readouterr().out)
    assert invalid["valid"] is False
