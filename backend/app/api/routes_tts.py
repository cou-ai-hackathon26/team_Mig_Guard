"""POST /api/tts — server speech with browser-speech fallback metadata."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.pipeline.tts import TTSUnavailable, synthesize_bangla

router = APIRouter(tags=["tts"])


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


@router.post("/tts")
def text_to_speech(payload: TTSRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Text must not be blank.")
    try:
        result = synthesize_bangla(text)
    except TTSUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if result.audio is None:
        return {
            "audio_available": False,
            "fallback": result.fallback,
            "text": text,
        }
    return Response(content=result.audio, media_type=result.mime_type)
