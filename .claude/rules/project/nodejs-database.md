# Node Database Rules (Prisma + PostgreSQL)

**Applies when:** editing the Prisma schema, models, or migrations in `apps/api/prisma/**` (or any `*.prisma`).

Project-specific rules for `apps/api/prisma`. Source: CLAUDE.md § Database Rules.
Generic version: `database.md`. This file pins the canonical Prisma schema.

## Schema rules

- Every model has `id` (cuid), `createdAt`, `updatedAt`.
- Soft deletes via `deletedAt DateTime?` — never hard delete user data.
- All FKs explicit with `onDelete`; indexes on FKs and frequently queried columns.
- Enums in schema for role/status/etc.
- Sensitive fields (`mfaSecret`, `passwordHash`) never returned by default.

## Query rules

- Select only needed fields; never return `passwordHash`/`mfaSecret`.
- `prisma.$transaction` for multi-step operations.
- Paginate all lists (default 20, max 100).
- Never `findFirst` without unique constraints; add query timeout via Prisma middleware.

## Required base schema

```prisma
generator client { provider = "prisma-client-js" }
datasource db { provider = "postgresql"; url = env("DATABASE_URL") }

enum Role { ADMIN USER VIEWER }
enum TokenFamily { REFRESH MFA_CHALLENGE PASSWORD_RESET EMAIL_VERIFICATION }

model User {
  id               String    @id @default(cuid())
  email            String    @unique
  emailVerified    Boolean   @default(false)
  emailVerifiedAt  DateTime?
  passwordHash     String
  role             Role      @default(USER)
  mfaEnabled       Boolean   @default(false)
  mfaSecret        String?   // AES-256-GCM encrypted
  mfaBackupCodes   String[]  // bcrypt hashed
  lastLoginAt      DateTime?
  lastLoginIp      String?
  failedLoginCount Int       @default(0)
  lockedUntil      DateTime?
  createdAt        DateTime  @default(now())
  updatedAt        DateTime  @updatedAt
  deletedAt        DateTime?
  sessions         Session[]
  auditLogs        AuditLog[]
  @@index([email])
  @@index([deletedAt])
}

model Session {
  id           String    @id @default(cuid())
  userId       String
  refreshToken String    @unique // hashed
  userAgent    String
  ipAddress    String
  expiresAt    DateTime
  createdAt    DateTime  @default(now())
  revokedAt    DateTime?
  user         User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  @@index([userId])
  @@index([refreshToken])
}

model AuditLog {
  id         String   @id @default(cuid())
  userId     String?
  action     String
  resource   String
  resourceId String?
  metadata   Json?
  ipAddress  String
  userAgent  String
  createdAt  DateTime @default(now())
  user       User?    @relation(fields: [userId], references: [id], onDelete: SetNull)
  @@index([userId])
  @@index([action])
  @@index([createdAt])
}
```

Migrations run inside the container: `docker compose run --rm api pnpm prisma migrate deploy`.
