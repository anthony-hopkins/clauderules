# Rust Rules

**Applies when:** editing Rust (`.rs`).

Source: GENERAL_CLAUDE.md § Language & Type Safety Rules.

- Deny warnings in CI unless documented
- No unwrap/expect in production paths without justification comment
- Clippy clean per project configuration
- Explicit error types (Result) — no silent failures
