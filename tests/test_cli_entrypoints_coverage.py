from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

import gazeaudit.gazebase_cli as gazebase_cli
import gazeaudit.korthals_execution_v2_cli as execution_v2_cli
import gazeaudit.korthals_freeze_cli as freeze_cli
import gazeaudit.korthals_freeze_v2_cli as freeze_v2_cli
import gazeaudit.korthals_reveal_v2_cli as reveal_v2_cli
import gazeaudit.korthals_source_cli as source_cli
import gazeaudit.korthals_source_v2_cli as source_v2_cli


def test_korthals_source_cli_archives_source_identity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    intake = object()
    seen: dict[str, object] = {}

    def prepare(root: Path) -> object:
        seen["root"] = root
        return intake

    def write(
        value: object,
        output: Path,
        *,
        overwrite: bool,
    ) -> dict[str, str]:
        seen["intake"] = value
        seen["output"] = output
        seen["overwrite"] = overwrite
        return {
            "artifact_manifest_fingerprint": "artifact-v1",
            "source_manifest_fingerprint": "source-v1",
        }

    monkeypatch.setattr(
        source_cli,
        "prepare_korthals_from_companion",
        prepare,
    )
    monkeypatch.setattr(
        source_cli,
        "write_korthals_source_intake_artifacts",
        write,
    )

    output = tmp_path / "out"

    assert (
        source_cli.main(
            [
                "--data-root",
                str(tmp_path / "data"),
                "--output-dir",
                str(output),
                "--overwrite",
            ]
        )
        == 0
    )

    assert seen == {
        "root": tmp_path / "data",
        "intake": intake,
        "output": output,
        "overwrite": True,
    }

    assert json.loads(capsys.readouterr().out) == {
        "artifact_manifest_fingerprint": "artifact-v1",
        "source_manifest_fingerprint": "source-v1",
        "status": "source_intake_archived",
    }


def test_korthals_source_v2_cli_archives_source_identity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    intake = object()
    seen: dict[str, object] = {}

    def prepare(root: Path) -> object:
        seen["root"] = root
        return intake

    def write(
        value: object,
        output: Path,
        *,
        overwrite: bool,
    ) -> dict[str, str]:
        seen["intake"] = value
        seen["output"] = output
        seen["overwrite"] = overwrite
        return {
            "artifact_manifest_fingerprint": "artifact-v2",
            "source_manifest_fingerprint": "source-v2",
        }

    monkeypatch.setattr(
        source_v2_cli,
        "prepare_korthals_from_companion_v2_streaming",
        prepare,
    )
    monkeypatch.setattr(
        source_v2_cli,
        "write_korthals_source_intake_artifacts_v2",
        write,
    )

    output = tmp_path / "out"

    assert (
        source_v2_cli.main(
            [
                "--data-root",
                str(tmp_path / "data"),
                "--output-dir",
                str(output),
                "--overwrite",
            ]
        )
        == 0
    )

    assert seen == {
        "root": tmp_path / "data",
        "intake": intake,
        "output": output,
        "overwrite": True,
    }

    assert json.loads(capsys.readouterr().out) == {
        "artifact_manifest_fingerprint": "artifact-v2",
        "source_manifest_fingerprint": "source-v2",
        "status": "source_intake_v2_archived",
    }


