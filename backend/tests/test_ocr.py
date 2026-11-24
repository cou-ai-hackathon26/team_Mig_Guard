from unittest.mock import patch

import pytest

from app.llm.client import LLMExtractionError
from app.pipeline.orchestrator import analyze_document
from app.api.schemas import ExtractedField, OfferExtraction
from app.utils.errors import AnalyzePipelineError


def _extraction() -> OfferExtraction:
    return OfferExtraction(
        destination=ExtractedField(value="Qatar", confidence=0.9, source_snippet="Qatar"),
        employer=ExtractedField(value="Acme", confidence=0.9, source_snippet="Acme"),
        job_title=ExtractedField(value="driver", confidence=0.9, source_snippet="driver"),
        salary=ExtractedField(value="QAR 1200 per month", confidence=0.9, source_snippet="QAR 1200"),
        fee_asked=ExtractedField(value="BDT 90000", confidence=0.9, source_snippet="BDT 90000"),
        visa_type=ExtractedField(value="work", confidence=0.9, source_snippet="work"),
        duration=ExtractedField(value="2 years", confidence=0.9, source_snippet="2 years"),
        hours=ExtractedField(value="8 hours", confidence=0.9, source_snippet="8 hours"),
        accommodation=ExtractedField(value="provided", confidence=0.9, source_snippet="provided"),
        license_number=ExtractedField(value="RL1857", confidence=0.9, source_snippet="RL1857"),
        agent=ExtractedField(value="1 Plus Overseas Limited", confidence=0.9, source_snippet="1 Plus"),
    )


@patch("app.pipeline.orchestrator.extract_offer_fields")
@patch("app.pipeline.orchestrator.transcribe_images")
def test_ocr_used_when_vision_fails(mock_ocr, mock_extract):
    mock_extract.side_effect = [
        LLMExtractionError("vision down"),
        _extraction(),
    ]
    mock_ocr.return_value = "Job in Qatar salary QAR 1200 overtime food medical"

    result = analyze_document(images=[(b"fake-bytes", "image/jpeg")], text="", language="en")

    assert result.read_method == "ocr_fallback"
    mock_ocr.assert_called_once()
    assert mock_extract.call_count == 2
    assert result.extracted["destination"].value == "Qatar"


@patch("app.pipeline.orchestrator.extract_offer_fields")
def test_timeout_maps_to_pipeline_error(mock_extract):
    mock_extract.side_effect = LLMExtractionError("deadline exceeded", timed_out=True)
    with pytest.raises(AnalyzePipelineError) as caught:
        analyze_document(images=[], text="some offer", language="bn")
    assert caught.value.http_status == 504
    assert caught.value.code == "LLM_TIMEOUT"


@patch("PIL.Image.open")
def test_transcribe_images_tesseract_not_found(mock_open):
    import pytesseract
    from unittest.mock import MagicMock
    from app.pipeline.ocr import transcribe_images
    mock_img = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_img
    with patch("pytesseract.image_to_string", side_effect=pytesseract.TesseractNotFoundError()):
        with pytest.raises(AnalyzePipelineError) as exc_info:
            transcribe_images([(b"fake-bytes", "image/jpeg")])
        assert exc_info.value.code == "OCR_UNAVAILABLE"
        assert exc_info.value.http_status == 503


@patch("PIL.Image.open")
def test_transcribe_images_unreadable_when_all_empty(mock_open):
    from unittest.mock import MagicMock
    from app.pipeline.ocr import transcribe_images
    mock_img = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_img
    with patch("pytesseract.image_to_string", return_value="   "):
        with pytest.raises(AnalyzePipelineError) as exc_info:
            transcribe_images([(b"fake-bytes", "image/jpeg")])
        assert exc_info.value.code == "UNREADABLE_DOCUMENT"
        assert exc_info.value.http_status == 422

