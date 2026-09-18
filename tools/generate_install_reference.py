from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover - generator runs on Python 3.12 in CI
    raise SystemExit("Python 3.11+ is required to generate install metadata") from exc

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
TEST_WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
OUTPUT = ROOT / "_data" / "install_reference.json"
SCHEMA = "gazeaudit-install-reference-v1"


def _tested_python_versions(path: Path = TEST_WORKFLOW) -> list[str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r'python-version:\s*\[(?P<versions>[^\]]+)\]',
        text,
    )
    if match is None:
        raise ValueError("tests workflow Python matrix was not found")
    versions = re.findall(r'"([0-9]+\.[0-9]+)"', match.group("versions"))
    if not versions:
        raise ValueError("tests workflow Python matrix is empty")
    return versions


def build_reference() -> dict[str, object]:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    optional = project.get("optional-dependencies", {})
    scripts = project.get("scripts", {})

    return {
        "schema": SCHEMA,
        "name": project["name"],
        "version": project["version"],
        "requires_python": project["requires-python"],
        "tested_python_versions": _tested_python_versions(),
        "dependencies": list(project.get("dependencies", [])),
        "extras": {name: list(values) for name, values in optional.items()},
        "scripts": dict(scripts),
        "urls": dict(project.get("urls", {})),
    }


def _serialise(reference: dict[str, object]) -> str:
    return json.dumps(reference, indent=2, ensure_ascii=False) + "\n"


def write_reference(path: Path = OUTPUT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_serialise(build_reference()), encoding="utf-8")


def check_reference(path: Path = OUTPUT) -> None:
    expected = _serialise(build_reference())
    try:
        current = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"install reference is missing: {path}") from exc
    if current != expected:
        raise SystemExit(
            "install reference is stale. Run: "
            "python tools/generate_install_reference.py"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate installation metadata from pyproject.toml and CI."
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    if args.check:
        check_reference(args.output)
    else:
        write_reference(args.output)
        print(f"INSTALL REFERENCE: WROTE {args.output}")


if __name__ == "__main__":
    main()
