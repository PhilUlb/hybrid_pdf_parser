"""OpenAI backend implementation for vision and adjudication."""

import base64
import io
import os
from typing import TYPE_CHECKING

from openai import OpenAI

from hybrid_pdf_parser.vendors.base import AdjudicationResult, AdjudicatorBackend, VisionBackend


def get_openai_api_key() -> str:
    """
    Get OpenAI API key from environment variable.

    Returns:
        API key string

    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables.\n"
            "Please set it in your .env file or export it:\n"
            "  export OPENAI_API_KEY=sk-..."
        )
    return api_key

if TYPE_CHECKING:
    from PIL import Image

OPENAI_VISION_SYSTEM_PROMPT = "You are a text extraction assistant. Convert the image to clean GitHub-flavored Markdown. Preserve headings (#…), lists, tables (Markdown pipes), inline formatting. Return Markdown only."

OPENAI_ADJUDICATOR_SYSTEM_PROMPT = """You are an extraction adjudicator. Given two alternatives (A and B) for the same snippet, select exactly one. Do not rewrite. Return the chosen text verbatim."""


class OpenAIVisionBackend(VisionBackend):
    """OpenAI vision backend using GPT-4o for OCR."""

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: str | None = None,
        max_retries: int = 3,
    ):
        """
        Initialize OpenAI vision backend.

        Args:
            model: Model name (e.g., gpt-4o, gpt-4o-mini)
            api_key: OpenAI API key (defaults to env var)
            max_retries: Maximum retry attempts
        """
        self.model = model
        self.client = OpenAI(api_key=api_key or get_openai_api_key())
        self.max_retries = max_retries

    def _image_to_base64(self, image: "Image.Image") -> str:
        """Convert PIL Image to base64 string."""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode("utf-8")

    def extract(self, image: "Image.Image", prompt: str | None = None) -> str:
        """
        Extract text from image using OpenAI vision model.

        Args:
            image: PIL Image
            prompt: Optional custom prompt (defaults to system prompt)

        Returns:
            Extracted markdown text
        """
        prompt = prompt or OPENAI_VISION_SYSTEM_PROMPT

        image_data = self._image_to_base64(image)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
                        ],
                    },
                ],
                temperature=0,
                max_tokens=4000,
            )

            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"OpenAI vision extraction failed: {e}") from e


class OpenAIAdjudicatorBackend(AdjudicatorBackend):
    """OpenAI backend for adjudication (selection-only)."""

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: str | None = None,
        max_retries: int = 3,
    ):
        """
        Initialize OpenAI adjudicator backend.

        Args:
            model: Model name (e.g., gpt-4o)
            api_key: OpenAI API key (defaults to env var)
            max_retries: Maximum retry attempts
        """
        self.model = model
        self.client = OpenAI(api_key=api_key or get_openai_api_key())
        self.max_retries = max_retries

    def select(
        self,
        context_before: str,
        candidate_a: str,
        candidate_b: str,
        context_after: str,
    ) -> AdjudicationResult:
        """
        Select one of two candidates using OpenAI model.

        Args:
            context_before: Previous context
            candidate_a: First candidate (A)
            candidate_b: Second candidate (B)
            context_after: Following context

        Returns:
            AdjudicationResult with selected candidate
        """
        user_prompt = f"""Context before:
{context_before}

Option A:
{candidate_a}

Option B:
{candidate_b}

Context after:
{context_after}

Select A or B and return the chosen text verbatim. Do not rewrite or merge. Return JSON format: {{"pick": "A" or "B", "text": "<verbatim chosen text>"}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": OPENAI_ADJUDICATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )

            result_text = response.choices[0].message.content or ""
            import json

            result = json.loads(result_text)
            pick = result.get("pick", "A")
            text = result.get("text", candidate_a if pick == "A" else candidate_b)

            return AdjudicationResult(pick=pick, text=text)
        except Exception as e:
            raise RuntimeError(f"OpenAI adjudication failed: {e}") from e

