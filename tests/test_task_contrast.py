import numpy as np
import pandas as pd
import pytest

from gazeaudit import ConclusionRule
from gazeaudit.task_contrast import (
    audit_detector_robustness,
    detector_task_contrast,
    fixation_event_durations,
    fixed_reference_cohort,
    participant_task_fixation_summary,
)

EXPECTED = ("ivt", "ivvt", "idt", "idvt", "engbert", "nh", "remodnav")
RULE = ConclusionRule(
    relative_tolerance=0.20,
    require_sign=True,
    minimum_recovery_fraction=6 / 7,
)


def _stream(participant, task, run_lengths, *, dt=10.0, start=0.0):
    labels = []
    for index, run_length in enumerate(run_lengths):
        if index:
            labels.append("saccade")
        labels.extend(["fixation"] * run_length)
    timestamps = start + np.arange(len(labels), dtype=float) * dt
    return pd.DataFrame(
        {
            "participant": participant,
            "task": task,
            "timestamp": timestamps,
            "event_label": labels,
        }
    )


def _two_task_samples(participants=(1, 2, 3, 4), *, fxs=6, tex=4):
    frames = []
    for participant in participants:
        frames.append(_stream(participant, "FXS", [fxs]))
        frames.append(_stream(participant, "TEX", [tex]))
    return pd.concat(frames, ignore_index=True)


def _detectors(*, n_bad=0):
    detector_map = {}
    for index, name in enumerate(EXPECTED):
        detector_map[name] = _two_task_samples(
            fxs=8 if index < n_bad else 6,
            tex=4,
        )
    return detector_map


def test_fixation_event_duration_uses_median_interval_for_single_sample_event():
    frame = pd.DataFrame(
        {
            "timestamp": [0.0, 10.0, 20.0, 30.0, 40.0],
            "event_label": ["saccade", "fixation", "saccade", "fixation", "fixation"],
        }
    )

    durations = fixation_event_durations(frame)

    np.testing.assert_allclose(durations, [10.0, 20.0])


def test_fixation_event_duration_supports_irregular_sampling():
    frame = pd.DataFrame(
        {
            "timestamp": [0.0, 9.0, 20.0, 30.0],
            "event_label": ["fixation", "fixation", "saccade", "fixation"],
        }
    )

    durations = fixation_event_durations(frame)

    np.testing.assert_allclose(durations, [19.0, 10.0])


@pytest.mark.parametrize(
    "timestamps",
    [
        [0.0, np.nan, 20.0],
        [0.0, 10.0, 10.0],
        [0.0],
    ],
)
def test_invalid_streams_are_rejected_by_event_extraction(timestamps):
    frame = pd.DataFrame(
        {
            "timestamp": timestamps,
            "event_label": ["fixation"] * len(timestamps),
        }
    )

    with pytest.raises(ValueError):
        fixation_event_durations(frame)


def test_participant_task_summary_marks_invalid_stream_missing():
    valid = _stream(1, "FXS", [3])
    invalid = _stream(1, "TEX", [3])
    invalid.loc[2, "timestamp"] = invalid.loc[1, "timestamp"]
    samples = pd.concat([valid, invalid], ignore_index=True)

    summary = participant_task_fixation_summary(samples)

    fxs = summary.loc[summary["task"].eq("FXS")].iloc[0]
    tex = summary.loc[summary["task"].eq("TEX")].iloc[0]
    assert fxs["valid_stream"]
    assert fxs["median_fixation_duration"] == 30.0
    assert not tex["valid_stream"]
    assert np.isnan(tex["median_fixation_duration"])


def test_reference_cohort_is_defined_only_by_valid_paired_reference_data():
    reference = _two_task_samples(participants=(1, 2, 3))
    bad_mask = reference["participant"].eq(3) & reference["task"].eq("TEX")
    bad_index = reference.index[bad_mask][-1]
    previous = reference.index[bad_mask][-2]
    reference.loc[bad_index, "timestamp"] = reference.loc[previous, "timestamp"]

    cohort, _, contrasts, effect = fixed_reference_cohort(
        reference,
        task_a="FXS",
        task_b="TEX",
    )

    assert cohort == (1, 2)
    assert contrasts["participant"].tolist() == [1, 2]
    assert effect == 20.0


