from __future__ import annotations

import json
import runpy
import sys
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from gazeaudit.gazebase_execution import (
    GAZEBASE_ARCHIVE_MD5,
    GAZEBASE_DETECTORS,
    PreparedGazeBaseData,
)
import gazeaudit.gazebase_failure as gazebase_failure
import gazeaudit.gazebase_partitioned as partitioned
import gazeaudit.korthals_execution_archive_v2 as archive_v2
import gazeaudit.pedrotti_execution as pedrotti_execution
import gazeaudit.pedrotti_freeze_cli as pedrotti_freeze_cli
import gazeaudit.sensitivity as sensitivity
from gazeaudit.study import GazeStudy


COMMIT = "c" * 40


class _FakeDetector:
    def __init__(self, algorithm: str) -> None:
        self.algorithm = algorithm

    def get_default_params(self) -> dict[str, str]:
        return {
            "frozen_default": f"default-{self.algorithm}",
        }


class _NoDefaultsDetector:
    pass


class _BadDefaultsDetector:
    def get_default_params(self) -> list[str]:
        return []


class _DetectionResult:
    def __init__(self, samples: object) -> None:
        self.samples = samples


def _versions():
    values = {
        "pEYES": "0.2.2",
        "pymovements": "0.28.0",
        "gazeaudit": "0.1.0.dev11",
    }
    return lambda name: values[name]


def _source_identity() -> dict[str, object]:
    return {
        "dataset": "GazeBase",
        "dataset_version": 3,
        "paper_doi": "10.1038/s41597-021-00959-y",
        "data_doi": "10.6084/m9.figshare.12912257",
        "catalog_archive_md5": GAZEBASE_ARCHIVE_MD5,
        "round": 1,
        "session": 1,
        "tasks": ["FXS", "TEX"],
        "selected_file_count": 8,
        "selected_files_fingerprint": "synthetic-source",
    }


def _prepared() -> PreparedGazeBaseData:
    rows: list[dict[str, object]] = []

    for participant in (1, 2, 3, 4):
        for task in ("FXS", "TEX"):
            labels = np.full(
                6,
                "fixation",
                dtype=object,
            )

            if task == "TEX":
                labels[4:] = "saccade"

            for index in range(6):
                rows.append(
                    {
                        "x": float(index),
                        "y": float(participant),
                        "timestamp": float(index * 10),
                        "participant": participant,
                        "trial": task,
                        "reference_event_label": labels[index],
                    }
                )

    return PreparedGazeBaseData(
        GazeStudy(pd.DataFrame(rows)),
        _source_identity(),
    )


def _factory(
    algorithm: str,
    **_kwargs: object,
) -> _FakeDetector:
    return _FakeDetector(algorithm)


def _runner(
    study: GazeStudy,
    detector: _FakeDetector,
    **_kwargs: object,
) -> _DetectionResult:
    del detector
    output = study.data.copy()
    output["event_label"] = output[
        "reference_event_label"
    ].copy()
    return _DetectionResult(
        output.reset_index(drop=True)
    )


def _context(
    prepared: PreparedGazeBaseData,
) -> partitioned.GazeBaseExecutionContext:
    return partitioned.prepare_gazebase_execution_context(
        prepared,
        gazeaudit_commit=COMMIT,
        version_getter=_versions(),
    )


def _all_partitions(
    prepared: PreparedGazeBaseData,
    context: partitioned.GazeBaseExecutionContext,
) -> list[partitioned.GazeBaseDetectorPartition]:
    return [
        partitioned.run_gazebase_detector_partition(
            prepared,
            context,
            algorithm,
            detector_factory=_factory,
            detector_runner=_runner,
        )
        for algorithm in GAZEBASE_DETECTORS
    ]


