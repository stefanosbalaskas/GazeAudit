from __future__ import annotations

import copy
import dataclasses
import importlib.metadata
import pathlib
import runpy
import types

import numpy as np
import pandas as pd
import pytest

import gazeaudit.gazebase_execution as gb
import gazeaudit.korthals_execution as ke
import gazeaudit.korthals_execution_v2 as kev2
import gazeaudit.study as study_module


ROOT = pathlib.Path(__file__).resolve().parents[1]
GB_FIX = runpy.run_path(str(ROOT / "tests" / "test_gazebase_execution.py"))
K_FIX = runpy.run_path(str(ROOT / "tests" / "test_korthals_execution.py"))
K2_FIX = runpy.run_path(str(ROOT / "tests" / "test_korthals_execution_v2.py"))


def _gb_prepared():
    return GB_FIX["_prepared"]()


def _gb_versions():
    return GB_FIX["_versions"]()


def _gb_factory_calls():
    return GB_FIX["_factory_calls"]()


def _gb_runner(**kwargs):
    return GB_FIX["_runner"](**kwargs)


def _k_prepared():
    return ke.prepare_korthals_aligned_data(
        K_FIX["_aligned_fixture"](participants=("p1",)),
        K_FIX["_validation_fixture"](participants=("p1",), error_avg=0.0),
    )


def _k_execution():
    return ke.run_korthals_aoi_execution(_k_prepared())


def _k2_prepared():
    return K2_FIX["_synthetic_prepared"]()


def _k2_execution():
    return kev2.run_korthals_aoi_execution_v2(_k2_prepared())


# ---------------------------------------------------------------------------
# GazeBase protocol, dataset-adapter, execution, and provenance guards
# ---------------------------------------------------------------------------


class _FakeResource:
    def __init__(self, text: str) -> None:
        self.text = text

    def joinpath(self, _name: str):
        return self

    def read_text(self, *, encoding: str) -> str:
        assert encoding == "utf-8"
        return self.text


def test_gazebase_protocol_loader_and_verifier_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gb.resources,
        "files",
        lambda _name: _FakeResource("[]"),
    )
    with pytest.raises(ValueError, match="JSON object"):
        gb.load_gazebase_protocol()

    with pytest.raises(ValueError, match="unexpected fingerprint"):
        gb.verify_gazebase_protocol(
            {
                "protocol_fingerprint": "wrong",
                "protocol": {},
            }
        )

    with pytest.raises(ValueError, match="missing the protocol object"):
        gb.verify_gazebase_protocol(
            {
                "protocol_fingerprint": gb.GAZEBASE_PROTOCOL_FINGERPRINT,
                "protocol": None,
            }
        )

    document = copy.deepcopy(GB_FIX["load_gazebase_protocol"]())
    protocol = document["protocol"]
    protocol["detector_space"]["post_hoc_retuning_allowed"] = True
    document["protocol_fingerprint"] = gb.fingerprint(protocol)
    monkeypatch.setattr(
        gb,
        "GAZEBASE_PROTOCOL_FINGERPRINT",
        document["protocol_fingerprint"],
    )
    with pytest.raises(ValueError, match="frozen guardrails"):
        gb.verify_gazebase_protocol(document)


def _recording(
    *,
    lab: bool = True,
    pixel: bool = True,
    n: int = 2,
):
    data = {
        "time": np.arange(n, dtype=float) * 10,
        "position": [np.array([float(i), 0.0]) for i in range(n)],
    }
    if pixel:
        data["pixel"] = data["position"]
    if lab:
        data["lab"] = [1] * n
    return GB_FIX["_FakeRecording"](pd.DataFrame(data))


def _fileinfo(
    tasks: tuple[str, ...],
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "round_id": 1,
                "subject_id": 1,
                "session_id": 1,
                "task_name": task,
            }
            for task in tasks
        ]
    )


