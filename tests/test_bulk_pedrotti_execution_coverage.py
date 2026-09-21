from __future__ import annotations

import json
import runpy
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import gazeaudit.pedrotti_execution as pe
from gazeaudit.pedrotti_source import psource.PedrottiSourceIntake


ROOT = Path(__file__).resolve().parents[1]
BASE = runpy.run_path(str(ROOT / "tests" / "test_pedrotti_execution.py"))
_trial = BASE["_trial"]
_synthetic_prepared = BASE["_synthetic_prepared"]
_locked_shape_identity = BASE["_locked_shape_identity"]


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("", 1, "short", [0, 1], [0, 1], [0, 1]), "participant_id"),
        (("01", 0, "short", [0, 1], [0, 1], [0, 1]), "trial_index"),
        (("01", True, "short", [0, 1], [0, 1], [0, 1]), "trial_index"),
        (("01", 1, "bad", [0, 1], [0, 1], [0, 1]), "condition"),
        (("01", 1, "short", [[0, 1]], [0, 1], [0, 1]), "one-dimensional"),
        (("01", 1, "short", [0], [0], [0]), "at least two"),
        (("01", 1, "short", [0, 1], [0], [0, 1]), "equal length"),
        (("01", 1, "short", [0, np.nan], [0, 1], [0, 1]), "strictly increasing"),
        (("01", 1, "short", [1, 1], [0, 1], [0, 1]), "strictly increasing"),
    ],
)
def test_make_trial_validation_guards(args, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        pe.make_pedrotti_trial(*args)


def _intake() -> psource.PedrottiSourceIntake:
    return psource.PedrottiSourceIntake(
        source_manifest={"source_manifest_fingerprint": "s" * 64},
        intake_summary={
            "participant_count": 1,
            "source_file_count": 1,
            "total_row_count": 4,
            "total_trial_count": 2,
            "short_numeric_trial_count": 1,
            "long_numeric_trial_count": 1,
            "eye_counts": {"left": 1, "right": 0},
            "participants": [
                {
                    "participant_id": "01",
                    "eye": "left",
                    "short_numeric_trial_count": 1,
                    "long_numeric_trial_count": 1,
                }
            ],
        },
    )


def _source_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "TRIAL_INDEX": [1, 1, 2, 2],
            "LEFT_GAZE_X": [0.0, 1.0, 0.0, 2.0],
            "LEFT_GAZE_Y": [0.0, 0.0, 0.0, 0.0],
            "TIMESTAMP": [0.0, 1.0, 0.0, 1.0],
            "TrialTextShown": ["1,234", "1,234", "12,345,678", "12,345,678"],
        }
    )


def test_prepare_execution_data_full_positive_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(pe.pd, "read_csv", lambda *args, **kwargs: _source_frame())
    prepared = pe.prepare_pedrotti_execution_data(tmp_path, _intake())
    assert prepared.participant_ids == ("01",)
    assert len(prepared.trials) == 2
    assert prepared.source_identity["numeric_trial_count"] == 2
    assert prepared.source_identity["scientific_endpoint_evaluated_before_preparation"] is False


def test_prepare_execution_data_type_and_source_guards(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="psource.PedrottiSourceIntake"):
        pe.prepare_pedrotti_execution_data(tmp_path, object())  # type: ignore[arg-type]

    with pytest.raises(FileNotFoundError, match="source_dir"):
        pe.prepare_pedrotti_execution_data(tmp_path / "missing", _intake())


def test_prepare_execution_data_rejects_unstable_stimulus_and_count_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unstable = _source_frame()
    unstable.loc[1, "TrialTextShown"] = "other"
    monkeypatch.setattr(pe.pd, "read_csv", lambda *args, **kwargs: unstable)
    with pytest.raises(ValueError, match="unstable stimulus"):
        pe.prepare_pedrotti_execution_data(tmp_path, _intake())

    short_only = _source_frame()
    short_only.loc[short_only["TRIAL_INDEX"] == 2, "TrialTextShown"] = "word"
    monkeypatch.setattr(pe.pd, "read_csv", lambda *args, **kwargs: short_only)
    with pytest.raises(ValueError, match="long-numeric trial count drifted"):
        pe.prepare_pedrotti_execution_data(tmp_path, _intake())

    long_only = _source_frame()
    long_only.loc[long_only["TRIAL_INDEX"] == 1, "TrialTextShown"] = "word"
    monkeypatch.setattr(pe.pd, "read_csv", lambda *args, **kwargs: long_only)
    with pytest.raises(ValueError, match="short-numeric trial count drifted"):
        pe.prepare_pedrotti_execution_data(tmp_path, _intake())


