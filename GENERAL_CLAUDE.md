# GENERAL_CLAUDE.md — Enterprise Engineering & Development

> **AUTHORITY LEVEL: ABSOLUTE**
> This file is the single source of truth for all AI-assisted development on this project.
> **Always-on core:** [GENERAL_CLAUDE_CORE.md](./GENERAL_CLAUDE_CORE.md) + [.cursor/rules/core.mdc](./.cursor/rules/core.mdc)
> **Scoped detail:** [.cursor/rules/](./.cursor/rules/) — see [RULES_SPLIT.md](./RULES_SPLIT.md)
> Every rule in this document is MANDATORY and NON-NEGOTIABLE.
> Rules are NOT to be interpreted, approximated, or selectively applied.
> If ANY rule is ambiguous, unclear, or appears to conflict with a task — STOP and ask the user before proceeding.
> Proceeding without clarification when uncertainty exists is a critical violation.

---

## PRIME DIRECTIVES — READ BEFORE EVERY ACTION

THESE DIRECTIVES OVERRIDE ALL OTHER INSTRUCTIONS IN ALL CIRCUMSTANCES

  1. NEVER break, skip, interpret, or approximate any rule in this file.
  2. NEVER assume intent. If uncertain about ANYTHING — ASK FIRST.
  3. NEVER make changes outside the explicit scope of the user's request.
  4. NEVER deploy, scaffold, or configure any service without following
     the Deployment Configuration Protocol (Section: DEPLOYMENT) exactly,
     line by line, in documented order.
  5. NEVER repeat a mistake. All user corrections MUST be appended to
     this file immediately under the relevant section as a CORRECTION ENTRY.
  6. ALL user input that changes behavior, corrects an error, or clarifies
     a rule becomes a permanent rule with the same authority as this file.

---

## TABLE OF CONTENTS

  1.  Prime Directives
  2.  Clarification Protocol
  3.  Correction & Memory Protocol
  4.  Deployment Configuration Protocol
  5.  Design System & Color Tokens
  6.  Project Structure
  7.  Runtime Model
  8.  Authentication & Security
  9.  RBAC
  10. Security Headers
  11. Input Security
  12. Rate Limiting
  13. Architecture Rules
  14. Optional Modules
  15. Language & Type Safety Rules
  16. Database Rules
  17. API Design Rules
  18. Frontend Rules
  19. Container & Infrastructure Rules
  20. Testing Rules
  21. CI/CD
  22. Environment Variables
  23. Code Quality
  24. Documentation Rules
  25. Security Checklist
  26. Correction Log

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
  | A deployment step in Section DEPLOYMENT is unclear for the current service| Ask for clarification                    |
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
  2. Identify      — the section of this file that is affected.
  3. Append        — a CORRECTION ENTRY to the Correction Log at the bottom of this file.
  4. Update        — the relevant rule section inline if the correction modifies an existing rule.
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

## DEPLOYMENT CONFIGURATION PROTOCOL

THIS SECTION IS ENFORCED WITHOUT EXCEPTION FOR EVERY SERVICE DEPLOYMENT.
It does not matter what the service is — internal, external, new, or existing.
Every deployment action MUST follow this protocol line by line, in the order written.
No steps may be skipped, reordered, or combined unless a CORRECTION ENTRY explicitly permits it.

GOVERNING DEPLOYMENT FILES — DISCOVERY ORDER:
Before any deployment, Claude MUST identify the project's authoritative deployment mechanism
by inspecting the repository in this order. The first match that is documented or actively
used in CI/RUNBOOK becomes the root deployment configuration unless the user specifies otherwise.

  ROOT DEPLOYMENT CONFIGURATION (discover in order):
    1. docker-compose.yml / compose.yaml
    2. Makefile or Taskfile.yml (deploy targets)
    3. helm/ chart directory
    4. k8s/ or kubernetes/ manifests
    5. terraform/ or *.tf at project root
    6. .github/workflows/deploy.yml (or equivalent CI deploy workflow)
    7. README.md / RUNBOOK.md deployment section (when no manifest exists)

  OVERRIDE / PROFILE FILES (when applicable):
    - docker-compose.override.yml, compose.*.yaml
    - Makefile environment-specific targets (deploy-staging, deploy-prod)
    - CI environment matrices and branch-based profiles
    - Terraform workspace / var-file per environment

  ENVIRONMENT SOURCE:
    - Root .env, .env.local, or framework-native validated config
    - 12-factor principle: environment variables are runtime truth
    - Secrets managers (Vault, cloud provider secrets) when documented in RUNBOOK

  ENVIRONMENT TEMPLATE:
    - .env.example, .env.sample, config schema docs — documentation only, not runtime

The discovered root deployment configuration is authoritative for that project.
All services MUST be defined, configured, and deployed through that mechanism.
Alternate undocumented deployment paths are PROHIBITED (see Runtime Model).