def test_gazebase_dataset_adapter_rejects_empty_missing_and_misaligned_inputs() -> None:
    dataset_type = GB_FIX["_FakeDataset"]

    with pytest.raises(ValueError, match="dataset.gaze"):
        gb.prepare_gazebase_pymovements_dataset(
            dataset_type([], pd.DataFrame())
        )

    with pytest.raises(ValueError, match="fileinfo is missing"):
        gb.prepare_gazebase_pymovements_dataset(
            dataset_type(
                [_recording()],
                pd.DataFrame([{"round_id": 1}]),
            )
        )

    with pytest.raises(ValueError, match="one-to-one"):
        gb.prepare_gazebase_pymovements_dataset(
            dataset_type(
                [_recording(), _recording()],
                _fileinfo(("FXS",)),
            )
        )

    with pytest.raises(ValueError, match="both FXS and TEX"):
        gb.prepare_gazebase_pymovements_dataset(
            dataset_type(
                [_recording()],
                _fileinfo(("FXS",)),
            )
        )


def test_gazebase_dataset_adapter_requires_deg2pix_and_pixel_result() -> None:
    fileinfo = _fileinfo(("FXS", "TEX"))

    without_converter = types.SimpleNamespace(
        gaze=[
            _recording(pixel=False),
            _recording(pixel=False),
        ],
        fileinfo=fileinfo,
    )
    with pytest.raises(TypeError, match="deg2pix"):
        gb.prepare_gazebase_pymovements_dataset(without_converter)

    class BadDataset:
        def __init__(self) -> None:
            self.gaze = [
                _recording(pixel=False),
                _recording(pixel=False),
            ]
            self.fileinfo = fileinfo

        def deg2pix(self, **_kwargs) -> None:
            return None

    with pytest.raises(ValueError, match="did not produce"):
        gb.prepare_gazebase_pymovements_dataset(BadDataset())


def test_gazebase_dataset_adapter_requires_reference_labels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dataset_type = GB_FIX["_FakeDataset"]
    dataset = dataset_type(
        [
            _recording(lab=False),
            _recording(lab=False),
        ],
        _fileinfo(("FXS", "TEX")),
    )
    with pytest.raises(ValueError, match="must contain EyeLink parser"):
        gb.prepare_gazebase_pymovements_dataset(dataset)

    dataset = dataset_type(
        [
            _recording(),
            _recording(),
        ],
        _fileinfo(("FXS", "TEX")),
    )

    class Adapter:
        def __init__(self, **_kwargs) -> None:
            pass

        def to_study(self, recording):
            frame = recording.samples.iloc[:1]
            return study_module.GazeStudy(
                pd.DataFrame(
                    {
                        "x": [0.0],
                        "y": [0.0],
                        "timestamp": [0.0],
                        "participant": [1],
                        "trial": ["x"],
                    }
                )
            )

    monkeypatch.setattr(gb, "PymovementsGazeAdapter", Adapter)
    with pytest.raises(ValueError, match="one-to-one"):
        gb.prepare_gazebase_pymovements_dataset(dataset)


def test_gazebase_software_version_error_paths() -> None:
    def missing(name: str) -> str:
        if name == "pymovements":
            raise importlib.metadata.PackageNotFoundError(name)
        return "0"

    with pytest.raises(RuntimeError, match="not installed"):
        gb.verify_gazebase_software_versions(missing)

    values = {
        "pymovements": "0.28.0",
        "pEYES": "0.2.2",
        "gazeaudit": "not-a-version",
    }
    with pytest.raises(RuntimeError, match="PEP 440"):
        gb.verify_gazebase_software_versions(values.__getitem__)


def test_gazebase_execution_requires_prepared_data() -> None:
    with pytest.raises(TypeError, match="PreparedGazeBaseData"):
        gb.run_gazebase_multidetector_execution(
            object(),  # type: ignore[arg-type]
            gazeaudit_commit="a" * 40,
        )


class _NoDefaults:
    pass


class _BadDefaults:
    def get_default_params(self):
        return []


