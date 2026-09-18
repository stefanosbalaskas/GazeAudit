import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from gazeaudit import GazeStudy, audit_study_qc, study_qc_diagnostics

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "_data" / "qc_issues.yml"
JSON_SOURCE = ROOT / "assets" / "qc-issue-reference.json"
CLINIC = ROOT / "docs" / "reference" / "qc-issue-clinic.md"
GUIDE = ROOT / "docs" / "guides" / "structural-qc-triage.md"
EXAMPLE = ROOT / "docs" / "examples" / "all-structural-qc-issues.md"
LAYOUT = ROOT / "_layouts" / "default.html"
CSS = ROOT / "assets" / "css" / "qc-issue-clinic.css"
JS = ROOT / "assets" / "js" / "qc-issue-clinic.js"
DOCS = ROOT / "docs" / "index.md"
GUIDES = ROOT / "docs" / "guides" / "index.md"
EXAMPLES = ROOT / "docs" / "examples" / "index.md"
REFERENCE = ROOT / "docs" / "reference" / "index.md"
COMPASS = ROOT / "docs" / "documentation-map.md"
FAQ = ROOT / "docs" / "faq.md"
README = ROOT / "README.md"
API_REFERENCE = ROOT / "assets" / "api-symbol-reference.json"
SITE_CHECK = ROOT / "tools" / "check_docs_site.py"

EXPECTED_ISSUES = {
    "coordinate_nonfinite",
    "timestamp_nonfinite",
    "identifier_missing",
    "timestamp_duplicate",
    "timestamp_decreasing",
}

