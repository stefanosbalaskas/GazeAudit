from __future__ import annotations

import copy
import json
import os
import runpy
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import gazeaudit.korthals_source as ks
import gazeaudit.pedrotti_source as ps
from gazeaudit.provenance import canonical_json, fingerprint


ROOT = Path(__file__).resolve().parents[1]
KS_TEST = runpy.run_path(str(ROOT / "tests" / "test_korthals_source.py"))
PS_LOCK = runpy.run_path(str(ROOT / "tests" / "test_pedrotti_source_lock.py"))

_make_source_tree = KS_TEST["_make_source_tree"]
_preprocessed_tables = KS_TEST["_preprocessed_tables"]
_FakeParticipant = KS_TEST["_FakeParticipant"]
_FakePreprocessor = KS_TEST["_FakePreprocessor"]
_configure_fakes = KS_TEST["_configure_fakes"]
_synthetic_locked_manifest = PS_LOCK["_synthetic_locked_manifest"]
_synthetic_locked_summary = PS_LOCK["_synthetic_locked_summary"]


def _rehash_korthals(document: dict[str, object]) -> dict[str, object]:
    output = copy.deepcopy(document)
    core = dict(output)
    core.pop("source_manifest_fingerprint", None)
    output["source_manifest_fingerprint"] = fingerprint(core)
    return output