def test_gazebase_execution_requires_detector_default_contract() -> None:
    with pytest.raises(TypeError, match="get_default_params"):
        gb.run_gazebase_multidetector_execution(
            _gb_prepared(),
            gazeaudit_commit="a" * 40,
            detector_factory=lambda *args, **kwargs: _NoDefaults(),
            detector_runner=_gb_runner(),
            version_getter=_gb_versions(),
        )

    with pytest.raises(TypeError, match="defaults must be a mapping"):
        gb.run_gazebase_multidetector_execution(
            _gb_prepared(),
            gazeaudit_commit="a" * 40,
            detector_factory=lambda *args, **kwargs: _BadDefaults(),
            detector_runner=_gb_runner(),
            version_getter=_gb_versions(),
        )


def test_gazebase_execution_requires_detector_sample_contract() -> None:
    _, factory = _gb_factory_calls()

    with pytest.raises(TypeError, match="pandas DataFrame samples"):
        gb.run_gazebase_multidetector_execution(
            _gb_prepared(),
            gazeaudit_commit="a" * 40,
            detector_factory=factory,
            detector_runner=lambda *args, **kwargs: types.SimpleNamespace(samples=None),
            version_getter=_gb_versions(),
        )

    _, factory = _gb_factory_calls()
    with pytest.raises(ValueError, match="missing required columns"):
        gb.run_gazebase_multidetector_execution(
            _gb_prepared(),
            gazeaudit_commit="a" * 40,
            detector_factory=factory,
            detector_runner=lambda *args, **kwargs: types.SimpleNamespace(
                samples=pd.DataFrame(
                    {
                        "participant": [1],
                        "trial": ["FXS"],
                        "timestamp": [0.0],
                    }
                )
            ),
            version_getter=_gb_versions(),
        )


def _gb_baseline_execution():
    _, factory = _gb_factory_calls()
    return gb.run_gazebase_multidetector_execution(
        _gb_prepared(),
        gazeaudit_commit="a" * 40,
        detector_factory=factory,
        detector_runner=_gb_runner(),
        version_getter=_gb_versions(),
    )


def test_gazebase_execution_rechecks_frozen_reference_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline = _gb_baseline_execution()

    monkeypatch.setattr(
        gb,
        "audit_detector_robustness",
        lambda *args, **kwargs: dataclasses.replace(
            baseline.audit,
            fixed_cohort=("changed",),
        ),
    )
    _, factory = _gb_factory_calls()
    with pytest.raises(RuntimeError, match="changed the frozen reference-defined cohort"):
        gb.run_gazebase_multidetector_execution(
            _gb_prepared(),
            gazeaudit_commit="a" * 40,
            detector_factory=factory,
            detector_runner=_gb_runner(),
            version_getter=_gb_versions(),
        )

    monkeypatch.setattr(
        gb,
        "audit_detector_robustness",
        lambda *args, **kwargs: dataclasses.replace(
            baseline.audit,
            reference_effect=baseline.audit.reference_effect + 1.0,
        ),
    )
    _, factory = _gb_factory_calls()
    with pytest.raises(RuntimeError, match="changed the frozen external-reference effect"):
        gb.run_gazebase_multidetector_execution(
            _gb_prepared(),
            gazeaudit_commit="a" * 40,
            detector_factory=factory,
            detector_runner=_gb_runner(),
            version_getter=_gb_versions(),
        )


def test_gazebase_execution_requires_verified_publication_bundle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        gb,
        "verify_publication_audit_bundle",
        lambda _bundle: False,
    )
    _, factory = _gb_factory_calls()
    with pytest.raises(RuntimeError, match="publication bundle failed verification"):
        gb.run_gazebase_multidetector_execution(
            _gb_prepared(),
            gazeaudit_commit="a" * 40,
            detector_factory=factory,
            detector_runner=_gb_runner(),
            version_getter=_gb_versions(),
        )


