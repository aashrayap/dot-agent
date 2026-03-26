---
name: qa
description: Live app smoke test using Chrome. Hits every route, reads console errors, checks network failures, identifies issues, and fixes them with user approval.
---

# QA

Live runtime smoke test via Chrome browser automation. Navigates every route, captures console errors and network failures, identifies broken UI, then offers to fix.

## Triggers

- `qa`, `smoke test`, `test the app`
- `check the app`, `is the app working`

## Prerequisites

- App must be running (use the project's dev server command)
- Chrome must be open with the Claude extension active

## Protocol

### Phase 1: Setup

1. Read project docs (architecture.md or CLAUDE.md) to get the current route list.
2. Call `mcp__claude-in-chrome__tabs_context_mcp` to get browser state.
3. Check if the app is already open. If not, create a new tab to the project's dev URL.

### Phase 2: Route Sweep

For each route in the app:

1. Navigate to the route using `mcp__claude-in-chrome__navigate`.
2. Wait for page load.
3. Read console messages with `mcp__claude-in-chrome__read_console_messages` — filter for `error` and `warn` levels.
4. Read network requests with `mcp__claude-in-chrome__read_network_requests` — flag any 4xx/5xx responses.
5. Read the page with `mcp__claude-in-chrome__read_page` — check for:
   - Blank/empty page content (render failure)
   - Error boundary messages ("Something went wrong", "Unhandled Runtime Error", etc.)
   - Missing data indicators (empty tables/lists that should have data)
6. Take a screenshot for the report if issues are found.

### Phase 3: API Health

For each API route discovered in the project:

1. Determine the HTTP method (GET routes only — don't mutate data).
2. Hit the endpoint via the browser or fetch and check for non-200 responses.
3. Log response status and any error bodies.

### Phase 4: Report

Output a findings table to conversation:

```
## QA Report — YYYY-MM-DD

### Summary
- Routes tested: N
- API endpoints tested: N
- Issues found: N (X critical, Y warnings)

### Findings
| Route/Endpoint | Type | Severity | Detail |
|----------------|------|----------|--------|
| /health        | Console Error | CRITICAL | TypeError: Cannot read property 'map' of undefined |
| /api/signals   | Network       | WARNING  | 500 on GET |

### Console Output (condensed)
- /route: N errors, M warnings
- ...
```

### Phase 5: Fix

After presenting the report:

1. Ask user which issues to fix (or "all").
2. For each approved fix:
   - Read the relevant source file.
   - Diagnose the root cause from the error + code.
   - Apply the fix.
   - Re-test the specific route/endpoint in Chrome to verify.
3. After all fixes, do a quick re-sweep of affected routes to confirm.

## Rules

- **Don't mutate data**: only GET requests for API testing. Never POST/PUT/DELETE during QA.
- **Don't fix without asking**: always present findings first, get approval.
- **Use Chrome tools**: this is runtime testing, not static analysis. The app must be running.
- **Severity levels**:
  - `CRITICAL`: Console errors, 5xx responses, render failures, unhandled exceptions
  - `WARNING`: Console warnings, empty data states, 4xx responses
  - `INFO`: Deprecation notices, slow loads, minor UI issues
- **Skip noise**: filter out known benign console messages (React DevTools, HMR, favicon 404s).
- **If app isn't running**: tell the user to start it and stop. Don't try to start it yourself.
- **Re-test after fix**: always verify the fix by re-navigating to the affected route.
- **Keep report concise**: group similar errors, don't dump raw stack traces unless asked.