PRE-DEPLOYMENT CHECKLIST — MANDATORY, IN ORDER:
Before any deploy command is executed, Claude MUST verify and complete all of the following
steps in sequence. Each step must be completed fully before proceeding.

  STEP 1 — Verify environment configuration exists and is populated
    - Discover required variables from: .env.example, config schema, env validation code,
      deployment manifest references, or README/RUNBOOK
    - Verify ALL required variables are present in the runtime environment source
    - Verify NO required variable is empty (unless explicitly optional)
    - If any variable is missing or empty: STOP → ask user to provide value

  STEP 2 — Verify deployment manifest exists and is structurally valid
    - Confirm the root deployment configuration file exists
    - Confirm the service or component being deployed is defined in that manifest
    - Confirm all required environment variable references exist in the service definition
    - Confirm dependency ordering (depends_on, health gates, init containers) is correct
    - If any issue found: STOP → report exact issue → ask user how to proceed

  STEP 3 — Verify build artifacts and build configuration exist
    - Discover build mechanism: Dockerfile, build.sh, Makefile target, CI build job,
      pyproject.toml, Cargo.toml, go.mod, pom.xml, etc.
    - Confirm build configuration matches target environment (production vs development)
    - For containerized services: confirm multi-stage build when applicable
    - If missing and required: STOP → propose build config per Section CONTAINER & INFRASTRUCTURE
      RULES → confirm with user

  STEP 4 — Verify health checks / readiness probes for stateful or long-running services
    - Confirm healthcheck blocks (Compose), liveness/readiness probes (K8s), or equivalent
    - Confirm database, cache, queue, and app services expose verifiable health endpoints
    - If missing: STOP → add health checks per project patterns → confirm with user

  STEP 5 — Verify network / connectivity configuration
    - Confirm explicit network isolation where the deployment mechanism supports it
      (Compose networks, K8s Services/NetworkPolicies, security groups, VPC rules)
    - Confirm services can reach dependencies without exposing unnecessary public ports
    - If misconfigured: STOP → report exact issue → ask user how to proceed

  STEP 6 — Verify secrets and security posture
    - Confirm NO secrets are hardcoded in deployment manifests
    - Confirm NO secrets are hardcoded in Dockerfiles, build scripts, or source code
    - Confirm all sensitive values reference environment variables or secret stores
    - If any hardcoded secret found: STOP → do not proceed → alert user immediately

  STEP 7 — Verify pinned versions
    - Confirm container images use pinned tags (not :latest in production)
    - Confirm language runtime versions are pinned (Dockerfile FROM, .tool-versions,
      CI node-version, go directive, rust-toolchain.toml, etc.)
    - Confirm dependency lockfiles are committed and used in CI/deploy
    - If :latest or unpinned production versions found: STOP → replace → confirm with user

  STEP 8 — Verify least-privilege runtime configuration
    - For containers: confirm non-root USER or equivalent security context
    - For K8s: confirm service accounts, runAsNonRoot, dropped capabilities where applicable
    - For cloud resources: confirm IAM least-privilege per RUNBOOK
    - If missing where applicable: STOP → add least-privilege config → confirm with user

  STEP 9 — Run deployment command
    - Use the project-documented deploy command discovered from README, RUNBOOK, Makefile,
      or CI workflow — never assume a specific tool
    - Examples (use only when documented for this project):
        docker compose up -d --build
        make deploy
        helm upgrade --install ...
        terraform apply
        kubectl apply -f k8s/
    - NEVER use an undocumented alternate path when the project standardizes on a mechanism
    - NEVER run long-running deploy without -d or detached equivalent in automated/CI contexts

  STEP 10 — Run schema migrations / data migrations (if applicable)
    - Discover migration command from project docs (flyway, alembic, prisma, goose, rails db:migrate, etc.)
    - Run migrations in the appropriate runtime context (container, CI job, documented shell)
    - NEVER run migrations on an ad-hoc host path when the project runs them in CI/containers
    - Confirm migration succeeded before proceeding

  STEP 11 — Verify service health post-deployment
    - Use project-documented status commands (compose ps, kubectl get pods, health URL, etc.)
    - All services must show healthy/running state per project definition
    - Check logs for startup errors using documented log commands
    - If any service is unhealthy or exited: STOP → diagnose → report to user

  STEP 12 — Confirm deployment complete
    - Report to user: which components were deployed, their status, and any warnings

DEPLOYMENT COMMAND REFERENCE — EXAMPLES ONLY (discover actual commands from project):

  # Docker Compose (example — use only when compose is the project mechanism)
  docker compose up -d --build
  docker compose ps
  docker compose logs -f [service_name]
  docker compose run --rm [service_name] [command]
  docker compose down

  # Makefile (example)
  make deploy
  make deploy-staging
  make migrate

  # Kubernetes (example)
  kubectl apply -f k8s/
  kubectl rollout status deployment/[name]
  kubectl logs -f deployment/[name]

  # Terraform (example)
  terraform plan
  terraform apply

  # Destructive teardown — ALWAYS requires explicit user confirmation
  docker compose down -v
  terraform destroy
  kubectl delete namespace [name]

DEPLOYMENT RULES:
  Rule D-01: The project's discovered root deployment configuration is the ONLY deployment
             mechanism. No undocumented exceptions.
  Rule D-02: Every variable consumed by a deployed service MUST be defined in the project's
             environment source (.env, secret store, or validated config).
  Rule D-03: Use the project's documented CLI and syntax. Never substitute an equivalent tool
             without user confirmation.
  Rule D-04: The Pre-Deployment Checklist is executed in full for EVERY deployment,
             including incremental redeployments of a single service.
  Rule D-05: If Step 6 reveals a hardcoded secret, ALL work stops immediately.
             The user is alerted before any other action is taken.
  Rule D-06: Schema migrations run in the project's documented runtime context.
             Never run migrations via an ad-hoc path when the project standardizes otherwise.
  Rule D-07: If Claude is asked to deploy a service type not covered by this protocol,
             Claude MUST ask the user how to classify and configure it before proceeding.
  Rule D-08: Destructive teardown commands (volume removal, destroy, namespace delete)
             require explicit user confirmation every time, without exception.

