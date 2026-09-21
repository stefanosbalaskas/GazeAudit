from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

import gazeaudit.korthals_freeze as kfreeze
import gazeaudit.korthals_freeze_v2 as kfreeze2
import gazeaudit.korthals_osf as kosf
import gazeaudit.pedrotti_fetch as pfetch
import gazeaudit.pedrotti_freeze as pfreeze


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _minimal_intake(root: Path) -> None:
    root.mkdir(parents=True)
    _write_json(
        root / "source_manifest.json",
        {"source_manifest_fingerprint": "s" * 64},
    )
    _write_json(
        root / "intake_summary.json",
        {"summary": "endpoint-blind"},
    )
    _write_json(
        root / "artifact_manifest.json",
        {"artifact_manifest_fingerprint": "a" * 64},
    )
    (root / "SHA256SUMS").write_text("", encoding="utf-8")


def _freeze_context(workflow: str) -> dict[str, object]:
    return {
        "execution_commit": "a" * 40,
        "workflow_ref": workflow,
        "github_run_id": "123",
    }


def _write_fake_korthals_freeze(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    intake = tmp_path / "k-intake"
    _minimal_intake(intake)
    context = _freeze_context(kfreeze.KORTHALS_FREEZE_WORKFLOW)
    monkeypatch.setattr(
        kfreeze,
        "verify_korthals_source_intake_artifacts",
        lambda _path: True,
    )
    monkeypatch.setattr(
        kfreeze,
        "_validated_execution_context",
        lambda _document, _intake: dict(context),
    )
    output = tmp_path / "k-freeze"
    kfreeze.write_korthals_source_freeze_artifacts(
        intake,
        output,
        execution_context={},
        environment_text="gazeaudit==test\n",
    )
    return output


def _write_fake_korthals_freeze_v2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    intake = tmp_path / "k2-intake"
    _minimal_intake(intake)
    context = _freeze_context(kfreeze2.KORTHALS_FREEZE_WORKFLOW)
    monkeypatch.setattr(
        kfreeze2,
        "verify_korthals_source_intake_artifacts_v2",
        lambda _path: True,
    )
    monkeypatch.setattr(
        kfreeze2,
        "_validated_execution_context_v2",
        lambda _document, _intake: dict(context),
    )
    output = tmp_path / "k2-freeze"
    kfreeze2.write_korthals_source_freeze_artifacts_v2(
        intake,
        output,
        execution_context={},
        environment_text="gazeaudit==test\n",
    )
    return output


def _write_fake_pedrotti_freeze(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    intake = tmp_path / "p-intake"
    _minimal_intake(intake)
    context = _freeze_context(pfreeze.PEDROTTI_FREEZE_WORKFLOW)
    monkeypatch.setattr(
        pfreeze,
        "verify_pedrotti_source_intake_artifacts",
        lambda _path: True,
    )
    monkeypatch.setattr(
        pfreeze,
        "_validated_execution_context",
        lambda _document, _intake: dict(context),
    )
    output = tmp_path / "p-freeze"
    pfreeze.write_pedrotti_source_freeze_artifacts(
        intake,
        output,
        execution_context={},
        environment_text="gazeaudit==test\n",
    )
    return output


def _rewrite_freeze_manifest(
    module,
    root: Path,
    mutate,
    *,
    fingerprint_key: str = "freeze_manifest_fingerprint",
) -> None:
    path = root / "freeze_manifest.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    mutate(document)
    core = dict(document)
    core.pop(fingerprint_key, None)
    document[fingerprint_key] = module.fingerprint(core)
    module._write_json(path, document)


@pytest.mark.parametrize(
    ("writer", "verify_name", "message"),
    [
        (
            kfreeze.write_korthals_source_freeze_artifacts,
            "verify_korthals_source_intake_artifacts",
            "valid Korthals source-intake",
        ),
        (
            kfreeze2.write_korthals_source_freeze_artifacts_v2,
            "verify_korthals_source_intake_artifacts_v2",
            "valid Korthals protocol-v2 source intake",
        ),
        (
            pfreeze.write_pedrotti_source_freeze_artifacts,
            "verify_pedrotti_source_intake_artifacts",
            "valid Pedrotti source-intake",
        ),
    ],
)
def test_freeze_writers_require_valid_intake(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    writer,
    verify_name: str,
    message: str,
) -> None:
    module = sys.modules[writer.__module__]
    monkeypatch.setattr(module, verify_name, lambda _path: False)
    with pytest.raises(ValueError, match=message):
        writer(
            tmp_path / "missing",
            tmp_path / "out",
            execution_context={},
            environment_text="x",
        )


@pytest.mark.parametrize(
    ("module", "writer", "verify_name", "validator_name"),
    [
        (
            kfreeze,
            kfreeze.write_korthals_source_freeze_artifacts,
            "verify_korthals_source_intake_artifacts",
            "_validated_execution_context",
        ),
        (
            kfreeze2,
            kfreeze2.write_korthals_source_freeze_artifacts_v2,
            "verify_korthals_source_intake_artifacts_v2",
            "_validated_execution_context_v2",
        ),
        (
            pfreeze,
            pfreeze.write_pedrotti_source_freeze_artifacts,
            "verify_pedrotti_source_intake_artifacts",
            "_validated_execution_context",
        ),
    ],
)
def test_freeze_writers_require_environment_and_fail_if_self_verification_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module,
    writer,
    verify_name: str,
    validator_name: str,
) -> None:
    intake = tmp_path / "intake"
    _minimal_intake(intake)
    monkeypatch.setattr(module, verify_name, lambda _path: True)
    monkeypatch.setattr(
        module,
        validator_name,
        lambda _document, _intake: _freeze_context(
            getattr(module, "KORTHALS_FREEZE_WORKFLOW", pfreeze.PEDROTTI_FREEZE_WORKFLOW)
        ),
    )
    with pytest.raises(ValueError, match="environment_text"):
        writer(
            intake,
            tmp_path / "blank",
            execution_context={},
            environment_text=" ",
        )

    verifier = (
        "verify_korthals_source_freeze_artifacts_v2"
        if module is kfreeze2
        else "verify_korthals_source_freeze_artifacts"
        if module is kfreeze
        else "verify_pedrotti_source_freeze_artifacts"
    )
    monkeypatch.setattr(module, verifier, lambda _path: False)
    with pytest.raises(RuntimeError, match="failed verification"):
        writer(
            intake,
            tmp_path / "bad",
            execution_context={},
            environment_text="x\n",
        )


@pytest.mark.parametrize(
    ("builder", "verifier"),
    [
        (_write_fake_korthals_freeze, kfreeze.verify_korthals_source_freeze_artifacts),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
        ),
        (_write_fake_pedrotti_freeze, pfreeze.verify_pedrotti_source_freeze_artifacts),
    ],
)
def test_freeze_verifiers_reject_non_directory_extra_entry_and_blank_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    builder,
    verifier,
) -> None:
    assert verifier(tmp_path / "missing") is False

    root = builder(tmp_path, monkeypatch)
    (root / "extra.txt").write_text("x", encoding="utf-8")
    assert verifier(root) is False
    (root / "extra.txt").unlink()

    (root / "pip_freeze.txt").write_text("\n", encoding="utf-8")
    assert verifier(root) is False


