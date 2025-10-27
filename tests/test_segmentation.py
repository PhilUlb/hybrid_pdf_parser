"""Tests for text segmentation."""

from hybrid_pdf_parser.core.segmentation import (
    detect_heading,
    detect_list,
    detect_table,
    segment_text,
    SegmentType,
)


def test_detect_heading():
    """Test heading detection."""
    assert detect_heading("# Title")
    assert detect_heading("## Title")
    assert detect_heading("### Title")
    assert not detect_heading("Not a heading")
    assert not detect_heading("Title\n====")  # Setext needs to be full match


def test_detect_list():
    """Test list detection."""
    assert detect_list("- item")
    assert detect_list("* item")
    assert detect_list("1. item")
    assert detect_list("   * item")  # With indentation
    assert not detect_list("Not a list")


def test_detect_table():
    """Test table detection."""
    table_text = "| col1 | col2 |\n|------|------|\n| val1 | val2 |"
    assert detect_table(table_text)

    non_table = "Just text\nMore text"
    assert not detect_table(non_table)


def test_segment_text():
    """Test text segmentation."""
    text = """# Heading

This is a paragraph.

- Item 1
- Item 2

Another paragraph here.
"""
    segments = segment_text(text)

    assert len(segments) > 0
    # Check that heading was detected
    heading_segs = [s for s in segments if s.type == SegmentType.HEADING]
    assert len(heading_segs) > 0

