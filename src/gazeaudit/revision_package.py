"""Scaffold and validate reviewer-revision reproducibility packages."""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .provenance import canonical_json, fingerprint, software_environment

REVISION_PACKAGE_SCHEMA = "gazeaudit-revision-package-v1"
REVISION_PACKAGE_VALIDATION_SCHEMA = "gazeaudit-revision-package-validation-v1"

REVISION_CHANGE_CATEGORIES = (
    "documentation_clarification",
    "correction",
    "sensitivity_amendment",
    "analytical_amendment",
    "endpoint_amendment",
    "measurement_amendment",
)

_RESPONSE_MATRIX_FIELDS = (
    "reviewer_item",
    "category",
    "results_already_seen",
    "action",
    "submitted_denominator",
    "post_review_denominator",
    "manuscript_location",
    "archive_location",
    "status",
)

_CHANGE_MANIFEST_FIELDS = (
    "change_id",
    "category",
    "results_already_seen",
    "submitted_location",
    "revised_location",
    "evidence_added_or_regenerated",
    "denominator_effect",
    "claim_impact",
    "status",
)

_EVIDENCE_MAP_FIELDS = (
    "claim_id",
    "claim_component",
    "temporal_status",
    "supporting_evidence",
    "manuscript_location",
    "verification_status",
)


def build_revision_package_manifest(
    project_slug: str,
    *,
    review_round: int = 1,
) -> dict[str, Any]:
    """Return the deterministic structural manifest for a revision package."""

    slug = str(project_slug).strip()
    if not slug:
        raise ValueError("project_slug must not be empty")
    if review_round < 1:
        raise ValueError("review_round must be at least 1")

    required_paths = _required_paths(review_round)
    manifest: dict[str, Any] = {
        "schema": REVISION_PACKAGE_SCHEMA,
        "project_slug": slug,
        "review_round": int(review_round),
        "required_paths": required_paths,
        "change_categories": list(REVISION_CHANGE_CATEGORIES),
        "temporal_safeguards": {
            "submitted_record_immutable": True,
            "post_review_work_separate": True,
            "endpoint_amendments_separate_from_original_denominator": True,
            "failed_valid_branches_remain_visible": True,
            "corrections_preserve_superseded_record": True,
        },
    }
    manifest["manifest_fingerprint"] = fingerprint(manifest)
    return manifest


