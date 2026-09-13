from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

import gazeaudit.pedrotti_execution as execution_module
import gazeaudit.pedrotti_execution_cli as execution_cli
import gazeaudit.pedrotti_reveal_cli as reveal_cli
from gazeaudit.pedrotti_execution import (
    PEDROTTI_EXECUTION_WORKFLOW,
    PreparedPedrottiData,
    _added_missingness_positions,
    _child_seed,
    _trial_rate_missingness,
    _trial_rate_native,
    _trial_rate_sampled,
    execution_context,
    make_pedrotti_trial,
    reveal_pedrotti_locked_execution,
    run_pedrotti_scientific_execution,
    verify_pedrotti_locked_execution_artifacts,
    write_pedrotti_locked_execution_artifacts,
)
from gazeaudit.pedrotti_source import (
    PEDROTTI_CASE_STUDY_ID,
    PEDROTTI_PROTOCOL_FINGERPRINT,
)
from gazeaudit.pedrotti_source_lock import (
    PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT,
    PEDROTTI_SOURCE_LOCK_FINGERPRINT,
)


def _trial(
    participant: str = "01",
    trial_index: int = 1,
    condition: str = "short",
    *,
    scale: float = 1.0,
    missing: tuple[int, ...] = (),
    n: int = 21,
):
    times = np.arange(n, dtype=float)
    x = scale * np.arange(n, dtype=float)
    y = np.zeros(n, dtype=float)
    if missing:
        x[list(missing)] = np.nan
        y[list(missing)] = np.nan
    return make_pedrotti_trial(
        participant,
        trial_index,
        condition,
        times,
        x,
        y,
    )


def _synthetic_prepared(participants: int = 2) -> PreparedPedrottiData:
    ids = tuple(f"{index:02d}" for index in range(1, participants + 1))
    trials = []
    for index, participant in enumerate(ids, start=1):
        trials.append(_trial(participant, 1, "short", scale=1.0 + index * 0.01))
        trials.append(_trial(participant, 2, "long", scale=2.0 + index * 0.01))
    return PreparedPedrottiData(
        source_identity={
            "case_study_id": "synthetic-pedrotti",
            "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
            "source_manifest_fingerprint": "synthetic",
        },
        trials=tuple(trials),
        participant_ids=ids,
    )


def _locked_shape_identity() -> dict[str, object]:
    return {
        "case_study_id": PEDROTTI_CASE_STUDY_ID,
        "protocol_fingerprint": PEDROTTI_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT,
        "participant_count": 36,
        "source_file_count": 37,
        "total_row_count": 13149347,
        "total_trial_count": 3456,
        "short_numeric_trial_count": 864,
        "long_numeric_trial_count": 864,
        "numeric_trial_count": 1728,
        "eye_counts": {"left": 20, "right": 16},
        "scientific_endpoint_evaluated_before_preparation": False,
    }


def test_native_path_never_bridges_published_missingness() -> None:
    trial = _trial(missing=(10,))
    # Two nine-pixel finite segments across a 20 ms source duration.
    assert _trial_rate_native(trial) == pytest.approx(18.0 / 0.020)


def test_sampling_uses_earlier_row_on_tie_and_original_duration() -> None:
    trial = make_pedrotti_trial(
        "01",
        1,
        "short",
        [0.0, 1.0, 3.0],
        [0.0, 1.0, 3.0],
        [0.0, 0.0, 0.0],
    )
    # The 2 ms grid point is tied between source rows at 1 and 3 ms.
    # Frozen tie handling chooses the earlier row (1 ms), while the denominator
    # remains the original 3 ms duration.
    assert _trial_rate_sampled(trial, 500.0) == pytest.approx(1.0 / 0.003)


@pytest.mark.parametrize("mechanism", ["mcar_within_trial", "single_block_within_trial"])
def test_added_missingness_masks_exact_finite_count_without_native_rows(
    mechanism: str,
) -> None:
    trial = _trial(missing=(4, 11), n=20)
    selected = _added_missingness_positions(
        trial,
        mechanism=mechanism,
        fraction=0.20,
        replicate=3,
        root_seed=20260913,
    )
    assert selected.size == round(0.20 * trial.finite_positions.size)
    assert np.all(trial.finite_mask[selected])
    assert np.array_equal(
        selected,
        _added_missingness_positions(
            trial,
            mechanism=mechanism,
            fraction=0.20,
            replicate=3,
            root_seed=20260913,
        ),
    )
    if mechanism == "single_block_within_trial":
        finite_indices = np.searchsorted(trial.finite_positions, selected)
        assert np.all(np.diff(finite_indices) == 1)