def test_korthals_discovery_and_manifest_source_guards(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    missing.mkdir()
    with pytest.raises(FileNotFoundError, match="data/clean"):
        ks.discover_korthals_participants(missing)

    empty = tmp_path / "empty"
    (empty / "clean").mkdir(parents=True)
    with pytest.raises(ValueError, match="no participant IDs"):
        ks.discover_korthals_participants(empty)

    partial = tmp_path / "partial"
    (partial / "clean").mkdir(parents=True)
    with pytest.raises(FileNotFoundError, match="both data/raw and data/clean"):
        ks.build_korthals_source_manifest(partial)


def test_korthals_manifest_verifier_all_structural_guards(
    tmp_path: Path,
) -> None:
    manifest = ks.build_korthals_source_manifest(
        _make_source_tree(tmp_path)
    )
    assert ks.verify_korthals_source_manifest(manifest)

    for field, value in [
        ("schema", "wrong"),
        ("case_study_id", "wrong"),
        ("protocol_fingerprint", "wrong"),
        ("companion_commit", "wrong"),
        ("osf_project", "wrong"),
        ("osf_doi", "wrong"),
    ]:
        bad = copy.deepcopy(manifest)
        bad[field] = value
        assert not ks.verify_korthals_source_manifest(bad)

    bad = copy.deepcopy(manifest)
    bad["source_manifest_fingerprint"] = "0" * 64
    assert not ks.verify_korthals_source_manifest(bad)

    for mutate in [
        lambda doc: doc.__setitem__("participants", "bad"),
        lambda doc: doc.__setitem__("participants", ["p2", "p1"]),
        lambda doc: doc.__setitem__("participant_count", 99),
        lambda doc: doc.__setitem__("files", []),
        lambda doc: doc.__setitem__("file_count", 99),
    ]:
        bad = copy.deepcopy(manifest)
        mutate(bad)
        bad = _rehash_korthals(bad)
        assert not ks.verify_korthals_source_manifest(bad)

    mutations = [
        lambda record: record.clear(),
        lambda record: record.__setitem__("path", "../bad"),
        lambda record: record.__setitem__("path", "/absolute"),
        lambda record: record.__setitem__("path", "other/file"),
        lambda record: record.__setitem__("sha256", "short"),
        lambda record: record.__setitem__("size_bytes", -1),
    ]
    for mutate in mutations:
        bad = copy.deepcopy(manifest)
        mutate(bad["files"][0])
        bad = _rehash_korthals(bad)
        assert not ks.verify_korthals_source_manifest(bad)

    bad = copy.deepcopy(manifest)
    bad["files"].append(copy.deepcopy(bad["files"][0]))
    bad["file_count"] = len(bad["files"])
    bad = _rehash_korthals(bad)
    assert not ks.verify_korthals_source_manifest(bad)

    assert not ks.verify_korthals_source_manifest(
        {"schema": object()}  # type: ignore[arg-type]
    )


def test_korthals_companion_public_guard_matrix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wrong = tmp_path / "wrong"
    wrong.mkdir()
    with pytest.raises(ValueError, match="named exactly 'data'"):
        ks.prepare_korthals_from_companion(
            wrong,
            participant_factory=_FakeParticipant,
            preprocessor_factory=_FakePreprocessor,
        )

    root = _make_source_tree(tmp_path / "source")
    _configure_fakes()
    monkeypatch.setattr(
        ks,
        "verify_korthals_source_manifest",
        lambda _doc: False,
    )
    with pytest.raises(RuntimeError, match="failed verification"):
        ks.prepare_korthals_from_companion(
            root,
            participant_factory=_FakeParticipant,
            preprocessor_factory=_FakePreprocessor,
        )

    monkeypatch.undo()
    _configure_fakes()

    class NoValidation(_FakeParticipant):
        def validation_check(self, raw_data_path: str) -> pd.DataFrame:
            del raw_data_path
            return pd.DataFrame()

    with pytest.raises(ValueError, match="no validation summaries"):
        ks.prepare_korthals_from_companion(
            root,
            participant_factory=NoValidation,
            preprocessor_factory=_FakePreprocessor,
        )

    class UnknownSplit(_FakeParticipant):
        def __init__(self, id: str, preprocessor: object) -> None:
            super().__init__(id, preprocessor)
            self.subset = "unknown"

    with pytest.raises(ValueError, match="unresolved train/test split"):
        ks.prepare_korthals_from_companion(
            root,
            participant_factory=UnknownSplit,
            preprocessor_factory=_FakePreprocessor,
        )


def test_korthals_companion_default_import_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "data"
    root.mkdir()

    monkeypatch.setattr(
        ks,
        "build_korthals_source_manifest",
        lambda _root: {
            "participants": [],
            "source_manifest_fingerprint": "s" * 64,
            "file_count": 0,
            "download_contract": {},
        },
    )
    monkeypatch.setattr(
        ks,
        "verify_korthals_source_manifest",
        lambda _doc: True,
    )
    monkeypatch.setattr(
        ks,
        "_working_directory",
        lambda _path: __import__("contextlib").nullcontext(),
    )
    modules = {
        "eyemovement_data.participant": SimpleNamespace(
            Participant=_FakeParticipant
        ),
        "eyemovement_data.preprocessor": SimpleNamespace(
            OriginalPreprocessor=_FakePreprocessor
        ),
    }
    monkeypatch.setattr(
        ks.importlib,
        "import_module",
        lambda name: modules[name],
    )
    with pytest.raises(ValueError):
        ks.prepare_korthals_from_companion(root)


def test_korthals_intake_writer_and_verifier_guards(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_source_tree(tmp_path / "source")
    _configure_fakes()
    intake = ks.prepare_korthals_from_companion(
        root,
        participant_factory=_FakeParticipant,
        preprocessor_factory=_FakePreprocessor,
    )

    with pytest.raises(TypeError, match="KorthalsSourceIntake"):
        ks.write_korthals_source_intake_artifacts(
            object(),  # type: ignore[arg-type]
            tmp_path / "bad-type",
        )

    bad_manifest = copy.deepcopy(intake.source_manifest)
    bad_manifest["schema"] = "wrong"
    with pytest.raises(ValueError, match="source manifest is invalid"):
        ks.write_korthals_source_intake_artifacts(
            ks.KorthalsSourceIntake(
                prepared=intake.prepared,
                source_manifest=bad_manifest,
                participant_splits=intake.participant_splits,
            ),
            tmp_path / "bad-manifest",
        )

    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory path"):
        ks.write_korthals_source_intake_artifacts(
            intake,
            file_path,
        )

    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "x").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="not empty"):
        ks.write_korthals_source_intake_artifacts(
            intake,
            nonempty,
        )

    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "sub").mkdir()
    with pytest.raises(ValueError, match="nested directories"):
        ks.write_korthals_source_intake_artifacts(
            intake,
            nested,
            overwrite=True,
        )

    monkeypatch.setattr(
        ks,
        "verify_korthals_source_intake_artifacts",
        lambda _root: False,
    )
    with pytest.raises(RuntimeError, match="failed verification"):
        ks.write_korthals_source_intake_artifacts(
            intake,
            tmp_path / "self-check",
        )