def test_validate_prepared_contract_guards() -> None:
    with pytest.raises(TypeError, match="PreparedPedrottiData"):
        pe._validate_prepared(object())  # type: ignore[arg-type]

    empty = pe.PreparedPedrottiData({}, (), ())
    with pytest.raises(ValueError, match="participants and numeric trials"):
        pe._validate_prepared(empty)

    trial = _trial("01", 1, "short")
    duplicate_ids = pe.PreparedPedrottiData({}, (trial,), ("01", "01"))
    with pytest.raises(ValueError, match="participant identities"):
        pe._validate_prepared(duplicate_ids)

    wrong_trial = pe.PreparedPedrottiData({}, (object(),), ("01",))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="PedrottiTrial"):
        pe._validate_prepared(wrong_trial)

    absent = pe.PreparedPedrottiData({}, (_trial("02", 1, "short"),), ("01",))
    with pytest.raises(ValueError, match="absent from participant_ids"):
        pe._validate_prepared(absent)

    duplicate = pe.PreparedPedrottiData(
        {},
        (_trial("01", 1, "short"), _trial("01", 1, "long")),
        ("01",),
    )
    with pytest.raises(ValueError, match="duplicate participant-by-trial"):
        pe._validate_prepared(duplicate)

    missing_condition = pe.PreparedPedrottiData({}, (_trial("01", 1, "short"),), ("01",))
    with pytest.raises(ValueError, match="both frozen numeric conditions"):
        pe._validate_prepared(missing_condition)


def _lock_for(prepared: pe.PreparedPedrottiData) -> dict[str, object]:
    identity = prepared.source_identity
    return {
        "source": {
            "source_manifest_fingerprint": identity["source_manifest_fingerprint"],
            "file_count": identity["source_file_count"],
        },
        "intake": {
            "participant_count": identity["participant_count"],
            "total_row_count": identity["total_row_count"],
            "total_trial_count": identity["total_trial_count"],
            "short_numeric_trial_count": identity["short_numeric_trial_count"],
            "long_numeric_trial_count": identity["long_numeric_trial_count"],
            "eye_counts": identity["eye_counts"],
        },
    }


def test_locked_prepared_positive_and_identity_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base = _synthetic_prepared(participants=36)
    prepared = replace(base, source_identity=_locked_shape_identity())
    lock = _lock_for(prepared)
    monkeypatch.setattr(pe, "verify_pedrotti_source_lock", lambda _doc=None: lock)
    assert pe._verify_locked_prepared(prepared, lock_document=lock) is prepared

    bad_identity = dict(prepared.source_identity)
    bad_identity["source_file_count"] = -1
    with pytest.raises(ValueError, match="differs from source lock"):
        pe._verify_locked_prepared(
            replace(prepared, source_identity=bad_identity),
            lock_document=lock,
        )


