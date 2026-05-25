# CLAUDE.md — Enterprise Node.js Fullstack Application

> **AUTHORITY LEVEL: ABSOLUTE**
> This file is the single source of truth for all AI-assisted development on this project.
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
  15. TypeScript Rules
  16. Database Rules
  17. API Design Rules
  18. Frontend Rules
  19. Docker Rules
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

GOVERNING DEPLOYMENT FILES:
  ROOT DEPLOYMENT CONFIGURATION FILE : docker-compose.yml
  OVERRIDE FILE                       : docker-compose.override.yml
  ENVIRONMENT SOURCE                  : .env (root, single source of truth)
  ENVIRONMENT TEMPLATE                : .env.example (documentation only, not runtime)

The docker-compose.yml at the project root is the authoritative deployment configuration.
All services MUST be defined, configured, and deployed through this file.
Direct host-level execution of services is PROHIBITED (see Runtime Model).

PRE-DEPLOYMENT CHECKLIST — MANDATORY, IN ORDER:
Before any "docker compose up" or deploy command is executed, Claude MUST verify and complete
all of the following steps in sequence. Each step must be completed fully before proceeding.

  STEP 1 — Verify root .env file exists and is populated
    - Check that .env exists at project root
    - Verify ALL required variables in Section ENVIRONMENT VARIABLES are present
    - Verify NO required variable is empty (unless explicitly optional)
    - If any variable is missing or empty: STOP → ask user to provide value

  STEP 2 — Verify docker-compose.yml is present and structurally valid
    - Confirm file exists at project root
    - Confirm the service being deployed is defined in docker-compose.yml
    - Confirm all required environment variable references exist in the service block
    - Confirm depends_on conditions are correct for the service
    - If any issue found: STOP → report exact issue → ask user how to proceed

  STEP 3 — Verify Dockerfile exists for each application service
    - apps/api/Dockerfile must exist and use multi-stage build
    - apps/web/Dockerfile must exist and use multi-stage build
    - Confirm target stage matches environment (production vs deps)
    - If missing: STOP → generate Dockerfile per Section DOCKER RULES → confirm with user

  STEP 4 — Verify health checks are defined for all stateful services
    - postgres service must have healthcheck block
    - redis service must have healthcheck block
    - If missing: STOP → add health checks per Section DOCKER RULES → confirm with user

  STEP 5 — Verify network configuration
    - app_network must be explicitly defined under networks:
    - All services must be assigned to app_network
    - Default bridge network must NOT be used

  STEP 6 — Verify secrets and security posture
    - Confirm NO secrets are hardcoded in docker-compose.yml
    - Confirm NO secrets are hardcoded in any Dockerfile
    - Confirm all sensitive values reference .env variables using ${VAR_NAME} syntax
    - If any hardcoded secret found: STOP → do not proceed → alert user immediately

  STEP 7 — Verify base image versions are pinned
    - postgres must use postgres:16-alpine (not :latest)
    - redis must use redis:7-alpine (not :latest)
    - node base must use node:20-alpine (not :latest)
    - nginx must use nginx:alpine (not :latest)
    - If :latest is found anywhere: STOP → replace with pinned version → confirm with user

  STEP 8 — Verify non-root user configuration in application Dockerfiles
    - api Dockerfile must create and switch to non-root appuser
    - Confirm USER appuser appears before EXPOSE and CMD
    - If missing: STOP → add non-root user → confirm with user

  STEP 9 — Run deployment command
    - For production:  docker compose up -d --build
    - For development: docker compose up -d --build  (override auto-merged)
    - NEVER run services directly on host (no pnpm dev, no node server.ts on host)
    - NEVER use docker compose up without -d in automated/CI contexts

  STEP 10 — Run database migrations (if schema changes exist)
    - Command: docker compose run --rm api pnpm prisma migrate deploy
    - This runs INSIDE the container — never on host
    - Confirm migration succeeded before proceeding

  STEP 11 — Verify service health post-deployment
    - Command: docker compose ps
    - All services must show status: running (healthy) or running
    - Check logs for startup errors: docker compose logs [service]
    - If any service is unhealthy or exited: STOP → diagnose → report to user

  STEP 12 — Confirm deployment complete
    - Report to user: which services were deployed, their status, and any warnings

DEPLOYMENT COMMAND REFERENCE:

  # Standard production deployment
  docker compose up -d --build

  # View all service statuses
  docker compose ps

  # View logs for a specific service
  docker compose logs -f [service_name]

  # Run a one-off command inside a container
  docker compose run --rm [service_name] [command]

  # Run database migrations
  docker compose run --rm api pnpm prisma migrate deploy

  # Run tests inside container
  docker compose run --rm api pnpm test

  # Shut down all services (preserve volumes)
  docker compose down

  # Shut down all services and remove volumes — DESTRUCTIVE, ask user first
  docker compose down -v

  # Rebuild a single service
  docker compose up -d --build [service_name]

DEPLOYMENT RULES:
  Rule D-01: docker-compose.yml is the ONLY deployment mechanism. No exceptions.
  Rule D-02: Every variable consumed by a service MUST be defined in root .env.
  Rule D-03: "docker compose" (V2 CLI syntax) MUST be used. Never "docker-compose" (V1 hyphenated).
  Rule D-04: The Pre-Deployment Checklist is executed in full for EVERY deployment,
             including incremental redeployments of a single service.
  Rule D-05: If Step 6 reveals a hardcoded secret, ALL work stops immediately.
             The user is alerted before any other action is taken.
  Rule D-06: Database migrations run inside the container.
             Never run prisma migrate on the host.
  Rule D-07: If Claude is asked to deploy a service type not covered by this protocol,
             Claude MUST ask the user how to classify and configure it before proceeding.
  Rule D-08: docker compose down -v requires explicit user confirmation every time,
             without exception.

---

## DESIGN SYSTEM & COLOR TOKENS

All UI work MUST adhere to the following design tokens.
Never hardcode colors outside of tailwind.config.ts or CSS variables.

  COLOR TOKENS:
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

  TYPOGRAPHY:
    font_sans:   "'Inter', 'Segoe UI', sans-serif"
    font_mono:   "'JetBrains Mono', 'Fira Code', monospace"
    base_size:   "16px"
    scale:       "tailwind default (text-xs through text-9xl)"

  SPACING:        tailwind default 4px base scale
  BORDER RADIUS:  rounded-lg (8px) default, rounded-xl (12px) for cards
  SHADOW:         0 0 20px rgba(57,255,20,0.15) for primary glow effects

