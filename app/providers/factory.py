from ..config import settings
from .base import HumanizerProvider
from .openai_compat import OpenAICompatProvider


def build_provider(name: str | None = None) -> HumanizerProvider:
    name = (name or settings.DEFAULT_PROVIDER).lower()

    if name == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set")
        return OpenAICompatProvider(
            "groq",
            "https://api.groq.com/openai/v1",
            settings.GROQ_API_KEY,
            settings.GROQ_MODEL,
        )

    if name == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set")
        return OpenAICompatProvider(
            "gemini",
            "https://generativelanguage.googleapis.com/v1beta/openai/",
            settings.GEMINI_API_KEY,
            settings.GEMINI_MODEL,
        )

    if name == "ollama":
        return OpenAICompatProvider(
            "ollama",
            settings.OLLAMA_BASE_URL,
            "not-needed",
            settings.OLLAMA_MODEL,
        )

    raise ValueError(f"unknown provider: {name}")