def test_gazebase_source_identity_and_study_guards() -> None:
    protocol = gb.verify_gazebase_protocol()
    with pytest.raises(ValueError, match="non-empty mapping"):
        gb._validate_source_identity({}, protocol)

    identity = GB_FIX["_source_identity"]()
    identity["dataset"] = "wrong"
    with pytest.raises(ValueError, match="does not match"):
        gb._validate_source_identity(identity, protocol)

    identity = GB_FIX["_source_identity"]()
    identity["catalog_archive_md5"] = "wrong"
    with pytest.raises(ValueError, match="archive MD5"):
        gb._validate_source_identity(identity, protocol)

    with pytest.raises(TypeError, match="GazeStudy"):
        gb._validate_execution_study(object())  # type: ignore[arg-type]

    study = _gb_prepared().study
    only_fxs = study.copy_with(
        study.data.loc[study.data["trial"].eq("FXS")].reset_index(drop=True)
    )
    with pytest.raises(ValueError, match="exactly the frozen"):
        gb._validate_execution_study(only_fxs)


def test_gazebase_small_provenance_helpers() -> None:
    assert gb._reference_label(np.nan) == "undefined"
    assert gb._reference_label("not-an-int") == "undefined"
    assert gb._reference_label(1) == "fixation"

    assert gb._sample_columns(types.SimpleNamespace()) == set()
    assert gb._sample_columns(types.SimpleNamespace(columns=["x", 2])) == {"x", "2"}

    with pytest.raises(TypeError, match="expose to_pandas"):
        gb._to_pandas_frame(object(), "value")

    class Bad:
        def to_pandas(self):
            return []

    with pytest.raises(TypeError, match="must return a pandas DataFrame"):
        gb._to_pandas_frame(Bad(), "value")

    assert gb._safe_value(np.int64(2)) == 2
    assert gb._safe_value({"x": np.int64(3)}) == {"x": 3}
    assert gb._safe_value(np.array([1, 2])) == [1, 2]
    stamp = pd.Timestamp("2026-01-01")
    assert gb._safe_value(stamp) == stamp.isoformat()
    assert gb._safe_value(pd.NA) is None

    class Unsupported:
        pass

    with pytest.raises(TypeError, match="unsupported GazeBase provenance"):
        gb._safe_value(Unsupported())


# ---------------------------------------------------------------------------
# Korthals v1 normalization, endpoint, identity, artifact guards
# ---------------------------------------------------------------------------


def test_korthals_protocol_loader_and_verifier_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ke.resources,
        "files",
        lambda _name: _FakeResource("[]"),
    )
    with pytest.raises(ValueError, match="JSON object"):
        ke.load_korthals_protocol()

    with pytest.raises(ValueError, match="generic protocol verification"):
        ke.verify_korthals_protocol({})

    protocol = copy.deepcopy(K_FIX["load_korthals_protocol"]())
    protocol["monte_carlo"]["draws"] = 1
    core = dict(protocol)
    core.pop("protocol_fingerprint")
    protocol["protocol_fingerprint"] = ke.fingerprint(core)
    monkeypatch.setattr(
        ke,
        "KORTHALS_PROTOCOL_FINGERPRINT",
        protocol["protocol_fingerprint"],
    )
    with pytest.raises(ValueError, match="frozen guardrails"):
        ke.verify_korthals_protocol(protocol)


def test_korthals_prepare_public_input_guards() -> None:
    validations = K_FIX["_validation_fixture"](participants=("p1",))

    with pytest.raises(TypeError, match="aligned_data"):
        ke.prepare_korthals_aligned_data(object(), validations)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="validations"):
        ke.prepare_korthals_aligned_data(
            K_FIX["_aligned_fixture"](participants=("p1",)),
            object(),  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="must not be empty"):
        ke.prepare_korthals_aligned_data(pd.DataFrame(), validations)


def _base_aligned() -> pd.DataFrame:
    return K_FIX["_aligned_fixture"](participants=("p1",))


def _base_validation() -> pd.DataFrame:
    return K_FIX["_validation_fixture"](participants=("p1",))


def test_korthals_prepare_target_and_gaze_guardrails() -> None:
    aligned = _base_aligned()
    aligned["target_type"] = "other"
    with pytest.raises(ValueError, match="no frozen moving/jumping-circle"):
        ke.prepare_korthals_aligned_data(aligned, _base_validation())

    aligned = _base_aligned()
    aligned.loc[aligned["target_type"].eq("jumping_circle"), "target_type"] = "other"
    with pytest.raises(ValueError, match="both frozen target types"):
        ke.prepare_korthals_aligned_data(aligned, _base_validation())

    aligned = _base_aligned()
    aligned.loc[0, "target_x"] = np.inf
    with pytest.raises(ValueError, match="target coordinates"):
        ke.prepare_korthals_aligned_data(aligned, _base_validation())

    aligned = _base_aligned()
    aligned[["gaze_x", "gaze_y"]] = np.nan
    with pytest.raises(ValueError, match="no finite gaze rows"):
        ke.prepare_korthals_aligned_data(aligned, _base_validation())