---

## PROJECT STRUCTURE

The following directory layout is MANDATORY for all new projects.
Never deviate from this structure without explicit instruction.

  root/
  ├── .github/
  │   └── workflows/
  │       ├── ci.yml                  # Lint, typecheck, test on PR
  │       └── deploy.yml              # Build + push Docker images on merge to main
  ├── apps/
  │   ├── api/                        # Express REST API (Node.js + TypeScript)
  │   │   ├── prisma/
  │   │   │   ├── schema.prisma       # Single source of truth for DB schema
  │   │   │   ├── migrations/         # Prisma migration history
  │   │   │   └── seed.ts             # Database seeder
  │   │   ├── src/
  │   │   │   ├── config/
  │   │   │   │   ├── env.ts          # Zod-validated environment variables
  │   │   │   │   ├── database.ts     # Prisma client singleton
  │   │   │   │   ├── redis.ts        # Redis client (token blocklist + rate limiting)
  │   │   │   │   └── logger.ts       # Pino logger configuration
  │   │   │   ├── modules/
  │   │   │   │   ├── auth/
  │   │   │   │   │   ├── auth.controller.ts
  │   │   │   │   │   ├── auth.service.ts
  │   │   │   │   │   ├── auth.repository.ts
  │   │   │   │   │   ├── auth.routes.ts
  │   │   │   │   │   ├── auth.schema.ts      # Zod request schemas
  │   │   │   │   │   ├── auth.types.ts
  │   │   │   │   │   └── auth.test.ts
  │   │   │   │   ├── users/
  │   │   │   │   │   ├── users.controller.ts
  │   │   │   │   │   ├── users.service.ts
  │   │   │   │   │   ├── users.repository.ts
  │   │   │   │   │   ├── users.routes.ts
  │   │   │   │   │   ├── users.schema.ts
  │   │   │   │   │   ├── users.types.ts
  │   │   │   │   │   └── users.test.ts
  │   │   │   │   └── [feature]/          # All future features follow this pattern
  │   │   │   ├── middleware/
  │   │   │   │   ├── authenticate.ts     # JWT verification middleware
  │   │   │   │   ├── authorize.ts        # RBAC role enforcement middleware
  │   │   │   │   ├── validate.ts         # Zod request validation middleware
  │   │   │   │   ├── rateLimiter.ts      # express-rate-limit + Redis store
  │   │   │   │   ├── errorHandler.ts     # Global error handler
  │   │   │   │   ├── requestLogger.ts    # HTTP request logging
  │   │   │   │   └── sanitize.ts         # Input sanitization middleware
  │   │   │   ├── shared/
  │   │   │   │   ├── errors/
  │   │   │   │   │   ├── AppError.ts     # Base custom error class
  │   │   │   │   │   ├── HttpError.ts    # HTTP-specific errors
  │   │   │   │   │   └── errorCodes.ts   # Centralized error code registry
  │   │   │   │   ├── types/
  │   │   │   │   │   ├── express.d.ts    # Express Request augmentation
  │   │   │   │   │   └── global.d.ts     # Global type declarations
  │   │   │   │   └── utils/
  │   │   │   │       ├── crypto.ts       # Hashing, token generation utilities
  │   │   │   │       ├── pagination.ts   # Cursor/offset pagination helpers
  │   │   │   │       └── response.ts     # Standardized API response builder
  │   │   │   ├── app.ts                  # Express app setup (no listen here)
  │   │   │   └── server.ts               # HTTP server entry point
  │   │   ├── .env.example            # Optional docs-only template
  │   │   ├── Dockerfile
  │   │   ├── jest.config.ts
  │   │   ├── tsconfig.json
  │   │   └── package.json
  │   └── web/                        # React + Vite + TypeScript frontend
  │       ├── src/
  │       │   ├── assets/
  │       │   ├── components/
  │       │   │   ├── ui/             # shadcn/ui generated components (DO NOT manually edit)
  │       │   │   ├── layout/
  │       │   │   │   ├── AppShell.tsx
  │       │   │   │   ├── Sidebar.tsx
  │       │   │   │   ├── TopNav.tsx
  │       │   │   │   └── PageWrapper.tsx
  │       │   │   └── shared/         # Reusable app-level components
  │       │   ├── features/
  │       │   │   ├── auth/
  │       │   │   │   ├── LoginPage.tsx
  │       │   │   │   ├── RegisterPage.tsx
  │       │   │   │   ├── MFASetupPage.tsx
  │       │   │   │   ├── MFAVerifyPage.tsx
  │       │   │   │   └── hooks/
  │       │   │   │       └── useAuth.ts
  │       │   │   └── [feature]/
  │       │   ├── hooks/
  │       │   ├── lib/
  │       │   │   ├── apiClient.ts    # Axios instance with interceptors
  │       │   │   ├── queryClient.ts  # TanStack Query client config
  │       │   │   └── utils.ts        # shadcn/ui cn() + misc helpers
  │       │   ├── providers/
  │       │   │   ├── AuthProvider.tsx
  │       │   │   ├── ThemeProvider.tsx
  │       │   │   └── QueryProvider.tsx
  │       │   ├── router/
  │       │   │   ├── index.tsx
  │       │   │   ├── ProtectedRoute.tsx
  │       │   │   └── RoleGuard.tsx
  │       │   ├── store/
  │       │   │   └── authStore.ts
  │       │   ├── styles/
  │       │   │   └── globals.css
  │       │   ├── types/
  │       │   │   └── api.ts
  │       │   ├── App.tsx
  │       │   └── main.tsx
  │       ├── .env.example
  │       ├── Dockerfile
  │       ├── index.html
  │       ├── tailwind.config.ts
  │       ├── tsconfig.json
  │       ├── vite.config.ts
  │       └── package.json
  ├── README.md
  ├── QUICK_START.md
  ├── USER_GUIDE.md
  ├── API_REFERENCE.md
  ├── ARCHITECTURE.md
  ├── RUNBOOK.md
  ├── CHANGELOG.md
  ├── docker-compose.yml
  ├── docker-compose.override.yml
  ├── .env.example
  ├── pnpm-workspace.yaml
  └── package.json

---

## RUNTIME MODEL

  mode: docker_compose_only

  REQUIREMENTS:
    - Run API, web, postgres, and redis via Docker Compose only
    - Do not document or support host runtime paths for api/web services
    - Root .env is the runtime source of truth
    - App-level .env.example files are optional documentation templates only

  COMMAND POLICY:
    - Operational commands use docker compose (up/down/logs/ps/run/exec)
    - Testing, linting, and typecheck are run via docker compose run

