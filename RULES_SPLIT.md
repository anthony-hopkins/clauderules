# Rules Split Architecture

How to split `GENERAL_CLAUDE.md` (or `CLAUDE.md`) into **always-on** core rules and **scoped**, read-on-demand rules for better adherence without losing authority.

> **Format note (Claude):** the implemented rules use plain Markdown with **no YAML frontmatter**. The
> always-on core is pulled in via an `@import` in the root `CLAUDE.md` (`@.claude/rules/core.md`), and
> every other file opens with an **"Applies when"** line that tells the agent when to read it. The
> `globs:` strings shown in the examples below are kept only as a reference for *which paths each rule
> concerns* — they are expressed as that "Applies when" line in each file, not as machine frontmatter.

## Problem

The full rules files (~1,200–1,800 lines) fit in context but compete with code, diffs, and chat history. Models follow Prime Directives reliably; distant sections (documentation, design tokens, CI templates) drift unless the task touches them.

## Strategy

| Layer | Role | Target size |
|-------|------|-------------|
| **Core (always-on)** | Non-negotiable behavior on every turn | ~350–500 lines |
| **Scoped (`.claude/rules/*.md`)** | Deep rules loaded when relevant files are in context | ~50–150 lines each |
| **Full reference** | `GENERAL_CLAUDE.md` / `CLAUDE.md` remain source of truth; scoped rules link back | unchanged |

On conflict: **Core > scoped rule > full reference examples**. Corrections still append to the active file's Correction Log.

---

## Always-on: `GENERAL_CLAUDE_CORE.md` (imported by `CLAUDE.md` via `@.claude/rules/core.md`)

Keep these sections **verbatim or tightly summarized**. This is what loads every session.

| Section | In core? | Notes |
|---------|----------|-------|
| Header + authority block | Yes | Full |
| Prime Directives | Yes | Full — all 6 |
| Table of Contents | Yes | List sections + pointer to `.claude/rules/` |
| Clarification Protocol | Yes | Full trigger table + warning format |
| Correction & Memory Protocol | Yes | Full 7-step + entry format |
| Deployment Configuration Protocol | **Abbreviated** | 12-step checklist titles + STOP conditions only; link to `deployment.md` for detail |
| Runtime Model | Yes | Full, including Project Discovery Protocol |
| Project Structure | **Summary** | Discovery protocol + "never deviate"; drop archetype templates |
| Architecture Rules | Yes | Full dependency direction + layer responsibilities |
| Code Quality | Yes | Limits, commits, PR checklist |
| Enforcement Summary | Yes | Full table |
| Correction Log | Yes | Append-only; stays in core file |

**Do not put in always-on:** long examples, YAML templates, per-language blocks, default color hex lists, CI workflow samples.

### Abbreviated deployment block (example for core)

```markdown
## DEPLOYMENT — MANDATORY CHECKLIST (detail: .claude/rules/deployment.md)

Before ANY deploy: complete Steps 1–12 in order. STOP on missing env, hardcoded secrets,
or unknown mechanism. Discover commands from README/RUNBOOK/manifests — never assume.

1. Env/config populated
2. Deployment manifest valid
3. Build artifacts exist
4. Health checks defined
5. Network/connectivity correct
6. No hardcoded secrets
7. Pinned versions
8. Least-privilege runtime
9. Run project-documented deploy command
10. Run migrations in runtime context
11. Verify post-deploy health
12. Report status to user

Rules D-01 through D-08 apply. Destructive teardown requires explicit user confirmation.
```

Estimated core size: **~400 lines** including Correction Log.

---

## Scoped rules: `.claude/rules/`

Create plain Markdown `.md` files — **no frontmatter**. Begin each with an **"Applies when"** line
describing the context that should trigger a read (derived from the `globs` reference shown per rule below).

### 1. `deployment.md`

```yaml
description: Full 12-step deployment protocol, D-01–D-08, manifest discovery, command examples
globs: "**/docker-compose*.yml,**/compose.yaml,**/Makefile,**/Taskfile.yml,**/.github/workflows/deploy*.yml,**/terraform/**,**/k8s/**,**/helm/**,**/RUNBOOK.md"
alwaysApply: false
```

