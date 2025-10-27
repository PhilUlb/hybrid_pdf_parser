"""Hybrid PDF parser package."""

from hybrid_pdf_parser.__version__ import __version__
from hybrid_pdf_parser.config import PipelineConfig
from hybrid_pdf_parser.core import PdfEnsemblePipeline
from hybrid_pdf_parser.simple import PDFExtractor
from hybrid_pdf_parser.vendors import (
    OllamaAdjudicatorBackend,
    OllamaVisionBackend,
    OpenAIAdjudicatorBackend,
    OpenAIVisionBackend,
)

__all__ = [
    "__version__",
    "PDFExtractor",  # Simple high-level API
    "PdfEnsemblePipeline",  # Low-level API
    "PipelineConfig",
    "OpenAIVisionBackend",
    "OpenAIAdjudicatorBackend",
    "OllamaVisionBackend",
    "OllamaAdjudicatorBackend",
]

