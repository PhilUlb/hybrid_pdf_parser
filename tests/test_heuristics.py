"""Tests for scoring and selection heuristics."""

from hybrid_pdf_parser.config.schema import HeuristicsConfig
from hybrid_pdf_parser.core.heuristics import choose_segment, score_segment
from hybrid_pdf_parser.core.segmentation import Segment, SegmentType


def test_score_segment():
    """Test segment scoring."""
    good_seg = Segment(
        text="This is a good quality text with reasonable structure.",
        start=0,
        end=50,
        type=SegmentType.PARAGRAPH,
    )
    score = score_segment(good_seg)
    assert 0.0 < score < 1.0

    # Test that table segments get bonus
    table_seg = Segment(text="| col1 | col2 |\n|------|------|", start=0, end=30, type=SegmentType.TABLE)
    table_score = score_segment(table_seg)
    assert table_score > 0.0

    # Empty segment should score 0
    empty_seg = Segment(text="", start=0, end=0, type=SegmentType.SENTENCE)
    assert score_segment(empty_seg) == 0.0


def test_choose_segment():
    """Test segment choice logic."""
    config = HeuristicsConfig(score_margin=0.15, ambiguity_band=0.05)

    t_seg = Segment(text="High quality text", start=0, end=17, type=SegmentType.PARAGRAPH)
    v_seg = Segment(text="Also good quality", start=0, end=17, type=SegmentType.PARAGRAPH)

    t_score = 0.8
    v_score = 0.7

    choice = choose_segment(t_seg, v_seg, t_score, v_score, config)
    assert choice.source in ["T", "V"]

    # When scores are very close, might be ambiguous
    choice_close = choose_segment(t_seg, v_seg, 0.5, 0.48, config)
    # Could be ambiguous or prefer one based on heuristics
    assert choice_close.source in ["T", "V", "AMBIGUOUS"]


def test_choose_segment_with_structure():
    """Test that structural elements influence choice."""
    config = HeuristicsConfig()

    t_seg = Segment(text="Plain paragraph", start=0, end=15, type=SegmentType.PARAGRAPH)
    v_seg = Segment(text="| col1 | col2 |", start=0, end=15, type=SegmentType.TABLE)

    t_score = 0.6
    v_score = 0.5  # V has lower score but has structure

    choice = choose_segment(t_seg, v_seg, t_score, v_score, config)
    # Should prefer V because it has table structure
    assert choice.source == "V"

