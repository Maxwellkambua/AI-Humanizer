"""Cheap post-LLM normalization. Keep this conservative — the LLM does the
stylistic work; this only removes artifacts and fixes spacing."""
import re


def cleanup(text: str) -> str:
    t = text.strip()
    # Strip markdown fences the model may have added.
    t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
    t = re.sub(r"\n?```$", "", t)
    # Collapse excess blank lines and spaces.
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    # Remove spaces before punctuation.
    t = re.sub(r"\s+([,.!?;:])", r"\1", t)
    return t.strip()