---

## AUTHENTICATION & SECURITY

These rules are NON-NEGOTIABLE and must be present in every project.

  STRATEGY: JWT Access Token + HTTP-only Refresh Token Cookie

  ACCESS TOKEN:
    algorithm : RS256              # Asymmetric — never use HS256 in production
    expiry    : 15m                # Short-lived, always 15 minutes maximum
    storage   : memory only        # NEVER localStorage, NEVER sessionStorage
    delivery  : Authorization: Bearer header

  REFRESH TOKEN:
    algorithm      : RS256
    expiry         : 7d
    storage        : HTTP-only, Secure, SameSite=Strict cookie
    rotation       : true          # Issue new refresh token on every use
    family_tracking: true          # Detect refresh token reuse attacks
    invalidation   : Redis blocklist

  PASSWORD:
    hashing       : bcrypt
    rounds        : 12             # Minimum 12 rounds, never lower
    min_length    : 12
    requirements  : uppercase + lowercase + number + special character
    breach_check  : true           # Check against HaveIBeenPwned API on registration

  MFA:
    method          : TOTP (RFC 6238)
    library         : otplib
    qr_generation   : qrcode
    secret_storage  : encrypted in DB using AES-256-GCM
    backup_codes:
      count  : 10
      hashed : true                # Store backup codes as bcrypt hashes
    enforcement: optional at registration, admin-enforceable per role

  SESSION SECURITY:
    - Bind refresh tokens to user-agent + IP fingerprint
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
    - Roles stored in JWT claims AND verified server-side on every request
    - Never trust client-provided role data
    - Middleware: authenticate.ts runs before authorize.ts always
    - Resource ownership checks separate from role checks
    - Audit log every privilege escalation attempt

  MIDDLEWARE USAGE EXAMPLES:

    // Protect route by authentication only:
    router.get('/profile', authenticate, controller.getProfile);

    // Protect route by role:
    router.delete('/users/:id', authenticate, authorize(['admin']), controller.deleteUser);

    // Protect route by role OR ownership:
    router.patch('/users/:id', authenticate, authorizeOwnerOrRole(['admin']), controller.updateUser);

---

## SECURITY HEADERS

  library: helmet

  REQUIRED HEADERS:
    - Content-Security-Policy (strict, no unsafe-inline)
    - X-Frame-Options: DENY
    - X-Content-Type-Options: nosniff
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: camera=(), microphone=(), geolocation=()
    - Strict-Transport-Security: max-age=31536000; includeSubDomains

---

## INPUT SECURITY

  - Validate ALL incoming data with Zod schemas — no exceptions.
  - Sanitize with DOMPurify on frontend, xss-clean on backend.
  - Parameterized queries only via Prisma — raw SQL requires an explanatory review comment.
  - File uploads: validate MIME type server-side, never trust Content-Type header.
  - Strip unknown fields from request bodies before processing.

---

## RATE LIMITING

  library: express-rate-limit + rate-limit-redis

  TIERS:
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

  DEPENDENCY DIRECTION: Controller → Service → Repository → Prisma

  CONTROLLER:
    responsibilities:
      - Parse and validate HTTP request (via validate middleware)
      - Call service layer — NO business logic here
      - Format and send HTTP response using response.ts utility
      - Handle HTTP-specific concerns ONLY
    forbidden:
      - Direct Prisma/database calls
      - Business logic or data transformation
      - Direct error throwing (use next(error))

  SERVICE:
    responsibilities:
      - All business logic lives here
      - Orchestrate repository calls
      - Enforce business rules and invariants
      - Throw AppError subclasses on failures
      - Handle transactions via Prisma $transaction
    forbidden:
      - Direct req/res/next references
      - Direct Prisma client usage (use repository)
      - Sending HTTP responses

  REPOSITORY:
    responsibilities:
      - All database interactions via Prisma
      - Data mapping between DB models and domain types
      - Query optimization and eager loading decisions
    forbidden:
      - Business logic
      - Calling other repositories directly (go through service)

---

## OPTIONAL MODULES

  PURPOSE:
    Dashboard integrations (Open WebUI, future third parties) are optional.
    Core auth, users, and settings must start and remain healthy even when
    an optional module is unconfigured or its upstream is down.

  REQUIRED PATTERNS:
    - Each optional module implements AppModuleDefinition in shared/modules/types.ts
    - Register via registerAppModule() in modules/register-optional-modules.ts
    - Mount routes with setupOptionalModules(app) — never import-throw at module load
    - isEnabled() checks env only — no network I/O
    - checkHealth() probes upstream at request time only; must never throw
    - createRouter() uses lazy controller/client instantiation inside handlers
    - Integration env vars use empty defaults in env.ts — never required for core boot
    - Expose GET /api/v1/modules (capability list) and GET /api/v1/{module}/health
    - Return 503 OPEN_WEBUI_NOT_CONFIGURED when disabled
    - Return 502 OPEN_WEBUI_ERROR when upstream fails

  FORBIDDEN PATTERNS:
    - Constructors or top-level route files that connect to upstream services
    - Throwing during import, registerAppModule(), or createRouter() when not configured
    - Adding optional integration vars as required in envSchema
    - Hard-coding optional module nav in Sidebar without module-nav.ts + useModules gating

  WEB UI:
    - Register nav in apps/web/src/config/module-nav.ts with moduleId matching API id
    - Always show optional module links in sidebar; use Disabled badge when module.enabled is false
    - Use ModuleUnavailable for disabled or unavailable module pages
    - Use useModules() / useModule(id, { probe: true }) for capability discovery

  NEW MODULE CHECKLIST:
    - apps/api/src/modules/{id}/{id}.module.ts  — AppModuleDefinition
    - apps/api/src/modules/{id}/{id}.config.ts  — isConfigured helper
    - apps/api/src/modules/{id}/{id}.health.ts  — probe function
    - apps/api/src/modules/{id}/{id}.routes.ts  — createXRouter() factory
    - registerAppModule in register-optional-modules.ts
    - apps/web/src/config/module-nav.ts entry
    - Document env vars in root .env.example and API_REFERENCE.md

  NAMING CONVENTIONS:
    files             : kebab-case               (auth.service.ts)
    classes           : PascalCase               (AuthService)
    functions         : camelCase                (generateTokenPair)
    constants         : SCREAMING_SNAKE_CASE     (JWT_EXPIRY)
    types/interfaces  : PascalCase, I prefix     (IUserRepository)
    zod schemas       : camelCase + Schema suffix (loginRequestSchema)
    react components  : PascalCase               (LoginPage.tsx)
    react hooks       : camelCase + use prefix   (useAuthStore.ts)

