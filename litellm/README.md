# Governance Rules & LiteLLM / Open WebUI Integration

This directory holds **governance artifacts and reference code** for enforcing the Prime Directives
via LiteLLM and Open WebUI. It does **not** define or deploy a stack — use your existing LiteLLM
and Open WebUI installation and follow the integration guides below.

> **Honest guarantee:** Prose rules cannot be 100% obeyed by a model. Deterministic rules enforced
> in LiteLLM **can** be guaranteed (forced presence, override gate, secret blocks). Semantic rules
> are only *reduced*. See [docs/litellm-rule-enforcement-guide.md](../docs/litellm-rule-enforcement-guide.md).

---

## Table of Contents

1. [Glossary](#glossary)
2. [Start here — implementation guides](#start-here--implementation-guides)
3. [What lives in this directory](#what-lives-in-this-directory)
4. [Relationship to the root rules files](#relationship-to-the-root-rules-files)
5. [Architecture (defense in depth)](#architecture-defense-in-depth)
6. [Prime Directive enforcement map](#prime-directive-enforcement-map)
7. [The two-key Override Protocol](#the-two-key-override-protocol)
8. [Editing the governance core](#editing-the-governance-core)
9. [Limitations](#limitations)
10. [FAQ](#faq)

---

## Glossary

| Term | Definition |
|------|------------|
| **Governance core** | [`governance_core.md`](./governance_core.md) — trimmed Prime Directives injected by LiteLLM. |
| **Guard module** | [`guards/`](./guards/) — reference `CustomLogger` to copy into your proxy. |
| **Open WebUI filter** | [`openwebui/governance_filter.py`](./openwebui/governance_filter.py) — optional UX reinforcement. |
| **Chokepoint** | Your LiteLLM proxy — hard enforcement lives here, not in Open WebUI. |
| **Deterministic rule** | Decidable by code (override gate, secret patterns) → **100% enforceable** in LiteLLM. |
| **Semantic rule** | Needs judgment (scope, intent) → **reduced**, never guaranteed from text. |
| **`GOV_MARKER`** | `<<GOVERNANCE_CORE_v1>>` — tamper marker; stripped from client messages before re-inject. |
| **Override ack token** | `[[OVERRIDE-ACK]]` — only valid when proxy state is UNLOCKED. |

---

## Start here — implementation guides

| Guide | When to read |
|-------|----------------|
| [docs/litellm-rule-enforcement-guide.md](../docs/litellm-rule-enforcement-guide.md) | **Design** — mental model, layers A–F, what can be guaranteed |
| [docs/litellm-integration-guide.md](../docs/litellm-integration-guide.md) | **Do this** — wire rules + `guards/` into your existing LiteLLM proxy |
| [docs/openwebui-integration-guide.md](../docs/openwebui-integration-guide.md) | **Do this** — Open WebUI wiring, filter install, what UI can/cannot enforce |

**Typical workflow:**

1. Read the design guide (once).
2. Copy `governance_core.md` and `guards/` into your LiteLLM deployment.
3. Register `guards.proxy_handler_instance` in your `config.yaml` and set env vars (your stack).
4. Optionally paste `openwebui/governance_filter.py` into Open WebUI for UX reinforcement.
5. Smoke-test via your proxy URL — not via a compose file in this repo.

---

## What lives in this directory

```
litellm/
├── README.md                 # This index
├── governance_core.md        # Injectable rules text (trimmed Prime Directives)
├── guards/                   # Reference enforcement module — COPY into your LiteLLM runtime
│   ├── governance_guard.py   # CustomLogger: pre_call + post_call hooks
│   ├── output_rules.py       # Secret scan, override-token checks
│   ├── overrides.py          # Two-key Override Protocol state machine
│   ├── verifier.py           # Optional LLM-as-judge (fail-open)
│   └── settings.py           # Env-driven guard configuration
└── openwebui/
    └── governance_filter.py  # Optional filter — paste into Open WebUI Workspace
```

**Not in this repo:** Docker Compose, `.env` templates, or a bundled LiteLLM/Open WebUI stack.
Those belong in **your** infrastructure repo or runbook.

---

## Relationship to the root rules files

This directory **does not replace** `CLAUDE.md`, `GENERAL_CLAUDE.md`, `GENERAL_CLAUDE_CORE.md`, or
`.claude/rules/`. It sits on top of them.

- **Root files = source of truth.** Full directives, scoped rules, Correction Log, deployment
  protocol, architecture, code quality — all live at the repo root and in `.claude/rules/`.
- **`governance_core.md` = trimmed projection.** Short, imperative copy of the Prime Directives for
  injection only. Edit root files first, then propagate here.
- **LiteLLM governs proxy traffic only.** Cursor, Claude Code, and Claude Desktop read the root
  files directly and never touch LiteLLM. Do not delete root rules.
- **Guards = reference implementation.** Copy into your stack; configure paths and env per the
  [LiteLLM integration guide](../docs/litellm-integration-guide.md).

| Artifact | Role |
|----------|------|
| Root `CLAUDE.md` / `GENERAL_CLAUDE*.md` + `.claude/rules/` | Authoritative ruleset + Correction Log |
| `governance_core.md` | Injected rules text for served models |
| `guards/` | Deterministic enforcement (copy to your proxy) |
| `openwebui/governance_filter.py` | Optional UI reinforcement (not enforcement) |

---

## Architecture (defense in depth)

```
                 +-------------+
   user  ------->| Open WebUI  |   Reinforcement only (BYPASSABLE)
                 +------+------+
                        |
                        v
        +-------------------------------+
        |     YOUR LiteLLM proxy         |   <-- ENFORCEMENT CHOKEPOINT (copy guards/ here)
        |  forced core injection       |
        |  pre_call / post_call guards |
        |  override state machine      |
        +---------------+----------------+
                        v
                 +-------------+
                 |  Provider   |
                 +-------------+
```

Hard guarantees require LiteLLM. Open WebUI filters improve UX for chat users only.

---

## Prime Directive enforcement map

| # | Prime Directive | Guarantee in LiteLLM |
|---|-----------------|----------------------|
| 1 | Follow every rule exactly | **Reduced** (presence guaranteed via injection) |
| 2 | Never assume intent | **Reduced** |
| 3 | Stay in scope | **Reduced** in chat; **Guaranteed** on committed code (Layer F: linter/CI) |
| 4 | No override without both keys | **Guaranteed** (`overrides.py` + output guard) |
| 5 | Deploy only by protocol | **Reduced** |
| 6 | Pre-output self-audit | **Guaranteed** subset (secrets, override token); **Reduced** remainder |
| 7 | Never repeat mistakes | **Reduced** (corrections in core text) |
| 8 | User input becomes law | **Reduced** |

---

## The two-key Override Protocol

State: `LOCKED` → `PENDING:<rule>` → `UNLOCKED:<rule>` → (one turn) → `LOCKED`.

1. User: `OVERRIDE RULE: scope-discipline` → PENDING.
2. User (separate message): `YES, OVERRIDE scope-discipline` → UNLOCKED for one turn.
3. Model may emit `[[OVERRIDE-ACK]]` only while UNLOCKED; otherwise post_call returns HTTP 422.

Requires shared Redis on LiteLLM for cross-turn state. Details:
[integration guide § Step 5](../docs/litellm-integration-guide.md#step-5--enable-redis-for-the-override-state-machine).

---

## Editing the governance core

1. Edit root rules and append corrections per the Correction & Memory Protocol.
2. Propagate changes into [`governance_core.md`](./governance_core.md). Keep it short.
3. Restart **your** LiteLLM proxy so it reloads the file.
4. If you change `GOV_MARKER` or `OVERRIDE_ACK_TOKEN`, update `guards/settings.py` in your copy.

---

## Limitations

- Semantic obedience is not guaranteed — only deterministic checks are absolute.
- Open WebUI cannot enforce hard rules; direct API calls skip WebUI entirely.
- Secret scanning is pattern-based; pair with CI secret scanning for code repos.
- This repo provides rules and reference code, not runtime operations for your stack.

---

## FAQ

**Q: Where is docker-compose?**
There isn't one. Integrate into your existing stack using the guides in `docs/`.

**Q: Do I still need `CLAUDE.md` at the repo root?**
Yes. See [Relationship to the root rules files](#relationship-to-the-root-rules-files).

**Q: Can I run guards without copying files?**
You need the guard module on LiteLLM's Python path and `governance_core.md` readable at
`GOVERNANCE_CORE_PATH`. Copying from this repo is the supported approach.

**Q: Is the Open WebUI filter required?**
No. It is optional reinforcement. LiteLLM guards are required for hard enforcement.