def _partition_with_nan_effect(
    value: partitioned.GazeBaseDetectorPartition,
) -> partitioned.GazeBaseDetectorPartition:
    core = {
        "schema": partitioned.PARTITION_SCHEMA,
        "algorithm": value.algorithm,
        "context_fingerprint": value.context_fingerprint,
        "detector_parameters": value.detector_parameters,
        "participant_tasks": partitioned._frame_records(
            value.participant_tasks
        ),
        "contrasts": partitioned._frame_records(
            value.contrasts
        ),
        "effect": None,
        "coverage": float(value.coverage),
    }

    return replace(
        value,
        effect=float("nan"),
        partition_fingerprint=partitioned.fingerprint(core),
    )


# ---------------------------------------------------------------------------
# GazeBase fail-closed execution
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "catch",
    [
        (),
        (ValueError, "not-an-exception"),
    ],
)
def test_fail_closed_rejects_invalid_exception_contract(
    catch: tuple[object, ...],
) -> None:
    prepared = _prepared()
    context = _context(prepared)

    with pytest.raises(
        TypeError,
        match="non-empty tuple of exception classes",
    ):
        gazebase_failure.run_gazebase_detector_partition_fail_closed(
            prepared,
            context,
            "ivt",
            detector_factory=_factory,
            detector_runner=_runner,
            catch=catch,  # type: ignore[arg-type]
        )


def test_failed_partition_requires_detector_defaults_method() -> None:
    prepared = _prepared()
    context = _context(prepared)

    with pytest.raises(
        TypeError,
        match="get_default_params",
    ):
        gazebase_failure._failed_partition(
            prepared,
            context,
            "ivt",
            detector_factory=lambda *args, **kwargs: _NoDefaultsDetector(),
            error=ValueError("failure"),
        )


def test_failed_partition_requires_mapping_defaults() -> None:
    prepared = _prepared()
    context = _context(prepared)

    with pytest.raises(
        TypeError,
        match="defaults must be a mapping",
    ):
        gazebase_failure._failed_partition(
            prepared,
            context,
            "ivt",
            detector_factory=lambda *args, **kwargs: _BadDefaultsDetector(),
            error=ValueError("failure"),
        )


def test_failed_partition_invariant_rejects_nonzero_coverage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _prepared()
    context = _context(prepared)

    monkeypatch.setattr(
        gazebase_failure,
        "detector_task_contrast",
        lambda *args, **kwargs: (
            pd.DataFrame(),
            pd.DataFrame(),
            float("nan"),
            0.5,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="zero coverage",
    ):
        gazebase_failure._failed_partition(
            prepared,
            context,
            "ivt",
            detector_factory=_factory,
            error=ValueError("failure"),
        )


# ---------------------------------------------------------------------------
# GazeBase partitioned execution
# ---------------------------------------------------------------------------


def test_prepare_partition_context_requires_prepared_contract() -> None:
    with pytest.raises(
        TypeError,
        match="PreparedGazeBaseData",
    ):
        partitioned.prepare_gazebase_execution_context(
            object(),  # type: ignore[arg-type]
            gazeaudit_commit=COMMIT,
            version_getter=_versions(),
        )


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (
            lambda *args, **kwargs: _NoDefaultsDetector(),
            "get_default_params",
        ),
        (
            lambda *args, **kwargs: _BadDefaultsDetector(),
            "defaults must be a mapping",
        ),
    ],
)
def test_partition_runner_requires_detector_default_contract(
    factory,
    message: str,
) -> None:
    prepared = _prepared()
    context = _context(prepared)

    with pytest.raises(
        TypeError,
        match=message,
    ):
        partitioned.run_gazebase_detector_partition(
            prepared,
            context,
            "ivt",
            detector_factory=factory,
            detector_runner=_runner,
        )


def test_partition_runner_requires_dataframe_samples() -> None:
    prepared = _prepared()
    context = _context(prepared)

    with pytest.raises(
        TypeError,
        match="pandas DataFrame samples",
    ):
        partitioned.run_gazebase_detector_partition(
            prepared,
            context,
            "ivt",
            detector_factory=_factory,
            detector_runner=lambda *args, **kwargs: _DetectionResult(
                object()
            ),
        )


