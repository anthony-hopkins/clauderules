# TypeScript & JavaScript Rules

**Applies when:** editing TypeScript or JavaScript (`.ts`, `.tsx`, `.js`, `.jsx`).

Source: GENERAL_CLAUDE.md § Language & Type Safety Rules.

## Universal (apply here too)

**Forbidden:** any without justification, ignored promises, console.log in production paths, direct process.env, @ts-ignore without explanation.

**Required:** explicit return types on exports, schema-as-source-of-truth, discriminated unions for complex state.

## TypeScript config

- strict, noUncheckedIndexedAccess, noImplicitReturns, exactOptionalPropertyTypes
- moduleResolution: bundler (frontend) or node16+ (backend)

## Patterns

- No `any` — use `unknown` and narrow
- Env via validated `config/env.ts` (Zod)
- Infer types from Zod schemas: `type X = z.infer<typeof xSchema>`
