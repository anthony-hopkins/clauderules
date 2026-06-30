# Node Fullstack — Project Structure & Architecture

**Applies when:** working anywhere in the Node fullstack scaffold (`apps/**`, `pnpm-workspace.yaml`, root `package.json`).

Project-specific rules for the enterprise Node.js fullstack scaffold (`apps/api` + `apps/web`).
Source: CLAUDE.md §§ Project Structure, Runtime Model, Architecture Rules, Optional Modules.
Generic layering lives in `core.md`; this file prescribes the concrete project layout.

## Mandatory layout

```
root/
├── apps/
│   ├── api/   # Express REST API (Node.js + TypeScript)
│   │   ├── prisma/ (schema.prisma, migrations/, seed.ts)
│   │   └── src/
│   │       ├── config/ (env.ts, database.ts, redis.ts, logger.ts)
│   │       ├── modules/<feature>/ (controller, service, repository, routes, schema, types, test)
│   │       ├── middleware/ (authenticate, authorize, validate, rateLimiter, errorHandler, requestLogger, sanitize)
│   │       ├── shared/ (errors/, types/, utils/)
│   │       ├── app.ts  # Express app setup (no listen here)
│   │       └── server.ts
│   └── web/   # React + Vite + TypeScript frontend
│       └── src/ (assets, components/ui+layout+shared, features/<feature>, hooks, lib, providers, router, store, styles, types)
├── docker-compose.yml, docker-compose.override.yml, .env.example
├── pnpm-workspace.yaml, package.json
└── README.md, QUICK_START.md, USER_GUIDE.md, API_REFERENCE.md, ARCHITECTURE.md, RUNBOOK.md, CHANGELOG.md
```

Do not deviate from this tree without explicit user instruction. All future features follow the
`modules/<feature>/` (API) and `features/<feature>/` (web) pattern.

## Runtime model

`docker_compose_only`. Run api, web, postgres, redis via Docker Compose only — never directly on host.
Root `.env` is the runtime source of truth; app-level `.env.example` files are docs-only templates.
Operational commands use `docker compose`; tests/lint/typecheck run via `docker compose run`.

## Architecture (concrete)

Dependency direction: **Controller → Service → Repository → Prisma**.

- **Controller:** parse/validate request, call service, format response via `response.ts`. No business logic, no Prisma, no direct `throw` (use `next(error)`).
- **Service:** all business logic, orchestrate repositories, enforce invariants, throw `AppError` subclasses, `$transaction` for multi-step ops. No `req`/`res`/`next`, no direct Prisma.
- **Repository:** all Prisma interaction, mapping, query optimization. No business logic, no cross-repository calls.

## Optional modules

Core auth/users/settings must boot when an optional module (e.g. Open WebUI) is unconfigured or down.

- Implement `AppModuleDefinition` in `shared/modules/types.ts`; register via `registerAppModule()`; mount with `setupOptionalModules(app)`.
- `isEnabled()` checks env only; `checkHealth()` probes upstream at request time and never throws.
- `createRouter()` uses lazy controller/client instantiation inside handlers.
- Endpoints: `GET /api/v1/modules`, `GET /api/v1/{module}/health`. `503 OPEN_WEBUI_NOT_CONFIGURED` when disabled; `502 OPEN_WEBUI_ERROR` when upstream fails.
- Web: register nav in `apps/web/src/config/module-nav.ts`; show disabled badge; gate with `useModules()` / `useModule()`.
- Forbidden: import-time upstream connections, throwing during import/register/router creation, required env vars for optional integrations.

## Naming conventions

files kebab-case (`auth.service.ts`); classes PascalCase; functions camelCase; constants SCREAMING_SNAKE_CASE;
interfaces PascalCase with `I` prefix (`IUserRepository`); zod schemas camelCase + `Schema`; React components PascalCase; hooks `use` prefix.
