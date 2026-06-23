# AI Rules Guide

This repository provides authoritative rules for AI-assisted development (Cursor, Claude Code, and similar agents). Rules are **mandatory and non-negotiable** when active: not suggestions to approximate. When a rule is ambiguous, work stops until a human clarifies—never proceed on a best guess.

## Repository layout

```
claude/
├── GENERAL_CLAUDE.md          # Full stack-agnostic rules (reference)
├── GENERAL_CLAUDE_CORE.md     # Always-on slim core (~315 lines)
├── CLAUDE.md                  # Full Node.js fullstack rules (reference)
├── RULES_SPLIT.md             # Split architecture design doc
├── README.md                  # This guide
└── .cursor/rules/             # Scoped Cursor rules (20 .mdc files)
    ├── core.mdc               # alwaysApply: true
    ├── deployment.mdc
    ├── auth-security.mdc
    └── …                      # See table below
```

## Three layers (recommended for generic projects)

| Layer | File(s) | When loaded |
|-------|---------|-------------|
| **Always-on core** | `GENERAL_CLAUDE_CORE.md` + `.cursor/rules/core.mdc` | Every agent session |
| **Scoped rules** | `.cursor/rules/*.mdc` (except core) | When matching files are open or in context |
| **Full reference** | `GENERAL_CLAUDE.md` | Human review, rule edits, dispute resolution |

On conflict: **Core > scoped rule > GENERAL_CLAUDE.md examples**.

| File | Use when |
|------|----------|
| **Split pack** (`GENERAL_CLAUDE_CORE.md` + `.cursor/rules/`) | **Recommended** for generic/polyglot projects in Cursor |
| [GENERAL_CLAUDE.md](./GENERAL_CLAUDE.md) | Full single-file reference, or non-Cursor agents |
| [CLAUDE.md](./CLAUDE.md) | Enterprise Node.js fullstack (Compose, Express, React, Prisma) |

**Choose one rules system per project.** Do not load `GENERAL_CLAUDE.md` and `CLAUDE.md` together unless a CORRECTION ENTRY explicitly permits it.

This README explains what each layer requires and **how to install the split pack in a generic project**. For literal rule text, see [GENERAL_CLAUDE.md](./GENERAL_CLAUDE.md) or [GENERAL_CLAUDE_CORE.md](./GENERAL_CLAUDE_CORE.md). For split design rationale, see [RULES_SPLIT.md](./RULES_SPLIT.md).

---

## Table of Contents

