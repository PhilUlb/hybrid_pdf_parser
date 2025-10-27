"""
Example usage of the Hybrid PDF Parser.

This script demonstrates how to use the PDF extraction pipeline
with OpenAI backends.

Prerequisites:
- OPENAI_API_KEY environment variable set
- Input PDF file at 'example.pdf'
"""

from pathlib import Path

from hybrid_pdf_parser import (
    OpenAIVisionBackend,
    PdfEnsemblePipeline,
    PipelineConfig,
)
from hybrid_pdf_parser.vendors.openai_backend import OpenAIAdjudicatorBackend


def main():
    """Example usage of the PDF extraction pipeline."""
    # Load configuration
    config = PipelineConfig.from_yaml("src/hybrid_pdf_parser/config/default.yaml")

    # Setup OpenAI backends
    # Requires OPENAI_API_KEY environment variable
    vision = OpenAIVisionBackend(model="gpt-4o")
    adjudicator = OpenAIAdjudicatorBackend(model="gpt-4o")

    # Create pipeline
    pipeline = PdfEnsemblePipeline(config, vision, adjudicator)

    # Input/output paths
    pdf_path = Path("example.pdf")  # Update this to your PDF
    output_md = Path("output.md")
    report_jsonl = Path("report.jsonl")

    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        print("Please update 'example.pdf' to point to your input PDF")
        return

    # Extract text
    print(f"Processing PDF: {pdf_path}")
    result = pipeline.extract(pdf_path, output_md, report_jsonl)

    print(f"✓ Processed {result.pages_processed} pages")
    print(f"✓ Generated {len(result.records)} segment records")
    print(f"✓ Output written to: {output_md}")
    print(f"✓ Provenance report: {report_jsonl}")


if __name__ == "__main__":
    main()

