"""CLI for revision reproducibility-package scaffolding and validation."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .provenance import canonical_json
from .revision_package import validate_revision_package, write_revision_package_skeleton


def build_parser() -> argparse.ArgumentParser:
    """Build the reproducibility-package command-line parser."""

    parser = argparse.ArgumentParser(
        prog="gazeaudit-revision-package",
        description=(
            "Scaffold or validate a reviewer-revision provenance package while keeping "
            "submitted and post-review evidence temporally separate."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init",
        help="create a bounded revision-package scaffold",
    )
    init_parser.add_argument("--output-dir", required=True, type=Path)
    init_parser.add_argument("--project-slug", required=True)
    init_parser.add_argument("--review-round", type=int, default=1)
    init_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace only known scaffold files; unrelated files are never deleted",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="validate structure and manifest integrity without judging scientific validity",
    )
    validate_parser.add_argument("--root", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the scaffold or structural validation command."""

    args = build_parser().parse_args(argv)
    if args.command == "init":
        manifest = write_revision_package_skeleton(
            args.output_dir,
            project_slug=args.project_slug,
            review_round=args.review_round,
            overwrite=args.overwrite,
        )
        result = {
            "action": "init",
            "output_dir": str(args.output_dir),
            "schema": manifest["schema"],
            "manifest_fingerprint": manifest["manifest_fingerprint"],
            "required_file_count": len(manifest["required_paths"]),
        }
        sys.stdout.write(canonical_json(result) + "\n")
        return 0

    result = validate_revision_package(args.root)
    sys.stdout.write(canonical_json(result) + "\n")
    return 0 if result["valid"] else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