def test_korthals_alignment_guards() -> None:
    tables = _preprocessed_tables("p1")

    with pytest.raises(ValueError, match="preprocessed data is missing"):
        ks._align_companion_preprocessed_participant(
            "p1",
            {"gaze": tables["gaze"]},
        )

    bad = {name: frame.copy() for name, frame in tables.items()}
    bad["gaze"] = pd.concat(
        [bad["gaze"], bad["gaze"].iloc[[0]]],
        ignore_index=True,
    )
    with pytest.raises(ValueError, match="gaze alignment keys are duplicated"):
        ks._align_companion_preprocessed_participant("p1", bad)

    bad = {name: frame.copy() for name, frame in tables.items()}
    bad["targets"] = pd.concat(
        [bad["targets"], bad["targets"].iloc[[0]]],
        ignore_index=True,
    )
    with pytest.raises(ValueError, match="target alignment keys are duplicated"):
        ks._align_companion_preprocessed_participant("p1", bad)

    bad = {name: frame.copy() for name, frame in tables.items()}
    duplicate = bad["trials"].iloc[[0]].copy()
    duplicate["target_speed"] = 99.0
    bad["trials"] = pd.concat(
        [bad["trials"], duplicate],
        ignore_index=True,
    )
    with pytest.raises(ValueError, match="trial metadata is not one-to-one"):
        ks._align_companion_preprocessed_participant("p1", bad)

    bad = {name: frame.copy() for name, frame in tables.items()}
    bad["trials"] = bad["trials"].iloc[1:].copy()
    with pytest.raises(ValueError, match="target rows without trial metadata"):
        ks._align_companion_preprocessed_participant("p1", bad)


def _tutorial_frame(**overrides: object) -> pd.DataFrame:
    row = {
        "participant_id": "p1",
        "trial_number": 0,
        "trial_name": "Tutorial",
        "target_type": "moving_circle",
        "target_speed": 2.0,
        "target_trajectory": "east",
    }
    row.update(overrides)
    task = dict(row)
    task["trial_number"] = 1
    task["trial_name"] = "Task"
    return pd.DataFrame([row, task])


def test_korthals_authoritative_scope_guard_matrix() -> None:
    with pytest.raises(ValueError, match="non-empty DataFrame"):
        ks._scope_authoritative_task_trials(pd.DataFrame())

    frame = _tutorial_frame()
    frame.loc[0, "trial_number"] = 1.5
    with pytest.raises(ValueError, match="finite and integer-valued"):
        ks._scope_authoritative_task_trials(frame)

    frame = _tutorial_frame()
    frame.loc[0, "trial_number"] = 145
    with pytest.raises(ValueError, match="out-of-range trials"):
        ks._scope_authoritative_task_trials(frame)

    for key, value, message in [
        ("trial_name", "Wrong", "tutorial name"),
        ("target_type", "jumping_circle", "tutorial target type"),
        ("target_speed", 3.0, "tutorial target speed"),
        ("target_trajectory", "north", "tutorial trajectory"),
    ]:
        with pytest.raises(ValueError, match=message):
            ks._scope_authoritative_task_trials(
                _tutorial_frame(**{key: value})
            )

    scoped = ks._scope_authoritative_task_trials(
        _tutorial_frame()
    )
    assert scoped["trial_number"].tolist() == [1]


