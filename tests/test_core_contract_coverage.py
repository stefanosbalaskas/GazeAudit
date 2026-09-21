from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest

from gazeaudit.adapters import (
    DetectionResult,
    adapt_study,
    run_detector_backend,
)
from gazeaudit.aoi import CircleAOI, RectangleAOI
from gazeaudit.benchmark import (
    evaluate_aoi_recovery,
    fit_error_model_from_known_truth,
    simulate_boundary_data,
)
from gazeaudit.endpoints import (
    expected_dwell,
    expected_fixation_count,
)
from gazeaudit.multiverse import PipelineSpace, run_specs
from gazeaudit.study import GazeStudy
from gazeaudit.uncertainty import GaussianGazeErrorModel


def _study() -> GazeStudy:
    return GazeStudy(
        pd.DataFrame(
            {
                "participant": ["p1", "p1", "p2", "p2"],
                "trial": [1, 1, 1, 1],
                "timestamp": [0.0, 10.0, 0.0, 10.0],
                "x": [0.0, 1.0, 2.0, 3.0],
                "y": [0.0, 0.0, 0.0, 0.0],
                "extra": ["a", "b", "c", "d"],
            }
        )
    )


# ----------------------------------------------------------------------
# adapters.py
# ----------------------------------------------------------------------


def test_detection_result_accepts_valid_contract() -> None:
    result = DetectionResult(
        samples=pd.DataFrame(
            {
                "event_label": ["fixation"],
            }
        ),
        metadata=pd.DataFrame(
            {
                "source": ["test"],
            }
        ),
        backend="backend",
        detector="detector",
    )

    assert result.backend == "backend"
    assert result.detector == "detector"


@pytest.mark.parametrize(
    ("samples", "metadata", "backend", "detector", "message"),
    [
        (
            [],
            pd.DataFrame(),
            "backend",
            "detector",
            "samples must be a pandas DataFrame",
        ),
        (
            pd.DataFrame({"event_label": ["fixation"]}),
            [],
            "backend",
            "detector",
            "metadata must be a pandas DataFrame",
        ),
        (
            pd.DataFrame({"event_label": []}),
            pd.DataFrame(),
            "backend",
            "detector",
            "at least one row",
        ),
        (
            pd.DataFrame({"x": [1.0]}),
            pd.DataFrame(),
            "backend",
            "detector",
            "event_label",
        ),
        (
            pd.DataFrame({"event_label": ["fixation"]}),
            pd.DataFrame(),
            "",
            "detector",
            "backend must be",
        ),
        (
            pd.DataFrame({"event_label": ["fixation"]}),
            pd.DataFrame(),
            "backend",
            "",
            "detector must be",
        ),
    ],
)
def test_detection_result_rejects_invalid_contracts(
    samples: object,
    metadata: object,
    backend: str,
    detector: str,
    message: str,
) -> None:
    with pytest.raises(
        (TypeError, ValueError),
        match=message,
    ):
        DetectionResult(
            samples=samples,  # type: ignore[arg-type]
            metadata=metadata,  # type: ignore[arg-type]
            backend=backend,
            detector=detector,
        )


def test_adapt_study_contract_success_and_failures() -> None:
    study = _study()

    class Adapter:
        name = "valid"

        def to_study(self, source: object) -> GazeStudy:
            assert source == "source"
            return study

    assert adapt_study("source", Adapter()) is study

    with pytest.raises(
        TypeError,
        match="StudyAdapter",
    ):
        adapt_study(
            "source",
            object(),  # type: ignore[arg-type]
        )

    class WrongReturn:
        name = "wrong"

        def to_study(self, source: object) -> str:
            return "not-a-study"

    with pytest.raises(
        TypeError,
        match="must return a GazeStudy",
    ):
        adapt_study(
            "source",
            WrongReturn(),  # type: ignore[arg-type]
        )


