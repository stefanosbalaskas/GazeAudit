#!/usr/bin/env python3
"""Fail-closed verifier for PyPI/Zenodo publication transport."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

_PLAN_SCHEMA = "gazeaudit-external-publication-plan-v1"
_GITHUB_SCHEMA = "gazeaudit-publication-manifest-v1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return document


def validate(
    plan: dict[str, Any],
    github_manifest: dict[str, Any],
    *,
    destination: str,
    expected_version: str,
    expected_tag: str,
    expected_commit: str,
) -> None:
    if plan.get("schema") != _PLAN_SCHEMA:
        raise ValueError("unexpected external publication plan schema")
    if github_manifest.get("schema") != _GITHUB_SCHEMA:
        raise ValueError("unexpected GitHub publication manifest schema")
    if expected_tag != f"v{expected_version}":
        raise ValueError("expected tag must equal v{expected_version}")
    for document, label in ((plan, "plan"), (github_manifest, "GitHub manifest")):
        if document.get("version") != expected_version:
            raise ValueError(f"{label} version mismatch")
        if document.get("tag") != expected_tag:
            raise ValueError(f"{label} tag mismatch")
        if document.get("source_commit") != expected_commit:
            raise ValueError(f"{label} source commit mismatch")

    payload = plan.get("payload")
    github_distributions = github_manifest.get("distributions")
    if not isinstance(payload, dict) or not isinstance(github_distributions, dict):
        raise ValueError("missing publication payload records")
    if set(payload) != {"wheel", "sdist"}:
        raise ValueError("external publication payload must define wheel and sdist only")
    for family in ("wheel", "sdist"):
        record = payload[family]
        github_record = github_distributions.get(family)
        if record != github_record:
            raise ValueError(f"{family} payload does not match GitHub release manifest")
        if _SHA256.fullmatch(str(record.get("sha256", ""))) is None:
            raise ValueError(f"invalid {family} SHA-256")

    if destination == "pypi":
        pypi = plan.get("pypi")
        expected = {
            "authorized": True,
            "project": "gazeaudit",
            "authentication": "trusted-publishing-oidc",
            "workflow": ".github/workflows/publish-pypi.yml",
            "environment": "pypi",
            "project_url": "https://pypi.org/project/gazeaudit/",
            "version": expected_version,
            "status": "pending_external_configuration",
        }
        if pypi != expected:
            raise ValueError("PyPI publication plan mismatch")
    elif destination == "zenodo":
        zenodo = plan.get("zenodo")
        if not isinstance(zenodo, dict) or zenodo.get("authorized") is not True:
            raise ValueError("Zenodo publication is not authorized")
        if zenodo.get("mode") != "manual-existing-release-deposit":
            raise ValueError("unexpected Zenodo publication mode")
        if zenodo.get("resource_type") != "software":
            raise ValueError("Zenodo resource type must be software")
        if zenodo.get("metadata_source") != "CITATION.cff@v0.1.0":
            raise ValueError("unexpected Zenodo metadata source")
        sdist = payload["sdist"]
        if zenodo.get("single_file") != sdist["filename"]:
            raise ValueError("Zenodo single-file payload mismatch")
        if zenodo.get("single_file_sha256") != sdist["sha256"]:
            raise ValueError("Zenodo single-file checksum mismatch")
        if zenodo.get("version_doi") is not None or zenodo.get("concept_doi") is not None:
            raise ValueError("Zenodo DOI fields must remain empty before verification")
        if zenodo.get("status") != "pending_external_deposit":
            raise ValueError("unexpected Zenodo publication status")
    else:
        raise ValueError("destination must be pypi or zenodo")


def verify_payload(plan: dict[str, Any], destination: str, dist_dir: Path) -> None:
    payload = plan["payload"]
    if destination == "pypi":
        families = ("wheel", "sdist")
    elif destination == "zenodo":
        families = ("sdist",)
    else:
        raise ValueError("destination must be pypi or zenodo")

    expected_names = sorted(payload[family]["filename"] for family in families)
    actual_names = sorted(path.name for path in dist_dir.iterdir() if path.is_file())
    if actual_names != expected_names:
        raise ValueError(
            f"payload directory mismatch: expected {expected_names}, got {actual_names}"
        )
    for family in families:
        record = payload[family]
        path = dist_dir / record["filename"]
        if path.stat().st_size != record["size_bytes"]:
            raise ValueError(f"{family} size mismatch")
        if _sha256(path) != record["sha256"]:
            raise ValueError(f"{family} SHA-256 mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--github-manifest", type=Path, required=True)
    parser.add_argument("--destination", choices=("pypi", "zenodo"), required=True)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--expected-tag", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--dist-dir", type=Path)
    args = parser.parse_args()

    plan = _load(args.plan)
    github_manifest = _load(args.github_manifest)
    validate(
        plan,
        github_manifest,
        destination=args.destination,
        expected_version=args.expected_version,
        expected_tag=args.expected_tag,
        expected_commit=args.expected_commit,
    )
    if args.dist_dir is not None:
        verify_payload(plan, args.destination, args.dist_dir)
    print(
        "external publication gate: verified "
        f"{args.destination} for {args.expected_tag} at {args.expected_commit}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
