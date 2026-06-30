# Database Rules

**Applies when:** editing database schema, models, migrations, or data-access code.

Source: GENERAL_CLAUDE.md § Database Rules.

## Schema

- Stable primary key, createdAt, updatedAt on every entity
- Soft delete for user data (deletedAt / is_deleted) — never hard delete
- Explicit FKs with onDelete behavior; indexes on FKs and hot columns
- Enums/constrained types for role, status
- Never return password hashes, MFA secrets, tokens by default

## Queries

- Select only needed fields
- Transactions for multi-step writes
- Paginate lists: default 20, max 100
- No ambiguous single-record queries without unique constraints
- Query timeout via ORM middleware or connection config

## Data access

- Prefer ORM/query builder (Prisma, SQLAlchemy, GORM, Hibernate, etc.)
- Raw SQL requires review comment with parameterization justification
- Migrations versioned; apply via project-documented command

## Reference entities (relational)

User, Session, AuditLog — see GENERAL_CLAUDE.md for field patterns. Adapt to project's ORM.
