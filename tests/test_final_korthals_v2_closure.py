from __future__ import annotations

import copy
import json
import runpy
from contextlib import nullcontext
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import gazeaudit.korthals_execution_v2 as ev2
import gazeaudit.korthals_v2 as kv2
from gazeaudit.korthals_source_lock import (
    KORTHALS_SOURCE_LOCK_FINGERPRINT,
    load_korthals_source_lock,
)
from gazeaudit.provenance import canonical_json, fingerprint


ROOT = Path(__file__).resolve().parents[1]
V2 = runpy.run_path(str(ROOT / "tests" / "test_korthals_v2.py"))
EV2 = runpy.run_path(str(ROOT / "tests" / "test_korthals_execution_v2.py"))
KS = runpy.run_path(str(ROOT / "tests" / "test_korthals_source.py"))

_aligned_fixture = V2["_aligned_fixture"]
_validation_fixture = V2["_validation_fixture"]
_source_tree = V2["_source_tree"]
_source_identity = V2["_source_identity"]
_synthetic_prepared = EV2["_synthetic_prepared"]
_execution_context = EV2["_execution_context"]
_environment_text = EV2["_environment_text"]
_FakeParticipant = KS["_FakeParticipant"]
_FakePreprocessor = KS["_FakePreprocessor"]
_configure_fakes = KS["_configure_fakes"]


class _JsonResource:
    def __init__(self, text: str) -> None:
        self.text = text

    def joinpath(self, _name: str) -> "_JsonResource":
        return self

    def read_text(self, *, encoding: str) -> str:
        assert encoding == "utf-8"
        return self.text


def _rehash_manifest(document: dict[str, object]) -> dict[str, object]:
    output = copy.deepcopy(document)
    core = dict(output)
    core.pop("source_manifest_fingerprint", None)
    output["source_manifest_fingerprint"] = fingerprint(core)
    return output


def test_v2_protocol_loader_requires_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        kv2.resources,
        "files",
        lambda _package: _JsonResource("[]"),
    )
    with pytest.raises(ValueError, match="JSON object"):
        kv2.load_korthals_protocol_v2()


def test_v2_protocol_verifier_requires_generic_verification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol = kv2.load_korthals_protocol_v2()
    monkeypatch.setattr(
        kv2,
        "verify_aoi_uncertainty_protocol",
        lambda _document: False,
    )
    with pytest.raises(ValueError, match="generic protocol verification"):
        kv2.verify_korthals_protocol_v2(protocol)


def test_v2_manifest_builder_self_verifies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        kv2,
        "_build_korthals_source_manifest_v1",
        lambda _root: {
            "schema": kv2.KORTHALS_SOURCE_SCHEMA,
            "case_study_id": "old",
            "protocol_fingerprint": "old",
            "source_manifest_fingerprint": "old",
        },
    )
    monkeypatch.setattr(
        kv2,
        "verify_korthals_source_manifest_v2",
        lambda _document: False,
    )
    with pytest.raises(RuntimeError, match="failed verification"):
        kv2.build_korthals_source_manifest_v2("ignored")


def test_v2_manifest_verifier_guard_matrix(tmp_path: Path) -> None:
    manifest = kv2.build_korthals_source_manifest_v2(
        _source_tree(tmp_path)
    )
    assert kv2.verify_korthals_source_manifest_v2(manifest)

    for field, value in [
        ("schema", "wrong"),
        ("case_study_id", "wrong"),
        ("protocol_fingerprint", "wrong"),
    ]:
        bad = _rehash_manifest(manifest)
        bad[field] = value
        bad = _rehash_manifest(bad)
        assert not kv2.verify_korthals_source_manifest_v2(bad)

    bad = copy.deepcopy(manifest)
    bad["source_manifest_fingerprint"] = "0" * 64
    assert not kv2.verify_korthals_source_manifest_v2(bad)

    assert not kv2.verify_korthals_source_manifest_v2(
        {"schema": object()}  # type: ignore[arg-type]
    )


