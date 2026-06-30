# Optional Modules

**Applies when:** building optional integrations, plugins, or pluggable modules.

Source: GENERAL_CLAUDE.md § Optional Modules.

Core app must boot when optional integrations are unconfigured or upstream is down.

## Required patterns

- Module contract (e.g. AppModuleDefinition); central registry
- `isEnabled()` from config only — no network at startup
- `checkHealth()` at request time — never throw during boot
- Lazy handler/controller instantiation
- Optional env vars default empty — not required for core boot
- API: capability list + per-module health endpoints
- 503 NOT_CONFIGURED when disabled; 502 UPSTREAM_ERROR when upstream fails

## Forbidden

- Import-time upstream connections
- Throwing during import/register/router creation when not configured
- Required env vars for optional features in core schema
- Hard-coded nav without capability gating (when UI exists)

## New module checklist

module definition, config/isEnabled, health probe, routes factory, registry entry, nav entry (if UI), .env.example + API_REFERENCE docs.
