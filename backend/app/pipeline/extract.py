# Thin pipeline step: validates and normalises the raw LLM extraction output.
# Sits between the route handler and the LLM client so the route never sees
# partially-filled or inconsistent ExtractedField objects.

import math
from typing import Sequence

from app.api.schemas import OfferExtraction
from app.llm.client import extract_structured_fields  # fixed import path
from app.utils.pii_mask import mask_extraction_pii


def extract_offer_fields(
    images: Sequence[tuple[bytes, str]],
    text: str = "",
) -> OfferExtraction:
    """Call the LLM client and enforce the no-evidence-no-value rule.

    If a field has a value but no source_snippet (or vice versa), the whole
    field is zeroed out.  Confidence is clamped to [0, 1].
    """
    extraction = extract_structured_fields(
        images=images,
        text=text,
    )
    mask_extraction_pii(extraction)

    # Enforce: every accepted field must have both a value and a source snippet.
    for field_name in OfferExtraction.model_fields:
        field = getattr(extraction, field_name)

        value = field.value
        source_snippet = field.source_snippet
        has_value = isinstance(value, str) and bool(value.strip())
        has_snippet = isinstance(source_snippet, str) and bool(source_snippet.strip())

        if not has_value or not has_snippet:
            # Reject — missing evidence means the field cannot be trusted.
            field.value = None
            field.confidence = 0.0
            field.source_snippet = ""
        else:
            # Clean whitespace and clamp confidence to valid range.
            field.value = value.strip() if isinstance(value, str) else value
            field.source_snippet = source_snippet.strip()
            confidence = float(field.confidence)
            field.confidence = (
                max(0.0, min(1.0, confidence))
                if math.isfinite(confidence)
                else 0.0
            )
    return extraction
