"""Validate the static HTML emitted by Jekyll in ``_site``."""

from __future__ import annotations

import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
ERRORS: list[str] = []


def _read_baseurl() -> str:
    config = ROOT / "_config.yml"
    for line in config.read_text(encoding="utf-8").splitlines():
        if line.startswith("baseurl:"):
            value = line.split(":", 1)[1].strip().strip("\"'")
            return value.rstrip("/")
    return ""


BASEURL = _read_baseurl()


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str]] = []
        self.ids: list[str] = []
        self.lang: str | None = None
        self.h1_count = 0
        self.has_canonical = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)

        if tag == "html":
            self.lang = values.get("lang")
        if tag == "h1":
            self.h1_count += 1
        if values.get("id"):
            self.ids.append(values["id"] or "")

        if tag == "img" and "alt" not in values:
            ERRORS.append("Image without alt attribute")

        if tag == "link" and values.get("rel") == "canonical":
            self.has_canonical = bool(values.get("href"))

        for attribute in ("href", "src", "poster"):
            value = values.get(attribute)
            if value:
                self.references.append((attribute, value))

        srcset = values.get("srcset")
        if srcset:
            for candidate in srcset.split(","):
                url = candidate.strip().split()[0]
                if url:
                    self.references.append(("srcset", url))

        if tag == "script" and _is_external(values.get("src")):
            ERRORS.append(f"External script dependency: {values['src']}")
        if (
            tag == "link"
            and "stylesheet" in (values.get("rel") or "").split()
            and _is_external(values.get("href"))
        ):
            ERRORS.append(f"External stylesheet dependency: {values['href']}")


def _is_external(value: str | None) -> bool:
    return bool(value and (value.startswith("http://") or value.startswith("https://") or value.startswith("//")))


def _target_for(page: Path, reference: str) -> Path | None:
    if not reference or reference.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
        return None

    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc:
        return None

    path = unquote(parsed.path)
    if not path:
        return None

    if path.startswith("/"):
        if BASEURL and (path == BASEURL or path.startswith(f"{BASEURL}/")):
            path = path[len(BASEURL) :] or "/"
        target = SITE / path.lstrip("/")
    else:
        target = page.parent / path
    if path.endswith("/"):
        target /= "index.html"
    elif target.is_dir():
        target /= "index.html"
    return target.resolve()


def check_page(page: Path) -> None:
    parser = PageParser()
    parser.feed(page.read_text(encoding="utf-8"))
    relative = page.relative_to(SITE)

    if parser.lang != "pt-BR":
        ERRORS.append(f"{relative}: expected html lang=pt-BR")
    if parser.h1_count != 1:
        ERRORS.append(f"{relative}: expected exactly one h1, found {parser.h1_count}")
    if not parser.has_canonical:
        ERRORS.append(f"{relative}: canonical link is missing")

    duplicates = [item for item, count in Counter(parser.ids).items() if count > 1]
    if duplicates:
        ERRORS.append(f"{relative}: duplicate IDs: {', '.join(sorted(duplicates))}")

    for attribute, reference in parser.references:
        target = _target_for(page, reference)
        if target is not None and not target.exists():
            ERRORS.append(f"{relative}: broken {attribute} reference: {reference}")


def main() -> int:
    if not SITE.exists():
        print("Build checks failed:\n- _site does not exist; run Jekyll first")
        return 1

    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        print("Build checks failed:\n- no generated HTML pages found")
        return 1

    for page in pages:
        before = len(ERRORS)
        check_page(page)
        for index in range(before, len(ERRORS)):
            if ERRORS[index] == "Image without alt attribute":
                ERRORS[index] = f"{page.relative_to(SITE)}: image without alt attribute"

    if ERRORS:
        print("Build checks failed:")
        for item in ERRORS:
            print(f"- {item}")
        return 1

    print(f"Build checks passed. {len(pages)} HTML pages validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
