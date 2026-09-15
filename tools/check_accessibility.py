from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


@dataclass
class ButtonRecord:
    attrs: dict[str, str | None]
    text: list[str] = field(default_factory=list)


class AccessibilityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.references: list[tuple[str, str]] = []
        self.images_missing_alt: list[str] = []
        self.dialogs_missing_name = 0
        self.html_lang: str | None = None
        self.main_ids: list[str | None] = []
        self.skip_targets: list[str] = []
        self.buttons: list[ButtonRecord] = []
        self._button_stack: list[ButtonRecord] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)

        for attr in ("aria-controls", "aria-labelledby", "aria-describedby"):
            value = values.get(attr)
            if value:
                for target in value.split():
                    self.references.append((attr, target))

        if tag == "html":
            self.html_lang = values.get("lang")
        elif tag == "main":
            self.main_ids.append(values.get("id"))
        elif tag == "img" and "alt" not in values:
            self.images_missing_alt.append(values.get("src") or "<unknown src>")
        elif tag == "dialog" and not (values.get("aria-label") or values.get("aria-labelledby")):
            self.dialogs_missing_name += 1
        elif tag == "a" and "skip-link" in (values.get("class") or "").split():
            href = values.get("href") or ""
            if href.startswith("#"):
                self.skip_targets.append(href[1:])
        elif tag == "button":
            record = ButtonRecord(values)
            self.buttons.append(record)
            self._button_stack.append(record)

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self._button_stack:
            self._button_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._button_stack and data.strip():
            self._button_stack[-1].text.append(data.strip())


def _button_has_name(button: ButtonRecord) -> bool:
    attrs = button.attrs
    return bool(
        (attrs.get("aria-label") or "").strip()
        or (attrs.get("aria-labelledby") or "").strip()
        or (attrs.get("title") or "").strip()
        or " ".join(button.text).strip()
    )


def verify_accessibility(site_root: Path) -> None:
    if not site_root.is_dir():
        raise SystemExit(f"site root does not exist: {site_root}")

    html_files = sorted(site_root.rglob("*.html"))
    if not html_files:
        raise SystemExit("no generated HTML files found")

    failures: list[str] = []
    for path in html_files:
        parser = AccessibilityParser()
        parser.feed(path.read_text(encoding="utf-8"))
        display = path.relative_to(site_root)
        ids = set(parser.ids)

        duplicates = sorted(identifier for identifier, count in Counter(parser.ids).items() if count > 1)
        if duplicates:
            failures.append(f"{display}: duplicate ids {duplicates}")

        for attr, target in parser.references:
            if target not in ids:
                failures.append(f"{display}: {attr} references missing id {target!r}")

        if not (parser.html_lang or "").strip():
            failures.append(f"{display}: html element has no lang")

        if len(parser.main_ids) != 1:
            failures.append(f"{display}: expected exactly one main landmark, found {len(parser.main_ids)}")

        if "main-content" not in parser.main_ids:
            failures.append(f"{display}: main landmark is not id='main-content'")

        if "main-content" not in parser.skip_targets:
            failures.append(f"{display}: skip link does not target #main-content")

        for src in parser.images_missing_alt:
            failures.append(f"{display}: image missing alt attribute: {src}")

        if parser.dialogs_missing_name:
            failures.append(f"{display}: {parser.dialogs_missing_name} dialog(s) missing accessible name")

        unnamed_buttons = sum(1 for button in parser.buttons if not _button_has_name(button))
        if unnamed_buttons:
            failures.append(f"{display}: {unnamed_buttons} button(s) have no accessible name")

    if failures:
        preview = "\n".join(failures[:50])
        extra = "" if len(failures) <= 50 else f"\n... and {len(failures) - 50} more"
        raise SystemExit(f"ACCESSIBILITY VERIFY: FAIL ({len(failures)} issues)\n{preview}{extra}")

    print(f"ACCESSIBILITY VERIFY: PASS ({len(html_files)} HTML pages)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify generated GazeAudit HTML accessibility contracts")
    parser.add_argument("site_root", type=Path)
    args = parser.parse_args()
    verify_accessibility(args.site_root)


if __name__ == "__main__":
    main()
