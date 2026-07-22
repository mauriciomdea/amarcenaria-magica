"""Fast repository checks that do not require a running Jekyll server."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
IGNORED_TOP_LEVEL_DIRS = {"_site", "vendor", ".bundle", ".jekyll-cache"}


def error(message: str) -> None:
    ERRORS.append(message)


def project_files(*patterns: str) -> list[Path]:
    """Return first-party files without generated output or installed dependencies."""
    files: set[Path] = set()
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            relative = path.relative_to(ROOT)
            if path.is_file() and relative.parts[0] not in IGNORED_TOP_LEVEL_DIRS:
                files.add(path)
    return sorted(files)


def check_required_files() -> None:
    required = [
        "_config.yml",
        "Gemfile",
        "CNAME",
        "index.html",
        "moveis-sob-medida/index.html",
        "decoracao/index.html",
        "quem-somos/index.html",
        "privacidade/index.html",
        "404.html",
        "assets/vendor/bootstrap/bootstrap.min.css",
        "assets/vendor/bootstrap/bootstrap.bundle.min.js",
        "assets/css/main.css",
        "assets/js/main.js",
    ]
    for relative in required:
        if not (ROOT / relative).exists():
            error(f"Missing required file: {relative}")


def check_media() -> dict:
    manifest_path = ROOT / "_data" / "media.json"
    if not manifest_path.exists():
        error("Missing _data/media.json")
        return {}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key, media in manifest.items():
        if not media.get("alt", "").strip():
            error(f"Missing alt text: {key}")
        variants = media.get("variants", [])
        if not variants:
            error(f"No variants generated: {key}")
            continue
        for variant in variants:
            for format_name in ("avif", "webp", "jpg"):
                path = ROOT / variant[format_name].lstrip("/")
                if not path.exists():
                    error(f"Missing {format_name} variant: {path.relative_to(ROOT)}")
        fallback = ROOT / media["fallback"].lstrip("/")
        if fallback.exists():
            with Image.open(fallback) as image:
                if image.getexif():
                    error(f"Generated JPEG still contains EXIF: {fallback.relative_to(ROOT)}")
    return manifest


def check_media_references(manifest: dict) -> None:
    pattern = re.compile(r"(?:key=|hero_image:\s*|image:\s*|card_image:\s*|^\s*-\s+)(?:['\"])?([a-z]+/[a-z0-9-]+)", re.MULTILINE)
    source_files = project_files("*.html", "**/*.html", "_projects/*.md", "_decor/*.md")
    for path in source_files:
        text = path.read_text(encoding="utf-8")
        for key in pattern.findall(text):
            if key not in manifest and not key.startswith(("moveis/", "decoracao/", "quem/", "privacidade/")):
                error(f"Unknown media key '{key}' in {path.relative_to(ROOT)}")


def check_external_runtime_dependencies() -> None:
    templates = list(ROOT.glob("_includes/*.html")) + list(ROOT.glob("_layouts/*.html"))
    for path in templates:
        text = path.read_text(encoding="utf-8")
        if re.search(r"<(?:script|link)[^>]+(?:src|href)=['\"]https?://", text, re.IGNORECASE):
            error(f"External runtime asset found in {path.relative_to(ROOT)}")


def check_liquid_balance() -> None:
    block_pairs = {
        "if": "endif",
        "unless": "endunless",
        "for": "endfor",
        "case": "endcase",
        "capture": "endcapture",
    }
    closing = set(block_pairs.values())
    template_files = project_files("*.html", "**/*.html", "_projects/*.md", "_decor/*.md")
    for path in template_files:
        text = path.read_text(encoding="utf-8")
        if text.count("{{") != text.count("}}"):
            error(f"Unbalanced Liquid output braces: {path.relative_to(ROOT)}")
        if text.count("{%") != text.count("%}"):
            error(f"Unbalanced Liquid tag braces: {path.relative_to(ROOT)}")

        stack: list[tuple[str, str]] = []
        for match in re.finditer(r"{%[-\s]*(\w+).*?%}", text, re.DOTALL):
            tag = match.group(1)
            if tag in block_pairs:
                stack.append((tag, block_pairs[tag]))
            elif tag in closing:
                if not stack or stack[-1][1] != tag:
                    error(f"Unexpected Liquid tag '{tag}' in {path.relative_to(ROOT)}")
                    break
                stack.pop()
        if stack:
            error(f"Unclosed Liquid tag '{stack[-1][0]}' in {path.relative_to(ROOT)}")


def check_video() -> None:
    video = ROOT / "assets" / "video" / "mauricio-marcenaria-fina.mp4"
    poster = ROOT / "assets" / "video" / "mauricio-marcenaria-fina-poster.jpg"
    if not video.exists() or not poster.exists():
        error("Video or poster is missing")
    elif video.stat().st_size > 25 * 1024 * 1024:
        error("Web video is larger than 25 MB")


def main() -> int:
    check_required_files()
    manifest = check_media()
    check_media_references(manifest)
    check_external_runtime_dependencies()
    check_liquid_balance()
    check_video()

    if ERRORS:
        print("Site checks failed:")
        for item in ERRORS:
            print(f"- {item}")
        return 1

    print(f"All checks passed. {len(manifest)} media entries validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