---

## DESIGN SYSTEM & COLOR TOKENS

APPLICABILITY: This section applies when the project includes a user interface OR when the
user explicitly requests UI work. For CLI tools, libraries, backend-only services, and
infrastructure projects with no UI, skip this section unless the task involves UI.

When the project HAS an existing design system:
  - Follow the project's design tokens, theme config, CSS variables, or design documentation.
  - Never hardcode colors, spacing, or typography outside the project's token system.
  - Extend the existing system; do not introduce a parallel styling approach.

When NO design system exists AND the user requests UI work:
  - Establish tokens in the project's styling configuration (theme file, CSS variables, design tokens JSON).
  - Use the following default palette as a scaffold — never hardcode hex values in components:

  COLOR TOKENS (default scaffold):
    background:        "#1a1a2e"   # Page/app background (near-black navy)
    surface:           "#16213e"   # Card/panel background
    surface_elevated:  "#0f3460"   # Elevated surfaces, modals, dropdowns
    primary:           "#39FF14"   # Neon green — primary actions, CTAs, active states
    primary_hover:     "#2ecc0f"   # Slightly dimmed green on hover
    primary_muted:     "#1a7a08"   # Subtle green backgrounds, badges
    accent:            "#9B59B6"   # Purple — secondary actions, links, highlights
    accent_hover:      "#8e44ad"   # Darker purple on hover
    accent_muted:      "#4a235a"   # Subtle purple backgrounds
    text_primary:      "#FFFFFF"   # Primary text
    text_secondary:    "#A0AEC0"   # Muted/helper text
    text_disabled:     "#4A5568"   # Disabled state text
    border:            "#2D3748"   # Default border color
    border_focus:      "#39FF14"   # Focus ring — always neon green
    error:             "#FC8181"   # Error states
    warning:           "#F6E05E"   # Warning states
    success:           "#68D391"   # Success states (distinct from primary green)
    info:              "#63B3ED"   # Informational states

  TYPOGRAPHY (default scaffold):
    font_sans:   "'Inter', 'Segoe UI', sans-serif"
    font_mono:   "'JetBrains Mono', 'Fira Code', monospace"
    base_size:   "16px"
    scale:       framework default scale or 4px base grid

  SPACING:        4px base scale or framework default
  BORDER RADIUS:  8px default, 12px for cards
  SHADOW:         subtle glow on primary interactive elements when appropriate

---

## PROJECT STRUCTURE

The following protocol is MANDATORY for all projects governed by this file.
Never deviate from established project conventions without explicit user instruction.

STRUCTURE DISCOVERY PROTOCOL — execute on first interaction with a repository:

  1. Identify primary language(s) and package manager from manifests:
     package.json, go.mod, pyproject.toml, Cargo.toml, pom.xml, build.gradle,
     Gemfile, composer.json, *.csproj, etc.

  2. Identify application archetype:
     - monorepo (workspaces, multiple packages)
     - single application (web, API, desktop)
     - library / SDK
     - CLI tool
     - fullstack (frontend + backend)
     - infrastructure / data pipeline
     - hybrid

  3. Map existing directory layout and naming conventions.
  4. Identify where features, tests, config, and docs live in THIS repo.
  5. All new code MUST follow the discovered patterns — not a template from another project.

REFERENCE ARCHETYPES (examples only — not mandates):

  API / backend service:
    src/ or app/
      config/           # validated configuration
      modules/ or handlers/  # feature boundaries
      middleware/ or filters/
      shared/ or common/
    tests/
    Dockerfile or equivalent (when containerized)

  Fullstack:
    apps/ or packages/ or frontend/ + backend/
    shared types/contracts where applicable

  Library:
    src/ or lib/
    tests/
    examples/
    API docs

  CLI:
    cmd/ or cli/
    internal/ or lib/
    tests/

  Infrastructure:
    terraform/ or pulumi/ or cdktf/
    modules/
    environments/
    README + RUNBOOK for apply order

FORBIDDEN:
  - Imposing a structure from a different stack without user approval
  - Creating parallel folder hierarchies that conflict with existing conventions
  - Placing business logic in entry-point scripts when the project uses layered architecture

NEW FEATURE CHECKLIST:
  - Follow existing module/package naming in the repo
  - Place tests alongside or in the project's standard test directory
  - Update README project tree when adding top-level directories
  - Register routes, commands, or jobs per project conventions

---

## RUNTIME MODEL

  mode: project_documented_runtime

PROJECT DISCOVERY PROTOCOL — execute before implementing:

  Before writing code or running commands, Claude MUST identify from the repository (not assumption):

    1. Primary language(s) and package manager
    2. Application archetype (API, web, CLI, library, infrastructure, data)
    3. Deployment mechanism and documented commands
    4. Test, lint, build, and format commands
    5. Existing architecture patterns and naming conventions

  If any item is ambiguous or undocumented: STOP → Clarification Protocol.

REQUIREMENTS:
  - Run services using the mechanism documented in README, RUNBOOK, Makefile, or CI
  - Do not invent host-level shortcuts when the project standardizes on containers, VMs,
    or remote execution environments
  - Root .env (or documented config source) is runtime truth for environment variables
  - App-level .env.example files are optional documentation templates only
  - Do not document or support alternate runtime paths that bypass project standards

