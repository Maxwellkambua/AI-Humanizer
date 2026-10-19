import asyncio

from ..config import settings
from ..providers.factory import build_provider
from ..schemas import HumanizeRequest, HumanizeResponse, TextMetrics
from ..utils.metrics import compute_metrics
from .citations import extract_protected, restore_protected
from .cleanup import cleanup
from .preprocess import split_paragraphs
from .rewrite import rewrite_paragraph
from .verify import deterministic_warnings, llm_verify


async def _rewrite_all(provider, paragraphs: list[str], tone: str) -> list[str]:
    sem = asyncio.Semaphore(settings.MAX_CONCURRENCY)

    async def one(i: int, para: str) -> str:
        async with sem:
            # Context = up to 2 preceding ORIGINAL paragraphs. Using originals
            # instead of rewrites lets us run this concurrently without a
            # sequential dependency chain.
            context = "\n\n".join(paragraphs[max(0, i - 2):i])
            out = await rewrite_paragraph(provider, para, tone, context)
            return cleanup(out)

    return await asyncio.gather(*(one(i, p) for i, p in enumerate(paragraphs)))


def _to_metrics(original: str, humanized: str) -> dict[str, TextMetrics]:
    return {
        "original": TextMetrics(**compute_metrics(original)),
        "humanized": TextMetrics(**compute_metrics(humanized)),
    }


async def humanize(req: HumanizeRequest) -> HumanizeResponse:
    provider = build_provider(req.provider)

    # 1. Protect citations/URLs so the model can't touch them.
    protected, tokens = extract_protected(req.text)

    # 2. Chunk.
    paragraphs = split_paragraphs(protected)
    if not paragraphs:
        raise ValueError("nothing to rewrite")

    # 3. Rewrite concurrently.
    rewritten_paras = await _rewrite_all(provider, paragraphs, req.tone)
    rewritten_text = "\n\n".join(rewritten_paras)

    # 4. Restore protected spans.
    humanized = restore_protected(rewritten_text, tokens)

    # 5. Verify.
    warnings = deterministic_warnings(req.text, humanized)
    if req.verify and settings.VERIFY_ENABLED:
        warnings += await llm_verify(provider, req.text, humanized)

    return HumanizeResponse(
        original=req.text,
        humanized=humanized,
        provider=provider.name,
        metrics=_to_metrics(req.text, humanized),
        warnings=warnings,
    )