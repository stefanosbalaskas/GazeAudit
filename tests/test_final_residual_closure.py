from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import gazeaudit.gazebase_execution as ge
import gazeaudit.korthals_execution as ke
import gazeaudit.korthals_freeze as kf
import gazeaudit.korthals_freeze_v2 as kf2
import gazeaudit.korthals_osf as kosf
import gazeaudit.pedrotti_execution as pe
import gazeaudit.pedrotti_freeze as pf
import gazeaudit.readiness as readiness

ROOT = Path(__file__).resolve().parents[1]
K = runpy.run_path(str(ROOT / "tests" / "test_bulk_korthals_execution_coverage.py"))
P = runpy.run_path(str(ROOT / "tests" / "test_bulk_pedrotti_execution_coverage.py"))
R = runpy.run_path(str(ROOT / "tests" / "test_bulk_readiness_coverage.py"))

_k_prepared = K["_prepared"]
_k_execution = K["_execution"]
_k_aligned = K["_aligned_fixture"]
_k_validation = K["_validation_fixture"]
_p_trial = P["_trial"]
_p_synthetic = P["_synthetic_prepared"]
_p_execution36 = P["_execution36"]
_readiness_demo = R["_demo"]


class _BadPandas:
    def to_pandas(self) -> object:
        return object()


def test_gazebase_to_pandas_requires_dataframe_result() -> None:
    with pytest.raises(TypeError, match="must return a pandas DataFrame"):
        ge._to_pandas_frame(_BadPandas(), "demo")


def test_korthals_prepare_post_filter_and_validation_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol = ke.load_korthals_protocol()
    excluded_id = str(
        protocol["dataset"]["author_directed_exclusion"]["participant_id"]
    )
    frame = _k_aligned(participants=(excluded_id,)).iloc[:2].copy()
    start = int(
        protocol["dataset"]["author_directed_exclusion"]["trial_number_start"]
    )
    end = int(
        protocol["dataset"]["author_directed_exclusion"]["trial_number_end"]
    )
    assert start + 1 <= end
    frame["trial_number"] = [start, start + 1]
    frame["target_type"] = ["moving_circle", "jumping_circle"]
    monkeypatch.setattr(
        ke,
        "_normalize_aligned_data",
        lambda _frame: frame.copy(),
    )
    monkeypatch.setattr(ke, "_require_complete_trial_pairing", lambda _frame: None)
    with pytest.raises(ValueError, match="remain after filtering"):
        ke.prepare_korthals_aligned_data(
            frame,
            _k_validation(participants=(excluded_id,)),
        )

    monkeypatch.undo()
    one_type = _k_aligned(participants=("p1",))
    original = ke._normalize_aligned_data

    def normalized(_frame: pd.DataFrame) -> pd.DataFrame:
        result = original(one_type)
        return result.loc[result["target_type"] == "moving_circle"].copy()

    monkeypatch.setattr(ke, "_normalize_aligned_data", normalized)
    monkeypatch.setattr(ke, "_require_complete_trial_pairing", lambda _frame: None)
    with pytest.raises(ValueError, match="both frozen target types"):
        ke.prepare_korthals_aligned_data(
            one_type,
            _k_validation(participants=("p1",)),
        )


def test_korthals_sampling_remaining_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = _k_aligned(participants=("p1",))
    monkeypatch.setattr(
        ke,
        "_downsample_trial_50hz",
        lambda trial: trial.assign(target_x=np.nan),
    )
    with pytest.raises(ValueError, match="target coordinates"):
        ke.prepare_korthals_aligned_data(
            data,
            _k_validation(participants=("p1",)),
        )

    trial = pd.DataFrame(
        {
            "trial_time": [0.011, 0.02],
            "x": [1, 2],
        }
    )
    sampled = ke._downsample_trial_50hz(trial)
    assert sampled.iloc[0]["x"] == 1

    late = pd.DataFrame(
        {
            "trial_time": [0.0, 0.021],
            "x": [1, 2],
        }
    )
    sampled = ke._downsample_trial_50hz(late)
    assert len(sampled) == 2


def test_korthals_writer_overwrite_and_verifier_remaining_paths(
    tmp_path: Path,
) -> None:
    execution = _k_execution()
    root = tmp_path / "archive"
    root.mkdir()
    (root / "old.txt").write_text("old", encoding="utf-8")
    ke.write_korthals_execution_artifacts(
        execution,
        root,
        overwrite=True,
    )
    assert not (root / "old.txt").exists()

    manifest_path = root / "artifact_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["schema"] = "wrong"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert not ke.verify_korthals_execution_artifacts(root)


def test_korthals_endpoint_missing_participant_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _k_prepared()
    data = prepared.data.copy()

    original_meta = ke._trial_metadata

    def incomplete_meta(frame: pd.DataFrame) -> pd.DataFrame:
        meta = original_meta(frame)
        return meta.loc[meta["participant_id"] != meta["participant_id"].iloc[-1]].copy()

    monkeypatch.setattr(ke, "_trial_metadata", incomplete_meta)
    with pytest.raises(ValueError):
        ke._endpoint_weights(data)


def test_pedrotti_trial_duration_and_locked_entrypoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_isfinite = pe.np.isfinite

    def controlled_isfinite(value):
        if np.isscalar(value):
            return False
        return original_isfinite(value)

    monkeypatch.setattr(
        pe.np,
        "isfinite",
        controlled_isfinite,
    )
    with pytest.raises(ValueError, match="duration"):
        pe.make_pedrotti_trial(
            "01",
            1,
            "short",
            [0.0, 1.0],
            [0.0, 1.0],
            [0.0, 1.0],
        )

    monkeypatch.undo()
    sentinel = object()
    monkeypatch.setattr(pe, "inspect_pedrotti_source", lambda _root: sentinel)
    monkeypatch.setattr(pe, "verify_pedrotti_locked_intake", lambda intake, **kwargs: intake)
    monkeypatch.setattr(pe, "prepare_pedrotti_execution_data", lambda _root, _intake: sentinel)
    monkeypatch.setattr(pe, "_verify_locked_prepared", lambda prepared, **kwargs: prepared)
    assert pe.prepare_pedrotti_locked_execution_data("source") is sentinel


