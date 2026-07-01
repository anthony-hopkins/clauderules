# Guide: Enforcing Rigid, Deterministic Rules for Claude via LiteLLM + Open WebUI

> **Read this first.** You cannot get "100% guaranteed unbreakable" from anything written in
> prose — not in `CLAUDE.md`, not in a system prompt, not in a rule file. A system prompt is just
> more tokens fed to a probabilistic model; it raises compliance, it never guarantees it. The only
> way to reach *literal* 100% is to move each enforceable rule **out of the model's text and into
> deterministic code that runs around the model and can hard-block it.** With a LiteLLM + Open WebUI
> stack, that deterministic layer is **LiteLLM** (the proxy every request must pass through). That is
> where "unbreakable" actually lives.
>
> **This repo provides rules + reference code + guides — not a deployable stack.**
> - Design (this document): mental model and layer architecture.
> - Rules artifact: [`litellm/governance_core.md`](../litellm/governance_core.md).
> - Reference guards: [`litellm/guards/`](../litellm/guards/).
> - **Hands-on:** [litellm-integration-guide.md](./litellm-integration-guide.md) (your existing LiteLLM),
>   [openwebui-integration-guide.md](./openwebui-integration-guide.md) (your existing Open WebUI).

---

## 0. The mental model: two classes of rules

Sort every rule into one of two buckets. This sort decides whether a rule *can* be made unbreakable.

| Class | Definition | Can it be 100%? | Where it's enforced |
|---|---|---|---|
| **Deterministic** | Decidable by code without judgment: "no unused imports," "line length <= N," "output must be valid JSON matching schema X," "diff touches only files A/B," "no string matching a secret pattern," "response must contain the confirmation token." | **Yes, 100%** | LiteLLM hook / linter / CI — code that returns true/false |
| **Semantic** | Requires judgment: "don't change anything out of scope," "ask before assuming," "don't reformat unrelated code." | **No — only *raised*, never guaranteed** | A verifier (LLM-as-judge or diff heuristics) that approximates, plus prose in the system prompt |

**Strategy:** convert as many semantic rules as possible into deterministic checks, enforce those in
LiteLLM/tooling, and accept that the irreducibly-semantic remainder is *reduced* (system prompt +
verifier) but never *guaranteed*.

---

## 1. Architecture: defense in depth, chokepoint at LiteLLM

```
                 +-------------+
   user  ------->| Open WebUI  |   Layer E: UX-only reinforcement (BYPASSABLE)
                 +------+------+
                        |  (a user with an API key can skip Open WebUI entirely)
                        v
        +-------------------------------+
        |          LiteLLM proxy         |   <-- THE ENFORCEMENT CHOKEPOINT
        |  A. forced/immutable system    |       (every request must pass here)
        |     prompt injection           |
        |  B. pre_call input guardrail   |
        |  C. post_call output guardrail |
        |  D. override state machine     |
        +---------------+----------------+
                        v
                 +-------------+
                 | Anthropic   |  Haiku / Sonnet
                 +-------------+

   If Claude produces CODE that lands in a repo, add:
   Layer F: linter + pre-commit + CI + Cursor hooks (deterministic, blocks the diff)
```

**Critical correctness point:** Open WebUI's `outlet()` (response post-processing) **only runs for
WebUI chat requests, not for direct API calls** to `/api/chat/completions`. So Open WebUI filters are
*reinforcement and UX*, not enforcement — anyone with the key bypasses them. **All hard guarantees
must live in LiteLLM**, the one component a client cannot route around (assuming the upstream
Anthropic key is never handed out).

---

## 2. Layer A — Immutable system prompt injection (the *presence* guarantee)

Goal: guarantee the rules are **always** in context, exactly, regardless of what any client sends,
and that a client cannot strip or override them. Do this in a LiteLLM `async_pre_call_hook`, not in
Open WebUI. The hook rewrites `data["messages"]` to force the governance block as the first system
message and strips any client-supplied attempt to impersonate it.

