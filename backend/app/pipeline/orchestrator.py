"""Run ingest → read (vision, OCR fallback) → extract → verify → score → explain."""

from __future__ import annotations

import logging
from typing import Sequence

from app.api.schemas import AnalyzeResponse
from app.config import settings
from app.data.loader import helplines
from app.llm.client import LLMExtractionError, LLMUsageLimitError
from app.pipeline.explain import explain_flags
from app.pipeline.extract import extract_offer_fields
from app.pipeline.ocr import transcribe_images
from app.pipeline.scoring import audio_script_bn, score_flags
from app.pipeline.verify import verify_offer
from app.utils.errors import TIMEOUT, VISION_FAILED, AnalyzePipelineError

logger = logging.getLogger(__name__)


def _map_llm_error(exc: LLMExtractionError) -> AnalyzePipelineError:
    if isinstance(exc, LLMUsageLimitError):
        return AnalyzePipelineError(
            code="AI_USAGE_LIMIT",
            message_en="The AI usage limit has been reached. Please try again tomorrow.",
            message_bn="এআই ব্যবহারের দৈনিক সীমা শেষ হয়েছে। আগামীকাল আবার চেষ্টা করুন।",
            http_status=429,
        )
    if exc.timed_out:
        return AnalyzePipelineError(
            code=TIMEOUT.code,
            message_en=TIMEOUT.message_en,
            message_bn=TIMEOUT.message_bn,
            http_status=TIMEOUT.http_status,
        )
    return AnalyzePipelineError(
        code=VISION_FAILED.code,
        message_en=VISION_FAILED.message_en,
        message_bn=VISION_FAILED.message_bn,
        http_status=VISION_FAILED.http_status,
    )


def analyze_document(
    images: Sequence[tuple[bytes, str]],
    text: str = "",
    language: str = "bn",
) -> AnalyzeResponse:
    cleaned_text = (text or "").strip()
    document_text = cleaned_text
    read_method = "pasted_text" if cleaned_text and not images else "vision"
    unverifiable: list[str] = []

    if images:
        try:
            extraction = extract_offer_fields(images=images, text=cleaned_text)
            read_method = "vision"
        except LLMExtractionError as vision_error:
            logger.warning("Vision extraction failed; trying OCR. %s", vision_error)
            ocr_text = transcribe_images(images)
            document_text = "\n".join(part for part in (cleaned_text, ocr_text) if part)
            try:
                extraction = extract_offer_fields(images=[], text=document_text)
                read_method = "ocr_fallback"
                unverifiable.append(
                    "read_method: vision failed; text was recovered with OCR fallback."
                )
            except LLMExtractionError as ocr_extract_error:
                raise _map_llm_error(ocr_extract_error) from ocr_extract_error
    else:
        try:
            extraction = extract_offer_fields(images=[], text=cleaned_text)
        except LLMExtractionError as exc:
            raise _map_llm_error(exc) from exc

    verification = verify_offer(extraction, document_text=document_text)
    flags = explain_flags(verification.flags, use_llm=settings.explain_with_llm)
    verdict, score = score_flags(flags)

    summary_parts = []
    if images:
        summary_parts.append(f"{len(images)} image(s) analyzed")
    if cleaned_text:
        summary_parts.append(f"{len(cleaned_text)} characters of text analyzed")
    summary_parts.append(f"read via {read_method}")

    questions = []
    seen = set()
    for item in verification.questions_to_ask:
        key = (item.get("en"), item.get("bn"))
        if key in seen:
            continue
        seen.add(key)
        questions.append(item)

    return AnalyzeResponse(
        verdict=verdict,
        score=score,
        language=language,
        input_summary="; ".join(summary_parts),
        extracted=extraction.model_dump(),
        flags=flags,
        missing_clauses=verification.missing_clauses,
        questions_to_ask=questions,
        unverifiable=unverifiable + verification.unverifiable,
        helplines=helplines(),
        audio_script_bn=audio_script_bn(verdict, flags, verification.missing_clauses),
        read_method=read_method,
    )
