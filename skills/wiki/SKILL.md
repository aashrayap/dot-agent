---
name: wiki
description: "Manage an LLM knowledge base — scaffold, ingest sources, rebuild index state, query, lint. Karpathy-pattern: raw sources → compiled wiki → query/output."
---

# Wiki

## Composes With

- Parent: user wiki init/ingest/query/lint request.
- Children: `excalidraw-diagram` when a wiki answer or schema explanation needs a durable visual map.
- Uses format from: `excalidraw-diagram` for human-facing concept graphs, source flows, or schema diagrams when useful.
- Reads state from: detected wiki directory, `schema.md`, `index.md`, `log.md`, raw sources, and compiled pages.
- Writes through: wiki files under the selected wiki root.
- Hands off to: none.
- Receives back from: none.

LLM-maintained knowledge base. Raw sources are compiled into interlinked markdown articles.

When presenting a complex concept graph, ingestion flow, or wiki schema to a
human, lead with or link to a diagram when it will make the structure easier to
understand. Keep direct factual query answers concise when a diagram would add
noise.

## Subcommands

- `/wiki init` — scaffold a new wiki directory
- `/wiki ingest <file-or-folder>` — process a raw source into the wiki
- `/wiki rebuild-index` — generate machine-readable page graph and backlinks
- `/wiki query <question>` — research and answer from wiki content
- `/wiki lint` — health check the wiki

## Finding the Wiki

Search these paths in order, use the first match containing `schema.md`:
1. `./wiki/`
2. `../wiki/`
3. `~/Documents/wiki/`
4. `~/Documents/*/wiki/`

If no wiki found and subcommand is not `init`, tell the user and suggest `/wiki init`.

---

## /wiki init

Scaffold a new wiki directory in the current working directory.

Create:
```
wiki/
├── schema.md
├── index.md
├── log.md
├── raw/
│   └── assets/
├── concepts/
├── sources/
└── outputs/
```

**schema.md** — write the full wiki conventions:
- Three layers: raw (immutable) → wiki (LLM-owned) → schema (co-evolved)
- Page format: YAML frontmatter (title, tags, sources, created, updated; add `source_created` on source-derived pages when known) + markdown body + "See also" wikilinks
- Naming: lowercase hyphenated filenames, one concept per page
- Directory roles: raw/ = source documents, concepts/ = compiled knowledge, sources/ = per-source summaries, outputs/ = filed query results

**index.md** — master catalog with tables for Concepts, Sources, Outputs (initially empty).

**log.md** — append-only activity log. First entry: `## [YYYY-MM-DD] init | Wiki scaffolded`.

After creation, tell the user to:
1. Open the parent directory as an Obsidian vault
2. Install Obsidian Web Clipper, set default folder to `wiki/raw/`
3. Set attachment folder to `wiki/raw/assets/`
4. Bind "Download all remote images" to a hotkey
5. Optionally install agent-browser (`npm install -g agent-browser && agent-browser install`) for CLI-based scraping

---

## /wiki ingest

Process a raw source into the wiki.

### Input

A file or folder path in `raw/`. If the user just says "ingest this" without a path, check `raw/` for recently modified files and suggest them.

If the user provides a URL instead of a file path, detect the source type:

**YouTube URLs** (`youtube.com`, `youtu.be`):

Write and run a Python script that:
1. Uses `yt-dlp` to extract the video title and subtitles (auto-generated or manual)
2. Parses the VTT/SRT output — strips timestamps, deduplicates repeated lines, joins into clean paragraphs
3. Writes a markdown file to `raw/<slugified-title>.md` with a header like:
   ```
   # <Video Title>

   Source: YouTube transcript (<YYYY-MM-DD>)
   URL: <original-url>

   ---

   <cleaned transcript text>
   ```
4. Prints the output path so ingest can continue

Do NOT use browser tools for YouTube. The script must do all the work programmatically via `yt-dlp` (already installed). Prefer `--write-auto-sub --sub-lang en --skip-download` flags. Clean the VTT aggressively:
- Strip all timestamps and VTT formatting tags
- Deduplicate repeated lines (auto-subs repeat heavily)
- Decode HTML entities (`&gt;` → `>`, `&amp;` → `&`, etc.)
- Break paragraphs on speaker turns (`>>`) first, then sub-split long monologues every ~5 sentences
- Do NOT use mechanical fixed-length paragraph breaks — respect natural conversation flow

