import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit.gazebase_execution import (
    GAZEBASE_ARCHIVE_MD5,
    GAZEBASE_DETECTORS,
    GAZEBASE_PROTOCOL_FINGERPRINT,
    PreparedGazeBaseData,
    load_gazebase_protocol,
    prepare_gazebase_pymovements_dataset,
    run_gazebase_multidetector_execution,
    verify_gazebase_protocol,
    verify_gazebase_software_versions,
)
from gazeaudit.provenance import fingerprint
from gazeaudit.study import GazeStudy

COMMIT = "a" * 40


class _FakeDetector:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def get_default_params(self):
        return {"frozen_default": f"default-{self.algorithm}"}


class _DetectionResult:
    def __init__(self, samples):
        self.samples = samples


class _FakeRecording:
    def __init__(self, samples):
        self.samples = samples
        self.trial_columns = []


class _FakeDataset:
    def __init__(self, recordings, fileinfo):
        self.gaze = recordings
        self.fileinfo = fileinfo
        self.deg2pix_calls = 0

    def deg2pix(self, **kwargs):
        self.deg2pix_calls += 1
        for recording in self.gaze:
            if "pixel" not in recording.samples:
                recording.samples["pixel"] = recording.samples["position"].copy()
        return self


def _versions(peyes="0.2.2", pymovements="0.28.0", gazeaudit="0.1.0.dev9"):
    values = {
        "pEYES": peyes,
        "pymovements": pymovements,
        "gazeaudit": gazeaudit,
    }
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
            n = 6
            labels = np.full(n, "fixation", dtype=object)
            if task == "TEX" and not reference_equal:
                labels[4:] = "saccade"
            for index in range(n):
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


def _factory_calls():
    calls = []

    def factory(algorithm, **kwargs):
        calls.append((algorithm, kwargs.copy()))
        return _FakeDetector(algorithm)

    return calls, factory


def _runner(*, bad=(), incomplete=()):
    bad = set(bad)
    incomplete = set(incomplete)

    def runner(study, detector, **kwargs):
        output = study.data.copy()
        output["event_label"] = output["reference_event_label"].copy()
        if detector.algorithm in bad:
            mask = output["trial"].eq("TEX")
            tex_indices = output.index[mask]
            for participant in output.loc[mask, "participant"].unique():
                participant_indices = tex_indices[
                    output.loc[tex_indices, "participant"].to_numpy() == participant
                ]
                output.loc[participant_indices[2:], "event_label"] = "saccade"
        if detector.algorithm in incomplete:
            output = output.loc[~output["participant"].eq(4)].copy()
        return _DetectionResult(output.reset_index(drop=True))

    return runner


def test_packaged_protocol_matches_repository_frozen_protocol():
    packaged = load_gazebase_protocol()
    protocol_path = (
        Path(__file__).parents[1]
        / "docs"
        / "case_studies"
        / "gazebase_multidetector_protocol.json"
    )
    repository = json.loads(protocol_path.read_text(encoding="utf-8"))

    assert packaged == repository
    assert packaged["protocol_fingerprint"] == GAZEBASE_PROTOCOL_FINGERPRINT
    assert fingerprint(packaged["protocol"]) == GAZEBASE_PROTOCOL_FINGERPRINT
    assert verify_gazebase_protocol(packaged)["case_study_id"].endswith("multidetector-v1")


def test_protocol_drift_fails_closed():
    drifted = copy.deepcopy(load_gazebase_protocol())
    drifted["protocol"]["conclusion_rule"]["relative_tolerance"] = 0.25

    with pytest.raises(ValueError, match="frozen fingerprint"):
        verify_gazebase_protocol(drifted)


