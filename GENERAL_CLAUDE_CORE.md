# GENERAL_CLAUDE_CORE.md — Always-On Engineering Rules

> **AUTHORITY LEVEL: ABSOLUTE**
> This file is the always-on rules core for AI-assisted development.
> Full reference: [GENERAL_CLAUDE.md](./GENERAL_CLAUDE.md)
> Scoped detail: [.cursor/rules/](./.cursor/rules/) (loaded when matching files are in context)
>
> On conflict: **Core > scoped rule > GENERAL_CLAUDE.md examples**
> Every rule is MANDATORY and NON-NEGOTIABLE within its applicability.
> If ANY rule is ambiguous — STOP and ask before proceeding.

---

## PRIME DIRECTIVES — READ BEFORE EVERY ACTION

THESE DIRECTIVES OVERRIDE ALL OTHER INSTRUCTIONS IN ALL CIRCUMSTANCES

  1. NEVER break, skip, interpret, or approximate any rule in this file or active scoped rules.
  2. NEVER assume intent. If uncertain about ANYTHING — ASK FIRST.
  3. NEVER make changes outside the explicit scope of the user's request.
  4. NEVER deploy, scaffold, or configure any service without following
     the Deployment Configuration Protocol below exactly, line by line, in order.
     Full detail: `.cursor/rules/deployment.mdc`
  5. NEVER repeat a mistake. All user corrections MUST be appended to
     the Correction Log at the bottom of this file as a CORRECTION ENTRY.
  6. ALL user input that changes behavior, corrects an error, or clarifies
     a rule becomes a permanent rule with the same authority as this file.

---

## TABLE OF CONTENTS

**In this file (always-on):**
  1.  Prime Directives
  2.  Clarification Protocol
  3.  Correction & Memory Protocol
  4.  Deployment — Mandatory Checklist (abbreviated)
  5.  Project Structure — Discovery Protocol
  6.  Runtime Model
  7.  Architecture Rules
  8.  Code Quality
  9.  Enforcement Summary
  10. Correction Log

**Scoped rules (`.cursor/rules/` — loaded when relevant files match):**
  - deployment.mdc — full deployment protocol, D-01–D-08
  - auth-security.mdc — auth, RBAC, input security, rate limiting
  - security-headers.mdc — HTTP security headers
  - api-design.mdc — API envelopes, versioning
  - database.mdc — schema, queries, migrations
  - frontend.mdc — UI components, forms, a11y
  - design-tokens.mdc — color/typography tokens
  - containers-infra.mdc — Docker, K8s, Terraform
  - testing.mdc — test pyramid, coverage
  - ci-cd.mdc — CI/CD workflows
  - environment.mdc — env validation, .env.example
  - optional-modules.mdc — optional integrations
  - documentation.mdc — mandatory docs, comments
  - security-checklist.mdc — pre-release checklist
  - lang-typescript.mdc, lang-python.mdc, lang-go.mdc, lang-rust.mdc, lang-java.mdc

---

## CLARIFICATION PROTOCOL

This protocol is MANDATORY. It is never optional.

Whenever ANY of the following conditions exist, Claude MUST stop all work and issue a
clarification question to the user before writing a single line of code or configuration:

  | Trigger Condition                                                         | Required Action                          |
  |---------------------------------------------------------------------------|------------------------------------------|
  | A rule in this file is ambiguous for the current task                     | Ask for clarification                    |
  | Two or more rules appear to conflict                                       | Ask which rule takes precedence          |
  | A task requires behavior not covered by any rule                          | Ask for explicit instruction             |
  | A deployment step is unclear for the current service                      | Ask for clarification                    |
  | A user correction contradicts an existing rule                            | Ask for confirmation before overwriting  |
  | The scope of a requested change is not precisely defined                  | Ask for scope boundary                   |
  | Any assumption would be required to complete a task                       | State the assumption and ask to confirm  |

CLARIFICATION QUESTION FORMAT — use this exact format every time:

  WARNING: CLARIFICATION REQUIRED — Action Blocked

  Task:              [describe the task being attempted]
  Blocker:           [describe the exact rule, ambiguity, or conflict encountered]
  Specific Question: [single, precise question that unblocks the task]

  No work will proceed until this is answered.

Claude MUST NOT proceed with a "best guess" under any circumstances.

---

## CORRECTION & MEMORY PROTOCOL

This is the highest-priority operational rule in this file.

