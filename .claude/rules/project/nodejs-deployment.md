# Node Deployment Rules (Docker Compose)

**Applies when:** deploying the Node stack, or editing Compose files, `apps/*/Dockerfile`, or the root `.env`/`.env.example`.

Project-specific deployment for the Node fullstack scaffold. Source: CLAUDE.md §§ Deployment Configuration Protocol,
Docker Rules, Environment Variables. Generic protocol + 12-step checklist + D-01–D-08: `deployment.md` (always run it).
This file pins the concrete compose stack and commands.

## Governing files

`docker-compose.yml` (authoritative), `docker-compose.override.yml` (dev overrides), root `.env` (runtime truth),
`.env.example` (docs only). `docker-compose.yml` is the ONLY deployment mechanism (Rule D-01).

## Pre-deploy specifics (in addition to deployment.md steps 1–12)

- Pinned images: `postgres:16-alpine`, `redis:7-alpine`, `node:20-alpine`, `nginx:alpine` — never `:latest`.
- Health checks on `postgres` and `redis`. Explicit `app_network` (no default bridge).
- API Dockerfile creates and switches to non-root `appuser` before `EXPOSE`/`CMD`.
- No hardcoded secrets — all sensitive values reference `.env` via `${VAR_NAME}` (Rule D-05: stop and alert if found).

## Commands (V2 CLI — never `docker-compose`)

```bash
docker compose up -d --build                              # standard deploy
docker compose ps                                         # status
docker compose logs -f <service>                          # logs
docker compose run --rm api pnpm prisma migrate deploy    # migrations (inside container)
docker compose run --rm api pnpm test                     # tests
docker compose down                                       # stop (keep volumes)
docker compose down -v                                    # DESTRUCTIVE — explicit user confirmation every time (D-08)
```

## Multi-stage Dockerfiles

- `apps/api/Dockerfile`: base → deps → builder (`prisma generate`, `pnpm build`) → production (non-root `appuser`, `node dist/server.js`).
- `apps/web/Dockerfile`: base → deps → builder (`pnpm build` with `VITE_API_URL` arg) → `nginx:alpine` serving `/usr/share/nginx/html`.

## Service topology

postgres (healthcheck `pg_isready`), redis (`--requirepass`, healthcheck `redis-cli ping`), api (`depends_on`
postgres+redis healthy), web (`depends_on` api). Dev override adds hot-reload volumes, exposed debug ports, pgadmin.

## Required env vars (root `.env`)

PostgreSQL (`POSTGRES_USER/PASSWORD/DB`), `API_URL`, `REDIS_PASSWORD`, JWT RS256 key pairs
(`JWT_ACCESS_PRIVATE_KEY`, `JWT_ACCESS_PUBLIC_KEY`, `JWT_REFRESH_PRIVATE_KEY`, `JWT_REFRESH_PUBLIC_KEY`),
`JWT_ACCESS_EXPIRY`, `JWT_REFRESH_EXPIRY`, `MFA_ENCRYPTION_KEY` (64 hex), `APP_NAME`, SMTP group, `CORS_ORIGIN`,
`BCRYPT_ROUNDS`, `RATE_LIMIT_WINDOW_MS`, `RATE_LIMIT_MAX`, `VITE_API_URL`, `HIBP_API_KEY`.
Validated via Zod in `apps/api/src/config/env.ts`; invalid env exits the process.
