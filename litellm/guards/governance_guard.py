"""GovernanceGuard — the LiteLLM CustomLogger that enforces the governance core.

This is the enforcement chokepoint. Every governed completion passes through here. It wires
the deterministic pieces together:

  pre_call  (async_pre_call_hook):
    1. Force non-streaming so the response is buffered and therefore blockable.
    2. Strip any client message that forges the governance marker (anti-tamper).
    3. Inject the governance core as the FIRST system message (presence guarantee).
    4. Advance the two-key override state machine from the latest user message.
    5. Hard-block secret-bearing input.

  post_call (async_post_call_success_hook):
    6. Reject responses that assert an override the proxy never granted, or leak secrets.
    7. Optionally run the semantic verifier (scope/intent) and block on FAIL.
    8. Relock the override once its single unlocked turn has been consumed.

Why presence is guaranteed but obedience is not: steps 1-3 are pure functions of the request
and cannot be talked around, so the rules text is *always* present and untampered. Whether the
model obeys that text is what steps 6-8 (and repo-level tooling) police.

Ownership: the LiteLLM enforcement layer (litellm/). Registered via config.yaml ->
``litellm_settings.callbacks``.
"""

from __future__ import annotations

import logging
from typing import Literal

from litellm.integrations.custom_logger import CustomLogger

from . import output_rules, overrides
from .settings import GOV_MARKER, SETTINGS
from .verifier import verify_scope

try:  # FastAPI is available inside the LiteLLM proxy; guard import for unit tests.
    from fastapi import HTTPException
except Exception:  # pragma: no cover - exercised only when FastAPI is absent.
    class HTTPException(Exception):  # type: ignore[no-redef]
        def __init__(self, status_code: int, detail) -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

logger = logging.getLogger("governance.guard")

_COMPLETION_CALLS = ("completion", "text_completion")


def _conversation_id(data: dict) -> str:
    """Best-effort stable conversation id for override state, scoped per chat.

    Open WebUI and SDK clients surface different metadata shapes; we probe the common
    locations and fall back to the per-request call id (which degrades the override to a
    single request — fail-safe, since a missing id never *grants* an override).
    """
    for container in (data.get("litellm_metadata"), data.get("metadata")):
        if isinstance(container, dict):
            for field in ("conversation_id", "chat_id", "session_id", "thread_id"):
                value = container.get(field)
                if value:
                    return str(value)
    return str(data.get("litellm_call_id") or "anon")


def _last_user_message(messages: list[dict]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return str(message.get("content", ""))
    return ""


def _all_user_text(messages: list[dict]) -> str:
    return "\n".join(str(m.get("content", "")) for m in messages if m.get("role") == "user")


def _inject_core(messages: list[dict]) -> list[dict]:
    """Strip forged governance blocks, then force the core as the first system message.

    Any inbound message carrying the tamper marker is a forgery attempt and is removed
    before the authentic, marker-bracketed core is prepended.
    """
    cleaned = [m for m in messages if GOV_MARKER not in str(m.get("content", ""))]
    forced = {"role": "system", "content": f"{GOV_MARKER}\n{SETTINGS.governance_core}"}
    return [forced] + cleaned


class GovernanceGuard(CustomLogger):
    """LiteLLM callback enforcing the governance core at the proxy chokepoint."""

    def __init__(self) -> None:
        super().__init__()
        # The proxy cache is a process-wide singleton; stashing the reference in pre_call
        # lets the post_call hook (which receives no cache arg) read override state. Only
        # the reference is shared — per-conversation keys keep requests isolated.
        self._cache = None

    async def async_pre_call_hook(
        self,
        user_api_key_dict,
        cache,
        data: dict,
        call_type: Literal[
            "completion", "text_completion", "embeddings",
            "image_generation", "moderation", "audio_transcription",
        ],
    ) -> dict:
        if call_type not in _COMPLETION_CALLS:
            return data

        self._cache = cache

        if SETTINGS.force_non_streaming:
            data["stream"] = False

        messages = data.get("messages", [])
        last_user = _last_user_message(messages)

        input_result = output_rules.check_input(last_user, block_secrets=SETTINGS.block_secrets_in_input)
        if not input_result.ok:
            raise HTTPException(status_code=400, detail={"error": "Input rejected by guardrail", "violations": list(input_result.violations)})

        if SETTINGS.enable_override_state_machine:
            decision = await overrides.advance(cache, _conversation_id(data), last_user)
            if decision.transitioned:
                logger.info("Override state: %s (%s)", decision.state, decision.note)

        data["messages"] = _inject_core(messages)
        return data

    async def async_post_call_success_hook(self, data: dict, user_api_key_dict, response):
        text = self._extract_text(response)
        conv_id = _conversation_id(data)

        unlocked, _rule = (False, None)
        if SETTINGS.enable_override_state_machine:
            unlocked, _rule = await overrides.is_unlocked(self._cache, conv_id)

        result = output_rules.check_output(
            text, override_unlocked=unlocked, block_secrets=SETTINGS.block_secrets_in_output
        )
        if not result.ok:
            raise HTTPException(status_code=422, detail={"error": "Output rejected by guardrail", "violations": list(result.violations)})

        if SETTINGS.enable_semantic_verifier:
            verdict = await verify_scope(_all_user_text(data.get("messages", [])), text)
            if not verdict.ok:
                raise HTTPException(status_code=422, detail={"error": "Output failed scope verification", "violations": [verdict.reason]})

        # An override is valid for a single turn; consume it so the next turn is LOCKED again.
        if unlocked and SETTINGS.enable_override_state_machine:
            await overrides.relock(self._cache, conv_id)

        return response

    @staticmethod
    def _extract_text(response) -> str:
        """Pull assistant text out of either an object- or dict-shaped completion response."""
        try:
            return response.choices[0].message.content or ""
        except AttributeError:
            try:
                return response["choices"][0]["message"]["content"] or ""
            except (KeyError, IndexError, TypeError):
                return ""


proxy_handler_instance = GovernanceGuard()
