# Testing Rules

**Applies when:** writing or editing tests, or configuring the test runner.

Source: GENERAL_CLAUDE.md § Testing Rules.

Discover test runner from project (Jest, Vitest, pytest, go test, cargo test, JUnit, etc.).

## Coverage thresholds (when measured)

| Metric | Min |
|--------|-----|
| branches | 80% |
| functions | 85% |
| lines | 85% |
| statements | 85% |

## Required test types

**Unit:** services (mock repos), utilities, schema validators, RBAC guards per role.

**Integration:** API happy paths, auth flow end-to-end, RBAC, rate limits.

**Security:** injection attempts, token tampering, expiry, refresh reuse detection.

## Execution

- Project-documented test command
- Same runtime context as CI when documented
- Deterministic — mock external services