def test_korthals_freeze_cli_builds_provenance_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()

    (intake / "source_manifest.json").write_text(
        json.dumps(
            {
                "source_manifest_fingerprint": "source-v1",
            }
        ),
        encoding="utf-8",
    )

    environment_file = tmp_path / "environment.txt"
    environment_file.write_text(
        "gazeaudit==test\n",
        encoding="utf-8",
    )

    seen: dict[str, object] = {}

    def write(
        intake_dir: Path,
        output_dir: Path,
        *,
        execution_context: dict[str, object],
        environment_text: str,
        overwrite: bool,
    ) -> dict[str, str]:
        seen["intake"] = intake_dir
        seen["output"] = output_dir
        seen["context"] = execution_context
        seen["environment"] = environment_text
        seen["overwrite"] = overwrite
        return {
            "source_manifest_fingerprint": "source-v1",
            "freeze_manifest_fingerprint": "freeze-v1",
        }

    monkeypatch.setattr(
        freeze_cli,
        "write_korthals_source_freeze_artifacts",
        write,
    )
    monkeypatch.setattr(
        freeze_cli,
        "version",
        lambda _: "0.1.test",
    )
    monkeypatch.setattr(
        freeze_cli.platform,
        "platform",
        lambda: "test-platform",
    )

    output = tmp_path / "freeze"

    assert (
        freeze_cli.main(
            [
                "--intake-dir",
                str(intake),
                "--output-dir",
                str(output),
                "--environment-file",
                str(environment_file),
                "--execution-commit",
                "a" * 40,
                "--run-id",
                "123",
                "--runner-os",
                "TestOS",
                "--runner-arch",
                "X64",
                "--overwrite",
            ]
        )
        == 0
    )

    context = seen["context"]

    assert isinstance(context, dict)
    assert context["execution_commit"] == "a" * 40
    assert context["github_run_id"] == "123"
    assert context["source_manifest_fingerprint"] == "source-v1"
    assert context["package_version"] == "0.1.test"
    assert context["platform"] == "test-platform"
    assert context["runner_os"] == "TestOS"
    assert context["runner_arch"] == "X64"

    assert seen["intake"] == intake
    assert seen["output"] == output
    assert seen["environment"] == "gazeaudit==test\n"
    assert seen["overwrite"] is True

    assert json.loads(capsys.readouterr().out) == {
        "freeze_manifest_fingerprint": "freeze-v1",
        "source_manifest_fingerprint": "source-v1",
        "status": "source_freeze_archived",
    }


def test_korthals_freeze_cli_rejects_non_object_manifest(
    tmp_path: Path,
) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()

    (intake / "source_manifest.json").write_text(
        "[]",
        encoding="utf-8",
    )

    environment_file = tmp_path / "environment.txt"
    environment_file.write_text(
        "gazeaudit==test\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="source_manifest.json must contain a JSON object",
    ):
        freeze_cli.main(
            [
                "--intake-dir",
                str(intake),
                "--output-dir",
                str(tmp_path / "out"),
                "--environment-file",
                str(environment_file),
                "--execution-commit",
                "a" * 40,
                "--run-id",
                "1",
            ]
        )


def test_korthals_freeze_v2_cli_builds_provenance_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()

    (intake / "source_manifest.json").write_text(
        json.dumps(
            {
                "source_manifest_fingerprint": "source-v2",
            }
        ),
        encoding="utf-8",
    )

    environment_file = tmp_path / "environment.txt"
    environment_file.write_text(
        "gazeaudit==test\n",
        encoding="utf-8",
    )

    seen: dict[str, object] = {}

    def write(
        intake_dir: Path,
        output_dir: Path,
        *,
        execution_context: dict[str, object],
        environment_text: str,
        overwrite: bool,
    ) -> dict[str, str]:
        seen["intake"] = intake_dir
        seen["output"] = output_dir
        seen["context"] = execution_context
        seen["environment"] = environment_text
        seen["overwrite"] = overwrite
        return {
            "source_manifest_fingerprint": "source-v2",
            "freeze_manifest_fingerprint": "freeze-v2",
        }

    monkeypatch.setattr(
        freeze_v2_cli,
        "write_korthals_source_freeze_artifacts_v2",
        write,
    )
    monkeypatch.setattr(
        freeze_v2_cli,
        "version",
        lambda _: "0.1.test",
    )
    monkeypatch.setattr(
        freeze_v2_cli.platform,
        "platform",
        lambda: "test-platform",
    )

    output = tmp_path / "freeze"

    assert (
        freeze_v2_cli.main(
            [
                "--intake-dir",
                str(intake),
                "--output-dir",
                str(output),
                "--environment-file",
                str(environment_file),
                "--execution-commit",
                "b" * 40,
                "--run-id",
                "456",
                "--runner-os",
                "TestOS",
                "--runner-arch",
                "ARM64",
                "--overwrite",
            ]
        )
        == 0
    )

    context = seen["context"]

    assert isinstance(context, dict)
    assert context["execution_commit"] == "b" * 40
    assert context["github_run_id"] == "456"
    assert context["source_manifest_fingerprint"] == "source-v2"
    assert context["package_version"] == "0.1.test"
    assert context["platform"] == "test-platform"
    assert context["runner_os"] == "TestOS"
    assert context["runner_arch"] == "ARM64"

    assert seen["intake"] == intake
    assert seen["output"] == output
    assert seen["environment"] == "gazeaudit==test\n"
    assert seen["overwrite"] is True

    assert json.loads(capsys.readouterr().out) == {
        "freeze_manifest_fingerprint": "freeze-v2",
        "source_manifest_fingerprint": "source-v2",
        "status": "source_freeze_v2_archived",
    }


