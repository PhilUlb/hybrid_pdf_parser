"""Text extraction using Docling."""

from pathlib import Path

import docling.document_converter
from docling.document_converter import DocumentConverter

from hybrid_pdf_parser.core.utils import normalize_whitespace, repair_hyphenation


def extract_text_candidate(pdf_path: Path, page_num: int) -> str:
    """
    Extract text from a PDF page using Docling.

    Args:
        pdf_path: Path to PDF file
        page_num: Page number (0-indexed)

    Returns:
        Extracted and cleaned text
    """
    # Initialize Docling converter
    converter = DocumentConverter()

    # Convert document - this processes all pages
    doc = converter.convert(str(pdf_path))

    # Docling returns results as a dict with 'content' containing markdown
    # We need to extract just the specific page
    # Note: Docling doesn't directly support page-level extraction in this way
    # This is a simplified version that extracts markdown for the entire document

    # For now, extract from the document content
    # In a production version, you'd need to parse the docling output structure
    # to extract specific pages

    markdown = doc.document.model_dump().get("content", "")
    if isinstance(markdown, dict):
        # Extract text content
        text = markdown.get("text", "")
    else:
        text = str(markdown)

    # Apply cleaning
    text = repair_hyphenation(text)
    text = normalize_whitespace(text)

    return text

