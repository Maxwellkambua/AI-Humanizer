"""Extract and restore protected spans before/after the LLM rewrite.

Protects: inline citations like (Smith, 2020, p. 12), bracketed refs [1],
and URLs. Placeholders use [[PROTECT_N]] so the model can copy them verbatim.
"""
import re

_CITE_PATTERNS = [
    # (Smith, 2020) / (Smith et al., 2020, p. 12) / (Smith & Jones 2021a)
    re.compile(
        r"\([A-Z][A-Za-z\-']+(?:\s(?:et\s+al\.?|and|&)\s[A-Za-z\-']+)?"
        r",?\s\d{4}[a-z]?(?:,\spp?\.\s?\d+(?:[-–]\d+)?)?\)"
    ),
    re.compile(r"\[\d+(?:[,–-]\s?\d+)*\]"),  # [1] / [1,2] / [1-3]
    re.compile(r"https?://\S+"),
]

_PLACEHOLDER_RE = re.compile(r"\[\[PROTECT_\d+\]\]")


def extract_protected(text: str) -> tuple[str, dict[str, str]]:
    tokens: dict[str, str] = {}
    counter = 0

    def _repl(match: re.Match) -> str:
        nonlocal counter
        counter += 1
        key = f"[[PROTECT_{counter}]]"
        tokens[key] = match.group(0)
        return key

    for pat in _CITE_PATTERNS:
        text = pat.sub(_repl, text)
    return text, tokens


def restore_protected(text: str, tokens: dict[str, str]) -> str:
    for key, val in tokens.items():
        text = text.replace(key, val)
    return text


def has_leftover_placeholders(text: str) -> bool:
    return bool(_PLACEHOLDER_RE.search(text))


def find_citations(text: str) -> list[str]:
    found: list[str] = []
    for pat in _CITE_PATTERNS:
        found.extend(pat.findall(text))
    return found