from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "src" / "gazeaudit" / "__init__.py"
API_MAP = ROOT / "docs" / "reference" / "api-map.md"
LAYOUT = ROOT / "_layouts" / "default.html"
SEARCH_INDEX = ROOT / "assets" / "search-index.json"

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
    api_text = API_MAP.read_text(encoding="utf-8")
    tracked = sorted(
        name
        for name in exports
        if imported_from.get(name) in TRACKED_MODULES and not name.isupper()
    )
    missing = [name for name in tracked if f"`{name}`" not in api_text]
    if missing:
        raise SystemExit(
            "site governance: API map is missing tracked public exports: " + ", ".join(missing)
        )


def check_search_coverage() -> None:
    layout = LAYOUT.read_text(encoding="utf-8")
    indexed = {
        item["url"]
        for item in json.loads(SEARCH_INDEX.read_text(encoding="utf-8"))
        if isinstance(item, dict) and isinstance(item.get("url"), str)
    }
    nav_urls = set(
        re.findall(r"href=\"\{\{ '(/docs/[^']+)' \| relative_url \}\}\"", layout)
    )
    missing = sorted(url for url in nav_urls if url not in indexed)
    if missing:
        raise SystemExit(
            "site governance: navigation routes missing from search index: " + ", ".join(missing)
        )


def check_site_contract() -> None:
    layout = LAYOUT.read_text(encoding="utf-8")
    required = (
        'property="og:title"',
        'property="og:description"',
        'property="og:url"',
        'name="twitter:card"',
        "site.docs_channel",
        "site.release_version",
        "site.github.build_revision",
    )
    missing = [token for token in required if token not in layout]
    if missing:
        raise SystemExit("site governance: layout contract missing: " + ", ".join(missing))


if __name__ == "__main__":
    check_api_map()
    check_search_coverage()
    check_site_contract()
    print("SITE GOVERNANCE: PASS")
