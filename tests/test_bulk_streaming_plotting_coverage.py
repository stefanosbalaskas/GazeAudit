from __future__ import annotations

import builtins
from contextlib import nullcontext
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import gazeaudit.korthals_streaming as streaming
import gazeaudit.plotting as plotting
from gazeaudit.aoi import CircleAOI, RectangleAOI
from gazeaudit.korthals_execution import PreparedKorthalsData
from gazeaudit.korthals_v2 import (
    KORTHALS_V2_CASE_STUDY_ID,
    KORTHALS_V2_MISSINGNESS_POLICY,
    KORTHALS_V2_PROTOCOL_FINGERPRINT,
)


def _local_part(
    participant: str = "p1",
    *,
    participant_count: int = 1,
    case_study_id: str = KORTHALS_V2_CASE_STUDY_ID,
    protocol_fingerprint: str = KORTHALS_V2_PROTOCOL_FINGERPRINT,
    missingness_policy: str = KORTHALS_V2_MISSINGNESS_POLICY,
    error_group: str | None = None,
) -> PreparedKorthalsData:
    group = error_group or f"{participant}-v1"
    data = pd.DataFrame(
        {
            "participant_id": [participant],
            "trial_number": [1],
            "scheduled_trial_time": [0.0],
            "trial_time": [0.0],
            "error_group": [group],
        }
    )
    validation = pd.DataFrame(
        {
            "participant_id": [participant],
            "validation_nr": [1],
            "error_group": [group],
        }
    )
    identity = {
        "participant_count": participant_count,
        "case_study_id": case_study_id,
        "protocol_fingerprint": protocol_fingerprint,
        "missingness_policy": missingness_policy,
        "zero_finite_scheduled_trials": [],
        "sampling_incomplete_matched_cells": [],
    }
    return PreparedKorthalsData(
        data=data,
        validation_groups=validation,
        source_identity=identity,
    )


def _source_identity() -> dict[str, object]:
    return {
        "source_manifest_fingerprint": "a" * 64,
        "source_file_count": 2,
        "download_contract": {
            "raw_clean": "both",
        },
        "participant_split_fingerprint": "b" * 64,
        "participant_splits": [
            {
                "participant_id": "p1",
                "split": "train",
            }
        ],
    }


@pytest.mark.parametrize(
    "expected",
    [
        [],
        ["p1", "p1"],
    ],
)
def test_streaming_combiner_requires_unique_nonempty_expected_cohort(
    expected: list[str],
) -> None:
    with pytest.raises(
        ValueError,
        match="non-empty unique",
    ):
        streaming.combine_korthals_prepared_participants_v2(
            [],
            expected_participants=expected,
            source_identity=_source_identity(),
        )


def test_streaming_combiner_requires_matching_part_count() -> None:
    with pytest.raises(
        ValueError,
        match="prepared participant count differs",
    ):
        streaming.combine_korthals_prepared_participants_v2(
            [],
            expected_participants=["p1"],
            source_identity=_source_identity(),
        )


def test_streaming_combiner_requires_object_source_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        streaming,
        "canonical_json",
        lambda _value: "[]",
    )

    with pytest.raises(
        TypeError,
        match="normalize to an object",
    ):
        streaming.combine_korthals_prepared_participants_v2(
            [_local_part()],
            expected_participants=["p1"],
            source_identity=_source_identity(),
        )


def test_streaming_combiner_requires_prepared_objects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        streaming,
        "_endpoint_weights",
        lambda _data: np.array([0.0]),
    )

    with pytest.raises(
        TypeError,
        match="PreparedKorthalsData",
    ):
        streaming.combine_korthals_prepared_participants_v2(
            [object()],  # type: ignore[list-item]
            expected_participants=["p1"],
            source_identity=_source_identity(),
        )


def test_streaming_combiner_requires_one_participant_per_part() -> None:
    part = _local_part()
    part.data.loc[
        len(part.data)
    ] = {
        "participant_id": "p2",
        "trial_number": 1,
        "scheduled_trial_time": 0.0,
        "trial_time": 0.0,
        "error_group": "p2-v1",
    }

    with pytest.raises(
        ValueError,
        match="exactly one participant",
    ):
        streaming.combine_korthals_prepared_participants_v2(
            [part],
            expected_participants=["p1"],
            source_identity=_source_identity(),
        )