def test_korthals_freeze_v2_cli_rejects_non_object_manifest(
    tmp_path: Path,
) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()

    (intake / "source_manifest.json").write_text(
        "[]",
        encoding="utf-8",
    )

    environment_file = tmp_path / "environment.txt"
    environment_file.write_text(
        "gazeaudit==test\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="source_manifest.json must contain a JSON object",
    ):
        freeze_v2_cli.main(
            [
                "--intake-dir",
                str(intake),
                "--output-dir",
                str(tmp_path / "out"),
                "--environment-file",
                str(environment_file),
                "--execution-commit",
                "b" * 40,
                "--run-id",
                "2",
            ]
        )


def test_korthals_reveal_v2_cli_serializes_verified_result(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {
        "classification": "robust_positive",
        "probability": 0.95,
    }

    artifact_dir = tmp_path / "archive"

    monkeypatch.setattr(
        reveal_v2_cli,
        "reveal_korthals_locked_execution_v2",
        lambda path: expected if path == artifact_dir else None,
    )

    assert (
        reveal_v2_cli.main(
            [
                "--artifact-dir",
                str(artifact_dir),
            ]
        )
        == 0
    )

    assert json.loads(capsys.readouterr().out) == expected


def test_korthals_execution_v2_cli_preserves_archive_before_reveal_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source_manifest = {
        "source_manifest_fingerprint": "locked-source",
    }

    prepared = object()
    intake = SimpleNamespace(
        source_manifest=source_manifest,
        prepared=prepared,
    )
    execution = object()

    environment_file = tmp_path / "environment.txt"
    environment_file.write_text(
        "gazeaudit==test\nnumpy==test\n",
        encoding="utf-8",
    )

    verified_manifests: list[object] = []
    verified_prepared: list[object] = []
    written: dict[str, object] = {}

    monkeypatch.setattr(
        execution_v2_cli,
        "build_korthals_source_manifest_v2",
        lambda root: source_manifest,
    )

    monkeypatch.setattr(
        execution_v2_cli,
        "verify_korthals_locked_source_manifest",
        verified_manifests.append,
    )

    monkeypatch.setattr(
        execution_v2_cli,
        "prepare_korthals_from_companion_v2_streaming",
        lambda root: intake,
    )

    monkeypatch.setattr(
        execution_v2_cli,
        "verify_korthals_locked_prepared",
        verified_prepared.append,
    )

    monkeypatch.setattr(
        execution_v2_cli,
        "run_korthals_locked_aoi_execution_v2",
        lambda value: execution if value is prepared else None,
    )

    def write(
        value: object,
        output: Path,
        *,
        execution_context: dict[str, object],
        environment_text: str,
    ) -> None:
        written["execution"] = value
        written["output"] = output
        written["context"] = execution_context
        written["environment"] = environment_text

    monkeypatch.setattr(
        execution_v2_cli,
        "write_korthals_locked_execution_artifacts_v2",
        write,
    )

    monkeypatch.setattr(
        execution_v2_cli,
        "version",
        lambda _: "0.1.test",
    )

    monkeypatch.setattr(
        execution_v2_cli.platform,
        "python_version",
        lambda: "3.12.test",
    )

    monkeypatch.setattr(
        execution_v2_cli.platform,
        "platform",
        lambda: "test-platform",
    )

    output = tmp_path / "out"

    assert (
        execution_v2_cli.main(
            [
                "--data-root",
                str(tmp_path / "data"),
                "--output-dir",
                str(output),
                "--environment-file",
                str(environment_file),
                "--execution-commit",
                "c" * 40,
                "--run-id",
                "789",
                "--runner-os",
                "TestOS",
                "--runner-arch",
                "X64",
            ]
        )
        == 0
    )

    assert verified_manifests == [
        source_manifest,
        source_manifest,
    ]
    assert verified_prepared == [prepared]

    assert written["execution"] is execution
    assert written["output"] == output
    assert written["environment"] == "gazeaudit==test\nnumpy==test\n"

    context = written["context"]

    assert isinstance(context, dict)
    assert context["execution_commit"] == "c" * 40
    assert context["github_run_id"] == "789"
    assert context["source_manifest_fingerprint"] == "locked-source"
    assert context["package_version"] == "0.1.test"
    assert context["python_version"] == "3.12.test"
    assert context["platform"] == "test-platform"
    assert context["runner_os"] == "TestOS"
    assert context["runner_arch"] == "X64"

    # Scientific values must remain silent until the separate reveal operation.
    assert capsys.readouterr().out == ""


def test_gazebase_cli_fails_closed_without_optional_dependency(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setitem(
        sys.modules,
        "pymovements",
        None,
    )

    with pytest.raises(
        SystemExit,
        match="requires the frozen case-study dependencies",
    ):
        gazebase_cli.main(
            [
                "--dataset-root",
                str(tmp_path / "dataset"),
                "--output-dir",
                str(tmp_path / "out"),
                "--gazeaudit-commit",
                "d" * 40,
            ]
        )


@pytest.mark.parametrize(
    "download",
    [
        False,
        True,
    ],
)
def test_gazebase_cli_executes_frozen_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    download: bool,
) -> None:
    seen: dict[str, object] = {}

    class FakeDataset:
        def __init__(
            self,
            name: str,
            *,
            path: Path,
        ) -> None:
            seen["dataset_name"] = name
            seen["dataset_path"] = path
            seen["dataset"] = self
            self.download_calls = 0
            self.load_calls: list[dict[str, object]] = []

        def download(self) -> None:
            self.download_calls += 1

        def load(self, **kwargs: object) -> None:
            self.load_calls.append(dict(kwargs))

    fake_pm = types.SimpleNamespace(
        Dataset=FakeDataset,
    )

    monkeypatch.setitem(
        sys.modules,
        "pymovements",
        fake_pm,
    )

    prepared = object()

    execution = SimpleNamespace(
        audit=SimpleNamespace(
            summary={
                "classification": "incomplete",
                "completeness_passed": False,
            }
        ),
        execution_fingerprint="execution-fingerprint",
    )

    def prepare(
        dataset: object,
        *,
        require_content_hash: bool,
    ) -> object:
        assert dataset is seen["dataset"]
        assert require_content_hash is True
        return prepared

    def run(
        value: object,
        *,
        gazeaudit_commit: str,
    ) -> object:
        assert value is prepared
        assert gazeaudit_commit == "d" * 40
        return execution

    def write(
        value: object,
        output: Path,
        *,
        overwrite: bool,
    ) -> dict[str, str]:
        assert value is execution
        seen["output"] = output
        seen["overwrite"] = overwrite
        return {
            "artifact_manifest_fingerprint": "artifact-fingerprint",
            "publication_scientific_fingerprint": "scientific-fingerprint",
            "publication_bundle_fingerprint": "bundle-fingerprint",
        }

    monkeypatch.setattr(
        gazebase_cli,
        "prepare_gazebase_pymovements_dataset",
        prepare,
    )
    monkeypatch.setattr(
        gazebase_cli,
        "run_gazebase_multidetector_execution",
        run,
    )
    monkeypatch.setattr(
        gazebase_cli,
        "write_gazebase_execution_artifacts",
        write,
    )

    args = [
        "--dataset-root",
        str(tmp_path / "dataset"),
        "--output-dir",
        str(tmp_path / "out"),
        "--gazeaudit-commit",
        "d" * 40,
        "--overwrite",
    ]

    if download:
        args.append("--download")

    assert gazebase_cli.main(args) == 0

    dataset = seen["dataset"]

    assert isinstance(dataset, FakeDataset)
    assert seen["dataset_name"] == "GazeBase"
    assert seen["dataset_path"] == tmp_path / "dataset"
    assert dataset.download_calls == (1 if download else 0)
    assert dataset.load_calls == [
        {
            "participants": False,
            "events": False,
            "stimuli": False,
            "subset": {
                "round_id": 1,
                "session_id": 1,
                "task_name": ["FXS", "TEX"],
            },
        }
    ]

    assert seen["output"] == tmp_path / "out"
    assert seen["overwrite"] is True

    payload = json.loads(capsys.readouterr().out)

    assert payload == {
        "artifact_manifest_fingerprint": "artifact-fingerprint",
        "classification": "incomplete",
        "completeness_passed": False,
        "execution_fingerprint": "execution-fingerprint",
        "output_dir": str(tmp_path / "out"),
        "publication_bundle_fingerprint": "bundle-fingerprint",
        "publication_scientific_fingerprint": "scientific-fingerprint",
    }
