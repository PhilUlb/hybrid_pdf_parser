"""Main pipeline orchestration for PDF extraction."""

from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import fitz

from hybrid_pdf_parser.config.schema import PipelineConfig
from hybrid_pdf_parser.vendors.base import AdjudicatorBackend, VisionBackend

if TYPE_CHECKING:
    from hybrid_pdf_parser.core.segmentation import Segment

# Import core modules locally to avoid circular imports
from hybrid_pdf_parser.core import (
    adjudicator,
    alignment,
    extract_text,
    extract_vision,
    heuristics,
    provenance,
    render,
)
from hybrid_pdf_parser.core.segmentation import Segment


class ExtractionResult:
    """Result of PDF extraction pipeline."""

    def __init__(
        self,
        markdown: str,
        records: List[provenance.ProvenanceRecord],
        pages_processed: int,
    ):
        self.markdown = markdown
        self.records = records
        self.pages_processed = pages_processed


class PdfEnsemblePipeline:
    """Main pipeline for hybrid PDF extraction."""

    def __init__(
        self,
        config: PipelineConfig,
        vision_backend: VisionBackend,
        adjudicator_backend: Optional[AdjudicatorBackend] = None,
    ):
        """
        Initialize PDF extraction pipeline.

        Args:
            config: Pipeline configuration
            vision_backend: Vision OCR backend
            adjudicator_backend: Optional LLM adjudicator backend
        """
        self.config = config
        self.vision_backend = vision_backend
        self.adjudicator_backend = adjudicator_backend

    def extract(
        self,
        pdf_path: Path,
        output_md: Path,
        report_jsonl: Path,
    ) -> ExtractionResult:
        """
        Extract text from PDF using hybrid approach.

        Args:
            pdf_path: Input PDF file
            output_md: Output markdown file
            report_jsonl: Output provenance report

        Returns:
            ExtractionResult with markdown and records
        """
        # Load PDF
        doc = fitz.open(str(pdf_path))
        num_pages = len(doc)

        all_segments = []
        all_records = []

        # Process each page
        for page_num in range(num_pages):
            # Render page to image
            page_hash = render.compute_page_hash(doc, page_num)
            image = render.render_page_to_image(doc, page_num, self.config.render)

            # Cache image if enabled
            if self.config.cache.enabled:
                cache_dir = self.config.cache.image_cache_dir
                render.save_image_to_cache(image, page_hash, cache_dir)

            # Extract T candidate (Docling)
            t_text = extract_text.extract_text_candidate(pdf_path, page_num)

            # Extract V candidate (Vision OCR)
            v_text = extract_vision.extract_vision_candidate(image, self.vision_backend)

            # Import segmentation here to avoid circular import
            from hybrid_pdf_parser.core import segmentation

            t_segments = segmentation.segment_text(t_text)
            v_segments = segmentation.segment_text(v_text)

            # Align T↔V
            aligned_pairs = alignment.align_segments(t_segments, v_segments)

            # Score and select
            page_segments = []
            page_records = []
            ambiguous_pairs = []

            for seg_idx, pair in enumerate(aligned_pairs):
                if pair.is_empty():
                    continue

                # Score segments
                t_score = heuristics.score_segment(pair.t_seg) if pair.t_seg else 0.0
                v_score = heuristics.score_segment(pair.v_seg) if pair.v_seg else 0.0

                # Choose segment
                choice = heuristics.choose_segment(pair.t_seg, pair.v_seg, t_score, v_score, self.config.heuristics)

                if choice.source == "AMBIGUOUS":
                    # Flag for adjudication
                    if pair.t_seg and pair.v_seg:
                        context_before, context_after = adjudicator.build_context(
                            t_segments if pair.t_seg else v_segments,
                            seg_idx if pair.t_seg else seg_idx,
                        )
                        ambiguous_pairs.append(
                            adjudicator.AmbiguousPair(
                                t_seg=pair.t_seg,
                                v_seg=pair.v_seg,
                                context_before=context_before,
                                context_after=context_after,
                                page_num=page_num,
                                segment_idx=seg_idx,
                            )
                        )
                    # Temporarily choose T as fallback
                    selected_text = pair.t_seg.text if pair.t_seg else pair.v_seg.text
                    choice = heuristics.Choice(source="T", selected_text=selected_text, reason="Pending adjudication")
                else:
                    # Deterministic choice
                    page_segments.append(choice.selected_text)
                    page_records.append(
                        provenance.ProvenanceRecord(
                            page_num=page_num,
                            segment_idx=seg_idx,
                            source=choice.source,
                            t_score=t_score,
                            v_score=v_score,
                            chosen_text=choice.selected_text,
                            backend_used=None,
                        )
                    )

            # Adjudicate ambiguous segments if backend available
            if ambiguous_pairs and self.adjudicator_backend:
                adjudication_results = adjudicator.adjudicate_batch(ambiguous_pairs, self.adjudicator_backend)

                for i, result in enumerate(adjudication_results):
                    pair = ambiguous_pairs[i]
                    # Insert adjudicated segments into page segments
                    llm_pick = result.pick
                    selected_text = pair.t_seg.text if llm_pick == "A" else pair.v_seg.text

                    page_segments.append(selected_text)
                    page_records.append(
                        provenance.ProvenanceRecord(
                            page_num=pair.page_num,
                            segment_idx=pair.segment_idx,
                            source="LLM",
                            llm_pick=llm_pick,
                            t_score=heuristics.score_segment(pair.t_seg) if pair.t_seg else 0.0,
                            v_score=heuristics.score_segment(pair.v_seg) if pair.v_seg else 0.0,
                            chosen_text=selected_text,
                            backend_used=type(self.adjudicator_backend).__name__,
                        )
                    )

            all_segments.extend(page_segments)
            all_records.extend(page_records)

        # Assemble final markdown
        markdown = "\n\n".join(all_segments)
        markdown_with_provenance = provenance.insert_provenance_comments(markdown, all_records)

        # Write outputs
        output_md.parent.mkdir(parents=True, exist_ok=True)
        with output_md.open("w") as f:
            f.write(markdown_with_provenance)

        provenance.write_jsonl_report(all_records, report_jsonl)

        return ExtractionResult(
            markdown=markdown_with_provenance,
            records=all_records,
            pages_processed=num_pages,
        )

