import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gazeaudit.aoi import RectangleAOI
from gazeaudit.aoi_artifacts import (
    verify_aoi_uncertainty_artifacts,
    write_aoi_uncertainty_artifacts,
)
from gazeaudit.aoi_propagation import audit_aoi_effect_uncertainty
from gazeaudit.aoi_protocol import (
    AOI_UNCERTAINTY_PROTOCOL_SCHEMA,
    build_aoi_uncertainty_protocol,
    verify_aoi_uncertainty_protocol,
)
from gazeaudit.scientific_benchmark import condition_dwell_effect
from gazeaudit.uncertainty import GaussianGazeErrorModel


def _data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "participant": ["p1", "p1", "p2", "p2"],
            "condition": ["control", "treatment", "control", "treatment"],
            "duration": [100.0, 100.0, 200.0, 200.0],
            "observed_x": [-5.0, 5.0, -5.0, 5.0],
            "observed_y": [0.0, 0.0, 0.0, 0.0],
        }
    )


def _aoi() -> RectangleAOI:
    return RectangleAOI("right", 0.0, -10.0, 10.0, 10.0)


def _protocol(*, draws: int = 32, interval: float = 0.95, reference: float = 0.0):
    return build_aoi_uncertainty_protocol(
        case_study_id="aoi-demo-v1",
        dataset={
            "name": "synthetic-demo",
            "identity": "fixture-v1",
            "role": "scientific observations",
        },
        validation={
            "name": "synthetic-validation",
            "identity": "fixture-validation-v1",
            "target_truth": "known",
        },
        aoi={
            "name": "right",
            "geometry": "rectangle",
            "xmin": 0.0,
            "ymin": -10.0,
            "xmax": 10.0,
            "ymax": 10.0,
        },
        endpoint={
            "name": "within-participant treatment-minus-control dwell",
            "unit": "ms",
        },
        error_model={
            "name": "global-bivariate-gaussian",
            "fit": "validation observed-minus-target errors",
        },
        monte_carlo={
            "draws": draws,
            "batch_size": 7,
            "interval": interval,
            "reference": reference,
            "rng_seed": 123,
        },
        interpretation={
            "name": "measurement-uncertainty audit",
            "rule": "report distribution without population-CI interpretation",
        },
    )


def _audit(*, draws: int = 32, interval: float = 0.95, reference: float = 0.0):
    model = GaussianGazeErrorModel(
        mean_error=np.zeros(2),
        covariance=np.eye(2) * 4.0,
        n_validation=20,
    )
    return audit_aoi_effect_uncertainty(
        _data(),
        _aoi(),
        model,
        condition_dwell_effect,
        draws=draws,
        batch_size=7,
        interval=interval,
        reference=reference,
        rng=123,
    )


def test_protocol_is_deterministic_verified_and_fingerprinted():
    first = _protocol()
    second = _protocol()

    assert first == second
    assert first["schema"] == AOI_UNCERTAINTY_PROTOCOL_SCHEMA
    assert len(first["protocol_fingerprint"]) == 64
    assert verify_aoi_uncertainty_protocol(first)

    tampered = json.loads(json.dumps(first))
    tampered["aoi"]["xmin"] = 1.0
    assert not verify_aoi_uncertainty_protocol(tampered)


def test_protocol_requires_reproducible_scientific_identity_and_mc_settings():
    with pytest.raises(ValueError, match="case_study_id"):
        build_aoi_uncertainty_protocol(
            case_study_id=" ",
            dataset={"name": "d"},
            validation={"name": "v"},
            aoi={"name": "a"},
            endpoint={"name": "e"},
            error_model={"name": "m"},
            monte_carlo={
                "draws": 32,
                "batch_size": 4,
                "interval": 0.95,
                "reference": 0.0,
                "rng_seed": 1,
            },
            interpretation={"name": "rule"},
        )

    with pytest.raises(ValueError, match="dataset.*name"):
        build_aoi_uncertainty_protocol(
            case_study_id="x",
            dataset={"id": "d"},
            validation={"name": "v"},
            aoi={"name": "a"},
            endpoint={"name": "e"},
            error_model={"name": "m"},
            monte_carlo={
                "draws": 32,
                "batch_size": 4,
                "interval": 0.95,
                "reference": 0.0,
                "rng_seed": 1,
            },
            interpretation={"name": "rule"},
        )

    bad = _protocol()
    core = dict(bad)
    core.pop("protocol_fingerprint")
    core["monte_carlo"] = dict(core["monte_carlo"])
    core["monte_carlo"].pop("rng_seed")
    with pytest.raises(ValueError, match="rng_seed"):
        build_aoi_uncertainty_protocol(
            case_study_id=core["case_study_id"],
            dataset=core["dataset"],
            validation=core["validation"],
            aoi=core["aoi"],
            endpoint=core["endpoint"],
            error_model=core["error_model"],
            monte_carlo=core["monte_carlo"],
            interpretation=core["interpretation"],
        )