@pytest.mark.parametrize("target_hz", [0.0, -1.0, np.nan, np.inf])
def test_sampled_rate_requires_positive_finite_rate(target_hz: float) -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        pe._trial_rate_sampled(_trial(), target_hz)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"mechanism": "bad", "fraction": 0.1, "replicate": 1}, "mechanism"),
        ({"mechanism": "mcar_within_trial", "fraction": -0.1, "replicate": 1}, "fraction"),
        ({"mechanism": "mcar_within_trial", "fraction": np.nan, "replicate": 1}, "fraction"),
        ({"mechanism": "mcar_within_trial", "fraction": 0.1, "replicate": 0}, "replicate"),
        ({"mechanism": "mcar_within_trial", "fraction": 0.1, "replicate": True}, "replicate"),
    ],
)
def test_added_missingness_argument_guards(kwargs, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        pe._added_missingness_positions(_trial(), root_seed=1, **kwargs)


def test_study_estimate_rejects_nonfinite_trial_endpoint() -> None:
    prepared = _synthetic_prepared()
    with pytest.raises(ValueError, match="trial endpoint"):
        pe._study_estimate(prepared, lambda _trial: np.nan)


def test_study_estimate_rejects_missing_condition() -> None:
    prepared = pe.PreparedPedrottiData(
        {},
        (_trial("01", 1, "short"),),
        ("01",),
    )
    with pytest.raises(ValueError, match="lacks a frozen numeric condition"):
        pe._study_estimate(prepared, pe._trial_rate_native)


@pytest.mark.parametrize(
    ("reference", "estimate"),
    [(np.nan, 1.0), (1.0, np.inf)],
)
def test_recovery_diagnostic_requires_finite_values(reference: float, estimate: float) -> None:
    protocol = pe._verified_protocol(None)
    with pytest.raises(ValueError, match="finite estimates"):
        pe._recovery_diagnostic(reference, estimate, protocol)


def _execution36() -> pe.PedrottiScientificExecution:
    return pe.run_pedrotti_scientific_execution(_synthetic_prepared(participants=36))


def test_archived_result_rows_positive_path() -> None:
    execution = _execution36()
    pe._validate_archived_result_rows(
        execution.reference,
        execution.sampling_results,
        execution.missingness_results,
        execution.protocol,
    )


@pytest.mark.parametrize(
    ("kind", "message"),
    [
        ("reference_fields", "unexpected field set"),
        ("unit", "unit differs"),
        ("participant_count", "36 participant"),
        ("participant_fields", "unexpected field set"),
        ("participant_ids", "01 through 36"),
        ("participant_nonfinite", "non-finite"),
        ("sampling_count", "count differs"),
        ("sampling_grid", "differs from frozen grid"),
        ("sampling_diagnostic", "diagnostic is inconsistent"),
        ("missing_count", "count differs"),
        ("missing_grid", "differs from frozen grid"),
        ("missing_diagnostic", "diagnostic is inconsistent"),
    ],
)
def test_archived_result_row_guardrails(kind: str, message: str) -> None:
    execution = _execution36()
    reference = json.loads(pe.canonical_json(execution.reference))
    sampling = json.loads(pe.canonical_json(list(execution.sampling_results)))
    missingness = json.loads(pe.canonical_json(list(execution.missingness_results)))

    if kind == "reference_fields":
        reference["extra"] = True
    elif kind == "unit":
        reference["unit"] = "wrong"
    elif kind == "participant_count":
        reference["participant_contrasts"] = reference["participant_contrasts"][:-1]
    elif kind == "participant_fields":
        reference["participant_contrasts"][0]["extra"] = True
    elif kind == "participant_ids":
        reference["participant_contrasts"][0]["participant_id"] = "99"
    elif kind == "participant_nonfinite":
        reference["participant_contrasts"][0]["contrast"] = np.nan
    elif kind == "sampling_count":
        sampling.pop()
    elif kind == "sampling_grid":
        sampling[0]["target_hz"] = -1
    elif kind == "sampling_diagnostic":
        sampling[0]["relative_deviation"] = 999.0
    elif kind == "missing_count":
        missingness.pop()
    elif kind == "missing_grid":
        missingness[0]["replicate"] = 999
    elif kind == "missing_diagnostic":
        missingness[0]["relative_deviation"] = 999.0

    with pytest.raises(ValueError, match=message):
        pe._validate_archived_result_rows(
            reference,
            sampling,
            missingness,
            execution.protocol,
        )


def _classify_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    sampling = [
        {
            "estimate": 1.0,
            "relative_deviation": 0.0,
            "same_strict_sign": True,
            "recovered": True,
        }
        for _ in range(5)
    ]
    missing = [
        {
            "estimate": 1.0,
            "relative_deviation": 0.0,
            "same_strict_sign": True,
            "recovered": True,
        }
        for _ in range(160)
    ]
    return sampling, missing


def _families(value: object) -> list[dict[str, object]]:
    return [{"recovery_fraction": value} for _ in range(9)]


def test_execution_classifier_all_boundaries() -> None:
    protocol = pe._verified_protocol(None)
    sampling, missing = _classify_rows()

    assert (
        pe._classify_execution(
            np.nan,
            sampling,
            missing,
            _families(1.0),
            protocol,
        )
        == "incomplete"
    )
    assert (
        pe._classify_execution(
            0.0,
            sampling,
            missing,
            _families(1.0),
            protocol,
        )
        == "indeterminate_reference_zero"
    )
    assert (
        pe._classify_execution(
            1.0,
            sampling[:-1],
            missing,
            _families(1.0),
            protocol,
        )
        == "incomplete"
    )
    assert (
        pe._classify_execution(
            1.0,
            sampling,
            missing,
            _families(1.0)[:-1],
            protocol,
        )
        == "incomplete"
    )

    bad = [dict(row) for row in sampling]
    bad[0].pop("estimate")
    assert pe._classify_execution(1.0, bad, missing, _families(1.0), protocol) == "incomplete"

    bad = [dict(row) for row in sampling]
    bad[0]["estimate"] = np.nan
    assert pe._classify_execution(1.0, bad, missing, _families(1.0), protocol) == "incomplete"

    bad = [dict(row) for row in sampling]
    bad[0]["same_strict_sign"] = None
    assert pe._classify_execution(1.0, bad, missing, _families(1.0), protocol) == "incomplete"

    bad = [dict(row) for row in sampling]
    bad[0]["recovered"] = None
    assert pe._classify_execution(1.0, bad, missing, _families(1.0), protocol) == "incomplete"

    assert pe._classify_execution(1.0, sampling, missing, _families(None), protocol) == "incomplete"
    assert (
        pe._classify_execution(
            1.0,
            sampling,
            missing,
            _families(np.nan),
            protocol,
        )
        == "incomplete"
    )
    assert pe._classify_execution(1.0, sampling, missing, _families(2.0), protocol) == "incomplete"

    minimum = float(protocol["interpretation"]["minimum_family_recovery"])
    fragile = float(protocol["interpretation"]["material_fragility_ceiling"])
    assert pe._classify_execution(1.0, sampling, missing, _families(minimum), protocol) == "robust"
    assert (
        pe._classify_execution(
            1.0,
            sampling,
            missing,
            _families(fragile),
            protocol,
        )
        == "materially_fragile"
    )

    middle = (minimum + fragile) / 2.0
    assert pe._classify_execution(1.0, sampling, missing, _families(middle), protocol) == "mixed"


def _context() -> dict[str, object]:
    return {
        "schema": "gazeaudit-pedrotti-execution-context-v1",
        "execution_commit": "a" * 40,
        "workflow_ref": pe.PEDROTTI_EXECUTION_WORKFLOW,
        "github_run_id": 1,
        "runner_os": "Linux",
        "runner_arch": "X64",
        "python": "3.12.14",
    }


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("schema", "wrong", "schema"),
        ("execution_commit", "bad", "40-hex"),
        ("workflow_ref", "wrong", "workflow"),
        ("github_run_id", 0, "positive integer"),
        ("github_run_id", True, "positive integer"),
        ("runner_os", "", "runner_os"),
        ("runner_arch", "", "runner_arch"),
        ("python", "3.13", "3.12.14"),
    ],
)
def test_execution_context_guardrails(field: str, value: object, message: str) -> None:
    document = _context()
    document[field] = value
    with pytest.raises(ValueError, match=message):
        pe._validated_execution_context(document)

    missing = _context()
    missing.pop("runner_arch")
    with pytest.raises(ValueError, match="field set"):
        pe._validated_execution_context(missing)


