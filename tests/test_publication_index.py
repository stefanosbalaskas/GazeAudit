from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "docs" / "REPRODUCIBILITY_INDEX.json"
SUMMARY_PATH = ROOT / "docs" / "PUBLICATION_SUMMARY.md"
CITATION_PATH = ROOT / "docs" / "CITATION_AND_REUSE.md"

EXPECTED = {
    "gazebase-multidetector": {
        "classification": "incomplete",
        "protocol": (
            "3f64122f62cbc9762b0bd0e0b95c7fef"
            "6ff40c4700215ee4b90f005af77003b1"
        ),
        "artifact_id": 10284017265,
        "zip_sha256": (
            "2fae4e99243e6738047a34b8dc24a183"
            "e8fb98606e4873723d43b8baa4ae937b"
        ),
    },
    "korthals-target-tracking-aoi-v2": {
        "classification": "robust_negative",
        "protocol": (
            "1cd4150c9341db145b8f6aee544f9634"
            "c67c46116e61e7e675ae3c50282d2d55"
        ),
        "artifact_id": 10306308440,
        "zip_sha256": (
            "2eaab8171d9d5f70e138eb929554648cb"
            "6bed10b21646ab0acd7cfae4d607d11"
        ),
    },
    "pedrotti-reading-numerals-sampling-missingness-v1": {
        "classification": "materially_fragile",
        "protocol": (
            "efb194ad2c492768962320198d281c985"
            "74eb2dc22291279bfd176a15606a0d5"
        ),
        "artifact_id": 10328414078,
        "zip_sha256": (
            "b411fe6a5f4ad7035ac606d60a952306"
            "c0b818d956f7b4930827b8cbe10ae8d5"
        ),
    },
}


def _index() -> dict[str, object]:
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def _path_values(value: object, key: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for child_key, child in value.items():
            found.extend(_path_values(child, child_key))
    elif isinstance(value, list):
        for child in value:
            found.extend(_path_values(child, key))
    elif isinstance(value, str) and (key == "path" or key.endswith("_path")):
        found.append(value)
    return found


def test_reproducibility_index_binds_canonical_cases() -> None:
    index = _index()
    assert index["schema"] == "gazeaudit-reproducibility-index-v1"
    cases = {case["case_id"]: case for case in index["cases"]}
    assert set(cases) == set(EXPECTED)

    for case_id, expected in EXPECTED.items():
        case = cases[case_id]
        assert case["canonical_classification"] == expected["classification"]
        assert case["protocol"]["fingerprint"] == expected["protocol"]
        assert case["scientific_artifact"]["artifact_id"] == expected["artifact_id"]
        assert case["scientific_artifact"]["zip_sha256"] == expected["zip_sha256"]


def test_reproducibility_index_distinguishes_source_control_modes() -> None:
    cases = {case["case_id"]: case for case in _index()["cases"]}

    gazebase = cases["gazebase-multidetector"]["source_control"]
    assert gazebase["mode"] == "execution_bound_source_identity"
    assert gazebase["separate_source_freeze"] is False

    korthals = cases["korthals-target-tracking-aoi-v2"]["source_control"]
    assert korthals["mode"] == "endpoint_blind_source_freeze"
    assert korthals["run_id"] == 34719412734
    assert korthals["artifact_id"] == 10305414874

    pedrotti_id = "pedrotti-reading-numerals-sampling-missingness-v1"
    pedrotti = cases[pedrotti_id]["source_control"]
    assert pedrotti["mode"] == "endpoint_blind_source_freeze"
    assert pedrotti["run_id"] == 34786624831
    assert pedrotti["artifact_id"] == 10326523152


def test_all_indexed_repository_paths_exist() -> None:
    paths = _path_values(_index())
    assert paths
    missing = [path for path in paths if not (ROOT / path).is_file()]
    assert missing == []


def test_publication_docs_bind_index_and_interpretation_boundary() -> None:
    summary = SUMMARY_PATH.read_text(encoding="utf-8")
    citation = CITATION_PATH.read_text(encoding="utf-8")

    assert "REPRODUCIBILITY_INDEX.json" in summary
    assert "VALIDATION_MATRIX.md" in summary
    assert "0.1.0.dev20" in summary
    assert "not a claim that `0.1.0` has been tagged" in summary

    for expected in EXPECTED.values():
        assert expected["classification"] in summary
        assert expected["protocol"] in summary
        assert expected["zip_sha256"] in summary

    assert "exact GazeAudit commit" in citation
    assert "source identity" in citation
    assert "protocol identity" in citation
    assert "execution identity" in citation
    assert "artifact identity" in citation
    assert "GitHub Release and PyPI stages are verified" in citation
    assert "Zenodo remained outside that release tranche" in citation
