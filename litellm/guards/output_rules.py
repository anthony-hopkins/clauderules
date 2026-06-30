"""Deterministic input/output guardrails.

Purpose: implement the rules that are decidable by code alone (no model judgment) so they
can hard-block with 100% reliability. Per the enforcement guide, only deterministic rules
can be made truly unbreakable; this module is where those live.

Covers:
  - Secret/credential pattern scanning for both inbound prompts and outbound responses.
  - Override-token consistency: the model may only assert an override (emit the ack token)
    when the proxy has actually unlocked one; otherwise the response is rejected.

Ownership: the LiteLLM enforcement layer (litellm/). Pure functions only — no I/O, no
network — so the logic is unit-testable without a running proxy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .settings import OVERRIDE_ACK_TOKEN

# Patterns that indicate a leaked secret. Intentionally conservative: each matches a
# well-known credential prefix/format so false positives stay low. Extend as needed.
_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b")),
    ("github_token", re.compile(r"\bgh[posru]_[A-Za-z0-9]{30,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("generic_bearer", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}\b")),
)

# Phrases that claim an override is in effect. If any appears without the ack token, the
# model is asserting authority it was never granted — a hard violation.
_OVERRIDE_CLAIM = re.compile(r"(?i)\boverride\s+(?:granted|approved|unlocked|in effect|active)\b")


@dataclass(frozen=True)
class RuleResult:
    """Outcome of a deterministic check: ``ok`` plus any human-readable violations."""

    ok: bool
    violations: tuple[str, ...]

    @classmethod
    def passed(cls) -> "RuleResult":
        return cls(ok=True, violations=())

    @classmethod
    def failed(cls, *violations: str) -> "RuleResult":
        return cls(ok=False, violations=tuple(violations))


def scan_secrets(text: str) -> tuple[str, ...]:
    """Return the names of every secret pattern found in ``text`` (empty tuple if clean)."""
    if not text:
        return ()
    return tuple(name for name, pattern in _SECRET_PATTERNS if pattern.search(text))


def check_input(text: str, *, block_secrets: bool) -> RuleResult:
    """Validate an inbound user message. Blocks secret-bearing input when enabled."""
    if block_secrets:
        found = scan_secrets(text)
        if found:
            return RuleResult.failed(f"Inbound message contains secret-like content: {', '.join(found)}.")
    return RuleResult.passed()


def check_output(text: str, *, override_unlocked: bool, block_secrets: bool) -> RuleResult:
    """Validate an outbound model response against deterministic rules.

    Args:
        text: the model's response content.
        override_unlocked: whether the proxy has granted an override for this turn.
        block_secrets: whether to reject responses containing secret-like content.
    """
    violations: list[str] = []

    if block_secrets:
        found = scan_secrets(text)
        if found:
            violations.append(f"Response contains secret-like content: {', '.join(found)}.")

    ack_present = OVERRIDE_ACK_TOKEN in text
    claims_override = bool(_OVERRIDE_CLAIM.search(text)) or ack_present

    if claims_override and not override_unlocked:
        violations.append("Response asserts an override that the proxy has not granted.")
    if ack_present and not override_unlocked:
        violations.append("Override acknowledgment token emitted while conversation is LOCKED.")

    return RuleResult.passed() if not violations else RuleResult.failed(*violations)
