"""Mask common identity numbers before text is sent to a model."""

from __future__ import annotations

import logging
import re
from io import BytesIO
from typing import Sequence

logger = logging.getLogger(__name__)

_PHONE_RE = re.compile(
    r"(?<!\w)(?:(?:\+?88[\s-]?)?01[3-9]|(?:\+?880[\s-]?)?[1][3-9])"
    r"(?:[\s-]?\d){8}(?!\w)",
    re.IGNORECASE,
)
_PASSPORT_LABEL_RE = re.compile(
    r"(?i)\b(?:passport(?:\s*(?:no|number))?|পাসপোর্ট(?:\s*নম্বর)?)"
    r"\s*[:#-]?\s*[A-Z0-9][A-Z0-9 -]{5,14}"
)
_PASSPORT_NUMBER_RE = re.compile(r"(?<!\w)[A-Z]{1,2}\d{7,9}(?!\w)", re.IGNORECASE)


def mask_pii(text: str) -> str:
    """Replace phone and passport identifiers while retaining surrounding text."""
    masked = _PHONE_RE.sub("[PHONE REDACTED]", text)
    masked = _PASSPORT_LABEL_RE.sub("[PASSPORT REDACTED]", masked)
    return _PASSPORT_NUMBER_RE.sub("[PASSPORT REDACTED]", masked)


def mask_extraction_pii(extraction):
    """Remove identifiers from model-returned values and evidence snippets."""
    for field_name in type(extraction).model_fields:
        field = getattr(extraction, field_name)
        field.value = mask_pii(field.value) if field.value else field.value
        field.source_snippet = mask_pii(field.source_snippet)
    return extraction


def mask_image_pii(images: Sequence[tuple[bytes, str]]) -> list[tuple[bytes, str]]:
    """Redact OCR-detected phone and passport tokens before vision calls."""
    try:
        import pytesseract
        from PIL import Image, ImageDraw
    except ImportError:
        logger.warning("Image PII masking dependencies are unavailable; passing original images.")
        return list(images)

    masked_images: list[tuple[bytes, str]] = []
    for payload, mime_type in images:
        try:
            with Image.open(BytesIO(payload)) as source:
                image = source.convert("RGB")
                data = pytesseract.image_to_data(
                    image,
                    lang="ben+eng",
                    output_type=pytesseract.Output.DICT,
                )
                draw = ImageDraw.Draw(image)
                for index, token in enumerate(data.get("text", [])):
                    if not token.strip() or not (
                        _PHONE_RE.search(token)
                        or _PASSPORT_NUMBER_RE.search(token)
                        or "passport" in token.lower()
                        or "পাসপোর্ট" in token
                    ):
                        continue
                    left = int(data["left"][index])
                    top = int(data["top"][index])
                    width = int(data["width"][index])
                    height = int(data["height"][index])
                    draw.rectangle(
                        (left, top, left + width, top + height),
                        fill="black",
                    )
                output = BytesIO()
                format_name = {
                    "image/png": "PNG",
                    "image/webp": "WEBP",
                }.get(mime_type, "JPEG")
                image.save(output, format=format_name)
                masked_images.append((output.getvalue(), mime_type))
        except Exception as exc:
            logger.warning("Image PII masking skipped due to error: %s", exc)
            masked_images.append((payload, mime_type))
    return masked_images
