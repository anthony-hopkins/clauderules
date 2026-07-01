# Guide: Governance in Open WebUI (Reinforcement + LiteLLM Wiring)

> **Scope:** This repo does **not** deploy Open WebUI. You already have a working stack. This guide
> explains what Open WebUI can and cannot enforce, how to connect it to your governed LiteLLM
> proxy, and how to install the optional **reinforcement filter** from
> [`litellm/openwebui/governance_filter.py`](../litellm/openwebui/governance_filter.py).
>
> **Hard enforcement lives in LiteLLM** — see [litellm-integration-guide.md](./litellm-integration-guide.md).

---

## Table of Contents

1. [Glossary](#glossary)
2. [What Open WebUI can and cannot do](#what-open-webui-can-and-cannot-do)
3. [Prerequisites](#prerequisites)
4. [Step 1 — Point Open WebUI at your LiteLLM proxy](#step-1--point-open-webui-at-your-litellm-proxy)
5. [Step 2 — Install the governance filter (optional)](#step-2--install-the-governance-filter-optional)
6. [Step 3 — Verify traffic passes through LiteLLM](#step-3--verify-traffic-passes-through-litellm)
7. [What the filter does (and does not do)](#what-the-filter-does-and-does-not-do)
8. [Conversation IDs and the override protocol](#conversation-ids-and-the-override-protocol)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Glossary

| Term | Definition |
|------|------------|
| **Filter (Open WebUI)** | A Python function plugin with `inlet()` / `outlet()` hooks on chat requests. |
| **Reinforcement** | UX nudges that raise compliance but can be bypassed — not a security control. |
| **Chokepoint** | LiteLLM proxy — the only place deterministic rules are guaranteed. |
| **`inlet()`** | Runs on the request **before** it is sent upstream (to LiteLLM). |
| **`outlet()`** | Runs on the response **after** the model returns — **WebUI chat only**, not direct API. |

---

## What Open WebUI can and cannot do

| Capability | Open WebUI | LiteLLM (your proxy) |
|------------|------------|----------------------|
| Force governance rules into every request | **No** — client can skip WebUI | **Yes** — `pre_call` injection |
| Block responses that violate deterministic rules | **No** — `outlet()` is not a hard gate for API traffic | **Yes** — `post_call` HTTP 422 |
| Two-key Override Protocol state | **No** | **Yes** — Redis-backed state machine |
| Secret scan / block | **No** (filter does not scan secrets) | **Yes** |
| Show "governed" banner in chat UI | **Yes** — filter `inlet()` | N/A |
| Hint when user sent `OVERRIDE RULE:` | **Yes** — filter `outlet()` display tweak | N/A |
| Survive direct API calls with proxy key | N/A — bypasses WebUI entirely | **Yes** — still enforced |

**Bottom line:** configure Open WebUI as the **front door** for humans, but implement every hard
rule in LiteLLM. Treat the Open WebUI filter as optional polish.

---

## Prerequisites

- Open WebUI already running in your environment.
- LiteLLM proxy running with governance guards installed ([integration guide](./litellm-integration-guide.md)).
- Admin access to Open WebUI (Workspace → Functions / Filters, depending on your version).

---

## Step 1 — Point Open WebUI at your LiteLLM proxy

Open WebUI should use LiteLLM as its OpenAI-compatible backend — you likely already have this.
Confirm in **your** Open WebUI settings or environment:

| Setting | Typical value |
|---------|----------------|
| OpenAI API base URL | `http://<your-litellm-host>:<port>/v1` |
| OpenAI API key | Your LiteLLM **master key** (or per-user key issued by LiteLLM), **not** the raw Anthropic key |

The upstream Anthropic (or other provider) key must exist **only inside LiteLLM**. If users or
Open WebUI hold the provider key directly, the chokepoint is bypassed and governance guarantees
do not apply.

Adjust hostnames and ports to match **your** network (Docker service name, ingress URL, etc.).

---

## Step 2 — Install the governance filter (optional)

1. Open Open WebUI → **Workspace** → **Functions** (or **Filters**, per version).
2. Create a new filter/function.
3. Paste the contents of [`litellm/openwebui/governance_filter.py`](../litellm/openwebui/governance_filter.py).
4. Enable the filter for the models/chats where you want reinforcement.

No additional Python packages are required beyond what Open WebUI already provides.

**Customize:** edit the banner string or override hint text in your pasted copy; do not rely on
this file for enforcement logic — keep that in LiteLLM `guards/`.

---

## Step 3 — Verify traffic passes through LiteLLM

1. Send a chat message in Open WebUI.
2. On the LiteLLM side, confirm the request is logged and the response is returned.
3. Optional: temporarily break `GOVERNANCE_CORE_PATH` on LiteLLM — the proxy should fail to start
   or reject misconfiguration; WebUI alone cannot inject the core.

If WebUI talks directly to Anthropic (misconfigured base URL), governance is **off** regardless of
this filter.

---

## What the filter does (and does not do)

**`inlet()` (request, WebUI only):**

- Prepends a one-line advisory system message: `[governed] This conversation is enforced by the governance proxy.`
- Does **not** replace LiteLLM injection — the proxy still strips forgeries and injects the real
  [`governance_core.md`](../litellm/governance_core.md).

**`outlet()` (response, WebUI chat only):**

- If the last user message matched `OVERRIDE RULE: <name>`, appends a short UI hint to confirm
  with `YES, OVERRIDE <name>`.
- Does **not** block, rewrite, or validate model output for secrets or overrides.

Direct API clients (`curl`, SDKs) never run `outlet()` — another reason enforcement must stay in LiteLLM.

---

## Conversation IDs and the override protocol

The two-key Override Protocol in LiteLLM keys state by `conversation_id` (or `chat_id`, etc.) from
request metadata. Open WebUI typically sends stable chat ids when using the built-in chat UI.

If overrides never persist across turns:

- Confirm Redis cache is enabled on LiteLLM ([integration guide § Step 5](./litellm-integration-guide.md#step-5--enable-redis-for-the-override-state-machine)).
- Confirm WebUI is not stripping metadata LiteLLM needs (check LiteLLM debug logs for `metadata`).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Banner shows but rules ignored | Only filter installed; LiteLLM guards missing | Complete LiteLLM integration guide |
| No banner, rules work | Filter not enabled | Enable filter in Workspace |
| Override works in UI but not API | Expected — API skips `outlet()` | Enforcement is in LiteLLM; test via proxy |
| WebUI errors on chat | LiteLLM returned 422 from guard | Inspect `violations` in proxy response body |
| Direct Anthropic calls bypass rules | Provider key exposed to clients | Route all traffic through LiteLLM only |

---

## FAQ

**Q: Can I enforce rules in Open WebUI alone?**
No. Filters are bypassable and `outlet()` does not run for direct API traffic. LiteLLM is required
for deterministic guarantees.

**Q: Should I paste `governance_core.md` into Open WebUI's system prompt?**
Not as the primary mechanism. Users can edit or disable UI prompts. LiteLLM injection is the
presence guarantee; keep WebUI prompts minimal or empty for governed models.

**Q: Does the filter replace LiteLLM guards?**
No. It is optional UX reinforcement only.

**Q: Where do I edit the rules text?**
Authoritative rules: repo root (`CLAUDE.md`, etc.). Injected copy: `litellm/governance_core.md`,
maintained top-down — see [litellm/README.md](../litellm/README.md#relationship-to-the-root-rules-files).
