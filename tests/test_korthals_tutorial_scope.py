import pandas as pd
import pytest

from gazeaudit.korthals_source import _scope_authoritative_task_trials


def _rows(*, tutorial_number=0, tutorial_name="Tutorial", tutorial_type="moving_circle", tutorial_speed=2.0, tutorial_trajectory="east"):
    return pd.DataFrame(
        [
            {
                "participant_id": "p1",
                "trial_number": tutorial_number,
                "trial_name": tutorial_name,
                "target_type": tutorial_type,
                "target_speed": tutorial_speed,
                "target_trajectory": tutorial_trajectory,
            },
            {
                "participant_id": "p1",
                "trial_number": 1,
                "trial_name": "Trial 1",
                "target_type": "moving_circle",
                "target_speed": 1.0,
                "target_trajectory": "east",
            },
            {
                "participant_id": "p1",
                "trial_number": 144,
                "trial_name": "Trial 144",
                "target_type": "jumping_circle",
                "target_speed": 6.0,
                "target_trajectory": "west",
            },
        ]
    )


def test_authoritative_tutorial_zero_is_removed_without_touching_task_trials():
    scoped = _scope_authoritative_task_trials(_rows())

    assert scoped["trial_number"].tolist() == [1, 144]
    assert scoped["trial_name"].tolist() == ["Trial 1", "Trial 144"]


def test_task_only_input_is_unchanged_and_does_not_require_tutorial_metadata():
    source = pd.DataFrame(
        {
            "participant_id": ["p1", "p1"],
            "trial_number": [1, 144],
            "target_type": ["moving_circle", "jumping_circle"],
        }
    )

    scoped = _scope_authoritative_task_trials(source)

    pd.testing.assert_frame_equal(scoped, source)


@pytest.mark.parametrize("trial_number", [-1, 145, 999])
def test_non_tutorial_out_of_range_trial_fails_closed(trial_number):
    with pytest.raises(ValueError, match="out-of-range trials other than"):
        _scope_authoritative_task_trials(_rows(tutorial_number=trial_number))


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"tutorial_name": "Trial 0"}, "tutorial name"),
        ({"tutorial_type": "jumping_circle"}, "tutorial target type"),
        ({"tutorial_speed": 1.0}, "tutorial target speed 2"),
        ({"tutorial_trajectory": "west"}, "tutorial trajectory east"),
    ],
)
def test_trial_zero_must_match_authoritative_tutorial_signature(kwargs, message):
    with pytest.raises(ValueError, match=message):
        _scope_authoritative_task_trials(_rows(**kwargs))


def test_mixed_tutorial_and_other_out_of_range_trial_fails_closed():
    source = pd.concat(
        [
            _rows(),
            pd.DataFrame(
                [
                    {
                        "participant_id": "p2",
                        "trial_number": 145,
                        "trial_name": "Trial 145",
                        "target_type": "moving_circle",
                        "target_speed": 1.0,
                        "target_trajectory": "east",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="\[0, 145\]"):
        _scope_authoritative_task_trials(source)
