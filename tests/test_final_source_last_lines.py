from __future__ import annotations

import runpy
from pathlib import Path

import pandas as pd
import pytest

import gazeaudit.korthals_source as ks
import gazeaudit.pedrotti_source as ps
import gazeaudit.provenance as provenance


ROOT = Path(__file__).resolve().parents[1]
SOURCE = runpy.run_path(str(ROOT / "tests" / "test_final_source_closure.py"))
KS_BASE = runpy.run_path(str(ROOT / "tests" / "test_korthals_source.py"))

_make_source_tree = KS_BASE["_make_source_tree"]
_FakeParticipant = KS_BASE["_FakeParticipant"]
_FakePreprocessor = KS_BASE["_FakePreprocessor"]
_configure_fakes = KS_BASE["_configure_fakes"]
_pedrotti_manifest_fixture = SOURCE["_pedrotti_manifest_fixture"]
_valid_summary_and_source = SOURCE["_valid_summary_and_source"]


def _rehash_korthals(document: dict[str, object]) -> None:
    core = dict(document)
    core.pop("source_manifest_fingerprint", None)
    document["source_manifest_fingerprint"] = provenance.fingerprint(core)


def _refresh_k_intake_manifest(root: Path) -> None:
    source = ks.json.loads(
        (root / "source_manifest.json").read_text(encoding="utf-8")
    )
    path = root / "artifact_manifest.json"
    manifest = ks.json.loads(path.read_text(encoding="utf-8"))
    manifest["files"] = [
        ks._file_record(root / "intake_summary.json", root),
        ks._file_record(root / "source_manifest.json", root),
    ]
    manifest["source_manifest_fingerprint"] = source[
        "source_manifest_fingerprint"
    ]
    core = dict(manifest)
    core.pop("artifact_manifest_fingerprint", None)
    manifest["artifact_manifest_fingerprint"] = provenance.fingerprint(core)
    ks._write_json(path, manifest)


def _refresh_k_checksums(root: Path) -> None:
    targets = sorted(
        path
        for path in root.iterdir()
        if path.is_file() and path.name != "SHA256SUMS"
    )
    (root / "SHA256SUMS").write_text(
        "\n".join(
            f"{ks._sha256_file(path)}  {path.name}"
            for path in targets
        )
        + "\n",
        encoding="utf-8",
    )


def test_korthals_empty_inventory_after_forced_discovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "data"
    (root / "raw").mkdir(parents=True)
    (root / "clean").mkdir()
    monkeypatch.setattr(
        ks,
        "discover_korthals_participants",
        lambda _root: ["p1"],
    )
    with pytest.raises(ValueError, match="contains no raw/clean files"):
        ks.build_korthals_source_manifest(root)


def test_korthals_manifest_rejects_nonmapping_file_record(
    tmp_path: Path,
) -> None:
    manifest = ks.build_korthals_source_manifest(
        _make_source_tree(tmp_path)
    )
    manifest["files"][0] = "bad"
    _rehash_korthals(manifest)
    assert not ks.verify_korthals_source_manifest(manifest)


def test_korthals_prepared_participant_count_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_source_tree(tmp_path)
    _configure_fakes()
    baseline = ks.prepare_korthals_from_companion(
        root,
        participant_factory=_FakeParticipant,
        preprocessor_factory=_FakePreprocessor,
    )
    bad_identity = dict(baseline.prepared.source_identity)
    bad_identity["participant_count"] = 999
    bad_prepared = type(baseline.prepared)(
        data=baseline.prepared.data,
        validation_groups=baseline.prepared.validation_groups,
        source_identity=bad_identity,
    )
    monkeypatch.setattr(
        ks,
        "prepare_korthals_aligned_data",
        lambda *args, **kwargs: bad_prepared,
    )
    with pytest.raises(ValueError, match="participant count differs"):
        ks.prepare_korthals_from_companion(
            root,
            participant_factory=_FakeParticipant,
            preprocessor_factory=_FakePreprocessor,
        )


def _valid_k_intake(
    tmp_path: Path,
) -> tuple[object, Path]:
    root = _make_source_tree(tmp_path / "source")
    _configure_fakes()
    intake = ks.prepare_korthals_from_companion(
        root,
        participant_factory=_FakeParticipant,
        preprocessor_factory=_FakePreprocessor,
    )
    output = tmp_path / "intake"
    ks.write_korthals_source_intake_artifacts(
        intake,
        output,
    )
    return intake, output


