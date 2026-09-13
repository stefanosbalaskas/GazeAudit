from __future__ import annotations

import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import pandas as pd
import pytest

from gazeaudit.pedrotti_freeze import (
    PEDROTTI_FREEZE_WORKFLOW,
    PEDROTTI_SOURCE_FREEZE_SCHEMA,
    verify_pedrotti_source_freeze_artifacts,
    write_pedrotti_source_freeze_artifacts,
)
from gazeaudit.pedrotti_source import (
    PEDROTTI_CASE_STUDY_ID,
    PEDROTTI_PROTOCOL_FINGERPRINT,
    PEDROTTI_SOURCE_INTAKE_SCHEMA,
    PEDROTTI_ZENODO_DOI,
    PEDROTTI_ZENODO_RECORD,
    inspect_pedrotti_source,
    verify_pedrotti_source_intake_artifacts,
    verify_pedrotti_source_manifest,
    write_pedrotti_source_intake_artifacts,
)
from gazeaudit.provenance import canonical_json, fingerprint

_COLUMNS = [
    "TRIAL_INDEX",
    "LEFT_GAZE_X",
    "LEFT_GAZE_Y",
    "LEFT_PUPIL_SIZE",
    "RIGHT_GAZE_X",
    "RIGHT_GAZE_Y",
    "RIGHT_PUPIL_SIZE",
    "TIMESTAMP",
    "TrialTextShown",
]


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_synthetic_source(root: Path) -> dict[str, str]:
    root.mkdir()
    for participant in range(1, 37):
        rows = []
        for trial in range(1, 97):
            if trial == 1:
                stimulus = "1,234"
            elif trial == 2:
                stimulus = "12,345,678"
            else:
                stimulus = f"word-{trial}"
            rows.append(
                {
                    "TRIAL_INDEX": trial,
                    "LEFT_GAZE_X": float(trial),
                    "LEFT_GAZE_Y": float(trial + 1),
                    "LEFT_PUPIL_SIZE": 1000.0,
                    "RIGHT_GAZE_X": ".",
                    "RIGHT_GAZE_Y": ".",
                    "RIGHT_PUPIL_SIZE": ".",
                    "TIMESTAMP": float(trial * 1000),
                    "TrialTextShown": stimulus,
                }
            )
        pd.DataFrame(rows, columns=_COLUMNS).to_csv(root / f"{participant:02d}.txt", index=False)
    (root / "readme.txt").write_text("synthetic endpoint-blind source fixture\n", encoding="utf-8")
    return {path.name: _md5(path) for path in root.iterdir() if path.is_file()}


@pytest.fixture
def synthetic_intake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    source_dir = tmp_path / "source"
    expected = _write_synthetic_source(source_dir)
    monkeypatch.setattr(
        "gazeaudit.pedrotti_source.expected_pedrotti_md5",
        lambda: dict(expected),
    )
    intake = inspect_pedrotti_source(source_dir)
    output = tmp_path / "intake"
    write_pedrotti_source_intake_artifacts(intake, output)
    assert verify_pedrotti_source_intake_artifacts(output)
    return output


def _context(intake: Path) -> dict[str, object]:
    source = json.loads((intake / "source_manifest.json").read_text(encoding="utf-8"))
    return {
        "repository": "stefanosbalaskas/GazeAudit",
        "execution_commit": "a" * 40,
        "workflow_ref": PEDROTTI_FREEZE_WORKFLOW,
        "github_run_id": "123456",
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": source["source_manifest_fingerprint"],
        "zenodo_doi": PEDROTTI_ZENODO_DOI,
        "zenodo_record": PEDROTTI_ZENODO_RECORD,
        "package_version": version("gazeaudit"),
        "python_version": "3.12.synthetic",
        "platform": "linux-synthetic",
        "runner_os": "Linux",
        "runner_arch": "X64",
    }


