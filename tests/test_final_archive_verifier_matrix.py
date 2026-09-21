from __future__ import annotations

import copy
import json
import runpy
import shutil
from pathlib import Path

import pytest

import gazeaudit.korthals_execution_v2 as kv2e
import gazeaudit.korthals_source_lock as lock_module
import gazeaudit.pedrotti_execution as pe
import gazeaudit.provenance as provenance

ROOT = Path(__file__).resolve().parents[1]
KV2 = runpy.run_path(str(ROOT / "tests" / "test_korthals_execution_v2.py"))
PED = runpy.run_path(
    str(ROOT / "tests" / "test_bulk_pedrotti_execution_coverage.py")
)

_k_prepared = KV2["_synthetic_prepared"]
_k_context = KV2["_execution_context"]
_k_environment = KV2["_environment_text"]
_p_execution = PED["_execution36"]
_p_context = PED["_context"]


def _read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.write_text(provenance.canonical_json(value) + "\n", encoding="utf-8")


def _refresh_k_manifest(root: Path) -> None:
    path = root / "artifact_manifest.json"
    document = _read(path)
    core = dict(document)
    core.pop("artifact_manifest_fingerprint", None)
    document["artifact_manifest_fingerprint"] = provenance.fingerprint(core)
    _write(path, document)


def _refresh_k_execution(root: Path) -> None:
    path = root / "execution_manifest.json"
    document = _read(path)
    core = dict(document)
    core.pop("execution_fingerprint", None)
    document["execution_fingerprint"] = provenance.fingerprint(core)
    _write(path, document)


def _refresh_p_execution(root: Path) -> None:
    path = root / "execution_manifest.json"
    document = _read(path)
    core = dict(document)
    core.pop("execution_fingerprint", None)
    document["execution_fingerprint"] = provenance.fingerprint(core)
    _write(path, document)


def _refresh_p_artifact(root: Path) -> None:
    path = root / "artifact_manifest.json"
    document = _read(path)
    core = dict(document)
    core.pop("artifact_manifest_fingerprint", None)
    document["artifact_manifest_fingerprint"] = provenance.fingerprint(core)
    _write(path, document)


def _refresh_p_checksums(root: Path) -> None:
    pe._write_sha256sums(root)


def _clone(base: Path, tmp_path: Path, name: str) -> Path:
    target = tmp_path / name
    shutil.copytree(base, target)
    return target