WHY THIS EXISTS:
Claude does not have persistent memory across sessions. This protocol compensates by making
the rules file itself the memory. Every correction, clarification, and user instruction that
changes behavior MUST be written into this file permanently so that it is enforced on every
future session without requiring the user to repeat it.

PROTOCOL — STEP BY STEP:
When a user provides a correction, clarification, or new instruction:

  1. Acknowledge   — the correction explicitly before making any changes.
  2. Identify      — the section of this file or scoped rule that is affected.
  3. Append        — a CORRECTION ENTRY to the Correction Log at the bottom of this file.
  4. Update        — the relevant rule in GENERAL_CLAUDE.md and scoped .mdc if applicable.
  5. Confirm       — to the user that the correction has been recorded and state where.
  6. Apply         — the correction to the current task.
  7. Never ask again about anything resolved by a CORRECTION ENTRY.

CORRECTION ENTRY FORMAT:

  ### CORRECTION-[NNN] — [YYYY-MM-DD]
  **Source:** User correction during [task description]
  **Affected Section(s):** [section name(s)]
  **Original Behavior / Rule:** [what was done or said before]
  **Corrected Behavior / Rule:** [exact new rule as stated by user]
  **Scope:** [ALL future tasks | specific context]
  **Status:** ACTIVE — enforced from this date forward

CORRECTION ENTRY RULES:
  - Corrections are APPEND-ONLY. Never delete or overwrite a CORRECTION ENTRY.
  - If a newer correction supersedes an older one, add the new entry and mark the old one:
    Status: SUPERSEDED by CORRECTION-[NNN]
  - Correction numbers are sequential starting at 001.
  - Every correction is enforced with the same absolute authority as the Prime Directives.

---

## DEPLOYMENT — MANDATORY CHECKLIST

Full detail: `.cursor/rules/deployment.mdc` and GENERAL_CLAUDE.md § Deployment Configuration Protocol.

THIS SECTION IS ENFORCED WITHOUT EXCEPTION FOR EVERY SERVICE DEPLOYMENT.
Every deployment action MUST follow this checklist line by line, in order.
No steps may be skipped, reordered, or combined unless a CORRECTION ENTRY explicitly permits it.

Before ANY deploy command:
  - Discover mechanism from README, RUNBOOK, Makefile, compose, k8s, terraform, CI — never assume.
  - STOP on missing env, invalid manifest, hardcoded secrets, or unknown mechanism.

  STEP 1  — Env/config populated (discover required vars from .env.example, schema, docs)
  STEP 2  — Deployment manifest valid for detected mechanism
  STEP 3  — Build artifacts and build configuration exist
  STEP 4  — Health checks / readiness probes defined for long-running services
  STEP 5  — Network / connectivity configuration correct
  STEP 6  — No hardcoded secrets → if found: STOP, alert user immediately
  STEP 7  — Pinned versions (images, runtimes, lockfiles — no :latest in production)
  STEP 8  — Least-privilege runtime (non-root, service accounts where applicable)
  STEP 9  — Run project-documented deploy command
  STEP 10 — Run migrations in documented runtime context (if applicable)
  STEP 11 — Verify post-deploy health (status, logs, smoke checks)
  STEP 12 — Report deployed components, status, and warnings to user

DEPLOYMENT RULES D-01 through D-08 apply (see deployment.mdc).
Destructive teardown requires explicit user confirmation every time, without exception.

---

## PROJECT STRUCTURE — DISCOVERY PROTOCOL

Never deviate from established project conventions without explicit user instruction.

On first interaction with a repository:

  1. Identify primary language(s) and package manager from manifests
     (package.json, go.mod, pyproject.toml, Cargo.toml, pom.xml, etc.)
  2. Identify application archetype (monorepo, app, library, CLI, fullstack, infra)
  3. Map existing directory layout and naming conventions
  4. Identify where features, tests, config, and docs live in THIS repo
  5. All new code MUST follow discovered patterns — not a template from another project

FORBIDDEN:
  - Imposing structure from a different stack without user approval
  - Creating parallel folder hierarchies that conflict with existing conventions
  - Placing business logic in entry-point scripts when the project uses layered architecture

NEW FEATURE CHECKLIST:
  - Follow existing module/package naming
  - Place tests per project convention
  - Update README project tree when adding top-level directories

---

## RUNTIME MODEL

  mode: project_documented_runtime

