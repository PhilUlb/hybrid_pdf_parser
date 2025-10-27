"""PDF to image rendering with PyMuPDF."""

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

import fitz

from hybrid_pdf_parser.config.schema import RenderConfig

if TYPE_CHECKING:
    from PIL import Image


def compute_page_hash(doc: fitz.Document, page_num: int) -> str:
    """
    Compute hash of page content for caching.

    Args:
        doc: PyMuPDF document
        page_num: Page number (0-indexed)

    Returns:
        SHA256 hash as hex string
    """
    page = doc[page_num]
    text = page.get_text()
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def render_page_to_image(doc: fitz.Document, page_num: int, config: RenderConfig) -> "Image.Image":
    """
    Render a PDF page to PIL Image.

    Args:
        doc: PyMuPDF document
        page_num: Page number (0-indexed)
        config: Rendering configuration

    Returns:
        PIL Image
    """
    page = doc[page_num]

    # Calculate scaling factor to cap long edge
    width, height = page.rect.width, page.rect.height
    long_edge = max(width, height)
    scale = min(1.0, config.max_long_edge / (long_edge * config.dpi / 72))

    # Calculate matrix for rendering
    matrix = fitz.Matrix(config.dpi / 72 * scale, config.dpi / 72 * scale)

    # Render to pixmap (no alpha if alpha=False)
    pix = page.get_pixmap(matrix=matrix, alpha=config.alpha)

    # Convert to PIL Image
    from PIL import Image

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    return img


def save_image_to_cache(image: "Image.Image", page_hash: str, cache_dir: Path) -> Path:
    """
    Save rendered image to cache.

    Args:
        image: PIL Image
        page_hash: Page hash for filename
        cache_dir: Cache directory

    Returns:
        Path to cached image
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{page_hash}.png"
    image.save(cache_path, format="PNG")
    return cache_path


def load_image_from_cache(page_hash: str, cache_dir: Path) -> "Image.Image | None":
    """
    Load rendered image from cache.

    Args:
        page_hash: Page hash
        cache_dir: Cache directory

    Returns:
        PIL Image or None if not cached
    """
    cache_path = cache_dir / f"{page_hash}.png"
    if not cache_path.exists():
        return None

    from PIL import Image

    return Image.open(cache_path)

