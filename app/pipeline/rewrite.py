from ..prompts.rewrite import REWRITE_SYSTEM, build_user_prompt
from ..providers.base import HumanizerProvider


async def rewrite_paragraph(
    provider: HumanizerProvider,
    paragraph: str,
    tone: str,
    context: str = "",
) -> str:
    user = build_user_prompt(paragraph, tone, context)
    return await provider.complete(
        REWRITE_SYSTEM, user, max_tokens=1500, temperature=0.75
    )