---

## TYPESCRIPT RULES

Strict TypeScript is mandatory. These rules are enforced via tsconfig.json.

  TSCONFIG REQUIRED SETTINGS:
    strict                          : true
    noUncheckedIndexedAccess        : true
    noImplicitReturns               : true
    noFallthroughCasesInSwitch      : true
    exactOptionalPropertyTypes      : true
    forceConsistentCasingInFileNames: true
    moduleResolution                : "bundler" for Vite frontend / "node16" for API

  FORBIDDEN PATTERNS:
    - any type — use unknown and narrow properly
    - Non-null assertion (!) without an explanatory comment
    - Type casting with 'as' without a comment explaining why
    - Ignoring promise rejections (floating promises)
    - console.log in production code — use logger.ts
    - process.env.X direct access — use validated config/env.ts
    - @ts-ignore — use @ts-expect-error with explanation if truly needed

  REQUIRED PATTERNS:
    - Return types explicitly declared on all exported functions
    - Zod schemas as single source of truth, infer types from them
    - Discriminated unions for complex state (AuthState, ApiResult)
    - Readonly arrays and objects where mutation is not intended
    - Generic constraints over any/unknown where possible

  CODE EXAMPLES:

    CORRECT — Zod schema as source of truth:
      export const loginSchema = z.object({
        email   : z.string().email().toLowerCase().trim(),
        password: z.string().min(12),
        totpCode: z.string().length(6).optional(),
      });
      export type LoginRequest = z.infer<typeof loginSchema>;

    CORRECT — Explicit return type, no any:
      export async function findUserById(
        id: string
      ): Promise<UserDto | null> {
        // ...
      }

    WRONG — Never do this:
      export async function findUser(id: any) {
        return await prisma.user.findFirst({ where: { id } } as any);
      }

---

## DATABASE RULES

  SCHEMA RULES:
    - Every model MUST have: id (cuid2), createdAt, updatedAt
    - Soft deletes via deletedAt DateTime? — never hard delete user data
    - All foreign keys explicitly defined with onDelete behavior
    - Indexes on all foreign keys and frequently queried columns
    - Enums defined in Prisma schema for role, status, etc.
    - Sensitive fields (mfaSecret, passwordHash) NEVER returned in queries by default

  QUERY RULES:
    - Always select only needed fields — never return passwordHash or mfaSecret
    - Use Prisma.$transaction for multi-step operations
    - Paginate all list endpoints — default 20, max 100
    - Never use findFirst without specifying unique constraints
    - Add database query timeout via Prisma middleware

  REQUIRED BASE PRISMA SCHEMA (prisma/schema.prisma):

    generator client {
      provider = "prisma-client-js"
    }

    datasource db {
      provider = "postgresql"
      url      = env("DATABASE_URL")
    }

    enum Role {
      ADMIN
      USER
      VIEWER
    }

    enum TokenFamily {
      REFRESH
      MFA_CHALLENGE
      PASSWORD_RESET
      EMAIL_VERIFICATION
    }

    model User {
      id                String     @id @default(cuid())
      email             String     @unique
      emailVerified     Boolean    @default(false)
      emailVerifiedAt   DateTime?
      passwordHash      String
      role              Role       @default(USER)
      mfaEnabled        Boolean    @default(false)
      mfaSecret         String?    // AES-256-GCM encrypted
      mfaBackupCodes    String[]   // bcrypt hashed
      lastLoginAt       DateTime?
      lastLoginIp       String?
      failedLoginCount  Int        @default(0)
      lockedUntil       DateTime?
      createdAt         DateTime   @default(now())
      updatedAt         DateTime   @updatedAt
      deletedAt         DateTime?
      sessions          Session[]
      auditLogs         AuditLog[]

      @@index([email])
      @@index([deletedAt])
    }

    model Session {
      id            String    @id @default(cuid())
      userId        String
      refreshToken  String    @unique  // hashed
      userAgent     String
      ipAddress     String
      expiresAt     DateTime
      createdAt     DateTime  @default(now())
      revokedAt     DateTime?
      user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)

      @@index([userId])
      @@index([refreshToken])
    }

    model AuditLog {
      id         String    @id @default(cuid())
      userId     String?
      action     String
      resource   String
      resourceId String?
      metadata   Json?
      ipAddress  String
      userAgent  String
      createdAt  DateTime  @default(now())
      user       User?     @relation(fields: [userId], references: [id], onDelete: SetNull)

      @@index([userId])
      @@index([action])
      @@index([createdAt])
    }

---

## API DESIGN RULES

  versioning: URL prefix /api/v1/

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
    Note: details contains Zod validation errors array if applicable.

  AUTH ENDPOINTS:
    POST   /api/v1/auth/register
    POST   /api/v1/auth/login
    POST   /api/v1/auth/logout
    POST   /api/v1/auth/refresh
    POST   /api/v1/auth/mfa/setup
    POST   /api/v1/auth/mfa/verify
    POST   /api/v1/auth/mfa/challenge
    POST   /api/v1/auth/mfa/disable
    POST   /api/v1/auth/mfa/backup
    POST   /api/v1/auth/password/reset-request
    POST   /api/v1/auth/password/reset
    POST   /api/v1/auth/email/verify
    GET    /api/v1/auth/sessions
    DELETE /api/v1/auth/sessions/:id
    DELETE /api/v1/auth/sessions

  API SECURITY RULES:
    - Auth endpoints rate limited at 10 req/15min per IP
    - Login response time constant regardless of user existence (prevent enumeration)
    - Password reset tokens expire in 1 hour, single use
    - Email verification tokens expire in 24 hours
    - All state-changing endpoints require CSRF protection

---

