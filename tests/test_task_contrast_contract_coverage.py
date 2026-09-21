from __future__ import annotations

from enum import Enum

import numpy as np
import pandas as pd
import pytest

import gazeaudit.task_contrast as tc
from gazeaudit.conclusion import ConclusionRule

RULE = ConclusionRule(
    relative_tolerance=0.20,
    require_sign=True,
    minimum_recovery_fraction=0.50,
)


def _stream(
    participant: object = "p1",
    task: object = "A",
    *,
    labels: list[object] | None = None,
    timestamps: list[float] | None = None,
) -> pd.DataFrame:
    if labels is None:
        labels = [
            "fixation",
            "fixation",
            "saccade",
        ]

    if timestamps is None:
        timestamps = [
            0.0,
            10.0,
            20.0,
        ]

    return pd.DataFrame(
        {
            "participant": [participant] * len(labels),
            "task": [task] * len(labels),
            "timestamp": timestamps,
            "event_label": labels,
        }
    )


def _two_task_reference(
    *,
    difference: int = 2,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for participant in (
        "p1",
        "p2",
    ):
        frames.append(
            _stream(
                participant,
                "A",
                labels=[
                    "fixation",
                    "fixation",
                    "fixation",
                    "fixation",
                ],
                timestamps=[
                    0.0,
                    10.0,
                    20.0,
                    30.0,
                ],
            )
        )

        frames.append(
            _stream(
                participant,
                "B",
                labels=(
                    [
                        "fixation",
                        "fixation",
                    ]
                    if difference
                    else [
                        "fixation",
                        "fixation",
                        "fixation",
                        "fixation",
                    ]
                ),
                timestamps=(
                    [
                        0.0,
                        10.0,
                    ]
                    if difference
                    else [
                        0.0,
                        10.0,
                        20.0,
                        30.0,
                    ]
                ),
            )
        )

    return pd.concat(
        frames,
        ignore_index=True,
    )


# ======================================================================
# fixation_event_durations
# ======================================================================


def test_event_durations_require_columns() -> None:
    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        tc.fixation_event_durations(
            pd.DataFrame(
                {
                    "timestamp": [
                        0.0,
                        1.0,
                    ]
                }
            )
        )


def test_event_durations_reject_empty_fixation_label_set() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": [
                0.0,
                10.0,
            ],
            "event_label": [
                "fixation",
                "fixation",
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="at least one label",
    ):
        tc.fixation_event_durations(
            frame,
            fixation_labels=(),
        )


def test_event_durations_can_return_empty_valid_result() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": [
                0.0,
                10.0,
                20.0,
            ],
            "event_label": [
                "saccade",
                "blink",
                "saccade",
            ],
        }
    )

    durations = tc.fixation_event_durations(
        frame
    )

    assert durations.dtype == float
    assert durations.size == 0


def test_event_duration_closes_fixation_before_nonfixation() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": [
                0.0,
                10.0,
                20.0,
                30.0,
            ],
            "event_label": [
                "fixation",
                "fixation",
                "saccade",
                "saccade",
            ],
        }
    )

    np.testing.assert_allclose(
        tc.fixation_event_durations(frame),
        [
            20.0,
        ],
    )


def test_event_duration_closes_fixation_at_last_sample() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": [
                0.0,
                10.0,
                20.0,
            ],
            "event_label": [
                "saccade",
                "fixation",
                "fixation",
            ],
        }
    )

    np.testing.assert_allclose(
        tc.fixation_event_durations(frame),
        [
            20.0,
        ],
    )


# ======================================================================
# participant_task_fixation_summary
# ======================================================================


def test_participant_summary_rejects_invalid_policy() -> None:
    with pytest.raises(
        ValueError,
        match="invalid must be",
    ):
        tc.participant_task_fixation_summary(
            _stream(),
            invalid="ignore",
        )


def test_participant_summary_requires_columns() -> None:
    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        tc.participant_task_fixation_summary(
            pd.DataFrame(
                {
                    "participant": ["p1"],
                    "task": ["A"],
                }
            )
        )


