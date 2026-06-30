# Node Testing & CI/CD Rules

**Applies when:** writing Node tests (Jest/Supertest) or editing `jest.config.*` or `.github/workflows/**`.

Project-specific rules. Source: CLAUDE.md §§ Testing Rules, CI/CD. Generic versions: `testing.md`, `ci-cd.md`.

## Framework

Jest + ts-jest + Supertest. `moduleNameMapper` `^@/(.*)$` → `<rootDir>/src/$1`. Coverage excludes
`*.d.ts`, `server.ts`, `config/**`.

## Coverage thresholds

branches 80, functions 85, lines 85, statements 85.

## Required tests

- **Unit:** service methods (mock repository), utilities, Zod schemas (valid + invalid), RBAC middleware per role.
- **Integration:** endpoint happy paths, auth flow (register → login → MFA → refresh → logout), RBAC enforcement, rate limiting.
- **Security:** SQL injection attempts, JWT tampering, expired-token rejection, refresh rotation + reuse detection.

Run tests via `docker compose run --rm api pnpm test`.

## CI (`.github/workflows/ci.yml`)

On PR to `main`/`develop` and push to `develop`:
- `lint-typecheck`: `pnpm -r lint`, `pnpm -r typecheck`.
- `test-api`: postgres + redis service containers, `prisma migrate deploy`, `pnpm --filter api test:coverage`.
- `security-scan`: `pnpm audit --audit-level=high`, Trivy fs scan (CRITICAL/HIGH).

## Deploy (`.github/workflows/deploy.yml`)

On push to `main`: build images via `docker compose build`, run Prisma migrations inside api container.