COMMAND POLICY:
  - Operational commands (up/down/logs/ps/run/exec/deploy) use project-documented tooling
  - Testing, linting, typecheck, and formatting use project-documented commands
  - Prefer the same execution context as CI (container, virtualenv, nix shell, etc.) when documented

---

## AUTHENTICATION & SECURITY

These rules are NON-NEGOTIABLE when the project includes authentication.
When the project has no auth: apply only to new auth implementation tasks.

Use the stack's established auth libraries and frameworks. The following invariants apply
regardless of language or framework.

  STRATEGY: Short-lived access token + long-lived refresh mechanism (cookie or secure storage)

  ACCESS TOKEN:
    algorithm : asymmetric signing preferred (e.g. RS256, ES256)
                # Never use shared-secret signing (HS256) in production
    expiry    : 15m maximum for interactive sessions
    storage   : memory only in browser SPAs — NEVER localStorage, NEVER sessionStorage
    delivery  : Authorization: Bearer header (or framework equivalent)

  REFRESH TOKEN:
    algorithm      : asymmetric signing preferred
    expiry         : 7d (or shorter per security policy)
    storage        : HTTP-only, Secure, SameSite=Strict cookie (or framework equivalent)
    rotation       : true — issue new refresh token on every use
    family_tracking: true — detect refresh token reuse attacks
    invalidation   : server-side blocklist or session store (Redis, DB, or equivalent)

  PASSWORD:
    hashing       : adaptive algorithm (bcrypt, argon2, scrypt)
    cost          : minimum equivalent of bcrypt 12 rounds — never lower
    min_length    : 12
    requirements  : uppercase + lowercase + number + special character
    breach_check  : true — check against breach corpus on registration when feasible

  MFA (when implemented):
    method          : TOTP (RFC 6238) or WebAuthn/FIDO2
    secret_storage  : encrypted at rest (AES-256-GCM or HSM equivalent)
    backup_codes:
      count  : 10
      hashed : true
    enforcement: optional at registration, admin-enforceable per role

  SESSION SECURITY:
    - Bind refresh tokens to user-agent + IP fingerprint where practical
    - Concurrent session limiting (configurable per role)
    - Force logout all sessions endpoint for users and admins
    - Last login timestamp tracking
    - Suspicious login detection (new location/device alerts)

---

## RBAC

  ROLES:
    admin:
      description: Full system access, user management, audit log access
      inherits: [user]
    user:
      description: Standard authenticated access to own resources
      inherits: [viewer]
    viewer:
      description: Read-only access to permitted resources
      inherits: []

  IMPLEMENTATION:
    - Roles stored in token/session claims AND verified server-side on every request
    - Never trust client-provided role data
    - Authentication middleware/guard runs before authorization middleware/guard always
    - Resource ownership checks separate from role checks
    - Audit log every privilege escalation attempt

  MIDDLEWARE USAGE PATTERN (framework-agnostic):

    // Protect route by authentication only:
    route('/profile', authenticate, handler.getProfile);

    // Protect route by role:
    route('/users/:id', authenticate, authorize(['admin']), handler.deleteUser);

    // Protect route by role OR ownership:
    route('/users/:id', authenticate, authorizeOwnerOrRole(['admin']), handler.updateUser);

---

## SECURITY HEADERS

APPLICABILITY: Required when the project serves HTTP responses (web apps, APIs, gateways).

  IMPLEMENTATION: Use framework security middleware equivalent to Helmet, or configure
  at reverse proxy / API gateway when documented in RUNBOOK.

  REQUIRED HEADERS:
    - Content-Security-Policy (strict, no unsafe-inline in production)
    - X-Frame-Options: DENY (or CSP frame-ancestors)
    - X-Content-Type-Options: nosniff
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: camera=(), microphone=(), geolocation=()
    - Strict-Transport-Security: max-age=31536000; includeSubDomains (HTTPS only)

---

## INPUT SECURITY

  - Validate ALL incoming data at system boundaries with schema validation — no exceptions.
    Use the project's schema library (Zod, Pydantic, Joi, JSON Schema, protobuf validation, etc.)
  - Sanitize output rendered in HTML contexts (DOMPurify or equivalent on frontend;
    HTML escape or sanitizer on backend templates)
  - Parameterized queries only via ORM/query builder — raw SQL requires explanatory review comment
  - File uploads: validate MIME type and content server-side, never trust Content-Type header alone
  - Strip unknown fields from request bodies before processing
  - Validate path parameters, query strings, and headers where they influence behavior

---

## RATE LIMITING

  IMPLEMENTATION: Use project-appropriate rate limiting (middleware, API gateway, WAF, or
  cloud edge). Persistent store (Redis or equivalent) required in production; in-memory
  acceptable for local development only.

  TIERS (apply when project exposes HTTP APIs):
    auth_endpoints:
      window  : 15m
      max     : 10
      message : "Too many authentication attempts"
    api_general:
      window  : 1m
      max     : 100
    api_authenticated:
      window  : 1m
      max     : 300

  progressive_delays                    : true
  ip_blocking_after_repeated_violations : true

---

