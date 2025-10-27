# Quick Start Guide

Get up and running with the Hybrid PDF Parser in minutes.

## Installation

```bash
# Clone or navigate to the project directory
cd hybrid_pdf_parser

# Install the package and dependencies
pip install -e .

# Or with additional tools
pip install -e ".[dev]"      # Development tools
pip install -e ".[notebook]"  # Jupyter notebook support
```

## Setup

### Using OpenAI (Recommended for production)

1. Get your API key from [OpenAI](https://platform.openai.com/api-keys)

2. Create a `.env` file in the project root:

```bash
cp env.example .env
```

3. Edit `.env` and add your API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Using Ollama (For local/open-source)

1. Install and start Ollama: https://ollama.ai

2. Pull a vision model:

```bash
ollama pull qwen2.5-vl
ollama pull llama3.1
```

3. Optionally configure in `.env`:

```bash
OLLAMA_API_BASE=http://localhost:11434
```

## Basic Usage

### Simple API (Recommended)

```python
from hybrid_pdf_parser import PDFExtractor

# Configure with OpenAI
extractor = PDFExtractor()
extractor.config(provider="openai", api_key="sk-...")

# Extract PDF
result = extractor.extract("example.pdf", output_md="output.md")
print(f"Extracted {result.pages} pages")
print(result.markdown)  # View markdown directly!
```

**Or use credentials from environment:**
```bash
# In your .env file
OPENAI_API_KEY=sk-...

# In Python
extractor.config(provider="openai")  # Auto-loads from env
```

### Jupyter Notebook Demo

Open `demo.ipynb` for interactive examples:
```bash
jupyter notebook demo.ipynb
```

### Advanced Options

```python
# Text-only mode (fast, no API calls)
result = extractor.extract("doc.pdf", mode="text_only")

# Vision-only mode (for scanned documents)
result = extractor.extract("scan.pdf", mode="vision_only")

# Disable adjudicator (heuristics only)
result = extractor.extract("doc.pdf", use_adjudicator=False)

# Custom configuration
extractor.config(
    provider="openai",
    vision_model="gpt-4o-mini",
    custom_config={"render": {"dpi": 300}},
)
```

## Output Files

### `output.md`

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
```

### `report.jsonl`

Provenance report in JSON Lines format:

```json
{"page_num": 0, "segment_idx": 0, "source": "T", "t_score": 0.85, "v_score": 0.72, "chosen_text": "...", "timestamp": "2024-01-01T00:00:00"}
{"page_num": 0, "segment_idx": 1, "source": "V", "t_score": 0.60, "v_score": 0.90, "chosen_text": "...", "timestamp": "2024-01-01T00:00:01"}
```

## Configuration

Edit `src/hybrid_pdf_parser/config/default.yaml` to customize:

- **Rendering**: DPI, max resolution
- **Heuristics**: Score margins, ambiguity thresholds  
- **Backends**: Model names, timeouts
- **Caching**: Enable/disable, directories

## Troubleshooting

### OpenAI: "API key not found"

Make sure your `.env` file exists and contains `OPENAI_API_KEY=sk-...`

### Ollama: Connection refused

Ensure Ollama is running:

```bash
ollama serve
```

### Missing dependencies

```bash
pip install -e ".[dev]"
```

## Next Steps

- Read [docs/README.md](docs/README.md) for detailed documentation
- See [docs/DESIGN.md](docs/DESIGN.md) for architecture details
- Check [docs/PROMPTS.md](docs/PROMPTS.md) for prompt templates

## Examples

See `example_usage.py` for a complete working example.