**Content:** Full `DEPLOYMENT CONFIGURATION PROTOCOL` from `GENERAL_CLAUDE.md` (discovery tables, steps 1–12 expanded, D-01–D-08, example commands labeled EXAMPLES ONLY).

---

### 2. `auth-security.md`

```yaml
description: Authentication, sessions, MFA, passwords, RBAC, rate limiting
globs: "**/auth/**,**/middleware/authenticate*,**/middleware/authorize*,**/security/**,**/*auth*.*"
alwaysApply: false
```

**Content:** Sections 8–9, 11–12 (Authentication & Security, RBAC, Input Security, Rate Limiting). Omit if project has no auth unless task is auth-related (agent uses Clarification Protocol).

---

### 3. `security-headers.md`

```yaml
description: HTTP security headers (CSP, HSTS, frame options)
globs: "**/middleware/**,**/nginx*.conf,**/Caddyfile,**/app.ts,**/main.go,**/settings.py"
alwaysApply: false
```

**Content:** Section 10 (Security Headers). Small; can merge into `auth-security.md` if preferred.

---

### 4. `api-design.md`

```yaml
description: API versioning, response envelopes, error format, auth endpoint capabilities
globs: "**/routes/**,**/controllers/**,**/handlers/**,**/api/**,**/openapi.*,**/swagger.*"
alwaysApply: false
```

**Content:** Section 17 (API Design Rules).

---

### 5. `database.md`

```yaml
description: Schema rules, queries, migrations, pagination, soft delete
globs: "**/migrations/**,**/prisma/**,**/alembic/**,**/db/**,**/models/**,**/schema.*,**/*migration*"
alwaysApply: false
```

**Content:** Section 16 (Database Rules).

---

### 6. `frontend.md`

```yaml
description: UI components, forms, a11y, loading states, routing guards
globs: "**/*.tsx,**/*.jsx,**/*.vue,**/*.svelte,**/components/**,**/features/**,**/pages/**"
alwaysApply: false
```

**Content:** Sections 5 + 18 (Design System & Color Tokens, Frontend Rules). Include default token scaffold only when project has no design system.

---

### 7. `design-tokens.md` (optional split from frontend)

```yaml
description: Color tokens, typography, spacing — no hardcoded values in components
globs: "**/tailwind.config.*,**/globals.css,**/theme.*,**/tokens.*,**/*.css"
alwaysApply: false
```

**Content:** Color/typography tables from Section 5. Skip if `frontend.md` is enough.

---

### 8. `containers-infra.md`

```yaml
description: Docker, Compose, K8s, Terraform — multi-stage, non-root, pinned images
globs: "**/Dockerfile*,**/docker-compose*.yml,**/compose.yaml,**/k8s/**,**/helm/**,**/*.tf"
alwaysApply: false
```

**Content:** Section 19 (Container & Infrastructure Rules).

---

### 9. `testing.md`

```yaml
description: Test pyramid, coverage thresholds, security tests
globs: "**/*.test.*,**/*.spec.*,**/*_test.*,**/tests/**,**/__tests__/**,**/jest.config.*,**/pytest.ini"
alwaysApply: false
```

**Content:** Section 20 (Testing Rules).

---

### 10. `ci-cd.md`

```yaml
description: CI jobs, security scan, deploy workflow patterns
globs: "**/.github/workflows/**,**/.gitlab-ci.yml,**/Jenkinsfile,**/azure-pipelines.yml"
alwaysApply: false
```

**Content:** Section 21 (CI/CD). Reference templates only.

---

### 11. `environment.md`

```yaml
description: Env validation, .env.example sync, 12-factor config
globs: "**/.env.example,**/config/env.*,**/settings.py,**/config.ts,**/*env*schema*"
alwaysApply: false
```

**Content:** Section 22 (Environment Variables).

---

### 12. `optional-modules.md`

```yaml
description: Optional integrations — lazy load, health probes, no import-time failures
globs: "**/modules/**,**/integrations/**,**/register*module*,**/plugin/**"
alwaysApply: false
```

