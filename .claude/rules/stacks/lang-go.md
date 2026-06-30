# Go Rules

**Applies when:** editing Go (`.go`).

Source: GENERAL_CLAUDE.md § Language & Type Safety Rules.

- go vet and staticcheck clean in CI
- Never ignore returned errors
- Context propagation for cancellation and deadlines
- Explicit return types on exported functions
- No unchecked type assertions without justification
