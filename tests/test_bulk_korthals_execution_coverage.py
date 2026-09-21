from __future__ import annotations

import dataclasses
import functools
import json
import pathlib
import runpy

import numpy as np
import pandas as pd
import pytest

import gazeaudit.korthals_execution as ke

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = runpy.run_path(str(ROOT / "tests" / "test_korthals_execution.py"))
_aligned_fixture = BASE["_aligned_fixture"]
_validation_fixture = BASE["_validation_fixture"]


def _prepared() -> ke.PreparedKorthalsData:
    return ke.prepare_korthals_aligned_data(
        _aligned_fixture(),
        _validation_fixture(),
        source_identity={"fixture": "bulk-coverage"},
    )


@functools.lru_cache(maxsize=1)
def _execution() -> ke.KorthalsAOIExecution:
    return ke.run_korthals_aoi_execution(_prepared())


def test_protocol_loader_requires_json_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ke.json, "loads", lambda _text: [])
    with pytest.raises(ValueError, match="JSON object"):
        ke.load_korthals_protocol()


def test_protocol_verification_rejects_generic_and_frozen_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol = ke.load_korthals_protocol()
    monkeypatch.setattr(ke, "verify_aoi_uncertainty_protocol", lambda _doc: False)
    with pytest.raises(ValueError, match="generic protocol verification"):
        ke.verify_korthals_protocol(protocol)

    monkeypatch.undo()
    bad = json.loads(ke.canonical_json(protocol))
    bad["case_study_id"] = "wrong"
    with pytest.raises(ValueError, match="frozen guardrails"):
        ke.verify_korthals_protocol(bad)


def test_prepare_public_type_and_empty_guards() -> None:
    validations = _validation_fixture()
    with pytest.raises(TypeError, match="aligned_data"):
        ke.prepare_korthals_aligned_data(object(), validations)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="validations"):
        ke.prepare_korthals_aligned_data(_aligned_fixture(), object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="must not be empty"):
        ke.prepare_korthals_aligned_data(pd.DataFrame(), validations)


def test_prepare_requires_both_target_types_before_and_after_filtering() -> None:
    one_type = _aligned_fixture()
    one_type = one_type.loc[one_type["target_type"] == "moving_circle"].copy()
    with pytest.raises(ValueError, match="both frozen target types"):
        ke.prepare_korthals_aligned_data(one_type, _validation_fixture())

    excluded = _aligned_fixture(participants=("21db28aa",))
    excluded = excluded.loc[excluded["target_type"] == "jumping_circle"].copy()
    with pytest.raises(ValueError, match="both frozen target types"):
        ke.prepare_korthals_aligned_data(excluded, _validation_fixture(participants=("21db28aa",)))


def test_prepare_rejects_nonfinite_target_and_all_missing_gaze() -> None:
    bad_target = _aligned_fixture()
    bad_target.loc[0, "target_x"] = np.nan
    with pytest.raises(ValueError, match="target coordinates"):
        ke.prepare_korthals_aligned_data(bad_target, _validation_fixture())

    missing = _aligned_fixture()
    missing[["gaze_x", "gaze_y"]] = np.nan
    with pytest.raises(ValueError, match="no finite gaze"):
        ke.prepare_korthals_aligned_data(missing, _validation_fixture())