def test_artifact_writer_is_deterministic_and_verified(tmp_path: Path):
    audit = _audit()
    protocol = _protocol()
    first = tmp_path / "first"
    second = tmp_path / "second"

    first_manifest = write_aoi_uncertainty_artifacts(audit, protocol, first)
    second_manifest = write_aoi_uncertainty_artifacts(audit, protocol, second)

    assert first_manifest == second_manifest
    assert verify_aoi_uncertainty_artifacts(first)
    assert verify_aoi_uncertainty_artifacts(second)
    assert first_manifest["protocol_fingerprint"] == protocol["protocol_fingerprint"]
    assert len(first_manifest["scientific_fingerprint"]) == 64
    assert len(first_manifest["artifact_manifest_fingerprint"]) == 64

    for name in (
        "protocol.json",
        "summary.json",
        "draw_effects.csv",
        "membership_probabilities.csv",
        "artifact_manifest.json",
        "SHA256SUMS",
    ):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_artifact_writer_rejects_protocol_audit_mismatch(tmp_path: Path):
    audit = _audit(draws=32)
    mismatched = _protocol(draws=64)

    with pytest.raises(ValueError, match="does not match"):
        write_aoi_uncertainty_artifacts(audit, mismatched, tmp_path / "bad")

    mismatched_aoi = _protocol()
    mismatched_aoi = json.loads(json.dumps(mismatched_aoi))
    core = dict(mismatched_aoi)
    core.pop("protocol_fingerprint")
    core["aoi"] = dict(core["aoi"])
    core["aoi"]["name"] = "left"
    mismatched_aoi = build_aoi_uncertainty_protocol(
        case_study_id=core["case_study_id"],
        dataset=core["dataset"],
        validation=core["validation"],
        aoi=core["aoi"],
        endpoint=core["endpoint"],
        error_model=core["error_model"],
        monte_carlo=core["monte_carlo"],
        interpretation=core["interpretation"],
    )
    with pytest.raises(ValueError, match="does not match|AOI"):
        write_aoi_uncertainty_artifacts(audit, mismatched_aoi, tmp_path / "bad-aoi")


def test_artifact_verifier_detects_result_and_protocol_tampering(tmp_path: Path):
    audit = _audit()
    protocol = _protocol()
    root = tmp_path / "audit"
    write_aoi_uncertainty_artifacts(audit, protocol, root)

    draw_path = root / "draw_effects.csv"
    original = draw_path.read_text(encoding="utf-8")
    draw_path.write_text(original + "# tampered\n", encoding="utf-8")
    assert not verify_aoi_uncertainty_artifacts(root)

    write_aoi_uncertainty_artifacts(audit, protocol, root, overwrite=True)
    protocol_path = root / "protocol.json"
    document = json.loads(protocol_path.read_text(encoding="utf-8"))
    document["endpoint"]["unit"] = "seconds"
    protocol_path.write_text(json.dumps(document), encoding="utf-8")
    assert not verify_aoi_uncertainty_artifacts(root)


def test_artifact_writer_refuses_nonempty_directory_without_overwrite(tmp_path: Path):
    root = tmp_path / "audit"
    root.mkdir()
    (root / "keep.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(FileExistsError, match="not empty"):
        write_aoi_uncertainty_artifacts(_audit(), _protocol(), root)