## FRONTEND RULES

  STACK:
    framework : React 18 + Vite + TypeScript
    styling   : Tailwind CSS v3 + shadcn/ui
    state     : Zustand (client state) + TanStack Query v5 (server state)
    routing   : React Router v6
    forms     : React Hook Form + Zod resolvers
    http      : Axios with interceptors

  TAILWIND CONFIG (tailwind.config.ts):

    import type { Config } from 'tailwindcss';
    export default {
      darkMode: ['class'],
      content: ['./index.html', './src/**/*.{ts,tsx}'],
      theme: {
        extend: {
          colors: {
            background : '#1a1a2e',
            surface    : '#16213e',
            elevated   : '#0f3460',
            primary: {
              DEFAULT : '#39FF14',
              hover   : '#2ecc0f',
              muted   : '#1a7a08',
            },
            accent: {
              DEFAULT : '#9B59B6',
              hover   : '#8e44ad',
              muted   : '#4a235a',
            },
            border : '#2D3748',
            ring   : '#39FF14',
          },
          fontFamily: {
            sans : ['Inter', 'Segoe UI', 'sans-serif'],
            mono : ['JetBrains Mono', 'Fira Code', 'monospace'],
          },
          boxShadow: {
            glow         : '0 0 20px rgba(57, 255, 20, 0.15)',
            'glow-lg'    : '0 0 40px rgba(57, 255, 20, 0.25)',
            'glow-accent': '0 0 20px rgba(155, 89, 182, 0.2)',
          },
          animation: {
            'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
          },
          keyframes: {
            pulseGlow: {
              '0%, 100%': { boxShadow: '0 0 20px rgba(57,255,20,0.15)' },
              '50%'      : { boxShadow: '0 0 40px rgba(57,255,20,0.35)' },
            },
          },
        },
      },
      plugins: [require('tailwindcss-animate')],
    } satisfies Config;

  GLOBALS CSS (src/styles/globals.css):

    @tailwind base;
    @tailwind components;
    @tailwind utilities;

    @layer base {
      :root {
        --background    : #1a1a2e;
        --surface       : #16213e;
        --elevated      : #0f3460;
        --primary       : #39FF14;
        --primary-hover : #2ecc0f;
        --accent        : #9B59B6;
        --accent-hover  : #8e44ad;
        --border        : #2D3748;
        --text-primary  : #FFFFFF;
        --text-secondary: #A0AEC0;
        --radius        : 0.5rem;
      }
      body {
        @apply bg-background text-white font-sans antialiased;
        background-color: var(--background);
      }
      * { @apply border-border; }
      ::selection {
        background-color: rgba(57, 255, 20, 0.2);
        color: #ffffff;
      }
      :focus-visible {
        @apply outline-none ring-2 ring-primary ring-offset-2 ring-offset-background;
      }
      ::-webkit-scrollbar       { width: 6px; height: 6px; }
      ::-webkit-scrollbar-track { background: var(--surface); }
      ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
      ::-webkit-scrollbar-thumb:hover { background: var(--primary); }
    }

    @layer components {
      .card-surface  { @apply bg-surface border border-border rounded-xl p-6; }
      .card-elevated { @apply bg-elevated border border-border rounded-xl p-6; }
      .btn-primary {
        @apply bg-primary text-background font-semibold
               hover:bg-primary-hover active:scale-95
               transition-all duration-200 rounded-lg
               focus-visible:ring-2 focus-visible:ring-primary;
      }
      .btn-accent {
        @apply bg-accent text-white font-semibold
               hover:bg-accent-hover active:scale-95
               transition-all duration-200 rounded-lg;
      }
      .btn-ghost {
        @apply bg-transparent text-text-secondary border border-border
               hover:border-primary hover:text-primary
               transition-all duration-200 rounded-lg;
      }
      .input-field {
        @apply bg-surface border border-border rounded-lg px-4 py-2.5
               text-white placeholder:text-text-secondary
               focus:border-primary focus:ring-1 focus:ring-primary
               transition-colors duration-200;
      }
      .glow-text {
        @apply text-primary;
        text-shadow: 0 0 20px rgba(57, 255, 20, 0.5);
      }
      .nav-link        { @apply text-text-secondary hover:text-primary transition-colors duration-200 flex items-center gap-2; }
      .nav-link-active { @apply text-primary; text-shadow: 0 0 10px rgba(57, 255, 20, 0.3); }
    }

  SHADCN/UI SETUP COMMAND:
    pnpm dlx shadcn-ui@latest init
    Select: TypeScript, Tailwind, CSS variables, NO default style (we use custom)

  SHADCN/UI REQUIRED CSS VARIABLE OVERRIDES (add to globals.css):
    --card              : var(--surface)
    --card-foreground   : var(--text-primary)
    --popover           : var(--elevated)
    --popover-foreground: var(--text-primary)
    --primary           : var(--primary)
    --primary-foreground: #0a0a0a
    --secondary         : var(--accent)
    --secondary-foreground: #ffffff
    --muted             : var(--surface)
    --muted-foreground  : var(--text-secondary)
    --destructive       : #FC8181
    --border            : var(--border)
    --input             : var(--surface)
    --ring              : var(--primary)

  COMPONENT RULES:
    - All form inputs use React Hook Form — no uncontrolled inputs
    - All forms have Zod validation schema defined before the component
    - Loading states required on all async actions
    - Error states displayed inline — never alert()
    - Skeleton loaders for all data-fetching components
    - Empty states designed and implemented for all list views
    - All interactive elements have accessible labels (aria-label)
    - Color contrast ratio minimum 4.5:1 for text
    - Never disable the submit button — show inline validation instead

  AXIOS CONFIG (src/lib/apiClient.ts):

    import axios from 'axios';
    import { useAuthStore } from '@/store/authStore';

    export const apiClient = axios.create({
      baseURL        : import.meta.env.VITE_API_URL,
      withCredentials: true,
      headers        : { 'Content-Type': 'application/json' },
    });

    apiClient.interceptors.request.use((config) => {
      const token = useAuthStore.getState().accessToken;
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    let isRefreshing = false;
    let failedQueue: Array<{ resolve: Function; reject: Function }> = [];

    apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            });
          }
          originalRequest._retry = true;
          isRefreshing = true;
          try {
            const { data } = await axios.post(
              `${import.meta.env.VITE_API_URL}/api/v1/auth/refresh`,
              {},
              { withCredentials: true }
            );
            useAuthStore.getState().setAccessToken(data.data.accessToken);
            failedQueue.forEach(({ resolve }) => resolve());
            return apiClient(originalRequest);
          } catch {
            failedQueue.forEach(({ reject }) => reject(error));
            useAuthStore.getState().logout();
            window.location.href = '/login';
          } finally {
            isRefreshing = false;
            failedQueue = [];
          }
        }
        return Promise.reject(error);
      }
    );

  PROTECTED ROUTE (src/router/ProtectedRoute.tsx):

    import { Navigate, useLocation } from 'react-router-dom';
    import { useAuthStore } from '@/store/authStore';

    interface ProtectedRouteProps {
      children  : React.ReactNode;
      requireMfa?: boolean;
    }

    export function ProtectedRoute({ children, requireMfa = false }: ProtectedRouteProps) {
      const { isAuthenticated, isMfaVerified, user } = useAuthStore();
      const location = useLocation();
      if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />;
      }
      if (requireMfa && user?.mfaEnabled && !isMfaVerified) {
        return <Navigate to="/mfa/challenge" state={{ from: location }} replace />;
      }
      return <>{children}</>;
    }

  ROLE GUARD (src/router/RoleGuard.tsx):

    import { Navigate } from 'react-router-dom';
    import { useAuthStore } from '@/store/authStore';
    import type { Role } from '@/types/api';

    interface RoleGuardProps {
      children     : React.ReactNode;
      allowedRoles : Role[];
      fallback?    : React.ReactNode;
    }

    export function RoleGuard({ children, allowedRoles, fallback }: RoleGuardProps) {
      const { user } = useAuthStore();
      if (!user || !allowedRoles.includes(user.role)) {
        return fallback ? <>{fallback}</> : <Navigate to="/unauthorized" replace />;
      }
      return <>{children}</>;
    }