def test_partition_runner_requires_normalized_detector_columns() -> None:
    prepared = _prepared()
    context = _context(prepared)

    samples = prepared.study.data[
        [
            "participant",
            "trial",
            "timestamp",
        ]
    ].copy()

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        partitioned.run_gazebase_detector_partition(
            prepared,
            context,
            "ivt",
            detector_factory=_factory,
            detector_runner=lambda *args, **kwargs: _DetectionResult(
                samples
            ),
        )


def test_partition_document_detects_in_memory_tampering() -> None:
    prepared = _prepared()
    context = _context(prepared)
    value = _all_partitions(
        prepared,
        context,
    )[0]

    tampered = replace(
        value,
        coverage=0.5,
    )

    with pytest.raises(
        ValueError,
        match="partition_fingerprint",
    ):
        partitioned.detector_partition_document(tampered)


def test_partition_reader_rejects_wrong_schema(tmp_path) -> None:
    target = tmp_path / "wrong.json"
    target.write_text(
        json.dumps(
            {
                "schema": "wrong-schema",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="unexpected detector partition schema",
    ):
        partitioned.read_gazebase_detector_partition(target)


def test_complete_partition_set_rejects_nonfinite_effect() -> None:
    prepared = _prepared()
    context = _context(prepared)
    values = _all_partitions(
        prepared,
        context,
    )
    values[0] = _partition_with_nan_effect(
        values[0]
    )

    with pytest.raises(
        RuntimeError,
        match="effect is non-finite",
    ):
        partitioned.assemble_gazebase_partitioned_execution(
            context,
            values,
        )


def test_partition_assembly_fails_closed_when_publication_verifier_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _prepared()
    context = _context(prepared)
    values = _all_partitions(
        prepared,
        context,
    )

    monkeypatch.setattr(
        partitioned,
        "verify_publication_audit_bundle",
        lambda _bundle: False,
    )

    with pytest.raises(
        RuntimeError,
        match="publication bundle failed verification",
    ):
        partitioned.assemble_gazebase_partitioned_execution(
            context,
            values,
        )


def test_context_verifier_rejects_nonprepared_object() -> None:
    prepared = _prepared()
    context = _context(prepared)

    with pytest.raises(
        TypeError,
        match="PreparedGazeBaseData",
    ):
        partitioned._verify_context_against_prepared(
            object(),  # type: ignore[arg-type]
            context,
        )


def test_context_verifier_rejects_changed_source_identity() -> None:
    prepared = _prepared()
    context = _context(prepared)
    prepared.source_identity[
        "selected_files_fingerprint"
    ] = "changed-source"

    with pytest.raises(
        ValueError,
        match="source identity differs",
    ):
        partitioned._verify_context_against_prepared(
            prepared,
            context,
        )


def test_partition_normalizer_rejects_wrong_object_type() -> None:
    with pytest.raises(
        TypeError,
        match="GazeBaseDetectorPartition",
    ):
        partitioned._normalize_partitions(
            [object()]  # type: ignore[list-item]
        )


def test_partition_normalizer_rejects_duplicate_detector() -> None:
    prepared = _prepared()
    context = _context(prepared)
    value = _all_partitions(
        prepared,
        context,
    )[0]

    with pytest.raises(
        ValueError,
        match="duplicate detector partition",
    ):
        partitioned._normalize_partitions(
            [value, value]
        )


# ---------------------------------------------------------------------------
# Korthals locked protocol-v2 archive wrapper
# ---------------------------------------------------------------------------


def _archive_lock() -> dict[str, object]:
    return {
        "source": {
            "source_manifest_fingerprint": "source-fingerprint",
            "file_count": 10,
            "participant_count": 10,
        },
        "intake": {
            "participant_split_fingerprint": "split-fingerprint",
            "retained_trial_count": 20,
            "missingness_policy": "preserve",
            "zero_finite_scheduled_trial_count": 0,
            "zero_finite_scheduled_trials": [],
            "sampling_incomplete_matched_cell_count": 0,
            "sampling_incomplete_matched_cells": [],
            "prepared_row_count": 30,
            "validation_group_count": 4,
        },
    }


def _write_archive_contract(root) -> None:
    source_identity = {
        "source_manifest_fingerprint": "source-fingerprint",
        "source_file_count": 10,
        "participant_count": 10,
        "participant_split_fingerprint": "split-fingerprint",
        "retained_trial_count": 20,
        "missingness_policy": "preserve",
        "zero_finite_scheduled_trial_count": 0,
        "zero_finite_scheduled_trials": [],
        "sampling_incomplete_matched_cell_count": 0,
        "sampling_incomplete_matched_cells": [],
    }
    execution = {
        "n_rows": 30,
        "n_validation_groups": 4,
        "classification": "robust_negative",
        "summary": {
            "n_observations": 30,
            "n_draws": 2000,
        },
    }

    (root / "source_identity.json").write_text(
        json.dumps(source_identity),
        encoding="utf-8",
    )
    (root / "execution_manifest.json").write_text(
        json.dumps(execution),
        encoding="utf-8",
    )


def test_locked_archive_writer_verifies_intake_and_archive(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    execution = SimpleNamespace(
        prepared=object()
    )
    calls: list[str] = []

    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_locked_prepared",
        lambda prepared: calls.append("prepared"),
    )
    monkeypatch.setattr(
        archive_v2,
        "write_korthals_execution_artifacts_v2",
        lambda *args, **kwargs: {
            "manifest": "ok",
        },
    )
    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_locked_execution_artifacts_v2",
        lambda _root: True,
    )

    result = archive_v2.write_korthals_locked_execution_artifacts_v2(
        execution,  # type: ignore[arg-type]
        tmp_path,
        execution_context={
            "run": 1,
        },
        environment_text="env",
    )

    assert result == {
        "manifest": "ok",
    }
    assert calls == ["prepared"]


def test_locked_archive_writer_fails_if_new_archive_does_not_verify(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    execution = SimpleNamespace(
        prepared=object()
    )

    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_locked_prepared",
        lambda prepared: None,
    )
    monkeypatch.setattr(
        archive_v2,
        "write_korthals_execution_artifacts_v2",
        lambda *args, **kwargs: {},
    )
    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_locked_execution_artifacts_v2",
        lambda _root: False,
    )

    with pytest.raises(
        RuntimeError,
        match="archive failed verification",
    ):
        archive_v2.write_korthals_locked_execution_artifacts_v2(
            execution,  # type: ignore[arg-type]
            tmp_path,
            execution_context={},
            environment_text="env",
        )


