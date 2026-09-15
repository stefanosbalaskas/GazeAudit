from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "src" / "gazeaudit" / "__init__.py"
API_MAP = ROOT / "docs" / "reference" / "api-map.md"
CORE_API_INVENTORY = ROOT / "docs" / "reference" / "core-api-inventory.md"
PROVENANCE_PAGE = ROOT / "docs" / "reference" / "site-provenance.md"
LAYOUT = ROOT / "_layouts" / "default.html"
SEARCH_INDEX = ROOT / "assets" / "search-index.json"
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"

TRACKED_MODULES = {
    "aoi",
    "aoi_audit",
    "endpoints",
    "multiverse",
    "plotting",
    "readiness",
    "robustness",
    "sampling",
    "sensitivity",
    "study",
    "study_qc",
    "uncertainty",
}


def parse_public_exports() -> tuple[set[str], dict[str, str]]:
    tree = ast.parse(INIT.read_text(encoding="utf-8"))
    imported_from: dict[str, str] = {}
    exports: set[str] = set()

    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            module = node.module.lstrip(".")
            for alias in node.names:
                imported_from[alias.asname or alias.name] = module
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    exports = {
                        item.value
                        for item in node.value.elts
                        if isinstance(item, ast.Constant) and isinstance(item.value, str)
                    }
    if not exports:
        raise SystemExit("site governance: could not parse gazeaudit.__all__")
    return exports, imported_from


def check_api_map() -> None:
    exports, imported_from = parse_public_exports()
    documented = "\n".join(
        (
            API_MAP.read_text(encoding="utf-8"),
            CORE_API_INVENTORY.read_text(encoding="utf-8"),
        )
    )
    tracked = sorted(
        name
        for name in exports
        if imported_from.get(name) in TRACKED_MODULES and not name.isupper()
    )
    missing = [name for name in tracked if f"`{name}`" not in documented]
    if missing:
        raise SystemExit(
            "site governance: core documentation is missing tracked public exports: "
            + ", ".join(missing)
        )


def check_search_coverage() -> None:
    layout = LAYOUT.read_text(encoding="utf-8")
    items = json.loads(SEARCH_INDEX.read_text(encoding="utf-8"))
    indexed = {
        item["url"]
        for item in items
        if isinstance(item, dict) and isinstance(item.get("url"), str)
    }
    nav_urls = set(
        re.findall(r"href=\"\{\{ '(/docs/[^']+)' \| relative_url \}\}\"", layout)
    )
    required_reference = {
        "/docs/reference/core-api-inventory/",
        "/docs/reference/site-provenance/",
    }
    missing = sorted((nav_urls | required_reference) - indexed)
    if missing:
        raise SystemExit(
            "site governance: searchable documentation is missing routes: " + ", ".join(missing)
        )


def check_site_contract() -> None:
    provenance = PROVENANCE_PAGE.read_text(encoding="utf-8")
    robots = ROBOTS.read_text(encoding="utf-8")
    sitemap = SITEMAP.read_text(encoding="utf-8")
    required_provenance = (
        "v0.1.0",
        "site.github.build_revision",
        "10.5281/zenodo.22757340",
        "incomplete",
        "robust_negative",
        "materially_fragile",
    )
    missing = [token for token in required_provenance if token not in provenance]
    if missing:
        raise SystemExit("site governance: provenance page missing: " + ", ".join(missing))
    if "Sitemap:" not in robots or "/sitemap.xml" not in robots:
        raise SystemExit("site governance: robots.txt does not advertise sitemap")
    if "<urlset" not in sitemap or "absolute_url" not in sitemap:
        raise SystemExit("site governance: sitemap.xml contract is incomplete")


if __name__ == "__main__":
    check_api_map()
    check_search_coverage()
    check_site_contract()
    print("SITE GOVERNANCE: PASS")