def test_execution_context_requires_object() -> None:
    class WeirdMapping(dict):
        pass

    with pytest.raises(TypeError, match="normalize to an object"):
        pe._validated_execution_context([])  # type: ignore[arg-type]


@pytest.mark.parametrize("text", ["", " ", "numpy==2.5.3\n"])
def test_environment_snapshot_guardrails(text: str) -> None:
    with pytest.raises(ValueError, match="environment snapshot"):
        pe._validate_environment_snapshot(text)

    pe._validate_environment_snapshot("numpy==2.5.3\npandas==2.3.3\n")


def test_writer_public_guards(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(TypeError, match="PedrottiScientificExecution"):
        pe.write_pedrotti_locked_execution_artifacts(
            object(),  # type: ignore[arg-type]
            tmp_path / "out",
            execution_context=_context(),
            environment_text="numpy==2.5.3\npandas==2.3.3\n",
        )

    execution = _execution36()
    monkeypatch.setattr(pe, "_verify_locked_prepared", lambda value, **kwargs: value)

    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory path"):
        pe.write_pedrotti_locked_execution_artifacts(
            execution,
            file_path,
            execution_context=_context(),
            environment_text="numpy==2.5.3\npandas==2.3.3\n",
        )

    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "x").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="not empty"):
        pe.write_pedrotti_locked_execution_artifacts(
            execution,
            nonempty,
            execution_context=_context(),
            environment_text="numpy==2.5.3\npandas==2.3.3\n",
        )

    monkeypatch.setattr(pe, "verify_pedrotti_locked_execution_artifacts", lambda _root: False)
    with pytest.raises(RuntimeError, match="failed verification"):
        pe.write_pedrotti_locked_execution_artifacts(
            execution,
            tmp_path / "self-check",
            execution_context=_context(),
            environment_text="numpy==2.5.3\npandas==2.3.3\n",
        )


def test_reveal_rejects_invalid_archive(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="failed locked verification"):
        pe.reveal_pedrotti_locked_execution(tmp_path)


def test_checksum_and_json_parsers(
    tmp_path: Path,
) -> None:
    checksum = tmp_path / "SHA256SUMS"
    checksum.write_text("bad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid SHA256SUMS"):
        pe._parse_checksums(checksum)

    checksum.write_text("a" * 64 + "  ../bad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid SHA256SUMS"):
        pe._parse_checksums(checksum)

    obj = tmp_path / "obj.json"
    obj.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        pe._read_json(obj)

    array = tmp_path / "array.json"
    array.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON array"):
        pe._read_json_list(array)

    array.write_text("[1]", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON array"):
        pe._read_json_list(array)
