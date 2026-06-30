"""Semantic verifier (LLM-as-judge) for the irreducibly-semantic rules.

Purpose: approximate enforcement of rules that cannot be decided by code — chiefly scope
discipline ("did the response change only what was requested?") and unrequested-extra
detection. A second, cheap model (Haiku by default) is asked one closed question and must
answer PASS or FAIL. This *reduces* violations; per the enforcement guide it can never
*guarantee* them, because a model judging a model is still probabilistic.

Design choices:
  - The verifier is OFF by default (GOV_ENABLE_VERIFIER) because it adds latency and cost.
  - It fails OPEN: if the judge errors or times out, the response is allowed (with a logged
    warning) rather than taking down all traffic. Hard guarantees live in the deterministic
    guards, not here, so a verifier outage must not become a denial of service.

Ownership: the LiteLLM enforcement layer (litellm/).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from .settings import SETTINGS

logger = logging.getLogger("governance.verifier")

_SYSTEM = (
    "You are a strict compliance verifier. You are given a user's request and an assistant's "
    "proposed response. Decide ONLY whether the response stays within the explicit scope of the "
    "request and introduces no unrequested changes, assumptions, or 'helpful extras'. "
    "Answer with exactly 'PASS' or 'FAIL: <one-line reason>'. Output nothing else."
)


@dataclass(frozen=True)
class VerdictResult:
    """Verifier outcome. ``ok`` is True for PASS or when verification was skipped/failed-open."""

    ok: bool
    reason: str


def _interpret(raw: str) -> VerdictResult:
    """Map the judge's raw text to a verdict. Unrecognized output fails open."""
    answer = (raw or "").strip()
    upper = answer.upper()
    if upper.startswith("PASS"):
        return VerdictResult(True, "Verifier: PASS")
    if upper.startswith("FAIL"):
        return VerdictResult(False, answer)
    logger.warning("Verifier returned unrecognized output; failing open: %r", answer)
    return VerdictResult(True, "Verifier: unrecognized output (failed open)")


async def verify_scope(user_request: str, proposed_output: str) -> VerdictResult:
    """Ask the judge model whether ``proposed_output`` stays within ``user_request`` scope.

    Returns a passing verdict (fail-open) when the verifier is disabled or errors out.
    """
    if not SETTINGS.enable_semantic_verifier:
        return VerdictResult(True, "Verifier disabled")

    try:
        import litellm

        response = await litellm.acompletion(
            model=SETTINGS.verifier_model,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": f"REQUEST:\n{user_request}\n\nRESPONSE:\n{proposed_output}"},
            ],
            temperature=0,
            max_tokens=60,
            stream=False,
        )
        raw = response["choices"][0]["message"]["content"]
        return _interpret(raw)
    except Exception as exc:  # noqa: BLE001 — verifier must never crash the request path.
        logger.warning("Verifier call failed; failing open: %s", exc)
        return VerdictResult(True, "Verifier error (failed open)")
