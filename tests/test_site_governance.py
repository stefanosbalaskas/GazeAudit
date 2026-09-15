from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_site_governance_verifier_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/check_site_governance.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "SITE GOVERNANCE: PASS" in completed.stdout


def test_docs_site_runs_on_main_push() -> None:
    workflow = (ROOT / ".github" / "workflows" / "docs-site.yml").read_text(encoding="utf-8")
    assert "push:" in workflow
    assert "- main" in workflow
    assert "python tools/check_site_governance.py" in workflow


def test_search_catalog_is_generated_and_core_routes_remain_governed() -> None:
    template = (ROOT / "assets" / "search-index.json").read_text(encoding="utf-8")
    verifier = (ROOT / "tools" / "check_site_governance.py").read_text(encoding="utf-8")
    for marker in (
        'site.pages | sort: "url"',
        "item.title",
        "item.url contains '/docs/'",
        "item.description | default: item.title",
        "item.title | jsonify",
        "item.url | jsonify",
    ):
        assert marker in template
    for route in (
        "/docs/workspace/",
        "/docs/reference/core-api-inventory/",
        "/docs/reference/site-provenance/",
    ):
        assert route in verifier


def test_site_provenance_keeps_release_and_development_identity_separate() -> None:
    page = (ROOT / "docs" / "reference" / "site-provenance.md").read_text(encoding="utf-8")
    assert "site.github.build_revision" in page
    assert "Stable package release: **v0.1.0**" in page
    assert "current `main` is equivalent to v0.1.0" in page
    assert "incomplete" in page
    assert "robust_negative" in page
    assert "materially_fragile" in page


def test_sitemap_and_robots_are_bound() -> None:
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    assert "<urlset" in sitemap
    assert "absolute_url" in sitemap
    assert "Sitemap: {{ '/sitemap.xml' | absolute_url }}" in robots