---

## DOCKER RULES

  DOCKER SECURITY RULES:
    - Run all containers as non-root user
    - Pin all base image versions — never use :latest
    - Multi-stage builds to minimize final image size
    - No secrets in Dockerfile or docker-compose.yml — use .env files
    - Health checks required for all stateful services
    - Networks defined explicitly — never use default bridge

  DOCKER-COMPOSE.YML:

    version: '3.9'
    services:
      postgres:
        image: postgres:16-alpine
        restart: unless-stopped
        environment:
          POSTGRES_USER    : ${POSTGRES_USER}
          POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
          POSTGRES_DB      : ${POSTGRES_DB}
        volumes:
          - postgres_data:/var/lib/postgresql/data
        healthcheck:
          test    : ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
          interval: 10s
          timeout : 5s
          retries : 5
        networks:
          - app_network
        ports:
          - "5432:5432"

      redis:
        image: redis:7-alpine
        restart: unless-stopped
        command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
        volumes:
          - redis_data:/data
        healthcheck:
          test    : ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
          interval: 10s
          timeout : 5s
          retries : 5
        networks:
          - app_network
        ports:
          - "6379:6379"

      api:
        build:
          context   : ./apps/api
          dockerfile: Dockerfile
          target    : production
        restart: unless-stopped
        environment:
          NODE_ENV              : production
          PORT                  : 3001
          API_URL               : ${API_URL:-http://localhost:3001}
          DATABASE_URL          : postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
          REDIS_URL             : redis://redis:6379
          REDIS_PASSWORD        : ${REDIS_PASSWORD}
          JWT_ACCESS_PRIVATE_KEY: ${JWT_ACCESS_PRIVATE_KEY}
          JWT_ACCESS_PUBLIC_KEY : ${JWT_ACCESS_PUBLIC_KEY}
          JWT_REFRESH_PRIVATE_KEY: ${JWT_REFRESH_PRIVATE_KEY}
          JWT_REFRESH_PUBLIC_KEY: ${JWT_REFRESH_PUBLIC_KEY}
          JWT_ACCESS_EXPIRY     : ${JWT_ACCESS_EXPIRY:-15m}
          JWT_REFRESH_EXPIRY    : ${JWT_REFRESH_EXPIRY:-7d}
          MFA_ENCRYPTION_KEY    : ${MFA_ENCRYPTION_KEY}
          APP_NAME              : ${APP_NAME:-App}
          BCRYPT_ROUNDS         : ${BCRYPT_ROUNDS:-12}
          CORS_ORIGIN           : ${CORS_ORIGIN:-http://localhost}
          RATE_LIMIT_WINDOW_MS  : ${RATE_LIMIT_WINDOW_MS:-900000}
          RATE_LIMIT_MAX        : ${RATE_LIMIT_MAX:-100}
        depends_on:
          postgres:
            condition: service_healthy
          redis:
            condition: service_healthy
        ports:
          - "3001:3001"
        networks:
          - app_network

      web:
        build:
          context   : ./apps/web
          dockerfile: Dockerfile
          target    : production
          args:
            VITE_API_URL: ${VITE_API_URL:-http://localhost:3001}
        restart: unless-stopped
        expose:
          - "80"
        depends_on:
          - api
        networks:
          - app_network

    volumes:
      postgres_data:
      redis_data:

    networks:
      app_network:
        driver: bridge

  DOCKER-COMPOSE.OVERRIDE.YML:

    version: '3.9'
    services:
      postgres:
        ports:
          - "5432:5432"

      redis:
        ports:
          - "6379:6379"

      api:
        build:
          target: deps
        environment:
          NODE_ENV    : development
          API_URL     : ${API_URL:-http://localhost:3001}
          DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-changeme}@postgres:5432/${POSTGRES_DB:-appdb}
          REDIS_URL   : redis://redis:6379
          REDIS_PASSWORD: ${REDIS_PASSWORD:-changeme}
          CORS_ORIGIN : ${CORS_ORIGIN:-http://localhost:8000}
        volumes:
          - ./apps/api/src:/app/src:cached
          - ./apps/api/prisma:/app/prisma:cached
          - ./apps/api/tsconfig.json:/app/tsconfig.json:cached
        command: pnpm dev
        ports:
          - "0.0.0.0:3001:3001"
          - "0.0.0.0:9229:9229"

      web:
        build:
          context   : ./apps/web
          dockerfile: Dockerfile
          target    : deps
        environment:
          VITE_API_URL         : ""
          VITE_API_PROXY_TARGET: http://api:3001
        volumes:
          - ./apps/web/src:/app/src:cached
          - ./apps/web/index.html:/app/index.html:cached
          - ./apps/web/postcss.config.js:/app/postcss.config.js:cached
          - ./apps/web/vite.config.ts:/app/vite.config.ts:cached
          - ./apps/web/tailwind.config.ts:/app/tailwind.config.ts:cached
          - ./apps/web/tsconfig.json:/app/tsconfig.json:cached
        command: pnpm dev --host 0.0.0.0 --port 8000
        ports:
          - "0.0.0.0:8000:8000"

      pgadmin:
        image: dpage/pgadmin4:8
        restart: unless-stopped
        environment:
          PGADMIN_DEFAULT_EMAIL   : ${PGADMIN_EMAIL:-admin@localhost.com}
          PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin}
          PGADMIN_LISTEN_PORT     : 5050
        ports:
          - "5050:5050"
        depends_on:
          postgres:
            condition: service_healthy
        networks:
          - app_network
        volumes:
          - pgadmin_data:/var/lib/pgadmin

    volumes:
      pgadmin_data:

  APPS/API/DOCKERFILE:

    FROM node:20-alpine AS base
    RUN corepack enable && corepack prepare pnpm@latest --activate

    FROM base AS deps
    WORKDIR /app
    COPY package.json pnpm-lock.yaml ./
    RUN pnpm install --frozen-lockfile

    FROM base AS builder
    WORKDIR /app
    COPY --from=deps /app/node_modules ./node_modules
    COPY . .
    RUN pnpm prisma generate
    RUN pnpm build

    FROM base AS production
    WORKDIR /app
    ENV NODE_ENV=production
    COPY --from=builder /app/dist ./dist
    COPY --from=builder /app/node_modules ./node_modules
    COPY --from=builder /app/prisma ./prisma
    COPY package.json ./
    RUN addgroup -S appgroup && adduser -S appuser -G appgroup
    USER appuser
    EXPOSE 3001
    CMD ["node", "dist/server.js"]

  APPS/WEB/DOCKERFILE:

    FROM node:20-alpine AS base
    RUN corepack enable && corepack prepare pnpm@latest --activate

    FROM base AS deps
    WORKDIR /app
    COPY package.json pnpm-lock.yaml ./
    RUN pnpm install --frozen-lockfile

    FROM base AS builder
    WORKDIR /app
    COPY --from=deps /app/node_modules ./node_modules
    COPY . .
    ARG VITE_API_URL
    ENV VITE_API_URL=$VITE_API_URL
    RUN pnpm build

    FROM nginx:alpine AS production
    COPY --from=builder /app/dist /usr/share/nginx/html
    COPY nginx.conf /etc/nginx/conf.d/default.conf
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]

---

## TESTING RULES

  FRAMEWORK: Jest + ts-jest + Supertest

  COVERAGE THRESHOLDS:
    branches  : 80
    functions : 85
    lines     : 85
    statements: 85

  REQUIRED TEST TYPES:

    unit:
      - All service methods — mock repository layer
      - All utility functions
      - All Zod schemas (valid and invalid inputs)
      - RBAC middleware (each role combination)

    integration:
      - All API endpoint happy paths
      - Auth flow: register → login → MFA → refresh → logout
      - RBAC enforcement on protected routes
      - Rate limiting behavior

    security:
      - SQL injection attempt on all endpoints
      - JWT tampering detection
      - Expired token rejection
      - Refresh token rotation and reuse detection

  JEST CONFIG (jest.config.ts):

    import type { Config } from 'jest';
    const config: Config = {
      preset         : 'ts-jest',
      testEnvironment: 'node',
      roots          : ['<rootDir>/src'],
      testMatch      : ['**/*.test.ts'],
      moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
      },
      collectCoverageFrom: [
        'src/**/*.ts',
        '!src/**/*.d.ts',
        '!src/server.ts',
        '!src/config/**',
      ],
      coverageThresholds: {
        global: {
          branches  : 80,
          functions : 85,
          lines     : 85,
          statements: 85,
        },
      },
      setupFilesAfterFramework: ['<rootDir>/src/test/setup.ts'],
    };
    export default config;

---

## CI/CD

  CI WORKFLOW (.github/workflows/ci.yml):

    name: CI
    on:
      pull_request:
        branches: [main, develop]
      push:
        branches: [develop]

    jobs:
      lint-typecheck:
        name: Lint & Type Check
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: pnpm/action-setup@v3
            with:
              version: latest
          - uses: actions/setup-node@v4
            with:
              node-version: '20'
              cache: 'pnpm'
          - run: pnpm install --frozen-lockfile
          - run: pnpm -r lint
          - run: pnpm -r typecheck

      test-api:
        name: API Tests
        runs-on: ubuntu-latest
        services:
          postgres:
            image: postgres:16-alpine
            env:
              POSTGRES_PASSWORD: testpassword
              POSTGRES_DB      : testdb
            options: >-
              --health-cmd pg_isready
              --health-interval 10s
              --health-timeout 5s
              --health-retries 5
          redis:
            image: redis:7-alpine
            options: >-
              --health-cmd "redis-cli ping"
              --health-interval 10s
        steps:
          - uses: actions/checkout@v4
          - uses: pnpm/action-setup@v3
          - uses: actions/setup-node@v4
            with:
              node-version: '20'
              cache: 'pnpm'
          - run: pnpm install --frozen-lockfile
          - run: pnpm --filter api prisma migrate deploy
            env:
              DATABASE_URL: postgresql://postgres:testpassword@localhost:5432/testdb
          - run: pnpm --filter api test:coverage
            env:
              DATABASE_URL           : postgresql://postgres:testpassword@localhost:5432/testdb
              REDIS_URL              : redis://localhost:6379
              JWT_ACCESS_PRIVATE_KEY : test-access-private-key-base64
              JWT_ACCESS_PUBLIC_KEY  : test-access-public-key-base64
              JWT_REFRESH_PRIVATE_KEY: test-refresh-private-key-base64
              JWT_REFRESH_PUBLIC_KEY : test-refresh-public-key-base64
              MFA_ENCRYPTION_KEY     : 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef

      security-scan:
        name: Security Audit
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: pnpm/action-setup@v3
          - uses: actions/setup-node@v4
            with:
              node-version: '20'
              cache: 'pnpm'
          - run: pnpm install --frozen-lockfile
          - run: pnpm audit --audit-level=high
          - name: Run Trivy vulnerability scanner
            uses: aquasecurity/trivy-action@master
            with:
              scan-type: 'fs'
              scan-ref : '.'
              severity : 'CRITICAL,HIGH'

  DEPLOY WORKFLOW (.github/workflows/deploy.yml):

    name: Deploy
    on:
      push:
        branches: [main]

    jobs:
      deploy:
        name: Build & Deploy
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - name: Build and push Docker images
            run: |
              docker compose build
              # Push to your registry here
          - name: Run database migrations
            run: |
              docker compose run --rm api pnpm prisma migrate deploy

---

## ENVIRONMENT VARIABLES

  ROOT .ENV.EXAMPLE (single runtime source for Docker Compose):

    # PostgreSQL
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=changeme
    POSTGRES_DB=appdb

    # Application
    # NOTE: Compose injects NODE_ENV/PORT/DATABASE_URL/REDIS_URL at runtime.
    API_URL=http://localhost:3001

    # Redis
    REDIS_PASSWORD=changeme

    # JWT — RS256 Asymmetric Keys
    # Generate with: openssl genrsa -out private.pem 2048
    JWT_ACCESS_PRIVATE_KEY=           # RS256 private key (base64 encoded)
    JWT_ACCESS_PUBLIC_KEY=            # RS256 public key (base64 encoded)
    JWT_REFRESH_PRIVATE_KEY=          # RS256 private key for refresh tokens
    JWT_REFRESH_PUBLIC_KEY=           # RS256 public key for refresh tokens
    JWT_ACCESS_EXPIRY=15m
    JWT_REFRESH_EXPIRY=7d

    # MFA
    MFA_ENCRYPTION_KEY=               # 32-byte hex key for AES-256-GCM
    APP_NAME=YourAppName              # Shown in authenticator app

    # Email
    SMTP_HOST=
    SMTP_PORT=587
    SMTP_USER=
    SMTP_PASS=
    EMAIL_FROM=noreply@yourdomain.com

    # Security
    # Use localhost:8000 when Docker development profile override is active.
    CORS_ORIGIN=http://localhost
    BCRYPT_ROUNDS=12
    RATE_LIMIT_WINDOW_MS=900000
    RATE_LIMIT_MAX=100

    # Frontend
    VITE_API_URL=http://localhost:3001

    # HaveIBeenPwned
    HIBP_API_KEY=

  ENV VALIDATION (src/config/env.ts):

    import { z } from 'zod';

    const envSchema = z.object({
      NODE_ENV               : z.enum(['development', 'test', 'production']),
      PORT                   : z.coerce.number().default(3001),
      DATABASE_URL           : z.string().url(),
      REDIS_URL              : z.string(),
      JWT_ACCESS_PRIVATE_KEY : z.string().min(1),
      JWT_ACCESS_PUBLIC_KEY  : z.string().min(1),
      JWT_REFRESH_PRIVATE_KEY: z.string().min(1),
      JWT_REFRESH_PUBLIC_KEY : z.string().min(1),
      JWT_ACCESS_EXPIRY      : z.string().default('15m'),
      JWT_REFRESH_EXPIRY     : z.string().default('7d'),
      MFA_ENCRYPTION_KEY     : z.string().length(64),
      APP_NAME               : z.string().default('App'),
      BCRYPT_ROUNDS          : z.coerce.number().min(12).default(12),
      CORS_ORIGIN            : z.string().url(),
    });

    const parsed = envSchema.safeParse(process.env);
    if (!parsed.success) {
      console.error('Invalid environment variables:', parsed.error.flatten());
      process.exit(1);
    }

    export const env = parsed.data;

---

## CODE QUALITY

  GENERAL:
    - Functions must be 40 lines or fewer — extract if longer
    - Files must be 300 lines or fewer — split by responsibility if longer
    - Cyclomatic complexity 10 or fewer per function
    - No magic numbers — use named constants
    - No commented-out code committed to repository
    - Every TODO must include: // TODO(yourname): description - Issue #XXX
    - All async functions must handle errors (try/catch or .catch())

  COMMIT FORMAT: Conventional Commits — type(scope): description

    types: feat, fix, docs, style, refactor, test, chore, security

    examples:
      feat(auth): implement TOTP MFA setup flow
      security(auth): rotate refresh tokens on every use
      fix(rbac): correct viewer role permission for dashboard

  PR CHECKLIST:
    - [ ] Tests added/updated for all changes
    - [ ] No new TypeScript errors or warnings
    - [ ] No new ESLint errors
    - [ ] Sensitive data not logged or exposed in responses
    - [ ] Environment variables documented in .env.example
    - [ ] Database migrations are backwards compatible
    - [ ] API changes documented
    - [ ] Security implications considered

---

## DOCUMENTATION RULES

  MANDATORY FILES:
    - README.md        — Source of truth for setup, architecture, workflows, and conventions
    - USER_GUIDE.md    — End-user flows, screenshots, FAQs, troubleshooting
    - API_REFERENCE.md — Endpoint contracts, auth requirements, request/response examples, error catalog
    - ARCHITECTURE.md  — Component boundaries, data flow, trust boundaries, sequence diagrams
    - CHANGELOG.md     — Human-readable release notes and migration callouts
    - RUNBOOK.md       — Deployment, rollback, incident triage, on-call diagnostics

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
      - All exported functions, classes, and React components require doc comments
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
    - Docker Compose bootstrap and environment setup
    - Security model (auth, MFA, RBAC, token handling)
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

  AUTHENTICATION:
    - [ ] JWT uses RS256 asymmetric signing
    - [ ] Access tokens expire in 15 minutes or less
    - [ ] Refresh tokens are HTTP-only cookies
    - [ ] Refresh token rotation is enabled
    - [ ] Token reuse triggers immediate family revocation
    - [ ] Passwords hashed with bcrypt rounds 12 or greater
    - [ ] MFA secrets encrypted at rest with AES-256-GCM
    - [ ] Account lockout after failed login attempts

  API:
    - [ ] All endpoints have authentication middleware
    - [ ] All endpoints have appropriate rate limiting
    - [ ] All request bodies validated with Zod
    - [ ] CORS restricted to known origins
    - [ ] Helmet security headers enabled
    - [ ] No sensitive data in logs
    - [ ] Error messages do not leak stack traces in production
    - [ ] All database queries parameterized (Prisma)

  INFRASTRUCTURE:
    - [ ] Containers run as non-root
    - [ ] Secrets in environment variables, not source code
    - [ ] Dependencies audited (pnpm audit)
    - [ ] Base images pinned to specific versions
    - [ ] Database not publicly accessible
    - [ ] Redis password protected

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
  | TypeScript Rules           | MANDATORY        | No exceptions                   |
  | Docker Rules               | MANDATORY        | No exceptions                   |
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

_CLAUDE.md — Single source of truth for all AI-assisted development on this project._
_Last structural revision: initial enterprise migration from cursorrules.md_
_All corrections are appended to the Correction Log with dates and sequential IDs._