`litellm_guards.py`:

```python
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy._types import UserAPIKeyAuth
from litellm.caching import DualCache
from typing import Literal
from fastapi import HTTPException

# Load once from disk so it is versioned with your repo, not pasted in a UI.
with open("/etc/litellm/governance_core.md", "r", encoding="utf-8") as f:
    GOVERNANCE_CORE = f.read()

GOV_MARKER = "<<GOVERNANCE_CORE_v1>>"  # tamper marker clients must not be able to forge

class GovernanceGuard(CustomLogger):
    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal["completion", "text_completion", "embeddings",
                            "image_generation", "moderation", "audio_transcription"],
    ) -> dict:
        if call_type not in ("completion", "text_completion"):
            return data

        # Force buffered output so the post_call hook can actually block (see Layer C).
        data["stream"] = False

        messages = data.get("messages", [])

        # 1. Strip any client message that tries to forge our governance block.
        cleaned = [m for m in messages if GOV_MARKER not in str(m.get("content", ""))]

        # 2. Force our governance core as the FIRST system message, every time.
        forced_system = {"role": "system", "content": f"{GOV_MARKER}\n{GOVERNANCE_CORE}"}
        data["messages"] = [forced_system] + cleaned
        return data

proxy_handler_instance = GovernanceGuard()
```

`config.yaml`:

```yaml
model_list:
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: claude-haiku
    litellm_params:
      model: anthropic/claude-haiku-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY

litellm_settings:
  callbacks: litellm_guards.proxy_handler_instance
```

- **Guaranteed:** the rules text is present and untampered in every call. That part *is*
  deterministic and unbreakable.
- **Not guaranteed:** that Claude *obeys* the text. Presence != compliance. That is what Layers
  C/D/F are for.

> Haiku note: smaller models follow long, dense, "everything-is-ABSOLUTE" prompts *worse* than
> Sonnet. Keep the forced block short and imperative (see Section 9).

---

## 3. Layer B — Deterministic input guardrails (`pre_call`)

Reject or rewrite requests before they reach Claude. The same `async_pre_call_hook` can
`raise HTTPException(...)` to hard-block. Use for input-side deterministic rules: blocklisted
patterns, required parameters, max context size, forbidden tools, etc.

```python
        last = str(messages[-1].get("content", "")) if messages else ""
        if "BEGIN RSA PRIVATE KEY" in last:
            raise HTTPException(status_code=400, detail="Blocked: secret-bearing input.")
```

Anything expressible as a pure function of the input is 100% enforceable here.

---

## 4. Layer C — Deterministic output guardrails (`post_call`) — the missing gate

This is the "pre-output self-audit" enforced *outside the model* so it cannot be skipped. The model's
drive to be helpful cannot override a Python `if`.

Two LiteLLM facts that dictate the implementation:

- `async_post_call_success_hook(data, user_api_key_dict, response)` can inspect **and block** the
  response — **but only for non-streaming requests.**
- For **streaming**, you must use `async_post_call_streaming_iterator_hook` (it can filter/block
  chunks). A plain success hook on a stream is audit-only.

**Recommendation: disable streaming for the governed models** (done in Layer A via
`data["stream"] = False`) so you get a clean, blockable, buffered response. This is the single
biggest lever for making output rules enforceable.

```python
    async def async_post_call_success_hook(
        self, data: dict, user_api_key_dict: UserAPIKeyAuth, response
    ):
        text = response.choices[0].message.content or ""
        violations = []

        # Example: an override may only be claimed with a confirmed two-key token (Section 5b).
        if "OVERRIDE GRANTED" in text and "[two-key:confirmed]" not in text:
            violations.append("Override claimed without confirmed two-key token.")

        # Add: JSON-schema validation, secret scanning, format checks, etc.

        if violations:
            # Hard-fail: the violating output never reaches the user.
            raise HTTPException(
                status_code=422,
                detail={"error": "Output rejected by guardrail", "violations": violations},
            )
            # Alternative: return a modified `response` to scrub/replace instead of failing.
        return response
```

