from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import pytest

import gazeaudit.aoi_propagation as propagation
import gazeaudit.aoi_protocol as protocol
from gazeaudit.aoi import RectangleAOI
from gazeaudit.uncertainty import (
    GaussianGazeErrorModel,
    GroupedGaussianGazeErrorModel,
)


# ======================================================================
# AOI protocol helpers
# ======================================================================


def _protocol_inputs() -> dict[str, object]:
    return {
        "case_study_id": "  study-001  ",
        "dataset": {
            "name": "dataset",
            "version": "1",
        },
        "validation": {
            "name": "validation",
            "n": 20,
        },
        "aoi": {
            "name": "target",
            "geometry": "rectangle",
        },
        "endpoint": {
            "name": "condition dwell contrast",
            "units": "ms",
        },
        "error_model": {
            "name": "bivariate Gaussian",
            "bias": [0.0, 0.0],
        },
        "monte_carlo": {
            "draws": 100,
            "batch_size": 20,
            "interval": 0.95,
            "reference": 0.0,
            "rng_seed": 123,
        },
        "interpretation": {
            "rule": "predeclared",
        },
    }


def _valid_protocol() -> dict[str, object]:
    return protocol.build_aoi_uncertainty_protocol(
        **_protocol_inputs()
    )


def _rehash(
    document: dict[str, object],
) -> dict[str, object]:
    copied = copy.deepcopy(document)

    core = dict(copied)
    core.pop(
        "protocol_fingerprint",
        None,
    )

    copied["protocol_fingerprint"] = protocol.fingerprint(
        core
    )

    return copied


# ======================================================================
# aoi_protocol.py — successful construction
# ======================================================================


def test_protocol_build_is_deterministic_and_verifiable() -> None:
    first = _valid_protocol()
    second = _valid_protocol()

    assert first == second

    assert first["schema"] == (
        protocol.AOI_UNCERTAINTY_PROTOCOL_SCHEMA
    )

    assert first["case_study_id"] == "study-001"

    assert isinstance(
        first["protocol_fingerprint"],
        str,
    )

    assert len(
        first["protocol_fingerprint"]
    ) == 64

    assert protocol.verify_aoi_uncertainty_protocol(
        first
    )


def test_protocol_fingerprint_changes_with_scientific_contract() -> None:
    first = _valid_protocol()

    inputs = _protocol_inputs()

    monte_carlo = dict(
        inputs["monte_carlo"]  # type: ignore[arg-type]
    )

    monte_carlo["draws"] = 200

    inputs["monte_carlo"] = monte_carlo

    second = protocol.build_aoi_uncertainty_protocol(
        **inputs
    )

    assert (
        first["protocol_fingerprint"]
        != second["protocol_fingerprint"]
    )


# ======================================================================
# aoi_protocol.py — builder validation
# ======================================================================


def test_protocol_requires_nonempty_case_study_id() -> None:
    inputs = _protocol_inputs()
    inputs["case_study_id"] = "   "

    with pytest.raises(
        ValueError,
        match="case_study_id",
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "field",
    [
        "dataset",
        "validation",
        "aoi",
        "endpoint",
        "error_model",
        "monte_carlo",
        "interpretation",
    ],
)
def test_protocol_mapping_fields_must_be_mappings(
    field: str,
) -> None:
    inputs = _protocol_inputs()
    inputs[field] = ["invalid"]

    with pytest.raises(
        TypeError,
        match=field,
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "field",
    [
        "dataset",
        "validation",
        "aoi",
        "endpoint",
        "error_model",
        "monte_carlo",
        "interpretation",
    ],
)
def test_protocol_mapping_fields_must_be_nonempty(
    field: str,
) -> None:
    inputs = _protocol_inputs()
    inputs[field] = {}

    with pytest.raises(
        ValueError,
        match=field,
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "field",
    [
        "dataset",
        "validation",
        "aoi",
        "endpoint",
    ],
)
@pytest.mark.parametrize(
    "label",
    [
        None,
        "",
        "   ",
        123,
    ],
)
def test_protocol_identity_fields_require_nonempty_name(
    field: str,
    label: object,
) -> None:
    inputs = _protocol_inputs()

    value = dict(
        inputs[field]  # type: ignore[arg-type]
    )

    value["name"] = label
    inputs[field] = value

    with pytest.raises(
        ValueError,
        match=field,
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


def test_canonical_mapping_rejects_normalized_nonobject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        protocol,
        "canonical_json",
        lambda value: "[]",
    )

    with pytest.raises(
        TypeError,
        match="must normalize to an object",
    ):
        protocol._canonical_mapping(
            {
                "name": "demo",
            },
            name="demo",
        )