def test_detector_backend_contract_success_and_failures() -> None:
    study = _study()

    expected = DetectionResult(
        samples=pd.DataFrame(
            {
                "event_label": ["fixation"],
            }
        ),
        metadata=pd.DataFrame(),
        backend="demo",
        detector="constant",
    )

    class Backend:
        name = "demo"

        def detect(self, source: GazeStudy) -> DetectionResult:
            assert source is study
            return expected

    assert run_detector_backend(study, Backend()) is expected

    with pytest.raises(
        TypeError,
        match="study must be",
    ):
        run_detector_backend(
            "not-study",  # type: ignore[arg-type]
            Backend(),
        )

    with pytest.raises(
        TypeError,
        match="DetectorBackend",
    ):
        run_detector_backend(
            study,
            object(),  # type: ignore[arg-type]
        )

    class WrongResult:
        name = "wrong"

        def detect(self, source: GazeStudy) -> str:
            return "not-detection-result"

    with pytest.raises(
        TypeError,
        match="must return a DetectionResult",
    ):
        run_detector_backend(
            study,
            WrongResult(),  # type: ignore[arg-type]
        )


# ----------------------------------------------------------------------
# aoi.py
# ----------------------------------------------------------------------


def test_rectangle_and_circle_membership_include_boundaries() -> None:
    points = np.array(
        [
            [-1.0, -1.0],
            [0.0, 0.0],
            [1.0, 1.0],
            [2.0, 0.0],
        ]
    )

    rectangle = RectangleAOI(
        "rect",
        -1.0,
        -1.0,
        1.0,
        1.0,
    )

    circle = CircleAOI(
        "circle",
        0.0,
        0.0,
        1.0,
    )

    assert rectangle.contains_points(points).tolist() == [
        True,
        True,
        True,
        False,
    ]

    assert circle.contains_points(points).tolist() == [
        False,
        True,
        False,
        False,
    ]


def test_aoi_geometry_validation_fails_closed() -> None:
    with pytest.raises(
        ValueError,
        match="xmax",
    ):
        RectangleAOI(
            "bad",
            2.0,
            0.0,
            1.0,
            1.0,
        )

    with pytest.raises(
        ValueError,
        match="ymax",
    ):
        RectangleAOI(
            "bad",
            0.0,
            2.0,
            1.0,
            1.0,
        )

    with pytest.raises(
        ValueError,
        match="radius",
    ):
        CircleAOI(
            "bad",
            0.0,
            0.0,
            -1.0,
        )


@pytest.mark.parametrize(
    "bad_points",
    [
        np.array([1.0, 2.0]),
        np.array(
            [
                [1.0, 2.0, 3.0],
            ]
        ),
    ],
)
def test_aoi_membership_requires_n_by_two_points(
    bad_points: np.ndarray,
) -> None:
    rectangle = RectangleAOI(
        "rect",
        0.0,
        0.0,
        1.0,
        1.0,
    )

    with pytest.raises(
        ValueError,
        match=r"shape \(n, 2\)",
    ):
        rectangle.contains_points(bad_points)


# ----------------------------------------------------------------------
# endpoints.py
# ----------------------------------------------------------------------


def test_expected_endpoints_valid_contract() -> None:
    probabilities = pd.DataFrame(
        {
            "target": [0.0, 0.5, 1.0],
        }
    )

    assert expected_dwell(
        probabilities,
        np.array([10.0, 20.0, 30.0]),
        "target",
    ) == pytest.approx(40.0)

    assert expected_fixation_count(
        probabilities,
        "target",
    ) == pytest.approx(1.5)


def test_expected_endpoints_require_existing_aoi() -> None:
    probabilities = pd.DataFrame(
        {
            "target": [0.5],
        }
    )

    with pytest.raises(
        ValueError,
        match="not present",
    ):
        expected_dwell(
            probabilities,
            np.array([1.0]),
            "missing",
        )

    with pytest.raises(
        ValueError,
        match="not present",
    ):
        expected_fixation_count(
            probabilities,
            "missing",
        )


@pytest.mark.parametrize(
    "durations",
    [
        np.array([[1.0], [2.0]]),
        np.array([1.0]),
    ],
)
def test_expected_dwell_requires_aligned_one_dimensional_durations(
    durations: np.ndarray,
) -> None:
    probabilities = pd.DataFrame(
        {
            "target": [0.25, 0.75],
        }
    )

    with pytest.raises(
        ValueError,
        match="one-dimensional and match",
    ):
        expected_dwell(
            probabilities,
            durations,
            "target",
        )