def _rewrite_artifact_integrity(root: Path) -> None:
    source = json.loads((root / "source_manifest.json").read_text(encoding="utf-8"))
    records = []
    for name in ("intake_summary.json", "source_manifest.json"):
        path = root / name
        records.append(
            {
                "path": name,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    core = {
        "schema": PEDROTTI_SOURCE_INTAKE_SCHEMA,
        "case_study_id": PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": source["source_manifest_fingerprint"],
        "files": records,
    }
    artifact = dict(core)
    artifact["artifact_manifest_fingerprint"] = fingerprint(core)
    (root / "artifact_manifest.json").write_text(canonical_json(artifact) + "\n", encoding="utf-8")
    checksum_targets = sorted(
        path for path in root.iterdir() if path.is_file() and path.name != "SHA256SUMS"
    )
    (root / "SHA256SUMS").write_text(
        "\n".join(f"{_sha256(path)}  {path.name}" for path in checksum_targets) + "\n",
        encoding="utf-8",
    )


def test_source_intake_is_semantically_bound_and_endpoint_blind(synthetic_intake: Path):
    summary = json.loads(
        (synthetic_intake / "intake_summary.json").read_text(encoding="utf-8")
    )
    assert summary["participant_count"] == 36
    assert summary["total_trial_count"] == 36 * 96
    assert summary["short_numeric_trial_count"] == 36
    assert summary["long_numeric_trial_count"] == 36
    assert summary["scientific_endpoint_evaluated"] is False
    assert verify_pedrotti_source_intake_artifacts(synthetic_intake)


def test_source_manifest_rejects_rewritten_download_contract(
    synthetic_intake: Path,
):
    manifest_path = synthetic_intake / "source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["download_contract"]["participants"] = "selected"
    manifest.pop("source_manifest_fingerprint")
    manifest["source_manifest_fingerprint"] = fingerprint(manifest)
    assert not verify_pedrotti_source_manifest(manifest)


def test_intake_rejects_semantic_tampering_even_after_rechecksumming(
    synthetic_intake: Path,
):
    summary_path = synthetic_intake / "intake_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["participant_count"] = 35
    summary_path.write_text(canonical_json(summary) + "\n", encoding="utf-8")
    _rewrite_artifact_integrity(synthetic_intake)
    assert not verify_pedrotti_source_intake_artifacts(synthetic_intake)


def test_source_freeze_envelope_is_valid_and_endpoint_blind(synthetic_intake: Path, tmp_path: Path):
    output = tmp_path / "freeze"
    manifest = write_pedrotti_source_freeze_artifacts(
        synthetic_intake,
        output,
        execution_context=_context(synthetic_intake),
        environment_text="gazeaudit==0.1.0.dev19\npandas==2.3.3\nnumpy==2.5.3\n",
    )
    assert manifest["schema"] == PEDROTTI_SOURCE_FREEZE_SCHEMA
    assert manifest["scientific_endpoint_evaluated"] is False
    assert verify_pedrotti_source_freeze_artifacts(output)
    searchable = "\n".join(
        path.read_text(encoding="utf-8")
        for path in output.rglob("*")
        if path.is_file()
    )
    for token in (
        '"reference_estimate"',
        '"study_estimate"',
        '"sampling_estimates"',
        '"missingness_estimates"',
        '"recovery_fraction"',
        '"classification"',
    ):
        assert token not in searchable


def test_source_freeze_fails_closed_on_identity_and_tampering(
    synthetic_intake: Path,
    tmp_path: Path,
):
    bad_context = _context(synthetic_intake)
    bad_context["source_manifest_fingerprint"] = "f" * 64
    with pytest.raises(ValueError, match="source fingerprint"):
        write_pedrotti_source_freeze_artifacts(
            synthetic_intake,
            tmp_path / "bad-freeze",
            execution_context=bad_context,
            environment_text="gazeaudit==0.1.0.dev19\n",
        )

    output = tmp_path / "freeze"
    write_pedrotti_source_freeze_artifacts(
        synthetic_intake,
        output,
        execution_context=_context(synthetic_intake),
        environment_text="gazeaudit==0.1.0.dev19\n",
    )
    (output / "pip_freeze.txt").write_text("tampered\n", encoding="utf-8")
    assert not verify_pedrotti_source_freeze_artifacts(output)


def test_source_freeze_workflow_is_manual_archive_before_reveal_and_has_no_endpoint():
    workflow = Path(".github/workflows/pedrotti-source-freeze.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch" in workflow
    assert "github.ref == 'refs/heads/main'" in workflow
    assert "actions/checkout@v7" in workflow
    assert "actions/setup-python@v7" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert workflow.index("actions/upload-artifact@v7") < workflow.index(
        "Reveal archived source identity"
    )
    assert "gazeaudit-pedrotti-source-intake" in workflow
    assert "gazeaudit-pedrotti-source-freeze" in workflow
    assert "gaze-path" not in workflow.lower()
    assert "sampling_sensitivity_curve" not in workflow
    assert "missingness_sensitivity_curve" not in workflow