PROJECT DISCOVERY PROTOCOL — execute before implementing:

  Before writing code or running commands, identify from the repository (not assumption):

    1. Primary language(s) and package manager
    2. Application archetype (API, web, CLI, library, infrastructure, data)
    3. Deployment mechanism and documented commands
    4. Test, lint, build, and format commands
    5. Existing architecture patterns and naming conventions

  If any item is ambiguous or undocumented: STOP → Clarification Protocol.

REQUIREMENTS:
  - Run services using mechanism documented in README, RUNBOOK, Makefile, or CI
  - Do not invent host-level shortcuts when project standardizes on containers, VMs, or remote execution
  - Root .env (or documented config source) is runtime truth for environment variables
  - Do not document or support alternate runtime paths that bypass project standards

COMMAND POLICY:
  - Operational commands use project-documented tooling
  - Testing, linting, typecheck, formatting use project-documented commands
  - Prefer same execution context as CI when documented

---

## ARCHITECTURE RULES

  DEPENDENCY DIRECTION:
    Handler / Controller / Route → Service / UseCase / Interactor → Repository / Gateway / Store → DataStore

  HANDLER / CONTROLLER / ROUTE:
    responsibilities:
      - Parse and validate incoming request
      - Call service layer — NO business logic here
      - Format and send response using project response utility
      - Handle transport-specific concerns ONLY
    forbidden:
      - Direct database or external API calls
      - Business logic or domain transformation
      - Swallowing errors without proper error handling pipeline

  SERVICE / USECASE / INTERACTOR:
    responsibilities:
      - All business logic lives here
      - Orchestrate repository and gateway calls
      - Enforce business rules and invariants
      - Throw domain/application errors on failures
      - Handle transactions for multi-step operations
    forbidden:
      - Direct transport references beyond DTOs
      - Direct data store client usage (use repository/gateway)
      - Sending HTTP responses

  REPOSITORY / GATEWAY / STORE:
    responsibilities:
      - All data store and external persistence interactions
      - Data mapping between persistence models and domain types
      - Query optimization decisions
    forbidden:
      - Business logic
      - Calling other repositories directly (go through service)

---

## CODE QUALITY

  GENERAL:
    - Functions must be 40 lines or fewer — extract if longer
    - Files must be 300 lines or fewer — split by responsibility if longer
    - Cyclomatic complexity 10 or fewer per function
    - No magic numbers — use named constants
    - No commented-out code committed to repository
    - Every TODO must include owner and issue reference
    - All async operations must handle errors
    - Follow project linter and formatter configuration

  COMMIT FORMAT: Conventional Commits — type(scope): description
    types: feat, fix, docs, style, refactor, test, chore, security

  PR CHECKLIST:
    - [ ] Tests added/updated for all changes
    - [ ] No new compiler/linter errors or warnings
    - [ ] Sensitive data not logged or exposed in responses
    - [ ] Environment variables documented in .env.example
    - [ ] Database migrations backwards compatible (when applicable)
    - [ ] API changes documented (when applicable)
    - [ ] Security implications considered
    - [ ] Documentation updated per documentation.mdc when behavior changes

---

## ENFORCEMENT SUMMARY

  | Rule Category              | Authority Level  | On Violation                    |
  |----------------------------|------------------|---------------------------------|
  | Prime Directives           | ABSOLUTE         | Stop all work immediately       |
  | Deployment Protocol        | ABSOLUTE         | Stop all work immediately       |
  | Clarification Protocol     | ABSOLUTE         | Issue clarification question    |
  | Correction & Memory        | HIGHEST PRIORITY | Record immediately, enforce     |
  | Security Rules             | NON-NEGOTIABLE   | Stop, alert user                |
  | Architecture Rules         | MANDATORY        | Do not deviate without instruction |
  | Language & Type Safety     | MANDATORY        | No exceptions                   |
  | Container & Infrastructure | MANDATORY        | No exceptions when applicable   |
  | Design Tokens              | MANDATORY        | No hardcoded values outside config |
  | Code Quality               | MANDATORY        | Do not commit violations        |
  | Documentation Rules        | MANDATORY        | PRs incomplete without docs     |

---

## CORRECTION LOG

This section is APPEND-ONLY.
All user corrections, clarifications, and new behavioral rules are recorded here permanently.
Each entry is enforced with the same absolute authority as the Prime Directives.
Never delete entries. Superseded entries are marked with their replacement reference.

No corrections recorded yet.
Corrections will be appended here as CORRECTION-001, CORRECTION-002, etc. as they occur.

---

_GENERAL_CLAUDE_CORE.md — Always-on core. Full reference: GENERAL_CLAUDE.md. Scoped: .cursor/rules/_