**Content:** Section 14 (Optional Modules).

---

### 13. `documentation.md`

```yaml
description: Mandatory docs, sync policy, comments, PR doc checklist
alwaysApply: false
```

**Note:** No file glob reliably signals "user is editing docs." Options:

- `globs: "**/README.md,**/CHANGELOG.md,**/ARCHITECTURE.md,**/API_REFERENCE.md,**/RUNBOOK.md,**/USER_GUIDE.md"`
- Or `alwaysApply: true` with **short** checklist only (~40 lines) in core and full rules here

**Content:** Section 24 (Documentation Rules).

---

### 14. `security-checklist.md`

```yaml
description: Pre-release security checklist — auth, API, infrastructure
globs: "**/CHANGELOG.md,**/RELEASE*,**/.github/workflows/release*"
alwaysApply: false
```

**Content:** Section 25 (Security Checklist). Often used at release time; short version can live in core PR checklist.

---

### 15. Language rules (`stacks/` — one file per language detected in repo)

| File | Globs | Content |
|------|-------|---------|
| `stacks/lang-typescript.md` | `**/*.{ts,tsx}` | TypeScript subsection from Section 15 |
| `stacks/lang-python.md` | `**/*.py` | Python subsection from Section 15 |
| `stacks/lang-go.md` | `**/*.go` | Go subsection from Section 15 |
| `stacks/lang-rust.md` | `**/*.rs` | Rust subsection from Section 15 |
| `stacks/lang-java.md` | `**/*.{java,kt}` | Java/Kotlin subsection from Section 15 |

**Content:** Only the relevant block from Section 15 (Language & Type Safety Rules), plus universal forbidden/required patterns.

---

## `CLAUDE.md` project split — IMPLEMENTED

`CLAUDE.md` is now a project-agnostic governance core (Prime Directives, protocols, abbreviated
deploy checklist, Correction Log). All Node specifics were extracted into `.claude/rules/project/`.

| Scoped file (`project/`) | Globs | Contains |
|--------------------------|-------|----------|
| `nodejs-architecture.md` | `apps/**`, `pnpm-workspace.yaml`, `package.json` | Structure tree, runtime model, layering, optional modules, naming |
| `nodejs-api.md` | `apps/api/**` | Express/Prisma/Zod, auth (RS256/MFA), RBAC, rate limits, security headers, API envelope |
| `nodejs-web.md` | `apps/web/**`, `tailwind.config.*`, `globals.css` | React/Vite/Tailwind/shadcn, design tokens, axios, route guards |
| `nodejs-database.md` | `apps/api/prisma/**`, `*.prisma` | Prisma schema + base models, query rules |
| `nodejs-deployment.md` | `docker-compose*.yml`, `apps/*/Dockerfile`, `.env.example` | Compose stack, Dockerfiles, env vars, commands |
| `nodejs-testing-ci.md` | `*.test.ts`, `jest.config.*`, `.github/workflows/**` | Jest/Supertest, coverage, CI/CD |

The governance core points to `CLAUDE.md` Correction Log and the abbreviated checklist; deep
YAML/templates live in the `project/` scoped files only — never in the core or Prime Directives.

---

## Loading behavior (how this helps)

```mermaid
flowchart LR
    subgraph alwaysOn [Every session]
        Core[GENERAL_CLAUDE_CORE]
    end
    subgraph onDemand [When task matches the rule]
        Deploy[deployment.md]
        FE[frontend.md]
        DB[database.md]
        Lang[lang-typescript.md]
    end
    UserTask[User task + open files] --> Core
    UserTask --> onDemand
    Core --> Agent[Agent behavior]
    onDemand --> Agent
```

| Task | What loads |
|------|------------|
| "Fix typo in README" | Core only |
| "Add login endpoint" | Core + `api-design.md` + `auth-security.md` + `lang-*.md` |
| "Style the dashboard" | Core + `frontend.md` + `design-tokens.md` |
| "Deploy to staging" | Core (abbrev checklist) + `deployment.md` + `containers-infra.md` |
| "Add migration" | Core + `database.md` + `lang-*.md` |

