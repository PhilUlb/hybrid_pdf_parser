# Hybrid PDF Parser

A production-ready Python library for extracting structured Markdown from PDF documents using a dual-extraction approach with optional LLM adjudication.

## Features

- **Dual Extraction**: Combines text-first extraction (Docling) with vision OCR (OpenAI/Ollama)
- **Deterministic Selection**: Uses quality heuristics to choose the best extraction per segment
- **LLM Adjudication**: Optional selection-only LLM for ambiguous cases
- **Provenance Tracking**: Detailed JSONL reports with per-segment diagnostics
- **Production Ready**: Type hints, comprehensive tests, caching, and error handling

## Installation

### Install from GitHub

Install directly from the repository:

```bash
# Basic installation
pip install git+https://github.com/PhilUlb/hybrid_pdf_parser.git@main

# With optional extras
pip install "git+https://github.com/PhilUlb/hybrid_pdf_parser.git@main#egg=hybrid-pdf-parser[notebook]"  # Jupyter support
pip install "git+https://github.com/PhilUlb/hybrid_pdf_parser.git@main#egg=hybrid-pdf-parser[dev]"     # Dev tools
```

Or add to your `requirements.txt`:

```txt
git+https://github.com/PhilUlb/hybrid_pdf_parser.git@main
```

### Local Development

For local development:

```bash
# Clone the repository
git clone https://github.com/PhilUlb/hybrid_pdf_parser.git
cd hybrid_pdf_parser

# Install in editable mode
pip install -e .

# With development dependencies
pip install -e ".[dev,notebook]"
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