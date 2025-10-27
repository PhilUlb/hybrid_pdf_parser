# Hybrid PDF Parser

A production-ready Python library for extracting structured Markdown from PDF documents using a dual-extraction approach with optional LLM adjudication.

## Features

- **Dual Extraction**: Combines text-first extraction (Docling) with vision OCR (OpenAI/Ollama)
- **Deterministic Selection**: Uses quality heuristics to choose the best extraction per segment
- **LLM Adjudication**: Optional selection-only LLM for ambiguous cases
- **Provenance Tracking**: Detailed JSONL reports with per-segment diagnostics
- **Production Ready**: Type hints, comprehensive tests, caching, and error handling

## Installation

Install from the project directory:

```bash
pip install -e .
```

Or install with development dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Simple API (Recommended)

```python
from hybrid_pdf_parser import PDFExtractor

# Configure once
extractor = PDFExtractor()
extractor.config(provider="openai", api_key="sk-...")  # Or use env var

# Extract PDF
result = extractor.extract("input.pdf", output_md="output.md")

print(f"Extracted {result.pages} pages")
print(result.markdown)  # View markdown directly
print(result.stats)     # {"T": 10, "V": 5, "LLM": 2}
```

See [demo.ipynb](demo.ipynb) for interactive examples with Jupyter!

### Advanced API (Low-level Control)

For more control, use the low-level API:

```python
from pathlib import Path
from hybrid_pdf_parser import PdfEnsemblePipeline, PipelineConfig
from hybrid_pdf_parser.vendors.openai_backend import (
    OpenAIVisionBackend,
    OpenAIAdjudicatorBackend,
)

# Setup
config = PipelineConfig.from_yaml("src/hybrid_pdf_parser/config/default.yaml")
vision = OpenAIVisionBackend(model="gpt-4o")
adjudicator = OpenAIAdjudicatorBackend(model="gpt-4o")

pipeline = PdfEnsemblePipeline(config, vision, adjudicator)
result = pipeline.extract(Path("input.pdf"), Path("output.md"), Path("report.jsonl"))
```

See the [docs/](docs/) directory for detailed documentation.