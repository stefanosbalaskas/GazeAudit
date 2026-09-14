#!/usr/bin/env python3
"""Verify the contents and metadata of built GazeAudit distributions."""

from __future__ import annotations

import argparse
import email
import hashlib
import re
import tarfile
import zipfile
from pathlib import Path

PROJECT_NAME = "gazeaudit"
REQUIRED_PACKAGE_DATA = {
    "gazeaudit/data/gazebase_multidetector_protocol.json",
    "gazeaudit/data/korthals2026_source_lock_v2.json",
    "gazeaudit/data/korthals2026_target_tracking_aoi_v1.json",
    "gazeaudit/data/korthals2026_target_tracking_aoi_v2.json",
    "gazeaudit/data/pedrotti2023_sampling_missingness_v1.json",
    "gazeaudit/data/pedrotti2023_source_lock_v1.json",
}
REQUIRED_SDIST_ROOT_FILES = {
    "CHANGELOG.md",
    "CITATION.cff",
    "LICENSE",
    "README.md",
    "pyproject.toml",
}


def project_version(project_root: Path) -> str:
    text = (project_root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', text, re.MULTILINE)
    if match is None:
        raise ValueError("pyproject.toml does not contain a quoted project version")
    return match.group(1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _single_match(dist_dir: Path, pattern: str, kind: str) -> Path:
    matches = sorted(dist_dir.glob(pattern))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {kind}, found {len(matches)}")
    return matches[0]


def verify_wheel(wheel: Path, version: str) -> dict[str, object]:
    expected_name = f"gazeaudit-{version}-py3-none-any.whl"
    if wheel.name != expected_name:
        raise ValueError(f"unexpected wheel filename: {wheel.name}")

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        if "gazeaudit/__init__.py" not in names:
            raise ValueError("wheel does not contain gazeaudit/__init__.py")
        missing = sorted(REQUIRED_PACKAGE_DATA - names)
        if missing:
            raise ValueError(f"wheel is missing scientific package data: {missing}")
        forbidden = [name for name in names if name.startswith(("tests/", ".github/"))]
        if forbidden:
            raise ValueError(f"wheel contains repository-only paths: {forbidden[:5]}")

        metadata_names = sorted(
            name for name in names if name.endswith(".dist-info/METADATA")
        )
        if len(metadata_names) != 1:
            raise ValueError("wheel must contain exactly one dist-info/METADATA file")
        message = email.message_from_bytes(archive.read(metadata_names[0]))
        if message.get("Name") != PROJECT_NAME:
            raise ValueError("wheel METADATA project name is not gazeaudit")
        if message.get("Version") != version:
            raise ValueError("wheel METADATA version differs from pyproject.toml")
        if message.get("Requires-Python") != ">=3.10":
            raise ValueError("wheel Requires-Python differs from the release contract")
        classifiers = message.get_all("Classifier", [])
        if "Development Status :: 3 - Alpha" not in classifiers:
            raise ValueError("wheel METADATA does not declare Alpha status")

        entry_points = sorted(
            name for name in names if name.endswith(".dist-info/entry_points.txt")
        )
        if len(entry_points) != 1:
            raise ValueError("wheel must contain exactly one entry_points.txt")
        entry_text = archive.read(entry_points[0]).decode("utf-8")
        required_scripts = {
            "gazeaudit-gazebase-run",
            "gazeaudit-korthals-source-freeze",
            "gazeaudit-pedrotti-source-freeze",
        }
        absent = sorted(script for script in required_scripts if script not in entry_text)
        if absent:
            raise ValueError(f"wheel is missing expected console scripts: {absent}")

    return {
        "path": wheel.name,
        "sha256": sha256(wheel),
        "size_bytes": wheel.stat().st_size,
        "member_count": len(names),
    }


def verify_sdist(sdist: Path, version: str) -> dict[str, object]:
    expected_name = f"gazeaudit-{version}.tar.gz"
    if sdist.name != expected_name:
        raise ValueError(f"unexpected sdist filename: {sdist.name}")
    root = f"gazeaudit-{version}/"

    with tarfile.open(sdist, "r:gz") as archive:
        names = {member.name for member in archive.getmembers() if member.isfile()}
        if any(not name.startswith(root) for name in names):
            raise ValueError("sdist contains a file outside the expected root directory")
        relative = {name.removeprefix(root) for name in names}
        missing_root = sorted(REQUIRED_SDIST_ROOT_FILES - relative)
        if missing_root:
            raise ValueError(f"sdist is missing release metadata files: {missing_root}")
        required_data = {
            f"src/{name}" for name in REQUIRED_PACKAGE_DATA
        }
        missing_data = sorted(required_data - relative)
        if missing_data:
            raise ValueError(f"sdist is missing scientific package data: {missing_data}")

    return {
        "path": sdist.name,
        "sha256": sha256(sdist),
        "size_bytes": sdist.stat().st_size,
        "member_count": len(names),
    }


def verify_distribution(dist_dir: Path, project_root: Path) -> dict[str, object]:
    if not dist_dir.is_dir():
        raise ValueError(f"distribution directory does not exist: {dist_dir}")
    version = project_version(project_root)
    wheel = _single_match(dist_dir, "*.whl", "wheel")
    sdist = _single_match(dist_dir, "*.tar.gz", "sdist")
    return {
        "project": PROJECT_NAME,
        "version": version,
        "wheel": verify_wheel(wheel, version),
        "sdist": verify_sdist(sdist, version),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist_dir", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    report = verify_distribution(args.dist_dir, args.project_root)
    print(f"distribution verification: {report['project']} {report['version']}")
    for kind in ("wheel", "sdist"):
        record = report[kind]
        print(
            f"{kind}: {record['path']} sha256={record['sha256']} "
            f"size={record['size_bytes']} members={record['member_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