def test_korthals_clean_identity_and_helper_guards(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="clean data is missing"):
        ks._require_clean_tables(
            "p1",
            {"gaze": pd.DataFrame({"x": [1]})},
        )

    complete = {
        name: pd.DataFrame({"x": [1]})
        for name in ("gaze", "targets", "trials", "blinks")
    }
    complete["gaze"] = pd.DataFrame()
    with pytest.raises(ValueError, match="clean table"):
        ks._require_clean_tables("p1", complete)

    assert ks._participant_identity_value_matches("p1", "p1")
    assert not ks._participant_identity_value_matches("p1", "1")
    assert ks._participant_identity_value_matches("68471e16", "6.8471e20")
    assert not ks._participant_identity_value_matches("68471e16", "not-a-number")

    frame = pd.DataFrame({"x": [1]})
    result = ks._participant_frame(frame, "p1", "demo")
    assert result["participant_id"].tolist() == ["p1"]

    with pytest.raises(ValueError, match="must be non-empty"):
        ks._participant_frame(pd.DataFrame(), "p1", "demo")

    with pytest.raises(ValueError, match="different participant"):
        ks._participant_frame(
            pd.DataFrame({"participant_id": ["p2"]}),
            "p1",
            "demo",
        )

    with pytest.raises(FileNotFoundError, match="does not exist"):
        ks._validated_data_root(tmp_path / "missing")

    with pytest.raises(ValueError, match="missing required columns"):
        ks._require_columns(
            pd.DataFrame({"a": [1]}),
            ["a", "b"],
            "demo",
        )

    before = Path.cwd()
    target = tmp_path / "cwd"
    target.mkdir()
    with ks._working_directory(target):
        assert Path.cwd() == target.resolve()
    assert Path.cwd() == before


def test_korthals_canonical_identity_source_guards(tmp_path: Path) -> None:
    clean_root = tmp_path / "clean"
    with pytest.raises(ValueError, match="no matching published clean CSV"):
        ks._canonicalize_companion_participant_identity(
            clean_root,
            "p1",
            {},
        )

    for split in ("train", "test"):
        folder = clean_root / split / "p1"
        folder.mkdir(parents=True)
        (folder / "p1_gaze.csv").write_text(
            "participant_id\np1\n",
            encoding="utf-8",
        )
    with pytest.raises(ValueError, match="multiple clean-data splits"):
        ks._canonicalize_companion_participant_identity(
            clean_root,
            "p1",
            {},
        )


def test_korthals_checksum_parser_guards(tmp_path: Path) -> None:
    path = tmp_path / "SHA256SUMS"
    path.write_text("\n" + "a" * 64 + "  file.txt\n", encoding="utf-8")
    assert ks._parse_checksums(path) == {"file.txt": "a" * 64}

    path.write_text("bad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid SHA256SUMS entry"):
        ks._parse_checksums(path)

    path.write_text("a" * 64 + "  ../file.txt\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid or duplicate"):
        ks._parse_checksums(path)

    path.write_text(
        "a" * 64 + "  file.txt\n" + "b" * 64 + "  file.txt\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid or duplicate"):
        ks._parse_checksums(path)


# ---------------------------------------------------------------------------
# Pedrotti source closure
# ---------------------------------------------------------------------------


class _ProtocolResource:
    def __init__(self, payload: str) -> None:
        self.payload = payload

    def read_text(self, *, encoding: str) -> str:
        assert encoding == "utf-8"
        return self.payload


def test_pedrotti_protocol_and_md5_contract_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_path = ps.Path

    class FakePath:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def resolve(self):
            return self

        @property
        def parent(self):
            return self

        def __truediv__(self, _other: object):
            return self

        def read_text(self, *, encoding: str) -> str:
            assert encoding == "utf-8"
            return "[]"

    monkeypatch.setattr(ps, "Path", FakePath)
    with pytest.raises(ValueError, match="JSON object"):
        ps.load_pedrotti_protocol()

    monkeypatch.setattr(ps, "Path", original_path)
    protocol = ps.load_pedrotti_protocol()
    bad = copy.deepcopy(protocol)
    bad["protocol_fingerprint"] = "wrong"

    class BadFingerprintPath(FakePath):
        def read_text(self, *, encoding: str) -> str:
            assert encoding == "utf-8"
            return json.dumps(bad)

    monkeypatch.setattr(ps, "Path", BadFingerprintPath)
    with pytest.raises(ValueError, match="fingerprint"):
        ps.load_pedrotti_protocol()


