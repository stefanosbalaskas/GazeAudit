from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "_config.yml"
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
    template = SEARCH_INDEX.read_text(encoding="utf-8")
    required_template = (
        'site.pages | sort: "url"',
        "item.title",
        "item.url contains '/docs/'",
        "item.search_category",
        "item.search_keywords",
        "search_description",
        "item.description | default: item.title",
        "item.title | jsonify",
        "item.url | jsonify",
        "search_description | jsonify",
        "search_keywords | strip | jsonify",
    )
    missing_template = [token for token in required_template if token not in template]
    if missing_template:
        raise SystemExit(
            "site governance: generated search template contract missing: "
            + ", ".join(missing_template)
        )

    nav_urls = set(
        re.findall(r"href=\"\{\{ '(/docs/[^']*)' \| relative_url \}\}\"", layout)
    )
    required_navigation = {
        "/docs/",
        "/docs/install/",
        "/docs/workspace/",
        "/docs/planner/",
        "/docs/methods/",
        "/docs/guides/first-real-audit/",
        "/docs/examples/first-real-audit/",
        "/docs/workflows/first-study-audit/",
        "/docs/reference/",
        "/docs/reference/api-map/",
        "/docs/reference/api-pathways/",
        "/docs/reference/cli-reference/",
        "/docs/reference/evidence-vocabulary/",
        "/docs/reference/core-api-inventory/",
        "/docs/reference/site-provenance/",
    }
    missing_nav = sorted(required_navigation - nav_urls)
    if missing_nav:
        raise SystemExit(
            "site governance: primary searchable navigation is missing routes: "
            + ", ".join(missing_nav)
        )

    metadata_pages = (
        ROOT / "docs" / "install.md",
        ROOT / "docs" / "workspace" / "index.md",
        ROOT / "docs" / "guides" / "first-real-audit.md",
        ROOT / "docs" / "examples" / "first-real-audit.md",
        ROOT / "docs" / "workflows" / "first-study-audit.md",
        ROOT / "docs" / "reference" / "index.md",
        ROOT / "docs" / "reference" / "api-pathways.md",
        ROOT / "docs" / "reference" / "cli-reference.md",
        ROOT / "docs" / "reference" / "evidence-vocabulary.md",
        CORE_API_INVENTORY,
        PROVENANCE_PAGE,
    )
    missing_metadata: list[str] = []
    for path in metadata_pages:
        text = path.read_text(encoding="utf-8")
        if "title:" not in text or "description:" not in text:
            missing_metadata.append(str(path.relative_to(ROOT)))
    if missing_metadata:
        raise SystemExit(
            "site governance: searchable core pages are missing title/description metadata: "
            + ", ".join(missing_metadata)
        )


def check_site_contract() -> None:
    config = CONFIG.read_text(encoding="utf-8")
    layout = LAYOUT.read_text(encoding="utf-8")
    provenance = PROVENANCE_PAGE.read_text(encoding="utf-8")
    robots = ROBOTS.read_text(encoding="utf-8")
    sitemap = SITEMAP.read_text(encoding="utf-8")

    required_config = (
        'release_version: "0.2.0"',
        "docs_channel: development",
    )
    missing = [token for token in required_config if token not in config]
    if missing:
        raise SystemExit("site governance: config identity missing: " + ", ".join(missing))

    required_layout = (
        'property="og:title"',
        'property="og:description"',
        'property="og:url"',
        'name="twitter:card"',
        "site.docs_channel",
        "site.release_version",
        "site.github.build_revision",
        "docs_source_ref",
        "data-copy-page-link",
        "View source",
        "data-primary-nav",
        "data-mobile-primary-nav",
        "/docs/reference/site-provenance/",
    )
    missing = [token for token in required_layout if token not in layout]
    if missing:
        raise SystemExit("site governance: layout contract missing: " + ", ".join(missing))

    required_provenance = (
        "v0.2.0",
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
