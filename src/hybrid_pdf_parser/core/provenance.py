"""Provenance tracking and reporting."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel


class ProvenanceRecord(BaseModel):
    """Record of provenance for a selected segment."""

    page_num: int
    segment_idx: int
    source: Literal["T", "V", "LLM"]
    llm_pick: Optional[Literal["A", "B"]] = None
    t_score: float
    v_score: float
    chosen_text: str
    backend_used: Optional[str] = None
    timestamp: datetime = datetime.now()


def write_jsonl_report(records: list[ProvenanceRecord], path: Path) -> None:
    """
    Write provenance records to JSONL file.

    Args:
        records: List of provenance records
        path: Output JSONL file path
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")


def insert_provenance_comments(markdown: str, records: list[ProvenanceRecord]) -> str:
    """
    Insert HTML comments with provenance metadata into markdown.

    Args:
        markdown: Original markdown text
        records: Provenance records

    Returns:
        Markdown with provenance comments inserted
    """
    # Group records by page and segment
    by_segment: dict[tuple[int, int], ProvenanceRecord] = {}
    for record in records:
        by_segment[(record.page_num, record.segment_idx)] = record

    lines = markdown.split("\n")
    output = []
    segment_idx = 0
    page_num = 0

    # Simple heuristic: insert comments at paragraph breaks
    for i, line in enumerate(lines):
        if line.strip() == "" and i > 0 and lines[i - 1].strip():
            # Paragraph break - insert provenance comment
            key = (page_num, segment_idx)
            if key in by_segment:
                record = by_segment[key]
                if record.source == "LLM":
                    comment = f"<!-- src:LLM:{record.llm_pick} -->"
                else:
                    comment = f"<!-- src:{record.source} -->"
                output.append(comment)

            segment_idx += 1

        output.append(line)

        # Detect page boundaries (heuristic: heading with # indicates new major section)
        if line.startswith("#"):
            # Could indicate new page/section
            pass

    # Add final provenance comment if needed
    if lines and output[-1].strip():
        key = (page_num, segment_idx)
        if key in by_segment:
            record = by_segment[key]
            if record.source == "LLM":
                comment = f"<!-- src:LLM:{record.llm_pick} -->"
            else:
                comment = f"<!-- src:{record.source} -->"
            output.append(comment)

    return "\n".join(output)