## ARCHITECTURE RULES

  DEPENDENCY DIRECTION:
    Handler / Controller / Route → Service / UseCase / Interactor → Repository / Gateway / Store → DataStore

  HANDLER / CONTROLLER / ROUTE:
    responsibilities:
      - Parse and validate incoming request (via validation middleware or decorators)
      - Call service layer — NO business logic here
      - Format and send HTTP response using project response utility
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
      - Direct transport references (req/res, context objects beyond DTOs)
      - Direct data store client usage (use repository/gateway)
      - Sending HTTP responses

  REPOSITORY / GATEWAY / STORE:
    responsibilities:
      - All data store and external persistence interactions
      - Data mapping between persistence models and domain types
      - Query optimization and eager loading decisions
    forbidden:
      - Business logic
      - Calling other repositories directly (go through service)

---

## OPTIONAL MODULES

  PURPOSE:
    Third-party integrations, plugins, and feature modules are optional.
    Core application functionality must start and remain healthy even when
    an optional module is unconfigured or its upstream is down.

  REQUIRED PATTERNS:
    - Each optional module implements a project module contract (e.g. AppModuleDefinition)
    - Register via centralized module registry — never import-throw at module load
    - isEnabled() checks configuration/env only — no network I/O at startup
    - checkHealth() probes upstream at request time only; must never throw during boot
    - Route/handler factories use lazy controller/client instantiation inside handlers
    - Integration env vars use empty defaults — never required for core boot
    - When API-shaped: expose capability list and per-module health endpoints
    - Return 503 with NOT_CONFIGURED code when disabled
    - Return 502 with UPSTREAM_ERROR code when upstream fails

  FORBIDDEN PATTERNS:
    - Constructors or top-level modules that connect to upstream services at import time
    - Throwing during import, registration, or router creation when not configured
    - Adding optional integration vars as required in core config schema
    - Hard-coding optional module navigation without capability gating (when UI exists)

  WEB UI (when project has frontend):
    - Register nav in project module-nav config with moduleId matching API id
    - Show optional module links; use Disabled state when module.enabled is false
    - Use unavailable/fallback component for disabled or unreachable modules
    - Use capability discovery hook or API for module availability

  NEW MODULE CHECKLIST:
    - {module-id}.module.ts / module definition — module contract
    - {module-id}.config.ts — isConfigured / isEnabled helper
    - {module-id}.health.ts — probe function
    - {module-id}.routes.ts — router/handler factory
    - Register in central optional-modules registry
    - Frontend nav entry (when applicable)
    - Document env vars in .env.example and API_REFERENCE.md

  NAMING CONVENTIONS (follow project; defaults when none exist):
    files             : kebab-case or snake_case per language convention
    classes           : PascalCase
    functions         : camelCase or snake_case per language convention
    constants         : SCREAMING_SNAKE_CASE
    types/interfaces  : PascalCase
    schema objects    : descriptive name + Schema/Model suffix
    UI components     : PascalCase
    hooks             : camelCase + use prefix (when applicable)

---

## LANGUAGE & TYPE SAFETY RULES

Strict typing and validation are mandatory where the language supports them.
Detect primary language(s) from project manifests before applying language-specific rules.

UNIVERSAL RULES (all languages):

  FORBIDDEN PATTERNS:
    - Untyped or dynamically bypassed types without justification (any, interface{}, unchecked casts)
    - Non-null assertion or force-unwrap without explanatory comment
    - Type coercion/casting without comment explaining why
    - Ignoring errors, exceptions, or promise rejections (floating promises)
    - Debug print statements in production code paths — use structured logger
    - Direct environment variable access without validated configuration layer
    - Suppressing compiler/linter warnings without @expect-error equivalent and explanation

  REQUIRED PATTERNS:
    - Return types explicitly declared on all exported functions (where language supports)
    - Schema objects as single source of truth; infer types from schemas where applicable
    - Discriminated unions / sum types / sealed hierarchies for complex state
    - Readonly/immutable structures where mutation is not intended
    - Generic constraints over unconstrained dynamic types

LANGUAGE-SPECIFIC RULES (apply when language is in use):

  TypeScript / JavaScript:
    tsconfig: strict, noUncheckedIndexedAccess, noImplicitReturns, exactOptionalPropertyTypes
    moduleResolution: bundler (frontend) or node16+ (backend)
    No any — use unknown and narrow. No process.env direct access.

  Python:
    type hints on all public functions; enforce with mypy, pyright, or ruff
    Pydantic or equivalent for config and request validation
    No bare except; no mutable default arguments

  Go:
    go vet and staticcheck clean
    Explicit error handling — never ignore returned errors
    Context propagation for cancellation and deadlines

  Rust:
    deny warnings in CI unless documented
    No unwrap/expect in production paths without justification
    Clippy clean per project configuration

  Java / Kotlin:
    Null-safety annotations or Optional for nullable values
    Bean validation or equivalent for request DTOs
    Explicit exception hierarchy for domain errors

  C# / .NET:
    Nullable reference types enabled
    FluentValidation or DataAnnotations for input validation

  CODE EXAMPLES:

    CORRECT — Schema as source of truth (TypeScript example):
      export const loginSchema = z.object({
        email   : z.string().email().toLowerCase().trim(),
        password: z.string().min(12),
        totpCode: z.string().length(6).optional(),
      });
      export type LoginRequest = z.infer<typeof loginSchema>;

    CORRECT — Explicit return type (Python example):
      def find_user_by_id(user_id: str) -> UserDto | None:
          ...

    WRONG — Never do this:
      def find_user(id):  # no types, swallows errors
          return db.query(f"SELECT * FROM users WHERE id = {id}")