def test_korthals_writer_overwrite_unlinks_existing_files(
    tmp_path: Path,
) -> None:
    intake, _output = _valid_k_intake(tmp_path / "base")
    target = tmp_path / "replace"
    target.mkdir()
    old = target / "old.txt"
    old.write_text("old", encoding="utf-8")
    ks.write_korthals_source_intake_artifacts(
        intake,
        target,
        overwrite=True,
    )
    assert not old.exists()


def test_korthals_intake_verifier_remaining_branches(
    tmp_path: Path,
) -> None:
    _intake, base = _valid_k_intake(tmp_path / "base")

    missing = tmp_path / "missing"
    assert not ks.verify_korthals_source_intake_artifacts(missing)

    source_bad = tmp_path / "source-bad"
    ks.shutil.copytree(base, source_bad) if hasattr(ks, "shutil") else _copytree(base, source_bad)
    source = ks.json.loads(
        (source_bad / "source_manifest.json").read_text(encoding="utf-8")
    )
    source["schema"] = "wrong"
    ks._write_json(source_bad / "source_manifest.json", source)
    assert not ks.verify_korthals_source_intake_artifacts(source_bad)

    for name, field, value in [
        ("schema", "schema", "wrong"),
        ("fingerprint", "artifact_manifest_fingerprint", "0" * 64),
        ("source-fp", "source_manifest_fingerprint", "wrong"),
    ]:
        root = _copytree(base, tmp_path / name)
        manifest_path = root / "artifact_manifest.json"
        manifest = ks.json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest[field] = value
        if field != "artifact_manifest_fingerprint":
            core = dict(manifest)
            core.pop("artifact_manifest_fingerprint", None)
            manifest["artifact_manifest_fingerprint"] = provenance.fingerprint(core)
        ks._write_json(manifest_path, manifest)
        assert not ks.verify_korthals_source_intake_artifacts(root)

    root = _copytree(base, tmp_path / "summary-fp")
    summary_path = root / "intake_summary.json"
    summary = ks.json.loads(summary_path.read_text(encoding="utf-8"))
    summary["source_manifest_fingerprint"] = "wrong"
    ks._write_json(summary_path, summary)
    _refresh_k_intake_manifest(root)
    _refresh_k_checksums(root)
    assert not ks.verify_korthals_source_intake_artifacts(root)

    root = _copytree(base, tmp_path / "checksum-set")
    checksum = root / "SHA256SUMS"
    lines = checksum.read_text(encoding="utf-8").splitlines()
    checksum.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    assert not ks.verify_korthals_source_intake_artifacts(root)

    root = _copytree(base, tmp_path / "malformed")
    (root / "artifact_manifest.json").write_text("{", encoding="utf-8")
    assert not ks.verify_korthals_source_intake_artifacts(root)


def _copytree(source: Path, target: Path) -> Path:
    import shutil

    shutil.copytree(source, target)
    return target


