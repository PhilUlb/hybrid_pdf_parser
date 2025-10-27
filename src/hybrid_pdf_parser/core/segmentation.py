"""Text segmentation into sentences, paragraphs, and structural elements."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List


class SegmentType(Enum):
    """Type of text segment."""

    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    LIST_ITEM = "list_item"
    HEADING = "heading"


@dataclass
class Segment:
    """Represents a segment of extracted text."""

    text: str
    start: int
    end: int
    type: SegmentType

    def __len__(self) -> int:
        """Return length of segment text."""
        return len(self.text)


def detect_heading(text: str) -> bool:
    """
    Detect if text is a markdown heading.

    Args:
        text: Text to check

    Returns:
        True if heading detected
    """
    # ATX heading: # Title
    if re.match(r"^#{1,6}\s", text.strip()):
        return True
    # Setext heading: Title\n=== or ---
    if re.search(r"^.+\n[-=]{3,}\s*$", text, re.MULTILINE):
        return True
    return False


def detect_list(text: str) -> bool:
    """
    Detect if text is a list item.

    Args:
        text: Text to check

    Returns:
        True if list item detected
    """
    return bool(re.match(r"^\s*(\*|-|\+|\d+\.)\s+", text))


def detect_table(text: str) -> bool:
    """
    Detect if text contains a markdown table.

    Args:
        text: Text to check

    Returns:
        True if table detected
    """
    lines = text.split("\n")
    pipe_count = sum(1 for line in lines if "|" in line)
    # Need at least 2 rows with pipes
    return pipe_count >= 2 and all("|" in line for line in lines if line.strip())


def segment_text(text: str) -> List[Segment]:
    """
    Segment text into sentences and paragraphs with structural detection.

    Args:
        text: Input text

    Returns:
        List of Segments with type annotations
    """
    segments = []
    lines = text.split("\n")
    current_paragraph = []
    start_idx = 0

    for line in lines:
        line = line.strip()
        if not line:
            # Empty line - paragraph break
            if current_paragraph:
                para_text = "\n".join(current_paragraph)
                seg_type = _determine_segment_type(para_text)
                segment = Segment(
                    text=para_text,
                    start=start_idx,
                    end=start_idx + len(para_text),
                    type=seg_type,
                )
                segments.append(segment)
                start_idx = segment.end
                current_paragraph = []
            continue

        current_paragraph.append(line)

    # Handle remaining paragraph
    if current_paragraph:
        para_text = "\n".join(current_paragraph)
        seg_type = _determine_segment_type(para_text)
        segment = Segment(
            text=para_text,
            start=start_idx,
            end=start_idx + len(para_text),
            type=seg_type,
        )
        segments.append(segment)

    return segments


def _determine_segment_type(text: str) -> SegmentType:
    """
    Determine the type of a text segment.

    Args:
        text: Text segment

    Returns:
        SegmentType
    """
    if detect_table(text):
        return SegmentType.TABLE
    if detect_list(text):
        return SegmentType.LIST_ITEM
    if detect_heading(text):
        return SegmentType.HEADING
    # Default to paragraph if multi-line, sentence if single line
    if "\n" in text:
        return SegmentType.PARAGRAPH
    return SegmentType.SENTENCE