@pytest.mark.parametrize(
    ("part", "message"),
    [
        (
            _local_part(
                participant_count=2
            ),
            "declare one participant",
        ),
        (
            _local_part(
                case_study_id="wrong"
            ),
            "wrong case-study identity",
        ),
        (
            _local_part(
                protocol_fingerprint="wrong"
            ),
            "wrong protocol identity",
        ),
        (
            _local_part(
                missingness_policy="wrong"
            ),
            "wrong missingness policy",
        ),
    ],
)
def test_streaming_combiner_validates_local_identity(
    part: PreparedKorthalsData,
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        streaming.combine_korthals_prepared_participants_v2(
            [part],
            expected_participants=["p1"],
            source_identity=_source_identity(),
        )


def test_streaming_combiner_rejects_duplicate_validation_groups(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p1 = _local_part(
        "p1",
        error_group="shared",
    )
    p2 = _local_part(
        "p2",
        error_group="shared",
    )
    monkeypatch.setattr(
        streaming,
        "_endpoint_weights",
        lambda data: np.zeros(
            len(data)
        ),
    )

    with pytest.raises(
        ValueError,
        match="validation groups must remain unique",
    ):
        streaming.combine_korthals_prepared_participants_v2(
            [
                p1,
                p2,
            ],
            expected_participants=[
                "p1",
                "p2",
            ],
            source_identity=_source_identity(),
        )


def test_streaming_combiner_requires_validation_coverage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    part = _local_part()
    part.validation_groups.loc[
        0,
        "error_group",
    ] = "other"
    monkeypatch.setattr(
        streaming,
        "_endpoint_weights",
        lambda data: np.zeros(
            len(data)
        ),
    )

    with pytest.raises(
        ValueError,
        match="exactly cover retained error groups",
    ):
        streaming.combine_korthals_prepared_participants_v2(
            [part],
            expected_participants=["p1"],
            source_identity=_source_identity(),
        )


def test_streaming_combiner_rechecks_retained_participants_after_endpoint_step(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    part = _local_part()

    def mutate(
        data: pd.DataFrame,
    ) -> np.ndarray:
        data.loc[
            :,
            "participant_id",
        ] = "changed"
        return np.zeros(
            len(data)
        )

    monkeypatch.setattr(
        streaming,
        "_endpoint_weights",
        mutate,
    )

    with pytest.raises(
        ValueError,
        match="every source participant",
    ):
        streaming.combine_korthals_prepared_participants_v2(
            [part],
            expected_participants=["p1"],
            source_identity=_source_identity(),
        )


def test_streaming_companion_requires_data_directory_name(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wrong = tmp_path / "wrong"
    wrong.mkdir()
    monkeypatch.setattr(
        streaming,
        "_validated_data_root",
        lambda _value: wrong,
    )

    with pytest.raises(
        ValueError,
        match="named exactly 'data'",
    ):
        streaming.prepare_korthals_from_companion_v2_streaming(
            wrong,
            participant_factory=object,
            preprocessor_factory=object,
        )


def test_streaming_companion_imports_default_factories(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "data"
    root.mkdir()

    monkeypatch.setattr(
        streaming,
        "_validated_data_root",
        lambda _value: root,
    )
    monkeypatch.setattr(
        streaming,
        "build_korthals_source_manifest_v2",
        lambda _root: {
            "participants": [],
            "source_manifest_fingerprint": "a" * 64,
            "file_count": 0,
            "download_contract": {},
        },
    )

    calls: list[str] = []

    def import_module(
        name: str,
    ) -> SimpleNamespace:
        calls.append(name)
        if name.endswith(
            ".participant"
        ):
            return SimpleNamespace(
                Participant=object
            )
        return SimpleNamespace(
            OriginalPreprocessor=object
        )

    monkeypatch.setattr(
        streaming.importlib,
        "import_module",
        import_module,
    )

    with pytest.raises(
        ValueError,
        match="non-empty unique",
    ):
        streaming.prepare_korthals_from_companion_v2_streaming(
            root
        )

    assert calls == [
        "eyemovement_data.participant",
        "eyemovement_data.preprocessor",
    ]


class _Participant:
    def __init__(
        self,
        *,
        id: str,
        preprocessor: object,
        validation: pd.DataFrame,
        split: str = "train",
    ) -> None:
        self.id = id
        self.preprocessor = preprocessor
        self.validation = validation
        self.subset = split
        self.clean_data: dict[str, pd.DataFrame] = {}
        self.preprocessed_data: dict[str, pd.DataFrame] = {}

    def set_clean_data(
        self,
        _path: str,
    ) -> None:
        self.clean_data = {
            "gaze": pd.DataFrame(
                {
                    "x": [1]
                }
            )
        }

    def preprocess_clean_data(
        self,
        **_kwargs: object,
    ) -> None:
        self.preprocessed_data = {
            "gaze": pd.DataFrame(
                {
                    "x": [1]
                }
            )
        }

    def validation_check(
        self,
        _path: str,
    ) -> pd.DataFrame:
        return self.validation.copy()


def _streaming_harness(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    validation: pd.DataFrame,
    split: str = "train",
    local_participant: str = "p1",
    final_participant_count: int = 1,
):
    root = tmp_path / "data"
    root.mkdir()

    monkeypatch.setattr(
        streaming,
        "_validated_data_root",
        lambda _value: root,
    )
    monkeypatch.setattr(
        streaming,
        "build_korthals_source_manifest_v2",
        lambda _root: {
            "participants": ["p1"],
            "source_manifest_fingerprint": "a" * 64,
            "file_count": 2,
            "download_contract": {},
        },
    )
    monkeypatch.setattr(
        streaming,
        "_working_directory",
        lambda _path: nullcontext(),
    )
    monkeypatch.setattr(
        streaming,
        "_require_clean_tables",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        streaming,
        "_canonicalize_companion_participant_identity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        streaming,
        "_align_companion_preprocessed_participant",
        lambda *args, **kwargs: pd.DataFrame(
            {
                "participant_id": ["p1"],
            }
        ),
    )
    monkeypatch.setattr(
        streaming,
        "_scope_authoritative_task_trials",
        lambda frame: frame,
    )

    def factory(
        *,
        id: str,
        preprocessor: object,
    ) -> _Participant:
        return _Participant(
            id=id,
            preprocessor=preprocessor,
            validation=validation,
            split=split,
        )

    local = _local_part(
        local_participant
    )
    monkeypatch.setattr(
        streaming,
        "prepare_korthals_aligned_data_v2",
        lambda aligned, validation: local,
    )

    final = _local_part(
        "p1",
        participant_count=final_participant_count,
    )
    monkeypatch.setattr(
        streaming,
        "combine_korthals_prepared_participants_v2",
        lambda *args, **kwargs: final,
    )

    return root, factory


def test_streaming_companion_requires_validation_summary(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, factory = _streaming_harness(
        tmp_path,
        monkeypatch,
        validation=pd.DataFrame(),
    )

    with pytest.raises(
        ValueError,
        match="no validation summaries",
    ):
        streaming.prepare_korthals_from_companion_v2_streaming(
            root,
            participant_factory=factory,
            preprocessor_factory=object,
        )


def test_streaming_companion_requires_resolved_split(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, factory = _streaming_harness(
        tmp_path,
        monkeypatch,
        validation=pd.DataFrame(
            {
                "error_avg": [0.5],
            }
        ),
        split="unknown",
    )

    with pytest.raises(
        ValueError,
        match="unresolved train/test split",
    ):
        streaming.prepare_korthals_from_companion_v2_streaming(
            root,
            participant_factory=factory,
            preprocessor_factory=object,
        )


def test_streaming_companion_requires_local_identity_preservation(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, factory = _streaming_harness(
        tmp_path,
        monkeypatch,
        validation=pd.DataFrame(
            {
                "error_avg": [0.5],
            }
        ),
        local_participant="changed",
    )

    with pytest.raises(
        ValueError,
        match="local preparation changed identity",
    ):
        streaming.prepare_korthals_from_companion_v2_streaming(
            root,
            participant_factory=factory,
            preprocessor_factory=object,
        )


def test_streaming_companion_rechecks_final_participant_count(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, factory = _streaming_harness(
        tmp_path,
        monkeypatch,
        validation=pd.DataFrame(
            {
                "error_avg": [0.5],
            }
        ),
        final_participant_count=2,
    )

    with pytest.raises(
        ValueError,
        match="prepared participant count differs",
    ):
        streaming.prepare_korthals_from_companion_v2_streaming(
            root,
            participant_factory=factory,
            preprocessor_factory=object,
        )


# ---------------------------------------------------------------------------
# Plotting validation and optional-dependency paths
# ---------------------------------------------------------------------------


def test_pyplot_reports_optional_dependency_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = builtins.__import__

    def guarded_import(
        name,
        globals=None,
        locals=None,
        fromlist=(),
        level=0,
    ):
        if name == "matplotlib.pyplot":
            raise ImportError(
                "blocked for test"
            )
        return original(
            name,
            globals,
            locals,
            fromlist,
            level,
        )

    monkeypatch.setattr(
        builtins,
        "__import__",
        guarded_import,
    )

    with pytest.raises(
        ImportError,
        match="gazeaudit\[plot\]",
    ):
        plotting._pyplot()


@pytest.mark.parametrize(
    "frame",
    [
        pd.DataFrame(),
        pd.DataFrame(
            {
                "value": [
                    np.nan,
                ]
            }
        ),
    ],
)
def test_finite_numeric_rejects_missing_or_nonfinite_data(
    frame: pd.DataFrame,
) -> None:
    with pytest.raises(
        ValueError,
    ):
        plotting._finite_numeric(
            frame,
            "value",
        )


def test_qc_issue_profile_accepts_mapping_and_rejects_other_types() -> None:
    values = {
        "coordinate_issue_rows": 1,
        "timestamp_issue_rows": 2,
        "missing_identifier_rows": 3,
        "duplicate_timestamp_rows": 4,
        "decreasing_time_groups": 5,
    }
    fig = plotting.plot_qc_issue_profile(
        values
    )
    assert len(
        fig.axes
    ) == 1

    with pytest.raises(
        TypeError,
        match="StudyQCReport or a mapping",
    ):
        plotting.plot_qc_issue_profile(
            object()
        )


def test_trial_readiness_requires_positive_max_units() -> None:
    frame = pd.DataFrame(
        {
            "trial_unit_id": ["T1"],
            "any_row_issue_fraction": [0.1],
            "passes_thresholds": [True],
        }
    )

    with pytest.raises(
        ValueError,
        match="max_units must be positive",
    ):
        plotting.plot_trial_readiness(
            frame,
            max_units=0,
        )


def test_participant_readiness_requires_columns() -> None:
    with pytest.raises(
        ValueError,
        match="participant summary is missing columns",
    ):
        plotting.plot_participant_readiness(
            pd.DataFrame()
        )


def test_cohort_impact_rejects_unknown_metric() -> None:
    with pytest.raises(
        ValueError,
        match="metric must be",
    ):
        plotting.plot_cohort_impact(
            pd.DataFrame(),
            metric="unknown",
        )


def test_cohort_impact_requires_metric_columns() -> None:
    with pytest.raises(
        ValueError,
        match="cohort impact is missing columns",
    ):
        plotting.plot_cohort_impact(
            pd.DataFrame(
                {
                    "scope": ["trial"],
                }
            )
        )


def test_repair_comparison_requires_columns() -> None:
    with pytest.raises(
        ValueError,
        match="repair comparison is missing columns",
    ):
        plotting.plot_repair_comparison(
            pd.DataFrame()
        )


def test_repair_comparison_requires_selected_metric() -> None:
    frame = pd.DataFrame(
        {
            "metric": ["other"],
            "before": [1],
            "after": [0],
        }
    )

    with pytest.raises(
        ValueError,
        match="none of metric_names",
    ):
        plotting.plot_repair_comparison(
            frame
        )


def test_repair_comparison_requires_finite_values() -> None:
    frame = pd.DataFrame(
        {
            "metric": [
                "coordinate_issue_rows"
            ],
            "before": [
                np.nan
            ],
            "after": [
                0
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="finite numeric",
    ):
        plotting.plot_repair_comparison(
            frame
        )


def test_policy_tradeoffs_requires_columns() -> None:
    with pytest.raises(
        ValueError,
        match="policy table is missing columns",
    ):
        plotting.plot_policy_tradeoffs(
            pd.DataFrame()
        )


def test_gaze_trajectory_reports_patch_import_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = pd.DataFrame(
        {
            "x": [0.0],
            "y": [0.0],
            "timestamp": [0.0],
        }
    )

    class FakeFigure:
        def colorbar(
            self,
            *args,
            **kwargs,
        ) -> None:
            return None

    class FakeAxes:
        def plot(
            self,
            *args,
            **kwargs,
        ) -> None:
            return None

        def scatter(
            self,
            *args,
            **kwargs,
        ) -> object:
            return object()

        def __getattr__(
            self,
            _name: str,
        ):
            return lambda *args, **kwargs: None

    monkeypatch.setattr(
        plotting,
        "_new_axes",
        lambda **kwargs: (
            FakeFigure(),
            FakeAxes(),
        ),
    )

    original = builtins.__import__

    def guarded_import(
        name,
        globals=None,
        locals=None,
        fromlist=(),
        level=0,
    ):
        if (
            name == "matplotlib.patches"
            and "Circle" in fromlist
            and "Rectangle" in fromlist
        ):
            raise ImportError(
                "blocked for test"
            )
        return original(
            name,
            globals,
            locals,
            fromlist,
            level,
        )

    monkeypatch.setattr(
        builtins,
        "__import__",
        guarded_import,
    )

    with pytest.raises(
        ImportError,
        match="AOI overlays",
    ):
        plotting.plot_gaze_trajectory(
            frame,
            aoi=RectangleAOI(
                "target",
                -1.0,
                -1.0,
                1.0,
                1.0,
            ),
        )


def test_gaze_trajectory_draws_circle_overlay() -> None:
    frame = pd.DataFrame(
        {
            "x": [
                0.0,
                1.0,
            ],
            "y": [
                0.0,
                1.0,
            ],
            "timestamp": [
                0.0,
                1.0,
            ],
        }
    )

    fig = plotting.plot_gaze_trajectory(
        frame,
        aoi=CircleAOI(
            "target",
            0.0,
            0.0,
            1.0,
        ),
    )

    assert len(
        fig.axes[0].patches
    ) == 1


def test_gaze_trajectory_rejects_unknown_aoi_type() -> None:
    frame = pd.DataFrame(
        {
            "x": [0.0],
            "y": [0.0],
            "timestamp": [0.0],
        }
    )

    with pytest.raises(
        TypeError,
        match="RectangleAOI, CircleAOI, or None",
    ):
        plotting.plot_gaze_trajectory(
            frame,
            aoi=object(),  # type: ignore[arg-type]
        )


def test_recovery_matrix_requires_columns() -> None:
    with pytest.raises(
        ValueError,
        match="recovery table is missing columns",
    ):
        plotting.plot_recovery_matrix(
            pd.DataFrame(),
            row_col="row",
            column_col="column",
            value_col="value",
        )


def test_recovery_matrix_requires_complete_finite_matrix() -> None:
    frame = pd.DataFrame(
        {
            "row": [
                "a",
                "b",
            ],
            "column": [
                "x",
                "y",
            ],
            "value": [
                1.0,
                np.nan,
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="complete and finite",
    ):
        plotting.plot_recovery_matrix(
            frame,
            row_col="row",
            column_col="column",
            value_col="value",
        )
