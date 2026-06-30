"""Open WebUI governance filter — REINFORCEMENT ONLY, never an enforcement point.

Paste this into Open WebUI (Workspace -> Functions -> Filter) to improve the chat UX around
governance: surface a banner that the conversation is governed, and tag messages that look
like override requests so users see the two-key flow.

CRITICAL: Open WebUI's ``outlet`` runs ONLY for WebUI chat requests, not for direct API
calls to the proxy. Anyone with the proxy key bypasses this entirely. All hard guarantees
live in the LiteLLM guards (litellm/guards/), which a client cannot route around. Treat
everything here as a nicety, never as a control.
"""

from __future__ import annotations

import re

_OVERRIDE_HINT = re.compile(r"\bOVERRIDE RULE:\s*[\w\-./]+", re.IGNORECASE)
_BANNER = "[governed] This conversation is enforced by the governance proxy."


class Filter:
    """Open WebUI filter. Advisory only; the real enforcement is in LiteLLM."""

    def __init__(self) -> None:
        self.toggle = True
        self.icon = "shield"

    def inlet(self, body: dict, __user__: dict | None = None) -> dict:
        """Prepend a one-line advisory banner; the proxy still re-injects the real core."""
        messages = body.get("messages", [])
        if messages and not any(_BANNER in str(m.get("content", "")) for m in messages):
            messages.insert(0, {"role": "system", "content": _BANNER})
            body["messages"] = messages
        return body

    def outlet(self, body: dict, __user__: dict | None = None) -> dict:
        """WebUI-only display tweak: note when the last user turn looked like an override request."""
        messages = body.get("messages", [])
        last_user = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        if last_user and _OVERRIDE_HINT.search(str(last_user.get("content", ""))):
            for message in reversed(messages):
                if message.get("role") == "assistant":
                    note = "\n\n_Override request detected — confirm with `YES, OVERRIDE <rule>` to grant (two-key protocol)._"
                    if note not in str(message.get("content", "")):
                        message["content"] = str(message.get("content", "")) + note
                    break
        return body