def test_missingness_path_removes_only_edges_adjacent_to_new_masks() -> None:
    trial = _trial(n=10)
    selected = _added_missingness_positions(
        trial,
        mechanism="mcar_within_trial",
        fraction=0.10,
        replicate=1,
        root_seed=20260913,
    )
    assert selected.size == 1
    adjacent = np.unique(
        np.concatenate((selected - 1, selected))
    )
    adjacent = adjacent[(adjacent >= 0) & (adjacent < len(trial.edge_distance))]
    expected = (
        trial.edge_distance.sum() - trial.edge_distance[adjacent].sum()
    ) / trial.duration_seconds
    observed = _trial_rate_missingness(
        trial,
        mechanism="mcar_within_trial",
        fraction=0.10,
        replicate=1,
        root_seed=20260913,
    )
    assert observed == pytest.approx(expected)


def test_child_seed_is_specification_keyed_and_loop_order_independent() -> None:
    first = _child_seed(20260913, "01", 12, "mcar_within_trial", 0.05, 7)
    second = _child_seed(20260913, "01", 12, "mcar_within_trial", 0.05, 7)
    changed = _child_seed(20260913, "01", 12, "mcar_within_trial", 0.10, 7)
    assert first == second
    assert first != changed


def test_synthetic_execution_runs_full_frozen_grid_deterministically() -> None:
    prepared = _synthetic_prepared()
    first = run_pedrotti_scientific_execution(prepared)
    second = run_pedrotti_scientific_execution(prepared)

    assert len(first.sampling_results) == 5
    assert len(first.missingness_results) == 160
    assert len(first.family_recovery) == 9
    assert first.classification in {
        "robust",
        "materially_fragile",
        "mixed",
        "indeterminate_reference_zero",
    }
    assert first.execution_fingerprint == second.execution_fingerprint
    assert first.reference == second.reference
    assert first.missingness_results == second.missingness_results


def test_reference_zero_uses_predeclared_indeterminate_rule() -> None:
    ids = ("01", "02")
    trials = []
    for participant in ids:
        trials.append(_trial(participant, 1, "short", scale=1.0))
        trials.append(_trial(participant, 2, "long", scale=1.0))
    prepared = PreparedPedrottiData(
        {"source_manifest_fingerprint": "synthetic-reference-zero"},
        tuple(trials),
        ids,
    )

    execution = run_pedrotti_scientific_execution(prepared)

    assert execution.reference["study_estimate"] == 0.0
    assert execution.classification == "indeterminate_reference_zero"
    assert all(row["relative_deviation"] is None for row in execution.sampling_results)
    assert all(row["recovered"] is None for row in execution.missingness_results)


def test_execution_context_is_pinned_to_manual_workflow() -> None:
    context = {
        "schema": "gazeaudit-pedrotti-execution-context-v1",
        "execution_commit": "a" * 40,
        "workflow_ref": PEDROTTI_EXECUTION_WORKFLOW,
        "github_run_id": 123,
        "runner_os": "Linux",
        "runner_arch": "X64",
        "python": "3.12.14",
    }
    assert execution_module._validated_execution_context(context) == context
    bad = dict(context)
    bad["workflow_ref"] = ".github/workflows/tests.yml"
    with pytest.raises(ValueError, match="workflow"):
        execution_module._validated_execution_context(bad)


