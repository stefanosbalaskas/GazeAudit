#!/usr/bin/env python3
"""Fail-closed publication manifest and distribution verifier."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

_SCHEMA = "gazeaudit-publication-manifest-v1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("publication manifest must be a JSON object")
    return document


def validate_manifest(
    document: dict[str, Any],
    *,
    expected_version: str,
    expected_tag: str,
    expected_commit: str,
) -> dict[str, Any]:
    if document.get("schema") != _SCHEMA:
        raise ValueError("unexpected publication manifest schema")
    if document.get("version") != expected_version:
        raise ValueError("publication manifest version mismatch")
    if document.get("tag") != expected_tag:
        raise ValueError("publication manifest tag mismatch")
    if expected_tag != f"v{expected_version}":
        raise ValueError("expected tag must equal v{expected_version}")
    if document.get("source_commit") != expected_commit:
        raise ValueError("publication manifest source commit mismatch")
    if _SHA1.fullmatch(str(document.get("source_tree", ""))) is None:
        raise ValueError("publication manifest source tree is not a Git SHA")
    if _SHA1.fullmatch(str(document.get("tag_object_sha", ""))) is None:
        raise ValueError("publication manifest tag object is not a Git SHA")

    distributions = document.get("distributions")
    if not isinstance(distributions, dict) or set(distributions) != {"wheel", "sdist"}:
        raise ValueError("publication manifest must define wheel and sdist only")
    expected_names = {
        "wheel": f"gazeaudit-{expected_version}-py3-none-any.whl",
        "sdist": f"gazeaudit-{expected_version}.tar.gz",
    }
    for family, expected_name in expected_names.items():
        record = distributions[family]
        if not isinstance(record, dict):
            raise ValueError(f"{family} publication record must be an object")
        if record.get("filename") != expected_name:
            raise ValueError(f"unexpected {family} filename")
        if _SHA256.fullmatch(str(record.get("sha256", ""))) is None:
            raise ValueError(f"invalid {family} SHA-256")
        size = record.get("size_bytes")
        if not isinstance(size, int) or size <= 0:
            raise ValueError(f"invalid {family} size")

    scope = document.get("publication_scope")
    if scope != {
        "github_release": True,
        "pypi": False,
        "doi_or_archival_registry": False,
    }:
        raise ValueError("publication scope must authorize GitHub Release only")
    return document


def verify_distributions(document: dict[str, Any], dist_dir: Path) -> None:
    actual_files = sorted(path.name for path in dist_dir.iterdir() if path.is_file())
    expected_files = sorted(
        record["filename"] for record in document["distributions"].values()
    )
    if actual_files != expected_files:
        raise ValueError(
            f"distribution directory mismatch: expected {expected_files}, got {actual_files}"
        )
    for family, record in document["distributions"].items():
        path = dist_dir / record["filename"]
        if path.stat().st_size != record["size_bytes"]:
            raise ValueError(f"{family} size mismatch")
        if _sha256(path) != record["sha256"]:
            raise ValueError(f"{family} SHA-256 mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--expected-tag", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--dist-dir", type=Path)
    args = parser.parse_args()

    document = validate_manifest(
        load_manifest(args.manifest),
        expected_version=args.expected_version,
        expected_tag=args.expected_tag,
        expected_commit=args.expected_commit,
    )
    if args.dist_dir is not None:
        verify_distributions(document, args.dist_dir)
    print(
        "publication gate: verified "
        f"{args.expected_tag} at {args.expected_commit} for GitHub Release"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