def test_pedrotti_expected_md5_contract_guard_matrix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol = ps.load_pedrotti_protocol()

    bad = copy.deepcopy(protocol)
    bad["dataset"]["source_files"]["expected_md5"] = []
    monkeypatch.setattr(ps, "load_pedrotti_protocol", lambda: bad)
    with pytest.raises(ValueError, match="must be an object"):
        ps.expected_pedrotti_md5()

    bad = copy.deepcopy(protocol)
    bad["dataset"]["source_files"]["expected_md5"] = {"01.txt": "a" * 32}
    monkeypatch.setattr(ps, "load_pedrotti_protocol", lambda: bad)
    with pytest.raises(ValueError, match="unexpected file set"):
        ps.expected_pedrotti_md5()

    bad = copy.deepcopy(protocol)
    values = bad["dataset"]["source_files"]["expected_md5"]
    first = next(iter(values))
    values[first] = "X" * 32
    monkeypatch.setattr(ps, "load_pedrotti_protocol", lambda: bad)
    with pytest.raises(ValueError, match="invalid digest"):
        ps.expected_pedrotti_md5()


def test_pedrotti_manifest_builder_guard_matrix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(FileNotFoundError, match="existing directory"):
        ps.build_pedrotti_source_manifest(tmp_path / "missing")

    root = tmp_path / "source"
    root.mkdir()
    monkeypatch.setattr(
        ps,
        "expected_pedrotti_md5",
        lambda: {"a.txt": "0" * 32},
    )
    with pytest.raises(ValueError, match="file set differs"):
        ps.build_pedrotti_source_manifest(root)

    payload = b"x"
    (root / "a.txt").write_bytes(payload)
    (root / "nested").mkdir()
    digest = __import__("hashlib").md5(
        payload,
        usedforsecurity=False,
    ).hexdigest()
    monkeypatch.setattr(
        ps,
        "expected_pedrotti_md5",
        lambda: {"a.txt": digest},
    )
    with pytest.raises(ValueError, match="nested directories"):
        ps.build_pedrotti_source_manifest(root)

    (root / "nested").rmdir()
    monkeypatch.setattr(
        ps,
        "expected_pedrotti_md5",
        lambda: {"a.txt": "f" * 32},
    )
    with pytest.raises(ValueError, match="MD5 mismatch"):
        ps.build_pedrotti_source_manifest(root)


def _pedrotti_manifest_fixture() -> tuple[dict[str, object], dict[str, str]]:
    expected = {
        f"{participant:02d}.txt": "a" * 32
        for participant in range(1, 37)
    }
    expected["readme.txt"] = "b" * 32
    files = [
        {
            "path": name,
            "size_bytes": 1,
            "md5": digest,
            "sha256": "c" * 64,
        }
        for name, digest in sorted(expected.items())
    ]
    core = {
        "schema": ps.PEDROTTI_SOURCE_SCHEMA,
        "case_study_id": ps.PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": ps.PEDROTTI_PROTOCOL_FINGERPRINT,
        "zenodo_doi": ps.PEDROTTI_ZENODO_DOI,
        "zenodo_record": ps.PEDROTTI_ZENODO_RECORD,
        "zenodo_version": ps.PEDROTTI_ZENODO_VERSION,
        "download_contract": ps._expected_download_contract(),
        "files": files,
        "file_count": len(files),
    }
    document = dict(core)
    document["source_manifest_fingerprint"] = fingerprint(core)
    return document, expected


def _rehash_pedrotti(document: dict[str, object]) -> dict[str, object]:
    output = copy.deepcopy(document)
    core = dict(output)
    core.pop("source_manifest_fingerprint", None)
    output["source_manifest_fingerprint"] = fingerprint(core)
    return output