def test_v2_prepare_public_and_identity_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validations = _validation_fixture(participants=("p1",))
    aligned = _aligned_fixture(participants=("p1",))

    with pytest.raises(ValueError, match="non-empty pandas DataFrame"):
        kv2.prepare_korthals_aligned_data_v2(
            pd.DataFrame(),
            validations,
        )

    with pytest.raises(TypeError, match="validations"):
        kv2.prepare_korthals_aligned_data_v2(
            aligned,
            object(),  # type: ignore[arg-type]
        )

    monkeypatch.setattr(
        kv2,
        "canonical_json",
        lambda _value: "[]",
    )
    with pytest.raises(TypeError, match="normalize to an object"):
        kv2.prepare_korthals_aligned_data_v2(
            aligned,
            validations,
            source_identity={"x": 1},
        )

    monkeypatch.undo()
    with pytest.raises(ValueError, match="may not override"):
        kv2.prepare_korthals_aligned_data_v2(
            aligned,
            validations,
            source_identity={
                "case_study_id": "bad",
            },
        )


def test_v2_prepare_internal_fail_closed_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validations = _validation_fixture(participants=("p1",))
    aligned = _aligned_fixture(participants=("p1",))

    no_frozen = aligned.copy()
    no_frozen["target_type"] = "other"
    monkeypatch.setattr(
        kv2,
        "_normalize_aligned_data",
        lambda _frame: no_frozen.copy(),
    )
    with pytest.raises(ValueError, match="no frozen moving/jumping"):
        kv2.prepare_korthals_aligned_data_v2(
            aligned,
            validations,
        )

    monkeypatch.undo()
    protocol = kv2.load_korthals_protocol_v2()
    excluded_id = str(
        protocol["dataset"]["author_directed_exclusion"]["participant_id"]
    )
    exclusion = _aligned_fixture(participants=(excluded_id,))
    start = int(
        protocol["dataset"]["author_directed_exclusion"]["trial_number_start"]
    )
    end = int(
        protocol["dataset"]["author_directed_exclusion"]["trial_number_end"]
    )
    exclusion["trial_number"] = start
    assert start <= end
    monkeypatch.setattr(
        kv2,
        "_require_complete_trial_pairing",
        lambda _frame: None,
    )
    with pytest.raises(ValueError, match="remain after filtering"):
        kv2.prepare_korthals_aligned_data_v2(
            exclusion,
            validations,
        )

    monkeypatch.undo()
    bad_target = _aligned_fixture(participants=("p1",))
    monkeypatch.setattr(
        kv2,
        "_downsample_trial_50hz",
        lambda trial: trial.assign(target_x=np.nan),
    )
    with pytest.raises(ValueError, match="target coordinates"):
        kv2.prepare_korthals_aligned_data_v2(
            bad_target,
            validations,
        )


def test_v2_prepare_zero_trial_metadata_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    aligned = _aligned_fixture(participants=("p1",))
    validations = _validation_fixture(participants=("p1",))
    aligned.loc[
        aligned["trial_number"] == 2,
        ["gaze_x", "gaze_y"],
    ] = np.nan

    original_normalize = kv2._normalize_aligned_data

    def duplicate_trial(frame: pd.DataFrame) -> pd.DataFrame:
        normalized = original_normalize(frame)
        duplicate = normalized.loc[
            normalized["trial_number"] == 1
        ].copy()
        duplicate["target_speed"] = 9.0
        return pd.concat(
            [normalized, duplicate],
            ignore_index=True,
        )

    monkeypatch.setattr(
        kv2,
        "_normalize_aligned_data",
        duplicate_trial,
    )
    monkeypatch.setattr(
        kv2,
        "_require_complete_trial_pairing",
        lambda _frame: None,
    )
    with pytest.raises(ValueError, match="one frozen metadata identity"):
        kv2.prepare_korthals_aligned_data_v2(
            aligned,
            validations,
        )

    monkeypatch.undo()

    original_downsample = kv2._downsample_trial_50hz

    def ambiguous_downsample(trial: pd.DataFrame) -> pd.DataFrame:
        output = original_downsample(trial)
        if int(trial["trial_number"].iloc[0]) == 2:
            output[["gaze_x", "gaze_y"]] = np.nan
        return output

    monkeypatch.setattr(
        kv2,
        "_downsample_trial_50hz",
        ambiguous_downsample,
    )
    monkeypatch.setattr(
        kv2,
        "_require_complete_trial_pairing",
        lambda _frame: None,
    )

    original_norm = kv2._normalize_aligned_data

    def duplicate_zero(frame: pd.DataFrame) -> pd.DataFrame:
        normalized = original_norm(frame)
        duplicate = normalized.loc[
            normalized["trial_number"] == 2
        ].copy()
        duplicate["target_speed"] = 99.0
        return pd.concat(
            [normalized, duplicate],
            ignore_index=True,
        )

    monkeypatch.setattr(
        kv2,
        "_normalize_aligned_data",
        duplicate_zero,
    )
    with pytest.raises(
        ValueError,
        match="one frozen metadata identity|ambiguous metadata",
    ):
        kv2.prepare_korthals_aligned_data_v2(
            aligned,
            validations,
        )


