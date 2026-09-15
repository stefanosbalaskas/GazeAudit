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


def _resolves(site_root: Path, source: Path, reference: str, baseurl: str) -> bool:
    candidates = _candidate_targets(site_root, source, f"{baseurl}{reference}", baseurl)
    return bool(candidates) and any(
        candidate.resolve().is_relative_to(site_root.resolve()) and candidate.exists()
        for candidate in candidates
    )


def _verify_search_index(site_root: Path, *, baseurl: str) -> None:
    search_path = site_root / "assets/search-index.json"
    try:
        index = json.loads(search_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid generated search index: {exc}") from exc

    if not isinstance(index, list) or len(index) < 20:
        raise SystemExit(
            "unexpected documentation search index: "
            f"{type(index).__name__}, entries={len(index) if isinstance(index, list) else 'n/a'}"
        )

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


def _verify_method_index(site_root: Path, *, baseurl: str) -> None:
    method_path = site_root / "assets/method-index.json"
    try:
        methods = json.loads(method_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid generated method index: {exc}") from exc

    if not isinstance(methods, list) or len(methods) != 10:
        raise SystemExit(
            "unexpected method catalog: "
            f"{type(methods).__name__}, entries={len(methods) if isinstance(methods, list) else 'n/a'}"
        )

    required_keys = {
        "id",
        "phase",
        "phase_key",
        "title",
        "question",
        "purpose",
        "functions",
        "guide_url",
        "guide_label",
        "example_url",
        "example_label",
        "plot_url",
        "plot_label",
        "evidence_url",
        "evidence_label",
        "evidence_note",
        "keywords",
    }
    expected_phases = {
        "preflight",
        "governance",
        "measurement",
        "robustness",
        "sensitivity",
        "benchmarking",
        "evidence",
        "integration",
    }
    ids: set[str] = set()
    phases: set[str] = set()
    failures: list[str] = []
    source = site_root / "docs/methods/index.html"

    for position, item in enumerate(methods):
        if not isinstance(item, dict):
            failures.append(f"method {position}: expected object")
            continue
        missing = required_keys.difference(item)
        if missing:
            failures.append(f"method {position}: missing keys {sorted(missing)}")
            continue

        method_id = item["id"]
        if not isinstance(method_id, str) or not method_id:
            failures.append(f"method {position}: invalid id {method_id!r}")
        elif method_id in ids:
            failures.append(f"method {position}: duplicate id {method_id!r}")
        else:
            ids.add(method_id)

        phase = item["phase_key"]
        if not isinstance(phase, str) or phase not in expected_phases:
            failures.append(f"method {position}: invalid phase_key {phase!r}")
        else:
            phases.add(phase)

        functions = item["functions"]
        if not isinstance(functions, list) or not functions or not all(isinstance(name, str) and name for name in functions):
            failures.append(f"method {position}: functions must be a non-empty string list")

        for field in ("guide_url", "example_url", "plot_url"):
            reference = item[field]
            if not isinstance(reference, str) or not reference.startswith("/"):
                failures.append(f"method {position}: invalid {field} {reference!r}")
            elif not _resolves(site_root, source, reference, baseurl):
                failures.append(f"method {position}: unresolved {field} {reference!r}")

        evidence = item["evidence_url"]
        if evidence:
            if not isinstance(evidence, str) or not evidence.startswith("/"):
                failures.append(f"method {position}: invalid evidence_url {evidence!r}")
            elif not _resolves(site_root, source, evidence, baseurl):
                failures.append(f"method {position}: unresolved evidence_url {evidence!r}")
            if not item["evidence_label"]:
                failures.append(f"method {position}: evidence URL requires evidence_label")

    if phases != expected_phases:
        failures.append(f"method phases mismatch: expected {sorted(expected_phases)}, got {sorted(phases)}")

    if failures:
        preview = "\n".join(failures[:30])
        extra = "" if len(failures) <= 30 else f"\n... and {len(failures) - 30} more"
        raise SystemExit(f"method index failures ({len(failures)}):\n{preview}{extra}")


def verify_site(site_root: Path, *, baseurl: str = "/GazeAudit") -> None:
    if not site_root.is_dir():
        raise SystemExit(f"site root does not exist: {site_root}")

    required = [
        "index.html",
        "docs/index.html",
        "docs/methods/index.html",
        "docs/plots/index.html",
        "docs/reference/core-api-inventory/index.html",
        "docs/reference/site-provenance/index.html",
        "docs/case-studies/index.html",
        "docs/case-studies/gazebase-incomplete/index.html",
        "docs/case-studies/korthals-target-tracking/index.html",
        "docs/case-studies/pedrotti-sensitivity/index.html",
        "robots.txt",
        "sitemap.xml",
        "assets/css/site.css",
        "assets/css/enhancements.css",
        "assets/css/gallery.css",
        "assets/css/landing.css",
        "assets/css/methods.css",
        "assets/js/site.js",
        "assets/js/gallery.js",
        "assets/js/landing.js",
        "assets/js/methods.js",
        "assets/search-index.json",
        "assets/method-index.json",
        "assets/plots/specification-curve-code.svg",
        "assets/plots/trial-readiness.svg",
        "assets/plots/cohort-impact.svg",
        "assets/plots/aoi-probability-profile.svg",
        "assets/plots/threshold-sweep.svg",
        "assets/plots/factor-sensitivity.svg",
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

    robots = (site_root / "robots.txt").read_text(encoding="utf-8")
    sitemap = (site_root / "sitemap.xml").read_text(encoding="utf-8")
    if "sitemap.xml" not in robots.lower() or "<urlset" not in sitemap:
        raise SystemExit("generated discoverability endpoints are incomplete")

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
            if not any(
                candidate.resolve().is_relative_to(site_root.resolve()) and candidate.exists()
                for candidate in candidates
            ):
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
    _verify_method_index(site_root, baseurl=baseurl)
    print(f"DOCS SITE VERIFY: PASS ({len(html_files)} HTML pages)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the generated GazeAudit documentation site")
    parser.add_argument("site_root", type=Path)
    parser.add_argument("--baseurl", default="/GazeAudit")
    args = parser.parse_args()
    verify_site(args.site_root, baseurl=args.baseurl.rstrip("/"))


if __name__ == "__main__":
    main()