# ======================================================================
# aoi_protocol.py — Monte Carlo validation
# ======================================================================


def test_protocol_requires_all_monte_carlo_fields() -> None:
    inputs = _protocol_inputs()

    mc = dict(
        inputs["monte_carlo"]  # type: ignore[arg-type]
    )

    mc.pop("rng_seed")
    inputs["monte_carlo"] = mc

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "value",
    [
        True,
        1.5,
        1,
    ],
)
def test_protocol_draws_requires_integer_at_least_two(
    value: object,
) -> None:
    inputs = _protocol_inputs()

    mc = dict(
        inputs["monte_carlo"]  # type: ignore[arg-type]
    )

    mc["draws"] = value
    inputs["monte_carlo"] = mc

    with pytest.raises(
        ValueError,
        match="draws",
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "value",
    [
        True,
        1.5,
        0,
    ],
)
def test_protocol_batch_size_requires_positive_integer(
    value: object,
) -> None:
    inputs = _protocol_inputs()

    mc = dict(
        inputs["monte_carlo"]  # type: ignore[arg-type]
    )

    mc["batch_size"] = value
    inputs["monte_carlo"] = mc

    with pytest.raises(
        ValueError,
        match="batch_size",
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "value",
    [
        True,
        1.5,
    ],
)
def test_protocol_rng_seed_requires_integer(
    value: object,
) -> None:
    inputs = _protocol_inputs()

    mc = dict(
        inputs["monte_carlo"]  # type: ignore[arg-type]
    )

    mc["rng_seed"] = value
    inputs["monte_carlo"] = mc

    with pytest.raises(
        ValueError,
        match="rng_seed",
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "value",
    [
        0.0,
        1.0,
        -0.1,
        1.1,
    ],
)
def test_protocol_interval_requires_open_unit_interval(
    value: float,
) -> None:
    inputs = _protocol_inputs()

    mc = dict(
        inputs["monte_carlo"]  # type: ignore[arg-type]
    )

    mc["interval"] = value
    inputs["monte_carlo"] = mc

    with pytest.raises(
        ValueError,
        match="strictly between 0 and 1",
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "value",
    [
        True,
        "not-numeric",
    ],
)
def test_protocol_interval_requires_numeric(
    value: object,
) -> None:
    inputs = _protocol_inputs()

    mc = dict(
        inputs["monte_carlo"]  # type: ignore[arg-type]
    )

    mc["interval"] = value
    inputs["monte_carlo"] = mc

    with pytest.raises(
        TypeError,
        match="interval.*numeric",
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_protocol_interval_requires_finite_value(
    value: float,
) -> None:
    inputs = _protocol_inputs()

    mc = dict(
        inputs["monte_carlo"]  # type: ignore[arg-type]
    )

    mc["interval"] = value
    inputs["monte_carlo"] = mc

    with pytest.raises(
        ValueError,
        match="finite",
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "value",
    [
        True,
        "bad",
    ],
)
def test_protocol_reference_requires_numeric(
    value: object,
) -> None:
    inputs = _protocol_inputs()

    mc = dict(
        inputs["monte_carlo"]  # type: ignore[arg-type]
    )

    mc["reference"] = value
    inputs["monte_carlo"] = mc

    with pytest.raises(
        TypeError,
        match="reference.*numeric",
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


@pytest.mark.parametrize(
    "value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_protocol_reference_requires_finite_value(
    value: float,
) -> None:
    inputs = _protocol_inputs()

    mc = dict(
        inputs["monte_carlo"]  # type: ignore[arg-type]
    )

    mc["reference"] = value
    inputs["monte_carlo"] = mc

    with pytest.raises(
        ValueError,
        match="reference.*finite",
    ):
        protocol.build_aoi_uncertainty_protocol(
            **inputs
        )


def test_finite_float_accepts_numeric_string() -> None:
    assert protocol._finite_float(
        "0.75",
        name="demo",
    ) == pytest.approx(0.75)


# ======================================================================
# aoi_protocol.py — verification guardrails
# ======================================================================


def test_protocol_verify_rejects_nonmapping() -> None:
    assert not protocol.verify_aoi_uncertainty_protocol(
        []  # type: ignore[arg-type]
    )


def test_protocol_verify_rejects_wrong_schema() -> None:
    document = _valid_protocol()
    document["schema"] = "wrong-schema"

    assert not protocol.verify_aoi_uncertainty_protocol(
        document
    )


@pytest.mark.parametrize(
    "fingerprint",
    [
        123,
        "short",
    ],
)
def test_protocol_verify_rejects_invalid_fingerprint_shape(
    fingerprint: object,
) -> None:
    document = _valid_protocol()

    document["protocol_fingerprint"] = fingerprint

    assert not protocol.verify_aoi_uncertainty_protocol(
        document
    )


def test_protocol_verify_detects_tampering() -> None:
    document = _valid_protocol()

    dataset = dict(
        document["dataset"]  # type: ignore[arg-type]
    )

    dataset["version"] = "tampered"
    document["dataset"] = dataset

    assert not protocol.verify_aoi_uncertainty_protocol(
        document
    )


def test_protocol_verify_rejects_empty_case_id_even_if_rehashed() -> None:
    document = _valid_protocol()
    document["case_study_id"] = "   "

    assert not protocol.verify_aoi_uncertainty_protocol(
        _rehash(document)
    )


@pytest.mark.parametrize(
    "field",
    [
        "dataset",
        "validation",
        "aoi",
        "endpoint",
        "error_model",
        "monte_carlo",
        "interpretation",
    ],
)
@pytest.mark.parametrize(
    "bad_value",
    [
        [],
        {},
    ],
)
def test_protocol_verify_rejects_invalid_core_mapping(
    field: str,
    bad_value: object,
) -> None:
    document = _valid_protocol()
    document[field] = bad_value

    assert not protocol.verify_aoi_uncertainty_protocol(
        _rehash(document)
    )


def test_protocol_verify_fails_closed_on_invalid_identity() -> None:
    document = _valid_protocol()

    dataset = dict(
        document["dataset"]  # type: ignore[arg-type]
    )

    dataset["name"] = "   "
    document["dataset"] = dataset

    assert not protocol.verify_aoi_uncertainty_protocol(
        _rehash(document)
    )


def test_protocol_verify_fails_closed_on_invalid_monte_carlo() -> None:
    document = _valid_protocol()

    mc = dict(
        document["monte_carlo"]  # type: ignore[arg-type]
    )

    mc["draws"] = 1
    document["monte_carlo"] = mc

    assert not protocol.verify_aoi_uncertainty_protocol(
        _rehash(document)
    )


def test_protocol_verify_fails_closed_on_json_decode_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = _valid_protocol()

    monkeypatch.setattr(
        protocol,
        "canonical_json",
        lambda value: "{",
    )

    assert not protocol.verify_aoi_uncertainty_protocol(
        document
    )


# ======================================================================
# AOI propagation helpers
# ======================================================================


def _data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "participant": [
                "p1",
                "p1",
                "p2",
                "p2",
            ],
            "condition": [
                "control",
                "treatment",
                "control",
                "treatment",
            ],
            "duration": [
                100.0,
                100.0,
                100.0,
                100.0,
            ],
            "observed_x": [
                -2.0,
                2.0,
                -3.0,
                3.0,
            ],
            "observed_y": [
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            "error_group": [
                "A",
                "A",
                "B",
                "B",
            ],
        }
    )


def _aoi() -> RectangleAOI:
    return RectangleAOI(
        "right",
        0.0,
        -10.0,
        10.0,
        10.0,
    )


def _zero_model() -> GaussianGazeErrorModel:
    return GaussianGazeErrorModel(
        mean_error=np.zeros(2),
        covariance=np.zeros(
            (
                2,
                2,
            )
        ),
        n_validation=2,
    )


def _grouped_model() -> GroupedGaussianGazeErrorModel:
    return GroupedGaussianGazeErrorModel(
        {
            "A": _zero_model(),
            "B": GaussianGazeErrorModel(
                mean_error=np.array(
                    [
                        1.0,
                        0.0,
                    ]
                ),
                covariance=np.zeros(
                    (
                        2,
                        2,
                    )
                ),
                n_validation=2,
            ),
        }
    )


def _mean_membership_endpoint(
    frame: pd.DataFrame,
    membership: np.ndarray,
) -> float:
    assert len(frame) == len(membership)
    return float(
        np.mean(
            membership
        )
    )


# ======================================================================
# aoi_propagation.py — successful paths
# ======================================================================


def test_global_model_audit_accepts_generator_rng() -> None:
    generator = np.random.default_rng(
        123
    )

    audit = propagation.audit_aoi_effect_uncertainty(
        _data(),
        _aoi(),
        _zero_model(),
        _mean_membership_endpoint,
        draws=3,
        batch_size=2,
        interval=0.80,
        reference=0.5,
        rng=generator,
    )

    assert audit.aoi == "right"

    assert audit.summary[
        "hard_effect"
    ] == pytest.approx(0.5)

    assert audit.summary[
        "expected_membership_effect"
    ] == pytest.approx(0.5)

    assert audit.summary[
        "probability_equal_reference"
    ] == pytest.approx(1.0)

    assert audit.summary[
        "probability_above_reference"
    ] == pytest.approx(0.0)

    assert audit.summary[
        "probability_below_reference"
    ] == pytest.approx(0.0)

    assert len(audit.draw_effects) == 3


def test_grouped_model_audit_uses_declared_column_groups() -> None:
    audit = propagation.audit_aoi_effect_uncertainty(
        _data(),
        _aoi(),
        _grouped_model(),
        _mean_membership_endpoint,
        error_group="error_group",
        draws=3,
        batch_size=2,
        rng=42,
    )

    assert len(audit.draw_effects) == 3
    assert len(audit.membership_probabilities) == 4

    assert np.isfinite(
        audit.draw_effects[
            "estimate"
        ].to_numpy()
    ).all()


def test_grouped_model_audit_supports_explicit_group_sequence() -> None:
    groups = [
        "A",
        "A",
        "B",
        "B",
    ]

    audit = propagation.audit_aoi_effect_uncertainty(
        _data(),
        _aoi(),
        _grouped_model(),
        _mean_membership_endpoint,
        error_group=groups,
        draws=2,
        batch_size=1,
        rng=7,
    )

    assert len(audit.draw_effects) == 2


# ======================================================================
# aoi_propagation.py — public argument guardrails
# ======================================================================


def test_audit_requires_dataframe() -> None:
    with pytest.raises(
        TypeError,
        match="pandas DataFrame",
    ):
        propagation.audit_aoi_effect_uncertainty(
            [],  # type: ignore[arg-type]
            _aoi(),
            _zero_model(),
            _mean_membership_endpoint,
        )


def test_audit_requires_supported_error_model() -> None:
    with pytest.raises(
        TypeError,
        match="error_model",
    ):
        propagation.audit_aoi_effect_uncertainty(
            _data(),
            _aoi(),
            object(),  # type: ignore[arg-type]
            _mean_membership_endpoint,
        )


def test_audit_requires_callable_endpoint() -> None:
    with pytest.raises(
        TypeError,
        match="endpoint must be callable",
    ):
        propagation.audit_aoi_effect_uncertainty(
            _data(),
            _aoi(),
            _zero_model(),
            None,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "draws",
    [
        0,
        1,
    ],
)
def test_audit_requires_at_least_two_draws(
    draws: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="draws",
    ):
        propagation.audit_aoi_effect_uncertainty(
            _data(),
            _aoi(),
            _zero_model(),
            _mean_membership_endpoint,
            draws=draws,
        )


def test_audit_requires_positive_batch_size() -> None:
    with pytest.raises(
        ValueError,
        match="batch_size",
    ):
        propagation.audit_aoi_effect_uncertainty(
            _data(),
            _aoi(),
            _zero_model(),
            _mean_membership_endpoint,
            batch_size=0,
        )


@pytest.mark.parametrize(
    "interval",
    [
        0.0,
        1.0,
        -0.1,
        1.1,
    ],
)
def test_audit_requires_open_interval(
    interval: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="interval",
    ):
        propagation.audit_aoi_effect_uncertainty(
            _data(),
            _aoi(),
            _zero_model(),
            _mean_membership_endpoint,
            interval=interval,
        )


@pytest.mark.parametrize(
    "reference",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_audit_requires_finite_reference(
    reference: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="reference",
    ):
        propagation.audit_aoi_effect_uncertainty(
            _data(),
            _aoi(),
            _zero_model(),
            _mean_membership_endpoint,
            reference=reference,
        )


def test_audit_requires_both_observed_coordinate_columns() -> None:
    with pytest.raises(
        ValueError,
        match="observed gaze columns",
    ):
        propagation.audit_aoi_effect_uncertainty(
            _data().drop(
                columns=[
                    "observed_y",
                ]
            ),
            _aoi(),
            _zero_model(),
            _mean_membership_endpoint,
        )


def test_audit_requires_nonempty_data() -> None:
    frame = pd.DataFrame(
        columns=[
            "observed_x",
            "observed_y",
        ]
    )

    with pytest.raises(
        ValueError,
        match="at least one observation",
    ):
        propagation.audit_aoi_effect_uncertainty(
            frame,
            _aoi(),
            _zero_model(),
            _mean_membership_endpoint,
        )


@pytest.mark.parametrize(
    "value",
    [
        np.nan,
        np.inf,
        "not-numeric",
    ],
)
def test_audit_requires_finite_complete_coordinates(
    value: object,
) -> None:
    frame = _data()
    frame.loc[
        0,
        "observed_x",
    ] = value

    with pytest.raises(
        ValueError,
        match="finite and complete",
    ):
        propagation.audit_aoi_effect_uncertainty(
            frame,
            _aoi(),
            _zero_model(),
            _mean_membership_endpoint,
        )


# ======================================================================
# grouped-error routing
# ======================================================================


def test_resolve_error_groups_ignores_group_for_global_model() -> None:
    result = propagation._resolve_error_groups(
        _data(),
        _zero_model(),
        "does-not-exist",
    )

    assert result is None


def test_grouped_error_model_requires_error_group() -> None:
    with pytest.raises(
        ValueError,
        match="error_group is required",
    ):
        propagation._resolve_error_groups(
            _data(),
            _grouped_model(),
            None,
        )


def test_grouped_error_group_column_must_exist() -> None:
    with pytest.raises(
        ValueError,
        match="not present",
    ):
        propagation._resolve_error_groups(
            _data(),
            _grouped_model(),
            "missing-column",
        )


def test_grouped_error_group_column_is_resolved() -> None:
    values = propagation._resolve_error_groups(
        _data(),
        _grouped_model(),
        "error_group",
    )

    assert values is not None

    assert values.tolist() == [
        "A",
        "A",
        "B",
        "B",
    ]


def test_grouped_error_explicit_sequence_is_resolved() -> None:
    values = propagation._resolve_error_groups(
        _data(),
        _grouped_model(),
        [
            "A",
            "A",
            "B",
            "B",
        ],
    )

    assert values is not None
    assert values.tolist() == [
        "A",
        "A",
        "B",
        "B",
    ]


def test_grouped_error_sequence_length_must_match() -> None:
    with pytest.raises(
        ValueError,
        match="match observations",
    ):
        propagation._resolve_error_groups(
            _data(),
            _grouped_model(),
            [
                "A",
            ],
        )


def test_grouped_error_unknown_group_fails_closed() -> None:
    with pytest.raises(
        ValueError,
        match="unmapped error-model group",
    ):
        propagation._resolve_error_groups(
            _data(),
            _grouped_model(),
            [
                "A",
                "A",
                "B",
                "UNKNOWN",
            ],
        )


# ======================================================================
# endpoint return-contract guardrails
# ======================================================================


def test_endpoint_value_accepts_numeric_scalar() -> None:
    assert propagation._endpoint_value(
        lambda frame, membership: np.float64(1.25),
        _data(),
        np.ones(
            len(_data())
        ),
    ) == pytest.approx(1.25)


def test_endpoint_value_rejects_nonscalar() -> None:
    with pytest.raises(
        TypeError,
        match="scalar",
    ):
        propagation._endpoint_value(
            lambda frame, membership: np.array(
                [
                    1.0,
                    2.0,
                ]
            ),
            _data(),
            np.ones(
                len(_data())
            ),
        )


def test_endpoint_value_rejects_nonnumeric_scalar() -> None:
    with pytest.raises(
        TypeError,
        match="numeric scalar",
    ):
        propagation._endpoint_value(
            lambda frame, membership: "not-numeric",
            _data(),
            np.ones(
                len(_data())
            ),
        )


@pytest.mark.parametrize(
    "value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_endpoint_value_rejects_nonfinite_scalar(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="finite scalar",
    ):
        propagation._endpoint_value(
            lambda frame, membership: value,
            _data(),
            np.ones(
                len(_data())
            ),
        )


# ======================================================================
# AOI membership guardrails
# ======================================================================


def test_validate_membership_accepts_valid_vector() -> None:
    propagation._validate_membership(
        np.array(
            [
                0.0,
                0.5,
                1.0,
            ]
        ),
        3,
        label="demo",
    )


def test_validate_membership_rejects_wrong_dimensions() -> None:
    with pytest.raises(
        ValueError,
        match="one-dimensional",
    ):
        propagation._validate_membership(
            np.ones(
                (
                    3,
                    1,
                )
            ),
            3,
            label="demo",
        )


def test_validate_membership_rejects_wrong_length() -> None:
    with pytest.raises(
        ValueError,
        match="match data rows",
    ):
        propagation._validate_membership(
            np.ones(2),
            3,
            label="demo",
        )


@pytest.mark.parametrize(
    "values",
    [
        np.array(
            [
                0.0,
                np.nan,
            ]
        ),
        np.array(
            [
                -0.1,
                0.5,
            ]
        ),
        np.array(
            [
                0.5,
                1.1,
            ]
        ),
    ],
)
def test_validate_membership_rejects_invalid_values(
    values: np.ndarray,
) -> None:
    with pytest.raises(
        ValueError,
        match="finite values between 0 and 1",
    ):
        propagation._validate_membership(
            values,
            2,
            label="demo",
        )


class WrongShapeAOI:
    name = "wrong-shape"

    def contains_points(
        self,
        points: np.ndarray,
    ) -> np.ndarray:
        return np.ones(
            (
                len(points),
                1,
            )
        )


def test_audit_validates_hard_membership_shape() -> None:
    with pytest.raises(
        ValueError,
        match="hard AOI membership",
    ):
        propagation.audit_aoi_effect_uncertainty(
            _data(),
            WrongShapeAOI(),  # type: ignore[arg-type]
            _zero_model(),
            _mean_membership_endpoint,
            draws=2,
        )


class InvalidSampleMembershipAOI:
    name = "stateful"

    def __init__(self) -> None:
        self.calls = 0

    def contains_points(
        self,
        points: np.ndarray,
    ) -> np.ndarray:
        self.calls += 1

        if self.calls == 1:
            return np.zeros(
                len(points),
                dtype=float,
            )

        return np.full(
            len(points),
            2.0,
            dtype=float,
        )


def test_audit_validates_sampled_membership_values() -> None:
    with pytest.raises(
        ValueError,
        match="sampled AOI membership",
    ):
        propagation.audit_aoi_effect_uncertainty(
            _data(),
            InvalidSampleMembershipAOI(),  # type: ignore[arg-type]
            _zero_model(),
            _mean_membership_endpoint,
            draws=2,
            batch_size=1,
            rng=1,
        )


# ======================================================================
# RNG helper
# ======================================================================


def test_as_rng_preserves_existing_generator() -> None:
    generator = np.random.default_rng(
        5
    )

    assert propagation._as_rng(
        generator
    ) is generator


def test_as_rng_builds_generator_from_seed() -> None:
    first = propagation._as_rng(
        99
    )

    second = propagation._as_rng(
        99
    )

    np.testing.assert_array_equal(
        first.integers(
            0,
            100,
            size=10,
        ),
        second.integers(
            0,
            100,
            size=10,
        ),
    )