"""Sequence alignment for T (text) and V (vision) extraction candidates."""

from dataclasses import dataclass
from typing import List

from rapidfuzz import fuzz


@dataclass
class AlignedPair:
    """Represents an aligned pair of T and V segments."""

    t_seg: "Segment | None"
    v_seg: "Segment | None"
    similarity: float

    def is_empty(self) -> bool:
        """Check if both segments are None."""
        return self.t_seg is None and self.v_seg is None


def normalize_text(text: str) -> str:
    """
    Normalize text for alignment comparison.

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    # Convert to lowercase, strip, collapse whitespace
    text = text.lower().strip()
    text = " ".join(text.split())
    return text


def align_segments(t_segments: List["Segment"], v_segments: List["Segment"]) -> List[AlignedPair]:
    """
    Align T and V segments using fuzzy matching.

    Args:
        t_segments: Text extraction segments
        v_segments: Vision extraction segments

    Returns:
        List of AlignedPair objects
    """
    if not t_segments and not v_segments:
        return []

    # Build normalized texts for matching
    t_texts = [normalize_text(seg.text) for seg in t_segments]
    v_texts = [normalize_text(seg.text) for seg in v_segments]

    # Use rapidfuzz for fuzzy matching with windowing
    aligned_pairs = []
    t_idx = 0
    v_idx = 0
    window_size = 3  # Look ahead window

    while t_idx < len(t_segments) or v_idx < len(v_segments):
        if t_idx >= len(t_segments):
            # Only V segments remain
            aligned_pairs.append(AlignedPair(t_seg=None, v_seg=v_segments[v_idx], similarity=0.0))
            v_idx += 1
            continue

        if v_idx >= len(v_segments):
            # Only T segments remain
            aligned_pairs.append(AlignedPair(t_seg=t_segments[t_idx], v_seg=None, similarity=0.0))
            t_idx += 1
            continue

        # Find best match in window
        t_text = t_texts[t_idx]
        best_similarity = 0.0
        best_v_idx = v_idx

        # Search in forward window
        for i in range(v_idx, min(v_idx + window_size, len(v_segments))):
            similarity = fuzz.ratio(t_text, v_texts[i])
            if similarity > best_similarity:
                best_similarity = similarity
                best_v_idx = i

        # If good match found, align
        if best_similarity > 50:  # Threshold for matching
            # Add unmatched V segments before the match
            for i in range(v_idx, best_v_idx):
                aligned_pairs.append(AlignedPair(t_seg=None, v_seg=v_segments[i], similarity=0.0))

            aligned_pairs.append(
                AlignedPair(t_seg=t_segments[t_idx], v_seg=v_segments[best_v_idx], similarity=best_similarity / 100.0)
            )
            t_idx += 1
            v_idx = best_v_idx + 1
        else:
            # No good match, add T segment unaligned
            aligned_pairs.append(AlignedPair(t_seg=t_segments[t_idx], v_seg=None, similarity=0.0))
            t_idx += 1

    return aligned_pairs

