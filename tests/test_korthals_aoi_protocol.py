import json
from pathlib import Path

from gazeaudit.aoi_protocol import verify_aoi_uncertainty_protocol

PROTOCOL_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "protocols"
    / "korthals2026_target_tracking_aoi_v1.json"
)
EXPECTED_FINGERPRINT = "2b8e8da84182316d08ab173ad7d71a2ff09fc45bd84f875ae548832a288ba291"
EXPECTED_COMPANION_COMMIT = "1d7ebec23e3fe20f6db952eefda1a0dd58ae09da"


def _load_protocol():
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def test_frozen_korthals_protocol_is_valid_and_fingerprint_locked():
    protocol = _load_protocol()

    assert verify_aoi_uncertainty_protocol(protocol)
    assert protocol["protocol_fingerprint"] == EXPECTED_FINGERPRINT
    assert protocol["case_study_id"] == "korthals2026-target-tracking-aoi-v1"


def test_protocol_locks_public_dataset_identity_and_author_directed_exclusion():
    dataset = _load_protocol()["dataset"]
    exclusion = dataset["author_directed_exclusion"]

    assert dataset["article_doi"] == "10.1038/s41597-026-06963-4"
    assert dataset["osf_doi"] == "10.17605/OSF.IO/ZX7HC"
    assert dataset["companion_repository"] == "lukekorthals/pursuing-smooth-pursuits-data"
    assert dataset["companion_commit"] == EXPECTED_COMPANION_COMMIT
    assert dataset["trial_types"] == ["moving_circle", "jumping_circle"]
    assert exclusion["participant_id"] == "21db28aa"
    assert exclusion["trial_number_start"] == 82
    assert exclusion["trial_number_end"] == 144


def test_protocol_locks_validation_grouping_without_pooled_fallback():
    protocol = _load_protocol()
    validation = protocol["validation"]
    error_model = protocol["error_model"]

    assert validation["grouping"] == ["participant_id", "validation_nr"]
    assert validation["metric"] == "error_avg"
    assert validation["n_validation_points"] == 9
    assert validation["unmapped_trial_policy"] == "fail_closed"
    assert error_model["group_key"] == ["participant_id", "validation_nr"]
    assert error_model["sigma_formula"] == "error_avg / sqrt(pi/2)"
    assert error_model["unknown_group_policy"] == "fail_closed"


def test_protocol_locks_target_centered_aoi_and_balanced_paired_estimand():
    protocol = _load_protocol()
    aoi = protocol["aoi"]
    endpoint = protocol["endpoint"]

    assert aoi["geometry"] == "circle"
    assert aoi["cx"] == 0.0
    assert aoi["cy"] == 0.0
    assert aoi["radius"] == 1.0
    assert aoi["coordinate_transform"]["observed_x"] == "gaze_x - target_x"
    assert aoi["coordinate_transform"]["observed_y"] == "gaze_y - target_y"
    assert endpoint["cell_contrast"] == "jumping_circle occupancy minus moving_circle occupancy"
    assert endpoint["matched_cell"] == [
        "participant_id",
        "repetition",
        "target_speed",
        "target_trajectory",
    ]
    assert endpoint["participant_estimate"] == "unweighted mean of complete matched-cell contrasts"
    assert endpoint["study_estimate"] == "unweighted mean of participant estimates"


def test_protocol_locks_sampling_monte_carlo_and_interpretation_rule():
    protocol = _load_protocol()
    sampling = protocol["dataset"]["sampling"]
    monte_carlo = protocol["monte_carlo"]
    interpretation = protocol["interpretation"]

    assert sampling["target_hz"] == 50.0
    assert monte_carlo == {
        "batch_size": 8,
        "draws": 2000,
        "interval": 0.95,
        "reference": 0.0,
        "rng_seed": 20260316,
    }
    assert "at least 0.95" in interpretation["robust_positive"]
    assert "at least 0.95" in interpretation["robust_negative"]
    assert interpretation["population_inference"].startswith("none;")
