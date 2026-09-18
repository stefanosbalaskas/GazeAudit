from pathlib import Path

import pandas as pd
import pytest

from gazeaudit import GazeStudy, audit_study_qc

ROOT = Path(__file__).resolve().parents[1]
CENTER = ROOT / "docs" / "data-contract.md"
GUIDE = ROOT / "docs" / "guides" / "map-your-table.md"
EXAMPLE = ROOT / "docs" / "examples" / "data-contract-valid-invalid.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "data-contract.css"
JS = ROOT / "assets" / "js" / "data-contract.js"
SVG = ROOT / "assets" / "images" / "data-contract-flow.svg"
DOCS = ROOT / "docs" / "index.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
EXAMPLES = ROOT / "docs" / "examples" / "index.md"
COMPASS = ROOT / "docs" / "documentation-map.md"
README = ROOT / "README.md"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _base() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "participant_id": ["P01", "P01", "P02", "P02"],
            "trial_id": ["T01", "T01", "T01", "T01"],
            "time_ms": [0.0, 16.7, 0.0, 16.7],
            "gaze_x_px": [500.0, 504.0, 610.0, 614.0],
            "gaze_y_px": [400.0, 402.0, 390.0, 394.0],
        }
    )


def _study(frame: pd.DataFrame) -> GazeStudy:
    return GazeStudy(
        frame,
        x="gaze_x_px",
        y="gaze_y_px",
        timestamp="time_ms",
        participant="participant_id",
        trial="trial_id",
    )


def test_documented_constructor_contract_matches_live_runtime() -> None:
    study = _study(_base())
    assert study.n_participants == 2
    assert study.n_trials == 2
    assert audit_study_qc(study).status == "pass"

    with pytest.raises(ValueError, match="missing required columns"):
        _study(_base().drop(columns=["gaze_y_px"]))

    nonnumeric = _base()
    nonnumeric["gaze_x_px"] = ["left", "left", "right", "right"]
    with pytest.raises(TypeError, match="must be numeric"):
        _study(nonnumeric)

    with pytest.raises(ValueError, match="at least one observation"):
        _study(_base().iloc[0:0].copy())


def test_documented_review_conditions_construct_then_surface_in_preflight() -> None:
    missing_x = _base()
    missing_x.loc[1, "gaze_x_px"] = float("nan")
    report = audit_study_qc(_study(missing_x))
    assert report.status == "review"
    assert "coordinate_nonfinite" in report.issue_codes

    missing_id = _base()
    missing_id.loc[2, "participant_id"] = None
    report = audit_study_qc(_study(missing_id))
    assert "identifier_missing" in report.issue_codes

    duplicate = _base()
    duplicate.loc[1, "time_ms"] = 0.0
    report = audit_study_qc(_study(duplicate))
    assert "timestamp_duplicate" in report.issue_codes

    decreasing = _base()
    decreasing.loc[1, "time_ms"] = -1.0
    study = _study(decreasing)
    report = audit_study_qc(study)
    assert "timestamp_decreasing" in report.issue_codes
    with pytest.raises(ValueError, match="timestamps decrease"):
        study.validate_time_order()


def test_extra_columns_are_preserved_but_not_required_by_constructor() -> None:
    frame = _base().assign(
        condition=["control", "control", "treatment", "treatment"],
        quality=[0.92, 0.89, 0.95, 0.93],
    )
    study = _study(frame)

    assert "condition" in study.data.columns
    assert "quality" in study.data.columns
    study.require_columns(["condition", "quality"])

    with pytest.raises(ValueError, match="missing required columns"):
        study.require_columns(["not_present"])


def test_data_contract_center_states_runtime_and_scientific_boundaries() -> None:
    text = _text(CENTER)

    for contract in (
        "permalink: /docs/data-contract/",
        "page_type: data-contract",
        "Semantic mapping, not automatic interpretation",
        "Numeric does not mean unitless",
        "Constructor contract",
        "Construction failure versus structural review",
        "units | not inferred or converted",
        "participant / trial values",
        "validate_time_order()",
        "does not establish calibration quality",
    ):
        assert contract in text

    for control in (
        'for="schema-data-var"',
        'for="schema-participant"',
        'for="schema-trial"',
        'for="schema-timestamp"',
        'for="schema-x"',
        'for="schema-y"',
        'data-schema-status role="status" aria-live="polite"',
    ):
        assert control in text

    assert 'type="file"' not in text
    assert "data-upload" not in text
    assert "FileReader" not in text


