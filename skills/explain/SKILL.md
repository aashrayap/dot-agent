---
name: explain
description: >
  Visual-first explanations of code, concepts, architectures, or systems.
  Always leads with an ASCII diagram, table, or tree before prose.
  Automatically selects the right visual format based on the question type.
  Use when the user types "/explain" followed by a topic or question.
argument-hint: <topic, question, or file path>
disable-model-invocation: true
---

# Explain Skill

## Composes With

- Parent: user explanation request; `visual-reasoning` when explanation is part of a grouped visual thinking workflow; `compare` when it needs visual Compare/Delta structure.
- Children: `excalidraw-diagram` when an explanation should become a durable rendered visual artifact.
- Uses format from: `excalidraw-diagram` for durable workflow, architecture, or before/after diagrams when useful.
- Reads state from: requested code, docs, files, or provided context.
- Writes through: none.
- Hands off to: none.
- Receives back from: none.

You produce visual-first explanations. Every explanation leads with a structural visual (ASCII diagram, table, tree, or flow chart) before any prose. The prose that follows adds the "so what" — it never restates what the visual already shows.

For durable human-facing explanations, especially architecture, workflow, or
before/after models, prefer an Excalidraw artifact over an ASCII-only diagram
when the user will likely reuse or review the drawing later.

## Routing

Parse `$ARGUMENTS` to determine the explanation type and visual format:

| Question Shape | Format Mode | Visual Lead | Example |
|---|---|---|---|
| "How does X work?" / mechanism / data flow | **Flow** | Box-and-arrow flow diagram showing stages, data movement, or control flow | "explain how /report generates output" |
| "What is X?" / concept / definition | **Zoom** | Layered summary: 1-line definition, then component breakdown table | "explain HBM supercycle" |
| "Why does X matter?" / significance / cause-effect | **Cascade** | Cause-effect chain — vertical cascade or timeline showing consequences | "explain why COHR is in every fund" |
| "How is X structured?" / anatomy / layout | **Tree** | Annotated file/component tree + role table | "explain the semi-stocks repo layout" |
| "X vs Y" / comparison / tradeoffs | **Compare** | Side-by-side box diagrams + comparison table | "explain pluggable vs CPO optics" |
| "What changed?" / diff / evolution | **Delta** | Before/after columns or timeline showing what moved | "explain what changed in Q1 2026 positions" |

If the question doesn't clearly fit one mode, default to **Flow** for processes or **Zoom** for static things.

## Output Structure

Every explanation follows this skeleton. Sections scale with complexity — a simple concept might be 20 lines total, an architecture walkthrough might be 80.

### 1. Title Line

One line. The question being answered, reframed as a declarative statement.

```
How /report builds the HTML output
```

### 2. Visual Lead

The primary diagram. This is the centerpiece. It should be understandable on its own without reading the prose.

**Format rules for ASCII visuals:**
- Use box-drawing characters: `┌ ┐ └ ┘ │ ─ ├ ┤ ┬ ┴ ┼`
- Arrows: `→ ← ↑ ↓ ▶ ▼`
- Keep width under 100 characters for terminal readability
- Label every box and arrow — no mystery nodes
- Use whitespace generously; dense diagrams defeat the purpose

### 3. Key Takeaways

2-5 bullets. Each one adds context the visual can't convey: why a design choice was made, what's non-obvious, what the gotcha is. These are insights, not descriptions of what the diagram shows.

### 4. Detail Table (optional)

When the explanation involves multiple components, stages, or options, add a table that gives each one a row with structured detail. Use table headers appropriate to the format mode:

| Format Mode | Suggested Columns |
|---|---|
| Flow | Stage, Input, Output, Key Logic |
| Zoom | Component, Role, Depends On |
| Cascade | Event, Effect, Timeframe |
| Tree | Path, Purpose, Key Files |
| Compare | Dimension, Option A, Option B, Verdict |
| Delta | Aspect, Before, After, Why |

### 5. Prose Closer (optional)

Only if there's a "so what" that doesn't fit in bullets or tables. 2-4 sentences max. Common uses:
- The core insight that ties everything together
- A recommendation or implication for the user's specific context
- A pointer to where to go deeper

**Never include** a prose closer that just summarizes what was already shown. If the visual + takeaways + table said it all, stop there.

## Depth Calibration

Match depth to scope. Don't over-explain simple things or under-explain complex ones.

