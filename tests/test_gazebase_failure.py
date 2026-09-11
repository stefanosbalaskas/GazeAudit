import numpy as np
import pandas as pd
import pytest

from gazeaudit.gazebase_execution import (
    GAZEBASE_ARCHIVE_MD5,
    GAZEBASE_DETECTORS,
    PreparedGazeBaseData,
)
from gazeaudit.gazebase_failure import run_gazebase_detector_partition_fail_closed
from gazeaudit.gazebase_partitioned import (
    assemble_gazebase_partitioned_execution,
    detector_partition_document,
    prepare_gazebase_execution_context,
    read_gazebase_detector_partition,
    run_gazebase_detector_partition,
    write_gazebase_detector_partition,
)
from gazeaudit.study import GazeStudy

COMMIT = "c" * 40


class _FakeDetector:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def get_default_params(self):
        return {"frozen_default": f"default-{self.algorithm}"}


class _DetectionResult:
    def __init__(self, samples):
        self.samples = samples


def _versions():
    values = {"pEYES": "0.2.2", "pymovements": "0.28.0", "gazeaudit": "0.1.0.dev11"}
    return lambda name: values[name]


def _source_identity():
    return {
        "dataset": "GazeBase",
        "dataset_version": 3,
        "paper_doi": "10.1038/s41597-021-00959-y",
        "data_doi": "10.6084/m9.figshare.12912257",
        "catalog_archive_md5": GAZEBASE_ARCHIVE_MD5,
        "round": 1,
        "session": 1,
        "tasks": ["FXS", "TEX"],
        "selected_file_count": 4,
        "selected_files_fingerprint": "synthetic-source",
    }


def _prepared():
    rows = []
    for participant in (1, 2):
        for task in ("FXS", "TEX"):
            labels = np.full(6, "fixation", dtype=object)
            if task == "TEX":
                labels[3:] = "saccade"
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
    return PreparedGazeBaseData(GazeStudy(pd.DataFrame(rows)), _source_identity())


def _factory(algorithm, **_kwargs):
    return _FakeDetector(algorithm)


def _success_runner(study, detector, **_kwargs):
    output = study.data.copy()
    output["event_label"] = output["reference_event_label"]
    return _DetectionResult(output.reset_index(drop=True))


def _value_error_runner(*_args, **_kwargs):
    raise ValueError("array must not contain infs or NaNs")


def _runtime_error_runner(*_args, **_kwargs):
    raise RuntimeError("backend failed")


def _context(prepared):
    return prepare_gazebase_execution_context(
        prepared,
        gazeaudit_commit=COMMIT,
        version_getter=_versions(),
    )


def test_success_path_is_exactly_the_existing_partition_runner():
    prepared = _prepared()
    context = _context(prepared)
    direct = run_gazebase_detector_partition(
        prepared,
        context,
        "ivt",
        detector_factory=_factory,
        detector_runner=_success_runner,
    )
    guarded = run_gazebase_detector_partition_fail_closed(
        prepared,
        context,
        "ivt",
        detector_factory=_factory,
        detector_runner=_success_runner,
    )

    assert detector_partition_document(guarded) == detector_partition_document(direct)
    assert guarded.partition_fingerprint == direct.partition_fingerprint


def test_detector_value_error_becomes_zero_coverage_verified_partition(tmp_path):
    prepared = _prepared()
    context = _context(prepared)
    partition = run_gazebase_detector_partition_fail_closed(
        prepared,
        context,
        "remodnav",
        detector_factory=_factory,
        detector_runner=_value_error_runner,
    )

    assert partition.coverage == 0.0
    assert np.isnan(partition.effect)
    assert not partition.contrasts["paired_complete"].any()
    assert partition.detector_parameters["execution_failure"] == {
        "policy": "mark_incomplete",
        "stage": "detector_runner",
        "exception_type": "ValueError",
        "message": "array must not contain infs or NaNs",
    }

    path = write_gazebase_detector_partition(partition, tmp_path / "remodnav.json")
    loaded = read_gazebase_detector_partition(path)
    assert detector_partition_document(loaded) == detector_partition_document(partition)
    assert loaded.coverage == 0.0
    assert np.isnan(loaded.effect)


def test_failed_predeclared_detector_forces_incomplete_without_recovery_or_bundle():
    prepared = _prepared()
    context = _context(prepared)
    partitions = []
    for algorithm in GAZEBASE_DETECTORS:
        runner = _value_error_runner if algorithm == "remodnav" else _success_runner
        partitions.append(
            run_gazebase_detector_partition_fail_closed(
                prepared,
                context,
                algorithm,
                detector_factory=_factory,
                detector_runner=runner,
            )
        )

    execution = assemble_gazebase_partitioned_execution(context, partitions)
    assert execution.audit.summary["classification"] == "incomplete"
    assert execution.audit.summary["completeness_passed"] is False
    assert execution.audit.summary["minimum_observed_coverage"] == 0.0
    assert execution.audit.recovery is None
    assert execution.publication_bundle is None
    remodnav = execution.audit.coverage.loc[
        execution.audit.coverage["detector"].eq("remodnav")
    ].iloc[0]
    assert remodnav["coverage_fraction"] == 0.0
    assert bool(remodnav["coverage_passed"]) is False


def test_runtime_error_is_not_hidden_unless_explicitly_declared():
    prepared = _prepared()
    context = _context(prepared)

    with pytest.raises(RuntimeError, match="backend failed"):
        run_gazebase_detector_partition_fail_closed(
            prepared,
            context,
            "nh",
            detector_factory=_factory,
            detector_runner=_runtime_error_runner,
        )

    partition = run_gazebase_detector_partition_fail_closed(
        prepared,
        context,
        "nh",
        detector_factory=_factory,
        detector_runner=_runtime_error_runner,
        catch=(ValueError, RuntimeError),
    )
    assert partition.coverage == 0.0
    assert partition.detector_parameters["execution_failure"]["exception_type"] == "RuntimeError"


def test_frozen_detector_identity_validation_is_never_converted_to_failure():
    prepared = _prepared()
    context = _context(prepared)

    with pytest.raises(ValueError, match="frozen detectors"):
        run_gazebase_detector_partition_fail_closed(
            prepared,
            context,
            "unknown",
            detector_factory=_factory,
            detector_runner=_value_error_runner,
        )
