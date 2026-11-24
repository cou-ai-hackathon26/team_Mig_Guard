# Integration tests for POST /api/analyze and GET /api/health.

import io
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.api.schemas import AnalyzeResponse, ExtractedField, OfferExtraction
from app.utils.errors import AnalyzePipelineError, VISION_FAILED


client = TestClient(app)


def _empty_extraction() -> OfferExtraction:
    return OfferExtraction()


def _response_with_destination(value="Malaysia") -> AnalyzeResponse:
    extraction = OfferExtraction(
        destination=ExtractedField(
            value=value,
            confidence=0.9,
            source_snippet=f"Destination: {value}",
        )
    )
    return AnalyzeResponse(
        verdict="caution",
        score=40,
        language="en",
        input_summary="text analyzed; read via pasted_text",
        extracted=extraction.model_dump(),
        flags=[],
        unverifiable=[],
        read_method="pasted_text",
    )


def test_health_returns_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "env" in body


def test_service_root_returns_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Mig_Guard"


def test_service_root_head_returns_ok():
    response = client.head("/")
    assert response.status_code == 200


def test_analyze_no_input_returns_400():
    response = client.post("/api/analyze")
    assert response.status_code == 400
    assert "image" in response.json()["detail"].lower() or "text" in response.json()["detail"].lower()


def test_analyze_invalid_language_returns_400():
    response = client.post(
        "/api/analyze",
        data={"text": "Some offer text", "language": "fr"},
    )
    assert response.status_code == 400
    assert "language" in response.json()["detail"].lower()


def test_analyze_unsupported_image_type_returns_400():
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
    response = client.post(
        "/api/analyze",
        files={"files": ("offer.pdf", fake_pdf, "application/pdf")},
    )
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()


def test_analyze_empty_image_returns_400():
    empty = io.BytesIO(b"")
    response = client.post(
        "/api/analyze",
        files={"files": ("empty.jpg", empty, "image/jpeg")},
    )
    assert response.status_code == 400


@patch("app.api.routes_analyze.analyze_document")
def test_analyze_text_returns_extraction(mock_analyze):
    mock_analyze.return_value = _response_with_destination("Qatar")

    response = client.post(
        "/api/analyze",
        data={"text": "Job offer for Qatar", "language": "en"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "caution"
    assert body["language"] == "en"
    assert body["extracted"]["destination"]["value"] == "Qatar"


@patch("app.api.routes_analyze.analyze_document")
def test_analyze_image_returns_extraction(mock_analyze):
    mock_analyze.return_value = AnalyzeResponse(
        verdict="fewer_concerns",
        score=0,
        language="bn",
        input_summary="1 image(s) analyzed; read via vision",
        extracted=_empty_extraction().model_dump(),
        read_method="vision",
    )

    tiny_jpeg = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
        0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9,
    ])

    response = client.post(
        "/api/analyze",
        files={"files": ("offer.jpg", io.BytesIO(tiny_jpeg), "image/jpeg")},
        data={"language": "bn"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "1 image(s) analyzed" in body["input_summary"]


@patch("app.api.routes_analyze.analyze_document")
def test_analyze_pipeline_error_returns_clear_payload(mock_analyze):
    mock_analyze.side_effect = AnalyzePipelineError(
        code=VISION_FAILED.code,
        message_en=VISION_FAILED.message_en,
        message_bn=VISION_FAILED.message_bn,
        http_status=VISION_FAILED.http_status,
    )

    response = client.post(
        "/api/analyze",
        data={"text": "Some offer text"},
    )

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert detail["code"] == "VISION_FAILED"
    assert "en" in detail and "bn" in detail


@patch("app.api.routes_analyze.analyze_document")
def test_analyze_response_shape(mock_analyze):
    mock_analyze.return_value = _response_with_destination("Qatar")

    response = client.post(
        "/api/analyze",
        data={"text": "Some text"},
    )

    body = response.json()
    for key in ("verdict", "score", "language", "input_summary",
                "extracted", "flags", "unverifiable", "missing_clauses",
                "questions_to_ask", "helplines", "audio_script_bn", "read_method"):
        assert key in body, f"Missing key: {key}"


@patch("app.pipeline.extract.extract_structured_fields")
def test_analyze_e2e_pipeline_through_api(mock_extract):
    mock_extract.return_value = OfferExtraction(
        destination=ExtractedField(value="Qatar", confidence=0.95, source_snippet="Qatar"),
        employer=ExtractedField(value="Gulf Builders", confidence=0.9, source_snippet="Gulf Builders"),
        job_title=ExtractedField(value="Laborer", confidence=0.9, source_snippet="Laborer"),
        salary=ExtractedField(value="USD 8000 per month", confidence=0.9, source_snippet="USD 8000 per month"),
        fee_asked=ExtractedField(value="BDT 300,000", confidence=0.9, source_snippet="BDT 300,000"),
        duration=ExtractedField(value="2 years", confidence=0.9, source_snippet="2 years"),
        hours=ExtractedField(value="8 hours", confidence=0.9, source_snippet="8 hours"),
        accommodation=ExtractedField(value="provided", confidence=0.9, source_snippet="provided"),
        visa_type=ExtractedField(value="employment", confidence=0.9, source_snippet="employment"),
        agent=ExtractedField(value="Fake Agency", confidence=0.8, source_snippet="Fake Agency"),
        license_number=ExtractedField(value="RL2058", confidence=0.9, source_snippet="RL2058"),
    )

    response = client.post(
        "/api/analyze",
        data={"text": "overtime food medical return ticket termination dispute repatriation", "language": "bn"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] in {"danger", "caution", "fewer_concerns"}
    assert body["verdict"] != "safe"
    assert body["score"] > 0
    assert len(body["flags"]) > 0
    assert len(body["helplines"]) > 0
    assert body["audio_script_bn"] != ""
    assert body["read_method"] == "pasted_text"

