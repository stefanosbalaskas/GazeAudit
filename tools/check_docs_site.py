from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class _ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in {"a", "link"} and values.get("href"):
            self.references.append(("href", values["href"] or ""))
        if tag in {"img", "script", "source"} and values.get("src"):
            self.references.append(("src", values["src"] or ""))


def _candidate_targets(site_root: Path, source: Path, raw_reference: str, baseurl: str) -> list[Path]:
    split = urlsplit(raw_reference)
    if split.scheme or split.netloc or raw_reference.startswith(("mailto:", "tel:", "javascript:")):
        return []

    path = unquote(split.path)
    if not path:
        return []

    if path.startswith(baseurl + "/") or path == baseurl:
        path = path[len(baseurl) :]

    if path.startswith("/"):
        relative = path.lstrip("/")
        target = site_root / relative
    else:
        target = source.parent / path

    if path.endswith("/"):
        return [target / "index.html"]
    if target.suffix:
        return [target]
    return [target, target.with_suffix(".html"), target / "index.html"]


def _verify_search_index(site_root: Path, *, baseurl: str) -> None:
    search_path = site_root / "assets/search-index.json"
    try:
        index = json.loads(search_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid generated search index: {exc}") from exc

    if not isinstance(index, list) or len(index) < 20:
        raise SystemExit(f"unexpected documentation search index: {type(index).__name__}, entries={len(index) if isinstance(index, list) else 'n/a'}")

    required_keys = {"title", "category", "url", "description", "keywords"}
    urls: set[str] = set()
    failures: list[str] = []
    source = site_root / "index.html"
    for position, item in enumerate(index):
        if not isinstance(item, dict):
            failures.append(f"entry {position}: expected object")
            continue
        missing = required_keys.difference(item)
        if missing:
            failures.append(f"entry {position}: missing keys {sorted(missing)}")
            continue
        url = item["url"]
        if not isinstance(url, str) or not url.startswith("/docs/"):
            failures.append(f"entry {position}: invalid url {url!r}")
            continue
        if url in urls:
            failures.append(f"entry {position}: duplicate url {url!r}")
        urls.add(url)
        candidates = _candidate_targets(site_root, source, f"{baseurl}{url}", baseurl)
        if not candidates or not any(candidate.exists() for candidate in candidates):
            candidate_text = ", ".join(str(path.relative_to(site_root)) for path in candidates)
            failures.append(f"entry {position}: {url!r} -> [{candidate_text}]")

    if failures:
        preview = "\n".join(failures[:30])
        extra = "" if len(failures) <= 30 else f"\n... and {len(failures) - 30} more"
        raise SystemExit(f"search index target failures ({len(failures)}):\n{preview}{extra}")


def verify_site(site_root: Path, *, baseurl: str = "/GazeAudit") -> None:
    if not site_root.is_dir():
        raise SystemExit(f"site root does not exist: {site_root}")

    required = [
        "index.html",
        "docs/index.html",
        "docs/case-studies/index.html",
        "docs/case-studies/gazebase-incomplete/index.html",
        "docs/case-studies/korthals-target-tracking/index.html",
        "docs/case-studies/pedrotti-sensitivity/index.html",
        "assets/css/site.css",
        "assets/css/enhancements.css",
        "assets/js/site.js",
        "assets/search-index.json",
        "assets/images/aoi-boundary-uncertainty.svg",
        "assets/images/specification-curve.svg",
        "assets/images/sensitivity-curves.svg",
        "assets/images/workflow-overview.svg",
        "assets/images/gazebase-completeness.svg",
        "assets/images/korthals-effect.svg",
        "assets/images/pedrotti-sampling-sensitivity.svg",
        "assets/images/pedrotti-missingness-recovery.svg",
    ]
    missing_required = [path for path in required if not (site_root / path).is_file()]
    if missing_required:
        raise SystemExit(f"missing required generated site files: {missing_required}")

    forbidden = ["src", "tests", "tools", "release", ".github", "pyproject.toml", "README.md"]
    leaked = [path for path in forbidden if (site_root / path).exists()]
    if leaked:
        raise SystemExit(f"repository internals leaked into generated Pages site: {leaked}")

    html_files = sorted(site_root.rglob("*.html"))
    if len(html_files) < 24:
        raise SystemExit(f"unexpectedly small documentation site: {len(html_files)} HTML files")

    failures: list[str] = []
    for html_file in html_files:
        parser = _ReferenceParser()
        parser.feed(html_file.read_text(encoding="utf-8"))
        for attribute, reference in parser.references:
            if reference.startswith("#"):
                continue
            candidates = _candidate_targets(site_root, html_file, reference, baseurl)
            if not candidates:
                continue
            if not any(candidate.resolve().is_relative_to(site_root.resolve()) and candidate.exists() for candidate in candidates):
                display = html_file.relative_to(site_root)
                candidate_text = ", ".join(
                    str(path.relative_to(site_root)) if path.is_relative_to(site_root) else str(path)
                    for path in candidates
                )
                failures.append(f"{display}: {attribute}={reference!r} -> [{candidate_text}]")

    if failures:
        preview = "\n".join(failures[:30])
        extra = "" if len(failures) <= 30 else f"\n... and {len(failures) - 30} more"
        raise SystemExit(f"broken generated-site references ({len(failures)}):\n{preview}{extra}")

    _verify_search_index(site_root, baseurl=baseurl)
    print(f"DOCS SITE VERIFY: PASS ({len(html_files)} HTML pages)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the generated GazeAudit documentation site")
    parser.add_argument("site_root", type=Path)
    parser.add_argument("--baseurl", default="/GazeAudit")
    args = parser.parse_args()
    verify_site(args.site_root, baseurl=args.baseurl.rstrip("/"))


if __name__ == "__main__":
    main()
