"""Integration tests for the PDF extraction pipeline."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from hybrid_pdf_parser import PdfEnsemblePipeline, PipelineConfig
from hybrid_pdf_parser.vendors.openai_backend import OpenAIAdjudicatorBackend, OpenAIVisionBackend


class MockVisionBackend:
    """Mock vision backend for testing."""

    def extract(self, image, prompt: str) -> str:
        """Return mock markdown."""
        return "# Mock Heading\n\nMock paragraph text."


class MockAdjudicatorBackend:
    """Mock adjudicator backend for testing."""

    def select(self, context_before, candidate_a, candidate_b, context_after):
        """Return mock selection."""
        from hybrid_pdf_parser.vendors.base import AdjudicationResult

        return AdjudicationResult(pick="A", text=candidate_a)


@pytest.fixture
def config():
    """Create test configuration."""
    return PipelineConfig()


@pytest.fixture
def vision_backend():
    """Create mock vision backend."""
    return MockVisionBackend()


@pytest.fixture
def adjudicator_backend():
    """Create mock adjudicator backend."""
    return MockAdjudicatorBackend()


@pytest.fixture
def pipeline(config, vision_backend, adjudicator_backend):
    """Create pipeline with mock backends."""
    return PdfEnsemblePipeline(config, vision_backend, adjudicator_backend)


def test_pipeline_initialization(pipeline, config):
    """Test that pipeline initializes correctly."""
    assert pipeline.config == config
    assert pipeline.vision_backend is not None
    assert pipeline.adjudicator_backend is not None


@pytest.mark.skip(reason="Requires actual PDF file and API keys")
def test_pipeline_extract_real(pipeline):
    """Test extraction with real PDF (requires setup)."""
    pdf_path = Path("tests/fixtures/sample.pdf")
    if not pdf_path.exists():
        pytest.skip("Sample PDF not available")

    output_md = Path("test_output.md")
    report_jsonl = Path("test_report.jsonl")

    try:
        result = pipeline.extract(pdf_path, output_md, report_jsonl)
        assert result.pages_processed > 0
        assert len(result.records) > 0
        assert output_md.exists()
        assert report_jsonl.exists()
    finally:
        # Cleanup
        if output_md.exists():
            output_md.unlink()
        if report_jsonl.exists():
            report_jsonl.unlink()

