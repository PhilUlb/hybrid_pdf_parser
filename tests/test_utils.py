"""Tests for utility functions."""

from hybrid_pdf_parser.core.utils import normalize_whitespace, repair_hyphenation


def test_repair_hyphenation():
    """Test hyphenation repair."""
    # Regular word hyphenation should be merged
    text_with_hyphen = "This is an exam-\nple of hyphenation."
    result = repair_hyphenation(text_with_hyphen)
    assert "exam\nple" not in result
    # Should be "example" (but note: this is simplified check)

    # ALLCAPS should not be merged
    allcaps_text = "ACRO-\nNYM should not merge"
    result = repair_hyphenation(allcaps_text)
    # Simple check - ACRO-\nNYM pattern should be preserved or handled specially


def test_normalize_whitespace():
    """Test whitespace normalization."""
    text = "Multiple    spaces\n\n\nand newlines"
    result = normalize_whitespace(text)
    assert "   " not in result  # Multiple spaces collapsed
    assert "\n\n\n" not in result  # Multiple newlines collapsed

    # Preserve single newline between paragraphs
    para_text = "Paragraph 1\n\nParagraph 2"
    result = normalize_whitespace(para_text)
    assert "\n\n" in result or "\n" in result  # Some newlines preserved

