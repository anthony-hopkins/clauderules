# CLAUDE.md Rules Guide

This repository contains **CLAUDE.md**, the authoritative rules file for AI-assisted development on an enterprise Node.js fullstack application. The rules are **mandatory and non-negotiable**: they are not suggestions, style preferences, or guidelines to approximate. Any AI agent (Claude, Cursor, or similar) working on a project governed by this file must follow every rule exactly. When a rule is ambiguous or conflicts with a task, work stops until a human clarifies—never proceed on a best guess.

This README explains **what** each section of `CLAUDE.md` requires, **why** it exists, and **how** humans and agents should use it. For the literal rule text, always refer to [CLAUDE.md](./CLAUDE.md).

---

## Table of Contents

1. [Glossary](#glossary)
2. [How to Use This Document](#how-to-use-this-document)
3. [Authority and Enforcement](#authority-and-enforcement)
4. [Prime Directives](#prime-directives)
5. [Clarification Protocol](#clarification-protocol)
6. [Correction & Memory Protocol](#correction--memory-protocol)
7. [Deployment Configuration Protocol](#deployment-configuration-protocol)
8. [Design System & Color Tokens](#design-system--color-tokens)
9. [Project Structure](#project-structure)
10. [Runtime Model](#runtime-model)
11. [Authentication & Security](#authentication--security)
12. [RBAC](#rbac)
13. [Security Headers, Input Security & Rate Limiting](#security-headers-input-security--rate-limiting)
14. [Architecture Rules](#architecture-rules)
15. [Optional Modules](#optional-modules)
16. [TypeScript Rules](#typescript-rules)
17. [Database Rules](#database-rules)
18. [API Design Rules](#api-design-rules)
19. [Frontend Rules](#frontend-rules)
20. [Docker Rules](#docker-rules)
21. [Testing Rules](#testing-rules)
22. [CI/CD](#cicd)
23. [Environment Variables](#environment-variables)
24. [Code Quality](#code-quality)
25. [Documentation Rules](#documentation-rules)
26. [Security Checklist](#security-checklist)
27. [Correction Log](#correction-log)
28. [Related Documentation](#related-documentation)

---

## Glossary

| Term | Definition |
|------|------------|
| **Access token** | Short-lived JWT (max 15 minutes) sent in the `Authorization: Bearer` header. Stored in memory only on the client—never in `localStorage` or `sessionStorage`. |
| **AppModuleDefinition** | TypeScript contract for optional integrations (e.g. Open WebUI). Modules register lazily and must not break core API startup when unconfigured. |
| **Asymmetric signing (RS256)** | JWT signing with a private key and verification with a public key. Required for production; HS256 (shared secret) is forbidden for production tokens. |
| **Audit log** | Immutable-style record of security-relevant actions (privilege changes, auth events) stored in PostgreSQL via the `AuditLog` Prisma model. |
| **bcrypt** | Password hashing algorithm. Minimum 12 rounds; never lower. |
| **Controller → Service → Repository** | Mandatory API layering: HTTP handling, business logic, and database access are strictly separated. |
| **CORRECTION ENTRY** | Append-only log entry (`CORRECTION-001`, etc.) recording a user correction so future sessions enforce it without re-asking. |
| **CORS** | Cross-Origin Resource Sharing. Origins must be explicitly allowed via `CORS_ORIGIN`; no wildcard in production. |
| **CSRF** | Cross-Site Request Forgery protection required on all state-changing API endpoints. |
| **cuid** | Collision-resistant unique identifier used as default Prisma `@id` for models. |
| **Docker Compose V2** | Use `docker compose` (space), not legacy `docker-compose` (hyphen). Sole deployment mechanism for api, web, postgres, and redis. |
| **docker-compose.override.yml** | Development overrides merged automatically with `docker-compose.yml` (hot reload, pgAdmin, exposed debug ports). |
| **Family tracking (refresh tokens)** | Detecting reuse of an old refresh token in a rotation chain to revoke the entire token family (reuse-attack mitigation). |
| **HaveIBeenPwned (HIBP)** | External API checked at registration to reject known-compromised passwords. |
| **Helmet** | Express middleware that sets security HTTP headers (CSP, HSTS, X-Frame-Options, etc.). |
| **HTTP-only cookie** | Cookie inaccessible to JavaScript; required for refresh token storage with `Secure` and `SameSite=Strict`. |
| **JWT** | JSON Web Token used for access tokens and embedded role claims; always verified server-side. |
| **MFA / TOTP** | Multi-factor authentication via time-based one-time passwords (RFC 6238), implemented with `otplib` and QR setup via `qrcode`. |
| **Optional module** | Feature integration that may be disabled via env; core auth/users must boot without it. |
| **pnpm workspace** | Monorepo package manager layout (`pnpm-workspace.yaml`) with `apps/api` and `apps/web` packages. |
| **Pre-Deployment Checklist** | Twelve ordered steps in `CLAUDE.md` that must complete before any `docker compose up`. |
| **Prime Directives** | Six top-level rules that override all other instructions, including “never assume intent” and “never deploy without the deployment protocol.” |
| **Prisma** | ORM and migration tool; sole approved database access path except documented raw SQL with review comments. |
| **RBAC** | Role-Based Access Control with roles `admin`, `user`, and `viewer` (with inheritance). |
| **Redis blocklist** | Redis store for invalidated refresh tokens and rate-limit counters. |
| **Refresh token** | Longer-lived JWT (7 days) in an HTTP-only cookie; rotated on every use with family tracking. |
| **Repository layer** | Data access layer: all Prisma calls live here; no business logic. |
| **shadcn/ui** | Copy-in React component library; files under `components/ui/` must not be hand-edited after generation. |
| **Soft delete** | Records marked with `deletedAt` instead of physical removal for user-related data. |
| **Supertest** | HTTP assertion library for API integration tests against Express. |
| **Token family** | Prisma enum grouping token purposes: `REFRESH`, `MFA_CHALLENGE`, `PASSWORD_RESET`, `EMAIL_VERIFICATION`. |
| **Zod** | Schema validation library; single source of truth for request bodies, env vars, and inferred TypeScript types. |
| **Zustand** | Lightweight React client state store (e.g. in-memory access token). |
| **TanStack Query** | Server-state cache and data-fetching for React (v5). |

---

## How to Use This Document

| Audience | Guidance |
|----------|----------|
| **Developers** | Read Prime Directives and Deployment Protocol before any infra change. Use the Glossary when onboarding. Submit corrections via the Correction Protocol so they persist in `CLAUDE.md`. |
| **AI agents** | Treat `CLAUDE.md` as absolute law. Use this README for context only; on conflict, `CLAUDE.md` wins. Stop and emit the Clarification format when blocked. |
| **Reviewers** | Verify PRs against Architecture, Security Checklist, Documentation Rules, and Code Quality sections. |

---

## Authority and Enforcement

`CLAUDE.md` is the **single source of truth** for AI-assisted development. Rule categories carry different authority levels:

| Category | Authority | If violated |
|----------|-----------|-------------|
| Prime Directives | Absolute | Stop all work |
| Deployment Protocol | Absolute | Stop all work |
| Clarification Protocol | Absolute | Ask user; do not guess |
| Correction & Memory | Highest priority | Record correction immediately |
| Security rules | Non-negotiable | Stop and alert user |
| Architecture, TypeScript, Docker, design tokens, code quality, documentation | Mandatory | Do not deviate without explicit user instruction |

Rules must not be interpreted loosely, skipped for convenience, or applied selectively.

---

## Prime Directives

Six directives override **all** other instructions:

1. **Never break or approximate rules** — Full compliance with `CLAUDE.md`, not “close enough.”
2. **Never assume intent** — Uncertainty requires asking the user first.
3. **Stay in scope** — Only change what the user explicitly requested.
4. **Deployment only via protocol** — Every deploy follows the 12-step Pre-Deployment Checklist in order.
5. **Never repeat mistakes** — User corrections become permanent CORRECTION ENTRIES.
6. **User input becomes law** — Behavior-changing instructions gain the same authority as the rules file.

---

## Clarification Protocol

When any trigger applies (ambiguous rule, conflicting rules, uncovered behavior, unclear deployment step, contradicting correction, undefined scope, or required assumption), the agent **must stop** and ask using this exact structure:

```
WARNING: CLARIFICATION REQUIRED — Action Blocked

Task:              [task being attempted]
Blocker:           [rule, ambiguity, or conflict]
Specific Question: [single question that unblocks work]

No work will proceed until this is answered.
```

Best-guess implementation is a **critical violation**.

---

## Correction & Memory Protocol

AI sessions do not retain memory across chats. This protocol makes **`CLAUDE.md` the memory**:

1. Acknowledge the correction.
2. Identify affected section(s).
3. Append a `CORRECTION-[NNN]` entry to the Correction Log (append-only).
4. Update inline rules if the correction changes existing text.
5. Confirm recording to the user.
6. Apply to the current task.
7. Never re-ask resolved items.

Corrections are sequential (`CORRECTION-001`, …), never deleted; superseded entries are marked `Status: SUPERSEDED by CORRECTION-[NNN]`.

---

## Deployment Configuration Protocol

**Every** deployment—new service, redeploy, or single-service rebuild—runs the full checklist:

| Step | Action |
|------|--------|
| 1 | Verify root `.env` exists and all required variables are populated |
| 2 | Validate `docker-compose.yml` structure and service definition |
| 3 | Confirm multi-stage Dockerfiles for `apps/api` and `apps/web` |
| 4 | Health checks on postgres and redis |
| 5 | Explicit `app_network`; no default bridge |
| 6 | No hardcoded secrets; use `${VAR_NAME}` from `.env` |
| 7 | Pinned images (`postgres:16-alpine`, `redis:7-alpine`, `node:20-alpine`, `nginx:alpine`) |
| 8 | Non-root `appuser` in API Dockerfile before `EXPOSE`/`CMD` |
| 9 | `docker compose up -d --build` (never host `pnpm dev` / `node` for services) |
| 10 | Migrations: `docker compose run --rm api pnpm prisma migrate deploy` |
| 11 | Verify health: `docker compose ps` and logs |
| 12 | Report deployed services and status to user |

**Governing files:** `docker-compose.yml` (authoritative), `docker-compose.override.yml` (dev), `.env` (runtime secrets/config), `.env.example` (documentation only).

**Key rules (D-01–D-08):** Compose-only deployment; root `.env` for all consumed variables; V2 CLI syntax; full checklist every time; stop on hardcoded secrets; migrations inside containers; confirm before `docker compose down -v`.

---

## Design System & Color Tokens

UI must use the defined dark theme: navy backgrounds (`#1a1a2e`, `#16213e`, `#0f3460`), neon green primary (`#39FF14`), purple accent (`#9B59B6`), and semantic colors for error/warning/success/info.

- Colors live in `tailwind.config.ts` and CSS variables in `globals.css`—**never** hardcode hex values in components.
- Typography: Inter (sans), JetBrains Mono (mono), 16px base.
- Spacing/radius follow Tailwind defaults; cards use `rounded-xl`; primary elements may use glow shadow `0 0 20px rgba(57,255,20,0.15)`.

---

## Project Structure

Mandatory monorepo layout:

- **`apps/api`** — Express + TypeScript API with `modules/[feature]/` pattern (controller, service, repository, routes, schema, types, test), `middleware/`, `shared/`, Prisma under `prisma/`.
- **`apps/web`** — React 18 + Vite frontend with `features/`, `components/ui/` (shadcn), `lib/`, `providers/`, `router/`.
- **Root** — `docker-compose.yml`, `.env`, docs (`README.md`, `API_REFERENCE.md`, `ARCHITECTURE.md`, etc.), `.github/workflows/`.

Do not deviate from this tree without explicit user instruction.

---

## Runtime Model

| Requirement | Detail |
|-------------|--------|
| Mode | `docker_compose_only` |
| Services | api, web, postgres, redis via Compose |
| Config source | Root `.env` only for runtime |
| Commands | `docker compose up/down/logs/ps/run/exec`; tests via `docker compose run` |
| Forbidden | Running api/web directly on the host |

---

## Authentication & Security

| Concern | Rule |
|---------|------|
| Access token | RS256, 15m max, Bearer header, memory-only client storage |
| Refresh token | RS256, 7d, HTTP-only Secure SameSite=Strict cookie, rotation + family tracking, Redis blocklist |
| Passwords | bcrypt ≥12 rounds, min 12 chars, complexity rules, HIBP breach check on register |
| MFA | TOTP (RFC 6238), encrypted `mfaSecret` (AES-256-GCM), 10 hashed backup codes |
| Sessions | Bind to user-agent + IP, concurrent limits, force-logout endpoints, suspicious login detection |

Symmetric HS256 signing is **not** allowed in production.

---

## RBAC

| Role | Access | Inherits |
|------|--------|----------|
| `admin` | Full system, users, audit logs | `user` |
| `user` | Standard authenticated access to own resources | `viewer` |
| `viewer` | Read-only where permitted | — |

- Roles appear in JWT claims **and** are re-verified server-side every request.
- `authenticate` middleware always runs before `authorize`.
- Resource ownership checks are separate from role checks.
- Privilege escalation attempts are audit-logged.

---

## Security Headers, Input Security & Rate Limiting

**Helmet** must set CSP (strict, no `unsafe-inline`), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, Referrer-Policy, Permissions-Policy, and HSTS.

**Input:** All bodies validated with Zod; strip unknown fields; DOMPurify (frontend) and xss-clean (backend); Prisma-only queries unless raw SQL has review comment; server-side MIME validation for uploads.

**Rate limits** (Redis-backed):

| Tier | Window | Max |
|------|--------|-----|
| Auth endpoints | 15m | 10 |
| General API | 1m | 100 |
| Authenticated API | 1m | 300 |

Progressive delays and IP blocking after repeated violations are enabled.

---

## Architecture Rules

Strict dependency direction: **Controller → Service → Repository → Prisma**.

| Layer | May do | Must not do |
|-------|--------|-------------|
| **Controller** | Parse/validate request, call service, format response | Business logic, Prisma, direct `throw` (use `next(error)`) |
| **Service** | Business rules, orchestrate repositories, transactions | Touch `req`/`res`, use Prisma directly, send HTTP responses |
| **Repository** | Queries, mapping, optimization | Business logic, call other repositories directly |

---

## Optional Modules

Integrations (e.g. Open WebUI) are **optional**: core auth and users must start even when a module is missing or upstream is down.

**Required patterns:**

- Implement `AppModuleDefinition`; register via `registerAppModule()`.
- `isEnabled()` checks env only (no network at startup).
- `checkHealth()` probes upstream at request time; never throws during import.
- Lazy instantiation in route handlers.
- Endpoints: `GET /api/v1/modules`, `GET /api/v1/{module}/health`.
- Status codes: `503` when not configured, `502` when upstream fails.

**Web:** Nav entries in `module-nav.ts`; sidebar shows disabled modules with a badge; use `useModules()` / `useModule()` for discovery.

**Forbidden:** Import-time throws, required env vars for optional integrations, eager upstream connections in constructors.

---

## TypeScript Rules

Strict mode with `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, explicit return types on exports, Zod-inferred types, and no `any`.

**Forbidden:** `process.env` direct access (use `config/env.ts`), `console.log` in production, `@ts-ignore`, careless `as` casts and `!` assertions.

**Module resolution:** `"bundler"` (Vite web), `"node16"` (API).

---

## Database Rules

- Every model: `id` (cuid), `createdAt`, `updatedAt`.
- User data: soft delete via `deletedAt`.
- Explicit FKs with `onDelete`; indexes on FKs and hot columns.
- Enums in schema for roles/status.
- Never return `passwordHash` or `mfaSecret` by default.
- Paginate lists (default 20, max 100); use `$transaction` for multi-step writes.

Base schema requires `User`, `Session`, and `AuditLog` models as documented in `CLAUDE.md`.

---

## API Design Rules

- Version prefix: `/api/v1/`.
- Success: `{ success: true, data, meta? }` (`meta` only for pagination).
- Error: `{ success: false, error: { code, message, details } }`.
- Auth routes: register, login, logout, refresh, MFA setup/verify/challenge/disable/backup, password reset, email verify, session management.
- Security: constant-time login responses, token expiry rules, CSRF on state-changing routes, auth rate limits.

---

## Frontend Rules

| Area | Stack / rule |
|------|----------------|
| Core | React 18, Vite, TypeScript, Tailwind v3, shadcn/ui |
| State | Zustand (client), TanStack Query v5 (server) |
| Routing | React Router v6 with `ProtectedRoute` and `RoleGuard` |
| Forms | React Hook Form + Zod; inline errors; no `alert()` |
| HTTP | Axios with refresh interceptor; `withCredentials: true` |
| UX | Loading/skeleton/empty states; aria labels; 4.5:1 contrast; do not disable submit—validate inline |

Tailwind and `globals.css` templates in `CLAUDE.md` are canonical; shadcn init uses custom styling (no default shadcn theme).

---

## Docker Rules

- Multi-stage builds; non-root runtime for API.
- Pinned base images; health checks for postgres/redis.
- Secrets only in `.env`; explicit `app_network`.
- Production web served via nginx; development override mounts source and runs `pnpm dev` on ports 3001 (api) and 8000 (web).
- pgAdmin available in override for local DB administration.

Reference `docker-compose.yml`, `docker-compose.override.yml`, and Dockerfiles in `CLAUDE.md` when implementing.

---

## Testing Rules

**Framework:** Jest + ts-jest + Supertest.

| Type | Coverage |
|------|----------|
| Unit | Services (mocked repos), utilities, Zod schemas, RBAC middleware |
| Integration | API happy paths, full auth flow, RBAC, rate limits |
| Security | SQL injection attempts, JWT tampering, expiry, refresh reuse |

**Thresholds:** branches 80%, functions/lines/statements 85%. Run tests via `docker compose run --rm api pnpm test`.

---

## CI/CD

**CI** (on PR to `main`/`develop` and push to `develop`):

- Lint and typecheck across workspace.
- API tests with service containers for postgres/redis.
- Security audit (`pnpm audit`) and Trivy filesystem scan (CRITICAL/HIGH).

**Deploy** (on push to `main`):

- Build Docker images via Compose.
- Run Prisma migrations inside api container.

---

## Environment Variables

| File | Purpose |
|------|---------|
| `.env` | Runtime secrets and config (Compose injects into services) |
| `.env.example` | Documented template; not used at runtime |

Required groups: PostgreSQL, Redis, JWT key pairs (base64 RS256), MFA encryption key (64 hex chars), CORS, bcrypt rounds, rate limits, `VITE_API_URL`, optional SMTP and HIBP.

API validates via Zod in `apps/api/src/config/env.ts`—invalid env causes process exit.

---

## Code Quality

| Rule | Limit |
|------|-------|
| Function length | ≤40 lines |
| File length | ≤300 lines |
| Cyclomatic complexity | ≤10 per function |
| TODOs | `// TODO(name): description - Issue #XXX` |
| Commits | Conventional Commits (`feat`, `fix`, `security`, etc.) |

PR checklist covers tests, lint, secrets exposure, env documentation, migration compatibility, and security review.

---

## Documentation Rules

Mandatory project docs (when application code exists):

| File | Contents |
|------|----------|
| `README.md` | Setup, architecture, conventions |
| `USER_GUIDE.md` | End-user flows |
| `API_REFERENCE.md` | Endpoints and errors |
| `ARCHITECTURE.md` | Boundaries and diagrams |
| `CHANGELOG.md` | Release notes |
| `RUNBOOK.md` | Operations and incidents |

Behavior changes require synchronized doc updates in the same PR. Source files need header comments; exported symbols need doc comments describing intent and failure modes.

---

## Security Checklist

Pre-release blocker checklist in `CLAUDE.md` covering:

- **Authentication:** RS256, token lifetimes, rotation, bcrypt, MFA encryption, lockout.
- **API:** Auth middleware, rate limits, Zod validation, CORS, Helmet, safe errors, Prisma parameterization.
- **Infrastructure:** Non-root containers, env-based secrets, dependency audit, pinned images, DB/Redis not exposed insecurely.

Every unchecked item blocks release.

---

## Correction Log

Located at the bottom of `CLAUDE.md`. Starts empty; accumulates `CORRECTION-001`, `CORRECTION-002`, … as users correct agent behavior. Entries are append-only and enforceable at the same level as Prime Directives. Check here first when onboarding to a project with prior AI sessions.

---

## Related Documentation

| Document | Role |
|----------|------|
| [CLAUDE.md](./CLAUDE.md) | Authoritative rules (this README summarizes it) |
| `QUICK_START.md` | Fast bootstrap (when project scaffold exists) |
| `API_REFERENCE.md` | HTTP contracts |
| `ARCHITECTURE.md` | System design |
| `RUNBOOK.md` | Operations |

When implementing an application from these rules, copy `CLAUDE.md` to the project root and keep this README alongside it so humans and agents share the same understanding of enforcement, deployment, and security expectations.
