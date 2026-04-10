#!/usr/bin/env python3
"""Rank relevant wiki pages for a question using generated graph state."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "i", "in", "is", "it", "me", "my", "of", "on", "or", "that", "the",
    "their", "this", "to", "what", "when", "where", "which", "who", "why",
    "with", "your",
}


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


def tokenize(text: str) -> list[str]:
    terms = re.findall(r"[a-z0-9]+", text.lower())
    return [term for term in terms if len(term) > 1 and term not in STOPWORDS]


def phrase(text: str) -> str:
    return " ".join(tokenize(text))


def score_page(page: dict[str, Any], query_terms: list[str], query_phrase: str) -> tuple[float, list[str]]:
    title_terms = Counter(tokenize(page["title"]))
    slug_terms = Counter(tokenize(page["slug"].replace("/", " ")))
    summary_terms = Counter(tokenize(page.get("summary", "")))
    tag_terms = Counter(tokenize(" ".join(page.get("tags", []))))
    alias_terms = Counter(tokenize(" ".join(page.get("aliases", []))))
    source_terms = Counter(tokenize(" ".join(page.get("sources", []))))

    score = 0.0
    reasons: list[str] = []

    for term in query_terms:
        title_hits = title_terms[term]
        alias_hits = alias_terms[term]
        tag_hits = tag_terms[term]
        slug_hits = slug_terms[term]
        summary_hits = summary_terms[term]
        source_hits = source_terms[term]

        if title_hits:
            score += 8.0 * title_hits
        if alias_hits:
            score += 7.0 * alias_hits
        if tag_hits:
            score += 6.0 * tag_hits
        if slug_hits:
            score += 5.0 * slug_hits
        if summary_hits:
            score += 3.0 * min(summary_hits, 2)
        if source_hits:
            score += 1.5 * min(source_hits, 2)

    normalized_title = phrase(page["title"])
    normalized_summary = phrase(page.get("summary", ""))
    normalized_slug = phrase(page["slug"].replace("/", " "))

    if query_phrase and query_phrase in normalized_title:
        score += 14.0
        reasons.append("title phrase match")
    if query_phrase and query_phrase in normalized_summary:
        score += 8.0
        reasons.append("summary phrase match")
    if query_phrase and query_phrase in normalized_slug:
        score += 7.0
        reasons.append("slug phrase match")

    if any(term in title_terms for term in query_terms):
        reasons.append("title match")
    if any(term in tag_terms for term in query_terms):
        reasons.append("tag match")
    if any(term in summary_terms for term in query_terms):
        reasons.append("summary match")
    if any(term in slug_terms for term in query_terms):
        reasons.append("slug match")
    if any(term in alias_terms for term in query_terms):
        reasons.append("alias match")

    if page["directory"] == "concepts":
        score += 0.5
    elif page["directory"] == "sources":
        score += 0.25
    elif page["directory"] == "outputs":
        score -= 1.5

    return score, list(dict.fromkeys(reasons))


def rank_pages(
    pages: list[dict[str, Any]],
    backlinks: dict[str, list[str]],
    question: str,
) -> list[dict[str, Any]]:
    query_terms = tokenize(question)
    query_phrase = phrase(question)
    if not query_terms:
        return []

    scored: dict[str, dict[str, Any]] = {}
    for page in pages:
        base_score, reasons = score_page(page, query_terms, query_phrase)
        scored[page["slug"]] = {
            "page": page,
            "base_score": base_score,
            "reasons": reasons,
        }

    for slug, payload in scored.items():
        inbound = backlinks.get(slug, [])
        link_bonus = 0.15 * sum(scored[source]["base_score"] for source in inbound if source in scored)
        payload["score"] = payload["base_score"] + link_bonus
        payload["backlink_count"] = len(inbound)
        if link_bonus >= 1.0:
            payload["reasons"].append("linked from relevant pages")

    ranked = [
        {
            "slug": slug,
            "title": payload["page"]["title"],
            "directory": payload["page"]["directory"],
            "summary": payload["page"].get("summary", ""),
            "tags": payload["page"].get("tags", []),
            "score": round(payload["score"], 2),
            "backlink_count": payload["backlink_count"],
            "outlinks": payload["page"].get("outlinks", []),
            "reasons": payload["reasons"],
        }
        for slug, payload in scored.items()
        if payload["score"] > 0
    ]
    ranked.sort(key=lambda item: (-item["score"], item["slug"]))
    return ranked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="Natural language question to route into the wiki")
    parser.add_argument("--wiki", help="Path to wiki root")
    parser.add_argument("--top", type=int, default=8, help="Number of ranked results to show")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki).expanduser().resolve() if args.wiki else discover_wiki()
    if not wiki_dir:
        raise SystemExit("Could not find a wiki directory with schema.md")

    index_path = wiki_dir / "_index.json"
    backlinks_path = wiki_dir / "_backlinks.json"
    if not index_path.exists() or not backlinks_path.exists():
        raise SystemExit(
            f"Missing generated state in {wiki_dir}. Run "
            f"`python3 ~/.dot-agent/skills/wiki/scripts/rebuild_index.py {wiki_dir}` first."
        )

    index_state = load_json(index_path)
    backlinks = load_json(backlinks_path)
    ranked = rank_pages(index_state["pages"], backlinks, args.question)[: args.top]

    if args.json:
        print(json.dumps({
            "wiki_root": str(wiki_dir),
            "question": args.question,
            "results": ranked,
        }, indent=2))
        return 0

    print(f"# Query Route\n")
    print(f"- Wiki: `{wiki_dir}`")
    print(f"- Question: {args.question}")
    print(f"- Indexed pages: {index_state['stats']['pages']}")
    if not ranked:
        print("- Results: no strong lexical matches; broaden tags or inspect `_index.json` manually")
        return 0

    print(f"- Results shown: {len(ranked)}\n")
    print("## Ranked Pages")
    for idx, item in enumerate(ranked, start=1):
        reason_text = ", ".join(item["reasons"][:3]) if item["reasons"] else "graph proximity"
        print(
            f"{idx}. [[{item['slug']}]] ({item['directory']}, score {item['score']}, "
            f"backlinks {item['backlink_count']})"
        )
        if item["summary"]:
            print(f"   - {item['summary']}")
        print(f"   - Why: {reason_text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
