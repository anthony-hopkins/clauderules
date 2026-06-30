"""Governance guards for the LiteLLM proxy.

This package turns the prose Prime Directives into deterministic enforcement that runs
*outside* the model and can hard-block it. The public entry point is
``proxy_handler_instance`` (referenced from config.yaml as ``guards.proxy_handler_instance``).

Modules:
    settings         -- env-driven configuration, resolved once at startup.
    output_rules     -- pure deterministic input/output checks (secrets, override token).
    overrides        -- two-key Override Protocol state machine (proxy-side).
    verifier         -- optional semantic LLM-as-judge (scope/intent), fail-open.
    governance_guard -- the CustomLogger wiring it all into the proxy lifecycle.

``proxy_handler_instance`` / ``GovernanceGuard`` are imported lazily (PEP 562) so the
pure-Python deterministic modules can be unit-tested without the heavy ``litellm`` runtime
installed, while the proxy still resolves them at startup.
"""

from __future__ import annotations

from typing import Any

__all__ = ["GovernanceGuard", "proxy_handler_instance"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from . import governance_guard

        return getattr(governance_guard, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