def test_locked_archive_round_trip_is_checksummed_and_semantically_verified(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared_core = _synthetic_prepared(participants=36)
    prepared = replace(prepared_core, source_identity=_locked_shape_identity())
    execution = run_pedrotti_scientific_execution(prepared)

    # Archive mechanics are synthetic-qualified without pretending that the 72
    # tiny synthetic trials are the locked 1,728 real numeric trials.
    manifest_core = dict(execution.execution_manifest)
    manifest_core.pop("execution_fingerprint")
    manifest_core["numeric_trial_count"] = 1728
    manifest_core["source_manifest_fingerprint"] = (
        PEDROTTI_LOCKED_SOURCE_MANIFEST_FINGERPRINT
    )
    manifest_core["source_lock_fingerprint"] = PEDROTTI_SOURCE_LOCK_FINGERPRINT
    patched_manifest = dict(manifest_core)
    patched_manifest["execution_fingerprint"] = execution_module.fingerprint(
        manifest_core
    )
    execution = replace(execution, execution_manifest=patched_manifest)

    monkeypatch.setattr(
        execution_module,
        "_verify_locked_prepared",
        lambda value, **_: value,
    )
    context = {
        "schema": "gazeaudit-pedrotti-execution-context-v1",
        "execution_commit": "a" * 40,
        "workflow_ref": PEDROTTI_EXECUTION_WORKFLOW,
        "github_run_id": 123,
        "runner_os": "Linux",
        "runner_arch": "X64",
        "python": "3.12.14",
    }
    output = tmp_path / "archive"
    write_pedrotti_locked_execution_artifacts(
        execution,
        output,
        execution_context=context,
        environment_text="numpy==2.5.3\npandas==2.3.3\n",
    )

    assert verify_pedrotti_locked_execution_artifacts(output)
    revealed = reveal_pedrotti_locked_execution(output)
    assert revealed["execution_manifest"]["execution_fingerprint"] == (
        execution.execution_fingerprint
    )
    assert (output / "SHA256SUMS").is_file()

    sampling_path = output / "sampling_results.json"
    sampling = json.loads(sampling_path.read_text(encoding="utf-8"))
    sampling[0]["target_hz"] = 499.0
    sampling_path.write_text(
        execution_module.canonical_json(sampling) + "\n",
        encoding="utf-8",
    )
    assert not verify_pedrotti_locked_execution_artifacts(output)


def test_execution_context_builder_rejects_nonfrozen_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(execution_module.platform, "python_version", lambda: "3.13.0")
    with pytest.raises(ValueError, match="Python 3.12.14"):
        execution_context(
            execution_commit="a" * 40,
            github_run_id=1,
            runner_os="Linux",
            runner_arch="X64",
        )


def test_execution_context_builder_accepts_frozen_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(execution_module.platform, "python_version", lambda: "3.12.14")
    context = execution_context(
        execution_commit="b" * 40,
        github_run_id=2,
        runner_os="Linux",
        runner_arch="X64",
    )
    assert context["python"] == "3.12.14"
    assert context["workflow_ref"] == PEDROTTI_EXECUTION_WORKFLOW


def test_hidden_execution_cli_writes_archive_without_printing_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    environment = tmp_path / "pip-freeze.txt"
    environment.write_text("numpy==2.5.3\npandas==2.3.3\n", encoding="utf-8")
    prepared = object()
    scientific_execution = object()
    context = {"context": "synthetic"}
    calls: dict[str, object] = {}

    monkeypatch.setattr(
        execution_cli,
        "prepare_pedrotti_locked_execution_data",
        lambda source_dir: prepared,
    )
    monkeypatch.setattr(
        execution_cli,
        "run_pedrotti_locked_scientific_execution",
        lambda value: scientific_execution if value is prepared else None,
    )
    monkeypatch.setattr(
        execution_cli,
        "execution_context",
        lambda **kwargs: context,
    )

    def fake_write(value, output_dir, *, execution_context, environment_text):
        calls["value"] = value
        calls["output_dir"] = output_dir
        calls["execution_context"] = execution_context
        calls["environment_text"] = environment_text

    monkeypatch.setattr(
        execution_cli,
        "write_pedrotti_locked_execution_artifacts",
        fake_write,
    )

    result = execution_cli.main(
        [
            "--source-dir",
            "source",
            "--output-dir",
            "archive",
            "--environment-file",
            str(environment),
            "--execution-commit",
            "a" * 40,
            "--run-id",
            "123",
            "--runner-os",
            "Linux",
            "--runner-arch",
            "X64",
        ]
    )
    assert result == 0
    assert calls["value"] is scientific_execution
    assert calls["execution_context"] is context
    assert calls["environment_text"] == "numpy==2.5.3\npandas==2.3.3\n"
    assert capsys.readouterr().out == ""


def test_reveal_cli_prints_only_verified_archive_summary(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        reveal_cli,
        "reveal_pedrotti_locked_execution",
        lambda _: {
            "status": "archived_scientific_result",
            "reference": {"study_estimate": 1.25},
            "sampling_results": [{"target_hz": 500.0}],
            "missingness_results": [{"estimate": 1.2}],
            "family_recovery": [{"family": "sampling"}],
            "execution_manifest": {
                "classification": "robust",
                "execution_fingerprint": "c" * 64,
            },
        },
    )
    assert reveal_cli.main(["--archive-dir", "archive"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["classification"] == "robust"
    assert output["execution_fingerprint"] == "c" * 64
    assert "missingness_results" not in output