def test_locked_archive_verifier_short_circuits_on_base_failure(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_execution_artifacts_v2",
        lambda _root: False,
    )

    assert (
        archive_v2.verify_korthals_locked_execution_artifacts_v2(
            tmp_path
        )
        is False
    )


def test_locked_archive_verifier_accepts_exact_source_contract(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_archive_contract(tmp_path)

    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_execution_artifacts_v2",
        lambda _root: True,
    )
    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_source_lock",
        _archive_lock,
    )

    assert archive_v2.verify_korthals_locked_execution_artifacts_v2(
        tmp_path
    )


def test_locked_archive_verifier_returns_false_for_guardrail_mismatch(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_archive_contract(tmp_path)
    execution_path = tmp_path / "execution_manifest.json"
    execution = json.loads(
        execution_path.read_text(
            encoding="utf-8"
        )
    )
    execution["summary"]["n_draws"] = 1999
    execution_path.write_text(
        json.dumps(execution),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_execution_artifacts_v2",
        lambda _root: True,
    )
    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_source_lock",
        _archive_lock,
    )

    assert (
        archive_v2.verify_korthals_locked_execution_artifacts_v2(
            tmp_path
        )
        is False
    )


def test_locked_archive_verifier_fails_closed_on_malformed_json(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "source_identity.json").write_text(
        "{",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_execution_artifacts_v2",
        lambda _root: True,
    )
    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_source_lock",
        _archive_lock,
    )

    assert (
        archive_v2.verify_korthals_locked_execution_artifacts_v2(
            tmp_path
        )
        is False
    )


