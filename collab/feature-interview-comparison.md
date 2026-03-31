Last compared: 2026-03-31
Sources: ash-feature-interview.md (populated), bryce-feature-interview.md (populated)

# Compare: Ash vs Bryce

## Philosophy
- **Ash**: Multi-window context isolation with parallel classified subagents, full lifecycle through execution + verification + shipping code. Output = working software.
- **Bryce**: TA workflow for decomposing ADO features into user stories with acceptance criteria, persistent knowledge base, and retrospective loop. Output = ADO stories + organizational learning.

## Structure Map

| # | Ash | Bryce |
|---|-----|-------|
| 1 | Generate Research Questions — human approves | Generate Research Questions — reads knowledge base first, fetches ADO parent/comments/attachments, asks for supplemental context |
| 2 | Parallel Research — 5 agent types (codebase/docs/patterns/external/cross-ref) in waves, structured return schema per question | Single Research Subagent — traces shared dependencies, excludes test automation, surfaces boundaries + risk indicators |
| 3 | Design Discussion — alignment + conflict agents pre-digest, then human locks decisions + verification strategy + tracer bullet structure | Analysis Discussion — decision frameworks (pareto, inversion, etc.), story decomposition by boundary, impact area with risk levels, tester notes, context budget (~30 exchanges) |
| 4 | Write Spec — subagent writes self-contained spec (10 sections), orchestrator summarizes for approval | Story Draft + ADO Creation — creates user stories in ADO with HTML descriptions, links parent/predecessor relations |
| 5 | Execute — wave-based parallel subagents, file-disjoint tasks, atomic commits | Retrospective — separate invocation, compares plan vs actual, updates knowledge base |
| 6 | Verify — tier 1 parallel (slop/scope/build), tier 2 sequential (chrome/criteria/fix loop) | — |
| 7 | Ship — doc-sync subagent, mark shipped, push | — |

## Key Divergences

1. **End goal**: Ash ships code; Bryce ships ADO stories. Ash's is a full dev pipeline; Bryce's is a TA/planning tool that hands off to developers.
2. **Knowledge persistence**: Bryce maintains `ta-knowledge-base.md` (domain corrections, process learnings, recurring edge cases) that accumulates across all features. Ash treats each feature as independent — no cross-feature memory.
3. **Research architecture**: Ash classifies questions into 5 agent types with wave-based parallelism and a structured return schema (answer/confidence/evidence/conflicts/open). Bryce uses a single subagent but adds shared dependency tracing, boundary detection, and risk indicators.
4. **Artifact lifecycle**: Bryce explicitly deletes ephemeral artifacts (questions.md, research.md) after Phase 4 and analysis.md after retro. Ash keeps all artifacts indefinitely.
5. **Decision frameworks**: Bryce embeds named mental models (pareto, inversion, second-order, etc.) into Phase 3 with guidance on when to apply each. Ash relies on the human + pre-digestion agents without named frameworks.

## Shared DNA

- Context decontamination — user input excluded from the research phase
- Human approval gates before advancing phases
- Decision tables with locked/TBD status that must be fully resolved before proceeding

## Steal List

**Ash should consider from Bryce:**
- Knowledge base that persists domain corrections and process learnings across features
- Retrospective phase comparing planned vs actual outcomes with feedback loop
- Decision frameworks embedded in the design discussion phase

**Bryce should consider from Ash:**
- Multi-agent research with classified question types and wave-based parallelism
- Structured per-question return schema (confidence, evidence, conflicts fields)
- Pre-digestion agents (alignment + conflict) before the human design discussion
