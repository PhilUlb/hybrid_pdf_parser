"""Pydantic configuration models for the PDF extraction pipeline."""

from typing import Literal, Optional
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class RenderConfig(BaseModel):
    """Configuration for PDF to image rendering."""

    dpi: int = Field(default=250, description="Rendering DPI")
    max_long_edge: int = Field(default=2400, description="Maximum long edge in pixels")
    format: str = Field(default="png", description="Output format")
    alpha: bool = Field(default=False, description="Include alpha channel")


class HeuristicsConfig(BaseModel):
    """Configuration for deterministic selection heuristics."""

    score_margin: float = Field(default=0.15, description="Minimum score difference to prefer higher candidate")
    ambiguity_band: float = Field(default=0.05, description="Score difference threshold for ambiguity")


class BackendConfig(BaseModel):
    """Configuration for LLM backends."""

    provider: Literal["openai", "ollama"] = Field(default="openai", description="Backend provider")
    vision_model: str = Field(default="gpt-4o", description="Vision model name")
    adjudicator_model: str = Field(default="gpt-4o", description="Adjudicator model name")
    api_base: Optional[str] = Field(default=None, description="API base URL (for Ollama)")
    timeout: int = Field(default=60, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class ConcurrencyConfig(BaseModel):
    """Configuration for parallel processing."""

    max_workers: int = Field(default=4, description="Maximum parallel workers")
    batch_size: int = Field(default=10, description="Batch size for adjudication")


class CacheConfig(BaseModel):
    """Configuration for caching."""

    enabled: bool = Field(default=True, description="Enable caching")
    image_cache_dir: Path = Field(default=Path(".cache/images"), description="Image cache directory")
    vision_cache_dir: Path = Field(default=Path(".cache/vision"), description="Vision output cache directory")

    @field_validator("image_cache_dir", "vision_cache_dir", mode="before")
    @classmethod
    def ensure_path(cls, v):
        """Convert string to Path."""
        return Path(v) if isinstance(v, str) else v


class PipelineConfig(BaseModel):
    """Root configuration for the PDF extraction pipeline."""

    render: RenderConfig = Field(default_factory=RenderConfig)
    heuristics: HeuristicsConfig = Field(default_factory=HeuristicsConfig)
    backend: BackendConfig = Field(default_factory=BackendConfig)
    concurrency: ConcurrencyConfig = Field(default_factory=ConcurrencyConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)

    @classmethod
    def from_yaml(cls, path: Path | str) -> "PipelineConfig":
        """Load configuration from YAML file."""
        import yaml

        path = Path(path) if isinstance(path, str) else path
        with path.open() as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    def to_yaml(self, path: Path | str) -> None:
        """Save configuration to YAML file."""
        import yaml

        path = Path(path) if isinstance(path, str) else path
        with path.open("w") as f:
            yaml.dump(self.model_dump(mode="json"), f, default_flow_style=False)