def test_pedrotti_manifest_verifier_guard_matrix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest, expected = _pedrotti_manifest_fixture()
    monkeypatch.setattr(
        ps,
        "expected_pedrotti_md5",
        lambda: dict(expected),
    )
    assert ps.verify_pedrotti_source_manifest(manifest)

    assert not ps.verify_pedrotti_source_manifest(
        []  # type: ignore[arg-type]
    )

    bad = copy.deepcopy(manifest)
    bad["extra"] = True
    assert not ps.verify_pedrotti_source_manifest(bad)

    for field, value in [
        ("schema", "wrong"),
        ("case_study_id", "wrong"),
        ("protocol_fingerprint", "wrong"),
        ("zenodo_doi", "wrong"),
        ("zenodo_record", -1),
        ("zenodo_version", "wrong"),
        ("download_contract", {}),
    ]:
        bad = copy.deepcopy(manifest)
        bad[field] = value
        assert not ps.verify_pedrotti_source_manifest(bad)

    bad = copy.deepcopy(manifest)
    bad["source_manifest_fingerprint"] = "0" * 64
    assert not ps.verify_pedrotti_source_manifest(bad)

    for mutate in [
        lambda doc: doc.__setitem__("files", []),
        lambda doc: doc.__setitem__("file_count", 1),
    ]:
        bad = copy.deepcopy(manifest)
        mutate(bad)
        bad = _rehash_pedrotti(bad)
        assert not ps.verify_pedrotti_source_manifest(bad)

    bad_records = [
        "bad",
        {"path": "01.txt"},
        {
            "path": "unknown.txt",
            "size_bytes": 1,
            "md5": "a" * 32,
            "sha256": "c" * 64,
        },
        {
            "path": "01.txt",
            "size_bytes": True,
            "md5": "a" * 32,
            "sha256": "c" * 64,
        },
        {
            "path": "01.txt",
            "size_bytes": 1,
            "md5": "f" * 32,
            "sha256": "c" * 64,
        },
        {
            "path": "01.txt",
            "size_bytes": 1,
            "md5": "a" * 32,
            "sha256": "bad",
        },
    ]
    for record in bad_records:
        bad = copy.deepcopy(manifest)
        bad["files"][0] = record
        bad = _rehash_pedrotti(bad)
        assert not ps.verify_pedrotti_source_manifest(bad)


def _valid_summary_and_source() -> tuple[dict[str, object], dict[str, object]]:
    summary = copy.deepcopy(_synthetic_locked_summary())
    source = copy.deepcopy(_synthetic_locked_manifest())
    source["file_count"] = 37
    source["source_manifest_fingerprint"] = summary[
        "source_manifest_fingerprint"
    ]
    participants = []
    for participant in range(1, 37):
        participants.append(
            {
                "participant_id": f"{participant:02d}",
                "row_count": 100,
                "trial_count": 96,
                "eye": "left" if participant <= 20 else "right",
                "short_numeric_trial_count": 1,
                "long_numeric_trial_count": 1,
                "numeric_trial_count": 2,
            }
        )
    summary["participants"] = participants
    summary["total_row_count"] = 3600
    summary["total_trial_count"] = 36 * 96
    summary["short_numeric_trial_count"] = 36
    summary["long_numeric_trial_count"] = 36
    summary["eye_counts"] = {"left": 20, "right": 16}
    return summary, source


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda s: s.pop("eye_counts"), "exact required field set"),
        (lambda s: s.__setitem__("schema", "wrong"), "summary schema"),
        (lambda s: s.__setitem__("case_study_id", "wrong"), "case-study identity"),
        (lambda s: s.__setitem__("protocol_fingerprint", "wrong"), "protocol fingerprint"),
        (lambda s: s.__setitem__("source_manifest_fingerprint", "wrong"), "fingerprint mismatch"),
        (lambda s: s.__setitem__("scientific_endpoint_evaluated", True), "endpoint-blind"),
        (lambda s: s.__setitem__("participant_count", 35), "36 participants"),
        (lambda s: s.__setitem__("source_file_count", 36), "37 frozen source files"),
        (lambda s: s.__setitem__("total_row_count", 0), "positive integer"),
        (lambda s: s.__setitem__("total_trial_count", 1), "96 trials per participant"),
        (lambda s: s.__setitem__("participants", []), "36 records"),
    ],
)
def test_pedrotti_summary_top_level_guards(mutator, message: str) -> None:
    summary, source = _valid_summary_and_source()
    mutator(summary)
    with pytest.raises(ValueError, match=message):
        ps._validate_intake_summary(summary, source)


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda r: r.__setitem__("extra", 1), "unexpected field set"),
        (lambda r: r.__setitem__("participant_id", 1), "participant_id must be a string"),
        (lambda r: r.__setitem__("row_count", 0), "row_count must be positive"),
        (lambda r: r.__setitem__("trial_count", 95), "exactly 96 trials"),
        (lambda r: r.__setitem__("eye", "both"), "eye must be left or right"),
        (lambda r: r.__setitem__("short_numeric_trial_count", 0), "both numeric length"),
        (lambda r: r.__setitem__("numeric_trial_count", 99), "do not reconcile"),
    ],
)
def test_pedrotti_summary_participant_guards(mutator, message: str) -> None:
    summary, source = _valid_summary_and_source()
    mutator(summary["participants"][0])
    with pytest.raises(ValueError, match=message):
        ps._validate_intake_summary(summary, source)


