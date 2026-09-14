from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_GATE = ROOT / "tools" / "release_gate.py"


def _run_gate(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RELEASE_GATE), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_current_development_metadata_is_internally_consistent() -> None:
    result = _run_gate()
    assert result.returncode == 0, result.stderr
    assert "0.1.0.dev20" in result.stdout


def test_current_development_version_is_not_stable_release_eligible() -> None:
    result = _run_gate("--require-stable", "--require-changelog-entry")
    assert result.returncode != 0
    assert "not a stable X.Y.Z release" in result.stderr


def test_stable_release_fixture_passes_exact_version_tag_and_changelog_gate(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "gazeaudit"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "CITATION.cff").write_text(
        'cff-version: 1.2.0\nversion: "0.1.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 0.1.0 — 2026-09-14\n",
        encoding="utf-8",
    )

    result = _run_gate(
        "--project-root",
        str(tmp_path),
        "--expected-version",
        "0.1.0",
        "--tag",
        "v0.1.0",
        "--require-stable",
        "--require-changelog-entry",
    )
    assert result.returncode == 0, result.stderr


def test_release_gate_rejects_wrong_tag(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "gazeaudit"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "CITATION.cff").write_text(
        'cff-version: 1.2.0\nversion: "0.1.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 0.1.0 — 2026-09-14\n",
        encoding="utf-8",
    )

    result = _run_gate(
        "--project-root",
        str(tmp_path),
        "--tag",
        "v0.1.1",
    )
    assert result.returncode != 0
    assert "must equal v0.1.0" in result.stderr


def test_release_workflows_are_qualification_only() -> None:
    distribution = (
        ROOT / ".github" / "workflows" / "distribution.yml"
    ).read_text(encoding="utf-8")
    release = (
        ROOT / ".github" / "workflows" / "release-candidate.yml"
    ).read_text(encoding="utf-8")
    combined = f"{distribution}\n{release}".lower()

    forbidden = {
        "pypa/gh-action-pypi-publish",
        "twine upload",
        "gh release create",
        "softprops/action-gh-release",
        "id-token: write",
        "packages: write",
    }
    assert all(token not in combined for token in forbidden)

    assert "python -m build" in distribution
    assert "python -m twine check dist/*" in distribution
    assert "python tools/verify_distribution.py dist" in distribution
    assert "python -m venv .wheel-smoke" in distribution

    assert "python tools/release_gate.py" in release
    assert '--tag "$GITHUB_REF_NAME"' in release
    assert "--require-stable" in release
    assert "actions/upload-artifact@v7" in release
