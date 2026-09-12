"""Post-archive reveal CLI for a verified Korthals protocol-v2 scientific execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .korthals_execution_archive_v2 import reveal_korthals_locked_execution_v2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reveal a Korthals protocol-v2 result only from an intact locked archive."
    )
    parser.add_argument("--artifact-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = reveal_korthals_locked_execution_v2(Path(args.artifact_dir))
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
