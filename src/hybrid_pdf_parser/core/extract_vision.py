"""Vision OCR extraction."""

from typing import TYPE_CHECKING

from hybrid_pdf_parser.vendors.base import VisionBackend

if TYPE_CHECKING:
    from PIL import Image


def extract_vision_candidate(image: "Image.Image", backend: VisionBackend) -> str:
    """
    Extract text from image using vision backend.

    Args:
        image: PIL Image
        backend: Vision backend implementation

    Returns:
        Extracted markdown text
    """
    prompt = "Convert this single page image to clean GitHub-flavored Markdown. Preserve headings (#…), lists, tables (Markdown pipes), inline formatting. Return Markdown only."

    return backend.extract(image, prompt=prompt)

