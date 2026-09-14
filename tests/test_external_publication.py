from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "release" / "0.1.0-external-publication.json"
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
    assert "pending Trusted Publisher" in text
    assert "publish-pypi.yml" in text
    assert "GitHub environment: `pypi`" in text
    assert "Upload **exactly one file**" in text
    assert "gazeaudit-0.1.0.tar.gz" in text
    assert "Do not upload the wheel" in text
    assert "CITATION.cff@v0.1.0" in text
