"""Tests for the two-key Override Protocol state machine.

Verifies the central guarantee: the model cannot reach UNLOCKED without two explicit,
correctly-ordered user keys, and an unlocked override is consumed (relocked) after use.
A fake cache stands in for the LiteLLM DualCache so no proxy is required.
"""

import pytest

from guards import overrides


class FakeCache:
    """Minimal async cache matching the LiteLLM DualCache interface used by overrides."""

    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def async_get_cache(self, key: str):
        return self.store.get(key)

    async def async_set_cache(self, key: str, value: str, ttl: int | None = None):
        self.store[key] = value


@pytest.fixture
def cache() -> FakeCache:
    return FakeCache()


async def test_default_state_is_locked(cache):
    assert await overrides.get_state(cache, "c1") == overrides.LOCKED


async def test_key1_moves_to_pending(cache):
    decision = await overrides.advance(cache, "c1", "Please OVERRIDE RULE: scope-discipline for this task")
    assert decision.state.startswith("PENDING:")
    assert decision.rule == "scope-discipline"
    unlocked, _ = await overrides.is_unlocked(cache, "c1")
    assert unlocked is False


async def test_key2_requires_prior_pending(cache):
    # KEY 2 with no pending request must not unlock anything.
    decision = await overrides.advance(cache, "c1", "YES, OVERRIDE scope-discipline")
    assert decision.transitioned is False
    unlocked, _ = await overrides.is_unlocked(cache, "c1")
    assert unlocked is False


async def test_two_key_flow_unlocks(cache):
    await overrides.advance(cache, "c1", "OVERRIDE RULE: scope-discipline")
    decision = await overrides.advance(cache, "c1", "YES, OVERRIDE scope-discipline")
    assert decision.state.startswith("UNLOCKED:")
    unlocked, rule = await overrides.is_unlocked(cache, "c1")
    assert unlocked is True
    assert rule == "scope-discipline"


async def test_unrelated_message_after_pending_does_not_unlock(cache):
    await overrides.advance(cache, "c1", "OVERRIDE RULE: scope-discipline")
    decision = await overrides.advance(cache, "c1", "actually let's keep going normally")
    assert decision.transitioned is False
    unlocked, _ = await overrides.is_unlocked(cache, "c1")
    assert unlocked is False


async def test_relock_resets_state(cache):
    await overrides.advance(cache, "c1", "OVERRIDE RULE: scope-discipline")
    await overrides.advance(cache, "c1", "YES, OVERRIDE scope-discipline")
    await overrides.relock(cache, "c1")
    unlocked, _ = await overrides.is_unlocked(cache, "c1")
    assert unlocked is False


async def test_conversations_are_isolated(cache):
    await overrides.advance(cache, "c1", "OVERRIDE RULE: scope-discipline")
    await overrides.advance(cache, "c1", "YES, OVERRIDE scope-discipline")
    unlocked_other, _ = await overrides.is_unlocked(cache, "c2")
    assert unlocked_other is False