EXPECTED_DETAILS = {
    "x_missing",
    "x_infinite",
    "y_missing",
    "y_infinite",
    "timestamp_missing",
    "timestamp_infinite",
    "participant_missing",
    "trial_missing",
    "timestamp_duplicate",
    "timestamp_decreasing",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _fixture() -> GazeStudy:
    frame = pd.DataFrame(
        {
            "participant_id": ["P01", "P01", "P01", None, "P02", "P02", "P03"],
            "trial_id": ["A", "A", "A", "A", "B", "B", None],
            "time_ms": [0.0, 0.0, np.nan, 2.0, 2.0, 1.0, np.inf],
            "gaze_x_px": [
                100.0,
                np.nan,
                np.inf,
                103.0,
                200.0,
                201.0,
                300.0,
            ],
            "gaze_y_px": [
                50.0,
                51.0,
                52.0,
                np.nan,
                60.0,
                np.inf,
                70.0,
            ],
        }
    )
    return GazeStudy(
        frame,
        x="gaze_x_px",
        y="gaze_y_px",
        timestamp="time_ms",
        participant="participant_id",
        trial="trial_id",
    )


def test_worked_fixture_exercises_every_runtime_issue_family() -> None:
    study = _fixture()
    report = audit_study_qc(study)

    assert report.status == "review"
    assert set(report.issue_codes) == EXPECTED_ISSUES
    assert report.coordinate_issue_rows == 4
    assert report.timestamp_issue_rows == 2
    assert report.missing_identifier_rows == 2
    assert report.duplicate_timestamp_rows == 2
    assert report.decreasing_time_groups == 1


def test_worked_fixture_exercises_every_runtime_detail_code_and_scope() -> None:
    diagnostics = study_qc_diagnostics(_fixture())

    assert len(diagnostics) == 11
    assert set(diagnostics["detail_code"]) == EXPECTED_DETAILS

    pairs = set(zip(diagnostics["issue_code"], diagnostics["scope"], strict=True))
    assert pairs == {
        ("coordinate_nonfinite", "row"),
        ("timestamp_nonfinite", "row"),
        ("identifier_missing", "row"),
        ("timestamp_duplicate", "row"),
        ("timestamp_decreasing", "group"),
    }

    expected_sequence = [
        "timestamp_duplicate",
        "x_missing",
        "timestamp_duplicate",
        "x_infinite",
        "timestamp_missing",
        "y_missing",
        "participant_missing",
        "y_infinite",
        "timestamp_infinite",
        "trial_missing",
        "timestamp_decreasing",
    ]
    assert diagnostics["detail_code"].tolist() == expected_sequence
    assert diagnostics["diagnostic_id"].tolist() == [
        f"D{number:06d}" for number in range(1, 12)
    ]


def test_governed_issue_catalog_matches_runtime_vocabulary() -> None:
    text = _text(CATALOG)

    issue_codes = set(
        re.findall(r"^- issue_code: ([a-z_]+)$", text, flags=re.MULTILINE)
    )
    detail_codes = set(
        re.findall(r"^    - code: ([a-z_]+)$", text, flags=re.MULTILINE)
    )

    assert issue_codes == EXPECTED_ISSUES
    assert detail_codes == EXPECTED_DETAILS
    assert text.count("  scope: row") == 4
    assert text.count("  scope: group") == 1

    for field in (
        "report_field:",
        "summary:",
        "inspect:",
        "possible_causes:",
        "not_infer:",
        "next_step:",
    ):
        assert text.count(field) >= 5


def test_issue_reference_json_is_generated_from_single_catalog() -> None:
    text = _text(JSON_SOURCE)

    assert "permalink: /assets/qc-issue-reference.json" in text
    assert "{{ site.data.qc_issues | jsonify }}" in text


def test_clinic_is_progressive_accessible_and_nonprescriptive() -> None:
    text = _text(CLINIC)

    for contract in (
        "page_type: qc-issue-clinic",
        "permalink: /docs/reference/qc-issue-clinic/",
        "site.data.qc_issues",
        "data-qc-clinic-controls",
        "data-qc-clinic-search",
        "data-qc-clinic-scope",
        "data-qc-clinic-status",
        'role="status"',
        'aria-live="polite"',
        "data-qc-issue",
        "All cards remain visible when JavaScript is unavailable.",
        "An issue code is an observation, not a verdict.",
        'Do not skip directly from §status == "review"§ to filtering.',
        "Do not reuse old diagnostic IDs",
    ):
        assert contract.replace("§", chr(96)) in text

    assert "Structural preflight evaluates a bounded set" in text
    assert "Do **not** copy numerical values from synthetic examples." in text


def test_clinic_filtering_and_styles_are_progressive() -> None:
    js = _text(JS)
    css = _text(CSS)

    for contract in (
        "data-qc-clinic",
        "data-qc-issue",
        "card.hidden = !show",
        "Showing ${visible} of ${total} issue families.",
        "empty.hidden = visible !== 0",
        "search.focus()",
    ):
        assert contract in js

    for contract in (
        ".qc-clinic-controls",
        ".qc-clinic-grid",
        ".qc-clinic-card",
        ".qc-clinic-boundary",
        ".qc-clinic-next",
        ":focus-visible",
        "@media (max-width: 760px)",
        "@media (forced-colors: active)",
    ):
        assert contract in css


def test_triage_guide_covers_decision_repair_reporting_and_limits() -> None:
    text = _text(GUIDE)

    for heading in (
        "Freeze the representation you are reviewing",
        "Run the summary and diagnostics together",
        "Classify the condition before deciding",
        "Trace every flag to source evidence",
        "Record the decision",
        "If you repair the representation, create a new audit state",
        "Keep structural QC separate from readiness policy",
        "Check endpoint dependence",
        "Preserve the denominator",
        "Reporting examples",
        "What not to report",
        "When not to use structural QC as the decision layer",
    ):
        assert heading in text

    for boundary in (
        "Do not silently interpolate or replace missing coordinates with zero.",
        "Do not deduplicate simply because timestamps are equal.",
        "Do not sort solely to make §timestamp_decreasing§ disappear.",
        "A reduced issue count is descriptive.",
        "Do not convert the mere presence of an issue code",
    ):
        assert boundary.replace("§", chr(96)) in text


def test_all_issue_example_is_governed_synthetic_and_bounded() -> None:
    text = _text(EXAMPLE)

    for contract in (
        "page_type: example",
        'example_data: "Synthetic"',
        'example_focus: "Data & QC"',
        "all five implemented structural-QC issue families",
        "all ten current **detail-code types**",
        "diagnostic table contains eleven records",
        "Teaching fixture, not a data-cleaning recipe.",
        "This numerical statement belongs only to this synthetic teaching fixture.",
        "Structural preflight identifies a bounded set",
    ):
        assert contract in text

    for code in EXPECTED_ISSUES | EXPECTED_DETAILS:
        assert f"§{code}§".replace("§", chr(96)) in text


def test_clinic_api_links_resolve_to_governed_api_anchors() -> None:
    clinic = _text(CLINIC)
    api = json.loads(_text(API_REFERENCE))
    anchors = {item["anchor"] for item in api["symbols"]}

    expected_anchors = {
        "api-gazestudy",
        "api-audit-study-qc",
        "api-study-qc-diagnostics",
        "api-build-study-qc-audit",
    }
    assert expected_anchors.issubset(anchors)

    for anchor in expected_anchors:
        assert f"#{anchor}" in clinic


def test_clinic_routes_are_discoverable_across_documentation_surfaces() -> None:
    layout = _text(LAYOUT)
    docs = _text(DOCS)
    guides = _text(GUIDES)
    examples = _text(EXAMPLES)
    reference = _text(REFERENCE)
    compass = _text(COMPASS)
    faq = _text(FAQ)
    readme = _text(README)

    assert layout.count("/docs/reference/qc-issue-clinic/") >= 2
    assert "/docs/guides/structural-qc-triage/" in layout
    assert "/docs/examples/all-structural-qc-issues/" in layout

    assert "[Structural QC Issue Clinic](reference/qc-issue-clinic/)" in docs
    assert 'href="structural-qc-triage/">Structural-QC triage →</a>' in guides
    assert (
        'href="all-structural-qc-issues/">All structural-QC issues →</a>'
        in examples
    )
    assert "/docs/reference/qc-issue-clinic/" in reference
    assert "/docs/reference/qc-issue-clinic/" in compass
    assert "/docs/reference/qc-issue-clinic/" in faq
    assert "/docs/reference/qc-issue-clinic/" in readme


def test_layout_and_site_verifier_govern_clinic_assets() -> None:
    layout = _text(LAYOUT)
    checker = _text(SITE_CHECK)

    assert "page.page_type == 'qc-issue-clinic'" in layout
    assert "assets/css/qc-issue-clinic.css" in layout
    assert "assets/js/qc-issue-clinic.js" in layout

    for contract in (
        "def _verify_qc_issue_reference",
        "unexpected QC issue catalog",
        "QC issue codes mismatch",
        "QC detail codes mismatch",
        "_verify_qc_issue_reference(site_root)",
        '"docs/reference/qc-issue-clinic/index.html"',
        '"docs/guides/structural-qc-triage/index.html"',
        '"docs/examples/all-structural-qc-issues/index.html"',
        '"assets/qc-issue-reference.json"',
        '"assets/css/qc-issue-clinic.css"',
        '"assets/js/qc-issue-clinic.js"',
    ):
        assert contract in checker
