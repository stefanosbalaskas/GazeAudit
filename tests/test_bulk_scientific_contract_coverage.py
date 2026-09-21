from __future__ import annotations

import copy
import json

import numpy as np
import pandas as pd
import pytest

import gazeaudit.pymovements_adapter as pymovements_adapter
import gazeaudit.sensitivity_protocol as sensitivity_protocol
import gazeaudit.study_qc as study_qc
import gazeaudit.uncertainty as uncertainty
from gazeaudit.aoi import RectangleAOI
from gazeaudit.study import GazeStudy


def _protocol_inputs() -> dict[str, object]:
    return {
        "case_study_id": "bulk-contract-v1",
        "dataset": {
            "name": "synthetic-source",
            "identity": "fixture-v1",
        },
        "representation": {
            "name": "native-stream",
            "unit": "px",
        },
        "endpoint": {
            "name": "condition contrast",
            "unit": "px/s",
        },
        "sampling": {
            "name": "sampling perturbation",
            "baseline_hz": 1000.0,
            "target_hz": [
                500.0,
                250.0,
            ],
        },
        "missingness": {
            "name": "missingness perturbation",
            "mechanisms": [
                "mcar",
                "block",
            ],
            "fractions": [
                0.05,
                0.10,
            ],
            "replicates": 4,
            "rng_seed": 123,
        },
        "interpretation": {
            "name": "recovery",
            "relative_tolerance": 0.20,
            "minimum_family_recovery": 0.90,
            "material_fragility_ceiling": 0.50,
        },
    }


def _protocol() -> dict[str, object]:
    return sensitivity_protocol.build_sampling_missingness_protocol(
        **_protocol_inputs()
    )


def _rehash_protocol(
    document: dict[str, object],
) -> dict[str, object]:
    output = copy.deepcopy(document)
    core = dict(output)
    core.pop(
        "protocol_fingerprint",
        None,
    )
    output["protocol_fingerprint"] = sensitivity_protocol.fingerprint(
        core
    )
    return output


def _qc_study() -> GazeStudy:
    return GazeStudy(
        pd.DataFrame(
            {
                "participant": [
                    "p1",
                    "p1",
                    "p2",
                    "p2",
                ],
                "trial": [
                    "a",
                    "a",
                    "b",
                    "b",
                ],
                "timestamp": [
                    0.0,
                    1.0,
                    0.0,
                    1.0,
                ],
                "x": [
                    10.0,
                    11.0,
                    20.0,
                    21.0,
                ],
                "y": [
                    5.0,
                    6.0,
                    7.0,
                    8.0,
                ],
            }
        )
    )


def _qc_audit() -> study_qc.StudyQCAudit:
    return study_qc.build_study_qc_audit(
        _qc_study()
    )


def _rewrite_artifact_manifest(
    path,
    mutate,
) -> dict[str, object]:
    document = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )
    mutate(document)
    core = dict(document)
    core.pop(
        "artifact_fingerprint",
        None,
    )
    document["artifact_fingerprint"] = study_qc.fingerprint(
        core
    )
    path.write_text(
        study_qc.canonical_json(document)
        + "\n",
        encoding="utf-8",
    )
    return document


# ---------------------------------------------------------------------------
# Sampling/missingness sensitivity protocol
# ---------------------------------------------------------------------------


def test_sensitivity_protocol_rejects_blank_case_identifier() -> None:
    values = _protocol_inputs()
    values["case_study_id"] = " "

    with pytest.raises(
        ValueError,
        match="case_study_id",
    ):
        sensitivity_protocol.build_sampling_missingness_protocol(
            **values
        )


def test_protocol_verifier_rejects_nonmapping() -> None:
    assert (
        sensitivity_protocol.verify_sampling_missingness_protocol(
            []  # type: ignore[arg-type]
        )
        is False
    )


def test_protocol_verifier_rejects_wrong_schema() -> None:
    document = _protocol()
    document["schema"] = "wrong-schema"

    assert not sensitivity_protocol.verify_sampling_missingness_protocol(
        document
    )


