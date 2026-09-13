"""Endpoint-blind source-intake CLI for the Pedrotti/de Chambrier case study."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pedrotti_source import inspect_pedrotti_source, write_pedrotti_source_intake_artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gazeaudit-pedrotti-source-intake",
        description=(
            "Verify the frozen Zenodo v1 bytes and archive endpoint-blind Pedrotti "
            "source compatibility facts without evaluating gaze-path effects."
        ),
    )
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    intake = inspect_pedrotti_source(Path(args.source_dir))
    manifest = write_pedrotti_source_intake_artifacts(
        intake,
        Path(args.output_dir),
        overwrite=args.overwrite,
    )
    print(
        json.dumps(
            {
                "status": "source_intake_archived",
                "source_manifest_fingerprint": intake.source_manifest[
                    "source_manifest_fingerprint"
                ],
                "artifact_manifest_fingerprint": manifest["artifact_manifest_fingerprint"],
                "participant_count": intake.intake_summary["participant_count"],
                "scientific_endpoint_evaluated": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
