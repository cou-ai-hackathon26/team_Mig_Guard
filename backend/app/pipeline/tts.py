"""Bangla speech generation with Edge TTS and a client-side fallback."""

from __future__ import annotations

import asyncio
import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class TTSUnavailable(Exception):
    """Raised when server-side speech is unavailable."""


@dataclass(frozen=True)
class TTSResult:
    audio: bytes | None
    mime_type: str
    fallback: str | None = None


async def _synthesize_edge(text: str) -> bytes:
    try:
        import edge_tts
    except ImportError as exc:
        raise TTSUnavailable(
            "Edge TTS is not installed on this server."
        ) from exc

    output_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as output:
            output_path = Path(output.name)
        communicate = edge_tts.Communicate(text, settings.tts_voice)
        await communicate.save(str(output_path))
        return output_path.read_bytes()
    except Exception as exc:
        raise TTSUnavailable("Edge TTS could not generate audio.") from exc
    finally:
        if output_path:
            output_path.unlink(missing_ok=True)


def synthesize_bangla(text: str) -> TTSResult:
    if settings.tts_provider in {"", "browser"}:
        return TTSResult(None, "audio/wav", "browser_speech")
    if settings.tts_provider != "edge":
        raise TTSUnavailable(f"Unsupported TTS provider: {settings.tts_provider}")

    try:
        audio = asyncio.run(_synthesize_edge(text))
    except TTSUnavailable:
        logger.exception("Edge TTS failed; client-side speech is available.")
        return TTSResult(None, "audio/wav", "browser_speech")
    return TTSResult(audio, "audio/mpeg")
