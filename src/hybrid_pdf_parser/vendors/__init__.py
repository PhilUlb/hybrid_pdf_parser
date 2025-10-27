"""Backend vendor implementations."""

from hybrid_pdf_parser.vendors.base import (
    AdjudicationResult,
    AdjudicatorBackend,
    VisionBackend,
)
from hybrid_pdf_parser.vendors.openai_backend import (
    OpenAIAdjudicatorBackend,
    OpenAIVisionBackend,
)
from hybrid_pdf_parser.vendors.ollama_backend import (
    OllamaAdjudicatorBackend,
    OllamaVisionBackend,
)

__all__ = [
    "VisionBackend",
    "AdjudicatorBackend",
    "AdjudicationResult",
    "OpenAIVisionBackend",
    "OpenAIAdjudicatorBackend",
    "OllamaVisionBackend",
    "OllamaAdjudicatorBackend",
]

