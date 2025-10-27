"""Tests for simple high-level API."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from hybrid_pdf_parser import PDFExtractor


def test_pdf_extractor_config():
    """Test PDFExtractor configuration."""
    extractor = PDFExtractor()
    
    # Test config without credentials (should error)
    with pytest.raises((ValueError, FileNotFoundError)):
        extractor.config(provider="openai")


def test_pdf_extractor_with_mock_credentials(monkeypatch):
    """Test PDFExtractor with mocked credentials."""
    # Mock environment variable
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    
    extractor = PDFExtractor()
    
    # Should not raise with env var set
    with patch('hybrid_pdf_parser.simple.OpenAIVisionBackend') as mock_vision, \
         patch('hybrid_pdf_parser.simple.OpenAIAdjudicatorBackend') as mock_adjudicator, \
         patch('hybrid_pdf_parser.simple.PipelineConfig') as mock_config:
        
        mock_config.from_yaml.return_value = Mock()
        
        extractor.config(provider="openai")
        assert extractor._configured is True
        assert extractor._provider == "openai"


def test_pdf_extractor_config_with_custom_config():
    """Test PDFExtractor with custom config dict."""
    extractor = PDFExtractor()
    
    custom_config = {
        "render": {"dpi": 300},
        "heuristics": {"score_margin": 0.2}
    }
    
    with patch('hybrid_pdf_parser.simple.OpenAIVisionBackend') as mock_vision, \
         patch('hybrid_pdf_parser.simple.OpenAIAdjudicatorBackend') as mock_adjudicator, \
         patch('hybrid_pdf_parser.simple.PipelineConfig') as mock_config, \
         patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        
        mock_config.from_yaml.return_value = Mock()
        
        extractor.config(
            provider="openai",
            custom_config=custom_config
        )
        
        assert extractor._configured is True


def test_extractor_method_chaining():
    """Test that config() returns self for chaining."""
    extractor = PDFExtractor()
    
    with patch('hybrid_pdf_parser.simple.OpenAIVisionBackend') as mock_vision, \
         patch('hybrid_pdf_parser.simple.OpenAIAdjudicatorBackend') as mock_adjudicator, \
         patch('hybrid_pdf_parser.simple.PipelineConfig') as mock_config, \
         patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        
        mock_config.from_yaml.return_value = Mock()
        
        result = extractor.config(provider="openai")
        assert result is extractor


def test_extractor_not_configured():
    """Test that extract() fails if not configured."""
    extractor = PDFExtractor()
    
    with pytest.raises(RuntimeError, match="Must call config"):
        extractor.extract("nonexistent.pdf")


def test_simple_api_usage():
    """Test basic usage of simple API."""
    with patch('hybrid_pdf_parser.simple.OpenAIVisionBackend') as mock_vision, \
         patch('hybrid_pdf_parser.simple.OpenAIAdjudicatorBackend') as mock_adjudicator, \
         patch('hybrid_pdf_parser.simple.PipelineConfig') as mock_config, \
         patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test'}):
        
        mock_config.from_yaml.return_value = Mock()
        
        # Basic usage
        extractor = PDFExtractor()
        extractor.config(provider="openai")
        
        # Should be configured
        assert extractor._configured is True
        assert extractor._provider == "openai"