def test_exact_frozen_software_versions_are_required():
    assert verify_gazebase_software_versions(_versions()) == {
        "pymovements": "0.28.0",
        "peyes": "0.2.2",
        "gazeaudit": "0.1.0.dev9",
    }

    with pytest.raises(RuntimeError, match="pEYES==0.2.2"):
        verify_gazebase_software_versions(_versions(peyes="0.2.3"))
    with pytest.raises(RuntimeError, match="pymovements==0.28.0"):
        verify_gazebase_software_versions(_versions(pymovements="0.29.0"))
    with pytest.raises(RuntimeError, match="GazeAudit>=0.1.0.dev7"):
        verify_gazebase_software_versions(_versions(gazeaudit="0.1.0.dev6"))


def test_invalid_commit_stops_before_detector_factory():
    calls, factory = _factory_calls()

    with pytest.raises(ValueError, match="40-character"):
        run_gazebase_multidetector_execution(
            _prepared(),
            gazeaudit_commit="not-a-sha",
            detector_factory=factory,
            detector_runner=_runner(),
            version_getter=_versions(),
        )

    assert calls == []


def test_software_version_drift_stops_before_detector_factory():
    calls, factory = _factory_calls()

    with pytest.raises(RuntimeError, match="pEYES==0.2.2"):
        run_gazebase_multidetector_execution(
            _prepared(),
            gazeaudit_commit=COMMIT,
            detector_factory=factory,
            detector_runner=_runner(),
            version_getter=_versions(peyes="0.2.3"),
        )

    assert calls == []


def test_zero_reference_effect_stops_before_detector_factory():
    calls, factory = _factory_calls()

    with pytest.raises(ValueError, match="exactly zero"):
        run_gazebase_multidetector_execution(
            _prepared(reference_equal=True),
            gazeaudit_commit=COMMIT,
            detector_factory=factory,
            detector_runner=_runner(),
            version_getter=_versions(),
        )

    assert calls == []


def test_runner_executes_frozen_detector_set_and_builds_verified_bundle():
    calls, factory = _factory_calls()
    execution = run_gazebase_multidetector_execution(
        _prepared(),
        gazeaudit_commit=COMMIT,
        detector_factory=factory,
        detector_runner=_runner(bad={"ivt"}),
        version_getter=_versions(),
    )

    assert [name for name, _ in calls] == list(GAZEBASE_DETECTORS)
    for algorithm, kwargs in calls:
        assert kwargs["missing_value"] is np.nan
        assert kwargs["min_event_duration"] == 40.0
        assert kwargs["pad_blinks_time"] == 0.0
        assert kwargs["name"] == algorithm
    assert execution.audit.summary["classification"] == "robust"
    assert execution.audit.summary["conclusion_recovery_fraction"] == pytest.approx(6 / 7)
    assert execution.publication_bundle is not None
    assert execution.execution_manifest["completeness_passed"] is True
    assert execution.execution_manifest["protocol_fingerprint"] == GAZEBASE_PROTOCOL_FINGERPRINT
    assert execution.detector_parameters["ivt"]["algorithm_specific"] == {
        "frozen_default": "default-ivt"
    }
    assert len(execution.execution_fingerprint) == 64


def test_five_of_seven_recovery_is_fragile_but_complete():
    _, factory = _factory_calls()
    execution = run_gazebase_multidetector_execution(
        _prepared(),
        gazeaudit_commit=COMMIT,
        detector_factory=factory,
        detector_runner=_runner(bad={"ivt", "ivvt"}),
        version_getter=_versions(),
    )

    assert execution.audit.summary["classification"] == "fragile"
    assert execution.audit.summary["conclusion_recovery_fraction"] == pytest.approx(5 / 7)
    assert execution.publication_bundle is not None


def test_coverage_failure_is_incomplete_and_has_no_publication_bundle():
    _, factory = _factory_calls()
    execution = run_gazebase_multidetector_execution(
        _prepared(),
        gazeaudit_commit=COMMIT,
        detector_factory=factory,
        detector_runner=_runner(incomplete={"ivt"}),
        version_getter=_versions(),
    )

    assert execution.audit.summary["classification"] == "incomplete"
    assert execution.audit.recovery is None
    assert execution.publication_bundle is None
    assert execution.execution_manifest["publication_bundle_fingerprint"] is None
    ivt = execution.audit.coverage.loc[execution.audit.coverage["detector"].eq("ivt")].iloc[0]
    assert ivt["coverage_fraction"] == 0.75


