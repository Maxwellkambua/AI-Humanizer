from app.pipeline.citations import (
    extract_protected,
    restore_protected,
    find_citations,
    has_leftover_placeholders,
)


def test_extracts_apa_citation():
    text = "This is well studied (Smith, 2020, p. 12)."
    protected, tokens = extract_protected(text)
    assert "[[PROTECT_1]]" in protected
    assert restore_protected(protected, tokens) == text


def test_extracts_bracket_and_url():
    text = "See [1] and https://example.com/x for details."
    protected, tokens = extract_protected(text)
    assert has_leftover_placeholders(protected)
    assert restore_protected(protected, tokens) == text


def test_multiple_citations_preserve_order():
    text = "One (Smith, 2020). Two (Jones et al., 2021a)."
    protected, tokens = extract_protected(text)
    restored = restore_protected(protected, tokens)
    assert restored == text


def test_find_citations_returns_all():
    cites = find_citations("(Smith, 2020) and [3] and https://a.b/c")
    assert any("Smith, 2020" in c for c in cites)
    assert "[3]" in cites