1. [Glossary](#glossary)
2. [Using Split Rules in a Generic Project](#using-split-rules-in-a-generic-project)
3. [Scoped Rules Reference](#scoped-rules-reference)
4. [Choosing a Rules File](#choosing-a-rules-file)
5. [How to Use This Document](#how-to-use-this-document)
6. [Authority and Enforcement](#authority-and-enforcement)
7. [Prime Directives](#prime-directives)
8. [Clarification Protocol](#clarification-protocol)
9. [Correction & Memory Protocol](#correction--memory-protocol)
10. [Deployment Configuration Protocol](#deployment-configuration-protocol)
11. [Design System & Color Tokens](#design-system--color-tokens)
12. [Project Structure](#project-structure)
13. [Runtime Model](#runtime-model)
14. [Authentication & Security](#authentication--security)
15. [RBAC](#rbac)
16. [Security Headers, Input Security & Rate Limiting](#security-headers-input-security--rate-limiting)
17. [Architecture Rules](#architecture-rules)
18. [Optional Modules](#optional-modules)
19. [Language & Type Safety Rules](#language--type-safety-rules)
20. [Database Rules](#database-rules)
21. [API Design Rules](#api-design-rules)
22. [Frontend Rules](#frontend-rules)
23. [Container & Infrastructure Rules](#container--infrastructure-rules)
24. [Testing Rules](#testing-rules)
25. [CI/CD](#cicd)
26. [Environment Variables](#environment-variables)
27. [Code Quality](#code-quality)
28. [Documentation Rules](#documentation-rules)
29. [Security Checklist](#security-checklist)
30. [Correction Log](#correction-log)
31. [Related Documentation](#related-documentation)
32. [Rules Split Architecture](#rules-split-architecture)

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
| **GENERAL_CLAUDE.md** | Stack-agnostic rules file; uses project discovery instead of prescribing Node.js or Docker Compose. |
| **Project Discovery Protocol** | Process in GENERAL_CLAUDE.md: identify language, archetype, deploy mechanism, and conventions from the repo before implementing. |
| **Project-documented runtime** | GENERAL_CLAUDE.md runtime mode: use README/RUNBOOK/Makefile/CI commands—never invent alternate paths. |
| **Language & Type Safety Rules** | GENERAL_CLAUDE.md section 15 (replaces stack-specific TypeScript Rules); applies strict typing per detected language. |
| **Container & Infrastructure Rules** | GENERAL_CLAUDE.md section 19; `containers-infra.mdc` when Dockerfile/compose/terraform in context. |
| **GENERAL_CLAUDE_CORE.md** | Always-on slim rules (~315 lines): directives, clarification, correction, abbreviated deploy, architecture, code quality. |
| **Scoped rule (`.mdc`)** | Cursor rule file in `.cursor/rules/` loaded when `globs` match open files. |
| **Split pack** | `GENERAL_CLAUDE_CORE.md` + `.cursor/rules/` — recommended for generic Cursor projects. |
| **core.mdc** | `alwaysApply: true` — injects core summary every session; points to GENERAL_CLAUDE_CORE.md. |

---

## Using Split Rules in a Generic Project

Use this workflow when adopting rules for a **polyglot or existing repo** (Python API, Go CLI, Terraform infra, etc.) in **Cursor**.

### Step 1 — Copy files into your project

From this repository into your project root:

```text
your-project/
├── GENERAL_CLAUDE_CORE.md     ← copy from this repo
├── GENERAL_CLAUDE.md          ← optional but recommended (full reference)
└── .cursor/
    └── rules/                 ← copy entire folder
```

Minimum required for Cursor split: **`GENERAL_CLAUDE_CORE.md`** + **`.cursor/rules/`**.

### Step 2 — Prune scoped rules you do not need

Delete unused language rules to reduce noise. Keep only what your repo uses:

| If your project uses… | Keep | Can remove |
|----------------------|------|------------|
| TypeScript only | `lang-typescript.mdc` | `lang-python`, `lang-go`, `lang-rust`, `lang-java` |
| Python only | `lang-python.mdc` | other `lang-*.mdc` |
| No web UI | `frontend.mdc`, `design-tokens.mdc` | — |
| No containers | `containers-infra.mdc`, `deployment.mdc` | Only if you never deploy via compose/k8s/terraform |
| Library / no HTTP API | `api-design.mdc`, `auth-security.mdc` | — |

Always keep: **`core.mdc`**.

### Step 3 — Verify Cursor picks up rules

1. Open your project in Cursor.
2. Confirm `.cursor/rules/core.mdc` exists with `alwaysApply: true`.
3. In **Cursor Settings → Rules**, verify project rules are enabled.
4. Open a file that matches a scoped glob (e.g. `docker-compose.yml`) and confirm the matching rule appears in context.

No extra configuration is required if `.cursor/rules/` is at the project root.

### Step 4 — Record corrections in the core file

When the agent makes a repeatable mistake:

1. Append a `CORRECTION-[NNN]` entry to **`GENERAL_CLAUDE_CORE.md`** Correction Log.
2. Update the matching section in **`GENERAL_CLAUDE.md`** and the relevant `.mdc` file if the rule is scoped.
3. Do not delete old correction entries.

### Step 5 — Optional: symlink instead of copy

For multiple repos sharing one rules source:

```bash
# From your project root (example paths)
ln -s /path/to/claude/GENERAL_CLAUDE_CORE.md ./GENERAL_CLAUDE_CORE.md
ln -s /path/to/claude/.cursor/rules ./.cursor/rules
```

On Windows, use directory junctions or copy on each rules update.

### What loads when (examples)

| You are working on… | Always-on | Scoped rules likely active |
|--------------------|-----------|----------------------------|
| README typo | `core.mdc` | `documentation.mdc` if README open |
| Login API endpoint | `core.mdc` | `api-design`, `auth-security`, `lang-*` |
| React dashboard | `core.mdc` | `frontend`, `design-tokens`, `lang-typescript` |
| `docker compose up` | `core.mdc` | `deployment`, `containers-infra` |
| Prisma migration | `core.mdc` | `database`, `lang-typescript` |
| GitHub Actions workflow | `core.mdc` | `ci-cd` |

### Single-file alternative (non-Cursor)

If you are not using Cursor scoped rules, copy **`GENERAL_CLAUDE.md`** only and configure your agent to read it as workspace rules. You lose on-demand loading but keep one file to maintain.

---

## Scoped Rules Reference

All files live in [`.cursor/rules/`](./.cursor/rules/).

| File | Loads when working with | Content summary |
|------|-------------------------|-----------------|
| `core.mdc` | **Always** (`alwaysApply: true`) | Prime directives, architecture, code quality summary |
| `deployment.mdc` | compose, Makefile, terraform, k8s, RUNBOOK | Full 12-step deploy, D-01–D-08 |
| `auth-security.mdc` | `auth/`, security middleware | Auth invariants, RBAC, input, rate limits |
| `security-headers.mdc` | middleware, nginx, app entrypoints | CSP, HSTS, frame options |
| `api-design.mdc` | routes, controllers, handlers, OpenAPI | Response envelopes, versioning |
| `database.mdc` | migrations, prisma, models, schema | Schema, queries, pagination |
| `frontend.mdc` | `.tsx`, `.vue`, components, pages | Forms, a11y, loading states |
| `design-tokens.mdc` | tailwind.config, globals.css, theme | Color/typography tokens |
| `containers-infra.mdc` | Dockerfile, compose, k8s, `.tf` | Non-root, pinned images, health checks |
| `testing.mdc` | `*.test.*`, `tests/`, jest/pytest config | Pyramid, 80/85% coverage |
| `ci-cd.mdc` | `.github/workflows`, Jenkinsfile | Lint, test, security scan jobs |
| `environment.mdc` | `.env.example`, config/env | 12-factor, schema validation |
| `optional-modules.mdc` | `modules/`, `integrations/` | Lazy plugins, health probes |
| `documentation.mdc` | README, CHANGELOG, ARCHITECTURE, etc. | Doc sync, comments, PR checklist |
| `security-checklist.mdc` | CHANGELOG, release workflows | Pre-release blocker checklist |
| `lang-typescript.mdc` | `*.ts`, `*.tsx` | strict, Zod, no `any` |
| `lang-python.mdc` | `*.py` | type hints, Pydantic, mypy |
| `lang-go.mdc` | `*.go` | vet, staticcheck, errors |
| `lang-rust.mdc` | `*.rs` | clippy, no unwrap in prod |
| `lang-java.mdc` | `*.java`, `*.kt` | null-safety, bean validation |

---

## Choosing a Rules File

| Criterion | Split pack (recommended) | GENERAL_CLAUDE.md only | CLAUDE.md |
|-----------|--------------------------|------------------------|-----------|
| **Cursor adherence** | Best — core always-on, detail on demand | Good — full file every session | Good for Node monorepo |
| **Stack** | Any language or framework | Any language or framework | Node, Express, React, Prisma |
| **Deployment** | Discovers mechanism | Discovers mechanism | Docker Compose only |
| **Project structure** | Follow existing conventions | Follow existing conventions | Mandatory `apps/api` + `apps/web` |
| **Maintenance** | Core + .mdc files; sync from GENERAL_CLAUDE.md | Single file | Single file |

When starting a **generic or existing repo** in Cursor, use the **split pack**. When starting a **new Node fullstack monorepo** matching the CLAUDE scaffold, use **CLAUDE.md** (Node scoped split not yet implemented).

---

## How to Use This Document

| Audience | Guidance |
|----------|----------|
| **Developers** | Install split pack (see above). Read Prime Directives before infra changes. Record corrections in `GENERAL_CLAUDE_CORE.md`. |
| **AI agents** | Follow `GENERAL_CLAUDE_CORE.md` + active scoped `.mdc` rules. Full reference: `GENERAL_CLAUDE.md`. On conflict: core wins. Use Clarification format when blocked. |
| **Reviewers** | Verify PRs against Architecture, Security Checklist (`security-checklist.mdc`), Documentation (`documentation.mdc`), and Code Quality (core). |

---

## Authority and Enforcement

The active rules system is authoritative for AI-assisted development:

- **Split pack:** `GENERAL_CLAUDE_CORE.md` + `.cursor/rules/`
- **Single file:** `GENERAL_CLAUDE.md` or `CLAUDE.md`

Rule categories carry different authority levels:

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

1. **Never break or approximate rules** — Full compliance with the active rules system, not “close enough.”
2. **Never assume intent** — Uncertainty requires asking the user first.
3. **Stay in scope** — Only change what the user explicitly requested.
4. **Deployment only via protocol** — Every deploy follows the 12-step checklist (`deployment.mdc` when in context).
5. **Never repeat mistakes** — User corrections become CORRECTION ENTRIES in `GENERAL_CLAUDE_CORE.md`.
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

AI sessions do not retain memory across chats. This protocol makes **`GENERAL_CLAUDE_CORE.md` the memory** (or `CLAUDE.md` when using the Node stack):

1. Acknowledge the correction.
2. Identify affected section(s) in core, full reference, or scoped `.mdc`.
3. Append a `CORRECTION-[NNN]` entry to the Correction Log in the **core** file.
4. Update inline rules in `GENERAL_CLAUDE.md` and relevant `.mdc` if applicable.
5. Confirm recording to the user.
6. Apply to the current task.
7. Never re-ask resolved items.

Corrections are sequential (`CORRECTION-001`, …), never deleted; superseded entries are marked `Status: SUPERSEDED by CORRECTION-[NNN]`.

---

## Deployment Configuration Protocol

**Every** deployment runs the full 12-step checklist in order. Both rules files enforce the same sequential logic; they differ in how steps are satisfied.

| Step | GENERAL_CLAUDE.md | CLAUDE.md |
|------|-------------------|-----------|
| 1 | Verify env/config from discovered sources | Verify root `.env` populated |
| 2 | Validate discovered deployment manifest | Validate `docker-compose.yml` |
| 3 | Verify build config (Dockerfile, Makefile, etc.) | Multi-stage Dockerfiles for `apps/api` and `apps/web` |
| 4 | Health checks / readiness probes | Health checks on postgres and redis |
| 5 | Network/connectivity per project mechanism | Explicit `app_network` |
| 6 | No hardcoded secrets | No hardcoded secrets |
| 7 | Pinned versions (images, runtimes, lockfiles) | Pinned postgres/redis/node/nginx images |
| 8 | Least-privilege runtime (non-root, service accounts) | Non-root `appuser` in API Dockerfile |
| 9 | Project-documented deploy command | `docker compose up -d --build` |
| 10 | Project-documented migrations in runtime context | `docker compose run --rm api pnpm prisma migrate deploy` |
| 11 | Post-deploy health via project commands | `docker compose ps` and logs |
| 12 | Report components and status to user | Report services and status to user |

**Key rules (D-01–D-08):** Single authoritative deploy path; env as source of truth; documented CLI; full checklist every time; stop on hardcoded secrets; migrations in runtime context; ask when service type unknown; destructive teardown requires explicit confirmation.

Full deploy detail when editing manifests: **`deployment.mdc`**. Abbreviated checklist always in **`GENERAL_CLAUDE_CORE.md`**.

---

## Design System & Color Tokens

UI must use the defined dark theme: navy backgrounds (`#1a1a2e`, `#16213e`, `#0f3460`), neon green primary (`#39FF14`), purple accent (`#9B59B6`), and semantic colors for error/warning/success/info.

- Colors live in `tailwind.config.ts` and CSS variables in `globals.css`—**never** hardcode hex values in components.
- Typography: Inter (sans), JetBrains Mono (mono), 16px base.
- Spacing/radius follow Tailwind defaults; cards use `rounded-xl`; primary elements may use glow shadow `0 0 20px rgba(57,255,20,0.15)`.

---

## Project Structure

**Generic (split / GENERAL_CLAUDE):** Follow the **Structure Discovery Protocol** in `GENERAL_CLAUDE_CORE.md` — identify layout from manifests, never impose foreign templates. See `documentation.mdc` when editing README.

**Node monorepo (CLAUDE.md):** Mandatory layout:

- **`apps/api`** — Express + TypeScript API with `modules/[feature]/` pattern (controller, service, repository, routes, schema, types, test), `middleware/`, `shared/`, Prisma under `prisma/`.
- **`apps/web`** — React 18 + Vite frontend with `features/`, `components/ui/` (shadcn), `lib/`, `providers/`, `router/`.
- **Root** — `docker-compose.yml`, `.env`, docs (`README.md`, `API_REFERENCE.md`, `ARCHITECTURE.md`, etc.), `.github/workflows/`.

Do not deviate from this tree without explicit user instruction.

---

## Runtime Model

**Generic (split / GENERAL_CLAUDE):** `project_documented_runtime` — discover commands from README, RUNBOOK, Makefile, CI. See `GENERAL_CLAUDE_CORE.md` § Runtime Model.

**Node monorepo (CLAUDE.md):**

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

## Language & Type Safety Rules

**CLAUDE.md** prescribes TypeScript strict mode (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, Zod-inferred types, no `any`).

**GENERAL_CLAUDE.md** generalizes to all languages: detect from manifests, enforce strict typing where supported (TypeScript, Python+mypy, Go vet, Rust clippy, etc.), schema-as-source-of-truth, no unchecked env access, no debug prints in production paths.

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

## Container & Infrastructure Rules

**CLAUDE.md** mandates Docker Compose with multi-stage Dockerfiles, non-root `appuser`, pinned images, `app_network`, and nginx for production web.

**GENERAL_CLAUDE.md** applies container and IaC rules only when the project uses them: non-root containers, pinned images, health checks, secrets via env, explicit networking. Supports Compose, Kubernetes, and Terraform as examples—not requirements.

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

Located at the bottom of **`GENERAL_CLAUDE_CORE.md`** when using the split pack (or `CLAUDE.md` / `GENERAL_CLAUDE.md` for single-file mode). Starts empty; accumulates `CORRECTION-001`, `CORRECTION-002`, … as users correct agent behavior. Entries are append-only and enforceable at the same level as Prime Directives. Check here first when onboarding to a project with prior AI sessions.

---

## Related Documentation

| Document | Role |
|----------|------|
| [GENERAL_CLAUDE_CORE.md](./GENERAL_CLAUDE_CORE.md) | Always-on rules (install in every generic project) |
| [GENERAL_CLAUDE.md](./GENERAL_CLAUDE.md) | Full stack-agnostic reference |
| [CLAUDE.md](./CLAUDE.md) | Node.js fullstack reference |
| [RULES_SPLIT.md](./RULES_SPLIT.md) | Split architecture design and rationale |
| [.cursor/rules/](./.cursor/rules/) | Scoped Cursor rules (install with core) |

### Quick install checklist (generic Cursor project)

- [ ] Copy `GENERAL_CLAUDE_CORE.md` to project root
- [ ] Copy `.cursor/rules/` to project `.cursor/rules/`
- [ ] Optionally copy `GENERAL_CLAUDE.md` for full reference
- [ ] Remove unused `lang-*.mdc` files for your stack
- [ ] Remove `frontend.mdc` / `design-tokens.mdc` if no UI
- [ ] Verify `core.mdc` has `alwaysApply: true`
- [ ] Record future corrections in `GENERAL_CLAUDE_CORE.md` Correction Log

---

## Rules Split Architecture

The split is **implemented** in this repository. Summary:

| Component | Lines (approx.) | Purpose |
|-----------|-----------------|--------|
| `GENERAL_CLAUDE_CORE.md` | ~315 | Always-on: directives, clarification, correction, deploy checklist, discovery, architecture, code quality |
| `.cursor/rules/core.mdc` | ~30 | Cursor `alwaysApply` hook to core |
| `.cursor/rules/*.mdc` (19 scoped) | ~50–80 each | Detail loaded when globs match |
| `GENERAL_CLAUDE.md` | ~1,220 | Complete single-file reference |

**Why split:** Reduces per-session token load (~4k–6k always-on vs ~15k–25k full file) while keeping deployment, auth, and language rules salient when you edit matching files.

**Maintaining rules:** Edit `GENERAL_CLAUDE.md` as the merge target; propagate changes to `GENERAL_CLAUDE_CORE.md` and affected `.mdc` files. See [RULES_SPLIT.md](./RULES_SPLIT.md) for the full section mapping.

**Not yet implemented:** `CLAUDE_CORE.md` + Node-specific scoped pack for `CLAUDE.md` monorepo projects.
