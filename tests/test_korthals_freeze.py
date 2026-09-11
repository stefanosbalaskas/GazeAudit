from __future__ import annotations

import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import pytest

from gazeaudit.korthals_execution import (
    KORTHALS_CASE_STUDY_ID,
    KORTHALS_COMPANION_COMMIT,
    KORTHALS_PROTOCOL_FINGERPRINT,
)
from gazeaudit.korthals_freeze import (
    KORTHALS_COMPANION_REPOSITORY,
    KORTHALS_FREEZE_WORKFLOW,
    KORTHALS_SOURCE_FREEZE_SCHEMA,
    verify_korthals_source_freeze_artifacts,
    write_korthals_source_freeze_artifacts,
)
from gazeaudit.korthals_source import (
    KORTHALS_OSF_DOI,
    KORTHALS_OSF_PROJECT,
    KORTHALS_SOURCE_INTAKE_SCHEMA,
    KORTHALS_SOURCE_SCHEMA,
    verify_korthals_source_intake_artifacts,
)
from gazeaudit.provenance import canonical_json, fingerprint


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record(path: Path, root: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": _sha(path),
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def _make_valid_intake(tmp_path: Path) -> Path:
    root = tmp_path / "intake"
    root.mkdir()
    source_core = {
        "schema": KORTHALS_SOURCE_SCHEMA,
        "case_study_id": KORTHALS_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "osf_project": KORTHALS_OSF_PROJECT,
        "osf_doi": KORTHALS_OSF_DOI,
        "companion_commit": KORTHALS_COMPANION_COMMIT,
        "download_contract": {
            "raw_clean": "both",
            "train_test": "both",
            "participants": "all",
        },
        "participants": ["p1"],
        "participant_count": 1,
        "files": [
            {
                "path": "raw/train/p1/p1.asc",
                "size_bytes": 1,
                "sha256": "0" * 64,
            }
        ],
        "file_count": 1,
    }
    source = dict(source_core)
    source["source_manifest_fingerprint"] = fingerprint(source_core)
    _write_json(root / "source_manifest.json", source)

    summary = {
        "case_study_id": KORTHALS_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": source["source_manifest_fingerprint"],
        "participant_count": 1,
        "prepared_row_count": 10,
        "retained_trial_count": 2,
        "validation_group_count": 1,
        "target_types": ["jumping_circle", "moving_circle"],
        "participant_split_fingerprint": "1" * 64,
    }
    _write_json(root / "intake_summary.json", summary)

    records = [
        _record(root / "intake_summary.json", root),
        _record(root / "source_manifest.json", root),
    ]
    artifact_core = {
        "schema": KORTHALS_SOURCE_INTAKE_SCHEMA,
        "case_study_id": KORTHALS_CASE_STUDY_ID,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": source["source_manifest_fingerprint"],
        "files": records,
    }
    artifact = dict(artifact_core)
    artifact["artifact_manifest_fingerprint"] = fingerprint(artifact_core)
    _write_json(root / "artifact_manifest.json", artifact)
    checksum_paths = sorted(path for path in root.iterdir() if path.is_file())
    (root / "SHA256SUMS").write_text(
        "\n".join(f"{_sha(path)}  {path.name}" for path in checksum_paths) + "\n",
        encoding="utf-8",
    )
    assert verify_korthals_source_intake_artifacts(root)
    return root


def _context(intake: Path) -> dict[str, str]:
    source = json.loads((intake / "source_manifest.json").read_text(encoding="utf-8"))
    return {
        "repository": "stefanosbalaskas/GazeAudit",
        "execution_commit": "a" * 40,
        "workflow_ref": KORTHALS_FREEZE_WORKFLOW,
        "github_run_id": "123456",
        "companion_repository": KORTHALS_COMPANION_REPOSITORY,
        "companion_commit": KORTHALS_COMPANION_COMMIT,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": source["source_manifest_fingerprint"],
        "package_version": version("gazeaudit"),
        "python_version": "3.12.synthetic",
        "platform": "linux-synthetic",
        "runner_os": "Linux",
        "runner_arch": "X64",
    }


def test_source_freeze_envelope_is_valid_and_endpoint_blind(tmp_path):
    intake = _make_valid_intake(tmp_path)
    output = tmp_path / "freeze"
    manifest = write_korthals_source_freeze_artifacts(
        intake,
        output,
        execution_context=_context(intake),
        environment_text="gazeaudit==0.1.0.dev18\npandas==3.0.5\n",
    )

    assert manifest["schema"] == KORTHALS_SOURCE_FREEZE_SCHEMA
    assert verify_korthals_source_freeze_artifacts(output)
    assert (output / "intake" / "SHA256SUMS").is_file()
    searchable = "\n".join(
        path.read_text(encoding="utf-8")
        for path in output.rglob("*")
        if path.is_file()
    )
    for token in (
        "hard_effect",
        "mc_mean",
        "classification",
        "probability_above_reference",
        "probability_below_reference",
        "draw_effects",
    ):
        assert token not in searchable


def test_source_freeze_fails_closed_on_identity_mismatch(tmp_path):
    intake = _make_valid_intake(tmp_path)
    context = _context(intake)
    context["companion_commit"] = "b" * 40
    with pytest.raises(ValueError, match="companion commit"):
        write_korthals_source_freeze_artifacts(
            intake,
            tmp_path / "freeze",
            execution_context=context,
            environment_text="gazeaudit==0.1.0.dev18\n",
        )

    context = _context(intake)
    context["source_manifest_fingerprint"] = "f" * 64
    with pytest.raises(ValueError, match="source fingerprint"):
        write_korthals_source_freeze_artifacts(
            intake,
            tmp_path / "freeze2",
            execution_context=context,
            environment_text="gazeaudit==0.1.0.dev18\n",
        )


def test_source_freeze_detects_environment_and_nested_intake_tampering(tmp_path):
    intake = _make_valid_intake(tmp_path)
    output = tmp_path / "freeze"
    write_korthals_source_freeze_artifacts(
        intake,
        output,
        execution_context=_context(intake),
        environment_text="gazeaudit==0.1.0.dev18\npandas==3.0.5\n",
    )
    (output / "pip_freeze.txt").write_text("tampered\n", encoding="utf-8")
    assert not verify_korthals_source_freeze_artifacts(output)

    output2 = tmp_path / "freeze2"
    write_korthals_source_freeze_artifacts(
        intake,
        output2,
        execution_context=_context(intake),
        environment_text="gazeaudit==0.1.0.dev18\npandas==3.0.5\n",
    )
    nested = output2 / "intake" / "intake_summary.json"
    nested.write_text(nested.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert not verify_korthals_source_freeze_artifacts(output2)


def test_source_freeze_workflow_is_manual_archive_before_reveal_and_has_no_endpoint():
    workflow = Path(".github/workflows/korthals-source-freeze.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch" in workflow
    assert KORTHALS_COMPANION_COMMIT in workflow
    assert 'raw_clean="both"' in workflow
    assert 'train_test="both"' in workflow
    assert 'participants="all"' in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert workflow.index("actions/upload-artifact@v4") < workflow.index(
        "Reveal archived source identity"
    )
    assert "run_korthals_aoi_execution" not in workflow
    assert "write_korthals_execution_artifacts" not in workflow
