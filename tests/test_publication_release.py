from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.publication_gate import load_manifest, validate_manifest, verify_distributions

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release" / "0.1.0-publication.json"


def test_publication_manifest_binds_canonical_release() -> None:
    document = validate_manifest(
        load_manifest(MANIFEST),
        expected_version="0.1.0",
        expected_tag="v0.1.0",
        expected_commit="fdade23c12b3c2a2f26a1ca8398034b6f8d0213f",
    )
    assert document["tag_object_sha"] == "51e9739e305b14c9cb97392b1cf8bdc28a01b132"
    assert document["source_tree"] == "938007cda6051d50243fff27a892870f7128d407"
    assert document["distributions"]["wheel"]["sha256"] == (
        "51fa1f0a0388dfe337fad0d6564df802ae8464f01d5ce666cc96ce2e144271a1"
    )
    assert document["distributions"]["sdist"]["sha256"] == (
        "8c449e2fc469c2b91f1c2471b674b5d6b16b6e6aa883289069ffb0a679517173"
    )
    assert document["qualification"]["pre_tag"]["run_id"] == 34835220715
    assert document["qualification"]["tag_bound"]["run_id"] == 34836251771
    assert document["scientific_record"] == {
        "gazebase": "incomplete",
        "korthals": "robust_negative",
        "pedrotti": "materially_fragile",
    }


def test_publication_gate_verifies_exact_distribution_bytes(tmp_path: Path) -> None:
    wheel = tmp_path / "gazeaudit-0.1.0-py3-none-any.whl"
    sdist = tmp_path / "gazeaudit-0.1.0.tar.gz"
    wheel.write_bytes(b"wheel-bytes")
    sdist.write_bytes(b"sdist-bytes")

    document = load_manifest(MANIFEST)
    for family, path in (("wheel", wheel), ("sdist", sdist)):
        document["distributions"][family]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        document["distributions"][family]["size_bytes"] = path.stat().st_size

    validate_manifest(
        document,
        expected_version="0.1.0",
        expected_tag="v0.1.0",
        expected_commit="fdade23c12b3c2a2f26a1ca8398034b6f8d0213f",
    )
    verify_distributions(document, tmp_path)

    wheel.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="wheel size mismatch|wheel SHA-256 mismatch"):
        verify_distributions(document, tmp_path)


def test_github_release_workflow_is_manual_fail_closed_and_not_pypi() -> None:
    text = (ROOT / ".github" / "workflows" / "publish-github-release.yml").read_text(
        encoding="utf-8"
    )
    assert "workflow_dispatch:" in text
    assert "contents: write" in text
    assert "github.ref == 'refs/heads/main'" in text
    assert "gh release create" in text
    assert "--draft" in text
    assert "gh release download" in text
    assert "publication_gate.py" in text
    assert "gh release edit" in text
    assert "--draft=false" in text
    assert "id-token: write" not in text
    assert "gh-action-pypi-publish" not in text
    assert "twine upload" not in text
    assert "git tag" not in text


def test_release_candidate_workflow_remains_read_only() -> None:
    text = (ROOT / ".github" / "workflows" / "release-candidate.yml").read_text(
        encoding="utf-8"
    )
    assert "contents: read" in text
    assert "contents: write" not in text
    assert "gh release create" not in text


def test_release_notes_preserve_publication_boundary() -> None:
    notes = (ROOT / "docs" / "RELEASE_NOTES_0.1.0.md").read_text(encoding="utf-8")
    for classification in ("incomplete", "robust_negative", "materially_fragile"):
        assert classification in notes
    assert "does **not** imply" in notes
    assert "PyPI" in notes
