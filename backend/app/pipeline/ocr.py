"""Tesseract OCR fallback when the vision model cannot read an image."""

from __future__ import annotations

import io
import logging
from typing import Sequence

from app.config import settings
from app.utils.errors import OCR_UNAVAILABLE, UNREADABLE, AnalyzePipelineError

logger = logging.getLogger(__name__)


def transcribe_images(images: Sequence[tuple[bytes, str]]) -> str:
    """Return concatenated Bangla+English text from images.

    Raises AnalyzePipelineError when Tesseract is missing or every image is empty.
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise AnalyzePipelineError(
            code=OCR_UNAVAILABLE.code,
            message_en=OCR_UNAVAILABLE.message_en,
            message_bn=OCR_UNAVAILABLE.message_bn,
            http_status=OCR_UNAVAILABLE.http_status,
        ) from exc

    chunks: list[str] = []
    timeout = settings.ocr_timeout_seconds
    for index, (payload, _mime) in enumerate(images, start=1):
        try:
            with Image.open(io.BytesIO(payload)) as image:
                rgb = image.convert("RGB")
                text = pytesseract.image_to_string(
                    rgb,
                    lang="ben+eng",
                    timeout=timeout,
                )
        except pytesseract.TesseractNotFoundError as exc:
            raise AnalyzePipelineError(
                code=OCR_UNAVAILABLE.code,
                message_en=OCR_UNAVAILABLE.message_en,
                message_bn=OCR_UNAVAILABLE.message_bn,
                http_status=OCR_UNAVAILABLE.http_status,
            ) from exc
        except RuntimeError as exc:
            logger.warning("OCR timeout on image %s: %s", index, exc)
            continue
        except Exception:
            logger.exception("OCR failed on image %s", index)
            continue
        cleaned = text.strip()
        if cleaned:
            chunks.append(cleaned)

    combined = "\n\n".join(chunks).strip()
    if not combined:
        raise AnalyzePipelineError(
            code=UNREADABLE.code,
            message_en=UNREADABLE.message_en,
            message_bn=UNREADABLE.message_bn,
            http_status=UNREADABLE.http_status,
        )
    return combined
