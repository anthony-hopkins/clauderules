# Core Engineering Rules

**Applies when:** ALWAYS. This file is imported by the root `CLAUDE.md` and applies to every task — never gate it on file type.

Follow **GENERAL_CLAUDE_CORE.md** at the repository root with ABSOLUTE authority.

- Full reference: `GENERAL_CLAUDE.md`
- Scoped detail (generic): sibling rules in `.claude/rules/`
- Stack-specific rules: `.claude/rules/stacks/` (read when working in that language/framework)
- Project-specific rules: `.claude/rules/project/` (read when working on this project's matching files)
- On conflict: **Core > scoped rule > GENERAL_CLAUDE.md examples**
- Project-specific configuration NEVER belongs in the core or Prime Directives — keep it in `project/`.

## Prime Directives (summary)

1. NEVER break, skip, or approximate rules.
2. NEVER assume intent — ASK FIRST.
3. NEVER change outside explicit scope (see Scope Discipline).
4. NEVER override a rule without the Override Protocol (both keys).
5. NEVER deploy without the 12-step deployment checklist (see `deployment.md`).
6. NEVER output a change without passing the Pre-Output Self-Audit.
7. NEVER repeat mistakes — append CORRECTION ENTRIES to GENERAL_CLAUDE_CORE.md.
8. User behavior-changing input becomes permanent law.

## Scope, override & self-audit (summary)

Full text in GENERAL_CLAUDE_CORE.md / CLAUDE.md. In brief:

- **Scope Discipline** — When told to do an enumerated subset ("do 1,2,6 ONLY"), change only the
  lines each item requires. No reformatting, renaming, extra imports, message/return/control-flow
  changes, or "helpful extras". If a requested change needs an unrequested one, STOP and ask.
- **Override Protocol** — A rule is relaxed only when BOTH keys hold: (1) the user explicitly names
  the rule to override, and (2) the agent re-asks a yes/no and gets an explicit "yes" in a separate
  message first. Then log a CORRECTION ENTRY before resuming. No implied or blanket consent.
- **Pre-Output Self-Audit** — Before sending any change: map every change to a requested item; drop
  anything unmapped; confirm no unused imports/symbols and no unrequested message/return/flow change.
- **Enforcement is external** — Back rules with linters, pre-commit hooks, and CI that block. Prose
  reduces violations; tooling is what makes compliance near-certain.

## When blocked

Use the Clarification Protocol format from GENERAL_CLAUDE_CORE.md. No best guesses.

## Architecture (summary)

Handler → Service → Repository → DataStore. No business logic in handlers. No DB in services.

## Code quality (summary)

Functions ≤40 lines, files ≤300 lines, complexity ≤10. Conventional Commits. Follow project linter.
