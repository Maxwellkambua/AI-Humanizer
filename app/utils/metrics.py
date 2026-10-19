import re
import statistics

AI_ISMS = [
    "delve", "tapestry", "leverage", "robust", "myriad", "pivotal",
    "seamless", "realm", "landscape", "foster", "meticulous", "utilize",
    "utilization", "it's worth noting", "it is worth noting",
    "it's important to note", "in conclusion",
]


def _sentence_lengths(text: str) -> list[int]:
    sents = re.split(r"(?<=[.!?])\s+", text)
    return [len(s.split()) for s in sents if s.strip()]


def burstiness(text: str) -> float:
    lens = _sentence_lengths(text)
    if len(lens) < 2:
        return 0.0
    mean = statistics.mean(lens) or 1.0
    return round(statistics.pstdev(lens) / mean, 3)


def ai_ism_density(text: str) -> float:
    lower = text.lower()
    words = lower.split()
    if not words:
        return 0.0
    hits = sum(lower.count(t) for t in AI_ISMS)
    return round(100.0 * hits / len(words), 3)


def compute_metrics(text: str) -> dict:
    return {
        "burstiness": burstiness(text),
        "ai_ism_density": ai_ism_density(text),
        "word_count": len(text.split()),
    }