def test_korthals_v2_archive_semantic_rejection_matrix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _k_prepared()
    execution = kv2e.run_korthals_aoi_execution_v2(prepared)
    base = tmp_path / "base-k"
    kv2e.write_korthals_execution_artifacts_v2(
        execution,
        base,
        execution_context=_k_context(prepared),
        environment_text=_k_environment(),
    )
    assert kv2e.verify_korthals_execution_artifacts_v2(base)

    lock = lock_module.load_korthals_source_lock()
    monkeypatch.setattr(
        kv2e,
        "_validated_execution_context_v2",
        lambda document, _prepared: dict(document),
    )
    monkeypatch.setattr(
        kv2e,
        "_validate_environment_snapshot",
        lambda _text: None,
    )

    def check(
        name: str,
        mutate,
        *,
        refresh_manifest: bool = False,
        refresh_execution: bool = False,
        lock_value: dict[str, object] | None = None,
    ) -> None:
        root = _clone(base, tmp_path, name)
        mutate(root)
        if refresh_execution:
            _refresh_k_execution(root)
        if refresh_manifest:
            _refresh_k_manifest(root)
        monkeypatch.setattr(
            kv2e,
            "verify_korthals_source_lock",
            lambda: copy.deepcopy(lock_value or lock),
        )
        assert not kv2e.verify_korthals_execution_artifacts_v2(root)

    check(
        "schema",
        lambda root: _mutate_json(
            root / "artifact_manifest.json",
            "schema",
            "wrong",
        ),
    )
    check(
        "artifact-fingerprint",
        lambda root: _mutate_json(
            root / "artifact_manifest.json",
            "artifact_manifest_fingerprint",
            "0" * 64,
        ),
    )
    for field, value in [
        ("case_study_id", "wrong"),
        ("protocol_fingerprint", "wrong"),
        ("source_lock_fingerprint", "wrong"),
        ("source_manifest_fingerprint", "wrong"),
        ("execution_fingerprint", "wrong"),
        ("classification", "wrong"),
        ("execution_commit", "wrong"),
        ("workflow_ref", "wrong"),
        ("github_run_id", "999"),
        ("audit_scientific_fingerprint", "wrong"),
    ]:
        check(
            "manifest-" + field,
            lambda root, f=field, v=value: _mutate_json(
                root / "artifact_manifest.json",
                f,
                v,
            ),
            refresh_manifest=True,
        )

    wrong_lock = copy.deepcopy(lock)
    wrong_lock["lock_fingerprint"] = "0" * 64
    check(
        "lock-fingerprint",
        lambda _root: None,
        lock_value=wrong_lock,
    )

    wrong_source_lock = copy.deepcopy(lock)
    wrong_source_lock["source"]["source_manifest_fingerprint"] = "0" * 64
    check(
        "lock-source-fingerprint",
        lambda _root: None,
        lock_value=wrong_source_lock,
    )

    for field, value in [
        ("protocol_fingerprint", "wrong"),
        ("companion_commit", "wrong"),
        ("missingness_policy", "wrong"),
    ]:
        check(
            "source-" + field,
            lambda root, f=field, v=value: _mutate_json(
                root / "source_identity.json",
                f,
                v,
            ),
        )

    check(
        "execution-fingerprint",
        lambda root: _mutate_json(
            root / "execution_manifest.json",
            "execution_fingerprint",
            "0" * 64,
        ),
    )
    check(
        "execution-source-identity",
        lambda root: _nested_mutate_json(
            root / "execution_manifest.json",
            "source_identity",
            "fixture",
            "changed",
        ),
        refresh_execution=True,
    )
    check(
        "declared-files",
        lambda root: _mutate_json(
            root / "artifact_manifest.json",
            "files",
            [],
        ),
        refresh_manifest=True,
    )

    root = _clone(base, tmp_path, "checksum-set")
    checksum = root / "SHA256SUMS"
    lines = checksum.read_text(encoding="utf-8").splitlines()
    checksum.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    monkeypatch.setattr(kv2e, "verify_korthals_source_lock", lambda: lock)
    assert not kv2e.verify_korthals_execution_artifacts_v2(root)

    root = _clone(base, tmp_path, "checksum-digest")
    checksum = root / "SHA256SUMS"
    lines = checksum.read_text(encoding="utf-8").splitlines()
    _digest, relative = lines[0].split("  ", 1)
    lines[0] = "0" * 64 + "  " + relative
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert not kv2e.verify_korthals_execution_artifacts_v2(root)


def _mutate_json(
    path: Path,
    field: str,
    value: object,
) -> None:
    document = _read(path)
    document[field] = value
    _write(path, document)


def _nested_mutate_json(
    path: Path,
    parent: str,
    field: str,
    value: object,
) -> None:
    document = _read(path)
    document[parent][field] = value
    _write(path, document)


def _build_pedrotti_base(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, object]:
    execution = _p_execution()
    root = tmp_path / "base-p"

    monkeypatch.setattr(
        pe,
        "_verify_locked_prepared",
        lambda value, **kwargs: value,
    )
    monkeypatch.setattr(
        pe,
        "verify_pedrotti_locked_execution_artifacts",
        lambda _root: True,
    )
    pe.write_pedrotti_locked_execution_artifacts(
        execution,
        root,
        execution_context=_p_context(),
        environment_text="numpy==2.5.3\npandas==2.3.3\n",
    )

    source_path = root / "source_identity.json"
    source = _read(source_path)
    source["numeric_trial_count"] = 1728
    _write(source_path, source)

    execution_path = root / "execution_manifest.json"
    execution_document = _read(execution_path)
    execution_document["numeric_trial_count"] = 1728
    execution_core = dict(execution_document)
    execution_core.pop("execution_fingerprint", None)
    execution_document["execution_fingerprint"] = provenance.fingerprint(execution_core)
    _write(execution_path, execution_document)

    artifact_path = root / "artifact_manifest.json"
    artifact = _read(artifact_path)
    artifact["execution_fingerprint"] = execution_document["execution_fingerprint"]
    artifact["files"] = pe._flat_file_records(
        root,
        excluded={"artifact_manifest.json", "SHA256SUMS"},
    )
    artifact_core = dict(artifact)
    artifact_core.pop("artifact_manifest_fingerprint", None)
    artifact["artifact_manifest_fingerprint"] = provenance.fingerprint(artifact_core)
    _write(artifact_path, artifact)

    _refresh_p_checksums(root)
    monkeypatch.undo()
    return root, execution