---

## File layout (recommended)

```
claude/
├── GENERAL_CLAUDE.md          # Full reference (unchanged authority)
├── GENERAL_CLAUDE_CORE.md     # Slim always-on — IMPLEMENTED
├── CLAUDE.md                  # Node project-agnostic governance core — IMPLEMENTED
├── RULES_SPLIT.md             # This document
├── README.md
└── .claude/
    └── rules/                 # IMPLEMENTED — generic rules + core.md
        ├── core.md             # always-on: imported by root CLAUDE.md
        ├── deployment.md
        ├── auth-security.md
        ├── security-headers.md
        ├── api-design.md
        ├── database.md
        ├── frontend.md
        ├── design-tokens.md
        ├── containers-infra.md
        ├── testing.md
        ├── ci-cd.md
        ├── environment.md
        ├── optional-modules.md
        ├── documentation.md
        ├── security-checklist.md
        ├── stacks/              # stack-specific (language/framework)
        │   ├── lang-typescript.md
        │   ├── lang-python.md
        │   ├── lang-go.md
        │   ├── lang-rust.md
        │   └── lang-java.md
        └── project/            # project-specific (this project only)
            ├── nodejs-architecture.md
            ├── nodejs-api.md
            ├── nodejs-web.md
            ├── nodejs-database.md
            ├── nodejs-deployment.md
            └── nodejs-testing-ci.md
```

**Placement rule:** generic rules live at the root of `.claude/rules/`; language/framework rules live
in `stacks/`; rules unique to the current project live in `project/`. Project-specific configuration
is never inlined into the always-on core or the Prime Directives.

### `core.md` (always-on via import)

Plain Markdown, no frontmatter. Pulled in by the root `CLAUDE.md` with a single import line:

```markdown
@.claude/rules/core.md
```

`core.md` itself opens with an "Applies when: ALWAYS" line, then:

```markdown
# Core Engineering Rules

Follow GENERAL_CLAUDE_CORE.md (or embedded content).
Full reference: GENERAL_CLAUDE.md. Scoped detail: sibling rules in .claude/rules/.
```

Either embed core content directly in `core.md` or keep `GENERAL_CLAUDE_CORE.md` at repo root and reference it.

---

## Migration steps

1. Create `GENERAL_CLAUDE_CORE.md` by copying sections listed in "Always-on" above.
2. Extract each scoped section into `.claude/rules/*.md` as plain Markdown with an "Applies when" line (no frontmatter).
3. Add to core TOC: "Sections 5–25: see `.claude/rules/` when applicable."
4. Update `README.md` with split architecture link.
5. In target projects: copy `GENERAL_CLAUDE_CORE.md` + `.claude/rules/` (or symlink from this repo).
6. Keep `GENERAL_CLAUDE.md` as the merge target when editing rules; regenerate core + scoped from it periodically.

---

## What not to split

| Keep unified | Reason |
|--------------|--------|
| Prime Directives | Must override everything; never gated |
| Clarification Protocol | Must trigger even when no files open |
| Correction & Memory | Corrections must apply globally |
| Correction Log | Single append-only audit trail |
| Enforcement Summary | Authority levels apply to all sections |

---

## Expected improvement

| Metric | Full file always-on | Split |
|--------|---------------------|-------|
| Always-on tokens | ~15k–25k | ~4k–6k |
| Deploy checklist adherence | Medium | High when compose/CI files in context |
| UI token compliance | Low on backend tasks | High when editing components |
| Rule contradictions | Rare if single file | Prevent with "core wins" hierarchy |

---

## Quick decision: which file for a project?

| Project | Always-on | Scoped pack |
|---------|-----------|-------------|
| Generic / polyglot | `GENERAL_CLAUDE_CORE.md` | `general/*.md` |
| Node fullstack monorepo | `CLAUDE_CORE.md` | `nodejs/*.md` |
| Library only | `GENERAL_CLAUDE_CORE.md` | `lang-*.md` + `testing.md` only |

Copy only the scoped rules that match the repo's languages and archetype.
