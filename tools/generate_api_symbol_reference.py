from __future__ import annotations

import argparse
import inspect
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
CATALOG = ROOT / "_data" / "methods.yml"
OUTPUT = ROOT / "assets" / "api-symbol-reference.json"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import gazeaudit  # noqa: E402

SCHEMA = "gazeaudit-api-symbol-reference-v1"


def _catalog_symbols(path: Path = CATALOG) -> list[tuple[str, str]]:
    symbols: list[tuple[str, str]] = []
    method_id = ""
    in_functions = False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("- id: "):
            method_id = raw_line.removeprefix("- id: ").strip()
            in_functions = False
            continue
        if raw_line == "  functions:":
            if not method_id:
                raise ValueError("functions block appears before method id")
            in_functions = True
            continue
        if in_functions and raw_line.startswith("    - "):
            symbols.append((raw_line.removeprefix("    - ").strip(), method_id))
            continue
        if in_functions and raw_line.startswith("  ") and not raw_line.startswith("    "):
            in_functions = False

    if not symbols:
        raise ValueError("method catalog contains no governed public symbols")
    return symbols


def _annotation_text(value: Any) -> str | None:
    if value is inspect.Signature.empty:
        return None
    if isinstance(value, str):
        return value
    text = inspect.formatannotation(value)
    return text.replace("gazeaudit.", "")


def _default_text(value: Any) -> str | None:
    if value is inspect.Signature.empty:
        return None
    text = repr(value)
    if " at 0x" in text:
        raise ValueError(f"non-deterministic default repr: {text}")
    return text


def _signature_metadata(obj: Any) -> tuple[str, list[dict[str, Any]], str | None]:
    signature = inspect.signature(obj)
    parameters = []
    for parameter in signature.parameters.values():
        parameters.append(
            {
                "name": parameter.name,
                "kind": parameter.kind.name.lower(),
                "annotation": _annotation_text(parameter.annotation),
                "default": _default_text(parameter.default),
            }
        )
    return (
        str(signature).replace("gazeaudit.", ""),
        parameters,
        _annotation_text(signature.return_annotation),
    )


def _source_metadata(obj: Any) -> tuple[str, int]:
    source_file = inspect.getsourcefile(obj)
    if source_file is None:
        raise ValueError(f"cannot locate source file for {obj!r}")
    source_path = Path(source_file).resolve()
    try:
        relative = source_path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"source is outside repository: {source_path}") from exc
    _, line = inspect.getsourcelines(obj)
    return relative.as_posix(), int(line)


def build_reference() -> dict[str, Any]:
    method_map: dict[str, list[str]] = {}
    order: list[str] = []
    for symbol, method_id in _catalog_symbols():
        if symbol not in method_map:
            order.append(symbol)
            method_map[symbol] = []
        method_map[symbol].append(method_id)

    symbols: list[dict[str, Any]] = []
    for name in order:
        obj = getattr(gazeaudit, name, None)
        if obj is None:
            raise ValueError(f"governed symbol is not exported by gazeaudit: {name}")

        signature, parameters, returns = _signature_metadata(obj)
        source_path, source_line = _source_metadata(obj)
        doc = inspect.getdoc(obj) or ""
        summary = doc.splitlines()[0].strip() if doc else ""

        symbols.append(
            {
                "name": name,
                "kind": "class" if inspect.isclass(obj) else "function",
                "signature": signature,
                "parameters": parameters,
                "returns": returns,
                "module": obj.__module__,
                "source_path": source_path,
                "source_line": source_line,
                "summary": summary,
                "method_ids": method_map[name],
                "anchor": f"api-{name.lower().replace('_', '-')}",
                "import_statement": f"from gazeaudit import {name}",
            }
        )

    return {
        "schema": SCHEMA,
        "package_version": gazeaudit.__version__,
        "symbol_count": len(symbols),
        "symbols": symbols,
    }


def _serialise(reference: dict[str, Any]) -> str:
    return json.dumps(reference, separators=(",", ":"), sort_keys=False, ensure_ascii=False) + "\n"


def write_reference(path: Path = OUTPUT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_serialise(build_reference()), encoding="utf-8")


def check_reference(path: Path = OUTPUT) -> None:
    expected = _serialise(build_reference())
    try:
        current = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"API symbol reference is missing: {path}") from exc
    if current != expected:
        raise SystemExit(
            "API symbol reference is stale. Run: "
            "python tools/generate_api_symbol_reference.py"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate deterministic source-level API metadata for governed public symbols."
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    if args.check:
        check_reference(args.output)
    else:
        write_reference(args.output)
        print(f"API SYMBOL REFERENCE: WROTE {args.output}")


if __name__ == "__main__":
    main()