@pytest.mark.parametrize(
    ("builder", "module", "verifier", "field", "value"),
    [
        (
            _write_fake_korthals_freeze,
            kfreeze,
            kfreeze.verify_korthals_source_freeze_artifacts,
            "schema",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze,
            kfreeze,
            kfreeze.verify_korthals_source_freeze_artifacts,
            "case_study_id",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze,
            kfreeze,
            kfreeze.verify_korthals_source_freeze_artifacts,
            "protocol_fingerprint",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze,
            kfreeze,
            kfreeze.verify_korthals_source_freeze_artifacts,
            "source_manifest_fingerprint",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze,
            kfreeze,
            kfreeze.verify_korthals_source_freeze_artifacts,
            "intake_artifact_manifest_fingerprint",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze,
            kfreeze,
            kfreeze.verify_korthals_source_freeze_artifacts,
            "execution_commit",
            "b" * 40,
        ),
        (
            _write_fake_korthals_freeze,
            kfreeze,
            kfreeze.verify_korthals_source_freeze_artifacts,
            "workflow_ref",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze,
            kfreeze,
            kfreeze.verify_korthals_source_freeze_artifacts,
            "github_run_id",
            "999",
        ),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
            "schema",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
            "case_study_id",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
            "protocol_fingerprint",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
            "source_manifest_fingerprint",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
            "intake_artifact_manifest_fingerprint",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
            "execution_commit",
            "b" * 40,
        ),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
            "workflow_ref",
            "wrong",
        ),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
            "github_run_id",
            "999",
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "schema",
            "wrong",
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "case_study_id",
            "wrong",
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "protocol_fingerprint",
            "wrong",
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "source_manifest_fingerprint",
            "wrong",
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "intake_artifact_manifest_fingerprint",
            "wrong",
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "execution_commit",
            "b" * 40,
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "workflow_ref",
            "wrong",
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "github_run_id",
            "999",
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "zenodo_record",
            -1,
        ),
        (
            _write_fake_pedrotti_freeze,
            pfreeze,
            pfreeze.verify_pedrotti_source_freeze_artifacts,
            "scientific_endpoint_evaluated",
            True,
        ),
    ],
)
def test_freeze_verifiers_bind_manifest_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    builder,
    module,
    verifier,
    field: str,
    value: object,
) -> None:
    root = builder(tmp_path, monkeypatch)
    _rewrite_freeze_manifest(
        module,
        root,
        lambda document: document.__setitem__(field, value),
    )
    assert verifier(root) is False