def test_prepare_rejects_validation_group_mismatch_and_duplicate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ke,
        "_validation_trial_mapping",
        lambda _data, _validations: {
            (str(row.participant_id), int(row.trial_number)): (999, 0.0)
            for row in _data[["participant_id", "trial_number"]]
            .drop_duplicates()
            .itertuples(index=False)
        },
    )
    with pytest.raises(ValueError, match="validation summary"):
        ke.prepare_korthals_aligned_data(_aligned_fixture(), _validation_fixture())

    monkeypatch.undo()
    duplicate = _validation_fixture()
    duplicate = pd.concat([duplicate, duplicate.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="validation_nr values must be unique"):
        ke.prepare_korthals_aligned_data(_aligned_fixture(), duplicate)


def test_run_requires_prepared_type() -> None:
    with pytest.raises(TypeError, match="PreparedKorthalsData"):
        ke.run_korthals_aoi_execution(object())  # type: ignore[arg-type]


def test_normalize_aligned_data_guard_matrix() -> None:
    base = _aligned_fixture(participants=("p1",))

    with pytest.raises(ValueError, match="missing required columns"):
        ke._normalize_aligned_data(base.drop(columns="gaze_x"))

    bad = base.copy()
    bad["participant_id"] = ""
    with pytest.raises(ValueError, match="participant_id"):
        ke._normalize_aligned_data(bad)

    bad = base.copy()
    bad.loc[0, "trial_number"] = np.nan
    with pytest.raises(ValueError, match="trial_number and trial_time"):
        ke._normalize_aligned_data(bad)

    bad = base.copy()
    bad.loc[0, "trial_number"] = 1.5
    with pytest.raises(ValueError, match="integer-valued"):
        ke._normalize_aligned_data(bad)

    bad = base.copy()
    bad.loc[0, "trial_number"] = 145
    with pytest.raises(ValueError, match="1..144"):
        ke._normalize_aligned_data(bad)

    bad = base.copy()
    bad.loc[0, "trial_time"] = np.inf
    with pytest.raises(ValueError, match="trial_time must be finite"):
        ke._normalize_aligned_data(bad)

    bad = base.copy()
    bad.loc[0, "trial_time"] = -0.1
    with pytest.raises(ValueError, match="non-negative"):
        ke._normalize_aligned_data(bad)

    bad = base.copy()
    bad.loc[0, "target_speed"] = np.nan
    with pytest.raises(ValueError, match="target coordinates and target_speed"):
        ke._normalize_aligned_data(bad)

    for column in ("target_type", "target_speed", "target_trajectory"):
        bad = base.copy()
        mask = bad["trial_number"] == 1
        index = bad.index[mask][-1]
        if column == "target_speed":
            bad.loc[index, column] = 99.0
        else:
            bad.loc[index, column] = "other"
        with pytest.raises(ValueError, match=f"{column} must be constant"):
            ke._normalize_aligned_data(bad)


def test_normalize_validations_guard_matrix() -> None:
    base = _validation_fixture(participants=("p1",))

    with pytest.raises(ValueError, match="missing required columns"):
        ke._normalize_validations(base.drop(columns="error_avg"))

    bad = base.copy()
    bad.loc[0, "first_trial"] = np.nan
    with pytest.raises(ValueError, match="both first_trial and last_trial"):
        ke._normalize_validations(bad)

    empty = base.copy()
    empty[["first_trial", "last_trial"]] = np.nan
    with pytest.raises(ValueError, match="no validation rows"):
        ke._normalize_validations(empty)

    bad = base.copy()
    bad.loc[0, "error_avg"] = np.nan
    with pytest.raises(ValueError, match="require validation_nr and error_avg"):
        ke._normalize_validations(bad)

    for value in (-1.0, np.inf):
        bad = base.copy()
        bad.loc[0, "error_avg"] = value
        with pytest.raises(ValueError, match="finite and non-negative"):
            ke._normalize_validations(bad)

    for column in ("validation_nr", "first_trial", "last_trial"):
        bad = base.copy()
        bad.loc[0, column] = 1.5
        with pytest.raises(ValueError, match="integer-valued"):
            ke._normalize_validations(bad)

    bad = base.copy()
    bad.loc[0, "first_trial"] = 10
    bad.loc[0, "last_trial"] = 1
    with pytest.raises(ValueError, match="must not exceed"):
        ke._normalize_validations(bad)

    duplicate = pd.concat([base, base.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="validation_nr values must be unique"):
        ke._normalize_validations(duplicate)


def test_validation_trial_mapping_guards() -> None:
    data = ke._normalize_aligned_data(_aligned_fixture(participants=("p1",)))
    validations = ke._normalize_validations(_validation_fixture(participants=("p1",)))

    missing_participant = validations.copy()
    missing_participant["participant_id"] = "other"
    with pytest.raises(ValueError, match="no validation summaries"):
        ke._validation_trial_mapping(data, missing_participant)

    overlapping = pd.concat(
        [
            validations,
            pd.DataFrame(
                {
                    "participant_id": ["p1"],
                    "validation_nr": [3],
                    "error_avg": [0.1],
                    "first_trial": [1],
                    "last_trial": [144],
                }
            ),
        ],
        ignore_index=True,
    )
    with pytest.raises(ValueError, match="exactly one validation block"):
        ke._validation_trial_mapping(data, overlapping)


def test_downsample_rejects_nonincreasing_and_duplicate_source_selection() -> None:
    frame = pd.DataFrame(
        {
            "trial_time": [0.0, 0.0],
            "x": [0, 1],
        }
    )
    with pytest.raises(ValueError, match="strictly increasing"):
        ke._downsample_trial_50hz(frame)

    sparse = pd.DataFrame(
        {
            "trial_time": [0.0, 0.05],
            "x": [0, 1],
        }
    )
    with pytest.raises(ValueError, match="duplicate source samples"):
        ke._downsample_trial_50hz(sparse)


def test_trial_metadata_and_pairing_guards() -> None:
    prepared = _prepared()
    data = prepared.data.copy()

    with pytest.raises(ValueError, match="missing columns"):
        ke._trial_metadata(data.drop(columns="target_type"))

    duplicate = pd.concat(
        [
            data,
            data.loc[data["trial_number"] == 1].assign(target_type="jumping_circle"),
        ],
        ignore_index=True,
    )
    with pytest.raises(ValueError, match="one frozen metadata identity"):
        ke._trial_metadata(duplicate)

    incomplete = data.loc[data["target_type"] == "moving_circle"].copy()
    with pytest.raises(ValueError, match="incomplete or duplicated"):
        ke._require_complete_trial_pairing(incomplete)

    duplicated_cell = pd.concat([data, data.loc[data["trial_number"] == 1]], ignore_index=True)
    duplicated_cell.loc[duplicated_cell.index[-1], "trial_number"] = 3
    with pytest.raises(ValueError, match="at most one trial"):
        ke._retain_complete_matched_cells(duplicated_cell)

    with pytest.raises(ValueError, match="no complete frozen matched cells"):
        ke._retain_complete_matched_cells(incomplete)


def test_endpoint_weights_and_membership_guards() -> None:
    prepared = _prepared()
    data = prepared.data.copy()

    with pytest.raises(ValueError, match="must not be empty"):
        ke._endpoint_weights(data.iloc[0:0])

    incomplete = data.loc[data["target_type"] == "moving_circle"].copy()
    with pytest.raises(ValueError, match="complete frozen matched cell"):
        ke._endpoint_weights(incomplete)

    with pytest.raises(ValueError, match="one-dimensional"):
        ke._validate_membership(np.ones((2, 2)), 4)
    with pytest.raises(ValueError, match="match data rows"):
        ke._validate_membership(np.ones(2), 4)
    with pytest.raises(ValueError, match="between 0 and 1"):
        ke._validate_membership(np.array([0.0, np.nan]), 2)
    with pytest.raises(ValueError, match="between 0 and 1"):
        ke._validate_membership(np.array([0.0, 2.0]), 2)


def test_prepared_identity_guard_matrix() -> None:
    prepared = _prepared()
    protocol = ke.verify_korthals_protocol()

    identity = dict(prepared.source_identity)
    identity["protocol_fingerprint"] = "wrong"
    with pytest.raises(ValueError, match="frozen protocol"):
        ke._validate_prepared_identity(
            dataclasses.replace(
                prepared,
                source_identity=identity,
            ),
            protocol,
        )

    identity = dict(prepared.source_identity)
    identity["companion_commit"] = "wrong"
    with pytest.raises(ValueError, match="companion commit"):
        ke._validate_prepared_identity(
            dataclasses.replace(
                prepared,
                source_identity=identity,
            ),
            protocol,
        )

    with pytest.raises(ValueError, match="missing columns"):
        ke._validate_prepared_identity(
            dataclasses.replace(prepared, data=prepared.data.drop(columns="error_group")),
            protocol,
        )

    bad_type = prepared.data.copy()
    bad_type["target_type"] = "moving_circle"
    with pytest.raises(ValueError, match="unexpected target types"):
        ke._validate_prepared_identity(dataclasses.replace(prepared, data=bad_type), protocol)

    bad_protocol = json.loads(ke.canonical_json(protocol))
    bad_protocol["validation"]["n_validation_points"] = 8
    with pytest.raises(ValueError, match="nine points"):
        ke._validate_prepared_identity(prepared, bad_protocol)


def test_korthals_classification_boundaries() -> None:
    assert ke._classify_korthals_result(
        pd.Series(
            {
                "hard_effect": 1.0,
                "probability_above_reference": 0.95,
                "probability_below_reference": 0.0,
            }
        )
    ) == "robust_positive"
    assert ke._classify_korthals_result(
        pd.Series(
            {
                "hard_effect": -1.0,
                "probability_above_reference": 0.0,
                "probability_below_reference": 0.95,
            }
        )
    ) == "robust_negative"
    assert ke._classify_korthals_result(
        pd.Series(
            {
                "hard_effect": 1.0,
                "probability_above_reference": 0.5,
                "probability_below_reference": 0.5,
            }
        )
    ) == "measurement_sensitive"


def test_writer_public_guards(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(TypeError, match="KorthalsAOIExecution"):
        ke.write_korthals_execution_artifacts(object(), tmp_path / "out")  # type: ignore[arg-type]

    execution = _execution()
    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory path"):
        ke.write_korthals_execution_artifacts(execution, file_path)

    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "x").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="not empty"):
        ke.write_korthals_execution_artifacts(execution, nonempty)

    monkeypatch.setattr(ke, "verify_korthals_execution_artifacts", lambda _root: False)
    with pytest.raises(RuntimeError, match="failed verification"):
        ke.write_korthals_execution_artifacts(execution, tmp_path / "self-check")


def _write_archive(tmp_path: pathlib.Path) -> pathlib.Path:
    root = tmp_path / "archive"
    ke.write_korthals_execution_artifacts(_execution(), root)
    return root


def _rewrite_manifest(root: pathlib.Path, mutate) -> None:
    path = root / "artifact_manifest.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    mutate(document)
    core = dict(document)
    core.pop("artifact_manifest_fingerprint", None)
    document["artifact_manifest_fingerprint"] = ke.fingerprint(core)
    path.write_text(ke.canonical_json(document) + "\n", encoding="utf-8")


def test_execution_artifact_verifier_guard_matrix(
    tmp_path: pathlib.Path,
) -> None:
    assert not ke.verify_korthals_execution_artifacts(tmp_path / "missing")

    root = _write_archive(tmp_path)
    (root / "audit" / "summary.json").unlink()
    assert not ke.verify_korthals_execution_artifacts(root)

    root = _write_archive(tmp_path / "schema")
    _rewrite_manifest(root, lambda doc: doc.__setitem__("schema", "wrong"))
    assert not ke.verify_korthals_execution_artifacts(root)

    root = _write_archive(tmp_path / "protocol")
    _rewrite_manifest(root, lambda doc: doc.__setitem__("protocol_fingerprint", "wrong"))
    assert not ke.verify_korthals_execution_artifacts(root)

    root = _write_archive(tmp_path / "declared")
    _rewrite_manifest(root, lambda doc: doc.__setitem__("files", "bad"))
    assert not ke.verify_korthals_execution_artifacts(root)

    root = _write_archive(tmp_path / "checksums")
    checksum = root / "SHA256SUMS"
    lines = checksum.read_text(encoding="utf-8").splitlines()
    checksum.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    assert not ke.verify_korthals_execution_artifacts(root)

    root = _write_archive(tmp_path / "digest")
    checksum = root / "SHA256SUMS"
    lines = checksum.read_text(encoding="utf-8").splitlines()
    _, relative = lines[0].split("  ", 1)
    lines[0] = "0" * 64 + "  " + relative
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert not ke.verify_korthals_execution_artifacts(root)

    root = _write_archive(tmp_path / "json")
    (root / "artifact_manifest.json").write_text("{", encoding="utf-8")
    assert not ke.verify_korthals_execution_artifacts(root)


def test_checksum_parser_guardrails(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "SHA256SUMS"
    path.write_text("\n" + "a" * 64 + "  file.txt\n", encoding="utf-8")
    assert ke._parse_checksums(path) == {"file.txt": "a" * 64}

    path.write_text("bad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid SHA256SUMS"):
        ke._parse_checksums(path)

    path.write_text("a" * 64 + "  ../file.txt\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid or duplicate"):
        ke._parse_checksums(path)