def test_v2_companion_positive_and_fail_closed_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _source_tree(tmp_path)
    _configure_fakes()

    intake = kv2.prepare_korthals_from_companion_v2(
        root,
        participant_factory=_FakeParticipant,
        preprocessor_factory=_FakePreprocessor,
    )
    assert intake.prepared.source_identity["participant_count"] == 1
    assert intake.participant_splits == (("p1", "train"),)

    wrong_root = tmp_path / "wrong"
    wrong_root.mkdir()
    monkeypatch.setattr(
        kv2,
        "_validated_data_root",
        lambda _root: wrong_root,
    )
    with pytest.raises(ValueError, match="named exactly 'data'"):
        kv2.prepare_korthals_from_companion_v2(
            wrong_root,
            participant_factory=_FakeParticipant,
            preprocessor_factory=_FakePreprocessor,
        )

    monkeypatch.undo()
    root = _source_tree(tmp_path / "invalid-validation")
    _configure_fakes()

    class NoValidation(_FakeParticipant):
        def validation_check(self, raw_data_path: str) -> pd.DataFrame:
            del raw_data_path
            return pd.DataFrame()

    with pytest.raises(ValueError, match="no validation summaries"):
        kv2.prepare_korthals_from_companion_v2(
            root,
            participant_factory=NoValidation,
            preprocessor_factory=_FakePreprocessor,
        )

    class UnknownSplit(_FakeParticipant):
        def __init__(self, id: str, preprocessor: object) -> None:
            super().__init__(id, preprocessor)
            self.subset = "unknown"

    with pytest.raises(ValueError, match="unresolved train/test split"):
        kv2.prepare_korthals_from_companion_v2(
            root,
            participant_factory=UnknownSplit,
            preprocessor_factory=_FakePreprocessor,
        )


def test_v2_companion_default_import_and_count_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "data"
    root.mkdir()

    monkeypatch.setattr(
        kv2,
        "build_korthals_source_manifest_v2",
        lambda _root: {
            "participants": [],
            "source_manifest_fingerprint": "s" * 64,
            "file_count": 0,
            "download_contract": {},
        },
    )
    monkeypatch.setattr(
        kv2,
        "_working_directory",
        lambda _path: nullcontext(),
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
        kv2.importlib,
        "import_module",
        lambda name: modules[name],
    )

    with pytest.raises(ValueError):
        kv2.prepare_korthals_from_companion_v2(root)


def _valid_intake(tmp_path: Path) -> kv2.KorthalsSourceIntakeV2:
    root = _source_tree(tmp_path)
    manifest = kv2.build_korthals_source_manifest_v2(root)
    prepared = kv2.prepare_korthals_aligned_data_v2(
        _aligned_fixture(participants=("p1",)),
        _validation_fixture(participants=("p1",)),
        source_identity=_source_identity(manifest),
    )
    return kv2.KorthalsSourceIntakeV2(
        prepared=prepared,
        source_manifest=manifest,
        participant_splits=(("p1", "train"),),
    )