---

## DATABASE RULES

APPLICABILITY: When the project uses a relational, document, or key-value data store.

  SCHEMA RULES:
    - Every entity MUST have: stable primary key, createdAt, updatedAt (or equivalent)
    - Soft deletes via deletedAt / deleted_at / is_deleted — never hard delete user data
    - All foreign keys explicitly defined with onDelete/on_delete behavior
    - Indexes on all foreign keys and frequently queried columns
    - Enums or constrained types for role, status, and categorical fields
    - Sensitive fields (password hashes, MFA secrets, tokens) NEVER returned by default

  QUERY RULES:
    - Always select only needed fields — never return secrets in list/detail queries
    - Use transactions for multi-step write operations
    - Paginate all list endpoints — default 20, max 100
    - Never use ambiguous single-record queries without unique constraints
    - Add query timeout via ORM middleware or connection config

  ORM / DATA ACCESS:
    - Prefer ORM or query builder (Prisma, SQLAlchemy, Django ORM, GORM, Hibernate, etc.)
    - Raw SQL requires explanatory review comment with parameterization justification
    - Migrations versioned and applied via project-documented command

  REFERENCE SCHEMA PATTERN (relational — adapt to project's ORM):

    User:
      id, email (unique), email_verified, password_hash, role, mfa_enabled, mfa_secret (encrypted),
      mfa_backup_codes (hashed), last_login_at, last_login_ip, failed_login_count, locked_until,
      created_at, updated_at, deleted_at

    Session:
      id, user_id (FK), refresh_token_hash (unique), user_agent, ip_address,
      expires_at, created_at, revoked_at

    AuditLog:
      id, user_id (FK nullable), action, resource, resource_id, metadata (JSON),
      ip_address, user_agent, created_at

---

## API DESIGN RULES

APPLICABILITY: When the project exposes HTTP or RPC APIs.

  versioning: URL prefix /api/v1/ or project-documented versioning scheme

  SUCCESS RESPONSE FORMAT:
    {
      "success": true,
      "data": { ... },
      "meta": {
        "total": 100,
        "page": 1,
        "limit": 20,
        "hasNextPage": true
      }
    }
    Note: meta is present on paginated responses only.

  ERROR RESPONSE FORMAT:
    {
      "success": false,
      "error": {
        "code": "AUTH_INVALID_CREDENTIALS",
        "message": "The email or password you entered is incorrect.",
        "details": []
      }
    }
    Note: details contains validation errors array if applicable.

  MINIMUM AUTH CAPABILITY SET (when building authentication):
    register, login, logout, refresh, MFA setup/verify/challenge/disable/backup,
    password reset request/confirm, email verification, session list/revoke

  API SECURITY RULES:
    - Auth endpoints rate limited at 10 req/15min per IP
    - Login response time constant regardless of user existence (prevent enumeration)
    - Password reset tokens expire in 1 hour, single use
    - Email verification tokens expire in 24 hours
    - All state-changing endpoints require CSRF protection (cookie-based auth)
    - Idempotency keys for critical mutating operations when documented

---

## FRONTEND RULES

APPLICABILITY: When the project includes a frontend or the user requests UI work.

  STACK DISCOVERY:
    Identify framework from project manifests (package.json, vite.config, next.config,
    angular.json, Cargo.toml + trunk, etc.). Follow the discovered stack — do not substitute.

  UNIVERSAL RULES:
    - Component boundaries: presentational vs container/smart components per project patterns
    - All form inputs use project form library with schema validation — no uncontrolled inputs
      without justification
    - Loading states required on all async actions
    - Error states displayed inline — never alert() or bare console for user-facing errors
    - Skeleton loaders for data-fetching components
    - Empty states designed for all list views
    - All interactive elements have accessible labels (aria-label, associated label elements)
    - Color contrast ratio minimum 4.5:1 for text
    - Never disable submit button solely for validation — show inline validation instead
    - No secrets, API keys, or private tokens in client bundle
    - Access token handling per Authentication & Security section

  STYLING:
    - Use project's styling system (Tailwind, CSS Modules, styled-components, MUI theme, etc.)
    - Follow Design System & Color Tokens section when applicable
    - Never hardcode design values outside theme/token configuration

  ROUTING & AUTH (when applicable):
    - Protected routes redirect unauthenticated users to login
    - MFA challenge route when MFA enabled and not yet verified
    - Role guard component/middleware for role-restricted views

  REFERENCE PATTERNS (examples only):

    React: ProtectedRoute, RoleGuard, axios/fetch client with refresh interceptor
    Vue: navigation guards, Pinia/Vuex auth store
    Svelte: stores + page load guards

---

## CONTAINER & INFRASTRUCTURE RULES

APPLICABILITY: When the project uses containers, orchestration, or infrastructure-as-code.
When the project has no containers: apply only when user requests containerization or
infrastructure work.

  CONTAINER SECURITY RULES:
    - Run application containers as non-root user where possible
    - Pin all base image versions — never use :latest in production
    - Multi-stage builds to minimize final image size and attack surface
    - No secrets in Dockerfile, compose files, or IaC — use env vars or secret stores
    - Health checks required for all stateful and long-running services
    - Networks defined explicitly — avoid implicit default networking in production

  DOCKER COMPOSE (example — when compose is project mechanism):
    - Explicit networks for service isolation
    - depends_on with health condition where supported
    - Environment variables from .env via ${VAR_NAME} syntax
    - Separate override file for development profiles

  KUBERNETES (example — when k8s is project mechanism):
    - Resource requests and limits defined
    - liveness and readiness probes on all deployments
    - Secrets via Secret resources or external secret operator
    - NetworkPolicies when security requirements demand

  INFRASTRUCTURE AS CODE (example — when terraform/pulumi is project mechanism):
    - State backend documented and locked
    - Variables for environment-specific values
    - No secrets in .tf files — use var files or secret stores
    - Plan before apply in automated contexts

  DOCKERFILE PATTERN (example — multi-stage):

    FROM [runtime]:[pinned-version] AS base

    FROM base AS deps
    # install dependencies
    ...

    FROM base AS builder
    ...

    FROM base AS production
    RUN adduser --disabled-password appuser
    USER appuser
    EXPOSE [port]
    CMD ["./start-command"]

---

## TESTING RULES

  FRAMEWORK: Discover from project (Jest, Vitest, pytest, go test, cargo test, JUnit,
  RSpec, xUnit, etc.). Use project-documented test command.

  COVERAGE THRESHOLDS (when coverage is measured):
    branches  : 80
    functions : 85
    lines     : 85
    statements: 85

  REQUIRED TEST TYPES:

    unit:
      - All service/use-case methods — mock repository and gateway boundaries
      - All utility functions
      - All schema validators (valid and invalid inputs)
      - RBAC middleware/guards (each role combination)

    integration:
      - All API endpoint happy paths
      - Auth flow: register → login → MFA → refresh → logout (when auth exists)
      - RBAC enforcement on protected routes
      - Rate limiting behavior

    security:
      - Injection attempts on all input-bearing endpoints
      - Token tampering detection (when auth exists)
      - Expired token rejection
      - Refresh token rotation and reuse detection (when applicable)

  EXECUTION:
    - Run tests via project-documented command
    - Prefer same runtime context as CI (container, virtualenv) when documented
    - Tests must be deterministic — no reliance on external services without mocks/containers

  REFERENCE JEST CONFIG (example — adapt to project's runner):

    roots: ['<rootDir>/src']
    testMatch: ['**/*.test.ts', '**/*_test.go', '**/test_*.py']
    coverageThresholds: { global: { branches: 80, functions: 85, lines: 85, statements: 85 } }

---

## CI/CD

Discover CI configuration from .github/workflows/, .gitlab-ci.yml, Jenkinsfile, etc.
Follow the project's existing pipeline patterns.

  CI WORKFLOW (reference — GitHub Actions example):

    triggers:
      pull_request: [main, develop]  # adapt to project's branch model
      push: [develop]

    jobs:
      lint-typecheck:
        - checkout
        - install dependencies (frozen lockfile)
        - run project lint command
        - run project typecheck command (when applicable)

      test:
        - checkout
        - start service containers (database, cache) when needed
        - run migrations in test context
        - run test suite with coverage

      security-scan:
        - dependency audit (npm audit, pip-audit, cargo audit, etc.)
        - filesystem/container vulnerability scan when applicable (Trivy, Snyk, etc.)

  DEPLOY WORKFLOW (reference — on merge to main/production branch):

    - Build artifacts per project mechanism
    - Run database migrations in deploy context
    - Deploy via discovered mechanism
    - Smoke test / health verification

  RULES:
    - CI must use pinned runtime versions matching production
    - Secrets via CI secret store — never in workflow files
    - Failed security scan at configured severity is a merge blocker

---

## ENVIRONMENT VARIABLES

  DEFAULT PATTERN (12-factor):
    Root .env for local/runtime injection
    .env.example for documentation (never committed secrets)

  DISCOVERY:
    Required variables come from: .env.example, config schema, validation code, RUNBOOK

  VALIDATION:
    All environment variables consumed at startup MUST be validated through a schema layer.
    Examples by stack:
      TypeScript: Zod in config/env.ts
      Python: Pydantic Settings
      Go: envconfig, viper with validation
      Rust: config crate with deserialize + validate

  VARIABLE GROUPS (document all that apply):
    - Data store connection strings
    - Cache / message broker URLs
    - Auth signing keys (asymmetric preferred)
    - Encryption keys for secrets at rest
    - CORS / allowed origins
    - Feature flags and optional module config
    - External service API keys (optional integrations)

  RULES:
    - Never commit .env with real secrets
    - New variables documented in .env.example and README in same PR
    - Invalid configuration must fail fast at startup with clear error message

  REFERENCE ENV SCHEMA (TypeScript/Zod example):

    const envSchema = z.object({
      NODE_ENV    : z.enum(['development', 'test', 'production']),
      PORT        : z.coerce.number().default(8080),
      DATABASE_URL: z.string().url(),
      ...
    });

---

## CODE QUALITY

  GENERAL:
    - Functions must be 40 lines or fewer — extract if longer
    - Files must be 300 lines or fewer — split by responsibility if longer
    - Cyclomatic complexity 10 or fewer per function
    - No magic numbers — use named constants
    - No commented-out code committed to repository
    - Every TODO must include: // TODO(yourname): description - Issue #XXX
      (or language-appropriate equivalent)
    - All async operations must handle errors (try/catch, Result type, error returns)
    - Follow project linter and formatter configuration (eslint, ruff, golint, rustfmt, etc.)

  COMMIT FORMAT: Conventional Commits — type(scope): description

    types: feat, fix, docs, style, refactor, test, chore, security

    examples:
      feat(auth): implement TOTP MFA setup flow
      security(auth): rotate refresh tokens on every use
      fix(rbac): correct viewer role permission for dashboard

  PR CHECKLIST:
    - [ ] Tests added/updated for all changes
    - [ ] No new compiler/linter errors or warnings
    - [ ] Sensitive data not logged or exposed in responses
    - [ ] Environment variables documented in .env.example
    - [ ] Database migrations are backwards compatible (when applicable)
    - [ ] API changes documented (when applicable)
    - [ ] Security implications considered

---

## DOCUMENTATION RULES

  MANDATORY FILES (for user-facing systems and services):
    - README.md        — Source of truth for setup, architecture, workflows, and conventions
    - USER_GUIDE.md    — End-user flows, screenshots, FAQs, troubleshooting
    - API_REFERENCE.md — Endpoint contracts, auth requirements, request/response examples, error catalog
    - ARCHITECTURE.md  — Component boundaries, data flow, trust boundaries, sequence diagrams
    - CHANGELOG.md     — Human-readable release notes and migration callouts
    - RUNBOOK.md       — Deployment, rollback, incident triage, on-call diagnostics

  SCALE-DOWN (libraries, CLIs, small tools):
    README.md is always required. Other files may be omitted with explicit user approval.
    Document the reduced set in README.

  SYNCHRONIZATION POLICY:
    - Any code change that alters behavior MUST update relevant documentation in the same PR
    - Any file or folder addition/removal/rename MUST update README.md project tree and related docs
    - Any new environment variable MUST be documented in root .env.example and README
    - Any API contract change MUST update API_REFERENCE.md and integration examples
    - Any auth/security change MUST update security sections in README and runbook checklists
    - PRs are incomplete until docs are updated and reviewer-verifiable

  COMMENTING POLICY:

    FILE HEADERS REQUIRED:
      - Every source file must begin with a concise header comment describing purpose,
        ownership scope, and key dependencies
      - Header comments should include why the file exists, not just what it contains

    FUNCTION COMMENTS REQUIRED:
      - All exported functions, classes, and public components require doc comments
        describing intent, inputs, outputs, side effects, and failure modes
      - Complex private functions require explanatory comments

    INLINE COMMENT RULES:
      - Comment business rules, security assumptions, and non-obvious tradeoffs
      - Do not add noisy comments that restate obvious code
      - Comment all TODOs with owner and tracking issue

    FORBIDDEN:
      - No stale comments that contradict implementation
      - No commented-out dead code in committed files
      - No undocumented magic constants in critical paths

  REQUIRED README SECTIONS:
    - Project overview and goals
    - Tech stack and architecture summary
    - Repository structure map
    - Bootstrap, environment setup, and documented runtime commands
    - Security model (when auth exists: auth, MFA, RBAC, token handling)
    - Testing strategy and quality gates
    - Deployment and operations basics
    - Contribution workflow and documentation expectations
    - Glossary of domain and platform terms

  PR DOCUMENTATION CHECKLIST:
    - [ ] README.md updated for all setup, behavior, or structure changes
    - [ ] USER_GUIDE.md updated for UX or workflow changes
    - [ ] API_REFERENCE.md updated for endpoint or schema changes
    - [ ] ARCHITECTURE.md updated for boundary or topology changes
    - [ ] CHANGELOG.md entry added
    - [ ] New/modified files include required header and function comments
    - [ ] Comments reviewed for accuracy against implementation

---

## SECURITY CHECKLIST

Run this checklist before every release. Every unchecked item is a release blocker.
Adapt checklist items to project's stack; principles are mandatory.

  AUTHENTICATION (when auth exists):
    - [ ] Access tokens use asymmetric signing in production
    - [ ] Access tokens expire in 15 minutes or less
    - [ ] Refresh tokens use HTTP-only secure cookies or equivalent
    - [ ] Refresh token rotation is enabled
    - [ ] Token reuse triggers immediate family/session revocation
    - [ ] Passwords hashed with adaptive algorithm at minimum cost equivalent to bcrypt 12
    - [ ] MFA secrets encrypted at rest
    - [ ] Account lockout after failed login attempts

  API (when HTTP API exists):
    - [ ] All protected endpoints have authentication middleware
    - [ ] All endpoints have appropriate rate limiting
    - [ ] All request bodies validated with schema validation
    - [ ] CORS restricted to known origins
    - [ ] Security headers enabled via middleware or gateway
    - [ ] No sensitive data in logs
    - [ ] Error messages do not leak stack traces in production
    - [ ] All database queries parameterized via ORM/query builder

  INFRASTRUCTURE:
    - [ ] Containers run as non-root (when containers used)
    - [ ] Secrets in environment variables or secret store, not source code
    - [ ] Dependencies audited (project package manager audit command)
    - [ ] Base images and runtime versions pinned to specific versions
    - [ ] Database not publicly accessible without authentication
    - [ ] Cache and message broker password protected (when applicable)

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

_GENERAL_CLAUDE.md — Single source of truth for all AI-assisted development on this project._
_Last structural revision: initial generic engineering rules derived from CLAUDE.md_
_All corrections are appended to the Correction Log with dates and sequential IDs._