@pytest.mark.parametrize(
    "stored",
    [
        None,
        "short",
    ],
)
def test_protocol_verifier_requires_sha256_shape(
    stored: object,
) -> None:
    document = _protocol()
    document["protocol_fingerprint"] = stored

    assert not sensitivity_protocol.verify_sampling_missingness_protocol(
        document
    )


def test_protocol_verifier_rejects_blank_case_after_valid_rehash() -> None:
    document = _protocol()
    document["case_study_id"] = " "
    document = _rehash_protocol(document)

    assert not sensitivity_protocol.verify_sampling_missingness_protocol(
        document
    )


def test_protocol_verifier_rejects_empty_core_mapping_after_rehash() -> None:
    document = _protocol()
    document["dataset"] = {}
    document = _rehash_protocol(document)

    assert not sensitivity_protocol.verify_sampling_missingness_protocol(
        document
    )


def test_protocol_verifier_fails_closed_on_validation_exception() -> None:
    document = _protocol()
    sampling = dict(document["sampling"])
    sampling.pop("baseline_hz")
    document["sampling"] = sampling
    document = _rehash_protocol(document)

    assert not sensitivity_protocol.verify_sampling_missingness_protocol(
        document
    )


@pytest.mark.parametrize(
    ("sampling", "message"),
    [
        (
            {
                "name": "sampling",
                "target_hz": [100.0],
            },
            "baseline_hz",
        ),
        (
            {
                "name": "sampling",
                "baseline_hz": 1000.0,
            },
            "target_hz",
        ),
        (
            {
                "name": "sampling",
                "baseline_hz": 1000.0,
                "target_hz": [],
            },
            "at least one value",
        ),
        (
            {
                "name": "sampling",
                "baseline_hz": 1000.0,
                "target_hz": [0.0],
            },
            "must be positive",
        ),
    ],
)
def test_sampling_contract_guardrails(
    sampling: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        sensitivity_protocol._validate_sampling(
            sampling
        )


def test_missingness_contract_requires_all_fields() -> None:
    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        sensitivity_protocol._validate_missingness(
            {
                "mechanisms": ["mcar"],
            }
        )


def test_missingness_mechanisms_require_sequence() -> None:
    with pytest.raises(
        TypeError,
        match="mechanisms must be a sequence",
    ):
        sensitivity_protocol._validate_missingness(
            {
                "mechanisms": "mcar",
                "fractions": [0.1],
                "replicates": 2,
                "rng_seed": 1,
            }
        )


@pytest.mark.parametrize(
    "mechanisms",
    [
        [],
        [""],
    ],
)
def test_missingness_mechanisms_require_nonempty_names(
    mechanisms: list[str],
) -> None:
    with pytest.raises(
        ValueError,
        match="non-empty names",
    ):
        sensitivity_protocol._validate_missingness(
            {
                "mechanisms": mechanisms,
                "fractions": [0.1],
                "replicates": 2,
                "rng_seed": 1,
            }
        )


def test_missingness_mechanisms_must_be_unique() -> None:
    with pytest.raises(
        ValueError,
        match="mechanisms must be unique",
    ):
        sensitivity_protocol._validate_missingness(
            {
                "mechanisms": [
                    "mcar",
                    "mcar",
                ],
                "fractions": [0.1],
                "replicates": 2,
                "rng_seed": 1,
            }
        )


def test_missingness_fractions_require_values() -> None:
    with pytest.raises(
        ValueError,
        match="fractions must contain at least one value",
    ):
        sensitivity_protocol._validate_missingness(
            {
                "mechanisms": ["mcar"],
                "fractions": [],
                "replicates": 2,
                "rng_seed": 1,
            }
        )


def test_missingness_fractions_must_be_unique() -> None:
    with pytest.raises(
        ValueError,
        match="fractions must be unique",
    ):
        sensitivity_protocol._validate_missingness(
            {
                "mechanisms": ["mcar"],
                "fractions": [
                    0.1,
                    0.1,
                ],
                "replicates": 2,
                "rng_seed": 1,
            }
        )


@pytest.mark.parametrize(
    "seed",
    [
        True,
        1.5,
    ],
)
def test_missingness_seed_requires_integer(
    seed: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="rng_seed must be an integer",
    ):
        sensitivity_protocol._validate_missingness(
            {
                "mechanisms": ["mcar"],
                "fractions": [0.1],
                "replicates": 2,
                "rng_seed": seed,
            }
        )


def test_interpretation_requires_all_fields() -> None:
    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        sensitivity_protocol._validate_interpretation(
            {
                "relative_tolerance": 0.1,
            }
        )


def test_interpretation_rejects_negative_tolerance() -> None:
    with pytest.raises(
        ValueError,
        match="non-negative",
    ):
        sensitivity_protocol._validate_interpretation(
            {
                "relative_tolerance": -0.1,
                "minimum_family_recovery": 0.9,
                "material_fragility_ceiling": 0.5,
            }
        )


def test_canonical_mapping_requires_mapping() -> None:
    with pytest.raises(
        TypeError,
        match="must be a mapping",
    ):
        sensitivity_protocol._canonical_mapping(
            [],  # type: ignore[arg-type]
            name="demo",
        )


def test_canonical_mapping_requires_nonempty_input() -> None:
    with pytest.raises(
        ValueError,
        match="must be non-empty",
    ):
        sensitivity_protocol._canonical_mapping(
            {},
            name="demo",
        )


def test_canonical_mapping_requires_object_normalization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        sensitivity_protocol,
        "canonical_json",
        lambda _value: "[]",
    )

    with pytest.raises(
        TypeError,
        match="normalize to an object",
    ):
        sensitivity_protocol._canonical_mapping(
            {
                "name": "demo",
            },
            name="demo",
        )