@pytest.mark.parametrize(
    ("builder", "module", "verifier"),
    [
        (_write_fake_korthals_freeze, kfreeze, kfreeze.verify_korthals_source_freeze_artifacts),
        (
            _write_fake_korthals_freeze_v2,
            kfreeze2,
            kfreeze2.verify_korthals_source_freeze_artifacts_v2,
        ),
        (_write_fake_pedrotti_freeze, pfreeze, pfreeze.verify_pedrotti_source_freeze_artifacts),
    ],
)
def test_freeze_verifiers_check_manifest_fingerprint_files_and_checksums(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    builder,
    module,
    verifier,
) -> None:
    root = builder(tmp_path, monkeypatch)
    manifest_path = root / "freeze_manifest.json"
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    document["freeze_manifest_fingerprint"] = "0" * 64
    module._write_json(manifest_path, document)
    assert verifier(root) is False

    root = builder(tmp_path / "second", monkeypatch)
    _rewrite_freeze_manifest(
        module,
        root,
        lambda document: document.__setitem__("files", []),
    )
    assert verifier(root) is False

    root = builder(tmp_path / "third", monkeypatch)
    checksum_path = root / "SHA256SUMS"
    lines = checksum_path.read_text(encoding="utf-8").splitlines()
    checksum_path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    assert verifier(root) is False

    root = builder(tmp_path / "fourth", monkeypatch)
    checksum_path = root / "SHA256SUMS"
    lines = checksum_path.read_text(encoding="utf-8").splitlines()
    digest, name = lines[0].split("  ", 1)
    del digest
    lines[0] = "0" * 64 + "  " + name
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert verifier(root) is False

    root = builder(tmp_path / "fifth", monkeypatch)
    (root / "freeze_manifest.json").write_text("{", encoding="utf-8")
    assert verifier(root) is False


