from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "release" / "0.1.0-external-publication.json"
VERIFICATION_PATH = ROOT / "release" / "0.1.0-external-publication-verification.json"
GITHUB_MANIFEST_PATH = ROOT / "release" / "0.1.0-publication.json"

_SPEC = importlib.util.spec_from_file_location(
    "gazeaudit_external_publication_gate",
    ROOT / "tools" / "external_publication_gate.py",
)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("could not load external_publication_gate.py")
_GATE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_GATE)
validate = _GATE.validate
verify_payload = _GATE.verify_payload


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_external_publication_plan_binds_frozen_release() -> None:
    plan = _load(PLAN_PATH)
    github_manifest = _load(GITHUB_MANIFEST_PATH)
    for destination in ("pypi", "zenodo"):
        validate(
            plan,
            github_manifest,
            destination=destination,
            expected_version="0.1.0",
            expected_tag="v0.1.0",
            expected_commit="fdade23c12b3c2a2f26a1ca8398034b6f8d0213f",
        )
    assert plan["github_release"]["release_id"] == 388545002
    assert plan["github_release"]["publication_run_id"] == 34868438946
    assert plan["github_release"]["payload_artifact_id"] == 10358460785
    assert plan["scientific_record"] == {
        "gazebase": "incomplete",
        "korthals": "robust_negative",
        "pedrotti": "materially_fragile",
    }


def test_external_publication_verification_binds_completed_release() -> None:
    plan = _load(PLAN_PATH)
    verification = _load(VERIFICATION_PATH)

    assert verification["schema"] == "gazeaudit-external-publication-verification-v1"
    for field in ("version", "tag", "source_commit", "source_tree"):
        assert verification[field] == plan[field]
    assert verification["github_release"]["release_id"] == plan["github_release"]["release_id"]

    pypi = verification["pypi"]
    assert pypi["status"] == "published_verified"
    assert pypi["publication_run_id"] == 34887345589
    assert pypi["publication_job_id"] == 104121447203
    assert pypi["payload_artifact_id"] == 10366130093
    assert pypi["wheel"] == plan["payload"]["wheel"]
    assert pypi["sdist"]["filename"] == plan["payload"]["sdist"]["filename"]
    assert pypi["sdist"]["size_bytes"] == plan["payload"]["sdist"]["size_bytes"]
    assert pypi["sdist"]["sha256"] == plan["payload"]["sdist"]["sha256"]
    assert pypi["sdist"]["md5"] == "7550c722e9ad18e4dd288c7e1aad7f05"

    zenodo = verification["zenodo"]
    assert zenodo["status"] == "published_verified"
    assert zenodo["record_id"] == 22757340
    assert zenodo["version_doi"] == "10.5281/zenodo.22757340"
    assert zenodo["concept_doi"] == "10.5281/zenodo.22757339"
    assert zenodo["resource_type"] == "software"
    assert zenodo["license"] == "MIT"
    assert zenodo["file"]["filename"] == plan["payload"]["sdist"]["filename"]
    assert zenodo["file"]["size_bytes"] == plan["payload"]["sdist"]["size_bytes"]
    assert zenodo["file"]["sha256"] == plan["payload"]["sdist"]["sha256"]
    assert zenodo["file"]["md5"] == "7550c722e9ad18e4dd288c7e1aad7f05"
    assert zenodo["independent_download_verification"] == {
        "workflow_run_id": 34889732485,
        "job_id": 104129090621,
        "runner": "ubuntu-24.04",
        "result": "success",
    }
    assert zenodo["keywords"] == [
        "eye tracking",
        "gaze",
        "measurement uncertainty",
        "inferential robustness",
        "multiverse analysis",
        "area of interest",
    ]
    assert verification["scientific_record"] == plan["scientific_record"]


def test_external_gate_verifies_pypi_two_file_payload(tmp_path: Path) -> None:
    plan = _load(PLAN_PATH)
    for family, payload in (("wheel", b"wheel"), ("sdist", b"sdist")):
        record = plan["payload"][family]
        path = tmp_path / record["filename"]
        path.write_bytes(payload)
        record["size_bytes"] = path.stat().st_size
        record["sha256"] = hashlib.sha256(payload).hexdigest()

    verify_payload(plan, "pypi", tmp_path)
    (tmp_path / plan["payload"]["wheel"]["filename"]).write_bytes(b"tampered")
    with pytest.raises(ValueError, match="wheel size mismatch|wheel SHA-256 mismatch"):
        verify_payload(plan, "pypi", tmp_path)


def test_external_gate_verifies_zenodo_sdist_only(tmp_path: Path) -> None:
    plan = _load(PLAN_PATH)
    record = plan["payload"]["sdist"]
    path = tmp_path / record["filename"]
    payload = b"canonical-source-archive"
    path.write_bytes(payload)
    record["size_bytes"] = path.stat().st_size
    record["sha256"] = hashlib.sha256(payload).hexdigest()

    verify_payload(plan, "zenodo", tmp_path)
    extra = tmp_path / plan["payload"]["wheel"]["filename"]
    extra.write_bytes(b"wheel")
    with pytest.raises(ValueError, match="payload directory mismatch"):
        verify_payload(plan, "zenodo", tmp_path)


def test_pypi_workflow_is_manual_oidc_and_fail_closed() -> None:
    text = (ROOT / ".github" / "workflows" / "publish-pypi.yml").read_text(
        encoding="utf-8"
    )
    assert "workflow_dispatch:" in text
    assert "github.ref == 'refs/heads/main'" in text
    assert "GH_TOKEN: ${{ github.token }}" in text
    assert "gh release download" in text
    assert "external_publication_gate.py" in text
    assert "environment:" in text and "name: pypi" in text
    assert "id-token: write" in text
    assert "pypa/gh-action-pypi-publish@release/v1" in text
    assert "skip-existing: false" in text
    assert "twine upload" not in text
    assert "PYPI_TOKEN" not in text
    assert "password:" not in text
    assert "git tag" not in text


def test_external_publication_guide_preserves_zenodo_single_file_boundary() -> None:
    text = (ROOT / "docs" / "EXTERNAL_PUBLICATION_0.1.0.md").read_text(
        encoding="utf-8"
    )
    assert "publish-pypi.yml" in text
    assert "Trusted Publishing" in text
    assert "gazeaudit-0.1.0.tar.gz" in text
    assert "CITATION.cff@v0.1.0" in text
    assert "10.5281/zenodo.22757340" in text
    assert "10.5281/zenodo.22757339" in text
    assert "34889732485" in text
    assert "104129090621" in text