def test_required_name_rejects_missing_name() -> None:
    with pytest.raises(
        ValueError,
        match="non-empty 'name'",
    ):
        sensitivity_protocol._require_name(
            {},
            name="dataset",
        )


def test_numeric_sequence_rejects_string() -> None:
    with pytest.raises(
        TypeError,
        match="must be a sequence",
    ):
        sensitivity_protocol._numeric_sequence(
            "1,2",
            name="values",
        )


def test_positive_float_rejects_zero() -> None:
    with pytest.raises(
        ValueError,
        match="must be positive",
    ):
        sensitivity_protocol._positive_float(
            0,
            name="rate",
        )


def test_probability_rejects_out_of_range_value() -> None:
    with pytest.raises(
        ValueError,
        match="between 0 and 1",
    ):
        sensitivity_protocol._probability(
            1.1,
            name="probability",
        )


@pytest.mark.parametrize(
    ("value", "error", "message"),
    [
        (
            True,
            TypeError,
            "must be numeric",
        ),
        (
            object(),
            TypeError,
            "must be numeric",
        ),
        (
            np.inf,
            ValueError,
            "must be finite",
        ),
    ],
)
def test_finite_float_guardrails(
    value: object,
    error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        error,
        match=message,
    ):
        sensitivity_protocol._finite_float(
            value,
            name="value",
        )


