"""Command-line entry point for endpoint-blind Korthals protocol-v2 source intake."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .korthals_streaming import prepare_korthals_from_companion_v2_streaming
from .korthals_v2 import write_korthals_source_intake_artifacts_v2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gazeaudit-korthals-source-intake-v2",
        description=(
            "Run Korthals protocol-v2 public-source preprocessing and archive source "
            "identity/readiness without evaluating the scientific AOI endpoint."
        ),
    )
    parser.add_argument(
        "--data-root",
        default="data",
        help="Published OSF source root containing data/raw and data/clean (default: data).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Empty output directory for the checksummed source-intake artifact.",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    intake = prepare_korthals_from_companion_v2_streaming(Path(args.data_root))
    manifest = write_korthals_source_intake_artifacts_v2(
        intake,
        Path(args.output_dir),
        overwrite=args.overwrite,
    )
    print(
        json.dumps(
            {
                "status": "source_intake_v2_archived",
                "artifact_manifest_fingerprint": manifest["artifact_manifest_fingerprint"],
                "source_manifest_fingerprint": manifest["source_manifest_fingerprint"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