def test_mapping_guide_prohibits_silent_schema_repairs() -> None:
    text = _text(GUIDE)

    for contract in (
        "Inventory the source before renaming anything",
        "Record units separately from names",
        "Distinguish constructor errors from review conditions",
        "Check time order explicitly",
        "Preserve source and mapping provenance",
        "Do not silently coerce a bad schema",
        "structural preflight was run",
    ):
        assert contract in text

    assert "converting arbitrary strings to numeric with coercion-to-missing" in text
    assert "inventing trial IDs when the analysis unit is ambiguous" in text


def test_failure_case_example_is_synthetic_and_nonprescriptive() -> None:
    text = _text(EXAMPLE)

    assert "fully synthetic data-contract exercise" in text
    assert "No case on this page defines a universal exclusion rule." in text

    for heading in (
        "missing mapped column: constructor failure",
        "nonnumeric coordinate: constructor failure",
        "empty table: constructor failure",
        "missing coordinate: construct, then review",
        "missing participant identifier: construct, then review",
        "duplicate timestamp: construct, then review",
        "decreasing timestamp: construct, review, optional fail-fast",
        "extra scientific columns: preserved, not interpreted",
    ):
        assert heading in text

    assert "constructor validity and temporal-order validity are separate contracts" in text
    assert "Passing the constructor or structural preflight does not establish" in _text(EXAMPLE)


def test_schema_mapper_is_local_labelled_and_does_not_infer_scientific_values() -> None:
    js = _text(JS)
    css = _text(CSS)

    for contract in (
        "data-schema-data-var",
        "data-schema-participant",
        "data-schema-trial",
        "data-schema-timestamp",
        "data-schema-x",
        "data-schema-y",
        "pythonIdentifier",
        "Complete all five semantic column mappings",
        "Units and scientific meaning still need to be recorded separately.",
        "navigator.clipboard",
        "document.execCommand('copy')",
        "search",
    ):
        if contract == "search":
            continue
        assert contract in js

    assert "fetch(" not in js
    assert "FileReader" not in js

    for contract in (
        ".schema-mapper",
        ".schema-mapper-grid",
        ".schema-mapper-output",
        ":focus-visible",
        "@media (max-width: 720px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_data_contract_visual_has_accessible_svg_metadata() -> None:
    text = _text(SVG)

    assert 'role="img"' in text
    assert 'aria-labelledby="title desc"' in text
    assert "<title" in text
    assert "<desc" in text
    assert "Structural preflight" in text
    assert "Downstream analysis" in text


def test_data_contract_routes_are_discoverable() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    compass = _text(COMPASS)
    readme = _text(README)

    assert layout.count("/docs/data-contract/") >= 3
    assert "/docs/guides/map-your-table/" in layout
    assert "/docs/examples/data-contract-valid-invalid/" in layout
    assert "[Data Contract & Schema Mapping Center](data-contract/)" in docs
    assert 'href="map-your-table/">Map your table →</a>' in guides
    assert 'href="data-contract-valid-invalid/">Data contract cases →</a>' in examples
    assert "/docs/data-contract/" in compass
    assert "/docs/data-contract/" in readme


def test_layout_loads_data_contract_assets_only_for_data_contract_page() -> None:
    text = _text(LAYOUT)

    assert "page.page_type == 'data-contract'" in text
    assert "assets/css/data-contract.css" in text
    assert "assets/js/data-contract.js" in text


def test_generated_site_requires_data_contract_routes_and_assets() -> None:
    text = _text(SITE_CHECK)

    for path in (
        "docs/data-contract/index.html",
        "docs/guides/map-your-table/index.html",
        "docs/examples/data-contract-valid-invalid/index.html",
        "assets/css/data-contract.css",
        "assets/js/data-contract.js",
        "assets/images/data-contract-flow.svg",
    ):
        assert f'"{path}"' in text
