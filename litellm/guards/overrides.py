"""Two-key Override Protocol, enforced as proxy state (not prose).

Purpose: make Prime Directive 4 ("never override a rule without both keys") deterministic.
The override decision lives in the proxy cache keyed by conversation, so the model literally
cannot grant itself an override — the Python state machine decides, the text never does.

State machine (stored per conversation in the LiteLLM cache):
    LOCKED            -> default; no override in effect.
    PENDING:<rule>    -> KEY 1 seen (user named a rule to override); awaiting explicit YES.
    UNLOCKED:<rule>   -> KEY 2 seen (user confirmed); override valid for a short TTL, one turn.

The pre_call hook feeds each user message to :func:`advance` to move the machine forward.
The post_call hook calls :func:`is_unlocked` to decide whether an override-asserting response
is permitted (see output_rules.check_output).

Ownership: the LiteLLM enforcement layer (litellm/). The cache object is injected so the
logic is unit-testable with a fake cache.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .settings import SETTINGS

LOCKED = "LOCKED"
_PENDING_PREFIX = "PENDING:"
_UNLOCKED_PREFIX = "UNLOCKED:"

# KEY 1: an explicit, rule-naming override request, e.g. "OVERRIDE RULE: scope-discipline".
_KEY1 = re.compile(r"\bOVERRIDE RULE:\s*(?P<rule>[\w\-./]+)", re.IGNORECASE)
# KEY 2: an explicit confirmation on a later turn, e.g. "YES, OVERRIDE scope-discipline".
_KEY2 = re.compile(r"\bYES,?\s+OVERRIDE\s+(?P<rule>[\w\-./]+)", re.IGNORECASE)


@dataclass(frozen=True)
class OverrideDecision:
    """Result of advancing the state machine for one inbound user message."""

    state: str
    rule: str | None
    transitioned: bool
    note: str


def _cache_key(conversation_id: str) -> str:
    return f"governance:override:{conversation_id}"


async def get_state(cache, conversation_id: str) -> str:
    """Return the current override state for a conversation (defaults to LOCKED)."""
    if cache is None:
        return LOCKED
    state = await cache.async_get_cache(key=_cache_key(conversation_id))
    return state or LOCKED


async def is_unlocked(cache, conversation_id: str) -> tuple[bool, str | None]:
    """Return ``(unlocked, rule)`` for the conversation's current state."""
    state = await get_state(cache, conversation_id)
    if state.startswith(_UNLOCKED_PREFIX):
        return True, state[len(_UNLOCKED_PREFIX):]
    return False, None


async def _set(cache, conversation_id: str, value: str, ttl: int) -> None:
    if cache is not None:
        await cache.async_set_cache(key=_cache_key(conversation_id), value=value, ttl=ttl)


async def advance(cache, conversation_id: str, user_message: str) -> OverrideDecision:
    """Advance the override state machine using the latest user message.

    KEY 1 (LOCKED/any -> PENDING): user names a rule to override.
    KEY 2 (PENDING -> UNLOCKED): on a *separate* message, user confirms the same context.
    Any other message while PENDING leaves the request pending (no silent unlock).
    """
    state = await get_state(cache, conversation_id)

    key1 = _KEY1.search(user_message or "")
    if key1:
        rule = key1.group("rule")
        await _set(cache, conversation_id, f"{_PENDING_PREFIX}{rule}", SETTINGS.override_pending_ttl_seconds)
        return OverrideDecision(f"{_PENDING_PREFIX}{rule}", rule, True, f"KEY 1 received for '{rule}'; awaiting explicit confirmation.")

    if state.startswith(_PENDING_PREFIX) and _KEY2.search(user_message or ""):
        rule = state[len(_PENDING_PREFIX):]
        await _set(cache, conversation_id, f"{_UNLOCKED_PREFIX}{rule}", SETTINGS.override_unlocked_ttl_seconds)
        return OverrideDecision(f"{_UNLOCKED_PREFIX}{rule}", rule, True, f"KEY 2 received; override UNLOCKED for '{rule}' (single turn).")

    return OverrideDecision(state, None, False, "No override transition.")


async def relock(cache, conversation_id: str) -> None:
    """Force the conversation back to LOCKED (used after an unlocked turn is consumed)."""
    await _set(cache, conversation_id, LOCKED, SETTINGS.override_pending_ttl_seconds)
