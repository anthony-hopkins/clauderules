# Documentation Rules

**Applies when:** writing or updating project documentation, or whenever a change alters behavior or structure.

Source: GENERAL_CLAUDE.md § Documentation Rules.

## Mandatory files (user-facing systems)

README.md, USER_GUIDE.md, API_REFERENCE.md, ARCHITECTURE.md, CHANGELOG.md, RUNBOOK.md.

Libraries/CLIs: README required; others with user approval.

## Synchronization

Behavior changes → update relevant docs in same PR.
New env vars → .env.example + README.
API changes → API_REFERENCE.md.
Auth/security → README + RUNBOOK.

## Comments

- File headers: purpose, scope, dependencies
- Exported symbols: intent, inputs, outputs, failure modes
- Comment business rules and non-obvious tradeoffs only

## PR documentation checklist

- [ ] README updated for setup/structure/behavior
- [ ] USER_GUIDE for UX changes
- [ ] API_REFERENCE for endpoint changes
- [ ] ARCHITECTURE for boundary changes
- [ ] CHANGELOG entry
- [ ] Headers/doc comments on new/modified files