def _korthals_context_base(module, intake: Path) -> dict[str, object]:
    source = json.loads((intake / "source_manifest.json").read_text(encoding="utf-8"))
    protocol = (
        module.KORTHALS_V2_PROTOCOL_FINGERPRINT
        if module is kfreeze2
        else module.KORTHALS_PROTOCOL_FINGERPRINT
    )
    return {
        "repository": "stefanosbalaskas/GazeAudit",
        "execution_commit": "a" * 40,
        "workflow_ref": module.KORTHALS_FREEZE_WORKFLOW,
        "github_run_id": "123",
        "companion_repository": module.KORTHALS_COMPANION_REPOSITORY,
        "companion_commit": module.KORTHALS_COMPANION_COMMIT,
        "protocol_fingerprint": protocol,
        "source_manifest_fingerprint": source["source_manifest_fingerprint"],
        "package_version": "test-version",
        "python_version": "3.12",
        "platform": "test",
        "runner_os": "Linux",
        "runner_arch": "X64",
    }


@pytest.mark.parametrize("module", [kfreeze, kfreeze2])
@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("repository", "wrong", "repository identity"),
        ("execution_commit", "XYZ", "40-character Git SHA"),
        ("workflow_ref", "wrong", "workflow identity"),
        ("github_run_id", 0, "positive integer"),
        ("companion_repository", "wrong", "companion repository"),
        ("companion_commit", "wrong", "companion commit"),
        ("protocol_fingerprint", "wrong", "protocol"),
        ("source_manifest_fingerprint", "wrong", "source fingerprint"),
        ("package_version", "wrong", "package version"),
        ("python_version", "", "non-empty string"),
    ],
)
def test_korthals_execution_context_validation_guards(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module,
    field: str,
    value: object,
    message: str,
) -> None:
    intake = tmp_path / "intake"
    _minimal_intake(intake)
    base = _korthals_context_base(module, intake)
    monkeypatch.setattr(module, "version", lambda _name: "test-version")
    validator = (
        module._validated_execution_context_v2
        if module is kfreeze2
        else module._validated_execution_context
    )
    bad = dict(base)
    bad[field] = value
    with pytest.raises(ValueError, match=message):
        validator(bad, intake)

    missing = dict(base)
    missing.pop("runner_arch")
    with pytest.raises(ValueError, match="exact required field set"):
        validator(missing, intake)

    assert validator(base, intake) == base


def _pedrotti_context_base(intake: Path) -> dict[str, object]:
    source = json.loads((intake / "source_manifest.json").read_text(encoding="utf-8"))
    return {
        "repository": "stefanosbalaskas/GazeAudit",
        "execution_commit": "a" * 40,
        "workflow_ref": pfreeze.PEDROTTI_FREEZE_WORKFLOW,
        "github_run_id": "123",
        "protocol_fingerprint": pfreeze.PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": source["source_manifest_fingerprint"],
        "zenodo_doi": pfreeze.PEDROTTI_ZENODO_DOI,
        "zenodo_record": pfreeze.PEDROTTI_ZENODO_RECORD,
        "package_version": "test-version",
        "python_version": "3.12",
        "platform": "test",
        "runner_os": "Linux",
        "runner_arch": "X64",
    }


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("repository", "wrong", "repository identity"),
        ("execution_commit", "XYZ", "40-character Git SHA"),
        ("workflow_ref", "wrong", "workflow identity"),
        ("github_run_id", 0, "positive integer"),
        ("protocol_fingerprint", "wrong", "protocol fingerprint"),
        ("source_manifest_fingerprint", "wrong", "source fingerprint"),
        ("zenodo_doi", "wrong", "Zenodo DOI"),
        ("zenodo_record", -1, "Zenodo record"),
        ("package_version", "wrong", "package version"),
        ("runner_os", "", "non-empty string"),
    ],
)
def test_pedrotti_execution_context_validation_guards(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
    message: str,
) -> None:
    intake = tmp_path / "intake"
    _minimal_intake(intake)
    base = _pedrotti_context_base(intake)
    monkeypatch.setattr(pfreeze, "version", lambda _name: "test-version")
    bad = dict(base)
    bad[field] = value
    with pytest.raises(ValueError, match=message):
        pfreeze._validated_execution_context(bad, intake)

    missing = dict(base)
    missing.pop("runner_arch")
    with pytest.raises(ValueError, match="exact required field set"):
        pfreeze._validated_execution_context(missing, intake)

    assert pfreeze._validated_execution_context(base, intake) == base


