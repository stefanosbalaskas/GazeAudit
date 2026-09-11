import json

import numpy as np
import pandas as pd
import pytest

from gazeaudit import (
    ARTIFACT_SCHEMA,
    GAZEBASE_ARCHIVE_MD5,
    GazeStudy,
    PreparedGazeBaseData,
    run_gazebase_multidetector_execution,
    verify_gazebase_execution_artifacts,
    write_gazebase_execution_artifacts,
)

COMMIT = "b" * 40


class _FakeDetector:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def get_default_params(self):
        return {"frozen_default": f"default-{self.algorithm}"}


class _DetectionResult:
    def __init__(self, samples):
        self.samples = samples


def _prepared():
    rows = []
    for participant in (1, 2, 3, 4):
        for task in ("FXS", "TEX"):
            labels = np.full(6, "fixation", dtype=object)
            if task == "TEX":
                labels[4:] = "saccade"
            for index, label in enumerate(labels):
                rows.append(
                    {
                        "x": float(index),
                        "y": float(participant),
                        "timestamp": float(index * 10),
                        "participant": participant,
                        "trial": task,
                        "reference_event_label": label,
                    }
                )
    source_identity = {
        "dataset": "GazeBase",
        "dataset_version": 3,
        "paper_doi": "10.1038/s41597-021-00959-y",
        "data_doi": "10.6084/m9.figshare.12912257",
        "catalog_archive_md5": GAZEBASE_ARCHIVE_MD5,
        "round": 1,
        "session": 1,
        "tasks": ["FXS", "TEX"],
        "selected_file_count": 8,
        "selected_files_fingerprint": "synthetic-artifact-source",
    }
    return PreparedGazeBaseData(GazeStudy(pd.DataFrame(rows)), source_identity)


def _factory(algorithm, **kwargs):
    return _FakeDetector(algorithm)


def _runner(*, incomplete=False):
    def runner(study, detector, **kwargs):
        output = study.data.copy()
        output["event_label"] = output["reference_event_label"].copy()
        if incomplete and detector.algorithm == "ivt":
            output = output.loc[~output["participant"].eq(4)].copy()
        return _DetectionResult(output.reset_index(drop=True))

    return runner


def _versions(name):
    return {
        "pymovements": "0.28.0",
        "pEYES": "0.2.2",
        "gazeaudit": "0.1.0.dev10",
    }[name]


def _execution(*, incomplete=False):
    return run_gazebase_multidetector_execution(
        _prepared(),
        gazeaudit_commit=COMMIT,
        detector_factory=_factory,
        detector_runner=_runner(incomplete=incomplete),
        version_getter=_versions,
    )


def test_complete_artifact_set_is_deterministic_and_verifiable(tmp_path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first_manifest = write_gazebase_execution_artifacts(_execution(), first_dir)
    second_manifest = write_gazebase_execution_artifacts(_execution(), second_dir)

    assert first_manifest["schema"] == ARTIFACT_SCHEMA
    assert first_manifest["classification"] == "robust"
    assert first_manifest["completeness_passed"] is True
    assert first_manifest["publication_bundle_fingerprint"] is not None
    assert verify_gazebase_execution_artifacts(first_dir)
    assert verify_gazebase_execution_artifacts(second_dir)
    assert (
        first_manifest["artifact_manifest_fingerprint"]
        == second_manifest["artifact_manifest_fingerprint"]
    )
    assert (first_dir / "SHA256SUMS").read_text() == (second_dir / "SHA256SUMS").read_text()

    names = {path.name for path in first_dir.iterdir()}
    assert "publication_report.md" in names
    assert "publication_manifest.json" in names
    assert "detector_participant_tasks.csv" in names
    assert "reference_participant_tasks.csv" in names
    assert not any("samples" in name or "raw" in name for name in names)


def test_artifact_verification_detects_tampering(tmp_path):
    output_dir = tmp_path / "artifacts"
    write_gazebase_execution_artifacts(_execution(), output_dir)
    effects = output_dir / "effects.csv"
    effects.write_text(effects.read_text() + "tampered\n", encoding="utf-8")

    assert not verify_gazebase_execution_artifacts(output_dir)


def test_artifact_verification_rejects_unexpected_files(tmp_path):
    output_dir = tmp_path / "artifacts"
    write_gazebase_execution_artifacts(_execution(), output_dir)
    (output_dir / "unbound.txt").write_text("not in manifest\n", encoding="utf-8")

    assert not verify_gazebase_execution_artifacts(output_dir)


def test_incomplete_execution_is_preserved_without_publication_bundle(tmp_path):
    output_dir = tmp_path / "incomplete"
    execution = _execution(incomplete=True)
    manifest = write_gazebase_execution_artifacts(execution, output_dir)

    assert manifest["classification"] == "incomplete"
    assert manifest["completeness_passed"] is False
    assert manifest["publication_scientific_fingerprint"] is None
    assert manifest["publication_bundle_fingerprint"] is None
    assert verify_gazebase_execution_artifacts(output_dir)
    assert not (output_dir / "publication_manifest.json").exists()
    assert not (output_dir / "publication_report.md").exists()
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["classification"] == "incomplete"


def test_writer_refuses_uncontrolled_overwrite(tmp_path):
    output_dir = tmp_path / "artifacts"
    write_gazebase_execution_artifacts(_execution(), output_dir)

    with pytest.raises(FileExistsError, match="not empty"):
        write_gazebase_execution_artifacts(_execution(), output_dir)

    manifest = write_gazebase_execution_artifacts(_execution(), output_dir, overwrite=True)
    assert manifest["classification"] == "robust"
    assert verify_gazebase_execution_artifacts(output_dir)


def test_overwrite_never_deletes_nested_directories(tmp_path):
    output_dir = tmp_path / "artifacts"
    output_dir.mkdir()
    (output_dir / "nested").mkdir()

    with pytest.raises(ValueError, match="nested directories"):
        write_gazebase_execution_artifacts(_execution(), output_dir, overwrite=True)
