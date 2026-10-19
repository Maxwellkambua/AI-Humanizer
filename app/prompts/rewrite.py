REWRITE_SYSTEM = """\
You are an editor that rewrites text so it reads like natural human writing
while preserving every fact, citation, quotation, number, and proper noun
EXACTLY.

Rules:
- Vary sentence length sharply: mix 3-6 word sentences with 20-30 word ones.
- Prefer active voice. Convert nominalizations into verbs (utilization → use).
- Use contractions where natural.
- Never use these words or phrases: delve, tapestry, leverage, robust, myriad,
  pivotal, seamless, realm, landscape, foster, meticulous, utilize,
  "it's worth noting", "it is worth noting", "it's important to note",
  "in conclusion", "furthermore", "moreover".
- Allow at most one sentence fragment per paragraph.
- Do not start consecutive sentences with the same word.
- Do NOT touch anything inside [[PROTECT_N]] placeholders — copy verbatim.
- Preserve all facts, numbers, names, and technical terms exactly.
- Keep total length within ±15% of the original.
- Output ONLY the rewritten paragraph. No preamble, no markdown fences.
"""

REWRITE_USER = """\
TONE: {tone}

PREVIOUS CONTEXT (topic continuity only — do not repeat):
{context}

PARAGRAPH TO REWRITE:
{paragraph}
"""

TONE_HINTS = {
    "academic": "Formal, measured, precise. No slang. Keep hedging that carries meaning.",
    "professional": "Clear and direct. Confident but not salesy. Contractions fine.",
    "casual": "Conversational and loose. Short sentences. Contractions encouraged.",
}


def build_user_prompt(paragraph: str, tone: str, context: str) -> str:
    hint = TONE_HINTS.get(tone, TONE_HINTS["academic"])
    return REWRITE_USER.format(
        tone=f"{tone} — {hint}",
        context=context or "(none)",
        paragraph=paragraph,
    )