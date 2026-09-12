"""Controlled first-scientific-execution CLI for the Korthals protocol-v2 case study."""

from __future__ import annotations

import argparse
import platform
from importlib.metadata import version
from pathlib import Path

from .korthals_execution import KORTHALS_COMPANION_COMMIT
from .korthals_execution_archive_v2 import write_korthals_locked_execution_artifacts_v2
from .korthals_execution_v2 import (
    KORTHALS_V2_EXECUTION_WORKFLOW,
    run_korthals_locked_aoi_execution_v2,
)
from .korthals_freeze import KORTHALS_COMPANION_REPOSITORY
from .korthals_source_lock import (
    KORTHALS_SOURCE_LOCK_FINGERPRINT,
    verify_korthals_locked_prepared,
    verify_korthals_locked_source_manifest,
)
from .korthals_streaming import prepare_korthals_from_companion_v2_streaming
from .korthals_v2 import KORTHALS_V2_PROTOCOL_FINGERPRINT, build_korthals_source_manifest_v2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute the source-lock-bound Korthals protocol-v2 AOI audit without "
            "printing scientific results. Archive verification/reveal is separate."
        )
    )
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--environment-file", required=True)
    parser.add_argument("--execution-commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--runner-os", required=True)
    parser.add_argument("--runner-arch", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.data_root)

    # Hard byte-identity gate before companion preprocessing or scientific execution.
    source_manifest = build_korthals_source_manifest_v2(root)
    verify_korthals_locked_source_manifest(source_manifest)

    intake = prepare_korthals_from_companion_v2_streaming(root)
    verify_korthals_locked_source_manifest(intake.source_manifest)
    verify_korthals_locked_prepared(intake.prepared)

    # This is the first operation in this CLI that evaluates the scientific endpoint.
    execution = run_korthals_locked_aoi_execution_v2(intake.prepared)

    environment_text = Path(args.environment_file).read_text(encoding="utf-8")
    context = {
        "repository": "stefanosbalaskas/GazeAudit",
        "execution_commit": str(args.execution_commit),
        "workflow_ref": KORTHALS_V2_EXECUTION_WORKFLOW,
        "github_run_id": str(args.run_id),
        "companion_repository": KORTHALS_COMPANION_REPOSITORY,
        "companion_commit": KORTHALS_COMPANION_COMMIT,
        "protocol_fingerprint": KORTHALS_V2_PROTOCOL_FINGERPRINT,
        "source_lock_fingerprint": KORTHALS_SOURCE_LOCK_FINGERPRINT,
        "source_manifest_fingerprint": source_manifest["source_manifest_fingerprint"],
        "package_version": version("gazeaudit"),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "runner_os": str(args.runner_os),
        "runner_arch": str(args.runner_arch),
    }
    write_korthals_locked_execution_artifacts_v2(
        execution,
        Path(args.output_dir),
        execution_context=context,
        environment_text=environment_text,
    )
    # Deliberately no stdout: scientific values remain unrevealed until after upload.
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
