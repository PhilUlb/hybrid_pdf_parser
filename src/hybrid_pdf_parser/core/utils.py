"""Utility functions for text processing and I/O."""

import re
from typing import Optional


def repair_hyphenation(text: str) -> str:
    """
    Repair hyphenated words split across lines.

    Merges patterns like "word-\n" followed by "word" into "wordword"
    unless the first part is all uppercase (acronyms).

    Args:
        text: Input text with potential hyphenation

    Returns:
        Text with hyphenation repaired
    """
    # Pattern: word part (not all caps) followed by - and newline, then another word part
    pattern = r"([a-z][\w]*)-[\n\r]+(\w+)"
    result = text

    def merge_match(match):
        first = match.group(1)
        second = match.group(2)
        # If first part is all uppercase (acronym), keep hyphen
        if first.isupper() and len(first) > 1:
            return match.group(0)
        return first + second

    result = re.sub(pattern, merge_match, result)
    return result


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace by collapsing multiple spaces and newlines.

    Args:
        text: Input text with potential extra whitespace

    Returns:
        Text with normalized whitespace
    """
    # Collapse multiple spaces
    text = re.sub(r" +", " ", text)
    # Collapse multiple newlines to maximum 2 (paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace from lines
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines)


def load_config(path: str) -> Optional[dict]:
    """
    Load YAML configuration file.

    Args:
        path: Path to YAML file

    Returns:
        Configuration dictionary or None if file not found
    """
    import yaml
    from pathlib import Path

    config_path = Path(path)
    if not config_path.exists():
        return None

    with config_path.open() as f:
        return yaml.safe_load(f)

