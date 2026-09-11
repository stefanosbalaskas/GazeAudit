import hashlib
import json
import pathlib

import pytest


PROTOCOL_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "docs"
    / "case_studies"
    / "gazebase_multidetector_protocol.json"
)
EXPECTED_FINGERPRINT = "3f64122f62cbc9762b0bd0e0b95c7fef6ff40c4700215ee4b90f005af77003b1"


def _load_protocol_document():
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def _fingerprint(protocol):
    canonical = json.dumps(
        protocol,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_frozen_protocol_fingerprint_matches_declared_identity():
    document = _load_protocol_document()

    assert document["protocol_fingerprint"] == EXPECTED_FINGERPRINT
    assert _fingerprint(document["protocol"]) == EXPECTED_FINGERPRINT


def test_protocol_freezes_dataset_tasks_and_exact_interop_versions():
    protocol = _load_protocol_document()["protocol"]

    assert protocol["status"] == "frozen-before-detector-output-inspection"
    assert protocol["dataset"]["name"] == "GazeBase"
    assert protocol["dataset"]["version"] == 3
    assert protocol["dataset"]["round"] == 1
    assert protocol["dataset"]["session"] == 1
    assert protocol["dataset"]["tasks"] == ["FXS", "TEX"]
    assert protocol["software"]["pymovements"] == "0.28.0"
    assert protocol["software"]["peyes"] == "0.2.2"


def test_protocol_freezes_all_seven_detector_families_without_post_hoc_removal():
    detector_space = _load_protocol_document()["protocol"]["detector_space"]

    assert detector_space["algorithms"] == [
        "ivt",
        "ivvt",
        "idt",
        "idvt",
        "engbert",
        "nh",
        "remodnav",
    ]
    assert detector_space["shared_parameters"]["min_event_duration_ms"] == 40.0
    assert detector_space["post_hoc_retuning_allowed"] is False
    assert detector_space["post_hoc_detector_removal_allowed"] is False


def test_protocol_freezes_fail_closed_completeness_and_recovery_rules():
    protocol = _load_protocol_document()["protocol"]
    completeness = protocol["completeness_gate"]
    rule = protocol["conclusion_rule"]

    assert completeness["minimum_finite_participant_fraction_per_detector"] == 0.95
    assert "must not receive a robust/fragile classification" in completeness["failure_action"]
    assert rule["relative_tolerance"] == 0.20
    assert rule["absolute_tolerance"] is None
    assert rule["require_sign"] is True
    assert rule["minimum_recovery_fraction"] == pytest.approx(6 / 7)
    assert rule["minimum_recovered_detectors"] == 6
    assert rule["n_predeclared_detectors"] == 7
    assert rule["uses_p_values"] is False


def test_protocol_cohort_cannot_depend_on_alternative_detector_results():
    cohort = _load_protocol_document()["protocol"]["cohort"]

    prohibited = set(cohort["must_not_depend_on"])
    assert "alternative-detector labels" in prohibited
    assert "alternative-detector effect estimates" in prohibited
    assert "p-values" in prohibited
    assert "preferred direction or magnitude" in prohibited