@pytest.mark.parametrize("module", [kfreeze, pfreeze])
def test_freeze_filesystem_json_and_checksum_helpers(
    tmp_path: Path,
    module,
) -> None:
    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory path"):
        module._prepare_destination(file_path, overwrite=False)

    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "keep.txt").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="not empty"):
        module._prepare_destination(nonempty, overwrite=False)

    nested = tmp_path / "replace"
    nested.mkdir()
    (nested / "old.txt").write_text("x", encoding="utf-8")
    (nested / "sub").mkdir()
    (nested / "sub" / "old.txt").write_text("x", encoding="utf-8")
    module._prepare_destination(nested, overwrite=True)
    assert list(nested.iterdir()) == []

    array_json = tmp_path / "array.json"
    array_json.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        module._read_json(array_json)

    checksums = tmp_path / "checksums"
    checksums.write_text("\n" + "a" * 64 + "  file.txt\n", encoding="utf-8")
    assert module._parse_checksums(checksums)["file.txt"] == "a" * 64

    checksums.write_text("bad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid SHA256SUMS entry"):
        module._parse_checksums(checksums)

    checksums.write_text(
        "a" * 64 + "  ../file.txt\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid or duplicate"):
        module._parse_checksums(checksums)


def test_korthals_v2_reuses_freeze_filesystem_helpers(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "file.txt").write_text("x", encoding="utf-8")
    kfreeze2._prepare_destination(root, overwrite=True)
    assert list(root.iterdir()) == []


