# Security Headers

**Applies when:** serving HTTP — configuring middleware, reverse proxies, or app entrypoints.

Source: GENERAL_CLAUDE.md § Security Headers.

Required when serving HTTP (web apps, APIs, gateways).

Implement via framework middleware (Helmet equivalent) or reverse proxy per RUNBOOK.

Required headers:
- Content-Security-Policy (strict, no unsafe-inline in production)
- X-Frame-Options: DENY (or CSP frame-ancestors)
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: camera=(), microphone=(), geolocation=()
- Strict-Transport-Security: max-age=31536000; includeSubDomains (HTTPS only)
