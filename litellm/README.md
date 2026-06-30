# Governance Enforcement Layer (LiteLLM)

This directory implements the design in [`docs/litellm-rule-enforcement-guide.md`](../docs/litellm-rule-enforcement-guide.md):
it moves the **Prime Directives out of prose and into deterministic code** that runs around the
model at the LiteLLM proxy and can **hard-block** non-compliant requests and responses.

> **Read this first — the honest guarantee.** You cannot get "100% unbreakable" from anything
> written in prose (not `CLAUDE.md`, not a system prompt). A prompt is just more tokens for a
> probabilistic model. *Literal* 100% is reachable **only for deterministic rules**, and **only**
> when enforced by code outside the model. This layer makes the deterministic directives truly
> unbreakable (forced presence, anti-tamper, the two-key override gate, secret/output checks) and
> *reduces* — never guarantees — the irreducibly-semantic ones (scope, intent) via a forced concise
> prompt plus an optional LLM verifier. Every claim below is labeled **Guaranteed** or **Reduced**.

---

## Table of Contents

1. [Glossary](#glossary)
2. [What this layer does](#what-this-layer-does)
3. [Relationship to the root rules files](#relationship-to-the-root-rules-files)
4. [Architecture (defense in depth)](#architecture-defense-in-depth)
5. [Prime Directive enforcement map](#prime-directive-enforcement-map)
6. [Directory layout](#directory-layout)
7. [Quick start (onboarding)](#quick-start-onboarding)
8. [Configuration reference](#configuration-reference)
9. [The two-key Override Protocol, step by step](#the-two-key-override-protocol-step-by-step)
10. [How a request flows through the guards](#how-a-request-flows-through-the-guards)
11. [Editing the governance core](#editing-the-governance-core)
12. [Testing and verification](#testing-and-verification)
13. [Operations and runbook](#operations-and-runbook)
14. [Security model and threat boundaries](#security-model-and-threat-boundaries)
15. [Limitations (what is NOT guaranteed)](#limitations-what-is-not-guaranteed)
16. [Troubleshooting](#troubleshooting)
17. [FAQ](#faq)
18. [Changelog](#changelog)

---

## Glossary

| Term | Definition |
|------|------------|
| **Chokepoint** | The single component every request must pass through. Here it is the **LiteLLM proxy**; because the upstream Anthropic key lives only inside it, clients cannot route around it. |
| **CustomLogger** | LiteLLM's callback base class. `GovernanceGuard` subclasses it to hook the request/response lifecycle. |
| **Deterministic rule** | A rule decidable by code without judgment (e.g. "no secret patterns in output", "output matches schema", "override token present"). Can be **100% enforced**. |
| **Semantic rule** | A rule needing judgment (e.g. "stay in scope", "don't assume intent"). Can only be **reduced**, never guaranteed, from text. |
| **Forced system-prompt injection** | The `pre_call` hook prepends the governance core as the first system message on every request, regardless of what the client sent. Guarantees **presence**, not **obedience**. |
| **Anti-tamper / tamper-strip** | The hook removes any client message that tries to forge the governance marker before re-injecting the authentic core. |
| **Governance core** | [`governance_core.md`](./governance_core.md): the short, imperative directive text that is injected. Versioned with the repo, not pasted into a UI. |
| **`GOV_MARKER`** | `<<GOVERNANCE_CORE_v1>>` — the marker bracketing the injected block. Clients cannot forge it; forgeries are stripped. |
| **Override Protocol (two keys)** | A proxy-side state machine (LOCKED → PENDING → UNLOCKED) that grants a rule relaxation only after two explicit, ordered user messages. The model **cannot self-grant** it. |
| **Override ack token** | `[[OVERRIDE-ACK]]` — the literal token the model must emit (and only emit) when acting on a granted override. Output guard rejects it when the conversation is LOCKED. |
| **`pre_call` hook** | `async_pre_call_hook`: inspects/rewrites the request before it reaches the model; can hard-block by raising. |
| **`post_call` hook** | `async_post_call_success_hook`: inspects the **buffered** response and can hard-block by raising (non-streaming only). |
| **Non-streaming enforcement** | Streaming is forced off for governed models so the full response is buffered and therefore blockable by `post_call`. |
| **Semantic verifier** | Optional second cheap model (Haiku) asked one PASS/FAIL question about scope/intent. **Reduces** scope violations; fails open on error. |
| **Fail open / fail closed** | On internal error, *fail open* = allow the request (used by the verifier so an outage isn't a denial of service); *fail closed* = block (used by deterministic security checks). |
| **Reinforcement (Open WebUI filter)** | UX-only nudges in the chat UI. **Bypassable** by anyone with the proxy key; never an enforcement point. |
| **Layer F** | Repo-level deterministic gates (linter, pre-commit, CI, editor hooks) for when the model's output becomes committed code. The unbreakable enforcer for "scope" on code. |

---

## What this layer does

Given a LiteLLM + Open WebUI + Claude stack, this layer guarantees, for **every** completion that
passes through the proxy:

- **Guaranteed — Presence:** the governance core is always the first system message, exactly, and a
  client cannot strip or impersonate it.
- **Guaranteed — Override integrity:** no response may assert or act on a rule override unless the
  proxy's two-key state machine has actually granted one for that conversation and turn.
- **Guaranteed — No secret leakage:** inbound prompts and outbound responses matching known
  credential patterns are hard-blocked.
- **Reduced — Scope/intent discipline:** a forced concise prompt plus an optional LLM-as-judge
  verifier lowers (does not eliminate) out-of-scope or assumption-driven output.

What it deliberately does **not** try to do: guarantee the model "obeys" any semantic instruction
from text alone. That is structurally impossible; see [Limitations](#limitations-what-is-not-guaranteed).

---

## Relationship to the root rules files

This layer **does not replace** the authoritative rules files at the repository root
(`CLAUDE.md`, `GENERAL_CLAUDE.md`, `GENERAL_CLAUDE_CORE.md`, and `.claude/rules/`). It sits **on top
of** them. All three statements below remain true at once:

- **The root files are still required, and they are the source of truth.** They hold the full
  directives, the deployment protocol, architecture and code-quality rules, the scoped detail in
  `.claude/rules/`, the glossary, and the append-only **Correction Log**. `governance_core.md` is a
  deliberately **trimmed projection** of the Prime Directives — not a substitute for any of that.
- **LiteLLM only governs proxy traffic.** Its guarantees apply *solely* to requests that pass
  through the proxy (Open WebUI, or API clients pointed at it). Agents that read rule files directly
  — **Cursor, Claude Code, Claude Desktop projects** — never touch this proxy, so for them the root
  files are the *only* governance. Deleting the root files would leave those agents with no rules.
- **Maintenance flows top-down.** Edit the root files first (and append corrections there, per the
  Correction & Memory Protocol), then propagate the trimmed result into `governance_core.md` and
  restart the proxy. Never treat `governance_core.md` as the primary source.

| Artifact | Role | Used by |
|----------|------|---------|
| `CLAUDE.md` / `GENERAL_CLAUDE*.md` + `.claude/rules/` | Authoritative, full, human-maintained ruleset; holds the Correction Log | File-reading agents (Cursor, Claude Code) **and** as the source for the trimmed core |
| `litellm/governance_core.md` | Trimmed projection of the Prime Directives | Injected by the proxy into governed traffic |
| `litellm/guards/` | Deterministic enforcement of the enforceable subset | The proxy chokepoint |

In short: the proxy is an enforcement **floor** for the deterministic rules; the prose files remain
the complete, authoritative rulebook for every agent — proxy-routed or not.

---

## Architecture (defense in depth)

```
                 +-------------+
   user  ------->| Open WebUI  |   Reinforcement only (BYPASSABLE) — openwebui/governance_filter.py
                 +------+------+
                        |  (a client with the proxy key can skip Open WebUI entirely)
                        v
        +-------------------------------+
        |          LiteLLM proxy         |   <-- THE ENFORCEMENT CHOKEPOINT (guards/)
        |  pre_call:  force non-stream   |
        |             tamper-strip       |
        |             inject core        |
        |             override advance   |
        |             block secret input |
        |  post_call: block override-    |
        |             without-grant      |
        |             block secret leak  |
        |             semantic verify     |
        |             relock override     |
        +---------------+----------------+
                        v   (upstream Anthropic key never leaves here)
                 +-------------+
                 | Anthropic   |  Sonnet / Haiku
                 +-------------+

   If model output becomes committed code, add Layer F: linter + pre-commit + CI + editor hooks.
```

The **only** components that provide guarantees are the LiteLLM `pre_call`/`post_call` hooks.
Everything in Open WebUI is convenience. This matches the guide's central correctness point:
Open WebUI's `outlet()` runs only for WebUI chats, not for direct API calls, so it can never be a
control.

---

## Prime Directive enforcement map

The eight Prime Directives (from `CLAUDE.md` / `GENERAL_CLAUDE_CORE.md`) sorted by how far each can
be enforced here. This is the core deliverable: **what "moving the directives into LiteLLM" actually
buys you, directive by directive.**

| # | Prime Directive | Class | Enforced by | Guarantee |
|---|-----------------|-------|-------------|-----------|
| 1 | Follow every rule; no approximation | Semantic | Forced injection + verifier | **Reduced** (presence guaranteed) |
| 2 | Never assume intent; ask first | Semantic | Forced injection + verifier | **Reduced** |
| 3 | Stay strictly in scope | Semantic (+ deterministic on code) | Verifier + Layer F diff allowlist | **Reduced** in chat; **Guaranteed** on committed code |
| 4 | No override without both keys | **Deterministic** | `overrides.py` state machine + output guard | **Guaranteed** |
| 5 | No deploy except by protocol | Semantic | Forced injection (+ Layer F/CI for real deploys) | **Reduced** |
| 6 | No output until self-audit passes | Partly deterministic | `output_rules.py` (secrets, override token); verifier for the rest | **Guaranteed** subset; **Reduced** remainder |
| 7 | Never repeat a corrected mistake | Process | Forced injection (corrections live in the core) | **Reduced** |
| 8 | User input becomes binding law | Process | Forced injection | **Reduced** |

**Presence of all eight is guaranteed** on every request (injection). **Compliance** is guaranteed
only for the deterministic pieces (Directive 4 in full; the secret/override-token parts of Directive
6). The rest is raised, not guaranteed — by design, and honestly labeled.

---

## Directory layout

```
litellm/
├── README.md                      # This document
├── governance_core.md             # The injected directive text (short, imperative)
├── config.yaml                    # LiteLLM proxy config (registers the guard callback)
├── docker-compose.yml             # LiteLLM + Redis + optional Open WebUI
├── requirements.txt               # Runtime + test dependencies (version floors)
├── .env.example                   # Environment template (copy to .env)
├── .gitignore                     # Ignore .env and python artifacts
├── pytest.ini                     # Test config (pythonpath, asyncio mode)
├── guards/                        # The enforcement code (the chokepoint)
│   ├── __init__.py               # Lazy export of proxy_handler_instance
│   ├── settings.py               # Env-driven config, resolved once at startup
│   ├── output_rules.py           # Pure deterministic input/output checks
│   ├── overrides.py              # Two-key Override Protocol state machine
│   ├── verifier.py               # Optional semantic LLM-as-judge (fail-open)
│   └── governance_guard.py       # CustomLogger wiring the lifecycle hooks
├── openwebui/
│   └── governance_filter.py       # Reinforcement-only UI filter (bypassable)
└── tests/
    ├── test_output_rules.py       # Secret scan + override-token consistency
    └── test_overrides.py          # State-machine transitions and isolation
```

---

## Quick start (onboarding)

**Prerequisites:** Docker + Docker Compose v2, an Anthropic API key.

1. **Copy the env template and fill in secrets.** From this directory:

```bash
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY, LITELLM_MASTER_KEY, REDIS_PASSWORD (and WEBUI_SECRET_KEY).
```

2. **Pin the proxy image.** In `.env` (or `docker-compose.yml`), set `LITELLM_IMAGE` to a real,
   released tag or digest. The default is a known stable tag and must be verified against the
   registry before production (deployment protocol, Step 7: no floating tags).

3. **Launch the stack.**

```bash
docker compose up -d
docker compose ps          # all services should be running/healthy
docker compose logs -f litellm
```

4. **Smoke-test the chokepoint** (replace `$LITELLM_MASTER_KEY`):

```bash
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet","messages":[{"role":"user","content":"Say hi."}]}'
```

The governance core is injected server-side; you do not (and cannot) send it from the client.

5. **(Optional) Open WebUI:** browse to `http://localhost:3000`, then add the filter in
   *Workspace → Functions* by pasting [`openwebui/governance_filter.py`](./openwebui/governance_filter.py).
   Remember it is reinforcement only.

---

## Configuration reference

All knobs are environment variables (see [`.env.example`](./.env.example)). Guards never read
`os.environ` directly — everything resolves through `guards/settings.py` at startup, so
misconfiguration fails fast.

| Variable | Default | Purpose |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | — (required) | Upstream provider key. Never exposed to clients. |
| `LITELLM_MASTER_KEY` | — (required) | Proxy admin/auth key clients use to reach the proxy. |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` | `redis` / `6379` / — | Shared cache for the override state machine. |
| `GOVERNANCE_CORE_PATH` | `/app/governance_core.md` | Path to the injected core. |
| `GOV_FORCE_NON_STREAMING` | `true` | Force buffered responses so `post_call` can block. **Keep on.** |
| `GOV_BLOCK_SECRETS_INPUT` | `true` | Hard-block secret-bearing prompts. |
| `GOV_BLOCK_SECRETS_OUTPUT` | `true` | Hard-block secret-leaking responses. |
| `GOV_ENABLE_OVERRIDE` | `true` | Enable the two-key override state machine. |
| `GOV_OVERRIDE_PENDING_TTL` | `1800` | Seconds a KEY-1 pending request stays valid. |
| `GOV_OVERRIDE_UNLOCKED_TTL` | `120` | Seconds a KEY-2 unlock stays valid (single turn). |
| `GOV_ENABLE_VERIFIER` | `false` | Enable the semantic scope verifier (adds latency/cost). |
| `GOV_VERIFIER_MODEL` | `claude-haiku` | Model name (from `config.yaml`) used as the judge. |
| `WEBUI_SECRET_KEY` | `changeme` | Open WebUI session secret. |

---

## The two-key Override Protocol, step by step

This is the flagship **Guaranteed** control: Prime Directive 4 made deterministic. The grant lives in
Python keyed to conversation state, so the model cannot talk its way past it.

State machine: `LOCKED` → `PENDING:<rule>` → `UNLOCKED:<rule>` → (consumed) → `LOCKED`.

1. **Default — LOCKED.** Any response asserting an override (or emitting `[[OVERRIDE-ACK]]`) is
   rejected by the output guard with HTTP 422.
2. **KEY 1 — request (deterministic detect).** The user sends a message naming the rule:
   `OVERRIDE RULE: scope-discipline`. The `pre_call` hook sets state `PENDING:scope-discipline`
   (TTL `GOV_OVERRIDE_PENDING_TTL`). The model is expected to ask one yes/no question and wait.
3. **KEY 2 — confirmation (deterministic detect).** On a **separate later** message the user
   confirms: `YES, OVERRIDE scope-discipline`. Only if state is still `PENDING` does the hook flip to
   `UNLOCKED:scope-discipline` (short TTL `GOV_OVERRIDE_UNLOCKED_TTL`).
4. **Single-turn use.** While `UNLOCKED`, the output guard permits a response that asserts the
   override and carries `[[OVERRIDE-ACK]]`. After that turn the `post_call` hook **relocks**.

Any out-of-order or unrelated message never unlocks anything (verified by tests). A missing
conversation id degrades the override to a single request — it can only ever *withhold*, never grant.

---

## How a request flows through the guards

`pre_call` (`async_pre_call_hook` in `governance_guard.py`):

1. Skip non-completion calls (embeddings, etc.).
2. Force `stream=False` (so the response is blockable).
3. Scan the latest user message for secrets → **HTTP 400** if found and blocking is on.
4. Advance the override state machine from that message.
5. Strip any forged governance block, then inject the authentic core as the first system message.

`post_call` (`async_post_call_success_hook`):

6. Extract the assistant text.
7. Read override state for the conversation (`UNLOCKED?`).
8. Run deterministic output checks → **HTTP 422** if the response leaks secrets or asserts an
   ungranted override.
9. If the verifier is enabled, ask the judge model PASS/FAIL on scope → **HTTP 422** on FAIL.
10. If the override was unlocked, relock it (single-turn consumption).

---

## Editing the governance core

[`governance_core.md`](./governance_core.md) is **production code**. To change what every governed
request sees:

1. Edit the file. Keep it short and imperative — bloated, all-caps prompts lower compliance,
   especially on Haiku (guide, Section 9).
2. Restart the proxy so it re-reads the file: `docker compose restart litellm`.
3. If you change the marker or the ack token, update `guards/settings.py` (`GOV_MARKER`,
   `OVERRIDE_ACK_TOKEN`) to match, or the anti-tamper/override checks will drift.

The injected core mirrors the Prime Directives but is intentionally trimmed; the full, authoritative
rules remain in `CLAUDE.md` / `GENERAL_CLAUDE.md` at the repo root.

---

## Testing and verification

The deterministic logic is unit-tested without needing a running proxy or the heavy `litellm`
runtime (the package exports its guard lazily).

```bash
cd litellm
pip install -r requirements.txt        # or: pip install pytest pytest-asyncio
pytest -q
```

What is covered:

- `test_output_rules.py` — secret pattern detection; input/output blocking; the override-token
  consistency rule (ack token rejected when LOCKED, allowed when UNLOCKED).
- `test_overrides.py` — the full state machine: KEY 1 → PENDING, KEY 2 → UNLOCKED, out-of-order
  rejection, relock, and per-conversation isolation.

Run these in CI as a Layer-F gate so a regression in the enforcement code cannot merge.

---

## Operations and runbook

| Task | Command |
|------|---------|
| Start | `docker compose up -d` |
| Status | `docker compose ps` |
| Logs | `docker compose logs -f litellm` |
| Restart proxy (reload core/config) | `docker compose restart litellm` |
| Stop (keep data) | `docker compose down` |
| Stop and wipe volumes (destructive — confirm first) | `docker compose down -v` |

**Override state inspection:** keys are `governance:override:<conversation_id>` in Redis. Connect with
`docker compose exec redis redis-cli -a "$REDIS_PASSWORD"` and `GET` the key to see `LOCKED` /
`PENDING:<rule>` / `UNLOCKED:<rule>`.

---

## Security model and threat boundaries

- **Trust boundary:** the upstream `ANTHROPIC_API_KEY` lives only inside the proxy container. If it
  is ever handed to a client, the chokepoint is gone and **no guarantee holds**. Guard it like any
  production secret.
- **Client cannot:** strip/forge the governance core, self-grant an override, exfiltrate matched
  secret patterns, or (with streaming forced off) stream past the output guard.
- **Client can (by design, harmless):** ignore the Open WebUI filter — it is reinforcement only.
- **Operator must:** pin the proxy image, set a strong `LITELLM_MASTER_KEY`, password-protect Redis,
  and keep `.env` out of version control (enforced by `.gitignore`).

---

## Limitations (what is NOT guaranteed)

Stated plainly so no one over-trusts the layer:

- **Semantic obedience is not guaranteed.** "Stay in scope", "don't assume intent", "follow the
  deploy protocol" are raised by the forced prompt and the optional verifier, but a sufficiently
  determined or unlucky generation can still violate them. Only the deterministic checks are absolute.
- **The verifier is a model judging a model.** It is probabilistic, off by default, and fails open.
- **Secret scanning is pattern-based.** It catches known credential formats, not novel or obfuscated
  secrets. Pair with repo secret-scanning in CI.
- **Override detection is literal.** It keys on the documented phrases (`OVERRIDE RULE:` /
  `YES, OVERRIDE`). This is intentional: a strict, unambiguous trigger is safer than a fuzzy one.
- **For code that lands in a repo, the real guarantee is Layer F** (linter/diff-allowlist/pre-commit/
  CI), not the chat layer. Wire the same checks there.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Proxy exits at startup: "Governance core not found" | `GOVERNANCE_CORE_PATH` wrong or file not mounted | Verify the volume mount and path in `docker-compose.yml`. |
| Overrides never unlock | No shared Redis cache (multi-worker), or wrong phrasing | Enable Redis cache; use the exact `OVERRIDE RULE:` / `YES, OVERRIDE` phrasing. |
| Override "works" but only within one request | Conversation id not propagated by the client | Pass a stable `conversation_id`/`chat_id` in metadata. |
| Responses get truncated/blocked unexpectedly | Output guard firing on a false positive secret match | Inspect logs; tune `_SECRET_PATTERNS` in `output_rules.py`. |
| Streaming clients get buffered responses | `GOV_FORCE_NON_STREAMING=true` (intended) | This is required for output blocking; leave on. |
| Verifier adds latency / blocks too much | Verifier enabled | Set `GOV_ENABLE_VERIFIER=false`, or refine the verifier prompt. |

---

## FAQ

**Q: Does this make `CLAUDE.md` "100% unbreakable"?**
Only its deterministic parts (the override gate, secret/output-token checks). The semantic
directives are *reduced*, not guaranteed. That distinction is the whole point of the guide.

**Q: Why force non-streaming?**
Because a streamed response has already partly reached the user by the time you could inspect it. A
buffered response can be fully validated and rejected before anything is delivered.

**Q: Can I keep streaming for some models?**
Yes, but those models lose `post_call` output blocking (it becomes audit-only). Keep governed models
non-streaming.

**Q: Where do user corrections live?**
In the authoritative rules files (`CLAUDE.md` / `GENERAL_CLAUDE_CORE.md`) and, in trimmed form, in
`governance_core.md` so they are injected every session.

**Q: Why is the verifier off by default?**
It costs a second model call per request and only *reduces* violations. Turn it on when scope
discipline matters more than latency/cost.

---

## Changelog

- **v1 (initial):** Forced injection + anti-tamper (presence guarantee), deterministic
  input/output secret guards, two-key Override Protocol state machine, optional fail-open semantic
  verifier, Open WebUI reinforcement filter, Docker Compose stack, and unit tests for all
  deterministic logic.
