from __future__ import annotations

import inspect
import json
import subprocess
import sys
from pathlib import Path

import gazeaudit

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "assets" / "api-symbol-reference.json"
GENERATOR = ROOT / "tools" / "generate_api_symbol_reference.py"
PAGE = ROOT / "docs" / "reference" / "api-pathways.md"
SCRIPT = ROOT / "assets" / "js" / "api-symbol-reference.js"
SEARCH = ROOT / "assets" / "js" / "search-tools.js"
LAYOUT = ROOT / "_layouts" / "default.html"
GUIDE = ROOT / "docs" / "guides" / "read-api-reference.md"
EXAMPLE = ROOT / "docs" / "examples" / "source-api-inspection.md"
CALL_CONTRACT_EXAMPLE = ROOT / "docs" / "examples" / "api-call-contracts.md"
DOCS_INDEX = ROOT / "docs" / "index.md"
GUIDES_INDEX = ROOT / "docs" / "guides" / "index.md"
EXAMPLES_INDEX = ROOT / "docs" / "examples" / "index.md"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _metadata() -> dict[str, object]:
    return json.loads(_text(REFERENCE))


def test_checked_api_symbol_metadata_matches_installed_package() -> None:
    subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        cwd=ROOT,
        check=True,
    )


def test_api_symbol_metadata_has_36_unique_governed_symbols() -> None:
    metadata = _metadata()
    symbols = metadata["symbols"]

    assert metadata["schema"] == "gazeaudit-api-symbol-reference-v2"
    assert metadata["symbol_count"] == 36
    assert isinstance(symbols, list)
    assert len(symbols) == 36

    names = [symbol["name"] for symbol in symbols]
    anchors = [symbol["anchor"] for symbol in symbols]
    assert len(names) == len(set(names))
    assert len(anchors) == len(set(anchors))


def _annotation_text(value: object) -> str | None:
    if value is inspect.Signature.empty:
        return None
    if isinstance(value, str):
        return value
    return inspect.formatannotation(value).replace("gazeaudit.", "")


def _minimal_call(name: str, signature: inspect.Signature) -> str:
    arguments: list[str] = []
    for parameter in signature.parameters.values():
        required = (
            parameter.default is inspect.Signature.empty
            and parameter.kind
            not in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}
        )
        if not required:
            continue
        if parameter.kind in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        }:
            arguments.append(parameter.name)
        elif parameter.kind is inspect.Parameter.KEYWORD_ONLY:
            arguments.append(f"{parameter.name}={parameter.name}")
    return f"{name}({', '.join(arguments)})"


def test_api_symbol_metadata_matches_live_signatures_and_source_files() -> None:
    for symbol in _metadata()["symbols"]:
        obj = getattr(gazeaudit, symbol["name"])
        signature = inspect.signature(obj)
        expected_signature = str(signature).replace("gazeaudit.", "")

        assert symbol["signature"] == expected_signature
        assert symbol["kind"] in {"class", "function"}
        assert symbol["summary"]
        assert symbol["module"] == obj.__module__
        assert symbol["source_path"].startswith("src/gazeaudit/")
        assert (ROOT / symbol["source_path"]).is_file()
        assert isinstance(symbol["source_line"], int) and symbol["source_line"] > 0
        assert symbol["import_statement"] == f"from gazeaudit import {symbol['name']}"
        assert symbol["method_ids"]
        assert symbol["return_annotation"] == _annotation_text(signature.return_annotation)
        assert symbol["minimal_call"] == _minimal_call(symbol["name"], signature)

        parameters = symbol["parameters"]
        assert len(parameters) == len(signature.parameters)
        for generated, live in zip(parameters, signature.parameters.values(), strict=True):
            assert generated["name"] == live.name
            assert generated["kind"] == live.kind.name.lower()
            assert generated["annotation"] == _annotation_text(live.annotation)
            expected_default = (
                None if live.default is inspect.Signature.empty else repr(live.default)
            )
            assert generated["default"] == expected_default
            assert generated["required"] is (
                live.default is inspect.Signature.empty
                and live.kind
                not in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}
            )


def test_generated_minimal_calls_cover_distinct_signature_shapes() -> None:
    symbols = {symbol["name"]: symbol for symbol in _metadata()["symbols"]}

    assert symbols["GazeStudy"]["minimal_call"] == "GazeStudy(data)"
    assert symbols["run_specs"]["minimal_call"] == "run_specs(study, space, endpoint)"
    assert (
        symbols["make_peyes_detector"]["minimal_call"]
        == "make_peyes_detector(algorithm, min_event_duration=min_event_duration)"
    )
    assert (
        symbols["simulate_known_aoi_effect"]["minimal_call"]
        == "simulate_known_aoi_effect()"
    )