def test_v2_intake_writer_guard_matrix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    intake = _valid_intake(tmp_path / "source")

    with pytest.raises(TypeError, match="KorthalsSourceIntakeV2"):
        kv2.write_korthals_source_intake_artifacts_v2(
            object(),  # type: ignore[arg-type]
            tmp_path / "wrong-type",
        )

    bad = copy.deepcopy(intake.source_manifest)
    bad["schema"] = "wrong"
    with pytest.raises(ValueError, match="source manifest is invalid"):
        kv2.write_korthals_source_intake_artifacts_v2(
            kv2.KorthalsSourceIntakeV2(
                prepared=intake.prepared,
                source_manifest=bad,
                participant_splits=intake.participant_splits,
            ),
            tmp_path / "bad-manifest",
        )

    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory path"):
        kv2.write_korthals_source_intake_artifacts_v2(
            intake,
            file_path,
        )

    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "x").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="not empty"):
        kv2.write_korthals_source_intake_artifacts_v2(
            intake,
            nonempty,
        )

    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "sub").mkdir()
    with pytest.raises(ValueError, match="nested directories"):
        kv2.write_korthals_source_intake_artifacts_v2(
            intake,
            nested,
            overwrite=True,
        )

    monkeypatch.setattr(
        kv2,
        "verify_korthals_source_intake_artifacts_v2",
        lambda _root: False,
    )
    with pytest.raises(RuntimeError, match="failed verification"):
        kv2.write_korthals_source_intake_artifacts_v2(
            intake,
            tmp_path / "self-check",
        )


def _write_v2_intake(
    tmp_path: Path,
) -> Path:
    intake = _valid_intake(tmp_path / "source")
    output = tmp_path / "intake"
    kv2.write_korthals_source_intake_artifacts_v2(
        intake,
        output,
    )
    return output


def _rewrite_json(path: Path, mutate) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    mutate(document)
    path.write_text(canonical_json(document) + "\n", encoding="utf-8")


def _refresh_v2_integrity(root: Path) -> None:
    source = json.loads(
        (root / "source_manifest.json").read_text(encoding="utf-8")
    )
    records = [
        kv2._file_record(root / "intake_summary.json", root),
        kv2._file_record(root / "source_manifest.json", root),
    ]
    manifest_path = root / "artifact_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"] = records
    manifest["source_manifest_fingerprint"] = source[
        "source_manifest_fingerprint"
    ]
    core = dict(manifest)
    core.pop("artifact_manifest_fingerprint", None)
    manifest["artifact_manifest_fingerprint"] = fingerprint(core)
    manifest_path.write_text(canonical_json(manifest) + "\n", encoding="utf-8")
    targets = sorted(
        path
        for path in root.iterdir()
        if path.is_file() and path.name != "SHA256SUMS"
    )
    (root / "SHA256SUMS").write_text(
        "\n".join(
            f"{kv2._sha256_file(path)}  {path.name}"
            for path in targets
        )
        + "\n",
        encoding="utf-8",
    )


def test_v2_intake_verifier_guard_matrix(
    tmp_path: Path,
) -> None:
    assert not kv2.verify_korthals_source_intake_artifacts_v2(
        tmp_path / "missing"
    )

    for index, mutate in enumerate(
        [
            lambda root: (root / "extra").write_text("x", encoding="utf-8"),
            lambda root: _rewrite_json(
                root / "artifact_manifest.json",
                lambda doc: doc.__setitem__("schema", "wrong"),
            ),
            lambda root: _rewrite_json(
                root / "artifact_manifest.json",
                lambda doc: doc.__setitem__("case_study_id", "wrong"),
            ),
            lambda root: _rewrite_json(
                root / "artifact_manifest.json",
                lambda doc: doc.__setitem__("protocol_fingerprint", "wrong"),
            ),
            lambda root: _rewrite_json(
                root / "intake_summary.json",
                lambda doc: doc.__setitem__("case_study_id", "wrong"),
            ),
            lambda root: _rewrite_json(
                root / "intake_summary.json",
                lambda doc: doc.__setitem__("protocol_fingerprint", "wrong"),
            ),
        ],
        start=1,
    ):
        root = _write_v2_intake(tmp_path / f"case-{index}")
        mutate(root)
        if index > 1:
            _refresh_v2_integrity(root)
        assert not kv2.verify_korthals_source_intake_artifacts_v2(root)


def _execution_archive(
    tmp_path: Path,
) -> tuple[Path, ev2.KorthalsAOIExecutionV2]:
    prepared = _synthetic_prepared()
    execution = ev2.run_korthals_aoi_execution_v2(prepared)
    output = tmp_path / "execution"
    ev2.write_korthals_execution_artifacts_v2(
        execution,
        output,
        execution_context=_execution_context(prepared),
        environment_text=_environment_text(),
    )
    return output, execution