# ---------------------------------------------------------------------------
# Measurement uncertainty contracts
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mean", "covariance", "n_validation", "message"),
    [
        (
            np.zeros(3),
            np.eye(2),
            2,
            "mean_error",
        ),
        (
            np.zeros(2),
            np.eye(3),
            2,
            "covariance",
        ),
        (
            np.zeros(2),
            np.eye(2),
            1,
            "n_validation",
        ),
        (
            np.array([np.nan, 0.0]),
            np.eye(2),
            2,
            "must be finite",
        ),
        (
            np.zeros(2),
            np.array(
                [
                    [-1.0, 0.0],
                    [0.0, 1.0],
                ]
            ),
            2,
            "positive semidefinite",
        ),
    ],
)
def test_gaussian_error_model_constructor_guardrails(
    mean: np.ndarray,
    covariance: np.ndarray,
    n_validation: int,
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        uncertainty.GaussianGazeErrorModel(
            mean,
            covariance,
            n_validation,
        )


def test_gaussian_fit_requires_validation_columns() -> None:
    with pytest.raises(
        ValueError,
        match="missing validation columns",
    ):
        uncertainty.GaussianGazeErrorModel.fit(
            pd.DataFrame(
                {
                    "observed_x": [0.0, 1.0],
                }
            )
        )


def test_gaussian_fit_requires_two_complete_observations() -> None:
    frame = pd.DataFrame(
        {
            "observed_x": [1.0, np.nan],
            "observed_y": [1.0, np.nan],
            "target_x": [0.0, np.nan],
            "target_y": [0.0, np.nan],
        }
    )

    with pytest.raises(
        ValueError,
        match="at least two complete",
    ):
        uncertainty.GaussianGazeErrorModel.fit(
            frame
        )


def test_mean_radial_error_requires_numeric_scalar() -> None:
    with pytest.raises(
        TypeError,
        match="numeric scalar",
    ):
        uncertainty.GaussianGazeErrorModel.from_mean_radial_error(
            object(),
            n_validation=2,
        )


def test_gaussian_sampling_requires_positive_draw_count() -> None:
    model = uncertainty.GaussianGazeErrorModel(
        np.zeros(2),
        np.eye(2),
        2,
    )

    with pytest.raises(
        ValueError,
        match="draws",
    ):
        model.sample_true_points(
            np.array(
                [
                    [0.0, 0.0],
                ]
            ),
            draws=0,
        )


def test_grouped_model_requires_mapping() -> None:
    with pytest.raises(
        TypeError,
        match="models must be a mapping",
    ):
        uncertainty.GroupedGaussianGazeErrorModel(
            []  # type: ignore[arg-type]
        )


def test_grouped_model_requires_at_least_one_group() -> None:
    with pytest.raises(
        ValueError,
        match="at least one group",
    ):
        uncertainty.GroupedGaussianGazeErrorModel(
            {}
        )


def test_grouped_model_rejects_key_that_loses_hash_contract() -> None:
    model = uncertainty.GaussianGazeErrorModel(
        np.zeros(2),
        np.eye(2),
        2,
    )

    class VanishingHash:
        def __hash__(self) -> int:
            type(self).__hash__ = None
            return 123

    key = VanishingHash()
    models = {
        key: model,
    }

    with pytest.raises(
        TypeError,
        match="keys must be hashable",
    ):
        uncertainty.GroupedGaussianGazeErrorModel(
            models
        )


def test_grouped_model_rejects_missing_group_key() -> None:
    model = uncertainty.GaussianGazeErrorModel(
        np.zeros(2),
        np.eye(2),
        2,
    )

    with pytest.raises(
        ValueError,
        match="must not be missing",
    ):
        uncertainty.GroupedGaussianGazeErrorModel(
            {
                np.nan: model,
            }
        )


def test_grouped_model_rejects_wrong_model_type() -> None:
    with pytest.raises(
        TypeError,
        match="GaussianGazeErrorModel",
    ):
        uncertainty.GroupedGaussianGazeErrorModel(
            {
                "a": object(),
            }  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "value",
    [
        [],
        {},
    ],
)
def test_grouped_radial_constructor_requires_nonempty_mapping(
    value: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="non-empty mapping",
    ):
        uncertainty.GroupedGaussianGazeErrorModel.from_mean_radial_errors(
            value,  # type: ignore[arg-type]
            n_validation=2,
        )


def test_aoi_probabilities_requires_at_least_one_aoi() -> None:
    model = uncertainty.GaussianGazeErrorModel(
        np.zeros(2),
        np.eye(2),
        2,
    )

    with pytest.raises(
        ValueError,
        match="at least one AOI",
    ):
        uncertainty.aoi_probabilities(
            np.array(
                [
                    [0.0, 0.0],
                ]
            ),
            [],
            model,
        )


def test_aoi_probabilities_requires_unique_names() -> None:
    model = uncertainty.GaussianGazeErrorModel(
        np.zeros(2),
        np.eye(2),
        2,
    )
    aois = [
        RectangleAOI(
            "same",
            -1.0,
            -1.0,
            1.0,
            1.0,
        ),
        RectangleAOI(
            "same",
            -2.0,
            -2.0,
            2.0,
            2.0,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="AOI names must be unique",
    ):
        uncertainty.aoi_probabilities(
            np.array(
                [
                    [0.0, 0.0],
                ]
            ),
            aois,
            model,
        )


def test_aoi_probabilities_requires_supported_error_model() -> None:
    with pytest.raises(
        TypeError,
        match="error_model",
    ):
        uncertainty.aoi_probabilities(
            np.array(
                [
                    [0.0, 0.0],
                ]
            ),
            [
                RectangleAOI(
                    "target",
                    -1.0,
                    -1.0,
                    1.0,
                    1.0,
                )
            ],
            object(),  # type: ignore[arg-type]
        )


def test_grouped_draw_major_sampler_requires_positive_draws() -> None:
    model = uncertainty.GaussianGazeErrorModel(
        np.zeros(2),
        np.eye(2),
        2,
    )
    grouped = uncertainty.GroupedGaussianGazeErrorModel(
        {
            "a": model,
        }
    )

    with pytest.raises(
        ValueError,
        match="draws",
    ):
        uncertainty.sample_grouped_errors_draw_major(
            grouped,
            ["a"],
            n_observations=1,
            draws=0,
        )


def test_grouped_true_point_sampler_requires_positive_draws() -> None:
    model = uncertainty.GaussianGazeErrorModel(
        np.zeros(2),
        np.eye(2),
        2,
    )
    grouped = uncertainty.GroupedGaussianGazeErrorModel(
        {
            "a": model,
        }
    )

    with pytest.raises(
        ValueError,
        match="draws",
    ):
        uncertainty._sample_grouped_true_points(
            np.array(
                [
                    [0.0, 0.0],
                ]
            ),
            grouped,
            groups=["a"],
            draws=0,
            rng=1,
        )


def test_group_parameter_returns_shared_scalar() -> None:
    assert (
        uncertainty._group_parameter(
            9,
            "a",
            "n_validation",
        )
        == 9
    )


def test_missing_group_helper_fails_closed_if_pandas_check_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        uncertainty.pd,
        "isna",
        lambda _value: (_ for _ in ()).throw(
            TypeError("bad missingness object")
        ),
    )

    assert (
        uncertainty._is_missing_group(
            object()
        )
        is False
    )


def test_missing_group_helper_rejects_nonscalar_missingness_result() -> None:
    assert (
        uncertainty._is_missing_group(
            [1, 2]
        )
        is False
    )


@pytest.mark.parametrize(
    ("points", "message"),
    [
        (
            np.array(
                [
                    1.0,
                    2.0,
                ]
            ),
            "shape",
        ),
        (
            np.array(
                [
                    [np.inf, 0.0],
                ]
            ),
            "finite",
        ),
    ],
)
def test_uncertainty_point_guardrails(
    points: np.ndarray,
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        uncertainty._as_points(points)


# ---------------------------------------------------------------------------
# Last pymovements duration-conversion path
# ---------------------------------------------------------------------------


def test_pymovements_object_duration_values_convert_to_milliseconds() -> None:
    values = pd.Series(
        [
            "0 days 00:00:00.001",
            "0 days 00:00:00.002",
        ],
        dtype="object",
    )

    converted = pymovements_adapter._time_to_milliseconds(
        values,
        "ms",
    )

    np.testing.assert_allclose(
        converted,
        [
            1.0,
            2.0,
        ],
    )


# ---------------------------------------------------------------------------
# Study QC verification and artifact guardrails
# ---------------------------------------------------------------------------


def test_qc_diagnostics_requires_gaze_study() -> None:
    with pytest.raises(
        TypeError,
        match="GazeStudy",
    ):
        study_qc.study_qc_diagnostics(
            pd.DataFrame()  # type: ignore[arg-type]
        )


def test_qc_audit_builder_requires_gaze_study() -> None:
    with pytest.raises(
        TypeError,
        match="GazeStudy",
    ):
        study_qc.build_study_qc_audit(
            pd.DataFrame()  # type: ignore[arg-type]
        )


def test_qc_manifest_verifier_rejects_wrong_schema() -> None:
    manifest = copy.deepcopy(
        _qc_audit().manifest
    )
    manifest["schema"] = "wrong-schema"

    assert not study_qc.verify_study_qc_manifest(
        manifest
    )


def test_qc_manifest_verifier_detects_study_fingerprint_change() -> None:
    manifest = copy.deepcopy(
        _qc_audit().manifest
    )
    manifest["study"]["n_rows"] = 999

    assert not study_qc.verify_study_qc_manifest(
        manifest
    )


def test_qc_manifest_verifier_detects_audit_fingerprint_change() -> None:
    manifest = copy.deepcopy(
        _qc_audit().manifest
    )
    manifest["report"]["n_rows"] = 999

    assert not study_qc.verify_study_qc_manifest(
        manifest
    )


def test_qc_manifest_verifier_fails_closed_on_missing_fields() -> None:
    assert not study_qc.verify_study_qc_manifest(
        {
            "schema": study_qc.STUDY_QC_SCHEMA,
        }
    )


def test_qc_audit_verifier_requires_audit_type() -> None:
    with pytest.raises(
        TypeError,
        match="StudyQCAudit",
    ):
        study_qc.verify_study_qc_audit(
            object()  # type: ignore[arg-type]
        )


def test_qc_audit_verifier_requires_software_mapping() -> None:
    audit = _qc_audit()
    audit.manifest["software"] = []

    assert not study_qc.verify_study_qc_audit(
        audit
    )


def test_qc_audit_verifier_fails_closed_on_invalid_decision_payload() -> None:
    valid = _qc_audit()
    invalid = study_qc.StudyQCAudit(
        report=valid.report,
        diagnostics=valid.diagnostics,
        decisions=(
            object(),  # type: ignore[arg-type]
        ),
        study_descriptor=valid.study_descriptor,
        manifest=valid.manifest,
    )

    assert not study_qc.verify_study_qc_audit(
        invalid
    )


def test_qc_publication_metadata_requires_audit_type() -> None:
    with pytest.raises(
        TypeError,
        match="StudyQCAudit",
    ):
        study_qc.study_qc_publication_metadata(
            object()  # type: ignore[arg-type]
        )


def test_qc_artifact_writer_requires_audit_type(
    tmp_path,
) -> None:
    with pytest.raises(
        TypeError,
        match="StudyQCAudit",
    ):
        study_qc.write_study_qc_artifacts(
            object(),  # type: ignore[arg-type]
            tmp_path,
        )


def test_qc_artifact_writer_rejects_invalid_audit(
    tmp_path,
) -> None:
    audit = _qc_audit()
    audit.manifest["report"]["n_rows"] = 999

    with pytest.raises(
        ValueError,
        match="does not match its manifest",
    ):
        study_qc.write_study_qc_artifacts(
            audit,
            tmp_path,
        )


def test_qc_artifact_verifier_requires_manifest_file(
    tmp_path,
) -> None:
    assert not study_qc.verify_study_qc_artifacts(
        tmp_path
    )


def test_qc_artifact_verifier_rejects_wrong_schema(
    tmp_path,
) -> None:
    paths = study_qc.write_study_qc_artifacts(
        _qc_audit(),
        tmp_path,
    )
    manifest_path = paths[
        "study_qc_artifacts.json"
    ]
    document = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )
    document["schema"] = "wrong-schema"
    manifest_path.write_text(
        json.dumps(document),
        encoding="utf-8",
    )

    assert not study_qc.verify_study_qc_artifacts(
        tmp_path
    )


def test_qc_artifact_verifier_detects_manifest_fingerprint_change(
    tmp_path,
) -> None:
    paths = study_qc.write_study_qc_artifacts(
        _qc_audit(),
        tmp_path,
    )
    manifest_path = paths[
        "study_qc_artifacts.json"
    ]
    document = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )
    document["artifact_fingerprint"] = "0" * 64
    manifest_path.write_text(
        json.dumps(document),
        encoding="utf-8",
    )

    assert not study_qc.verify_study_qc_artifacts(
        tmp_path
    )