Two enforcement styles, pick per rule:

- **Hard-fail** (raise): the violating output never reaches the user. Use for security-class rules.
- **Repair/replace** (return modified `response`): scrub or substitute. Use for formatting/PII.

---

## 5. Layer D — Semantic verifier and the deterministic Override Protocol

### 5a. LLM-as-judge for the irreducibly-semantic rules

For scope discipline ("did the diff change only what was requested?"), call a **second, cheap model
(Haiku) as a verifier** from inside `async_post_call_success_hook`. Give it the user request plus the
proposed output and ask one closed question: *"Does this output change anything not explicitly
requested? Answer ONLY `PASS` or `FAIL: <reason>`."* If `FAIL`, block or regenerate.

This is **still probabilistic** (a model judging a model), so it *reduces* scope violations; it does
not eliminate them. Combine it with deterministic diff checks (Layer F) wherever the output is code —
those *are* 100%.

### 5b. The two-key Override Protocol, enforced as proxy state (not prose)

Implement the override as a **state machine in LiteLLM keyed by conversation**, using the proxy
`cache`, so the model cannot self-grant an override:

1. **Default state = LOCKED.** Output guardrails (Layer C) block any response that asserts an
   override while the conversation is LOCKED.
2. **Key 1 (deterministic detect):** the `pre_call` hook scans the user message for an explicit
   override request naming the rule. On match, set cache state `PENDING:<rule>` and force the model
   to ask one yes/no question only.
3. **Key 2 (deterministic detect):** on the *next* user turn, if state is `PENDING` and the message
   is an explicit `YES, OVERRIDE <rule>`, flip cache state to `UNLOCKED:<rule>` for a single turn and
   append a CORRECTION ENTRY to the audit log.
4. While `UNLOCKED:<rule>`, Layer C permits exactly that rule's relaxation; then it auto-relocks.

```python
import re
conv_id = data.get("metadata", {}).get("conversation_id", "anon")
state_key = f"override:{conv_id}"
state = await cache.async_get_cache(state_key) or "LOCKED"

if re.search(r"\bOVERRIDE RULE:\s*\S+", last):
    rule = re.search(r"\bOVERRIDE RULE:\s*(\S+)", last).group(1)
    await cache.async_set_cache(state_key, f"PENDING:{rule}", ttl=1800)
elif state.startswith("PENDING:") and re.fullmatch(r"\s*YES,? OVERRIDE \S+\s*", last, re.I):
    rule = state.split(":", 1)[1]
    await cache.async_set_cache(state_key, f"UNLOCKED:{rule}", ttl=120)
    # append CORRECTION ENTRY to audit log here
```

Because the *gate* lives in Python keyed to conversation state, the model literally cannot
self-grant an override — the proxy decides, not the text.

---

## 6. Layer E — Open WebUI filter (reinforcement only, *not* a guarantee)

Useful for UX (showing when an override is pending, redacting before display, per-chat toggles), but
`outlet()` is skipped on direct API calls. Treat it as a nicety, never as a control.

```python
class Filter:
    async def inlet(self, body: dict) -> dict:
        # purely advisory; the real injection happens at LiteLLM
        return body

    async def outlet(self, body: dict) -> dict:
        # WebUI-only display tweaks; do NOT rely on this for enforcement
        return body
```

---

## 7. Layer F — Code-level deterministic gates (when Claude writes code that lands)

If Claude's output becomes files in a repo (via Cursor, Claude Code, or a pipeline), the unbreakable
enforcers are:

- **Linter/formatter** with the rules turned into errors: unused imports (`ruff F401` /
  `eslint no-unused-vars`), line length (`E501`), formatting (`ruff format` / `prettier --check`).
  100% deterministic, every time.
- **Diff/scope check**: a script that fails if the diff touches files or line ranges outside an
  allowlist for the task. The deterministic version of "scope discipline."
