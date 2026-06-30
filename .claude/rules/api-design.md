# API Design Rules

**Applies when:** designing or editing HTTP APIs — routes, controllers, handlers, or OpenAPI/Swagger specs.

Source: GENERAL_CLAUDE.md § API Design Rules.

## Versioning

URL prefix `/api/v1/` or project-documented scheme.

## Success response

```json
{
  "success": true,
  "data": { },
  "meta": { "total": 100, "page": 1, "limit": 20, "hasNextPage": true }
}
```

`meta` only on paginated responses.

## Error response

```json
{
  "success": false,
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Human-readable message.",
    "details": []
  }
}
```

## Minimum auth capabilities (when building auth)

register, login, logout, refresh, MFA setup/verify/challenge/disable/backup, password reset, email verify, session list/revoke.

## API security

- Auth endpoints: 10 req/15min per IP
- Constant-time login responses (prevent enumeration)
- Password reset: 1 hour, single use
- Email verification: 24 hours
- CSRF on state-changing endpoints (cookie-based auth)
- Idempotency keys for critical mutating ops when documented