def test_detector_coverage_uses_fixed_reference_denominator():
    reference = _two_task_samples()
    cohort, _, _, _ = fixed_reference_cohort(
        reference,
        task_a="FXS",
        task_b="TEX",
    )
    detector = _two_task_samples(participants=(1, 2, 3, 99))

    _, contrasts, effect, coverage = detector_task_contrast(
        detector,
        cohort,
        task_a="FXS",
        task_b="TEX",
    )

    assert contrasts["participant"].tolist() == [1, 2, 3, 4]
    assert contrasts["paired_complete"].sum() == 3
    assert coverage == 0.75
    assert effect == 20.0


def test_six_of_seven_recovery_is_robust():
    audit = audit_detector_robustness(
        _two_task_samples(),
        _detectors(n_bad=1),
        expected_detectors=EXPECTED,
        task_a="FXS",
        task_b="TEX",
        rule=RULE,
        minimum_coverage_fraction=1.0,
    )

    assert audit.fixed_cohort == (1, 2, 3, 4)
    assert audit.reference_effect == 20.0
    assert audit.summary["classification"] == "robust"
    assert audit.summary["completeness_passed"]
    assert audit.summary["conclusion_recovery_fraction"] == pytest.approx(6 / 7)
    assert audit.recovery is not None
    assert int(audit.recovery["conclusion_recovered"].sum()) == 6


def test_five_of_seven_recovery_is_fragile():
    audit = audit_detector_robustness(
        _two_task_samples(),
        _detectors(n_bad=2),
        expected_detectors=EXPECTED,
        task_a="FXS",
        task_b="TEX",
        rule=RULE,
        minimum_coverage_fraction=1.0,
    )

    assert audit.summary["classification"] == "fragile"
    assert audit.summary["conclusion_recovery_fraction"] == pytest.approx(5 / 7)


def test_completeness_gate_is_fail_closed():
    detectors = _detectors()
    detectors["ivt"] = _two_task_samples(participants=(1, 2, 3))

    audit = audit_detector_robustness(
        _two_task_samples(),
        detectors,
        expected_detectors=EXPECTED,
        task_a="FXS",
        task_b="TEX",
        rule=RULE,
        minimum_coverage_fraction=0.95,
    )

    assert audit.summary["classification"] == "incomplete"
    assert not audit.summary["completeness_passed"]
    assert audit.recovery is None
    ivt = audit.coverage.loc[audit.coverage["detector"].eq("ivt")].iloc[0]
    assert ivt["n_fixed_cohort"] == 4
    assert ivt["n_paired_complete"] == 3
    assert ivt["coverage_fraction"] == 0.75
    assert not ivt["coverage_passed"]


def test_missing_unexpected_and_duplicate_detectors_are_rejected():
    reference = _two_task_samples()
    samples = _two_task_samples()

    with pytest.raises(ValueError, match="missing"):
        audit_detector_robustness(
            reference,
            {"ivt": samples},
            expected_detectors=("ivt", "idt"),
            task_a="FXS",
            task_b="TEX",
            rule=RULE,
        )

    with pytest.raises(ValueError, match="unexpected"):
        audit_detector_robustness(
            reference,
            {"ivt": samples, "other": samples},
            expected_detectors=("ivt",),
            task_a="FXS",
            task_b="TEX",
            rule=RULE,
        )

    with pytest.raises(ValueError, match="duplicate detector"):
        audit_detector_robustness(
            reference,
            [("ivt", samples), ("ivt", samples)],
            expected_detectors=("ivt",),
            task_a="FXS",
            task_b="TEX",
            rule=RULE,
        )


def test_zero_reference_effect_stops_before_detector_aggregation():
    reference = _two_task_samples(fxs=4, tex=4)

    with pytest.raises(ValueError, match="exactly zero"):
        audit_detector_robustness(
            reference,
            {"ivt": pd.DataFrame({"not_the_expected_schema": [1]})},
            expected_detectors=("ivt",),
            task_a="FXS",
            task_b="TEX",
            rule=RULE,
        )


def test_p_values_are_ignored_by_recovery_classification():
    detectors = _detectors(n_bad=1)
    for frame in detectors.values():
        frame["p_value"] = 0.999

    audit = audit_detector_robustness(
        _two_task_samples(),
        detectors,
        expected_detectors=EXPECTED,
        task_a="FXS",
        task_b="TEX",
        rule=RULE,
        minimum_coverage_fraction=1.0,
    )

    assert audit.summary["classification"] == "robust"
    assert "p_value" not in audit.effects.columns
    assert audit.recovery is not None
    assert "p_value" not in audit.recovery.columns