def test_pedrotti_summary_reconciliation_guards() -> None:
    for field, value, message in [
        ("participant_id", "99", "identities/order"),
        ("row_count", 101, "row totals"),
        ("short_numeric_trial_count", 2, "short-numeric totals"),
        ("long_numeric_trial_count", 2, "long-numeric totals"),
        ("eye", "right", "eye counts"),
    ]:
        summary, source = _valid_summary_and_source()
        summary["participants"][0][field] = value
        if field == "short_numeric_trial_count":
            summary["participants"][0]["numeric_trial_count"] = 3
        if field == "long_numeric_trial_count":
            summary["participants"][0]["numeric_trial_count"] = 3
        with pytest.raises(ValueError, match=message):
            ps._validate_intake_summary(summary, source)


def _participant_frame_fixture() -> pd.DataFrame:
    rows = []
    for trial in range(1, 97):
        stimulus = (
            "1,234"
            if trial == 1
            else "12,345,678"
            if trial == 2
            else f"word-{trial}"
        )
        rows.append(
            {
                "TRIAL_INDEX": trial,
                "LEFT_GAZE_X": float(trial),
                "LEFT_GAZE_Y": float(trial + 1),
                "LEFT_PUPIL_SIZE": 1.0,
                "RIGHT_GAZE_X": np.nan,
                "RIGHT_GAZE_Y": np.nan,
                "RIGHT_PUPIL_SIZE": np.nan,
                "TIMESTAMP": float(trial),
                "TrialTextShown": stimulus,
            }
        )
    return pd.DataFrame(rows)


def _write_participant(path: Path, frame: pd.DataFrame) -> list[str]:
    frame.to_csv(path, index=False)
    return frame.columns.tolist()


def test_pedrotti_participant_file_guard_matrix(tmp_path: Path) -> None:
    base = _participant_frame_fixture()
    path = tmp_path / "01.txt"
    required = _write_participant(path, base)
    result = ps._inspect_participant_file(path, "01", required)
    assert result["eye"] == "left"

    bad = base.drop(columns="LEFT_PUPIL_SIZE")
    _write_participant(path, bad)
    with pytest.raises(ValueError, match="columns differ"):
        ps._inspect_participant_file(path, "01", required)

    pd.DataFrame(columns=required).to_csv(path, index=False)
    with pytest.raises(ValueError, match="no source rows"):
        ps._inspect_participant_file(path, "01", required)

    for field, value, message in [
        ("TRIAL_INDEX", "bad", "invalid TRIAL_INDEX"),
        ("TIMESTAMP", np.inf, "invalid TIMESTAMP"),
    ]:
        bad = base.copy()
        bad.loc[0, field] = value
        _write_participant(path, bad)
        with pytest.raises(ValueError, match=message):
            ps._inspect_participant_file(path, "01", required)

    bad = base.iloc[:-1].copy()
    _write_participant(path, bad)
    with pytest.raises(ValueError, match="trials 1..96"):
        ps._inspect_participant_file(path, "01", required)

    bad = pd.concat([base, base.iloc[[0]]], ignore_index=True)
    bad.loc[len(bad) - 1, "TIMESTAMP"] = base.loc[0, "TIMESTAMP"]
    _write_participant(path, bad)
    with pytest.raises(ValueError, match="strictly increasing"):
        ps._inspect_participant_file(path, "01", required)

    bad = base.copy()
    bad.loc[0, "TrialTextShown"] = pd.NA
    _write_participant(path, bad)
    with pytest.raises(ValueError, match="missing TrialTextShown"):
        ps._inspect_participant_file(path, "01", required)

    bad = pd.concat([base, base.iloc[[0]]], ignore_index=True)
    bad.loc[len(bad) - 1, "TIMESTAMP"] = base.loc[0, "TIMESTAMP"] + 0.5
    bad.loc[len(bad) - 1, "TrialTextShown"] = "other"
    _write_participant(path, bad)
    with pytest.raises(ValueError, match="unstable TrialTextShown"):
        ps._inspect_participant_file(path, "01", required)

    both = base.copy()
    both["RIGHT_GAZE_X"] = both["LEFT_GAZE_X"]
    both["RIGHT_GAZE_Y"] = both["LEFT_GAZE_Y"]
    _write_participant(path, both)
    with pytest.raises(ValueError, match="exactly one finite eye side"):
        ps._inspect_participant_file(path, "01", required)

    no_numeric = base.copy()
    no_numeric["TrialTextShown"] = [
        f"word-{trial}"
        for trial in range(1, 97)
    ]
    _write_participant(path, no_numeric)
    with pytest.raises(ValueError, match="lacks a frozen numeric length condition"):
        ps._inspect_participant_file(path, "01", required)


