---
name: wiki
description: "Manage an LLM knowledge base — scaffold, ingest sources, query, lint. Karpathy-pattern: raw sources → compiled wiki → query/output."
---

# Wiki

LLM-maintained knowledge base. Raw sources are compiled into interlinked markdown articles.

## Subcommands

- `/wiki init` — scaffold a new wiki directory
- `/wiki ingest <file-or-folder>` — process a raw source into the wiki
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
- Page format: YAML frontmatter (title, tags, sources, created, updated) + markdown body + "See also" wikilinks
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

If the user provides a URL instead of a file path, use agent-browser to scrape it:
```
agent-browser open <url>
agent-browser get text "article"
```
Save the output to `raw/<slugified-title>.md`, then proceed with normal ingest.

### Steps

1. Read the source document(s) and any referenced images
2. Summarize key takeaways — present to user for discussion before proceeding
3. After user confirms direction:
   - Create `sources/<name>.md` — summary page with frontmatter
   - Create or update relevant `concepts/*.md` pages — extract ideas, entities, claims
   - Add `[[wikilinks]]` cross-references between all touched pages
   - Note connections to existing wiki content and cross-repo links where relevant
4. Update `index.md` with new/changed pages
5. Append entry to `log.md`: `## [YYYY-MM-DD] ingest | <source title>`

### Rules

- Never modify files in `raw/`
- One source at a time unless user explicitly requests batch
- Every page gets YAML frontmatter: title, tags, sources, created, updated
- Flag contradictions with existing wiki content — don't silently overwrite
- Prefer updating existing concept pages over creating near-duplicates

---

## /wiki query

Research a question using wiki content.

### Steps

1. Read `index.md` to find relevant pages
2. Read relevant concept and source pages
3. Synthesize answer with `[[wikilinks]]` citations to wiki pages
4. Present answer in conversation
5. Ask user: "File this to outputs?" If yes:
   - Write `outputs/<descriptive-name>.md` with frontmatter
   - Update `index.md`
   - Append to `log.md`

### Output Formats

Choose based on the question:
- **Markdown page** — default for analysis, synthesis
- **Comparison table** — for "X vs Y" questions
- **Marp slides** — if user asks for presentation format
- **matplotlib/chart** — if user asks for visualization

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

Report findings in conversation. Suggest specific fixes. Only apply fixes with user approval.

Append to `log.md`: `## [YYYY-MM-DD] lint | <N> findings`

---

## Rules (all subcommands)

- Read `schema.md` at the start of every operation
- Never modify `raw/` files
- Always update `index.md` after any page creation or modification
- Always append to `log.md` after any operation
- Use `[[wikilinks]]` for all cross-references (Obsidian-compatible)
- YAML frontmatter on every wiki page (title, tags, sources, created, updated)
- Filenames: lowercase, hyphenated (e.g., `bottleneck-rotation.md`)
