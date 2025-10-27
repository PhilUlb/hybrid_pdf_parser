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

```python
from pathlib import Path
from hybrid_pdf_parser import (
    PdfEnsemblePipeline,
    PipelineConfig,
    OpenAIVisionBackend,
    OpenAIAdjudicatorBackend,
)

# Load configuration
config = PipelineConfig.from_yaml("config/default.yaml")

# Setup backends
vision = OpenAIVisionBackend(model="gpt-4o")
adjudicator = OpenAIAdjudicatorBackend(model="gpt-4o")

# Create pipeline
pipeline = PdfEnsemblePipeline(config, vision, adjudicator)

# Extract text
result = pipeline.extract(
    pdf_path=Path("input.pdf"),
    output_md=Path("output.md"),
    report_jsonl=Path("report.jsonl")
)

print(f"Processed {result.pages_processed} pages")
```

## Configuration

Edit `config/default.yaml` to customize:

- **Rendering**: DPI, max resolution, output format
- **Heuristics**: Score margins, ambiguity thresholds
- **Backend**: Provider (OpenAI/Ollama), model names, timeouts
- **Caching**: Enable/disable, cache directories

## Backends

### OpenAI Backend

Requires `OPENAI_API_KEY` environment variable:

```python
from hybrid_pdf_parser.vendors.openai_backend import OpenAIVisionBackend, OpenAIAdjudicatorBackend

vision = OpenAIVisionBackend(model="gpt-4o")
adjudicator = OpenAIAdjudicatorBackend(model="gpt-4o")
```

### Ollama Backend

Requires Ollama running locally on `http://localhost:11434`:

```python
from hybrid_pdf_parser.vendors.ollama_backend import OllamaVisionBackend, OllamaAdjudicatorBackend

vision = OllamaVisionBackend(model="qwen2.5-vl")
adjudicator = OllamaAdjudicatorBackend(model="llama3.1")
```

## Outputs

### Markdown Output (`output.md`)

Clean Markdown with provenance comments:

```markdown
# Title

<!-- src:T -->
This paragraph came from text extraction.

<!-- src:V -->
This table came from vision OCR:

| col1 | col2 |
|------|------|
| val1 | val2 |

<!-- src:LLM:A -->
This ambiguous segment was adjudicated by LLM.
```

### Provenance Report (`report.jsonl`)

JSON Lines format with per-segment diagnostics:

```json
{"page_num": 0, "segment_idx": 0, "source": "T", "t_score": 0.85, "v_score": 0.72, "chosen_text": "...", "timestamp": "2024-01-01T00:00:00"}
{"page_num": 0, "segment_idx": 1, "source": "V", "t_score": 0.60, "v_score": 0.90, "chosen_text": "...", "timestamp": "2024-01-01T00:00:01"}
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

With coverage:

```bash
pytest --cov=hybrid_pdf_parser --cov-report=html tests/
```

## Documentation

- [DESIGN.md](DESIGN.md) - Architecture and rationale
- [PROMPTS.md](PROMPTS.md) - LLM prompt design

## License

See LICENSE file.

