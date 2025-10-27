"""Ollama backend implementation for vision and adjudication."""

import base64
import io
import json
from typing import TYPE_CHECKING

import httpx

from hybrid_pdf_parser.vendors.base import AdjudicationResult, AdjudicatorBackend, VisionBackend

if TYPE_CHECKING:
    from PIL import Image

OLLAMA_VISION_PROMPT = "Convert this single page image to clean GitHub-flavored Markdown. Preserve headings (#…), lists, tables (Markdown pipes), inline formatting. Return Markdown only."

OLLAMA_ADJUDICATOR_PROMPT = """You are an extraction adjudicator. Given two alternatives (A and B) for the same snippet, select exactly one. Do not rewrite. Return the chosen text verbatim."""


class OllamaVisionBackend(VisionBackend):
    """Ollama backend for vision OCR."""

    def __init__(self, model: str = "qwen2.5-vl", api_base: str = "http://localhost:11434", timeout: int = 60):
        """
        Initialize Ollama vision backend.

        Args:
            model: Model name (e.g., qwen2.5-vl, llava, moondream)
            api_base: Ollama API base URL
            timeout: Request timeout in seconds
        """
        self.model = model
        self.api_base = api_base
        self.timeout = timeout

    def _image_to_base64(self, image: "Image.Image") -> str:
        """Convert PIL Image to base64 string."""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode("utf-8")

    def extract(self, image: "Image.Image", prompt: str | None = None) -> str:
        """
        Extract text from image using Ollama vision model.

        Args:
            image: PIL Image
            prompt: Optional custom prompt

        Returns:
            Extracted markdown text
        """
        prompt = prompt or OLLAMA_VISION_PROMPT
        image_data = self._image_to_base64(image)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "options": {"temperature": 0},
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.api_base}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            raise RuntimeError(f"Ollama vision extraction failed: {e}") from e


class OllamaAdjudicatorBackend(AdjudicatorBackend):
    """Ollama backend for adjudication (selection-only)."""

    def __init__(self, model: str = "llama3.1", api_base: str = "http://localhost:11434", timeout: int = 60):
        """
        Initialize Ollama adjudicator backend.

        Args:
            model: Text-only model name (e.g., llama3.1, mistral)
            api_base: Ollama API base URL
            timeout: Request timeout in seconds
        """
        self.model = model
        self.api_base = api_base
        self.timeout = timeout

    def select(
        self,
        context_before: str,
        candidate_a: str,
        candidate_b: str,
        context_after: str,
    ) -> AdjudicationResult:
        """
        Select one of two candidates using Ollama model.

        Args:
            context_before: Previous context
            candidate_a: First candidate (A)
            candidate_b: Second candidate (B)
            context_after: Following context

        Returns:
            AdjudicationResult with selected candidate
        """
        user_prompt = f"""{OLLAMA_ADJUDICATOR_PROMPT}

Context before:
{context_before}

Option A:
{candidate_a}

Option B:
{candidate_b}

Context after:
{context_after}

Select A or B and return the chosen text verbatim. Do not rewrite or merge. Return JSON format: {{"pick": "A" or "B", "text": "<verbatim chosen text>"}}"""

        payload = {
            "model": self.model,
            "prompt": user_prompt,
            "stream": False,
            "options": {"temperature": 0},
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.api_base}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                response_text = result.get("response", "{}")

                # Parse JSON response
                parsed = json.loads(response_text)
                pick = parsed.get("pick", "A")
                text = parsed.get("text", candidate_a if pick == "A" else candidate_b)

                return AdjudicationResult(pick=pick, text=text)
        except Exception as e:
            raise RuntimeError(f"Ollama adjudication failed: {e}") from e

