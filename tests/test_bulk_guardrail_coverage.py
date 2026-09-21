from __future__ import annotations

import copy
import json

import numpy as np
import pandas as pd
import pytest

import gazeaudit.bids_adapter as bids
import gazeaudit.conclusion as conclusion
import gazeaudit.korthals_source_lock as korthals_lock
import gazeaudit.missingness as missingness
import gazeaudit.pedrotti_source_lock as pedrotti_lock
import gazeaudit.provenance as provenance
import gazeaudit.robustness as robustness
import gazeaudit.scientific_benchmark as benchmark
from gazeaudit.study import GazeStudy


class _FakeJsonResource:
    def __init__(self, payload: str) -> None:
        self.payload = payload

    def joinpath(self, _name: str) -> _FakeJsonResource:
        return self

    def read_text(self, *, encoding: str) -> str:
        assert encoding == "utf-8"
        return self.payload


class _StubbornBlockGenerator:
    """Exercise deterministic block fallback without relying on RNG luck."""

    def integers(
        self,
        low: int,
        high: int | None = None,
        *args: object,
        **kwargs: object,
    ) -> int:
        del args, kwargs
        if low == 0:
            return 0
        assert high is not None
        return 1

    def choice(
        self,
        values: np.ndarray,
        *,
        size: int,
        replace: bool,
    ) -> np.ndarray:
        assert replace is False
        return np.asarray(values)[:size]


def _minimal_study(*, with_reason_column: bool = False) -> GazeStudy:
    data = pd.DataFrame(
        {
            "participant": ["p1"] * 5,
            "trial": [1] * 5,
            "timestamp": np.arange(5, dtype=float),
            "x": np.arange(5, dtype=float),
            "y": np.zeros(5, dtype=float),
        }
    )
    if with_reason_column:
        data["missing_reason"] = pd.Series(
            [pd.NA] * len(data),
            dtype="object",
        )
    return GazeStudy(data)


# ---------------------------------------------------------------------------
# BIDS ingestion
# ---------------------------------------------------------------------------