def test_korthals_decimal_exception_and_identity_skip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BadDecimal:
        def __init__(self, _value: object) -> None:
            raise ks.InvalidOperation

    monkeypatch.setattr(ks, "Decimal", BadDecimal)
    assert not ks._participant_identity_value_matches(
        "68471e16",
        "6.8471e20",
    )

    monkeypatch.undo()
    clean = tmp_path / "clean" / "train" / "p1"
    clean.mkdir(parents=True)
    (clean / "p1_gaze.csv").write_text(
        "participant_id\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="empty participant_id"):
        ks._canonicalize_companion_participant_identity(
            tmp_path / "clean",
            "p1",
            {},
        )

    (clean / "p1_gaze.csv").write_text(
        "participant_id\np1\n",
        encoding="utf-8",
    )
    clean_data = {
        "ignored": object(),
        "no_id": pd.DataFrame({"x": [1]}),
        "gaze": pd.DataFrame({"participant_id": ["p1"]}),
    }
    ks._canonicalize_companion_participant_identity(
        tmp_path / "clean",
        "p1",
        clean_data,
    )
    assert clean_data["gaze"]["participant_id"].tolist() == ["p1"]


# ---------------------------------------------------------------------------
# Pedrotti final source branches
# ---------------------------------------------------------------------------


def _valid_p_intake(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[object, Path]:
    manifest, expected = _pedrotti_manifest_fixture()
    summary, _source = _valid_summary_and_source()
    summary["source_manifest_fingerprint"] = manifest[
        "source_manifest_fingerprint"
    ]
    monkeypatch.setattr(
        ps,
        "expected_pedrotti_md5",
        lambda: dict(expected),
    )
    intake = ps.PedrottiSourceIntake(
        source_manifest=manifest,
        intake_summary=summary,
    )
    root = tmp_path / "intake"
    ps.write_pedrotti_source_intake_artifacts(
        intake,
        root,
    )
    return intake, root


def _refresh_p_artifact(root: Path) -> None:
    source = ps._read_json(root / "source_manifest.json")
    path = root / "artifact_manifest.json"
    artifact = ps._read_json(path)
    artifact["files"] = [
        ps._file_record(root / "intake_summary.json", root),
        ps._file_record(root / "source_manifest.json", root),
    ]
    artifact["source_manifest_fingerprint"] = source[
        "source_manifest_fingerprint"
    ]
    core = dict(artifact)
    core.pop("artifact_manifest_fingerprint", None)
    artifact["artifact_manifest_fingerprint"] = provenance.fingerprint(core)
    ps._write_json(path, artifact)


def _refresh_p_checksums(root: Path) -> None:
    targets = sorted(
        path
        for path in root.iterdir()
        if path.is_file() and path.name != "SHA256SUMS"
    )
    (root / "SHA256SUMS").write_text(
        "\n".join(
            f"{ps._digest_file(path, 'sha256')}  {path.name}"
            for path in targets
        )
        + "\n",
        encoding="utf-8",
    )


def test_pedrotti_expected_md5_success_and_verifier_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = ps.expected_pedrotti_md5()
    assert len(expected) == 37

    monkeypatch.setattr(
        ps,
        "canonical_json",
        lambda _value: (_ for _ in ()).throw(TypeError("forced")),
    )
    assert not ps.verify_pedrotti_source_manifest({})


def test_pedrotti_inspect_manifest_self_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ps,
        "build_pedrotti_source_manifest",
        lambda _root: {},
    )
    monkeypatch.setattr(
        ps,
        "verify_pedrotti_source_manifest",
        lambda _manifest: False,
    )
    with pytest.raises(RuntimeError, match="failed verification"):
        ps.inspect_pedrotti_source(tmp_path)


def test_pedrotti_intake_verifier_remaining_branches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _intake, base = _valid_p_intake(tmp_path / "base", monkeypatch)

    assert not ps.verify_pedrotti_source_intake_artifacts(
        tmp_path / "missing"
    )

    root = _copytree(base, tmp_path / "source-invalid")
    monkeypatch.setattr(
        ps,
        "verify_pedrotti_source_manifest",
        lambda _source: False,
    )
    assert not ps.verify_pedrotti_source_intake_artifacts(root)
    monkeypatch.undo()
    manifest, expected = _pedrotti_manifest_fixture()
    monkeypatch.setattr(
        ps,
        "expected_pedrotti_md5",
        lambda: dict(expected),
    )

    root = _copytree(base, tmp_path / "keys")
    artifact = ps._read_json(root / "artifact_manifest.json")
    artifact["extra"] = True
    ps._write_json(root / "artifact_manifest.json", artifact)
    assert not ps.verify_pedrotti_source_intake_artifacts(root)

    for name, field, value in [
        ("fp", "artifact_manifest_fingerprint", "0" * 64),
        ("schema", "schema", "wrong"),
        ("case", "case_study_id", "wrong"),
        ("protocol", "protocol_fingerprint", "wrong"),
        ("source-fp", "source_manifest_fingerprint", "wrong"),
        ("files", "files", []),
    ]:
        root = _copytree(base, tmp_path / name)
        path = root / "artifact_manifest.json"
        artifact = ps._read_json(path)
        artifact[field] = value
        if field != "artifact_manifest_fingerprint":
            core = dict(artifact)
            core.pop("artifact_manifest_fingerprint", None)
            artifact["artifact_manifest_fingerprint"] = provenance.fingerprint(core)
        ps._write_json(path, artifact)
        assert not ps.verify_pedrotti_source_intake_artifacts(root)

    root = _copytree(base, tmp_path / "checksum-set")
    checksum = root / "SHA256SUMS"
    lines = checksum.read_text(encoding="utf-8").splitlines()
    checksum.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    assert not ps.verify_pedrotti_source_intake_artifacts(root)


def test_pedrotti_destination_overwrite_unlinks_file(
    tmp_path: Path,
) -> None:
    root = tmp_path / "replace"
    root.mkdir()
    old = root / "old.txt"
    old.write_text("old", encoding="utf-8")
    assert ps._prepare_flat_destination(
        root,
        overwrite=True,
    ) == root
    assert not old.exists()