def write_revision_package_skeleton(
    output_dir: str | Path,
    *,
    project_slug: str,
    review_round: int = 1,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Create a bounded revision-package skeleton without deleting user files."""

    root = Path(output_dir)
    manifest = build_revision_package_manifest(project_slug, review_round=review_round)
    targets = [root / relative_path for relative_path in manifest["required_paths"]]

    existing = [path for path in targets if path.exists()]
    if existing and not overwrite:
        formatted = ", ".join(str(path.relative_to(root)) for path in existing)
        raise FileExistsError(f"revision package files already exist: {formatted}")

    for path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)

    _write_text(
        root / "README.md",
        _root_readme(project_slug=project_slug, review_round=review_round),
    )
    _write_text(root / "submission/README.md", _submission_readme())
    _write_csv(
        root / f"revision/round-{review_round}/reviewer-response/response-matrix.csv",
        _RESPONSE_MATRIX_FIELDS,
    )
    _write_csv(
        root / f"revision/round-{review_round}/change-manifest/version-change-manifest.csv",
        _CHANGE_MANIFEST_FIELDS,
    )
    _write_text(
        root / f"revision/round-{review_round}/amendments/README.md",
        _amendment_readme(kind="analysis"),
    )
    _write_text(
        root / f"revision/round-{review_round}/endpoint-amendments/README.md",
        _amendment_readme(kind="endpoint"),
    )
    _write_csv(root / "final/editor-facing-evidence-map.csv", _EVIDENCE_MAP_FIELDS)
    _write_text(
        root / "final/software-identity/environment.json",
        canonical_json(software_environment()) + "\n",
    )
    _write_text(root / "package-manifest.json", canonical_json(manifest) + "\n")
    return manifest


def validate_revision_package(root: str | Path) -> dict[str, Any]:
    """Validate revision-package structure and manifest integrity only.

    This validator does not assess scientific validity, manuscript quality,
    completeness of an analytical specification space, or acceptance readiness.
    """

    package_root = Path(root)
    manifest_path = package_root / "package-manifest.json"
    problems: list[str] = []
    missing_paths: list[str] = []

    manifest: dict[str, Any] | None = None
    manifest_fingerprint_valid = False
    review_round: int | None = None

    if not manifest_path.is_file():
        problems.append("missing package-manifest.json")
    else:
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            problems.append(f"unreadable package manifest: {exc}")
        else:
            if not isinstance(loaded, Mapping):
                problems.append("package manifest must be a JSON object")
            else:
                manifest = dict(loaded)
                if manifest.get("schema") != REVISION_PACKAGE_SCHEMA:
                    problems.append("unexpected package manifest schema")
                round_value = manifest.get("review_round")
                if (
                    isinstance(round_value, int)
                    and not isinstance(round_value, bool)
                    and round_value >= 1
                ):
                    review_round = round_value
                else:
                    problems.append("review_round must be an integer >= 1")

                expected_fingerprint = manifest.get("manifest_fingerprint")
                unsigned_manifest = dict(manifest)
                unsigned_manifest.pop("manifest_fingerprint", None)
                manifest_fingerprint_valid = (
                    isinstance(expected_fingerprint, str)
                    and expected_fingerprint == fingerprint(unsigned_manifest)
                )
                if not manifest_fingerprint_valid:
                    problems.append("package manifest fingerprint mismatch")

    if review_round is not None:
        for relative_path in _required_paths(review_round):
            if not (package_root / relative_path).is_file():
                missing_paths.append(relative_path)
        if missing_paths:
            problems.append("required package files are missing")

    return {
        "schema": REVISION_PACKAGE_VALIDATION_SCHEMA,
        "valid": not problems,
        "root": str(package_root),
        "review_round": review_round,
        "manifest_fingerprint_valid": manifest_fingerprint_valid,
        "missing_paths": missing_paths,
        "problems": problems,
        "scope": "structural_provenance_only",
    }


def _required_paths(review_round: int) -> list[str]:
    round_root = f"revision/round-{review_round}"
    return [
        "README.md",
        "submission/README.md",
        f"{round_root}/reviewer-response/response-matrix.csv",
        f"{round_root}/change-manifest/version-change-manifest.csv",
        f"{round_root}/amendments/README.md",
        f"{round_root}/endpoint-amendments/README.md",
        "final/editor-facing-evidence-map.csv",
        "final/software-identity/environment.json",
        "package-manifest.json",
    ]


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_csv(path: Path, fields: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(fields)


def _root_readme(*, project_slug: str, review_round: int) -> str:
    return f"""# Revision reproducibility package: {project_slug}

This directory is a structural provenance scaffold for review round {review_round}.

Keep submitted evidence, post-review amendments, corrections, endpoint changes, and
the final editor-facing evidence map as separate temporal layers. Do not relabel
reviewer-requested work as pre-specified and do not merge new endpoints into the
original endpoint denominator.

The scaffold does not certify scientific validity, analytical completeness, or
publication acceptance.
"""


def _submission_readme() -> str:
    return """# Submitted record

Place the immutable submitted manuscript record and the evidence that existed at
submission under this directory. Do not overwrite it with revision-stage outputs.
"""


def _amendment_readme(*, kind: str) -> str:
    if kind == "endpoint":
        detail = (
            "Store reviewer-requested endpoint analyses here. Keep them endpoint-specific "
            "and outside the original endpoint denominator unless the original declaration "
            "explicitly included them."
        )
    else:
        detail = (
            "Store reviewer-requested sensitivity or analytical amendments here. Preserve "
            "valid technical failures and record that outcomes had already been seen when "
            "that is true."
        )
    return f"""# Post-review {kind} amendments

{detail}

Corrections are not ordinary amendments: preserve the superseded record and the
reason for supersession.
"""