@pytest.mark.parametrize(
    "durations",
    [
        np.array([np.nan, 1.0]),
        np.array([np.inf, 1.0]),
        np.array([-1.0, 1.0]),
    ],
)
def test_expected_dwell_rejects_invalid_durations(
    durations: np.ndarray,
) -> None:
    probabilities = pd.DataFrame(
        {
            "target": [0.25, 0.75],
        }
    )

    with pytest.raises(
        ValueError,
        match="finite and non-negative",
    ):
        expected_dwell(
            probabilities,
            durations,
            "target",
        )


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ([np.nan], "finite"),
        ([np.inf], "finite"),
        ([-0.01], r"\[0, 1\]"),
        ([1.01], r"\[0, 1\]"),
    ],
)
def test_expected_endpoints_reject_invalid_probabilities(
    values: list[float],
    message: str,
) -> None:
    probabilities = pd.DataFrame(
        {
            "target": values,
        }
    )

    with pytest.raises(
        ValueError,
        match=message,
    ):
        expected_fixation_count(
            probabilities,
            "target",
        )


# ----------------------------------------------------------------------
# multiverse.py
# ----------------------------------------------------------------------


def test_pipeline_space_empty_space_has_one_empty_specification() -> None:
    space = PipelineSpace()

    assert space.size == 1
    assert space.enumerate_specs() == [{}]


def test_pipeline_space_choice_validation() -> None:
    space = PipelineSpace()

    with pytest.raises(
        ValueError,
        match="name",
    ):
        space.add_choice(
            "",
            [1],
        )

    with pytest.raises(
        ValueError,
        match="at least one value",
    ):
        space.add_choice(
            "detector",
            [],
        )


def test_pipeline_space_enumerates_deterministically_and_filters() -> None:
    space = (
        PipelineSpace()
        .add_choice(
            "detector",
            ["ivt", "idt"],
        )
        .add_choice(
            "qc",
            [0.1, 0.2],
        )
    )

    assert space.size == 4

    all_specs = space.enumerate_specs()

    assert all_specs == [
        {
            "detector": "ivt",
            "qc": 0.1,
        },
        {
            "detector": "ivt",
            "qc": 0.2,
        },
        {
            "detector": "idt",
            "qc": 0.1,
        },
        {
            "detector": "idt",
            "qc": 0.2,
        },
    ]

    filtered = space.enumerate_specs(
        valid_if=lambda spec: not (
            spec["detector"] == "idt"
            and spec["qc"] == 0.2
        )
    )

    assert len(filtered) == 3
    assert {
        "detector": "idt",
        "qc": 0.2,
    } not in filtered


def test_run_specs_covers_direct_and_processed_execution_paths() -> None:
    study = _study()

    space = PipelineSpace().add_choice(
        "offset",
        [1.0, 2.0],
    )

    direct = run_specs(
        study,
        space,
        endpoint=lambda source, spec: (
            float(source.data["x"].mean())
            + spec["offset"]
        ),
    )

    assert list(direct["estimate"]) == [
        2.5,
        3.5,
    ]

    calls: list[tuple[GazeStudy, dict[str, object]]] = []

    def processor(
        source: GazeStudy,
        spec: dict[str, object],
    ) -> float:
        calls.append(
            (
                source,
                spec,
            )
        )
        return float(source.data["x"].sum())

    processed = run_specs(
        study,
        space,
        processor=processor,
        valid_if=lambda spec: spec["offset"] == 2.0,
        endpoint=lambda value, spec: (
            float(value)
            + float(spec["offset"])
        ),
    )

    assert len(calls) == 1
    assert calls[0][0] is study
    assert processed.to_dict("records") == [
        {
            "spec_id": 0,
            "offset": 2.0,
            "estimate": 8.0,
        }
    ]


# ----------------------------------------------------------------------
# study.py
# ----------------------------------------------------------------------


