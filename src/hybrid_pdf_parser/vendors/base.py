"""Abstract base classes for backend implementations."""

from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel


class AdjudicationResult(BaseModel):
    """Result from LLM adjudication."""

    pick: Literal["A", "B"]
    text: str


class VisionBackend(ABC):
    """Abstract base class for vision OCR backends."""

    @abstractmethod
    def extract(self, image, prompt: str) -> str:
        """
        Extract text from an image using vision model.

        Args:
            image: PIL Image or image data
            prompt: Prompt for the vision model

        Returns:
            Extracted text as markdown
        """
        ...


class AdjudicatorBackend(ABC):
    """Abstract base class for adjudicator backends."""

    @abstractmethod
    def select(
        self,
        context_before: str,
        candidate_a: str,
        candidate_b: str,
        context_after: str,
    ) -> AdjudicationResult:
        """
        Select one of two candidates for a text segment.

        Args:
            context_before: Previous context (up to 200 chars)
            candidate_a: First candidate
            candidate_b: Second candidate
            context_after: Following context (up to 200 chars)

        Returns:
            AdjudicationResult with selected candidate
        """
        ...