def test_qc_artifact_verifier_requires_exact_file_set(
    tmp_path,
) -> None:
    paths = study_qc.write_study_qc_artifacts(
        _qc_audit(),
        tmp_path,
    )
    manifest_path = paths[
        "study_qc_artifacts.json"
    ]

    _rewrite_artifact_manifest(
        manifest_path,
        lambda document: document["files"].pop(
            "study_qc_report.json"
        ),
    )

    assert not study_qc.verify_study_qc_artifacts(
        tmp_path
    )


def test_qc_artifact_verifier_requires_each_payload_file(
    tmp_path,
) -> None:
    paths = study_qc.write_study_qc_artifacts(
        _qc_audit(),
        tmp_path,
    )
    paths[
        "study_qc_diagnostics.csv"
    ].unlink()

    assert not study_qc.verify_study_qc_artifacts(
        tmp_path
    )


def test_qc_artifact_verifier_checks_payload_size(
    tmp_path,
) -> None:
    paths = study_qc.write_study_qc_artifacts(
        _qc_audit(),
        tmp_path,
    )
    manifest_path = paths[
        "study_qc_artifacts.json"
    ]

    def mutate(
        document: dict[str, object],
    ) -> None:
        files = document["files"]
        files["study_qc_report.json"]["bytes"] += 1

    _rewrite_artifact_manifest(
        manifest_path,
        mutate,
    )

    assert not study_qc.verify_study_qc_artifacts(
        tmp_path
    )