def test_participant_summary_raise_policy_propagates_invalid_stream() -> None:
    invalid = pd.DataFrame(
        {
            "participant": [
                "p1",
            ],
            "task": [
                "A",
            ],
            "timestamp": [
                0.0,
            ],
            "event_label": [
                "fixation",
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="at least two samples",
    ):
        tc.participant_task_fixation_summary(
            invalid,
            invalid="raise",
        )


def test_participant_summary_valid_stream_without_fixations() -> None:
    frame = _stream(
        labels=[
            "saccade",
            "blink",
            "saccade",
        ]
    )

    summary = tc.participant_task_fixation_summary(
        frame
    )

    assert len(summary) == 1

    row = summary.iloc[0]

    assert bool(row["valid_stream"])
    assert not bool(row["has_fixation"])
    assert int(row["n_fixation_events"]) == 0
    assert np.isnan(
        float(row["median_fixation_duration"])
    )


# ======================================================================
# fixed_reference_cohort
# ======================================================================


def test_fixed_reference_cohort_rejects_empty_paired_cohort() -> None:
    reference = pd.concat(
        [
            _stream(
                "p1",
                "A",
                labels=[
                    "saccade",
                    "saccade",
                    "saccade",
                ],
            ),
            _stream(
                "p1",
                "B",
                labels=[
                    "saccade",
                    "saccade",
                    "saccade",
                ],
            ),
        ],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="empty paired fixed cohort",
    ):
        tc.fixed_reference_cohort(
            reference,
            task_a="A",
            task_b="B",
        )


def test_fixed_reference_cohort_rejects_nonfinite_effect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    summaries = pd.DataFrame(
        {
            "participant": [
                "p1",
            ],
            "task": [
                "A",
            ],
            "median_fixation_duration": [
                1.0,
            ],
        }
    )

    contrasts = pd.DataFrame(
        {
            "participant": [
                "p1",
            ],
            "paired_complete": [
                True,
            ],
            "task_contrast": [
                np.inf,
            ],
        }
    )

    monkeypatch.setattr(
        tc,
        "participant_task_fixation_summary",
        lambda *args, **kwargs: summaries,
    )

    monkeypatch.setattr(
        tc,
        "_paired_task_contrasts",
        lambda *args, **kwargs: contrasts,
    )

    with pytest.raises(
        ValueError,
        match="reference effect must be finite",
    ):
        tc.fixed_reference_cohort(
            pd.DataFrame(),
            task_a="A",
            task_b="B",
        )


# ======================================================================
# detector_task_contrast
# ======================================================================


def test_detector_contrast_rejects_empty_fixed_cohort() -> None:
    with pytest.raises(
        ValueError,
        match="at least one participant",
    ):
        tc.detector_task_contrast(
            _stream(),
            (),
            task_a="A",
            task_b="B",
        )


def test_detector_contrast_rejects_duplicate_fixed_cohort() -> None:
    with pytest.raises(
        ValueError,
        match="duplicate participants",
    ):
        tc.detector_task_contrast(
            _stream(),
            (
                "p1",
                "p1",
            ),
            task_a="A",
            task_b="B",
        )


def test_detector_contrast_requires_sample_columns() -> None:
    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        tc.detector_task_contrast(
            pd.DataFrame(
                {
                    "participant": [
                        "p1",
                    ]
                }
            ),
            (
                "p1",
            ),
            task_a="A",
            task_b="B",
        )


def test_detector_contrast_returns_nan_when_no_pair_is_complete() -> None:
    detector = _stream(
        "other",
        "A",
    )

    summaries, contrasts, effect, coverage = tc.detector_task_contrast(
        detector,
        (
            "p1",
        ),
        task_a="A",
        task_b="B",
    )

    assert summaries.empty
    assert len(contrasts) == 1
    assert not bool(
        contrasts.loc[
            0,
            "paired_complete",
        ]
    )
    assert np.isnan(effect)
    assert coverage == 0.0


# ======================================================================
# audit_detector_robustness argument validation
# ======================================================================


@pytest.mark.parametrize(
    "value",
    [
        np.nan,
        np.inf,
        -np.inf,
        -0.01,
        1.01,
    ],
)
def test_audit_rejects_invalid_minimum_coverage(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="between 0 and 1",
    ):
        tc.audit_detector_robustness(
            _two_task_reference(),
            {
                "detector": _two_task_reference(),
            },
            expected_detectors=(
                "detector",
            ),
            task_a="A",
            task_b="B",
            rule=RULE,
            minimum_coverage_fraction=value,
        )


def test_audit_rejects_empty_expected_detector_set() -> None:
    with pytest.raises(
        ValueError,
        match="at least one detector",
    ):
        tc.audit_detector_robustness(
            _two_task_reference(),
            {},
            expected_detectors=(),
            task_a="A",
            task_b="B",
            rule=RULE,
        )


def test_audit_rejects_duplicate_expected_detector_set() -> None:
    samples = _two_task_reference()

    with pytest.raises(
        ValueError,
        match="must not contain duplicates",
    ):
        tc.audit_detector_robustness(
            samples,
            {
                "detector": samples,
            },
            expected_detectors=(
                "detector",
                "detector",
            ),
            task_a="A",
            task_b="B",
            rule=RULE,
        )


def test_audit_runtime_guard_rejects_nonfinite_effect_after_complete_coverage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reference_tasks = pd.DataFrame(
        {
            "participant": [
                "p1",
            ]
        }
    )

    reference_contrasts = pd.DataFrame(
        {
            "participant": [
                "p1",
            ],
            "paired_complete": [
                True,
            ],
            "task_contrast": [
                1.0,
            ],
        }
    )

    monkeypatch.setattr(
        tc,
        "fixed_reference_cohort",
        lambda *args, **kwargs: (
            (
                "p1",
            ),
            reference_tasks,
            reference_contrasts,
            1.0,
        ),
    )

    detector_summary = pd.DataFrame(
        {
            "participant": [
                "p1",
            ],
            "task": [
                "A",
            ],
            "median_fixation_duration": [
                1.0,
            ],
            "n_fixation_events": [
                1,
            ],
            "valid_stream": [
                True,
            ],
            "has_fixation": [
                True,
            ],
        }
    )

    detector_contrasts = pd.DataFrame(
        {
            "participant": [
                "p1",
            ],
            "paired_complete": [
                True,
            ],
            "task_contrast": [
                1.0,
            ],
        }
    )

    monkeypatch.setattr(
        tc,
        "detector_task_contrast",
        lambda *args, **kwargs: (
            detector_summary,
            detector_contrasts,
            np.nan,
            1.0,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="effect is non-finite",
    ):
        tc.audit_detector_robustness(
            pd.DataFrame(),
            {
                "detector": pd.DataFrame(),
            },
            expected_detectors=(
                "detector",
            ),
            task_a="A",
            task_b="B",
            rule=RULE,
            minimum_coverage_fraction=1.0,
        )


# ======================================================================
# _paired_task_contrasts
# ======================================================================


def test_paired_task_contrasts_rejects_identical_tasks() -> None:
    with pytest.raises(
        ValueError,
        match="must differ",
    ):
        tc._paired_task_contrasts(
            pd.DataFrame(),
            task_a="A",
            task_b="A",
            participant_col="participant",
            task_col="task",
        )


def test_paired_task_contrasts_handles_empty_summary_without_participants() -> None:
    result = tc._paired_task_contrasts(
        pd.DataFrame(),
        task_a="A",
        task_b="B",
        participant_col="participant",
        task_col="task",
    )

    assert result.empty
    assert list(result.columns) == [
        "participant",
        "task_a_median",
        "task_b_median",
        "paired_complete",
        "task_contrast",
    ]


def test_paired_task_contrasts_handles_empty_summary_with_fixed_participants() -> None:
    result = tc._paired_task_contrasts(
        pd.DataFrame(),
        task_a="A",
        task_b="B",
        participant_col="participant",
        task_col="task",
        participants=(
            "p1",
            "p2",
        ),
    )

    assert result["participant"].tolist() == [
        "p1",
        "p2",
    ]

    assert not result["paired_complete"].any()

    assert result["task_contrast"].isna().all()


def test_paired_task_contrasts_rejects_duplicate_participant_task_rows() -> None:
    summaries = pd.DataFrame(
        {
            "participant": [
                "p1",
                "p1",
            ],
            "task": [
                "A",
                "A",
            ],
            "median_fixation_duration": [
                10.0,
                11.0,
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="must be unique",
    ):
        tc._paired_task_contrasts(
            summaries,
            task_a="A",
            task_b="B",
            participant_col="participant",
            task_col="task",
        )


def test_paired_task_contrasts_coerces_bad_numeric_summary_to_missing() -> None:
    summaries = pd.DataFrame(
        {
            "participant": [
                "p1",
                "p1",
            ],
            "task": [
                "A",
                "B",
            ],
            "median_fixation_duration": [
                "bad",
                10.0,
            ],
        }
    )

    result = tc._paired_task_contrasts(
        summaries,
        task_a="A",
        task_b="B",
        participant_col="participant",
        task_col="task",
    )

    assert len(result) == 1
    assert not bool(
        result.loc[
            0,
            "paired_complete",
        ]
    )
    assert np.isnan(
        float(
            result.loc[
                0,
                "task_contrast",
            ]
        )
    )


# ======================================================================
# _normalize_detector_inputs
# ======================================================================


def test_normalize_detector_inputs_mapping_path() -> None:
    frame = pd.DataFrame(
        {
            "x": [
                1,
            ]
        }
    )

    result = tc._normalize_detector_inputs(
        {
            "detector": frame,
        }
    )

    assert result == {
        "detector": frame,
    }


@pytest.mark.parametrize(
    "name",
    [
        "",
        123,
    ],
)
def test_normalize_detector_inputs_requires_nonempty_string_name(
    name: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="non-empty strings",
    ):
        tc._normalize_detector_inputs(
            [
                (
                    name,
                    pd.DataFrame(),
                )
            ]
        )


def test_normalize_detector_inputs_rejects_non_dataframe_samples() -> None:
    with pytest.raises(
        TypeError,
        match="pandas DataFrame",
    ):
        tc._normalize_detector_inputs(
            [
                (
                    "detector",
                    [],  # type: ignore[list-item]
                )
            ]
        )


# ======================================================================
# _normalize_label
# ======================================================================


class LabelEnum(Enum):
    FIXATION = 1


class NamedLabel:
    name = "  Fixation  "


class EmptyNamedLabel:
    name = ""

    def __str__(self) -> str:
        return " Custom "


def test_normalize_label_supports_enum_name_attribute() -> None:
    assert tc._normalize_label(
        LabelEnum.FIXATION
    ) == "fixation"

    assert tc._normalize_label(
        NamedLabel()
    ) == "fixation"


def test_normalize_label_empty_name_falls_back_to_string() -> None:
    assert tc._normalize_label(
        EmptyNamedLabel()
    ) == "custom"


@pytest.mark.parametrize(
    "value",
    [
        None,
        np.nan,
        pd.NA,
    ],
)
def test_normalize_label_missing_values_become_empty(
    value: object,
) -> None:
    assert tc._normalize_label(value) == ""


def test_normalize_label_scalar_string_fallback() -> None:
    assert tc._normalize_label(
        123
    ) == "123"

    assert tc._normalize_label(
        "  FIXATION "
    ) == "fixation"


# ======================================================================
# _require_columns
# ======================================================================


def test_require_columns_accepts_complete_schema() -> None:
    tc._require_columns(
        pd.DataFrame(
            {
                "a": [
                    1,
                ],
                "b": [
                    2,
                ],
            }
        ),
        [
            "a",
            "b",
        ],
    )


def test_require_columns_reports_all_missing_columns() -> None:
    with pytest.raises(
        ValueError,
        match="b.*c",
    ):
        tc._require_columns(
            pd.DataFrame(
                {
                    "a": [
                        1,
                    ]
                }
            ),
            [
                "a",
                "b",
                "c",
            ],
        )