# ---------------------------------------------------------------------------
# Korthals OSF transport/inventory guards
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "algorithm", "message"),
    [
        (None, "md5", "missing required"),
        (" ", "md5", "missing required"),
        ("x" * 32, "md5", "invalid md5"),
        ("a" * 63, "sha256", "invalid sha256"),
    ],
)
def test_osf_hash_normalization_rejects_invalid_values(
    value,
    algorithm: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        kosf._normalise_hash(value, algorithm=algorithm, remote_path="/x")

    assert (
        kosf._normalise_hash(
            " " + "A" * 32 + " ",
            algorithm="md5",
            remote_path="/x",
        )
        == "a" * 32
    )


class _RemoteIdentity:
    def __init__(self, path: str, name: str) -> None:
        self.path = path
        self.name = name


@pytest.mark.parametrize(
    ("remote", "message"),
    [
        (_RemoteIdentity("relative/file", "file"), "invalid OSF file identity"),
        (_RemoteIdentity("/folder/file", "bad/name"), "invalid OSF file identity"),
        (_RemoteIdentity("/../file", "file"), "parent traversal"),
    ],
)
def test_osf_companion_destination_guards(
    remote: _RemoteIdentity,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        kosf._companion_destination(remote)


def test_osf_companion_destination_must_remain_under_data_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(kosf, "KORTHALS_DATA_ROOT", Path("elsewhere"))
    with pytest.raises(ValueError, match="escapes data root"):
        kosf._companion_destination(_RemoteIdentity("/raw/file", "file"))


class _OSFFile:
    def __init__(
        self,
        path: str,
        name: str,
        hashes,
    ) -> None:
        self.path = path
        self.name = name
        self.hashes = hashes


def _install_fake_osfclient(
    monkeypatch: pytest.MonkeyPatch,
    files: list[_OSFFile],
) -> None:
    class FakeOSF:
        def project(self, project_id: str):
            assert project_id == kosf.KORTHALS_OSF_PROJECT_ID
            return SimpleNamespace(
                storages=[
                    SimpleNamespace(files=files),
                ]
            )

    module = ModuleType("osfclient")
    module.OSF = FakeOSF
    monkeypatch.setitem(sys.modules, "osfclient", module)


def test_osf_default_inventory_builds_checksum_locked_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    files = [
        _OSFFile(
            "/raw/a.bin",
            "a.bin",
            {"md5": "A" * 32, "sha256": "b" * 64},
        ),
        _OSFFile(
            "/clean/b.bin",
            "b.bin",
            {"md5": "c" * 32, "sha256": ""},
        ),
    ]
    _install_fake_osfclient(monkeypatch, files)
    records = kosf._default_remote_inventory()
    assert [record.destination for record in records] == [
        "data/clean/b.bin",
        "data/raw/a.bin",
    ]
    assert records[1].md5 == "a" * 32
    assert records[1].sha256 == "b" * 64
    assert records[0].sha256 is None


def test_osf_default_inventory_rejects_missing_checksums_duplicates_and_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_osfclient(
        monkeypatch,
        [_OSFFile("/raw/a.bin", "a.bin", None)],
    )
    with pytest.raises(ValueError, match="no checksum mapping"):
        kosf._default_remote_inventory()

    _install_fake_osfclient(
        monkeypatch,
        [
            _OSFFile("/raw/a.bin", "a.bin", {"md5": "a" * 32}),
            _OSFFile("/raw/a.bin", "a.bin", {"md5": "a" * 32}),
        ],
    )
    with pytest.raises(ValueError, match="duplicate OSF remote path"):
        kosf._default_remote_inventory()

    _install_fake_osfclient(
        monkeypatch,
        [
            _OSFFile("/raw/a.bin", "a.bin", {"md5": "a" * 32}),
            _OSFFile("/raw/other", "a.bin", {"md5": "b" * 32}),
        ],
    )
    with pytest.raises(ValueError, match="duplicate companion destination"):
        kosf._default_remote_inventory()

    _install_fake_osfclient(monkeypatch, [])
    with pytest.raises(ValueError, match="inventory is empty"):
        kosf._default_remote_inventory()


def test_osf_scrub_rejects_directory_at_expected_file_destination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    remote = kosf.KorthalsRemoteFile(
        remote_path="/raw/a.bin",
        destination="data/raw/a.bin",
        md5="a" * 32,
        sha256=None,
    )
    Path(remote.destination).mkdir(parents=True)
    with pytest.raises(ValueError, match="not a regular file"):
        kosf._scrub_unverified_local_files([remote])


def test_osf_complete_source_reports_missing_and_mismatched_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    payload = b"expected"
    remote_missing = kosf.KorthalsRemoteFile(
        "/raw/a.bin",
        "data/raw/a.bin",
        hashlib.md5(payload).hexdigest(),
        None,
    )
    remote_bad = kosf.KorthalsRemoteFile(
        "/raw/b.bin",
        "data/raw/b.bin",
        hashlib.md5(payload).hexdigest(),
        None,
    )
    bad = Path(remote_bad.destination)
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_bytes(b"wrong")
    with pytest.raises(ValueError, match="missing=.*a.bin.*mismatched=.*b.bin"):
        kosf._verify_complete_local_source([remote_missing, remote_bad])


def test_osf_default_companion_download_preserves_frozen_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    utils = ModuleType("eyemovement_data.utils")

    def download_osf_data(**kwargs: object) -> None:
        calls.append(dict(kwargs))

    utils.download_osf_data = download_osf_data
    parent = ModuleType("eyemovement_data")
    parent.utils = utils
    monkeypatch.setitem(sys.modules, "eyemovement_data", parent)
    monkeypatch.setitem(sys.modules, "eyemovement_data.utils", utils)

    kosf._default_companion_download()
    assert calls == [
        {
            "raw_clean": "both",
            "train_test": "both",
            "participants": "all",
            "overwrite": False,
        }
    ]


@pytest.mark.parametrize("value", [True, "1"])
def test_osf_backoff_requires_numeric_non_boolean(value) -> None:
    with pytest.raises(ValueError, match="non-negative number"):
        kosf.fetch_korthals_osf_resumable(
            initial_backoff_seconds=value,  # type: ignore[arg-type]
            inventory_fn=lambda: (),
            download_fn=lambda: None,
        )


def test_osf_fetch_rejects_empty_inventory() -> None:
    with pytest.raises(ValueError, match="inventory is empty"):
        kosf.fetch_korthals_osf_resumable(
            inventory_fn=lambda: (),
            download_fn=lambda: None,
        )


# ---------------------------------------------------------------------------
# Pedrotti Zenodo transport/parser guards
# ---------------------------------------------------------------------------


class _Response:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.offset = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        return False

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            return self.payload
        if self.offset:
            return b""
        self.offset = len(self.payload)
        return self.payload


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"max_attempts": 0}, "max_attempts"),
        ({"max_attempts": True}, "max_attempts"),
        ({"initial_backoff_seconds": -1}, "initial_backoff_seconds"),
        ({"timeout_seconds": 0}, "timeout_seconds"),
        ({"metadata_max_attempts": 0}, "metadata_max_attempts"),
        ({"metadata_max_attempts": True}, "metadata_max_attempts"),
        ({"metadata_timeout_seconds": 0}, "metadata_timeout_seconds"),
    ],
)
def test_pedrotti_fetch_argument_guards(
    tmp_path: Path,
    kwargs: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        pfetch.fetch_pedrotti_zenodo_source(tmp_path / "out", **kwargs)


def test_pedrotti_fetch_rejects_file_output_and_unexpected_entries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory path"):
        pfetch.fetch_pedrotti_zenodo_source(file_path)

    root = tmp_path / "root"
    root.mkdir()
    (root / "unexpected").mkdir()
    monkeypatch.setattr(pfetch, "expected_pedrotti_md5", lambda: {"01.txt": "a" * 32})
    with pytest.raises(ValueError, match="unexpected entries"):
        pfetch.fetch_pedrotti_zenodo_source(root)


def test_pedrotti_json_metadata_requires_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(pfetch, "urlopen", lambda *args, **kwargs: _Response(b"[]"))
    with pytest.raises(ValueError, match="JSON object"):
        pfetch._fetch_json_record_once(1.0)


def test_pedrotti_record_html_skips_unverifiable_rows_and_rejects_duplicates_or_empty() -> None:
    doi = pfetch.PEDROTTI_ZENODO_DOI
    no_checksum = (
        f"<html><body>{doi}<table><tr><td>"
        '<a href="/records/7962917/files/01.txt?download=1">01</a>'
        "</td></tr></table></body></html>"
    ).encode()
    with pytest.raises(ValueError, match="verifiable file table"):
        pfetch._metadata_from_record_html(no_checksum)

    no_link = (
        f"<html><body>{doi}<table><tr><td>md5:{'a' * 32}</td></tr>"
        "</table></body></html>"
    ).encode()
    with pytest.raises(ValueError, match="verifiable file table"):
        pfetch._metadata_from_record_html(no_link)

    duplicate = (
        f"<html><body>{doi}<table>"
        f'<tr><td><a href="/records/7962917/files/01.txt?download=1">01</a> md5:{"a" * 32}</td></tr>'
        f'<tr><td><a href="/records/7962917/files/01.txt?download=1">01</a> md5:{"a" * 32}</td></tr>'
        "</table></body></html>"
    ).encode()
    with pytest.raises(ValueError, match="duplicate Zenodo filename"):
        pfetch._metadata_from_record_html(duplicate)


@pytest.mark.parametrize(
    "url",
    [
        "https://zenodo.org/records/7962917/files/",
        "https://zenodo.org/records/7962917/files/a/b?download=1",
        "https://zenodo.org/records/7962917/files/%2F?download=1",
        "https://zenodo.org/records/7962917/files/a.txt?download=0",
    ],
)
def test_pedrotti_record_download_name_rejects_invalid_shapes(url: str) -> None:
    assert pfetch._pedrotti_record_download_name(url) is None


@pytest.mark.parametrize(
    ("contract", "message"),
    [
        ({1: "a" * 32}, "structurally invalid"),
        ({"a.txt": 123}, "structurally invalid"),
        ({"a.txt": "x" * 32}, "MD5 is invalid"),
        ({}, "contract is empty"),
    ],
)
def test_pedrotti_frozen_contract_validation(
    contract,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        pfetch._remote_contract_from_frozen_contract(contract)


@pytest.mark.parametrize(
    ("metadata", "expected", "message"),
    [
        ({}, {"a.txt": "a" * 32}, "files list"),
        ({"files": ["bad"]}, {"a.txt": "a" * 32}, "must contain objects"),
        (
            {"files": [{"key": "a.txt"}]},
            {"a.txt": "a" * 32},
            "structurally incomplete",
        ),
        (
            {
                "files": [
                    {"key": "a.txt", "checksum": "md5:" + "a" * 32},
                    {"key": "a.txt", "checksum": "md5:" + "a" * 32},
                ]
            },
            {"a.txt": "a" * 32},
            "duplicate Zenodo filename",
        ),
        (
            {"files": [{"key": "a.txt", "checksum": "sha256:" + "a" * 64}]},
            {"a.txt": "a" * 32},
            "not MD5",
        ),
        (
            {"files": [{"key": "b.txt", "checksum": "md5:" + "b" * 32}]},
            {"a.txt": "a" * 32},
            "file set differs",
        ),
    ],
)
def test_pedrotti_remote_metadata_contract_guards(
    metadata,
    expected,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        pfetch._verified_remote_contract(metadata, expected)


def test_pedrotti_verified_download_retries_after_bad_md5_and_cleans_partial(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "a.txt"
    partial = tmp_path / "a.txt.part"
    partial.write_bytes(b"stale")
    payloads = iter([b"wrong", b"right"])
    sleeps: list[float] = []

    monkeypatch.setattr(
        pfetch,
        "urlopen",
        lambda *args, **kwargs: _Response(next(payloads)),
    )
    monkeypatch.setattr(pfetch.time, "sleep", sleeps.append)

    attempts = pfetch._download_verified_file(
        "https://zenodo.org/records/7962917/files/a.txt?download=1",
        destination,
        expected_md5=hashlib.md5(b"right", usedforsecurity=False).hexdigest(),
        max_attempts=2,
        initial_backoff_seconds=0.25,
        timeout_seconds=1.0,
    )

    assert attempts == 2
    assert destination.read_bytes() == b"right"
    assert not partial.exists()
    assert sleeps == [0.25]


def test_pedrotti_verified_download_exhaustion_is_runtime_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        pfetch,
        "urlopen",
        lambda *args, **kwargs: _Response(b"wrong"),
    )
    monkeypatch.setattr(pfetch.time, "sleep", lambda _value: None)
    destination = tmp_path / "a.txt"

    with pytest.raises(RuntimeError, match="failed to download"):
        pfetch._download_verified_file(
            "https://zenodo.org/records/7962917/files/a.txt?download=1",
            destination,
            expected_md5="a" * 32,
            max_attempts=1,
            initial_backoff_seconds=0,
            timeout_seconds=1.0,
        )

    assert not (tmp_path / "a.txt.part").exists()