- **Pre-commit hooks** (`pre-commit`) so violations cannot be committed.
- **CI gates** (GitHub Actions) so they cannot merge.
- **Cursor `afterEdit` hooks** to run lint immediately after each edit and block.

Wire the *same* checks at all four points (editor hook -> pre-commit -> CI -> proxy if applicable) so
there is no gap to slip through.

---

## 8. What goes in prose vs. tooling

| Rule | Make it deterministic as... | Enforced in |
|---|---|---|
| Rules text must always be present | Forced system-prompt injection | LiteLLM `pre_call` (Sec. 2) |
| No secrets in output | Regex/secret-scanner on output | LiteLLM `post_call` (Sec. 4) + CI |
| No unused imports / line length / format | Linter rules as errors | Layer F (Sec. 7) |
| Output must match a schema | JSON-schema validation | LiteLLM `post_call` (Sec. 4) |
| Override only via two keys | Conversation state machine | LiteLLM pre+post (Sec. 5b) |
| Scope discipline (only requested lines) | Diff allowlist (code) + Haiku verifier (prose) | Layer F (100%) + Layer D (approx) |
| "Ask before assuming," tone, intent | Prose only — *not* guaranteeable | Forced system prompt, reduced not eliminated |

Anything in the bottom row is the irreducible part: *mitigated*, not *guaranteed*.

---

## 9. Trim the prose (raises compliance, especially on Haiku)

A bloated, duplicated always-on surface hurts a served model — especially Haiku.

- Keep one authoritative, short governance core that LiteLLM injects (Sec. 2). Tight, imperative,
  deduplicated.
- Stop marking everything "ABSOLUTE/MANDATORY/NON-NEGOTIABLE." When all of it shouts, none of it is
  salient. Reserve emphasis for the handful of true hard rules; push the rest to the deterministic
  layer where shouting is irrelevant because code enforces it.

---

## 10. Implementation order

Use the step-by-step guides for your **existing** stack — this repo does not ship Compose or images.

1. **Disable streaming** for governed models (unlocks blockable output) — [LiteLLM integration guide § Step 4](./litellm-integration-guide.md#step-4--configure-environment-variables) (`GOV_FORCE_NON_STREAMING`).
2. **Copy** [`litellm/governance_core.md`](../litellm/governance_core.md) and [`litellm/guards/`](../litellm/guards/) into your LiteLLM runtime — [integration guide § Steps 1–2](./litellm-integration-guide.md).
3. **Register** `guards.proxy_handler_instance` in your `config.yaml` — [§ Step 3](./litellm-integration-guide.md#step-3--register-the-callback-in-litellm).
4. **LiteLLM `post_call`**: deterministic output guardrails (reference: `guards/output_rules.py`, Sec. 4).
5. **Override state machine** + Redis cache (Sec. 5b) — [§ Step 5](./litellm-integration-guide.md#step-5--enable-redis-for-the-override-state-machine).
6. **Haiku verifier** (optional) — `GOV_ENABLE_VERIFIER` in your env.
7. **Repo tooling** (linter → pre-commit → CI) if output becomes code (Sec. 7).
8. **Trim** the always-on prose to one core (Sec. 9) — edit `governance_core.md`.
9. **Open WebUI filter** last, as reinforcement only (Sec. 6) — [Open WebUI integration guide](./openwebui-integration-guide.md).

---

## Bottom line

- **100% is achievable only for deterministic rules, and only in LiteLLM/tooling — never in prose.**
- **LiteLLM is the enforcement chokepoint;** Open WebUI filters are bypassable and UX-only.
- **Disabling streaming + a blocking `post_call` hook + a proxy-side override state machine** is the
  closest you get to "rigid and unbreakable" for a served Claude.
- The semantic residue (scope/intent) is *reduced* by a forced concise system prompt + an
  adversarial verifier, but it is structurally impossible to *guarantee* from text alone.
