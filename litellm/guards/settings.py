"""Settings loader for the governance guards.

Purpose: centralize all environment-driven configuration for the LiteLLM governance
layer so the guard modules never read ``os.environ`` directly (Prime Directive: no
unchecked env access). Values are read once at import and validated eagerly so the
proxy fails fast on misconfiguration instead of silently degrading enforcement.

Ownership: the LiteLLM enforcement layer (litellm/). Imported by every guard module.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Marker that brackets the injected governance block. Clients must not be able to forge
# it: the pre_call hook strips any inbound message containing it before re-injecting.
GOV_MARKER = "<<GOVERNANCE_CORE_v1>>"

# Literal token the model must emit (and only emit) when acting on a granted override.
# The output guard rejects any response that asserts an override without this token, and
# any response that emits this token while the conversation is LOCKED.
OVERRIDE_ACK_TOKEN = "[[OVERRIDE-ACK]]"

_DEFAULT_CORE = Path(__file__).resolve().parent.parent / "governance_core.md"


def _flag(name: str, default: str = "true") -> bool:
    """Parse a boolean-ish environment flag (``1/true/yes/on`` are truthy)."""
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _read_core(path: Path) -> str:
    """Read the injected governance core from disk, failing loudly if it is missing.

    A missing or empty core means the presence guarantee is broken, so we refuse to
    start rather than serve requests with no governance prompt.
    """
    if not path.is_file():
        raise RuntimeError(f"Governance core not found at {path}; cannot enforce presence.")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise RuntimeError(f"Governance core at {path} is empty; refusing to start.")
    return text


@dataclass(frozen=True)
class GuardSettings:
    """Immutable snapshot of guard configuration resolved at proxy startup."""

    governance_core: str
    force_non_streaming: bool
    block_secrets_in_input: bool
    block_secrets_in_output: bool
    enable_override_state_machine: bool
    enable_semantic_verifier: bool
    verifier_model: str
    override_pending_ttl_seconds: int
    override_unlocked_ttl_seconds: int


def load_settings() -> GuardSettings:
    """Resolve guard settings from the environment. Called once at module import."""
    core_path = Path(os.environ.get("GOVERNANCE_CORE_PATH", str(_DEFAULT_CORE)))
    return GuardSettings(
        governance_core=_read_core(core_path),
        force_non_streaming=_flag("GOV_FORCE_NON_STREAMING", "true"),
        block_secrets_in_input=_flag("GOV_BLOCK_SECRETS_INPUT", "true"),
        block_secrets_in_output=_flag("GOV_BLOCK_SECRETS_OUTPUT", "true"),
        enable_override_state_machine=_flag("GOV_ENABLE_OVERRIDE", "true"),
        enable_semantic_verifier=_flag("GOV_ENABLE_VERIFIER", "false"),
        verifier_model=os.environ.get("GOV_VERIFIER_MODEL", "claude-haiku"),
        override_pending_ttl_seconds=int(os.environ.get("GOV_OVERRIDE_PENDING_TTL", "1800")),
        override_unlocked_ttl_seconds=int(os.environ.get("GOV_OVERRIDE_UNLOCKED_TTL", "120")),
    )


SETTINGS = load_settings()
