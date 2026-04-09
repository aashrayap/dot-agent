#!/usr/bin/env python3
"""Build machine-readable wiki index and backlinks for local markdown wikis."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

WIKI_DIR_NAMES = ("concepts", "sources", "outputs")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
FRONTMATTER_BOUNDARY = "---"


def discover_wiki() -> Path | None:
    cwd = Path.cwd()
    candidates = [
        cwd / "wiki",
        cwd.parent / "wiki",
        Path.home() / "Documents" / "wiki",
    ]
    documents_dir = Path.home() / "Documents"
    if documents_dir.exists():
        candidates.extend(sorted(documents_dir.glob("*/wiki")))

    for candidate in candidates:
        if (candidate / "schema.md").exists():
            return candidate
    return None


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith(FRONTMATTER_BOUNDARY + "\n"):
        return {}, text

    lines = text.splitlines()
    frontmatter_lines: list[str] = []
    body_start = 0

    for idx in range(1, len(lines)):
        if lines[idx].strip() == FRONTMATTER_BOUNDARY:
            body_start = idx + 1
            break
        frontmatter_lines.append(lines[idx])
    else:
        return {}, text

    return parse_simple_yaml(frontmatter_lines), "\n".join(lines[body_start:])


def parse_simple_yaml(lines: list[str]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    current_items: list[str] = []

    def flush_multiline() -> None:
        nonlocal current_key, current_items
        if current_key is not None:
            data[current_key] = [item for item in current_items if item]
        current_key = None
        current_items = []

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line:
            continue

        if current_key and line.startswith("  - "):
            current_items.append(line[4:].strip())
            continue

        flush_multiline()
        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if value == "":
            current_key = key
            current_items = []
            continue

        data[key] = parse_scalar(value)

    flush_multiline()
    return data


def parse_scalar(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [strip_quotes(part.strip()) for part in inner.split(",") if part.strip()]
    return strip_quotes(value)


def strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def slugify_segment(value: str) -> str:
    lowered = value.lower().strip()
    lowered = re.sub(r"[^\w\s/-]", "", lowered)
    lowered = re.sub(r"\s+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered)
    return lowered.strip("-")


def clean_summary_line(line: str) -> str:
    cleaned = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", line)
    cleaned = re.sub(r"\[\[([^\]]+)\]\]", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:197] + "..." if len(cleaned) > 200 else cleaned


def extract_summary(body: str) -> str:
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("---"):
            continue
        return clean_summary_line(line)
    return ""


def extract_h1(body: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def normalize_link_target(target: str) -> str:
    target = target.strip()
    target = target.split("#", 1)[0]
    target = target.removesuffix(".md")
    return target


def classify_link(target: str, local_slugs: set[str], basename_map: dict[str, list[str]]) -> tuple[str | None, str]:
    normalized = normalize_link_target(target)
    if not normalized:
        return None, "ignored"

    candidates = [
        normalized,
        normalized.lower(),
        slugify_segment(normalized),
    ]

    for candidate in candidates:
        if candidate in local_slugs:
            return candidate, "local"

    if "/" not in normalized:
        slugged = slugify_segment(normalized)
        matches = (
            basename_map.get(normalized, [])
            + basename_map.get(normalized.lower(), [])
            + basename_map.get(slugged, [])
        )
        unique_matches = sorted(set(matches))
        if len(unique_matches) == 1:
            return unique_matches[0], "local"

    if normalized.startswith(("concepts/", "sources/", "outputs/")):
        return normalized, "dead"
    return normalized, "external"


def scan_pages(wiki_dir: Path) -> list[Path]:
    pages: list[Path] = []
    for dirname in WIKI_DIR_NAMES:
        root = wiki_dir / dirname
        if not root.exists():
            continue
        pages.extend(sorted(root.rglob("*.md")))
    return pages


def build_state(wiki_dir: Path) -> tuple[dict[str, Any], dict[str, list[str]], dict[str, Any]]:
    pages = scan_pages(wiki_dir)
    local_slugs = {path.relative_to(wiki_dir).with_suffix("").as_posix() for path in pages}
    basename_map: dict[str, list[str]] = {}

    for slug in local_slugs:
        basename = slug.rsplit("/", 1)[-1]
        basename_map.setdefault(basename, []).append(slug)
        basename_map.setdefault(basename.lower(), []).append(slug)

    page_entries: list[dict[str, Any]] = []
    backlinks: dict[str, list[str]] = {slug: [] for slug in sorted(local_slugs)}
    dead_links: list[dict[str, str]] = []

    for path in pages:
        slug = path.relative_to(wiki_dir).with_suffix("").as_posix()
        text = path.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(text)

        raw_links = [match.group(1) for match in WIKILINK_RE.finditer(body)]
        local_outlinks: list[str] = []
        external_links: list[str] = []
        page_dead_links: list[str] = []

        for raw_link in raw_links:
            target = raw_link.split("|", 1)[0]
            resolved, link_type = classify_link(target, local_slugs, basename_map)
            if link_type == "local" and resolved:
                local_outlinks.append(resolved)
                if slug != resolved:
                    backlinks[resolved].append(slug)
            elif link_type == "dead" and resolved:
                page_dead_links.append(resolved)
                dead_links.append({"source": slug, "target": resolved})
            elif link_type == "external" and resolved:
                external_links.append(resolved)

        entry = {
            "slug": slug,
            "path": str(path),
            "directory": slug.split("/", 1)[0],
            "title": frontmatter.get("title") or extract_h1(body, path.stem.replace("-", " ").title()),
            "summary": extract_summary(body),
            "tags": frontmatter.get("tags", []),
            "sources": frontmatter.get("sources", []),
            "created": frontmatter.get("created", ""),
            "updated": frontmatter.get("updated", ""),
            "source_created": frontmatter.get("source_created", ""),
            "aliases": frontmatter.get("aliases", []),
            "outlinks": sorted(set(local_outlinks)),
            "external_links": sorted(set(external_links)),
            "dead_links": sorted(set(page_dead_links)),
        }
        page_entries.append(entry)

    for slug in backlinks:
        backlinks[slug] = sorted(set(backlinks[slug]))

    orphan_pages = sorted(
        slug for slug, refs in backlinks.items() if not refs and not slug.startswith("outputs/")
    )
    stats = {
        "pages": len(page_entries),
        "concepts": sum(1 for item in page_entries if item["directory"] == "concepts"),
        "sources": sum(1 for item in page_entries if item["directory"] == "sources"),
        "outputs": sum(1 for item in page_entries if item["directory"] == "outputs"),
        "local_links": sum(len(item["outlinks"]) for item in page_entries),
        "external_links": sum(len(item["external_links"]) for item in page_entries),
        "dead_links": len(dead_links),
        "orphans": len(orphan_pages),
    }

    index_state = {
        "wiki_path": str(wiki_dir),
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "stats": stats,
        "pages": sorted(page_entries, key=lambda item: item["slug"]),
    }
    backlinks_state = {
        "wiki_path": str(wiki_dir),
        "generated_at": index_state["generated_at"],
        "backlinks": backlinks,
    }
    lint_state = {
        "wiki_path": str(wiki_dir),
        "generated_at": index_state["generated_at"],
        "orphan_pages": orphan_pages,
        "dead_links": dead_links,
    }
    return index_state, backlinks_state, lint_state


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wiki", nargs="?", help="Path to wiki root")
    return parser.parse_args()


def resolve_wiki(raw_path: str | None) -> Path:
    if raw_path:
        wiki_dir = Path(raw_path).expanduser().resolve()
    else:
        discovered = discover_wiki()
        if discovered is None:
            raise SystemExit("No wiki found. Pass the wiki path explicitly.")
        wiki_dir = discovered.resolve()

    if not (wiki_dir / "schema.md").exists():
        raise SystemExit(f"{wiki_dir} is not a wiki root (missing schema.md).")
    return wiki_dir


def main() -> int:
    args = parse_args()
    wiki_dir = resolve_wiki(args.wiki)
    index_state, backlinks_state, lint_state = build_state(wiki_dir)

    write_json(wiki_dir / "_index.json", index_state)
    write_json(wiki_dir / "_backlinks.json", backlinks_state)
    write_json(wiki_dir / "_lint.json", lint_state)

    print(
        f"Rebuilt wiki state for {wiki_dir} "
        f"({index_state['stats']['pages']} pages, {index_state['stats']['dead_links']} dead links, "
        f"{index_state['stats']['orphans']} orphans)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