def test_bids_empty_frame_after_successful_parser_fails_closed(
    tmp_path: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    physio = tmp_path / "sub-01_task-demo_recording-left_physio.tsv"
    sidecar = tmp_path / "sub-01_task-demo_recording-left_physio.json"
    physio.write_text("placeholder\n", encoding="utf-8")
    sidecar.write_text(
        json.dumps(
            {
                "PhysioType": "eyetrack",
                "SamplingFrequency": 60,
                "StartTime": 0,
                "Columns": [
                    "timestamp",
                    "x_coordinate",
                    "y_coordinate",
                ],
                "RecordedEye": "left",
                "SampleCoordinateSystem": "screen",
                "timestamp": {"Units": "s"},
                "x_coordinate": {"Units": "px"},
                "y_coordinate": {"Units": "px"},
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bids.pd,
        "read_csv",
        lambda *args, **kwargs: pd.DataFrame(columns=range(3)),
    )

    with pytest.raises(
        ValueError,
        match="at least one row",
    ):
        bids.read_bids_eyetrack(
            physio,
            sidecar_path=sidecar,
        )


# ---------------------------------------------------------------------------
# Robustness summaries
# ---------------------------------------------------------------------------


def test_marginal_sensitivity_rejects_unknown_factor() -> None:
    frame = pd.DataFrame(
        {
            "estimate": [1.0, 2.0],
            "known": ["a", "b"],
        }
    )

    with pytest.raises(
        ValueError,
        match="factor 'missing'.*not present",
    ):
        robustness.marginal_sensitivity(
            frame,
            ["missing"],
        )


def test_estimate_array_rejects_missing_estimate_column() -> None:
    with pytest.raises(
        ValueError,
        match="column 'estimate'.*not present",
    ):
        robustness._estimate_array(
            pd.DataFrame({"other": [1.0]}),
            "estimate",
        )


def test_estimate_array_rejects_empty_specification_set() -> None:
    with pytest.raises(
        ValueError,
        match="at least one specification",
    ):
        robustness._estimate_array(
            pd.DataFrame({"estimate": []}),
            "estimate",
        )


# ---------------------------------------------------------------------------
# Known-truth scientific benchmark
# ---------------------------------------------------------------------------


def test_condition_dwell_effect_requires_contract_columns() -> None:
    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        benchmark.condition_dwell_effect(
            pd.DataFrame(
                {
                    "participant": ["p1"],
                    "duration": [1.0],
                }
            ),
            np.ones(1),
        )


def test_condition_dwell_effect_requires_a_complete_within_person_pair() -> None:
    data = pd.DataFrame(
        {
            "participant": ["p1", "p2"],
            "condition": ["control", "treatment"],
            "duration": [100.0, 100.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="no participant has both control and treatment data",
    ):
        benchmark.condition_dwell_effect(
            data,
            np.ones(2),
        )


def test_known_aoi_benchmark_requires_truth_and_observed_coordinates() -> None:
    data = pd.DataFrame(
        {
            "participant": ["p1", "p1"],
            "condition": ["control", "treatment"],
            "duration": [100.0, 100.0],
            "true_x": [0.0, 1.0],
            "true_y": [0.0, 0.0],
            "observed_x": [0.0, 1.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        benchmark.benchmark_known_aoi_effect(
            data,
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
        )


def test_known_aoi_benchmark_rejects_nonfinite_coordinates() -> None:
    data = pd.DataFrame(
        {
            "participant": ["p1", "p1"],
            "condition": ["control", "treatment"],
            "duration": [100.0, 100.0],
            "true_x": [0.0, np.nan],
            "true_y": [0.0, 0.0],
            "observed_x": [0.0, 1.0],
            "observed_y": [0.0, 0.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="coordinates must be finite",
    ):
        benchmark.benchmark_known_aoi_effect(
            data,
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
        )


def test_scientific_benchmark_rng_helper_preserves_generator() -> None:
    generator = np.random.default_rng(123)
    assert benchmark._as_rng(generator) is generator


# ---------------------------------------------------------------------------
# Deterministic provenance
# ---------------------------------------------------------------------------


def test_specification_manifest_supports_absent_optional_endpoint() -> None:
    manifest = provenance.specification_manifest(
        {"detector": "ivt"},
    )

    assert "endpoint" not in manifest
    assert "metadata" not in manifest


def test_software_environment_falls_back_when_distribution_is_uninstalled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing_version(_name: str) -> str:
        raise provenance.PackageNotFoundError

    monkeypatch.setattr(
        provenance,
        "version",
        missing_version,
    )

    environment = provenance.software_environment()

    assert environment["gazeaudit"] == "uninstalled"


def test_provenance_normalizes_numpy_scalar() -> None:
    assert provenance._normalize(np.int64(7)) == 7


def test_provenance_normalizes_numpy_array() -> None:
    assert provenance._normalize(
        np.array([1, 2], dtype=np.int64)
    ) == [1, 2]


def test_provenance_normalizes_timestamp() -> None:
    timestamp = pd.Timestamp("2026-09-21T10:00:00")
    assert provenance._normalize(timestamp) == timestamp.isoformat()


def test_provenance_normalizes_missing_scalar_to_none() -> None:
    assert provenance._normalize(pd.NA) is None


# ---------------------------------------------------------------------------
# Conclusion-recovery guardrails
# ---------------------------------------------------------------------------


def _valid_recovery_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "absolute_error": [0.1],
            "relative_error": [0.1],
            "sign_recovered": [True],
            "sign_flipped": [False],
            "tolerance_recovered": [True],
            "conclusion_recovered": [True],
        }
    )


def test_conclusion_summary_requires_all_recovery_columns() -> None:
    frame = _valid_recovery_frame().drop(
        columns=["sign_flipped"]
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        conclusion.summarize_conclusion_recovery(
            frame,
            conclusion.ConclusionRule(
                relative_tolerance=0.2
            ),
        )


def test_conclusion_summary_rejects_empty_recovery_set() -> None:
    frame = _valid_recovery_frame().iloc[0:0].copy()

    with pytest.raises(
        ValueError,
        match="at least one specification",
    ):
        conclusion.summarize_conclusion_recovery(
            frame,
            conclusion.ConclusionRule(
                relative_tolerance=0.2
            ),
        )


def test_canonical_conclusion_benchmark_uses_default_rule() -> None:
    result = conclusion.run_canonical_conclusion_benchmark(
        "robust",
        rule=None,
        n_participants=8,
        trials_per_condition=3,
        draws=2,
        rng=123,
    )

    assert result.case == "robust"
    assert result.summary["minimum_recovery_fraction"] == pytest.approx(
        0.90
    )


def test_known_truth_validator_rejects_missing_schema() -> None:
    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        conclusion._validate_known_truth_data(
            pd.DataFrame(
                {
                    "participant": ["p1"],
                    "condition": ["control"],
                }
            )
        )


def test_known_truth_validator_rejects_empty_frame() -> None:
    frame = pd.DataFrame(
        columns=[
            "participant",
            "condition",
            "duration",
            "true_x",
            "true_y",
            "observed_x",
            "observed_y",
        ]
    )

    with pytest.raises(
        ValueError,
        match="at least one row",
    ):
        conclusion._validate_known_truth_data(frame)


def test_known_truth_validator_rejects_nonfinite_coordinate() -> None:
    frame = pd.DataFrame(
        {
            "participant": ["p1"],
            "condition": ["control"],
            "duration": [100.0],
            "true_x": [np.inf],
            "true_y": [0.0],
            "observed_x": [0.0],
            "observed_y": [0.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="coordinates must be finite",
    ):
        conclusion._validate_known_truth_data(frame)


def test_conclusion_rng_helper_preserves_generator() -> None:
    generator = np.random.default_rng(321)
    assert conclusion._as_rng(generator) is generator


# ---------------------------------------------------------------------------
# Missingness fallback paths
# ---------------------------------------------------------------------------


def test_missingness_reason_reuses_existing_reason_column() -> None:
    study = _minimal_study(
        with_reason_column=True
    )

    result = missingness.inject_missingness(
        study,
        0.4,
        rng=7,
        reason="quality_loss",
    )

    masked = result.data["x"].isna()
    assert int(masked.sum()) == 2
    assert (
        result.data.loc[
            masked,
            "missing_reason",
        ]
        == "quality_loss"
    ).all()


def test_block_positions_returns_empty_when_no_complete_rows() -> None:
    study = _minimal_study()
    data = study.data.copy()
    data[["x", "y"]] = np.nan
    all_missing = study.copy_with(data)

    selected = missingness._block_positions(
        all_missing,
        2,
        np.random.default_rng(1),
    )

    assert selected.size == 0


def test_block_positions_falls_back_after_repeated_duplicate_block_draws() -> None:
    selected = missingness._block_positions(
        _minimal_study(),
        3,
        _StubbornBlockGenerator(),  # type: ignore[arg-type]
    )

    np.testing.assert_array_equal(
        selected,
        np.array([0, 1, 2]),
    )


def test_missingness_rng_helper_preserves_generator() -> None:
    generator = np.random.default_rng(55)
    assert missingness._as_rng(generator) is generator


# ---------------------------------------------------------------------------
# Immutable Korthals source-lock guardrails
# ---------------------------------------------------------------------------


def test_korthals_packaged_lock_loader_rejects_nonobject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        korthals_lock.resources,
        "files",
        lambda _package: _FakeJsonResource("[]"),
    )

    with pytest.raises(
        ValueError,
        match="JSON object",
    ):
        korthals_lock.load_korthals_source_lock()


def test_korthals_lock_normalization_requires_object() -> None:
    with pytest.raises(
        TypeError,
        match="normalize to an object",
    ):
        korthals_lock.verify_korthals_source_lock(
            []  # type: ignore[arg-type]
        )


def test_korthals_lock_rejects_wrong_immutable_fingerprint() -> None:
    lock = copy.deepcopy(
        korthals_lock.load_korthals_source_lock()
    )
    lock["lock_fingerprint"] = "0" * 64

    with pytest.raises(
        ValueError,
        match="wrong immutable fingerprint",
    ):
        korthals_lock.verify_korthals_source_lock(lock)


def test_korthals_lock_guardrails_fail_closed_after_fingerprint_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lock = copy.deepcopy(
        korthals_lock.load_korthals_source_lock()
    )
    lock["environment"]["pandas"] = "unexpected"

    monkeypatch.setattr(
        korthals_lock,
        "fingerprint",
        lambda _value: korthals_lock.KORTHALS_SOURCE_LOCK_FINGERPRINT,
    )

    with pytest.raises(
        ValueError,
        match="failed guardrails",
    ):
        korthals_lock.verify_korthals_source_lock(lock)


def test_korthals_locked_manifest_rejects_failed_protocol_verification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        korthals_lock,
        "verify_korthals_source_manifest_v2",
        lambda _manifest: False,
    )

    with pytest.raises(
        ValueError,
        match="protocol-v2 verification",
    ):
        korthals_lock.verify_korthals_locked_source_manifest({})


def test_korthals_locked_prepared_requires_prepared_contract_type() -> None:
    with pytest.raises(
        TypeError,
        match="PreparedKorthalsData",
    ):
        korthals_lock.verify_korthals_locked_prepared(
            object()  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Immutable Pedrotti source-lock guardrails
# ---------------------------------------------------------------------------


def test_pedrotti_packaged_lock_loader_rejects_nonobject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        pedrotti_lock.resources,
        "files",
        lambda _package: _FakeJsonResource("[]"),
    )

    with pytest.raises(
        ValueError,
        match="JSON object",
    ):
        pedrotti_lock.load_pedrotti_source_lock()


def test_pedrotti_lock_normalization_requires_object() -> None:
    with pytest.raises(
        TypeError,
        match="normalize to an object",
    ):
        pedrotti_lock.verify_pedrotti_source_lock(
            []  # type: ignore[arg-type]
        )


def test_pedrotti_lock_rejects_wrong_immutable_fingerprint() -> None:
    lock = copy.deepcopy(
        pedrotti_lock.load_pedrotti_source_lock()
    )
    lock["lock_fingerprint"] = "0" * 64

    with pytest.raises(
        ValueError,
        match="wrong immutable fingerprint",
    ):
        pedrotti_lock.verify_pedrotti_source_lock(lock)


def test_pedrotti_lock_guardrails_fail_closed_after_fingerprint_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lock = copy.deepcopy(
        pedrotti_lock.load_pedrotti_source_lock()
    )
    lock["environment"]["pandas"] = "unexpected"

    monkeypatch.setattr(
        pedrotti_lock,
        "fingerprint",
        lambda _value: pedrotti_lock.PEDROTTI_SOURCE_LOCK_FINGERPRINT,
    )

    with pytest.raises(
        ValueError,
        match="failed guardrails",
    ):
        pedrotti_lock.verify_pedrotti_source_lock(lock)