def test_qc_artifact_verifier_checks_payload_hash(
    tmp_path,
) -> None:
    paths = study_qc.write_study_qc_artifacts(
        _qc_audit(),
        tmp_path,
    )
    target = paths[
        "study_qc_report.json"
    ]
    payload = target.read_text(
        encoding="utf-8"
    )
    replacement = (
        "["
        + payload[1:]
        if payload.startswith("{")
        else "X"
        + payload[1:]
    )
    target.write_bytes(
        replacement.encode("utf-8")
    )

    assert len(
        target.read_bytes()
    ) == len(
        payload.encode("utf-8")
    )
    assert not study_qc.verify_study_qc_artifacts(
        tmp_path
    )


def test_qc_artifact_verifier_fails_closed_on_invalid_json(
    tmp_path,
) -> None:
    manifest = (
        tmp_path
        / "study_qc_artifacts.json"
    )
    manifest.write_text(
        "{",
        encoding="utf-8",
    )

    assert not study_qc.verify_study_qc_artifacts(
        tmp_path
    )


def test_qc_table_descriptor_requires_dataframe() -> None:
    with pytest.raises(
        TypeError,
        match="pandas DataFrame",
    ):
        study_qc._qc_table_descriptor(
            object()  # type: ignore[arg-type]
        )


