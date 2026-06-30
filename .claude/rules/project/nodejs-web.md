# Node Web Rules

**Applies when:** working in `apps/web/**` (React + Vite + Tailwind frontend), or editing `tailwind.config.*` / `globals.css`.

Project-specific rules for `apps/web` (React 18 + Vite + TypeScript).
Source: CLAUDE.md §§ Design System & Color Tokens, Frontend Rules. Generic versions: `frontend.md`, `design-tokens.md`.

## Stack

framework React 18 + Vite + TS; styling Tailwind v3 + shadcn/ui; state Zustand (client) + TanStack Query v5 (server);
routing React Router v6; forms React Hook Form + Zod resolvers; http Axios with interceptors.

## Design tokens (canonical — never hardcode hex in components)

| Token | Value | Use |
|-------|-------|-----|
| background | #1a1a2e | Page background |
| surface | #16213e | Cards/panels |
| surface_elevated | #0f3460 | Modals/dropdowns |
| primary | #39FF14 | Neon green — CTAs, active |
| primary_hover | #2ecc0f | Hover |
| primary_muted | #1a7a08 | Badges |
| accent | #9B59B6 | Purple — secondary |
| accent_hover | #8e44ad | Hover |
| text_primary | #FFFFFF | Body text |
| text_secondary | #A0AEC0 | Muted text |
| border | #2D3748 | Borders |
| error | #FC8181 | Errors |
| warning | #F6E05E | Warnings |
| success | #68D391 | Success |
| info | #63B3ED | Info |

Typography: Inter (sans), JetBrains Mono (mono), 16px base. Radius: `rounded-lg` (8px) default, `rounded-xl` (12px) cards.
Glow shadow: `0 0 20px rgba(57,255,20,0.15)`. Colors live in `tailwind.config.ts` + CSS variables in `globals.css` only.

## Component rules

- All inputs via React Hook Form — no uncontrolled inputs; Zod schema defined before the component.
- Loading states on all async actions; inline error states — never `alert()`.
- Skeleton loaders for data fetching; empty states for all lists.
- aria-labels on interactive elements; 4.5:1 contrast minimum.
- Never disable submit — show inline validation instead.
- shadcn/ui: init with custom style (no default theme); files under `components/ui/` are not hand-edited.

## Axios (`src/lib/apiClient.ts`)

`withCredentials: true`; request interceptor attaches in-memory access token; response interceptor refreshes on
401 via `/api/v1/auth/refresh`, queues concurrent failures, logs out and redirects to `/login` on refresh failure.

## Route guards

- `ProtectedRoute`: redirect to `/login` when unauthenticated; redirect to `/mfa/challenge` when `requireMfa` and MFA enabled but unverified.
- `RoleGuard`: render fallback or redirect to `/unauthorized` when `user.role` not in `allowedRoles`.
