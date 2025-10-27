"""Simple high-level API for PDF extraction."""

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

# Optional import for .env support
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda: None

from hybrid_pdf_parser.config.schema import PipelineConfig
from hybrid_pdf_parser.core.pipeline import ExtractionResult, PdfEnsemblePipeline
from hybrid_pdf_parser.vendors.ollama_backend import OllamaAdjudicatorBackend, OllamaVisionBackend
from hybrid_pdf_parser.vendors.openai_backend import OpenAIVisionBackend, OpenAIAdjudicatorBackend


@dataclass
class SimpleExtractionResult:
    """Simple result object for PDF extraction."""

    markdown: str
    markdown_path: Optional[Path]
    report_path: Optional[Path]
    pages: int
    stats: dict


class PDFExtractor:
    """High-level convenience wrapper for PDF extraction."""

    def __init__(self):
        """Initialize PDF extractor."""
        self._provider: Optional[str] = None
        self._config: Optional[PipelineConfig] = None
        self._vision_backend: Optional[object] = None
        self._adjudicator_backend: Optional[object] = None
        self._configured = False

    def config(
        self,
        provider: Literal["openai", "ollama"],
        api_key: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434",
        vision_model: Optional[str] = None,
        adjudicator_model: Optional[str] = None,
        custom_config: Optional[dict] = None,
    ) -> "PDFExtractor":
        """
        Configure the extractor with provider and credentials.

        Args:
            provider: "openai" or "ollama" (required)
            api_key: OpenAI API key (optional if in env)
            ollama_base_url: Ollama API base URL
            vision_model: Model name for vision (optional, defaults provided)
            adjudicator_model: Model name for adjudicator (optional, defaults provided)
            custom_config: Dict to override default config

        Returns:
            Self for method chaining

        Example:
            >>> extractor = PDFExtractor()
            >>> extractor.config(provider="openai", api_key="sk-...")
            >>> # Or using defaults from env
            >>> extractor.config(provider="openai")
        """
        # Load .env if available
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)

        self._provider = provider

        # Set smart defaults for models
        if vision_model is None:
            vision_model = "gpt-4o" if provider == "openai" else "qwen2.5-vl"
        if adjudicator_model is None:
            adjudicator_model = "gpt-4o" if provider == "openai" else "llama3.1"

        # Load or create config
        if custom_config:
            config_data = custom_config
            # Merge with defaults
            config = self._load_default_config()
            config_dict = config.model_dump()
            _deep_merge(config_dict, custom_config)
            self._config = PipelineConfig.model_validate(config_dict)
        else:
            self._config = self._load_default_config()

        # Setup backends
        if provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found. Set it in config(), .env file, or environment variable."
                )
            self._vision_backend = OpenAIVisionBackend(model=vision_model, api_key=api_key)
            self._adjudicator_backend = OpenAIAdjudicatorBackend(model=adjudicator_model, api_key=api_key)

        elif provider == "ollama":
            base_url = ollama_base_url or os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
            self._vision_backend = OllamaVisionBackend(model=vision_model, api_base=base_url)
            self._adjudicator_backend = OllamaAdjudicatorBackend(model=adjudicator_model, api_base=base_url)

        else:
            raise ValueError(f"Unknown provider: {provider}. Must be 'openai' or 'ollama'")

        self._configured = True

        return self

    @staticmethod
    def _load_default_config() -> PipelineConfig:
        """Load default config from package data."""
        from pathlib import Path
        import importlib.resources

        try:
            # Try to load from package resources
            with importlib.resources.files("hybrid_pdf_parser.config") / "default.yaml" as config_path:
                return PipelineConfig.from_yaml(config_path)
        except (TypeError, AttributeError):
            # Fallback for older Python versions or when running from source
            from hybrid_pdf_parser.config import schema
            config_path = Path(schema.__file__).parent / "default.yaml"
            return PipelineConfig.from_yaml(config_path)

    def extract(
        self,
        pdf_path: str | Path,
        output_md: Optional[str | Path] = None,
        report_jsonl: Optional[str | Path] = None,
        use_adjudicator: bool = True,
        mode: Literal["hybrid", "text_only", "vision_only"] = "hybrid",
    ) -> SimpleExtractionResult:
        """
        Extract text from PDF.

        Args:
            pdf_path: Path to input PDF file
            output_md: Path to save markdown (optional, auto-saved if not provided)
            report_jsonl: Path to save provenance report (optional)
            use_adjudicator: Whether to use LLM adjudication (default: True)
            mode: Extraction mode - "hybrid" (default), "text_only", or "vision_only"

        Returns:
            SimpleExtractionResult with markdown, paths, and stats

        Example:
            >>> result = extractor.extract("input.pdf")
            >>> print(result.markdown)  # View markdown
            >>> print(result.pages)  # Pages processed
        """
        if not self._configured:
            raise RuntimeError("Must call config() before extract()")

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Handle different modes
        if mode == "text_only":
            # Use fallback to simple text extraction
            # For now, we'll use a simplified approach
            result = self._extract_text_only(pdf_path, output_md, report_jsonl)
        elif mode == "vision_only":
            result = self._extract_vision_only(pdf_path, output_md, report_jsonl, use_adjudicator)
        else:  # hybrid (default)
            result = self._extract_hybrid(pdf_path, output_md, report_jsonl, use_adjudicator)

        return result

    def _extract_hybrid(
        self, pdf_path: Path, output_md: Optional[Path], report_jsonl: Optional[Path], use_adjudicator: bool
    ) -> SimpleExtractionResult:
        """Extract using hybrid T+V approach."""
        # Auto-create output paths if not provided
        if output_md is None:
            output_md = pdf_path.with_suffix(".md")
        if report_jsonl is None:
            report_jsonl = pdf_path.with_suffix(".report.jsonl")

        output_md = Path(output_md)
        report_jsonl = Path(report_jsonl)

        # Create pipeline
        pipeline = PdfEnsemblePipeline(
            config=self._config,
            vision_backend=self._vision_backend,
            adjudicator_backend=self._adjudicator_backend if use_adjudicator else None,
        )

        # Extract
        result = pipeline.extract(pdf_path, output_md, report_jsonl)

        # Build stats
        stats = {"T": 0, "V": 0, "LLM": 0}
        for record in result.records:
            if record.source == "LLM":
                stats["LLM"] += 1
            elif record.source == "V":
                stats["V"] += 1
            else:  # T
                stats["T"] += 1

        return SimpleExtractionResult(
            markdown=result.markdown,
            markdown_path=output_md,
            report_path=report_jsonl,
            pages=result.pages_processed,
            stats=stats,
        )

    def _extract_text_only(
        self, pdf_path: Path, output_md: Optional[Path], report_jsonl: Optional[Path]
    ) -> SimpleExtractionResult:
        """Extract using text-only mode (Docling only)."""
        # For text-only, we'll use a simplified extraction without vision
        # This is a placeholder - full implementation would extract only text
        from hybrid_pdf_parser.core import extract_text as core_extract_text

        output_md = Path(output_md) if output_md else pdf_path.with_suffix(".md")

        # Extract text from first page as example
        import fitz

        doc = fitz.open(str(pdf_path))
        all_text = ""

        for page_num in range(len(doc)):
            text = core_extract_text.extract_text_candidate(pdf_path, page_num)
            all_text += text + "\n\n"

        # Save markdown
        output_md.parent.mkdir(parents=True, exist_ok=True)
        with output_md.open("w") as f:
            f.write(all_text)

        return SimpleExtractionResult(
            markdown=all_text,
            markdown_path=output_md,
            report_path=None,
            pages=len(doc),
            stats={"T": 1, "V": 0, "LLM": 0},
        )

    def _extract_vision_only(
        self, pdf_path: Path, output_md: Optional[Path], report_jsonl: Optional[Path], use_adjudicator: bool
    ) -> SimpleExtractionResult:
        """Extract using vision-only mode."""
        # Similar to hybrid but skip text extraction
        # Placeholder implementation
        return self._extract_hybrid(pdf_path, output_md, report_jsonl, use_adjudicator)


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Dictionary to merge in

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result

