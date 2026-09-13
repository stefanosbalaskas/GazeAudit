import json
from pathlib import Path

import pytest

from gazeaudit.provenance import fingerprint
from gazeaudit.sensitivity_protocol import (
    SENSITIVITY_PROTOCOL_SCHEMA,
    build_sampling_missingness_protocol,
    verify_sampling_missingness_protocol,
)


PEDROTTI_FINGERPRINT = "efb194ad2c492768962320198d281c98574eb2dc22291279bfd176a15606a0d5"


def _protocol(**overrides):
    fields = {
        "case_study_id": "sampling-demo-v1",
        "dataset": {"name": "synthetic-source", "identity": "fixture-v1"},
        "representation": {"name": "native-stream", "unit": "px"},
        "endpoint": {"name": "condition contrast", "unit": "px/s"},
        "sampling": {
            "name": "sampling perturbation",
            "baseline_hz": 1000.0,
            "target_hz": [500.0, 250.0, 100.0],
        },
        "missingness": {
            "name": "missingness perturbation",
            "mechanisms": ["mcar", "block"],
            "fractions": [0.01, 0.10],
            "replicates": 20,
            "rng_seed": 123,
        },
        "interpretation": {
            "name": "recovery",
            "relative_tolerance": 0.20,
            "minimum_family_recovery": 0.90,
            "material_fragility_ceiling": 0.50,
        },
    }
    fields.update(overrides)
    return build_sampling_missingness_protocol(**fields)


def test_protocol_is_deterministic_fingerprinted_and_tamper_evident():
    first = _protocol()
    second = _protocol()

    assert first == second
    assert first["schema"] == SENSITIVITY_PROTOCOL_SCHEMA
    assert len(first["protocol_fingerprint"]) == 64
    assert verify_sampling_missingness_protocol(first)

    core = dict(first)
    stored = core.pop("protocol_fingerprint")
    assert stored == fingerprint(core)

    tampered = json.loads(json.dumps(first))
    tampered["sampling"]["target_hz"][0] = 400.0
    assert not verify_sampling_missingness_protocol(tampered)


def test_protocol_rejects_invalid_sampling_grid():
    with pytest.raises(ValueError, match="below baseline_hz"):
        _protocol(
            sampling={
                "name": "sampling perturbation",
                "baseline_hz": 500.0,
                "target_hz": [250.0, 500.0],
            }
        )

    with pytest.raises(ValueError, match="unique"):
        _protocol(
            sampling={
                "name": "sampling perturbation",
                "baseline_hz": 1000.0,
                "target_hz": [500.0, 500.0],
            }
        )


def test_protocol_rejects_invalid_missingness_contract():
    with pytest.raises(ValueError, match="strictly between 0 and 1"):
        _protocol(
            missingness={
                "name": "missingness perturbation",
                "mechanisms": ["mcar"],
                "fractions": [0.0, 0.1],
                "replicates": 20,
                "rng_seed": 123,
            }
        )

    with pytest.raises(ValueError, match="integer >= 2"):
        _protocol(
            missingness={
                "name": "missingness perturbation",
                "mechanisms": ["mcar"],
                "fractions": [0.1],
                "replicates": 1,
                "rng_seed": 123,
            }
        )


def test_protocol_rejects_overlapping_robust_and_fragile_thresholds():
    with pytest.raises(ValueError, match="must not exceed"):
        _protocol(
            interpretation={
                "name": "recovery",
                "relative_tolerance": 0.20,
                "minimum_family_recovery": 0.50,
                "material_fragility_ceiling": 0.75,
            }
        )


def test_frozen_pedrotti_protocol_is_packaged_identically_and_verified():
    root = Path(__file__).resolve().parents[1]
    docs_path = root / "docs" / "protocols" / "pedrotti2023_sampling_missingness_v1.json"
    package_path = (
        root / "src" / "gazeaudit" / "data" / "pedrotti2023_sampling_missingness_v1.json"
    )
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    packaged = json.loads(package_path.read_text(encoding="utf-8"))

    assert docs == packaged
    assert verify_sampling_missingness_protocol(docs)
    assert docs["protocol_fingerprint"] == PEDROTTI_FINGERPRINT

    core = dict(docs)
    core.pop("protocol_fingerprint")
    assert fingerprint(core) == PEDROTTI_FINGERPRINT

    expected_md5 = docs["dataset"]["source_files"]["expected_md5"]
    assert len(expected_md5) == 37
    assert set(expected_md5) == {
        *(f"{participant:02d}.txt" for participant in range(1, 37)),
        "readme.txt",
    }
    assert docs["sampling"]["target_hz"] == [500.0, 250.0, 125.0, 100.0, 50.0]
    assert docs["missingness"]["mechanisms"] == [
        "mcar_within_trial",
        "single_block_within_trial",
    ]
    assert docs["missingness"]["fractions"] == [0.01, 0.05, 0.10, 0.20]
    assert docs["missingness"]["replicates"] == 20
    assert docs["missingness"]["rng_seed"] == 20260913


def test_frozen_pedrotti_protocol_round_trips_through_builder():
    root = Path(__file__).resolve().parents[1]
    path = root / "docs" / "protocols" / "pedrotti2023_sampling_missingness_v1.json"
    document = json.loads(path.read_text(encoding="utf-8"))

    rebuilt = build_sampling_missingness_protocol(
        case_study_id=document["case_study_id"],
        dataset=document["dataset"],
        representation=document["representation"],
        endpoint=document["endpoint"],
        sampling=document["sampling"],
        missingness=document["missingness"],
        interpretation=document["interpretation"],
    )

    assert rebuilt == document
