# Node API Rules

**Applies when:** working in `apps/api/**` (Express + Prisma + TypeScript API).

Project-specific rules for `apps/api` (Express + TypeScript + Prisma).
Source: CLAUDE.md §§ Authentication & Security, RBAC, Security Headers, Input Security, Rate Limiting, API Design.
Generic versions: `auth-security.md`, `api-design.md`, `security-headers.md`. This file pins the concrete stack.

## Authentication & sessions

- **Access token:** RS256 (never HS256 in prod), 15m max, memory-only on client, `Authorization: Bearer`.
- **Refresh token:** RS256, 7d, HTTP-only Secure SameSite=Strict cookie, rotation on every use, family tracking, Redis blocklist.
- **Passwords:** bcrypt ≥12 rounds, min 12 chars, upper+lower+number+special, HaveIBeenPwned check on registration.
- **MFA:** TOTP (RFC 6238) via `otplib`, QR via `qrcode`, `mfaSecret` AES-256-GCM encrypted at rest, 10 bcrypt-hashed backup codes.
- **Sessions:** bind to user-agent + IP, concurrent session limits per role, force-logout endpoints, last-login + suspicious-login detection.

## RBAC

Roles `admin` → inherits `user` → inherits `viewer`. Roles in JWT claims AND verified server-side every request.
`authenticate.ts` runs before `authorize.ts` always; ownership checks separate from role checks; audit-log every escalation attempt.

```ts
router.get('/profile', authenticate, controller.getProfile);
router.delete('/users/:id', authenticate, authorize(['admin']), controller.deleteUser);
router.patch('/users/:id', authenticate, authorizeOwnerOrRole(['admin']), controller.updateUser);
```

## Security headers (helmet)

CSP (strict, no `unsafe-inline`), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
`Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`,
`Strict-Transport-Security: max-age=31536000; includeSubDomains`.

## Input security

Validate ALL input with Zod (no exceptions). DOMPurify (frontend) + xss-clean (backend). Prisma parameterized
queries only — raw SQL needs a review comment. Validate upload MIME server-side. Strip unknown fields before processing.

## Rate limiting (express-rate-limit + rate-limit-redis)

| Tier | Window | Max |
|------|--------|-----|
| auth_endpoints | 15m | 10 |
| api_general | 1m | 100 |
| api_authenticated | 1m | 300 |

Progressive delays + IP blocking after repeated violations.

## API design

Versioning `/api/v1/`. Success `{ success: true, data, meta? }` (`meta` only on paginated). Error
`{ success: false, error: { code, message, details } }`.

Auth endpoints: register, login, logout, refresh, mfa/setup, mfa/verify, mfa/challenge, mfa/disable, mfa/backup,
password/reset-request, password/reset, email/verify, GET sessions, DELETE sessions/:id, DELETE sessions.

Security: auth endpoints 10 req/15min per IP; constant-time login responses; reset tokens 1h single-use;
email verification 24h; CSRF on state-changing endpoints.

## TypeScript

Zod schema as source of truth (`type X = z.infer<typeof xSchema>`), explicit return types on exports, no `any`,
env via validated `config/env.ts`. See `stacks/lang-typescript.md`.