def test_locked_archive_reveal_requires_verified_archive(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_locked_execution_artifacts_v2",
        lambda _root: False,
    )

    with pytest.raises(
        ValueError,
        match="archive failed verification",
    ):
        archive_v2.reveal_korthals_locked_execution_v2(
            tmp_path
        )


def test_locked_archive_reveal_delegates_after_verification(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = {
        "classification": "robust_negative",
    }

    monkeypatch.setattr(
        archive_v2,
        "verify_korthals_locked_execution_artifacts_v2",
        lambda _root: True,
    )
    monkeypatch.setattr(
        archive_v2,
        "reveal_korthals_execution_v2",
        lambda _root: expected,
    )

    assert archive_v2.reveal_korthals_locked_execution_v2(
        tmp_path
    ) == expected


# ---------------------------------------------------------------------------
# Remaining sensitivity helper branch
# ---------------------------------------------------------------------------


def test_sensitivity_rng_helper_preserves_generator() -> None:
    generator = np.random.default_rng(42)
    assert sensitivity._as_rng(generator) is generator


# ---------------------------------------------------------------------------
# Tiny Pedrotti CLI gaps
# ---------------------------------------------------------------------------


def test_pedrotti_freeze_cli_rejects_nonobject_source_manifest(
    tmp_path,
) -> None:
    intake = tmp_path / "intake"
    intake.mkdir()
    (intake / "source_manifest.json").write_text(
        "[]",
        encoding="utf-8",
    )
    environment = tmp_path / "environment.txt"
    environment.write_text(
        "environment",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="JSON object",
    ):
        pedrotti_freeze_cli.main(
            [
                "--intake-dir",
                str(intake),
                "--output-dir",
                str(tmp_path / "out"),
                "--environment-file",
                str(environment),
                "--execution-commit",
                "d" * 40,
                "--run-id",
                "1",
            ]
        )


def test_pedrotti_execution_cli_module_guard(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    environment = tmp_path / "environment.txt"
    environment.write_text(
        "environment",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        pedrotti_execution,
        "prepare_pedrotti_locked_execution_data",
        lambda _source: "prepared",
    )
    monkeypatch.setattr(
        pedrotti_execution,
        "run_pedrotti_locked_scientific_execution",
        lambda _prepared: "execution",
    )
    monkeypatch.setattr(
        pedrotti_execution,
        "execution_context",
        lambda **kwargs: kwargs,
    )
    monkeypatch.setattr(
        pedrotti_execution,
        "write_pedrotti_locked_execution_artifacts",
        lambda *args, **kwargs: {},
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gazeaudit.pedrotti_execution_cli",
            "--source-dir",
            str(tmp_path / "source"),
            "--output-dir",
            str(tmp_path / "out"),
            "--environment-file",
            str(environment),
            "--execution-commit",
            "e" * 40,
            "--run-id",
            "123",
            "--runner-os",
            "Linux",
            "--runner-arch",
            "X64",
        ],
    )

    with pytest.raises(
        SystemExit,
    ) as exc:
        runpy.run_module(
            "gazeaudit.pedrotti_execution_cli",
            run_name="__main__",
        )

    assert exc.value.code == 0


def test_pedrotti_reveal_cli_module_guard(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        pedrotti_execution,
        "reveal_pedrotti_locked_execution",
        lambda _root: {
            "status": "verified",
            "execution_manifest": {
                "classification": "robust",
                "execution_fingerprint": "fingerprint",
            },
            "reference": {
                "effect": 1.0,
            },
            "sampling_results": [],
            "family_recovery": [],
        },
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gazeaudit.pedrotti_reveal_cli",
            "--archive-dir",
            str(tmp_path),
        ],
    )

    with pytest.raises(
        SystemExit,
    ) as exc:
        runpy.run_module(
            "gazeaudit.pedrotti_reveal_cli",
            run_name="__main__",
        )

    assert exc.value.code == 0
    assert '"status":"verified"' in capsys.readouterr().out
