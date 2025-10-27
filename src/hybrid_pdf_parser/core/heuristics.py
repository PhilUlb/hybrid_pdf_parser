"""Deterministic scoring and selection heuristics."""

from dataclasses import dataclass
from typing import Literal

from hybrid_pdf_parser.config.schema import HeuristicsConfig
from hybrid_pdf_parser.core.segmentation import Segment


@dataclass
class Choice:
    """Represents a selection choice."""

    source: Literal["T", "V", "AMBIGUOUS"]
    selected_text: str
    reason: str


def score_segment(seg: Segment) -> float:
    """
    Compute quality score for a text segment.

    Args:
        seg: Text segment

    Returns:
        Quality score between 0 and 1
    """
    if not seg or not seg.text:
        return 0.0

    text = seg.text
    if not text:
        return 0.0

    # Alnum ratio: proportion of alphanumeric characters
    alnum_count = sum(1 for c in text if c.isalnum())
    alnum_ratio = alnum_count / len(text) if len(text) > 0 else 0.0

    # Weird char rate: proportion of replacement characters
    weird_count = text.count("")
    weird_rate = weird_count / len(text) if len(text) > 0 else 0.0

    # Average token length
    tokens = text.split()
    avg_token_len = sum(len(t) for t in tokens) / len(tokens) if tokens else 0.0

    # Structural bonuses
    structural_bonus = 0.0
    if seg.type.value == "table":
        structural_bonus = 0.2
    elif seg.type.value == "list_item":
        structural_bonus = 0.15
    elif seg.type.value == "heading":
        structural_bonus = 0.1

    # Combine scores
    score = (
        alnum_ratio * 0.6 +  # Primary quality indicator
        (1 - weird_rate) * 0.3 +  # Penalize weird chars
        min(avg_token_len / 10.0, 0.1) +  # Bonus for reasonable token length
        structural_bonus  # Bonus for structure
    )

    return min(max(score, 0.0), 1.0)


def choose_segment(
    t_seg: Segment | None,
    v_seg: Segment | None,
    t_score: float,
    v_score: float,
    config: HeuristicsConfig,
) -> Choice:
    """
    Choose between T and V segments using deterministic heuristics.

    Args:
        t_seg: Text extraction segment
        v_seg: Vision extraction segment
        t_score: Quality score for T segment
        v_score: Quality score for V segment
        config: Heuristics configuration

    Returns:
        Choice object with selected text and reason
    """
    # Handle missing segments
    if not t_seg and not v_seg:
        return Choice(source="T", selected_text="", reason="No segments available")
    if not t_seg:
        return Choice(source="V", selected_text=v_seg.text, reason="T segment missing")
    if not v_seg:
        return Choice(source="T", selected_text=t_seg.text, reason="V segment missing")

    # Calculate score difference
    score_diff = abs(t_score - v_score)

    # Check for ambiguity
    if score_diff < config.ambiguity_band:
        # Check length ratio
        len_ratio = max(len(t_seg.text), len(v_seg.text)) / min(len(t_seg.text), len(v_seg.text))
        if len_ratio > 1.5:
            return Choice(
                source="AMBIGUOUS",
                selected_text="",
                reason=f"Ambiguous: scores too close (diff={score_diff:.3f}, len_ratio={len_ratio:.2f})",
            )

    # Check structural cues
    v_has_structure = v_seg.type.value in ["table", "list_item", "heading"]
    t_has_structure = t_seg.type.value in ["table", "list_item", "heading"]

    if v_has_structure and not t_has_structure:
        return Choice(
            source="V",
            selected_text=v_seg.text,
            reason=f"V has {v_seg.type.value} structure, T does not",
        )

    # Check score margin
    if t_score > v_score + config.score_margin:
        return Choice(source="T", selected_text=t_seg.text, reason=f"T score higher by {t_score - v_score:.3f}")
    if v_score > t_score + config.score_margin:
        return Choice(source="V", selected_text=v_seg.text, reason=f"V score higher by {v_score - t_score:.3f}")

    # Default: prefer T (text-first)
    return Choice(source="T", selected_text=t_seg.text, reason="Default: text-first preferred")

