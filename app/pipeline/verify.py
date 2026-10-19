"""Two-layer verification:
1. Deterministic — every citation string in the original must appear verbatim
   in the rewrite (after placeholder restoration).
2. LLM — ask the same provider (temperature 0) to list any dropped or altered
   facts / caveats. Best-effort: failures are swallowed, not fatal.
"""
import json
import re

from ..providers.base import HumanizerProvider
from .citations import find_citations, has_leftover_placeholders

VERIFY_SYSTEM = (
    "You check whether a rewrite preserves the meaning of the original. "
    "Reply with a JSON array of short issue strings. Empty array if fine."
)

VERIFY_USER = """\
ORIGINAL:
{original}

REWRITTEN:
{rewritten}

List any fact, number, citation, name, or caveat that was dropped or altered.
Reply ONLY with a JSON array, e.g. [] or ["dropped statistic X"].
"""


def deterministic_warnings(original: str, rewritten: str) -> list[str]:
    warnings: list[str] = []
    if has_leftover_placeholders(rewritten):
        warnings.append(
            "Some protected spans (citations/URLs) could not be restored — "
            "the model altered a [[PROTECT_N]] placeholder."
        )
    for cite in find_citations(original):
        if cite not in rewritten:
            warnings.append(f"Citation may have changed or dropped: {cite}")
    return warnings


async def llm_verify(
    provider: HumanizerProvider, original: str, rewritten: str
) -> list[str]:
    try:
        raw = await provider.complete(
            VERIFY_SYSTEM,
            VERIFY_USER.format(original=original, rewritten=rewritten),
            max_tokens=400,
            temperature=0.0,
        )
        m = re.search(r"\[.*\]", raw, re.S)
        if not m:
            return []
        parsed = json.loads(m.group(0))
        return [str(x) for x in parsed] if isinstance(parsed, list) else []
    except Exception:
        return []