from openai import AsyncOpenAI

from .base import HumanizerProvider


class OpenAICompatProvider(HumanizerProvider):
    """Works for Groq, Ollama, and Gemini's OpenAI-compatible endpoint."""

    def __init__(self, name: str, base_url: str, api_key: str, model: str):
        self.name = name
        self.model = model
        # Ollama requires a placeholder key but ignores it.
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key or "not-needed")

    async def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 1500,
        temperature: float = 0.7,
    ) -> str:
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return (resp.choices[0].message.content or "").strip()