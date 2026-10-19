from typing import Optional
from pydantic import BaseModel


class HumanizeRequest(BaseModel):
    text: str
    tone: str = "academic"          # academic | professional | casual
    provider: Optional[str] = None  # override settings.DEFAULT_PROVIDER
    verify: bool = True


class TextMetrics(BaseModel):
    burstiness: float
    ai_ism_density: float
    word_count: int


class HumanizeResponse(BaseModel):
    original: str
    humanized: str
    provider: str
    metrics: dict[str, TextMetrics]
    warnings: list[str] = []