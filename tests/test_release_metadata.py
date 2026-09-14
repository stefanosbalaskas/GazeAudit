from __future__ import annotations

import re
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _quoted_scalar(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*\"([^\"]+)\"\s*$", text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"missing quoted scalar: {key}")
    return match.group(1)


def test_citation_version_matches_installed_package() -> None:
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert _quoted_scalar(citation, "version") == version("gazeaudit")


def test_release_metadata_is_stable_alpha_candidate() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release = (ROOT / "docs" / "RELEASE.md").read_text(encoding="utf-8")

    assert 'version = "0.1.0"' in pyproject
    assert 'version = "0.1.0.dev20"' not in pyproject
    assert '"Development Status :: 3 - Alpha"' in pyproject
    assert "Development Status :: 2 - Pre-Alpha" not in pyproject
    assert "pre-alpha" not in readme.lower()
    assert "## 0.1.0 — 2026-09-14" in changelog
    assert "stable `0.1.0` candidate metadata" in release
    assert "does not, by itself" in release


def test_authoritative_validation_matrix_binds_canonical_outcomes() -> None:
    matrix = (ROOT / "docs" / "VALIDATION_MATRIX.md").read_text(encoding="utf-8")

    required = {
        "2fae4e99243e6738047a34b8dc24a183e8fb98606e4873723d43b8baa4ae937b",
        "2eaab8171d9d5f70e138eb929554648cb6bed10b21646ab0acd7cfae4d607d11",
        "b411fe6a5f4ad7035ac606d60a952306c0b818d956f7b4930827b8cbe10ae8d5",
        "`incomplete`",
        "`robust_negative`",
        "`materially_fragile`",
    }
    assert all(value in matrix for value in required)


def test_pedrotti_authoritative_record_binds_execution_and_artifact() -> None:
    record = (
        ROOT / "docs" / "results" / "pedrotti_sampling_missingness_v1.md"
    ).read_text(encoding="utf-8")

    assert "34793103977" in record
    assert "10328414078" in record
    assert "35dd53da10646400aca657c388f8b77a6a974c555de7efbd6f83faeb970b1eb6" in record
    assert "**Classification: `materially_fragile`.**" in record
