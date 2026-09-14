#!/usr/bin/env python3
"""Fail-closed version/tag/changelog gate for a future GazeAudit release candidate."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_STABLE_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def _project_version(root: Path) -> str:
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', text, re.MULTILINE)
    if match is None:
        raise ValueError("pyproject.toml does not contain a quoted project version")
    return match.group(1)


def _citation_version(root: Path) -> str:
    text = (root / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(r'^version:\s*"([^"]+)"\s*$', text, re.MULTILINE)
    if match is None:
        raise ValueError("CITATION.cff does not contain a quoted version")
    return match.group(1)


def _has_changelog_entry(root: Path, version: str) -> bool:
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^##\s+(?:\[{re.escape(version)}\]|{re.escape(version)})(?:\s+[-—].*)?$",
        re.MULTILINE,
    )
    return pattern.search(text) is not None


def validate_release_gate(
    root: Path,
    *,
    expected_version: str | None = None,
    tag: str | None = None,
    require_stable: bool = False,
    require_changelog_entry: bool = False,
) -> str:
    project = _project_version(root)
    citation = _citation_version(root)
    if citation != project:
        raise ValueError(
            f"CITATION.cff version {citation!r} differs from project version {project!r}"
        )
    if expected_version is not None and project != expected_version:
        raise ValueError(
            f"project version {project!r} differs from expected {expected_version!r}"
        )
    if tag is not None and tag != f"v{project}":
        raise ValueError(f"tag {tag!r} must equal v{project}")
    if require_stable and _STABLE_VERSION.fullmatch(project) is None:
        raise ValueError(f"project version {project!r} is not a stable X.Y.Z release")
    if require_changelog_entry and not _has_changelog_entry(root, project):
        raise ValueError(f"CHANGELOG.md lacks a level-2 release entry for {project}")
    return project


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--expected-version")
    parser.add_argument("--tag")
    parser.add_argument("--require-stable", action="store_true")
    parser.add_argument("--require-changelog-entry", action="store_true")
    args = parser.parse_args()

    version = validate_release_gate(
        args.project_root,
        expected_version=args.expected_version,
        tag=args.tag,
        require_stable=args.require_stable,
        require_changelog_entry=args.require_changelog_entry,
    )
    print(f"release gate: eligible metadata for {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