def test_korthals_prepare_source_identity_must_normalize_to_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ke, "canonical_json", lambda _value: "[]")
    with pytest.raises(TypeError, match="normalize to an object"):
        ke.prepare_korthals_aligned_data(
            _base_aligned(),
            _base_validation(),
            source_identity={"x": 1},
        )


def test_korthals_normalize_aligned_data_guardrails() -> None:
    base = _base_aligned()

    blank = base.copy()
    blank.loc[0, "participant_id"] = " "
    with pytest.raises(ValueError, match="participant_id"):
        ke._normalize_aligned_data(blank)

    missing_trial = base.copy()
    missing_trial.loc[0, "trial_number"] = np.nan
    with pytest.raises(ValueError, match="trial_number and trial_time"):
        ke._normalize_aligned_data(missing_trial)

    noninteger = base.copy()
    noninteger.loc[0, "trial_number"] = 1.5
    with pytest.raises(ValueError, match="integer-valued"):
        ke._normalize_aligned_data(noninteger)

    out_of_range = base.copy()
    out_of_range.loc[0, "trial_number"] = 145
    with pytest.raises(ValueError, match="1..144"):
        ke._normalize_aligned_data(out_of_range)

    nonfinite_time = base.copy()
    nonfinite_time.loc[0, "trial_time"] = np.inf
    with pytest.raises(ValueError, match="trial_time must be finite"):
        ke._normalize_aligned_data(nonfinite_time)

    negative_time = base.copy()
    negative_time.loc[0, "trial_time"] = -0.1
    with pytest.raises(ValueError, match="non-negative"):
        ke._normalize_aligned_data(negative_time)

    target = base.copy()
    target.loc[0, "target_speed"] = np.inf
    with pytest.raises(ValueError, match="target coordinates and target_speed"):
        ke._normalize_aligned_data(target)

    inconsistent = base.copy()
    rows = inconsistent["trial_number"].eq(1)
    inconsistent.loc[inconsistent.index[rows][0], "target_trajectory"] = "different"
    with pytest.raises(ValueError, match="constant within participant trial"):
        ke._normalize_aligned_data(inconsistent)


