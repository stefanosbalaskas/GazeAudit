"""Command-line entry point for the frozen GazeBase real-data execution."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .gazebase_artifacts import write_gazebase_execution_artifacts
from .gazebase_execution import (
    prepare_gazebase_pymovements_dataset,
    run_gazebase_multidetector_execution,
)
from .provenance import canonical_json


def build_parser() -> argparse.ArgumentParser:
    """Build the deliberately narrow frozen-case-study command-line parser."""

    parser = argparse.ArgumentParser(
        prog="gazeaudit-gazebase-run",
        description=(
            "Execute the frozen GazeBase R1/S1 FXS-vs-TEX seven-detector protocol and "
            "write a checksummed publication artifact set."
        ),
    )
    parser.add_argument(
        "--dataset-root",
        required=True,
        type=Path,
        help="pymovements GazeBase dataset root directory",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="empty directory for immutable execution artifacts",
    )
    parser.add_argument(
        "--gazeaudit-commit",
        required=True,
        help="exact 40-character lowercase Git commit SHA for the executing GazeAudit code",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="download and extract the pymovements GazeBase resource before loading",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace existing files in output-dir; nested directories are never removed",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the frozen case study and serialize its auditable outputs."""

    args = build_parser().parse_args(argv)
    try:
        import pymovements as pm
    except ImportError as exc:
        raise SystemExit(
            "The real-data runner requires the frozen case-study dependencies. "
            "Install GazeAudit with the 'gazebase' extra."
        ) from exc

    dataset = pm.Dataset("GazeBase", path=args.dataset_root)
    if args.download:
        dataset.download()
    dataset.load(
        participants=False,
        events=False,
        stimuli=False,
        subset={
            "round_id": 1,
            "session_id": 1,
            "task_name": ["FXS", "TEX"],
        },
    )

    prepared = prepare_gazebase_pymovements_dataset(dataset)
    execution = run_gazebase_multidetector_execution(
        prepared,
        gazeaudit_commit=args.gazeaudit_commit,
    )
    artifact_manifest = write_gazebase_execution_artifacts(
        execution,
        args.output_dir,
        overwrite=args.overwrite,
    )

    result = {
        "classification": str(execution.audit.summary["classification"]),
        "completeness_passed": bool(execution.audit.summary["completeness_passed"]),
        "execution_fingerprint": execution.execution_fingerprint,
        "artifact_manifest_fingerprint": artifact_manifest["artifact_manifest_fingerprint"],
        "publication_scientific_fingerprint": artifact_manifest[
            "publication_scientific_fingerprint"
        ],
        "publication_bundle_fingerprint": artifact_manifest["publication_bundle_fingerprint"],
        "output_dir": str(args.output_dir),
    }
    sys.stdout.write(canonical_json(result) + "\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
