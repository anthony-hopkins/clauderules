# Guide: Integrating Governance Rules into Your Existing LiteLLM Stack

> **Scope:** This repo provides **rules and reference code**, not a deployable stack. You already
> run LiteLLM (and likely Open WebUI). This guide walks through wiring the governance artifacts
> from [`litellm/`](../litellm/) into **your** proxy configuration.
>
> **Read first:** [litellm-rule-enforcement-guide.md](./litellm-rule-enforcement-guide.md) for the
> design (deterministic vs. semantic rules, chokepoint model). Use this guide for hands-on steps.

---

## Table of Contents

1. [Glossary](#glossary)
2. [What you copy from this repo](#what-you-copy-from-this-repo)
3. [Prerequisites](#prerequisites)
4. [Step 1 — Place the governance core](#step-1--place-the-governance-core)
5. [Step 2 — Copy the guard module](#step-2--copy-the-guard-module)
6. [Step 3 — Register the callback in LiteLLM](#step-3--register-the-callback-in-litellm)
7. [Step 4 — Configure environment variables](#step-4--configure-environment-variables)
8. [Step 5 — Enable Redis for the override state machine](#step-5--enable-redis-for-the-override-state-machine)
9. [Step 6 — Restart and smoke-test](#step-6--restart-and-smoke-test)
10. [Guard behavior reference](#guard-behavior-reference)
11. [Troubleshooting](#troubleshooting)

---

## Glossary

| Term | Definition |
|------|------------|
| **Governance core** | [`litellm/governance_core.md`](../litellm/governance_core.md) — trimmed Prime Directives text injected on every request. |
| **Guard module** | [`litellm/guards/`](../litellm/guards/) — Python `CustomLogger` that enforces deterministic rules at the proxy. |
| **Chokepoint** | Your LiteLLM proxy — every governed request must pass through it; upstream model keys stay inside it. |
| **`GOV_MARKER`** | `<<GOVERNANCE_CORE_v1>>` — anti-tamper marker; clients cannot forge it. |
| **Override ack token** | `[[OVERRIDE-ACK]]` — emitted only when the proxy has granted an override for that turn. |

---

## What you copy from this repo

| Artifact | Copy to your stack | Purpose |
|----------|-------------------|---------|
| `litellm/governance_core.md` | A path readable by the proxy (volume mount or baked into image) | Rules text injected every request |
| `litellm/guards/` (entire folder) | On `PYTHONPATH` where LiteLLM runs (e.g. `/app/guards/`) | Deterministic enforcement hooks |
| This guide + [openwebui-integration-guide.md](./openwebui-integration-guide.md) | Documentation only | How to wire and verify |

**Do not copy:** there is no `docker-compose.yml`, `.env.example`, or stack definition in this repo.
Use your existing deployment mechanism.

---

## Prerequisites

- A **running LiteLLM proxy** you control (Compose, K8s, bare metal — any mechanism).
- Ability to **edit `config.yaml`** (or equivalent) and **restart** the proxy.
- **Redis** reachable by LiteLLM if you want the two-key Override Protocol to persist across
  turns and replicas (strongly recommended).
- Open WebUI (optional) already pointed at your LiteLLM base URL — see the
  [Open WebUI guide](./openwebui-integration-guide.md).

---

## Step 1 — Place the governance core

Copy [`litellm/governance_core.md`](../litellm/governance_core.md) to a stable path on the host or
inside the proxy container, for example:

```text
/etc/litellm/governance_core.md
# or, if guards live at /app/guards/:
/app/governance_core.md   # sibling to guards/ (default when GOVERNANCE_CORE_PATH is unset)
```

Set `GOVERNANCE_CORE_PATH` to that absolute path (Step 4).

**Maintenance:** edit root rules (`CLAUDE.md` / `GENERAL_CLAUDE_CORE.md`) first, then propagate
the trimmed result into `governance_core.md`. Restart the proxy after changes.

---

## Step 2 — Copy the guard module

Copy the entire [`litellm/guards/`](../litellm/guards/) directory into your LiteLLM runtime, e.g.:

```text
/app/guards/
  __init__.py
  settings.py
  output_rules.py
  overrides.py
  verifier.py
  governance_guard.py
```

Ensure the directory is importable as `guards`:

- Set `PYTHONPATH` to the parent of `guards/` (e.g. `PYTHONPATH=/app`), **or**
- Install/copy so `from guards import proxy_handler_instance` resolves from LiteLLM's working directory.

The proxy must be able to import `guards.proxy_handler_instance` at startup.

---

## Step 3 — Register the callback in LiteLLM

Add to **your existing** `config.yaml` (merge — do not replace your model list):

```yaml
litellm_settings:
  callbacks: guards.proxy_handler_instance
  drop_params: true   # recommended: honors forced stream=False from the guard
```

If you already have callbacks, LiteLLM supports a list — consult your LiteLLM version docs. The
guard must run for completion requests.

**Optional:** if you use a semantic verifier (`GOV_ENABLE_VERIFIER=true`), ensure
`GOV_VERIFIER_MODEL` matches a `model_name` already in your `model_list` (e.g. a cheap Haiku alias).

Example snippet only (adapt model names and keys to your setup):

```yaml
model_list:
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: claude-haiku
    litellm_params:
      model: anthropic/claude-3-5-haiku-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

litellm_settings:
  callbacks: guards.proxy_handler_instance
  drop_params: true
```

Restart LiteLLM using **your** documented procedure after editing config.

---

## Step 4 — Configure environment variables

Add these to **your** LiteLLM service environment (Compose `environment:`, K8s ConfigMap/Secret,
systemd, etc.). Document them in your stack's `.env.example` — not in this repo.

| Variable | Default | Purpose |
|----------|---------|---------|
| `GOVERNANCE_CORE_PATH` | sibling `governance_core.md` to `guards/` | Absolute path to injected rules file |
| `GOV_FORCE_NON_STREAMING` | `true` | Buffer responses so output guard can block. **Keep on.** |
| `GOV_BLOCK_SECRETS_INPUT` | `true` | Hard-block secret patterns in user messages |
| `GOV_BLOCK_SECRETS_OUTPUT` | `true` | Hard-block secret patterns in model output |
| `GOV_ENABLE_OVERRIDE` | `true` | Two-key Override Protocol state machine |
| `GOV_OVERRIDE_PENDING_TTL` | `1800` | Seconds KEY 1 (pending) stays valid |
| `GOV_OVERRIDE_UNLOCKED_TTL` | `120` | Seconds KEY 2 (unlocked) stays valid; single turn |
| `GOV_ENABLE_VERIFIER` | `false` | LLM-as-judge scope check (latency + cost) |
| `GOV_VERIFIER_MODEL` | `claude-haiku` | Model alias for verifier (must exist in `model_list`) |

The guard fails fast at startup if `GOVERNANCE_CORE_PATH` is missing or empty.

---

## Step 5 — Enable Redis for the override state machine

The override protocol stores conversation state in LiteLLM's cache (`LOCKED` / `PENDING` / `UNLOCKED`).
Without a **shared** Redis cache, state may not survive across requests or workers — overrides
degrade to fail-safe (never grant spuriously; may never unlock across turns).

In **your** LiteLLM config, enable cache if not already:

```yaml
general_settings:
  cache: true
  cache_params:
    type: redis
    host: os.environ/REDIS_HOST      # your existing Redis
    port: os.environ/REDIS_PORT
    password: os.environ/REDIS_PASSWORD
```

Use the Redis instance you already run for LiteLLM or rate limiting; no new service is defined here.

---

## Step 6 — Restart and smoke-test

1. Restart LiteLLM per your runbook.
2. Confirm the proxy starts without `Governance core not found` errors in logs.
3. Send a completion through **your** proxy URL (replace host, key, and model):

```bash
curl -s "$LITELLM_BASE_URL/v1/chat/completions" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet","messages":[{"role":"user","content":"Say hi."}]}'
```

You should **not** send the governance core from the client — the guard injects it server-side.

4. **Override smoke test (optional):**
   - Send: `OVERRIDE RULE: scope-discipline` → state becomes PENDING.
   - Send: `YES, OVERRIDE scope-discipline` → one turn UNLOCKED; model may emit `[[OVERRIDE-ACK]]`.
   - Next turn → LOCKED again.

5. **Secret block test:** a message containing `-----BEGIN RSA PRIVATE KEY-----` should return **HTTP 400**.

---

## Guard behavior reference

**`pre_call` (`async_pre_call_hook`):**

1. Force `stream=False` (when `GOV_FORCE_NON_STREAMING=true`).
2. Block secret-bearing input → HTTP 400.
3. Advance override state machine from latest user message.
4. Strip forged governance markers; inject authentic core as first system message.

**`post_call` (`async_post_call_success_hook`):**

5. Block ungranted override claims or `[[OVERRIDE-ACK]]` when LOCKED → HTTP 422.
6. Block secret leakage in output → HTTP 422.
7. Optional verifier PASS/FAIL on scope → HTTP 422 on FAIL.
8. Relock after a consumed UNLOCKED turn.

Full directive mapping: [litellm/README.md](../litellm/README.md#prime-directive-enforcement-map).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Proxy won't start | `GOVERNANCE_CORE_PATH` wrong or file not mounted | Fix path/mount; check logs |
| `ModuleNotFoundError: guards` | `PYTHONPATH` or copy location | Parent of `guards/` on path |
| Overrides never unlock | No Redis / no conversation id in metadata | Enable shared cache; ensure client sends stable `conversation_id` or `chat_id` |
| Output always blocked | False positive secret pattern | Tune `_SECRET_PATTERNS` in `output_rules.py` in your copy |
| Streaming clients behave differently | Forced non-streaming | Expected; required for output blocking |

For Open WebUI-specific wiring and what the UI can enforce, see
[openwebui-integration-guide.md](./openwebui-integration-guide.md).