def test_gaze_study_rejects_non_dataframe() -> None:
    with pytest.raises(
        TypeError,
        match="pandas DataFrame",
    ):
        GazeStudy(
            [],  # type: ignore[arg-type]
        )


def test_gaze_study_requires_semantic_columns() -> None:
    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        GazeStudy(
            pd.DataFrame(
                {
                    "x": [0.0],
                    "y": [0.0],
                }
            )
        )


@pytest.mark.parametrize(
    "column",
    [
        "x",
        "y",
        "timestamp",
    ],
)
def test_gaze_study_requires_numeric_measurement_columns(
    column: str,
) -> None:
    frame = pd.DataFrame(
        {
            "participant": ["p1"],
            "trial": [1],
            "timestamp": [0.0],
            "x": [1.0],
            "y": [2.0],
        }
    )

    frame[column] = ["not-numeric"]

    with pytest.raises(
        TypeError,
        match="must be numeric",
    ):
        GazeStudy(frame)


def test_gaze_study_rejects_empty_frame() -> None:
    with pytest.raises(
        ValueError,
        match="at least one observation",
    ):
        GazeStudy(
            pd.DataFrame(
                {
                    "participant": pd.Series(dtype="object"),
                    "trial": pd.Series(dtype="int64"),
                    "timestamp": pd.Series(dtype="float64"),
                    "x": pd.Series(dtype="float64"),
                    "y": pd.Series(dtype="float64"),
                }
            )
        )


