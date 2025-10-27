"""Tests for segment alignment."""

from hybrid_pdf_parser.core.alignment import AlignedPair, align_segments, normalize_text
from hybrid_pdf_parser.core.segmentation import Segment, SegmentType


def test_normalize_text():
    """Test text normalization."""
    assert normalize_text("  HELLO   WORLD  ") == "hello world"
    assert normalize_text("Hello\n  World") == "hello world"


def create_test_segment(text: str, idx: int) -> Segment:
    """Helper to create test segments."""
    return Segment(text=text, start=idx * 10, end=(idx + 1) * 10, type=SegmentType.SENTENCE)


def test_align_segments():
    """Test segment alignment."""
    t_segments = [
        create_test_segment("Hello world", 0),
        create_test_segment("This is a test", 1),
        create_test_segment("Goodbye", 2),
    ]

    v_segments = [
        create_test_segment("Hello world", 0),
        create_test_segment("This is a test", 1),
        create_test_segment("Goodbye", 2),
    ]

    aligned = align_segments(t_segments, v_segments)

    assert len(aligned) > 0
    # Should have high similarity for identical segments
    assert aligned[0].similarity > 0.9


def test_align_segments_with_differences():
    """Test alignment with differing segments."""
    t_segments = [create_test_segment("Same text", 0), create_test_segment("Different T", 1)]

    v_segments = [create_test_segment("Same text", 0), create_test_segment("Different V", 1)]

    aligned = align_segments(t_segments, v_segments)

    # First segments should match (high similarity)
    assert aligned[0].t_seg is not None
    assert aligned[0].v_seg is not None
    assert aligned[0].similarity > 0.8