def test_qc_decision_validator_requires_decision_objects() -> None:
    audit = _qc_audit()

    with pytest.raises(
        TypeError,
        match="StudyQCDecision",
    ):
        study_qc._validate_decisions(
            audit.report,
            audit.diagnostics,
            (
                object(),  # type: ignore[arg-type]
            ),
        )


def test_qc_normalization_handles_negative_infinity() -> None:
    assert study_qc._qc_normalize(
        -np.inf
    ) == {
        "__gazeaudit_nonfinite__": "negative_infinity",
    }


def test_qc_normalization_handles_timestamp() -> None:
    timestamp = pd.Timestamp(
        "2026-09-21T12:00:00"
    )

    assert study_qc._qc_normalize(
        timestamp
    ) == timestamp.isoformat()


def test_qc_normalization_handles_ndarray() -> None:
    assert study_qc._qc_normalize(
        np.array(
            [
                1,
                2,
            ]
        )
    ) == [
        1,
        2,
    ]


def test_qc_normalization_handles_missing_scalar() -> None:
    assert study_qc._qc_normalize(
        pd.NA
    ) is None


def test_qc_normalization_rejects_unsupported_object() -> None:
    with pytest.raises(
        TypeError,
        match="unsupported study QC provenance type",
    ):
        study_qc._qc_normalize(
            object()
        )