def test_execution_v2_writer_public_guards(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(TypeError, match="KorthalsAOIExecutionV2"):
        ev2.write_korthals_execution_artifacts_v2(
            object(),  # type: ignore[arg-type]
            tmp_path / "bad",
            execution_context={},
            environment_text="x",
        )

    prepared = _synthetic_prepared()
    execution = ev2.run_korthals_aoi_execution_v2(prepared)
    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory path"):
        ev2.write_korthals_execution_artifacts_v2(
            execution,
            file_path,
            execution_context=_execution_context(prepared),
            environment_text=_environment_text(),
        )

    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "x").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="not empty"):
        ev2.write_korthals_execution_artifacts_v2(
            execution,
            nonempty,
            execution_context=_execution_context(prepared),
            environment_text=_environment_text(),
        )

    monkeypatch.setattr(
        ev2,
        "verify_korthals_execution_artifacts_v2",
        lambda _root: False,
    )
    with pytest.raises(RuntimeError, match="failed verification"):
        ev2.write_korthals_execution_artifacts_v2(
            execution,
            tmp_path / "self-check",
            execution_context=_execution_context(prepared),
            environment_text=_environment_text(),
        )


def test_execution_v2_prepared_identity_guards() -> None:
    prepared = _synthetic_prepared()
    protocol = kv2.verify_korthals_protocol_v2()

    for key, value, message in [
        ("case_study_id", "wrong", "case study"),
        ("protocol_fingerprint", "wrong", "protocol v2"),
        ("companion_commit", "wrong", "companion commit"),
        ("missingness_policy", "wrong", "missingness policy"),
    ]:
        identity = dict(prepared.source_identity)
        identity[key] = value
        bad = replace_prepared(prepared, source_identity=identity)
        with pytest.raises(ValueError, match=message):
            ev2._validate_prepared_identity_v2(
                bad,
                protocol,
            )

    with pytest.raises(ValueError, match="missing columns"):
        ev2._validate_prepared_identity_v2(
            replace_prepared(
                prepared,
                data=prepared.data.drop(columns="error_group"),
            ),
            protocol,
        )

    bad_data = prepared.data.copy()
    bad_data["target_type"] = "moving_circle"
    with pytest.raises(ValueError, match="unexpected target types"):
        ev2._validate_prepared_identity_v2(
            replace_prepared(prepared, data=bad_data),
            protocol,
        )

    bad_protocol = copy.deepcopy(protocol)
    bad_protocol["validation"]["n_validation_points"] = 8
    with pytest.raises(ValueError, match="nine points"):
        ev2._validate_prepared_identity_v2(
            prepared,
            bad_protocol,
        )


def replace_prepared(prepared, **kwargs):
    values = {
        "data": prepared.data,
        "validation_groups": prepared.validation_groups,
        "source_identity": prepared.source_identity,
    }
    values.update(kwargs)
    return type(prepared)(**values)


def test_execution_v2_context_final_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _synthetic_prepared()
    context = _execution_context(prepared)
    lock = load_korthals_source_lock()

    monkeypatch.setattr(
        ev2,
        "verify_korthals_source_lock",
        lambda: lock,
    )

    bad = dict(context)
    bad["source_lock_fingerprint"] = "0" * 64
    with pytest.raises(ValueError, match="source-lock fingerprint"):
        ev2._validated_execution_context_v2(
            bad,
            prepared,
        )

    fake_lock = copy.deepcopy(lock)
    fake_lock["lock_fingerprint"] = "0" * 64
    monkeypatch.setattr(
        ev2,
        "verify_korthals_source_lock",
        lambda: fake_lock,
    )
    with pytest.raises(ValueError, match="differs from packaged source lock"):
        ev2._validated_execution_context_v2(
            context,
            prepared,
        )


def test_execution_v2_verifier_and_reveal_guards(
    tmp_path: Path,
) -> None:
    assert not ev2.verify_korthals_execution_artifacts_v2(
        tmp_path / "missing"
    )
    with pytest.raises(ValueError, match="failed verification"):
        ev2.reveal_korthals_execution_v2(
            tmp_path / "missing"
        )

    root, _execution = _execution_archive(tmp_path / "base")
    assert ev2.verify_korthals_execution_artifacts_v2(root)

    (root / "extra.txt").write_text("x", encoding="utf-8")
    assert not ev2.verify_korthals_execution_artifacts_v2(root)