def test_gaze_study_counts_validates_copies_and_requires_columns() -> None:
    study = _study()

    assert study.n_participants == 2
    assert study.n_trials == 2

    study.validate_time_order()

    study.require_columns(
        [
            "extra",
        ]
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        study.require_columns(
            [
                "extra",
                "missing",
            ]
        )

    changed = study.data.copy()
    changed["x"] += 100.0

    copied = study.copy_with(changed)

    assert copied is not study
    assert copied.x == study.x
    assert copied.y == study.y
    assert copied.timestamp == study.timestamp
    assert copied.participant == study.participant
    assert copied.trial == study.trial

    changed.loc[changed.index[0], "x"] = -999.0

    assert copied.data.loc[copied.data.index[0], "x"] != -999.0


def test_gaze_study_detects_descending_timestamps() -> None:
    frame = pd.DataFrame(
        {
            "participant": ["p1", "p1"],
            "trial": [1, 1],
            "timestamp": [2.0, 1.0],
            "x": [0.0, 0.0],
            "y": [0.0, 0.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="timestamps decrease",
    ):
        GazeStudy(frame).validate_time_order()


def test_gaze_study_ignores_nonfinite_values_when_checking_finite_order() -> None:
    frame = pd.DataFrame(
        {
            "participant": ["p1", "p1", "p1"],
            "trial": [1, 1, 1],
            "timestamp": [0.0, np.nan, 1.0],
            "x": [0.0, 0.0, 0.0],
            "y": [0.0, 0.0, 0.0],
        }
    )

    GazeStudy(frame).validate_time_order()


class _ScalarGroupDataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return _ScalarGroupDataFrame

    def groupby(self, *args, **kwargs):  # type: ignore[override]
        frame = pd.DataFrame(self)
        return [
            (
                "synthetic-scalar-key",
                frame,
            )
        ]


def test_gaze_study_defensive_scalar_group_key_path() -> None:
    frame = _ScalarGroupDataFrame(
        {
            "participant": ["p1", "p1"],
            "trial": [1, 1],
            "timestamp": [2.0, 1.0],
            "x": [0.0, 0.0],
            "y": [0.0, 0.0],
        }
    )

    with pytest.raises(
        ValueError,
        match=r"\('synthetic-scalar-key', None\)",
    ):
        GazeStudy(frame).validate_time_order()


# ----------------------------------------------------------------------
# benchmark.py
# ----------------------------------------------------------------------


def test_simulate_boundary_data_is_reproducible_and_uses_generator_input() -> None:
    first = simulate_boundary_data(
        n=8,
        rng=123,
    )

    second = simulate_boundary_data(
        n=8,
        rng=123,
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )

    generator = np.random.default_rng(77)

    generated = simulate_boundary_data(
        n=4,
        rng=generator,
        bias_x=1.0,
        bias_y=-1.0,
    )

    assert len(generated) == 4
    assert set(generated.columns) == {
        "true_x",
        "true_y",
        "observed_x",
        "observed_y",
    }


def test_simulate_boundary_data_validation() -> None:
    with pytest.raises(
        ValueError,
        match="at least 2",
    ):
        simulate_boundary_data(
            n=1,
        )

    for argument in (
        "true_x_sd",
        "y_sd",
        "measurement_sd",
    ):
        kwargs = {
            argument: -1.0,
        }

        with pytest.raises(
            ValueError,
            match="non-negative",
        ):
            simulate_boundary_data(
                **kwargs,
            )


def _zero_error_model() -> GaussianGazeErrorModel:
    return GaussianGazeErrorModel(
        mean_error=np.zeros(2),
        covariance=np.zeros(
            (
                2,
                2,
            )
        ),
        n_validation=4,
    )


def test_evaluate_aoi_recovery_known_truth_contract() -> None:
    truth = np.array(
        [
            [-1.0, 0.0],
            [1.0, 0.0],
        ]
    )

    observed = truth.copy()

    aois = [
        RectangleAOI(
            "left",
            -2.0,
            -1.0,
            0.0,
            1.0,
        ),
        RectangleAOI(
            "right",
            0.0,
            -1.0,
            2.0,
            1.0,
        ),
    ]

    result = evaluate_aoi_recovery(
        truth,
        observed,
        aois,
        _zero_error_model(),
        draws=8,
        rng=42,
    )

    assert list(result["aoi"]) == [
        "left",
        "right",
    ]

    assert (result["hard_accuracy"] == 1.0).all()
    assert (result["probabilistic_accuracy"] == 1.0).all()
    assert (result["hard_brier"] == 0.0).all()
    assert (result["probabilistic_brier"] == 0.0).all()


def test_evaluate_aoi_recovery_validation_paths() -> None:
    model = _zero_error_model()

    with pytest.raises(
        ValueError,
        match="truth_points must have shape",
    ):
        evaluate_aoi_recovery(
            np.array([1.0, 2.0]),
            np.array(
                [
                    [1.0, 2.0],
                ]
            ),
            [
                RectangleAOI(
                    "target",
                    0.0,
                    0.0,
                    2.0,
                    2.0,
                )
            ],
            model,
        )

    with pytest.raises(
        ValueError,
        match="observed_points must have shape",
    ):
        evaluate_aoi_recovery(
            np.array(
                [
                    [1.0, 2.0],
                ]
            ),
            np.array([1.0, 2.0]),
            [
                RectangleAOI(
                    "target",
                    0.0,
                    0.0,
                    2.0,
                    2.0,
                )
            ],
            model,
        )

    with pytest.raises(
        ValueError,
        match="finite",
    ):
        evaluate_aoi_recovery(
            np.array(
                [
                    [np.nan, 0.0],
                ]
            ),
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
            model,
        )

    with pytest.raises(
        ValueError,
        match="same shape",
    ):
        evaluate_aoi_recovery(
            np.array(
                [
                    [0.0, 0.0],
                    [1.0, 1.0],
                ]
            ),
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
            model,
        )

    with pytest.raises(
        ValueError,
        match="at least one AOI",
    ):
        evaluate_aoi_recovery(
            np.array(
                [
                    [0.0, 0.0],
                ]
            ),
            np.array(
                [
                    [0.0, 0.0],
                ]
            ),
            [],
            model,
        )


def test_fit_error_model_from_known_truth_supports_custom_column_names() -> None:
    data = pd.DataFrame(
        {
            "ox": [2.0, 3.0, 4.0],
            "oy": [3.0, 4.0, 5.0],
            "tx": [1.0, 2.0, 3.0],
            "ty": [5.0, 6.0, 7.0],
        }
    )

    model = fit_error_model_from_known_truth(
        data,
        observed_x="ox",
        observed_y="oy",
        true_x="tx",
        true_y="ty",
    )

    np.testing.assert_allclose(
        model.mean_error,
        [
            1.0,
            -2.0,
        ],
    )