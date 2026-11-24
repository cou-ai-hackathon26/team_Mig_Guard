from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api.schemas import ExtractedField, OfferExtraction
from app.main import app
from app.pipeline.extract import extract_offer_fields
from app.utils.pii_mask import mask_pii


client = TestClient(app)


def test_mask_pii_handles_phone_and_passport():
    masked = mask_pii("Call +880 1712-345678. Passport: AB1234567.")
    assert "1712" not in masked
    assert "AB1234567" not in masked
    assert "[PHONE REDACTED]" in masked
    assert "[PASSPORT REDACTED]" in masked


@patch("app.pipeline.extract.extract_structured_fields")
def test_extraction_masks_identifiers_in_values_and_evidence(mock_extract):
    mock_extract.return_value = OfferExtraction(
        contact_channel=ExtractedField(
            value="01712345678",
            confidence=0.9,
            source_snippet="Call 01712345678",
        )
    )
    result = extract_offer_fields([], "Call 01712345678")
    assert "01712345678" not in result.contact_channel.value
    assert "01712345678" not in result.contact_channel.source_snippet


def test_tts_without_provider_returns_browser_fallback():
    with patch("app.pipeline.tts.settings.tts_provider", "browser"):
        response = client.post("/api/tts", json={"text": "ফলাফল সতর্কতা"})
    assert response.status_code == 200
    assert response.json() == {
        "audio_available": False,
        "fallback": "browser_speech",
        "text": "ফলাফল সতর্কতা",
    }


def test_tts_edge_returns_mp3():
    with patch(
        "app.pipeline.tts._synthesize_edge",
        new_callable=AsyncMock,
        return_value=b"fake-mp3",
    ):
        with patch("app.pipeline.tts.settings.tts_provider", "edge"):
            response = client.post("/api/tts", json={"text": "ফলাফল সতর্কতা"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"fake-mp3"


def test_analyze_rate_limit_returns_429():
    with patch("app.api.routes_analyze._rate_limiter") as limiter:
        limiter.allow.return_value = False
        response = client.post("/api/analyze", data={"text": "offer"})
    assert response.status_code == 429
