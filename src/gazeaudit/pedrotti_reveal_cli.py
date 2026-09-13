"""Reveal a Pedrotti scientific result only from its verified archive."""

from __future__ import annotations

import argparse

from .pedrotti_execution import reveal_pedrotti_locked_execution
from .provenance import canonical_json


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reveal an already archived and verified Pedrotti scientific result."
    )
    parser.add_argument("--archive-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = reveal_pedrotti_locked_execution(args.archive_dir)
    execution = result["execution_manifest"]
    summary = {
        "status": result["status"],
        "classification": execution["classification"],
        "execution_fingerprint": execution["execution_fingerprint"],
        "reference": result["reference"],
        "sampling_results": result["sampling_results"],
        "family_recovery": result["family_recovery"],
    }
    print(canonical_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
