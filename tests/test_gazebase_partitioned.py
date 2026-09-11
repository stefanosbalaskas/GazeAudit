from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit.gazebase_execution import (
    GAZEBASE_ARCHIVE_MD5,
    GAZEBASE_DETECTORS,
    PreparedGazeBaseData,
    run_gazebase_multidetector_execution,
)
from gazeaudit.gazebase_partitioned import (
    assemble_gazebase_partitioned_execution,
    detector_partition_document,
    prepare_gazebase_execution_context,
    read_gazebase_detector_partition,
    run_gazebase_detector_partition,
    write_gazebase_detector_partition,
)
from gazeaudit.study import GazeStudy

COMMIT = "b" * 40


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
        "selected_file_count": 8,
        "selected_files_fingerprint": "synthetic-source",
    }


def _prepared(reference_equal=False):
    rows = []
    for participant in (1, 2, 3, 4):
        for task in ("FXS", "TEX"):
            labels = np.full(6, "fixation", dtype=object)
            if task == "TEX" and not reference_equal:
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
    return PreparedGazeBaseData(GazeStudy(pd.DataFrame(rows)), _source_identity())


def _factory(algorithm, **_kwargs):
    return _FakeDetector(algorithm)


def _runner(*, bad=(), incomplete=()):
    bad = set(bad)
    incomplete = set(incomplete)

    def runner(study, detector, **_kwargs):
        output = study.data.copy()
        output["event_label"] = output["reference_event_label"].copy()
        if detector.algorithm in bad:
            for participant in output["participant"].unique():
                mask = output["participant"].eq(participant) & output["trial"].eq("TEX")
                indices = output.index[mask]
                output.loc[indices[2:], "event_label"] = "saccade"
        if detector.algorithm in incomplete:
            output = output.loc[~output["participant"].eq(4)].copy()
        return _DetectionResult(output.reset_index(drop=True))

    return runner


def _partitioned(prepared, *, bad=(), incomplete=()):
    context = prepare_gazebase_execution_context(
        prepared,
        gazeaudit_commit=COMMIT,
        version_getter=_versions(),
    )
    runner = _runner(bad=bad, incomplete=incomplete)
    partitions = [
        run_gazebase_detector_partition(
            prepared,
            context,
            algorithm,
            detector_factory=_factory,
            detector_runner=runner,
        )
        for algorithm in GAZEBASE_DETECTORS
    ]
    return context, partitions, assemble_gazebase_partitioned_execution(context, partitions)


def test_partitioned_execution_is_exactly_equivalent_to_monolithic_runner():
    prepared = _prepared()
    monolithic = run_gazebase_multidetector_execution(
        prepared,
        gazeaudit_commit=COMMIT,
        detector_factory=_factory,
        detector_runner=_runner(bad={"ivt"}),
        version_getter=_versions(),
    )
    context, partitions, partitioned = _partitioned(prepared, bad={"ivt"})

    assert context.reference_effect == monolithic.audit.reference_effect
    assert [partition.algorithm for partition in partitions] == list(GAZEBASE_DETECTORS)
    pd.testing.assert_frame_equal(partitioned.audit.effects, monolithic.audit.effects)
    pd.testing.assert_frame_equal(partitioned.audit.coverage, monolithic.audit.coverage)
    pd.testing.assert_frame_equal(partitioned.audit.recovery, monolithic.audit.recovery)
    pd.testing.assert_series_equal(partitioned.audit.summary, monolithic.audit.summary)
    assert partitioned.execution_manifest == monolithic.execution_manifest
    assert partitioned.execution_fingerprint == monolithic.execution_fingerprint
    assert partitioned.publication_bundle is not None
    assert monolithic.publication_bundle is not None
    assert (
        partitioned.publication_bundle.scientific_fingerprint
        == monolithic.publication_bundle.scientific_fingerprint
    )


def test_partition_serialization_round_trip_is_verified(tmp_path: Path):
    prepared = _prepared()
    context = prepare_gazebase_execution_context(
        prepared, gazeaudit_commit=COMMIT, version_getter=_versions()
    )
    partition = run_gazebase_detector_partition(
        prepared,
        context,
        "ivt",
        detector_factory=_factory,
        detector_runner=_runner(),
    )
    target = write_gazebase_detector_partition(partition, tmp_path / "ivt.json")
    loaded = read_gazebase_detector_partition(target)

    assert loaded.algorithm == "ivt"
    assert loaded.partition_fingerprint == partition.partition_fingerprint
    assert detector_partition_document(loaded) == detector_partition_document(partition)
    pd.testing.assert_frame_equal(
        loaded.participant_tasks,
        partition.participant_tasks,
        check_like=True,
    )
    pd.testing.assert_frame_equal(
        loaded.contrasts,
        partition.contrasts,
        check_like=True,
    )


def test_partition_tampering_fails_closed(tmp_path: Path):
    prepared = _prepared()
    context = prepare_gazebase_execution_context(
        prepared, gazeaudit_commit=COMMIT, version_getter=_versions()
    )
    partition = run_gazebase_detector_partition(
        prepared, context, "ivt", detector_factory=_factory, detector_runner=_runner()
    )
    target = write_gazebase_detector_partition(partition, tmp_path / "ivt.json")
    text = target.read_text(encoding="utf-8").replace('"coverage":1.0', '"coverage":0.5')
    target.write_text(text, encoding="utf-8")

    with pytest.raises(ValueError, match="fingerprint verification failed"):
        read_gazebase_detector_partition(target)


def test_partition_set_must_be_exact_and_context_bound():
    prepared = _prepared()
    context, partitions, _ = _partitioned(prepared)

    with pytest.raises(ValueError, match="missing"):
        assemble_gazebase_partitioned_execution(context, partitions[:-1])

    other = _prepared()
    other.source_identity["source_variant"] = "different"
    other_context = prepare_gazebase_execution_context(
        other, gazeaudit_commit=COMMIT, version_getter=_versions()
    )
    with pytest.raises(ValueError, match="different execution context"):
        assemble_gazebase_partitioned_execution(other_context, partitions)


def test_unknown_detector_is_rejected_before_detector_factory():
    prepared = _prepared()
    context = prepare_gazebase_execution_context(
        prepared, gazeaudit_commit=COMMIT, version_getter=_versions()
    )
    calls = []

    def factory(*args, **kwargs):
        calls.append((args, kwargs))
        return _FakeDetector("unknown")

    with pytest.raises(ValueError, match="frozen detectors"):
        run_gazebase_detector_partition(
            prepared,
            context,
            "unknown",
            detector_factory=factory,
            detector_runner=_runner(),
        )
    assert calls == []


def test_partitioned_five_of_seven_is_fragile_and_coverage_failure_is_incomplete():
    _, _, fragile = _partitioned(_prepared(), bad={"ivt", "ivvt"})
    assert fragile.audit.summary["classification"] == "fragile"
    assert fragile.audit.summary["conclusion_recovery_fraction"] == pytest.approx(5 / 7)

    _, _, incomplete = _partitioned(_prepared(), incomplete={"ivt"})
    assert incomplete.audit.summary["classification"] == "incomplete"
    assert incomplete.audit.recovery is None
    assert incomplete.publication_bundle is None


def test_zero_reference_effect_stops_before_any_partition_execution():
    with pytest.raises(ValueError, match="exactly zero"):
        prepare_gazebase_execution_context(
            _prepared(reference_equal=True),
            gazeaudit_commit=COMMIT,
            version_getter=_versions(),
        )
