# Design Document

## Architecture Overview

The hybrid PDF extraction pipeline uses a dual-candidate approach with deterministic selection and optional LLM adjudication.

### Core Principles

1. **Deterministic First**: Heuristic-based selection for speed and cost efficiency
2. **Selection Only**: LLM adjudicator never rewrites, only selects between T and V candidates
3. **Provenance Tracking**: Every segment tagged with its source and score
4. **One-Pass Rendering**: Default 250 DPI, 2400px cap for efficiency

## Component Design

### Configuration Layer

Type-safe Pydantic models with YAML support:

- `RenderConfig`: Image rendering parameters
- `HeuristicsConfig`: Selection thresholds
- `BackendConfig`: LLM provider settings
- `ConcurrencyConfig`: Parallel processing limits
- `CacheConfig`: Caching strategy

### Dual Extraction

#### Text-First (T) Candidate

- **Primary**: Docling with `force_ocr=False`
- **Fallback**: PyMuPDF text extraction
- **Processing**: Hyphenation repair, whitespace normalization

#### Vision (V) Candidate

- **Rendering**: PyMuPDF → PNG at 250 DPI
- **Vision Model**: OpenAI GPT-4o or Ollama local models
- **Output**: Clean markdown with structure preservation

### Segmentation

Text is split into semantic units:

- **Sentences**: Basic text units
- **Paragraphs**: Multi-line content
- **Tables**: Markdown table syntax
- **Lists**: Bullet/numbered items
- **Headings**: ATX or Setext headings

Structural detection uses regex patterns and heuristics.

### Alignment

Fuzzy matching between T and V segments:

- Uses `rapidfuzz` for similarity scoring
- Forward windowing for O(n) performance
- Tolerant of small differences

### Heuristics

Quality scoring metrics:

- **Alnum ratio**: Proportion of alphanumeric characters
- **Weird char rate**: Penalty for replacement characters (``)
- **Token length**: Average word length
- **Structural bonus**: Extra points for tables, lists, headings

Selection logic:

1. Check if T and V scores are within ambiguity band
2. If V has structural cues that T lacks → prefer V
3. If score difference > threshold → prefer higher score
4. Default: prefer T (text-first)

### Adjudication

Only triggered for ambiguous segments:

- Score difference < `ambiguity_band` (default 0.05)
- AND length ratio > 1.5x

LLM is selection-only:

- System prompt: "Select exactly one, do not rewrite"
- User context: 200 chars before + candidates + 200 chars after
- Output: JSON with pick ("A" or "B") and verbatim text

### Provenance

Every chosen segment tracked:

- Source: T, V, or LLM
- Scores for both candidates
- LLM pick if adjudicated
- Backend used
- Timestamp

Report format: JSONL for easy analysis and debugging.

## Rendering Strategy

One-pass defaults for efficiency:

- DPI: 250 (good quality, reasonable size)
- Max long edge: 2400px (controls memory)
- Format: PNG, RGB, no alpha
- Downscaling: LANCZOS (high quality)
- Target size: ~1-1.5 MB per page

Optional tiling for very large pages (disabled by default).

## Caching

- **Page images**: Hash-based cache (`.cache/images/{sha}.png`)
- **Vision outputs**: Optional cache per page SHA (`.cache/vision/`)

Avoids re-processing and re-billing on pipeline re-runs.

## Error Handling

- Retries with exponential backoff (configurable)
- Fallback to deterministic choice on adjudicator failure
- Graceful degradation if Docling unavailable
- Clear error messages with context

## Extensibility

Adapter pattern for backends:

- `VisionBackend` abstract class
- `AdjudicatorBackend` abstract class
- Easy to add new providers (Azure, Anthropic, etc.)

## Performance

- Concurrent page processing (configurable workers)
- Batched adjudication
- Efficient alignment algorithm (O(n) with windowing)
- Minimal API calls (only for ambiguous segments)

## Determinism

- Temperature 0 for LLM calls
- Pure deterministic pipeline when adjudicator disabled
- Reproducible results for same inputs

## Future Enhancements

- Tiling support for very large pages
- Additional heuristics (language detection, confidence scores)
- Support for other vision backends (OCRmyPDF, Tesseract)
- Streaming for large documents
- GPU acceleration for vision models

