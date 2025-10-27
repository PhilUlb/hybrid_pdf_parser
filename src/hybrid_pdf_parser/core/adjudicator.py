"""LLM-based adjudication for ambiguous segments."""

from dataclasses import dataclass
from typing import List

from hybrid_pdf_parser.vendors.base import AdjudicatorBackend, AdjudicationResult


@dataclass
class AmbiguousPair:
    """Represents a pair of ambiguous T and V segments."""

    t_seg: "Segment"
    v_seg: "Segment"
    context_before: str
    context_after: str
    page_num: int
    segment_idx: int


def build_context(segments: List["Segment"], idx: int, max_length: int = 200) -> tuple[str, str]:
    """
    Build context before and after a segment.

    Args:
        segments: List of all segments
        idx: Index of current segment
        max_length: Maximum context length

    Returns:
        Tuple of (context_before, context_after)
    """
    before_text = ""
    if idx > 0:
        before_text = segments[idx - 1].text[-max_length:]
        # Try to get more context from earlier segments
        for i in range(max(0, idx - 3), idx - 1):
            before_text = segments[i].text + " " + before_text
        before_text = before_text[-max_length:]

    after_text = ""
    if idx < len(segments) - 1:
        after_text = segments[idx + 1].text[:max_length]
        # Try to get more context from later segments
        for i in range(idx + 2, min(len(segments), idx + 4)):
            after_text = after_text + " " + segments[i].text[:max_length]
        after_text = after_text[:max_length]

    return before_text, after_text


def adjudicate_batch(
    pairs: List[AmbiguousPair],
    backend: AdjudicatorBackend,
) -> List[AdjudicationResult]:
    """
    Adjudicate a batch of ambiguous segment pairs.

    Args:
        pairs: List of ambiguous pairs
        backend: Adjudicator backend

    Returns:
        List of AdjudicationResult objects
    """
    results = []

    for pair in pairs:
        try:
            result = backend.select(
                context_before=pair.context_before[:200],
                candidate_a=pair.t_seg.text,
                candidate_b=pair.v_seg.text,
                context_after=pair.context_after[:200],
            )
            results.append(result)
        except Exception as e:
            # On error, fall back to deterministic choice
            print(f"Adjudication failed for segment {pair.segment_idx}: {e}")
            # Default to T candidate on error
            results.append(AdjudicationResult(pick="A", text=pair.t_seg.text))

    return results

