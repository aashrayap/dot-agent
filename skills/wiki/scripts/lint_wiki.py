#!/usr/bin/env python3
"""Report wiki lint findings from generated graph state."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


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


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def normalize_wikilink(raw_link: str) -> str:
    target = raw_link.split("|", 1)[0].strip()
    target = target.split("#", 1)[0].removesuffix(".md")
    return target


def parse_index_links(index_path: Path) -> set[str]:
    if not index_path.exists():
        return set()
    text = index_path.read_text(encoding="utf-8")
    links = set()
    for match in WIKILINK_RE.finditer(text):
        target = normalize_wikilink(match.group(1))
        if target.startswith(("concepts/", "sources/", "outputs/")):
            links.add(target)
    return links


def compute_sparse_sources(pages: list[dict[str, Any]], backlinks: dict[str, list[str]]) -> list[str]:
    concept_or_output_pages = [
        page for page in pages if page["directory"] in {"concepts", "outputs"}
    ]
    sparse: list[str] = []
    for page in pages:
        if page["directory"] != "sources":
            continue

        raw_sources = set(page.get("sources", []))
        explicit_consumers = [
            slug for slug in backlinks.get(page["slug"], [])
            if slug.startswith(("concepts/", "outputs/"))
        ]
        shared_source_consumers = [
            other["slug"]
            for other in concept_or_output_pages
            if raw_sources and raw_sources.intersection(other.get("sources", []))
        ]
        if not explicit_consumers and not shared_source_consumers:
            sparse.append(page["slug"])
    return sorted(set(sparse))


def compute_index_drift(pages: list[dict[str, Any]], indexed_links: set[str]) -> list[str]:
    local_pages = {page["slug"] for page in pages}
    return sorted(local_pages - indexed_links)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki", help="Path to wiki root")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki).expanduser().resolve() if args.wiki else discover_wiki()
    if not wiki_dir:
        raise SystemExit("Could not find a wiki directory with schema.md")

    index_json = wiki_dir / "_index.json"
    backlinks_json = wiki_dir / "_backlinks.json"
    lint_json = wiki_dir / "_lint.json"
    if not index_json.exists() or not backlinks_json.exists() or not lint_json.exists():
        raise SystemExit(
            f"Missing generated state in {wiki_dir}. Run "
            f"`python3 ~/.dot-agent/skills/wiki/scripts/rebuild_index.py {wiki_dir}` first."
        )

    index_state = load_json(index_json)
    backlinks = load_json(backlinks_json)
    lint_state = load_json(lint_json)
    indexed_links = parse_index_links(wiki_dir / "index.md")

    sparse_sources = compute_sparse_sources(index_state["pages"], backlinks)
    index_drift = compute_index_drift(index_state["pages"], indexed_links)
    top_hubs = sorted(
        (
            {"slug": slug, "backlinks": len(refs)}
            for slug, refs in backlinks.items()
        ),
        key=lambda item: (-item["backlinks"], item["slug"]),
    )[:8]

    report = {
        "wiki_root": str(wiki_dir),
        "generated_at": index_state["generated_at"],
        "stats": index_state["stats"],
        "dead_links": lint_state.get("dead_links", []),
        "orphan_pages": lint_state.get("orphan_pages", []),
        "index_drift": index_drift,
        "sparse_sources": sparse_sources,
        "top_hubs": top_hubs,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("# Wiki Lint\n")
    print(f"- Wiki: `{wiki_dir}`")
    print(f"- Pages: {report['stats']['pages']}")
    print(f"- Dead links: {len(report['dead_links'])}")
    print(f"- Orphan pages: {len(report['orphan_pages'])}")
    print(f"- Index drift: {len(report['index_drift'])}")
    print(f"- Sparse sources: {len(report['sparse_sources'])}\n")

    print("## Findings")
    if report["dead_links"]:
        dead_links_text = ", ".join(
            f"{item['source']} -> {item['target']}"
            for item in report["dead_links"]
        )
        print(f"- Dead links: {dead_links_text}")
    else:
        print("- Dead links: none")
    if report["orphan_pages"]:
        print(f"- Orphan pages: {', '.join(report['orphan_pages'])}")
    else:
        print("- Orphan pages: none")
    if report["index_drift"]:
        print(f"- Index drift: {', '.join(report['index_drift'])}")
    else:
        print("- Index drift: none")
    if report["sparse_sources"]:
        print(f"- Sparse sources: {', '.join(report['sparse_sources'])}")
    else:
        print("- Sparse sources: none")

    print("\n## Hubs")
    for hub in report["top_hubs"]:
        print(f"- [[{hub['slug']}]] ({hub['backlinks']} backlinks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