def test_pedrotti_archive_semantic_rejection_matrix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base, execution = _build_pedrotti_base(tmp_path, monkeypatch)
    source_fingerprint = execution.prepared.source_identity[
        "source_manifest_fingerprint"
    ]
    fake_lock = {
        "source": {
            "source_manifest_fingerprint": source_fingerprint,
        }
    }

    monkeypatch.setattr(
        pe,
        "verify_pedrotti_source_lock",
        lambda: copy.deepcopy(fake_lock),
    )
    monkeypatch.setattr(
        pe,
        "PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT",
        source_fingerprint,
    )
    monkeypatch.setattr(
        pe,
        "_validated_execution_context",
        lambda document: dict(document),
    )
    monkeypatch.setattr(
        pe,
        "_validate_environment_snapshot",
        lambda _text: None,
    )

    assert pe.verify_pedrotti_locked_execution_artifacts(base)

    def check(
        name: str,
        mutate,
        *,
        refresh_execution: bool = False,
        refresh_artifact: bool = False,
        refresh_checksums: bool = True,
    ) -> None:
        root = _clone(base, tmp_path, "p-" + name)
        mutate(root)
        if refresh_execution:
            _refresh_p_execution(root)
        if refresh_artifact:
            _refresh_p_artifact(root)
        if refresh_checksums:
            _refresh_p_checksums(root)
        assert not pe.verify_pedrotti_locked_execution_artifacts(root)

    for field, value in [
        ("source_manifest_fingerprint", "wrong"),
        ("protocol_fingerprint", "wrong"),
        ("participant_count", 35),
        ("numeric_trial_count", 1),
    ]:
        check(
            "source-" + field,
            lambda root, f=field, v=value: _mutate_json(
                root / "source_identity.json",
                f,
                v,
            ),
        )

    check(
        "families",
        lambda root: _mutate_first_list_record(
            root / "family_recovery.json",
            "recovery_fraction",
            0.123456,
        ),
    )

    check(
        "execution-fingerprint",
        lambda root: _mutate_json(
            root / "execution_manifest.json",
            "execution_fingerprint",
            "0" * 64,
        ),
    )

    for field, value in [
        ("schema", "wrong"),
        ("case_study_id", "wrong"),
        ("results_fingerprint", "wrong"),
        ("classification", "wrong"),
        ("protocol_fingerprint", "wrong"),
        ("source_lock_fingerprint", "wrong"),
        ("participant_count", 35),
        ("numeric_trial_count", 1),
        ("source_manifest_fingerprint", "wrong"),
        ("sampling_result_count", 4),
        ("missingness_result_count", 159),
        ("family_recovery_count", 8),
    ]:
        check(
            "execution-" + field,
            lambda root, f=field, v=value: _mutate_json(
                root / "execution_manifest.json",
                f,
                v,
            ),
            refresh_execution=True,
        )

    check(
        "artifact-fingerprint",
        lambda root: _mutate_json(
            root / "artifact_manifest.json",
            "artifact_manifest_fingerprint",
            "0" * 64,
        ),
    )

    for field, value in [
        ("schema", "wrong"),
        ("source_lock_fingerprint", "wrong"),
        ("source_manifest_fingerprint", "wrong"),
        ("execution_fingerprint", "wrong"),
        ("classification", "wrong"),
        ("execution_commit", "wrong"),
        ("github_run_id", 999),
        ("workflow_ref", "wrong"),
        ("files", []),
    ]:
        check(
            "artifact-" + field,
            lambda root, f=field, v=value: _mutate_json(
                root / "artifact_manifest.json",
                f,
                v,
            ),
            refresh_artifact=True,
        )

    root = _clone(base, tmp_path, "p-checksum-set")
    checksum = root / "SHA256SUMS"
    lines = checksum.read_text(encoding="utf-8").splitlines()
    checksum.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    assert not pe.verify_pedrotti_locked_execution_artifacts(root)

    root = _clone(base, tmp_path, "p-checksum-digest")
    checksum = root / "SHA256SUMS"
    lines = checksum.read_text(encoding="utf-8").splitlines()
    _digest, relative = lines[0].split("  ", 1)
    lines[0] = "0" * 64 + "  " + relative
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert not pe.verify_pedrotti_locked_execution_artifacts(root)


def _mutate_first_list_record(
    path: Path,
    field: str,
    value: object,
) -> None:
    values = json.loads(path.read_text(encoding="utf-8"))
    values[0][field] = value
    _write(path, values)