def test_pedrotti_missingness_zero_and_negative_numerator_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trial = _p_trial()
    native = pe._trial_rate_missingness(
        trial,
        mechanism="mcar_within_trial",
        fraction=0.0,
        replicate=1,
        root_seed=1,
    )
    assert native == pytest.approx(pe._trial_rate_native(trial))

    monkeypatch.setattr(
        pe,
        "_added_missingness_positions",
        lambda *args, **kwargs: np.array([0], dtype=int),
    )
    bad = copy.copy(trial)
    object.__setattr__(
        bad,
        "edge_distance",
        np.array(
            [1000.0, -2000.0]
            + [0.0] * (len(trial.edge_distance) - 2)
        ),
    )
    with pytest.raises(RuntimeError, match="negative path numerator"):
        pe._trial_rate_missingness(
            bad,
            mechanism="mcar_within_trial",
            fraction=0.5,
            replicate=1,
            root_seed=1,
        )


def test_pedrotti_missingness_position_remaining_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trial = _p_trial()
    result = pe._added_missingness_positions(
        trial,
        mechanism="mcar_within_trial",
        fraction=0.0,
        replicate=1,
        root_seed=1,
    )
    assert result.size == 0

    class BadGenerator:
        def integers(self, *args, **kwargs) -> int:
            return 10**9

    monkeypatch.setattr(
        pe.np.random,
        "default_rng",
        lambda _seed: BadGenerator(),
    )
    with pytest.raises(RuntimeError, match="failed exact finite-sample target"):
        pe._added_missingness_positions(
            trial,
            mechanism="single_block_within_trial",
            fraction=0.5,
            replicate=1,
            root_seed=1,
        )


def test_pedrotti_archive_verifier_remaining_identity_branches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    execution = _p_execution36()
    monkeypatch.setattr(pe, "_verify_locked_prepared", lambda value, **kwargs: value)
    monkeypatch.setattr(
        pe,
        "verify_pedrotti_source_lock",
        lambda: {
            "source": {
                "source_manifest_fingerprint": execution.prepared.source_identity[
                    "source_manifest_fingerprint"
                ]
            }
        },
    )

    context = {
        "schema": "gazeaudit-pedrotti-execution-context-v1",
        "execution_commit": "a" * 40,
        "workflow_ref": pe.PEDROTTI_EXECUTION_WORKFLOW,
        "github_run_id": 1,
        "runner_os": "Linux",
        "runner_arch": "X64",
        "python": "3.12.14",
    }

    root = tmp_path / "archive"
    pe.write_pedrotti_locked_execution_artifacts(
        execution,
        root,
        execution_context=context,
        environment_text="numpy==2.5.3\npandas==2.3.3\n",
    )

    source_path = root / "source_identity.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["participant_count"] = 35
    source_path.write_text(pe.canonical_json(source) + "\n", encoding="utf-8")
    assert not pe.verify_pedrotti_locked_execution_artifacts(root)


def test_readiness_exception_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    demo = _readiness_demo()
    comparison = demo["repair_comparison"]
    report = demo["readiness"]

    original = readiness.fingerprint
    monkeypatch.setattr(
        readiness,
        "fingerprint",
        lambda _value: (_ for _ in ()).throw(ValueError("forced")),
    )
    assert not readiness.verify_repair_comparison_manifest(comparison.manifest)
    assert not readiness.verify_analysis_readiness_manifest(report.manifest)
    monkeypatch.setattr(readiness, "fingerprint", original)


def test_freeze_verifier_exception_and_forbidden_token_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cases = [
        (
            kf,
            kf.verify_korthals_source_freeze_artifacts,
            "verify_korthals_source_intake_artifacts",
        ),
        (
            kf2,
            kf2.verify_korthals_source_freeze_artifacts_v2,
            "verify_korthals_source_intake_artifacts_v2",
        ),
        (
            pf,
            pf.verify_pedrotti_source_freeze_artifacts,
            "verify_pedrotti_source_intake_artifacts",
        ),
    ]

    for module, verifier, intake_verifier in cases:
        root = tmp_path / module.__name__.split(".")[-1]
        (root / "intake").mkdir(parents=True)
        for name in (
            "execution_context.json",
            "pip_freeze.txt",
            "freeze_manifest.json",
            "SHA256SUMS",
        ):
            (root / name).write_text("x", encoding="utf-8")

        monkeypatch.setattr(
            module,
            intake_verifier,
            lambda _path: True,
        )
        monkeypatch.setattr(
            module,
            "_read_json",
            lambda _path: (_ for _ in ()).throw(ValueError("forced")),
        )
        assert verifier(root) is False
        monkeypatch.undo()


def test_osf_retry_exhaustion_is_explicit() -> None:
    item = kosf.KorthalsRemoteFile(
        remote_path="/raw/a.bin",
        destination="data/raw/a.bin",
        md5="0" * 32,
        sha256=None,
    )
    with pytest.raises(RuntimeError, match="failed after 1 attempts"):
        kosf.fetch_korthals_osf_resumable(
            max_attempts=1,
            initial_backoff_seconds=0,
            inventory_fn=lambda: (item,),
            download_fn=lambda: (_ for _ in ()).throw(RuntimeError("network")),
            sleep_fn=lambda _seconds: None,
        )