def test_pedrotti_helper_and_destination_guards(tmp_path: Path) -> None:
    assert ps._numeric_condition("1,234") == "short"
    assert ps._numeric_condition("12,345,678") == "long"
    assert ps._numeric_condition("abc") is None
    assert ps._numeric_condition("123") is None

    frame = pd.DataFrame(
        {
            "x": [1.0, np.nan],
            "y": [2.0, 3.0],
        }
    )
    assert ps._finite_xy(frame, "x", "y").tolist() == [True, False]
    assert ps._positive_int(1)
    assert not ps._positive_int(True)
    assert not ps._positive_int(0)

    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory path"):
        ps._prepare_flat_destination(file_path, overwrite=False)

    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "x").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="not empty"):
        ps._prepare_flat_destination(nonempty, overwrite=False)

    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "sub").mkdir()
    with pytest.raises(ValueError, match="nested directories"):
        ps._prepare_flat_destination(nested, overwrite=True)

    obj = tmp_path / "object.json"
    obj.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        ps._read_json(obj)

    assert ps._hex_digest("a" * 64, 64)
    assert not ps._hex_digest("A" * 64, 64)
    assert not ps._hex_digest(1, 64)

    checksums = tmp_path / "SHA256SUMS"
    checksums.write_text("\n" + "a" * 64 + "  file.txt\n", encoding="utf-8")
    assert ps._parse_checksums(checksums) == {"file.txt": "a" * 64}

    checksums.write_text("bad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid SHA256SUMS entry"):
        ps._parse_checksums(checksums)

    checksums.write_text("a" * 64 + "  ../bad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid or duplicate"):
        ps._parse_checksums(checksums)


def test_pedrotti_intake_writer_public_guards(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(TypeError, match="PedrottiSourceIntake"):
        ps.write_pedrotti_source_intake_artifacts(
            object(),  # type: ignore[arg-type]
            tmp_path / "bad",
        )

    manifest, expected = _pedrotti_manifest_fixture()
    summary, _source = _valid_summary_and_source()
    summary["source_manifest_fingerprint"] = manifest[
        "source_manifest_fingerprint"
    ]
    intake = ps.PedrottiSourceIntake(
        source_manifest=manifest,
        intake_summary=summary,
    )
    monkeypatch.setattr(
        ps,
        "expected_pedrotti_md5",
        lambda: dict(expected),
    )

    bad = copy.deepcopy(manifest)
    bad["schema"] = "wrong"
    with pytest.raises(ValueError, match="source manifest is invalid"):
        ps.write_pedrotti_source_intake_artifacts(
            ps.PedrottiSourceIntake(
                source_manifest=bad,
                intake_summary=summary,
            ),
            tmp_path / "bad-manifest",
        )

    monkeypatch.setattr(
        ps,
        "verify_pedrotti_source_intake_artifacts",
        lambda _root: False,
    )
    with pytest.raises(RuntimeError, match="failed verification"):
        ps.write_pedrotti_source_intake_artifacts(
            intake,
            tmp_path / "self-check",
        )