| Signal | Depth |
|---|---|
| Single function or small concept | **Light** — 1 visual + 2-3 takeaways, no table |
| Module, service, or medium concept | **Standard** — full skeleton as above |
| Full architecture, multi-system, or comparison | **Deep** — larger visuals, full tables, prose closer |

If the user asks for more detail after an explanation, go one level deeper on the specific area they point to — don't re-explain the whole thing.

## Format Mode Details

### Flow (mechanism / "how does X work")

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Input   │────▶│ Process  │────▶│  Output  │
│          │     │          │     │          │
└──────────┘     └────┬─────┘     └──────────┘
                      │
                      ▼
               ┌──────────┐
               │ Side     │
               │ Effect   │
               └──────────┘
```

- Show the happy path first, then branches/error paths if relevant
- Label arrows with what flows between stages (data type, event name, etc.)
- Annotate boxes with brief parenthetical when the name isn't self-explanatory

### Zoom (concept / "what is X")

Lead with a one-line definition, then break down components:

```
HBM (High Bandwidth Memory): stacked DRAM dies connected via through-silicon vias,
delivering 3-10x bandwidth vs standard DDR5.

┌─────────────────────────────────────────┐
│              HBM Stack                  │
├─────────────┬───────────────────────────┤
│ Layer       │ Role                      │
├─────────────┼───────────────────────────┤
│ Logic die   │ Controller + PHY          │
│ DRAM die x8 │ Capacity (each 2-4 GB)   │
│ TSVs        │ Vertical interconnect     │
│ Interposer  │ Connects stack to GPU     │
└─────────────┴───────────────────────────┘
```

### Cascade (significance / "why does X matter")

Vertical cause-effect chain. Each level shows the consequence of the level above.

```
  Trigger: NVIDIA cuts HBM3e orders by 20%
           │
           ▼
  ┌─ First-order ──────────────────────────┐
  │ SK Hynix revenue miss Q3              │
  └────────────────────────┬───────────────┘
                           ▼
  ┌─ Second-order ─────────────────────────┐
  │ HBM capex cycle questioned            │
  │ Micron, Samsung also derate           │
  └────────────────────────┬───────────────┘
                           ▼
  ┌─ Third-order ──────────────────────────┐
  │ Semiconductor ETFs reprice the entire  │
  │ memory supercycle thesis               │
  └────────────────────────────────────────┘
```

### Tree (anatomy / "how is X structured")

Annotated directory or component tree, followed by a role table.

```
semi-stocks/
├── data/
│   ├── sources/          ← raw analyst YAML
│   │   ├── leopold/
│   │   ├── baker/
│   │   └── semianalysis/
│   └── thesis.yaml       ← compiled investment thesis
├── src/
│   ├── synthesis.py      ← merges sources into analysis
│   └── report.py         ← generates HTML output
└── output/
    └── latest.html       ← the deliverable
```

### Compare (comparison / "X vs Y")

Side-by-side boxes for high-level shape, then a comparison table for specifics.

Use the side-by-side box format from the example the user showed — two `┌─ NAME ─┐` columns with annotations between them. Follow with a table:

```
┌────────────┬───────────────────┬───────────────────┬─────────┐
│ Dimension  │ Option A          │ Option B          │ Verdict │
├────────────┼───────────────────┼───────────────────┼─────────┤
│ ...        │ ...               │ ...               │ ...     │
└────────────┴───────────────────┴───────────────────┴─────────┘
```

### Delta (evolution / "what changed")

Before/after columns or a timeline. Highlight what moved and why.

## Context Gathering

Before generating the explanation:

1. **If the topic references code or files in the current project**: Read the relevant files first. Ground the explanation in actual implementation, not assumptions.
2. **If the topic is a general concept**: Use your training knowledge. No need to search.
3. **If the topic spans multiple files or systems**: Use an Explore agent to gather context before generating the visual.

Never guess at implementation details when the code is available to read.

## Rules

- Visual first, always. No explanation should start with a paragraph.
- Concise. The visual does the heavy lifting. Prose supplements, never duplicates.
- No filler, no praise, no "great question."
- Use exact names from the codebase — function names, file paths, config keys.
- Width under 100 chars for all ASCII art.
- Tables use box-drawing characters, not markdown pipes, for complex tables. Markdown pipes are fine for simple 2-3 column tables.
- If the user's question is ambiguous, pick the most likely interpretation and answer it. Don't ask clarifying questions unless genuinely unable to proceed.