def test_korthals_normalize_validations_guardrails() -> None:
    base = _base_validation()

    with pytest.raises(ValueError, match="missing required columns"):
        ke._normalize_validations(base.drop(columns="error_avg"))

    one_bound = base.copy()
    one_bound.loc[0, "last_trial"] = np.nan
    with pytest.raises(ValueError, match="both first_trial and last_trial"):
        ke._normalize_validations(one_bound)

    empty = base.copy()
    empty[["first_trial", "last_trial"]] = np.nan
    with pytest.raises(ValueError, match="no validation rows"):
        ke._normalize_validations(empty)

    negative = base.copy()
    negative.loc[0, "error_avg"] = -1.0
    with pytest.raises(ValueError, match="finite and non-negative"):
        ke._normalize_validations(negative)

    fractional = base.copy()
    fractional.loc[0, "validation_nr"] = 1.5
    with pytest.raises(ValueError, match="integer-valued"):
        ke._normalize_validations(fractional)

    reversed_range = base.copy()
    reversed_range.loc[0, ["first_trial", "last_trial"]] = [10, 1]
    with pytest.raises(ValueError, match="must not exceed"):
        ke._normalize_validations(reversed_range)

    duplicate = pd.concat([base, base.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="validation_nr values must be unique"):
        ke._normalize_validations(duplicate)


def test_korthals_mapping_sampling_and_metadata_guardrails() -> None:
    data = ke._normalize_aligned_data(_base_aligned())
    validations = ke._normalize_validations(_base_validation())

    with pytest.raises(ValueError, match="has no validation summaries"):
        ke._validation_trial_mapping(
            data.assign(participant_id="missing"),
            validations,
        )

    trial = data.loc[data["trial_number"].eq(1)].copy()
    trial = trial.sort_values("trial_time")
    trial.loc[trial.index[1], "trial_time"] = trial.iloc[0]["trial_time"]
    with pytest.raises(ValueError, match="strictly increasing"):
        ke._sample_trial_to_grid(trial)

    sparse = data.loc[data["trial_number"].eq(1)].iloc[[0, -1]].copy()
    sparse.iloc[0, sparse.columns.get_loc("trial_time")] = 0.0
    sparse.iloc[1, sparse.columns.get_loc("trial_time")] = 0.1
    with pytest.raises(ValueError, match="duplicate source samples"):
        ke._sample_trial_to_grid(sparse)

    missing = data.drop(columns="target_speed")
    with pytest.raises(ValueError, match="endpoint data is missing"):
        ke._trial_metadata(missing)

    inconsistent = data.copy()
    extra = inconsistent.iloc[[0]].copy()
    extra["target_type"] = "jumping_circle"
    inconsistent = pd.concat([inconsistent, extra], ignore_index=True)
    with pytest.raises(ValueError, match="one frozen metadata identity"):
        ke._trial_metadata(inconsistent)


def test_korthals_endpoint_and_membership_guardrails() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        ke._endpoint_weights(pd.DataFrame())

    data = _k_prepared().data.copy()
    with pytest.raises(ValueError, match="one-dimensional"):
        ke._validate_membership(np.zeros((len(data), 1)), len(data))

    bad = np.zeros(len(data))
    bad[0] = 2.0
    with pytest.raises(ValueError, match="between 0 and 1"):
        ke._validate_membership(bad, len(data))

    duplicate = data.copy()
    moving = duplicate.loc[duplicate["target_type"].eq("moving_circle")].iloc[[0]].copy()
    moving["trial_number"] = 99
    duplicate = pd.concat([duplicate, moving], ignore_index=True)
    with pytest.raises(ValueError, match="at most one trial"):
        ke._retain_complete_matched_cells(duplicate)


def test_korthals_prepared_identity_and_classification_guards() -> None:
    prepared = _k_prepared()
    protocol = ke.verify_korthals_protocol()

    bad_identity = dict(prepared.source_identity)
    bad_identity["protocol_fingerprint"] = "wrong"
    with pytest.raises(ValueError, match="frozen protocol"):
        ke._validate_prepared_identity(
            dataclasses.replace(prepared, source_identity=bad_identity),
            protocol,
        )

    bad_identity = dict(prepared.source_identity)
    bad_identity["companion_commit"] = "wrong"
    with pytest.raises(ValueError, match="companion commit"):
        ke._validate_prepared_identity(
            dataclasses.replace(prepared, source_identity=bad_identity),
            protocol,
        )

    with pytest.raises(ValueError, match="missing columns"):
        ke._validate_prepared_identity(
            dataclasses.replace(prepared, data=prepared.data.drop(columns="observed_x")),
            protocol,
        )

    bad_types = prepared.data.assign(target_type="moving_circle")
    with pytest.raises(ValueError, match="unexpected target types"):
        ke._validate_prepared_identity(
            dataclasses.replace(prepared, data=bad_types),
            protocol,
        )

    bad_protocol = copy.deepcopy(protocol)
    bad_protocol["validation"]["n_validation_points"] = 8
    with pytest.raises(ValueError, match="requires nine points"):
        ke._validate_prepared_identity(prepared, bad_protocol)

    negative = pd.Series(
        {
            "hard_effect": -1.0,
            "probability_above_reference": 0.0,
            "probability_below_reference": 0.95,
        }
    )
    assert ke._classify_korthals_result(negative) == "robust_negative"

    sensitive = pd.Series(
        {
            "hard_effect": 1.0,
            "probability_above_reference": 0.5,
            "probability_below_reference": 0.5,
        }
    )
    assert ke._classify_korthals_result(sensitive) == "measurement_sensitive"


def test_korthals_execution_and_writer_public_guards(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(TypeError, match="PreparedKorthalsData"):
        ke.run_korthals_aoi_execution(object())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="KorthalsAOIExecution"):
        ke.write_korthals_execution_artifacts(
            object(),  # type: ignore[arg-type]
            tmp_path / "bad",
        )

    execution = _k_execution()
    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory path"):
        ke.write_korthals_execution_artifacts(execution, file_path)

    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "x").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="not empty"):
        ke.write_korthals_execution_artifacts(execution, nonempty)

    monkeypatch.setattr(
        ke,
        "verify_korthals_execution_artifacts",
        lambda _path: False,
    )
    with pytest.raises(RuntimeError, match="failed verification"):
        ke.write_korthals_execution_artifacts(
            execution,
            tmp_path / "self-check",
        )


