from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _catalog_ids(source: str) -> set[str]:
    return set(re.findall(r"^- id: ([a-z0-9-]+)$", source, flags=re.MULTILINE))


def _plot_method_ids(source: str) -> set[str]:
    values: set[str] = set()
    in_methods = False
    for line in source.splitlines():
        if line == "  method_ids:":
            in_methods = True
            continue
        if in_methods and line.startswith("    - "):
            values.add(line.removeprefix("    - ").strip())
            continue
        if in_methods and not line.startswith("    "):
            in_methods = False
    return values


def test_governed_plot_catalog_covers_every_method_family() -> None:
    methods = _catalog_ids(_text("_data/methods.yml"))
    plot_methods = _plot_method_ids(_text("_data/plots.yml"))
    assert len(methods) == 10
    assert plot_methods == methods


def test_planner_exports_are_portable_and_non_diagnostic() -> None:
    page = _text("docs/planner/index.md")
    script = _text("assets/js/planner.js")
    assert "data-planner-copy-brief" in page
    assert "data-planner-download-json" in page
    assert "data-planner-export-status" in page
    assert "stable `schema_version`" in page
    assert "No timestamp is inserted" in page
    assert "schema_version: 1" in script
    assert "artifact_type: 'gazeaudit-navigation-plan'" in script
    assert "selected_conditions:" in script
    assert "method_route:" in script
    assert "workflow_handoffs:" in script
    assert "gazeaudit_release:" in script
    assert "docs_revision:" in script
    assert "plan_url:" in script
    assert "renderBrief" in script
    assert "gazeaudit-audit-plan.json" in script
    assert "new Date(" not in script
    assert "Date.now(" not in script
    boundary = (
        "Thresholds, exclusions, scientific assumptions, and validity judgements "
        "remain researcher-owned."
    )
    assert boundary in script


def test_researcher_utilities_have_generated_site_gate() -> None:
    verifier = _text("tools/check_researcher_utilities.py")
    workflow = _text(".github/workflows/docs-site.yml")
    assert "EXPECTED_CATEGORIES" in verifier
    assert "plot/method coverage mismatch" in verifier
    assert "points to ungoverned plot" in verifier
    assert "must not add volatile timestamps" in verifier
    assert "RESEARCHER UTILITIES VERIFY: PASS" in verifier
    assert "python tools/check_researcher_utilities.py _site --baseurl /GazeAudit" in workflow
    assert '"tools/check_researcher_utilities.py"' in workflow
    assert '"tests/test_researcher_utilities.py"' in workflow


def test_plot_gallery_links_back_to_method_explorer() -> None:
    page = _text("docs/plots/index.md")
    css = _text("assets/css/gallery.css")
    assert "plot-method-links" in page
    assert "plot.method_ids" in page
    assert "/docs/methods/#method-" in page
    assert ".plot-method-links" in css
    assert ".plot-card:target" in css
