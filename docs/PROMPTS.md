# LLM Prompts

This document describes the exact prompts used for vision OCR and adjudication.

## Vision OCR Prompt

Used by both OpenAI and Ollama vision backends.

### System/Base Prompt

```
Convert this single page image to clean GitHub-flavored Markdown. 
Preserve headings (#…), lists, tables (Markdown pipes), inline formatting. 
Return Markdown only.
```

### Rationale

- **Single page focus**: Prevents context bleed between pages
- **GitHub-flavored Markdown**: Ensures compatibility
- **Structure preservation**: Emphasizes tables, lists, headings
- **Markdown only**: Prevents extra commentary or explanations

### Temperature

`0` - Deterministic output

## Adjudicator Prompt

Used for LLM-based selection between T and V candidates.

### System Prompt

```
You are an extraction adjudicator. Given two alternatives (A and B) 
for the same snippet, select exactly one. Do not rewrite. 
Return the chosen text verbatim.
```

### User Prompt Template

```
Context before:
{context_before}

Option A:
{candidate_a}

Option B:
{candidate_b}

Context after:
{context_after}

Select A or B and return the chosen text verbatim. 
Do not rewrite or merge. 
Return JSON format: {"pick": "A" or "B", "text": "<verbatim chosen text>"}
```

### Rationale

- **Selection only**: Explicitly forbids rewriting or merging
- **Context windows**: 200 chars before/after for disambiguation
- **JSON output**: Structured response for parsing
- **Verbatim requirement**: Prevents hallucination

### Temperature

`0` - Deterministic selection

### Output Format

Expected JSON response:

```json
{
  "pick": "A",
  "text": "exact verbatim text from chosen candidate"
}
```

Validation: Returned text must match one of the candidates exactly (whitespace-tolerant comparison).

## Implementation Notes

### OpenAI Backend

- Uses `response_format={"type": "json_object"}` for structured output
- System message + user message for context
- Base64 image encoding for vision

### Ollama Backend

- Plain JSON parsing from text response
- Image passed as base64 in request payload
- Requires local model with vision capabilities (qwen2.5-vl, llava, etc.)

### Retry Logic

Both backends use exponential backoff on failures:

- Max retries: 3 (configurable)
- Backoff multiplier: 2
- Jitter: Random between 0 and 1 second