def test_korthals_artifact_verifier_basic_fail_closed_paths(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert not ke.verify_korthals_execution_artifacts(tmp_path / "missing")

    root = tmp_path / "valid"
    execution = _k_execution()
    ke.write_korthals_execution_artifacts(execution, root)

    monkeypatch.setattr(
        ke,
        "verify_aoi_uncertainty_artifacts",
        lambda _path: False,
    )
    assert not ke.verify_korthals_execution_artifacts(root)


def test_korthals_checksum_parser_guardrails(
    tmp_path: pathlib.Path,
) -> None:
    path = tmp_path / "sums"
    path.write_text("\n" + "a" * 64 + "  file\n", encoding="utf-8")
    assert ke._parse_checksums(path) == {"file": "a" * 64}

    path.write_text("bad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid SHA256SUMS"):
        ke._parse_checksums(path)

    path.write_text("a" * 64 + "  ../file\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid or duplicate"):
        ke._parse_checksums(path)


# ---------------------------------------------------------------------------
# Korthals protocol-v2 execution and archive guards
# ---------------------------------------------------------------------------


def test_korthals_v2_execution_requires_prepared_type() -> None:
    with pytest.raises(TypeError, match="PreparedKorthalsData"):
        kev2.run_korthals_aoi_execution_v2(object())  # type: ignore[arg-type]


def test_korthals_v2_locked_entry_delegates_after_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _k2_prepared()
    marker = object()
    calls: list[object] = []
    monkeypatch.setattr(
        kev2,
        "verify_korthals_locked_prepared",
        lambda value, lock_document=None: calls.append(value),
    )
    monkeypatch.setattr(
        kev2,
        "run_korthals_aoi_execution_v2",
        lambda *args, **kwargs: marker,
    )
    assert (
        kev2.run_korthals_locked_aoi_execution_v2(prepared)
        is marker
    )
    assert calls == [prepared]


def test_korthals_v2_prepared_identity_guardrails() -> None:
    prepared = _k2_prepared()
    protocol = kev2.verify_korthals_protocol_v2()

    cases = [
        ("case_study_id", "wrong", "case study"),
        ("protocol_fingerprint", "wrong", "protocol v2"),
        ("companion_commit", "wrong", "companion commit"),
        ("missingness_policy", "wrong", "missingness policy"),
    ]
    for field, value, message in cases:
        identity = dict(prepared.source_identity)
        identity[field] = value
        with pytest.raises(ValueError, match=message):
            kev2._validate_prepared_identity_v2(
                dataclasses.replace(prepared, source_identity=identity),
                protocol,
            )

    with pytest.raises(ValueError, match="missing columns"):
        kev2._validate_prepared_identity_v2(
            dataclasses.replace(prepared, data=prepared.data.drop(columns="observed_x")),
            protocol,
        )

    with pytest.raises(ValueError, match="unexpected target types"):
        kev2._validate_prepared_identity_v2(
            dataclasses.replace(prepared, data=prepared.data.assign(target_type="moving_circle")),
            protocol,
        )

    bad_protocol = copy.deepcopy(protocol)
    bad_protocol["validation"]["n_validation_points"] = 8
    with pytest.raises(ValueError, match="requires nine points"):
        kev2._validate_prepared_identity_v2(prepared, bad_protocol)


def test_korthals_v2_writer_public_guards(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(TypeError, match="KorthalsAOIExecutionV2"):
        kev2.write_korthals_execution_artifacts_v2(
            object(),  # type: ignore[arg-type]
            tmp_path / "bad",
            execution_context={},
            environment_text="x",
        )

    execution = _k2_execution()
    context = K2_FIX["_execution_context"](execution.prepared)
    environment = K2_FIX["_environment_text"]()

    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="directory path"):
        kev2.write_korthals_execution_artifacts_v2(
            execution,
            file_path,
            execution_context=context,
            environment_text=environment,
        )

    nonempty = tmp_path / "nonempty"
    nonempty.mkdir()
    (nonempty / "x").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="not empty"):
        kev2.write_korthals_execution_artifacts_v2(
            execution,
            nonempty,
            execution_context=context,
            environment_text=environment,
        )

    monkeypatch.setattr(
        kev2,
        "verify_korthals_execution_artifacts_v2",
        lambda _path: False,
    )
    with pytest.raises(RuntimeError, match="failed verification"):
        kev2.write_korthals_execution_artifacts_v2(
            execution,
            tmp_path / "self-check",
            execution_context=context,
            environment_text=environment,
        )


