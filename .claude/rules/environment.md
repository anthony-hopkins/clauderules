# Environment Variables

**Applies when:** adding or changing environment variables, config schemas, or `.env.example`.

Source: GENERAL_CLAUDE.md § Environment Variables.

## Pattern (12-factor)

- `.env` — local/runtime injection
- `.env.example` — documentation only, never real secrets

## Validation

All startup env vars MUST pass schema validation:
- TypeScript: Zod in config/env.ts
- Python: Pydantic Settings
- Go: envconfig / viper
- Rust: config crate + validate

## Variable groups

Document: data store, cache/broker, auth keys, encryption keys, CORS, feature flags, optional integrations.

## Rules

- Never commit .env with secrets
- New vars in .env.example + README in same PR
- Invalid config → fail fast at startup with clear error
