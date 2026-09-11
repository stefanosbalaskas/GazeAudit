"""Manual source-freeze CLI for the Korthals public-data case study."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from importlib.metadata import version
from pathlib import Path

from .korthals_execution import KORTHALS_COMPANION_COMMIT, KORTHALS_PROTOCOL_FINGERPRINT
from .korthals_freeze import (
    KORTHALS_COMPANION_REPOSITORY,
    KORTHALS_FREEZE_WORKFLOW,
    write_korthals_source_freeze_artifacts,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gazeaudit-korthals-source-freeze",
        description=(
            "Wrap an endpoint-blind Korthals source intake in an immutable execution "
            "and environment provenance envelope."
        ),
    )
    parser.add_argument("--intake-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--environment-file", required=True)
    parser.add_argument("--execution-commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--runner-os", default=os.environ.get("RUNNER_OS", "unknown"))
    parser.add_argument("--runner-arch", default=os.environ.get("RUNNER_ARCH", "unknown"))
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    intake_dir = Path(args.intake_dir)
    environment_text = Path(args.environment_file).read_text(encoding="utf-8")
    source_manifest = json.loads(
        (intake_dir / "source_manifest.json").read_text(encoding="utf-8")
    )
    if not isinstance(source_manifest, dict):
        raise ValueError("source_manifest.json must contain a JSON object")

    context = {
        "repository": "stefanosbalaskas/GazeAudit",
        "execution_commit": args.execution_commit,
        "workflow_ref": KORTHALS_FREEZE_WORKFLOW,
        "github_run_id": str(args.run_id),
        "companion_repository": KORTHALS_COMPANION_REPOSITORY,
        "companion_commit": KORTHALS_COMPANION_COMMIT,
        "protocol_fingerprint": KORTHALS_PROTOCOL_FINGERPRINT,
        "source_manifest_fingerprint": source_manifest["source_manifest_fingerprint"],
        "package_version": version("gazeaudit"),
        "python_version": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "runner_os": str(args.runner_os),
        "runner_arch": str(args.runner_arch),
    }
    manifest = write_korthals_source_freeze_artifacts(
        intake_dir,
        Path(args.output_dir),
        execution_context=context,
        environment_text=environment_text,
        overwrite=args.overwrite,
    )
    print(
        json.dumps(
            {
                "status": "source_freeze_archived",
                "source_manifest_fingerprint": manifest["source_manifest_fingerprint"],
                "freeze_manifest_fingerprint": manifest["freeze_manifest_fingerprint"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