def test_korthals_v2_reveal_rejects_invalid_archive(
    tmp_path: pathlib.Path,
) -> None:
    with pytest.raises(ValueError, match="failed verification"):
        kev2.reveal_korthals_execution_v2(tmp_path / "missing")


def test_korthals_v2_execution_context_and_environment_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _k2_prepared()
    context = K2_FIX["_execution_context"](prepared)
    lock = {
        "lock_fingerprint": kev2.KORTHALS_SOURCE_LOCK_FINGERPRINT,
        "source": {
            "source_manifest_fingerprint": prepared.source_identity[
                "source_manifest_fingerprint"
            ]
        },
        "environment": {
            "python": context["python_version"],
            "numpy": "2.5.3",
            "pandas": "2.3.3",
            "scipy": "1.18.1",
        },
    }
    monkeypatch.setattr(kev2, "verify_korthals_source_lock", lambda: lock)
    monkeypatch.setattr(kev2, "version", lambda _name: context["package_version"])

    missing = dict(context)
    missing.pop("runner_arch")
    with pytest.raises(ValueError, match="exact required field set"):
        kev2._validated_execution_context_v2(missing, prepared)

    cases = [
        ("repository", "wrong", "repository identity"),
        ("execution_commit", "bad", "40-character Git SHA"),
        ("workflow_ref", "wrong", "workflow identity"),
        ("github_run_id", 0, "positive integer"),
        ("companion_repository", "wrong", "companion repository"),
        ("companion_commit", "wrong", "companion commit"),
        ("protocol_fingerprint", "wrong", "protocol-v2 fingerprint"),
        ("source_lock_fingerprint", "wrong", "source-lock fingerprint"),
        ("source_manifest_fingerprint", "wrong", "source fingerprint"),
        ("package_version", "wrong", "package version"),
        ("python_version", "wrong", "Python version"),
        ("runner_arch", "", "non-empty string"),
    ]
    for field, value, message in cases:
        bad = dict(context)
        bad[field] = value
        with pytest.raises(ValueError, match=message):
            kev2._validated_execution_context_v2(bad, prepared)

    assert kev2._validated_execution_context_v2(context, prepared) == context

    with pytest.raises(ValueError, match="non-empty dependency snapshot"):
        kev2._validate_environment_snapshot(" ")

    monkeypatch.setattr(kev2, "verify_korthals_source_lock", lambda: lock)
    with pytest.raises(ValueError, match="lacks locked critical versions"):
        kev2._validate_environment_snapshot("numpy==2.5.3\n")


def test_korthals_v2_prepared_identity_proxy_requires_positive_rows() -> None:
    with pytest.raises(ValueError, match="positive row count"):
        kev2._prepared_identity_proxy({}, {"n_rows": 0})
