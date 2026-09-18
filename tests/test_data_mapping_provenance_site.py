import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENTER = ROOT / "docs" / "data-contract.md"
GUIDE = ROOT / "docs" / "guides" / "data-mapping-provenance.md"
EXAMPLE = ROOT / "docs" / "examples" / "data-mapping-change-audit.md"
SCHEMA = ROOT / "assets" / "data-mapping-record.schema.json"
JS = ROOT / "assets" / "js" / "data-contract.js"
CSS = ROOT / "assets" / "css" / "data-contract.css"
LAYOUT = ROOT / "_layouts" / "default.html"
DOCS = ROOT / "docs" / "index.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
EXAMPLES = ROOT / "docs" / "examples" / "index.md"
REFERENCE = ROOT / "docs" / "reference" / "index.md"
COMPASS = ROOT / "docs" / "documentation-map.md"
README = ROOT / "README.md"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_mapping_record_schema_is_strict_and_versioned() -> None:
    payload = json.loads(_text(SCHEMA))

    assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert payload["title"] == "GazeAudit data mapping record"
    assert payload["type"] == "object"
    assert payload["additionalProperties"] is False

    required = {
        "schema",
        "source_id",
        "columns",
        "units",
        "coordinate_convention",
        "pre_mapping_transformations",
    }
    assert set(payload["required"]) == required
    assert payload["properties"]["schema"]["const"] == "gazeaudit-data-mapping-record-v1"

    columns = payload["properties"]["columns"]
    assert set(columns["required"]) == {"participant", "trial", "timestamp", "x", "y"}
    assert columns["additionalProperties"] is False
    for key in ("participant", "trial", "timestamp", "x", "y"):
        assert columns["properties"][key] == {"type": "string", "minLength": 1}

    units = payload["properties"]["units"]
    assert set(units["required"]) == {"coordinates", "timestamp"}
    assert units["additionalProperties"] is False

    assert "does not certify scientific validity" in payload["description"]


def test_browser_record_shape_matches_checked_schema_contract() -> None:
    text = _text(JS)

    for contract in (
        "gazeaudit-data-mapping-record-v1",
        "source_id: mapping.sourceId",
        "participant: mapping.participant",
        "trial: mapping.trial",
        "timestamp: mapping.timestamp",
        "x: mapping.x",
        "y: mapping.y",
        "coordinates: mapping.coordinateUnit",
        "timestamp: mapping.timestampUnit",
        "coordinate_convention: mapping.coordinateConvention",
        "pre_mapping_transformations: mapping.transformations",
        "JSON.stringify(",
        "recordCopy.disabled = true",
        "recordCopy.disabled = false",
        "Optional provenance fields remain descriptive and are never inferred.",
    ):
        assert contract in text

    assert "fetch(" not in text
    assert "FileReader" not in text


def test_data_contract_center_exposes_optional_provenance_without_guessing() -> None:
    text = _text(CENTER)

    for control in (
        'for="schema-source-id"',
        'for="schema-coordinate-unit"',
        'for="schema-coordinate-convention"',
        'for="schema-timestamp-unit"',
        'for="schema-transformations"',
        "data-schema-record-copy",
        "data-schema-record",
    ):
        assert control in text

    assert "optional" in text.lower()
    assert "the mapper never guesses" in text.lower()
    assert "does not hash or inspect your data" in text
    assert "data-mapping record JSON Schema" in text
    assert "/assets/data-mapping-record.schema.json" in text


def test_provenance_guide_separates_mapping_from_scientific_decisions() -> None:
    text = _text(GUIDE)

    for heading in (
        "Record the source identity you actually control",
        "Bind semantic roles to source columns",
        "Record units independently of column names",
        "Record coordinate convention",
        "Record transformations before canonical mapping",
        "Classify mapping changes",
        "Keep mapping provenance separate from QC decisions",
        "Treat missing provenance as missing, not as a guess",
        "Review changes before rerunning downstream work",
    ):
        assert heading in text

    assert "Do not fabricate a checksum" in text
    assert "Unknown provenance is a limitation to resolve or report." in text
    assert "A complete provenance record improves reconstruction. It does **not** establish" in text
    assert "/assets/data-mapping-record.schema.json" in text


def test_mapping_change_example_is_synthetic_and_preserves_history() -> None:
    text = _text(EXAMPLE)

    assert "fully synthetic provenance exercise" in text
    for change in (
        "Change A — source column renamed, semantics unchanged",
        "Change B — corrected source export",
        "Change C — timestamp unit conversion",
        "Change D — coordinate conversion",
        "Change E — trial identifier redefined",
        "Change F — rows excluded after QC",
    ):
        assert change in text

    for contract in (
        "mapping record itself does not compare data values",
        "Mapping provenance and scientific decision provenance are complementary.",
        (
            "It cannot decide whether a change is harmless, required, scientifically "
            "material, or outcome-informed."
        ),
        "do not rewrite the old record",
    ):
        assert contract in text

    exclusion_row = (
        "| scientific exclusion | yes | yes | "
        "full affected scientific record + decision provenance |"
    )
    assert exclusion_row in text


def test_mapping_provenance_controls_are_accessible_and_responsive() -> None:
    text = _text(CSS)

    for contract in (
        ".schema-mapper-grid textarea",
        ".schema-mapper-wide",
        ".schema-mapper-record-note",
        ":focus-visible",
        "@media (max-width: 720px)",
        "@media (forced-colors: active)",
    ):
        assert contract in text


def test_mapping_provenance_routes_are_discoverable() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    readme = _text(README)

    assert "/docs/guides/data-mapping-provenance/" in layout
    assert "/docs/examples/data-mapping-change-audit/" in layout
    assert "[Data mapping provenance](guides/data-mapping-provenance/)" in docs
    assert "[Mapping change audit](examples/data-mapping-change-audit/)" in docs
    assert 'href="data-mapping-provenance/">Data mapping provenance →</a>' in guides
    assert 'href="data-mapping-change-audit/">Mapping change audit →</a>' in examples
    assert "/assets/data-mapping-record.schema.json" in reference
    assert "/docs/guides/data-mapping-provenance/" in compass
    assert "/docs/guides/data-mapping-provenance/" in readme


def test_generated_site_requires_mapping_provenance_assets() -> None:
    text = _text(SITE_CHECK)

    for path in (
        "docs/guides/data-mapping-provenance/index.html",
        "docs/examples/data-mapping-change-audit/index.html",
        "assets/data-mapping-record.schema.json",
    ):
        assert f'"{path}"' in text
