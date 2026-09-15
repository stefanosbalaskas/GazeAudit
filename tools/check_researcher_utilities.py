from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED_CATEGORIES = {"readiness", "robustness", "sensitivity", "measurement"}
REQUIRED_PLOT_KEYS = {"id", "filename", "title", "category", "question", "function", "method_ids"}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify(site: Path, baseurl: str) -> tuple[int, int]:
    methods = _load_json(site / "assets" / "method-index.json")
    plots = _load_json(site / "assets" / "plot-index.json")
    method_ids = {item["id"] for item in methods}

    if len(plots) != 14:
        raise SystemExit(f"expected 14 governed plots, found {len(plots)}")
    plot_ids = [item["id"] for item in plots]
    filenames = [item["filename"] for item in plots]
    if len(plot_ids) != len(set(plot_ids)):
        raise SystemExit("duplicate governed plot ids")
    if len(filenames) != len(set(filenames)):
        raise SystemExit("duplicate governed plot filenames")
    if {item["category"] for item in plots} != EXPECTED_CATEGORIES:
        raise SystemExit("governed plot categories do not match the four gallery categories")

    represented_methods: set[str] = set()
    plot_by_filename: dict[str, dict] = {}
    for plot in plots:
        missing = REQUIRED_PLOT_KEYS - set(plot)
        if missing:
            raise SystemExit(f"plot {plot.get('id', '<unknown>')} missing keys: {sorted(missing)}")
        if not plot["method_ids"]:
            raise SystemExit(f"plot {plot['id']} has no governed method links")
        unknown = set(plot["method_ids"]) - method_ids
        if unknown:
            raise SystemExit(f"plot {plot['id']} references unknown methods: {sorted(unknown)}")
        represented_methods.update(plot["method_ids"])
        plot_by_filename[plot["filename"]] = plot
        if not (site / "assets" / "plots" / plot["filename"]).is_file():
            raise SystemExit(f"published plot asset missing: {plot['filename']}")

    if represented_methods != method_ids:
        missing = sorted(method_ids - represented_methods)
        extra = sorted(represented_methods - method_ids)
        raise SystemExit(f"plot/method coverage mismatch; missing={missing}, extra={extra}")

    for method in methods:
        filename = Path(method["plot_url"]).name
        plot = plot_by_filename.get(filename)
        if plot is None:
            raise SystemExit(f"method {method['id']} points to ungoverned plot {filename}")
        if method["id"] not in plot["method_ids"]:
            raise SystemExit(f"method {method['id']} is not linked back from governed plot {plot['id']}")

    gallery = (site / "docs" / "plots" / "index.html").read_text(encoding="utf-8")
    for plot in plots:
        if f'id="plot-{plot["id"]}"' not in gallery:
            raise SystemExit(f"plot gallery missing stable anchor for {plot['id']}")
        for method_id in plot["method_ids"]:
            expected = f'{baseurl}/docs/methods/#method-{method_id}'
            if expected not in gallery:
                raise SystemExit(f"plot {plot['id']} missing method link {expected}")

    planner_page = (site / "docs" / "planner" / "index.html").read_text(encoding="utf-8")
    for marker in ("data-planner-copy-brief", "data-planner-download-json", "data-planner-export-status"):
        if marker not in planner_page:
            raise SystemExit(f"planner page missing export control: {marker}")

    planner_js = (site / "assets" / "js" / "planner.js").read_text(encoding="utf-8")
    required_js = (
        "schema_version: 1",
        "artifact_type: 'gazeaudit-navigation-plan'",
        "selected_conditions:",
        "method_route:",
        "workflow_handoffs:",
        "provenance:",
        "renderBrief",
        "JSON.stringify(currentManifest, null, 2)",
        "gazeaudit-audit-plan.json",
    )
    for marker in required_js:
        if marker not in planner_js:
            raise SystemExit(f"planner export implementation missing marker: {marker}")
    if "new Date(" in planner_js or "Date.now(" in planner_js:
        raise SystemExit("planner export must not add volatile timestamps")

    return len(plots), len(method_ids)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify governed researcher-facing site utilities")
    parser.add_argument("site", type=Path)
    parser.add_argument("--baseurl", default="")
    args = parser.parse_args()
    plot_count, method_count = verify(args.site, args.baseurl.rstrip("/"))
    print(f"RESEARCHER UTILITIES VERIFY: PASS ({plot_count} plots, {method_count} methods)")


if __name__ == "__main__":
    main()