def test_identical_execution_is_deterministic_and_source_identity_is_bound():
    _, factory_one = _factory_calls()
    first = run_gazebase_multidetector_execution(
        _prepared(),
        gazeaudit_commit=COMMIT,
        detector_factory=factory_one,
        detector_runner=_runner(bad={"ivt"}),
        version_getter=_versions(),
    )
    _, factory_two = _factory_calls()
    second = run_gazebase_multidetector_execution(
        _prepared(),
        gazeaudit_commit=COMMIT,
        detector_factory=factory_two,
        detector_runner=_runner(bad={"ivt"}),
        version_getter=_versions(),
    )

    assert first.execution_fingerprint == second.execution_fingerprint
    assert first.publication_bundle is not None
    assert second.publication_bundle is not None
    assert (
        first.publication_bundle.scientific_fingerprint
        == second.publication_bundle.scientific_fingerprint
    )

    changed = _prepared()
    changed.source_identity["source_variant"] = "different-source-identity"
    _, factory_three = _factory_calls()
    third = run_gazebase_multidetector_execution(
        changed,
        gazeaudit_commit=COMMIT,
        detector_factory=factory_three,
        detector_runner=_runner(bad={"ivt"}),
        version_getter=_versions(),
    )
    assert third.execution_fingerprint != first.execution_fingerprint
    assert third.publication_bundle is not None
    assert (
        third.publication_bundle.scientific_fingerprint
        != first.publication_bundle.scientific_fingerprint
    )


def test_prepare_pymovements_subset_maps_reference_labels_without_path_identity():
    recordings = []
    info_rows = []
    for participant in (2, 1):
        for task in ("TEX", "FXS"):
            n = 6
            labels = [1, 1, 1, 1, 2, -1] if task == "TEX" else [1] * n
            positions = [np.array([float(i), float(participant)]) for i in range(n)]
            recordings.append(
                _FakeRecording(
                    pd.DataFrame(
                        {
                            "time": np.arange(n, dtype=float) * 10,
                            "position": positions,
                            "pixel": positions,
                            "lab": labels,
                        }
                    )
                )
            )
            info_rows.append(
                {
                    "round_id": 1,
                    "subject_id": participant,
                    "session_id": 1,
                    "task_name": task,
                    "filepath": f"/private/location/S_1{participant}_S1_{task}.csv",
                }
            )
    dataset = _FakeDataset(recordings, pd.DataFrame(info_rows))

    prepared = prepare_gazebase_pymovements_dataset(dataset)

    assert dataset.deg2pix_calls == 0
    assert set(prepared.study.data["trial"]) == {"FXS", "TEX"}
    assert set(prepared.study.data["reference_event_label"]) == {
        "fixation",
        "saccade",
        "blink",
    }
    assert prepared.source_identity["selected_file_count"] == 4
    assert prepared.source_identity["catalog_archive_md5"] == GAZEBASE_ARCHIVE_MD5
    assert "/private/location" not in json.dumps(prepared.source_identity)


def test_prepare_rejects_nonfrozen_subset():
    samples = pd.DataFrame(
        {
            "time": [0.0, 10.0],
            "position": [np.array([0.0, 0.0]), np.array([1.0, 1.0])],
            "pixel": [np.array([0.0, 0.0]), np.array([1.0, 1.0])],
            "lab": [1, 1],
        }
    )
    dataset = _FakeDataset(
        [_FakeRecording(samples), _FakeRecording(samples.copy())],
        pd.DataFrame(
            [
                {
                    "round_id": 1,
                    "subject_id": 1,
                    "session_id": 1,
                    "task_name": "FXS",
                },
                {
                    "round_id": 1,
                    "subject_id": 1,
                    "session_id": 1,
                    "task_name": "RAN",
                },
            ]
        ),
    )

    with pytest.raises(ValueError, match="only Round 1"):
        prepare_gazebase_pymovements_dataset(dataset)