def test_api_pathway_page_exposes_revision_pinned_metadata_hooks() -> None:
    page = _text(PAGE)

    assert "data-api-pathways" in page
    assert "data-api-symbol-reference=" in page
    assert "site.github.build_revision | default: 'main'" in page
    assert "data-api-source-base=" in page
    assert "Source-level details" in page
    assert "signature/source change cannot silently leave the checked reference stale" in page


def test_api_symbol_enhancement_escapes_metadata_and_uses_native_buttons() -> None:
    script = _text(SCRIPT)

    for contract in (
        "gazeaudit-api-symbol-reference-v2",
        "data-api-symbol-detail",
        "api-symbol-signature",
        "api-symbol-source",
        "api-symbol-summary",
        "api-symbol-pathway-links",
        "data-copy-api-import",
        "data-copy-api-call",
        "api-symbol-contract",
        "api-symbol-parameter-table",
        "parameter.required",
        "symbol.return_annotation",
        "symbol.minimal_call",
        "navigator.clipboard",
        "escapeHtml(symbol.signature)",
        "escapeHtml(symbol.summary",
        "escapeHtml(symbol.source_path)",
        "escapeHtml(symbol.minimal_call)",
        "escapeHtml(symbol.import_statement)",
    ):
        assert contract in script

    assert 'document.createElement("button")' not in script
    assert '<details class="api-symbol-contract">' in script
    assert '<button type="button" data-copy-api-call>' in script
    assert '<button type="button" data-copy-api-import>' in script


def test_layout_loads_api_metadata_globally_and_enhancement_only_on_pathways() -> None:
    layout = _text(LAYOUT)

    assert "data-api-symbol-reference=" in layout
    assert "/assets/api-symbol-reference.json" in layout
    assert "page.page_type == 'api-pathways'" in layout
    assert "/assets/js/api-symbol-reference.js" in layout


def test_search_adds_symbols_only_for_nonempty_queries() -> None:
    script = _text(SEARCH)

    for contract in (
        "let apiSymbolItems = []",
        "let apiSymbolsLoaded = false",
        "const loadApiSymbols = async () =>",
        "body.dataset.apiSymbolReference",
        "category: 'API symbol'",
        "kind: 'Reference'",
        "/docs/reference/api-pathways/#",
        "? [...(index || []), ...apiSymbolItems]",
        ": (index || [])",
    ):
        assert contract in script

    assert "['API', 'run_specs']" in script
    assert "symbol.minimal_call" in script
    assert "symbol.return_annotation" in script
    assert "symbol.parameters" in script
    assert "parameter.required ? 'required' : 'optional'" in script


def test_source_api_guide_and_example_preserve_scientific_boundaries() -> None:
    guide = _text(GUIDE)
    example = _text(EXAMPLE)

    assert "A Python signature can tell you what arguments a callable accepts" in guide
    assert "It cannot tell you whether a threshold" in guide
    assert "Copy the import, not a fabricated analysis" in guide
    assert "fully synthetic documentation exercise" in example
    assert "That is an inspection snippet, not a scientific analysis" in example
    assert "None of those alone establishes" in example

    contract_example = _text(CALL_CONTRACT_EXAMPLE)
    assert "fully synthetic interface-reading exercise" in contract_example
    assert "A minimal call shape is not a completed analysis" in contract_example
    assert "run_specs(study, space, endpoint)" in contract_example
    assert "min_event_duration=min_event_duration" in contract_example
    assert "simulate_known_aoi_effect()" in contract_example
    assert "software default scientifically justified" in contract_example


def test_source_api_routes_are_discoverable_and_required_in_generated_site() -> None:
    docs = _text(DOCS_INDEX)
    guides = _text(GUIDES_INDEX)
    examples = _text(EXAMPLES_INDEX)
    check = _text(SITE_CHECK)

    assert "[Source-level API guide](guides/read-api-reference/)" in docs
    assert "[Source-level API inspection](examples/source-api-inspection/)" in docs
    assert 'href="read-api-reference/">Source-level API guide →</a>' in guides
    assert 'href="source-api-inspection/">Source API inspection →</a>' in examples

    for path in (
        "docs/guides/read-api-reference/index.html",
        "docs/examples/source-api-inspection/index.html",
        "docs/examples/api-call-contracts/index.html",
        "assets/js/api-symbol-reference.js",
        "assets/api-symbol-reference.json",
    ):
        assert f'"{path}"' in check