**All other URLs** — use agent-browser to scrape:
```
agent-browser open <url>
agent-browser get text "article"
```
Save the output to `raw/<slugified-title>.md`.

In both cases, proceed with normal ingest after saving to `raw/`.

### Steps

1. Read the source document(s) and any referenced images
2. Summarize key takeaways — present to user for discussion before proceeding
3. After user confirms direction:
   - Create `sources/<name>.md` — summary page with frontmatter including `source_created` when the source exposes a publication or creation date
   - Create or update relevant `concepts/*.md` pages — extract ideas, entities, claims
   - Add `[[wikilinks]]` cross-references between all touched pages
   - Note connections to existing wiki content and cross-repo links where relevant
4. Update `index.md` with new/changed pages
5. Re-run `/wiki rebuild-index`
6. Append entry to `log.md`: `## [YYYY-MM-DD] ingest | <source title>`

### Rules

- Never modify files in `raw/`
- One source at a time unless user explicitly requests batch
- Every page gets YAML frontmatter: title, tags, sources, created, updated
- Source-derived pages should also include `source_created` when known from the source material; don't guess missing dates
- Flag contradictions with existing wiki content — don't silently overwrite
- Prefer updating existing concept pages over creating near-duplicates

---

## /wiki query

Research a question using wiki content.

### Steps

1. Run:

```bash
python3 ~/.dot-agent/skills/wiki/scripts/query_wiki.py --wiki <wiki-path> "<question>"
```

2. Read `_index.json` and `_backlinks.json` if present; otherwise fall back to `index.md`
3. Read the top-ranked concept and source pages from the query helper
4. Synthesize answer with `[[wikilinks]]` citations to wiki pages
5. Present answer in conversation
6. Ask user: "File this to outputs?" If yes:
   - Write `outputs/<descriptive-name>.md` with frontmatter
   - Update `index.md`
   - Re-run `/wiki rebuild-index`
   - Append to `log.md`

### Output Formats

Choose based on the question:
- **Markdown page** — default for analysis, synthesis
- **Comparison table** — for "X vs Y" questions
- **Marp slides** — if user asks for presentation format
- **matplotlib/chart** — if user asks for visualization

---

## /wiki rebuild-index

Generate machine-readable state files for query and lint.

Run:

```bash
python3 ~/.dot-agent/skills/wiki/scripts/rebuild_index.py <wiki-path>
```

If already inside the repo that owns the wiki, the path can be omitted and the script will auto-discover the wiki root.

### Files written

- `_index.json` — page metadata, summaries, tags, sources, outlinks
- `_backlinks.json` — reverse link map for every local page
- `_lint.json` — current orphan pages and dead local links

### When to run

- After any ingest that creates or updates wiki pages
- After filing a query result to `outputs/`
- Before `/wiki lint` if the graph state may be stale

### Rules

- Never modify `raw/`
- Keep `index.md` as the human-readable catalog
- Treat `_index.json`, `_backlinks.json`, and `_lint.json` as generated state

---

## /wiki lint

Health check the wiki.

### Checks

1. **Orphan pages** — pages with no inbound `[[wikilinks]]` from other pages
2. **Dead links** — `[[wikilinks]]` pointing to pages that don't exist
3. **Stale claims** — contradictions between pages (flag for review, don't auto-fix)
4. **Missing concepts** — terms frequently mentioned across pages but lacking their own concept page
5. **Index drift** — pages that exist but aren't listed in `index.md`
6. **Sparse sources** — source pages that didn't generate any concept page updates

### Output

Run `/wiki rebuild-index` first if `_lint.json` is missing or stale, then run:

```bash
python3 ~/.dot-agent/skills/wiki/scripts/lint_wiki.py --wiki <wiki-path>
```

Report findings in conversation. Suggest specific fixes. Only apply fixes with user approval.

Append to `log.md`: `## [YYYY-MM-DD] lint | <N> findings`

---

## Rules (all subcommands)

- Read `schema.md` at the start of every operation
- Never modify `raw/` files
- Always update `index.md` after any page creation or modification
- Re-run `/wiki rebuild-index` after any page creation or modification
- Always append to `log.md` after any operation
- Use `[[wikilinks]]` for all cross-references (Obsidian-compatible)
- YAML frontmatter on every wiki page (title, tags, sources, created, updated; add `source_created` on source-derived pages when known)
- Filenames: lowercase, hyphenated (e.g., `bottleneck-rotation.md`)
