---
name: dvn-web-libraries
description: Guide for using @devonenergyenterprise shared NPM packages (core-utils, service-utils, ag-grid-presets, ui-react, telemetry). Use when working with Devon Energy frontend projects that use these libraries, when writing React components with AG Grid, service hooks, date/string utilities, or Chakra UI wrappers.
---

# DVN Web Libraries

Answer questions about and guide usage of `@devonenergyenterprise` shared packages. Use the baked-in references for most questions. For source-level detail, fetch from GitHub.

## Workflow

1. Check `package.json` for installed `@devonenergyenterprise/*` packages and versions
2. Route to the correct module reference below
3. Use examples verbatim — never fabricate API signatures
4. When multiple modules solve a problem together, show them composed
5. Include `npm install` with peer deps when recommending a package for the first time

## Module Routing

| Package | NPM | Latest | Use For | Reference |
|---------|-----|--------|---------|-----------|
| `core-utils` | `@devonenergyenterprise/core-utils` | 0.2.7 | Date, string, collection utilities | `references/core-utils.md` |
| `service-utils` | `@devonenergyenterprise/service-utils` | 0.2.8 | React Query v5 hooks (query, mutation, on-demand) | `references/service-utils.md` |
| `ag-grid-presets` | `@devonenergyenterprise/ag-grid-presets` | 0.1.7 | AG Grid config, state persistence, filters, Chakra UI theming | `references/ag-grid-presets.md` |
| `ui-react` | `@devonenergyenterprise/ui-react` | 0.1.2 | Chakra UI wrapper components (Tooltip) | `references/ui-react.md` |
| `telemetry` | `@devonenergyenterprise/telemetry` | 0.0.4 | Application Insights tracking | `references/telemetry.md` |

Read the appropriate reference file(s) based on the user's question.

## Fetching Deeper Detail

If a reference file doesn't cover what's needed:

```bash
gh api repos/DevonEnergyEnterprise/dvn-web-libraries/contents/{module}/README.md --jq '.content' | base64 -d
gh api repos/DevonEnergyEnterprise/dvn-web-libraries/contents/{module}/src/{file} --jq '.content' | base64 -d
gh api repos/DevonEnergyEnterprise/dvn-web-libraries/commits?path={module}&per_page=5
```

## Cross-Module Patterns

Read `references/cross-module-patterns.md` for composed examples (AG Grid + core-utils dates, truncated cells with tooltips, search with filtering, full grid setup).

## Installation

Read `references/installation.md` for auth setup, npm install, and Azure Pipelines config.

## Rules

- Use examples from references verbatim — never fabricate API signatures or options
- When multiple modules solve a problem together, show them composed
- Always include `npm install` command with peer deps when recommending a package for the first time
- If the reference doesn't cover it, fetch from GitHub before answering
- Always end with: Full docs: https://github.com/DevonEnergyEnterprise/dvn-web-libraries/tree/master/{module}
