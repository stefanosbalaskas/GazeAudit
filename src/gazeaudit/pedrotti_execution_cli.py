"""CLI for hidden Pedrotti scientific execution and archival."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pedrotti_execution import (
    execution_context,
    prepare_pedrotti_locked_execution_data,
    run_pedrotti_locked_scientific_execution,
    write_pedrotti_locked_execution_artifacts,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute the frozen Pedrotti protocol and write its verified archive "
            "without revealing scientific outcomes."
        )
    )
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--environment-file", required=True)
    parser.add_argument("--execution-commit", required=True)
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--runner-os", required=True)
    parser.add_argument("--runner-arch", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    environment_text = Path(args.environment_file).read_text(encoding="utf-8")
    prepared = prepare_pedrotti_locked_execution_data(args.source_dir)
    execution = run_pedrotti_locked_scientific_execution(prepared)
    context = execution_context(
        execution_commit=args.execution_commit,
        github_run_id=args.run_id,
        runner_os=args.runner_os,
        runner_arch=args.runner_arch,
    )
    write_pedrotti_locked_execution_artifacts(
        execution,
        args.output_dir,
        execution_context=context,
        environment_text=environment_text,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
