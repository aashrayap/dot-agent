---
name: grill-me
description: Pressure-test a plan or design one question at a time until the risky branches are resolved. Use when the user asks to be grilled, wants a plan stress-tested, or when `spec-new-feature` reaches a checkpoint with unresolved tradeoffs.
---

# Grill Me

## Composes With

- Parent: direct user request to stress-test a plan or `spec-new-feature` when a checkpoint still has unresolved branches.
- Children: none.
- Uses format from: none.
- Reads state from: current plan, design notes, feature artifacts, and repo docs/code when a question is factual.
- Writes through: none; the parent workflow records resolved answers in its own artifact or notes.
- Hands off to: none.
- Receives back from: none.

Ask one question at a time. For each question:

1. pressure-test one concrete branch, assumption, or failure mode
2. offer a recommended answer when you have one
3. inspect the codebase instead of asking when the answer is factual
4. keep going until the risky branches are either resolved or clearly called out

Do not turn this into a full planning workflow. `grill-me` is a checkpoint
skill, not the owner of the feature artifact set.
