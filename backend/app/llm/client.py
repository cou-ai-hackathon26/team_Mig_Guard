# LLM client for Mig_Guard — wraps the Google Gemini SDK.
# Sends images + text to Gemini and returns structured OfferExtraction JSON.
# Timeouts, retries, and a secondary model are applied before giving up.

from __future__ import annotations

import json
import logging
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

from google import genai
from google.genai import types

from app.api.schemas import OfferExtraction
from app.config import settings
from app.utils.pii_mask import mask_image_pii, mask_pii
from app.utils.usage import UsageLimitExceeded, usage_guard

logger = logging.getLogger(__name__)


class LLMExtractionError(Exception):
    """Raised when no model can produce a valid extraction."""

    def __init__(self, message: str, timed_out: bool = False) -> None:
        super().__init__(message)
        self.timed_out = timed_out


class LLMUsageLimitError(LLMExtractionError):
    """Raised when the configured model budget is exhausted."""


PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "prompts"
    / "extract_system.txt"
)


@lru_cache(maxsize=4)
def _get_client(api_key: str) -> genai.Client:
    timeout_ms = settings.llm_timeout_seconds * 1000
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=timeout_ms),
    )


def _load_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise LLMExtractionError(f"Extraction prompt not found at {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8")


def _is_retryable(exc: Exception) -> bool:
    tokens = (
        "timeout",
        "timed out",
        "429",
        "500",
        "502",
        "503",
        "504",
        "unavailable",
        "temporarily",
        "resource exhausted",
        "deadline",
        "connection",
        "reset",
    )
    message = str(exc).lower()
    if any(token in message for token in tokens):
        return True
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return code in {408, 429, 500, 502, 503, 504}


def _is_timeout(exc: Exception) -> bool:
    message = str(exc).lower()
    return "timeout" in message or "timed out" in message or "deadline" in message


def _build_contents(
    images: Sequence[tuple[bytes, str]],
    text: str,
    prompt: str,
) -> list:
    parts: list[types.Part] = [types.Part.from_text(text=prompt)]
    if text.strip():
        parts.append(
            types.Part.from_text(
                text=f"Additional text supplied by the user:\n{mask_pii(text.strip())}"
            )
        )
    for index, (image_bytes, mime_type) in enumerate(images, start=1):
        parts.append(types.Part.from_text(text=f"Uploaded document image {index}:"))
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
    return parts


def _sleep_backoff(attempt: int) -> None:
    time.sleep(min(8.0, 0.8 * (2 ** attempt)))


def _generate(
    api_key: str,
    model: str,
    contents: list,
    config: types.GenerateContentConfig,
) -> str:
    attempts = max(1, settings.llm_max_attempts)
    last_error: Exception | None = None
    timed_out = False
    for attempt in range(attempts):
        try:
            usage_guard.reserve()
            client = _get_client(api_key)
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            output_text = response.text
            if not output_text:
                raise ValueError(f"Model '{model}' returned an empty response.")
            return output_text
        except Exception as exc:
            if isinstance(exc, UsageLimitExceeded):
                raise LLMUsageLimitError(str(exc)) from exc
            last_error = exc
            timed_out = timed_out or _is_timeout(exc)
            if attempt < attempts - 1 and _is_retryable(exc):
                logger.warning(
                    "LLM call failed (attempt %s/%s, model=%s): %s",
                    attempt + 1,
                    attempts,
                    model,
                    exc,
                )
                _sleep_backoff(attempt)
                continue
            break
    message = f"Model '{model}' failed: {last_error}"
    raise LLMExtractionError(message, timed_out=timed_out) from last_error


def _call_gemini(
    api_key: str,
    model: str,
    images: Sequence[tuple[bytes, str]],
    text: str,
    prompt: str,
) -> OfferExtraction:
    contents = _build_contents(images, text, prompt)
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=OfferExtraction,
        http_options=types.HttpOptions(timeout=settings.llm_timeout_seconds * 1000),
    )
    output_text = _generate(api_key, model, contents, config)
    return OfferExtraction.model_validate_json(output_text)


def _model_chain() -> list[tuple[str, str]]:
    if not settings.primary_llm_api_key:
        raise LLMExtractionError(
            "PRIMARY_LLM_API_KEY is not set. Add it to backend/.env."
        )
    chain = [(settings.primary_llm_api_key, settings.primary_llm_model)]
    fallback_key = settings.fallback_llm_api_key or settings.primary_llm_api_key
    fallback_model = settings.fallback_llm_model
    if fallback_key and fallback_model and (
        fallback_model != settings.primary_llm_model
        or fallback_key != settings.primary_llm_api_key
    ):
        chain.append((fallback_key, fallback_model))
    return chain


def extract_structured_fields(
    images: Sequence[tuple[bytes, str]],
    text: str = "",
) -> OfferExtraction:
    prompt = _load_prompt()
    try:
        safe_images = mask_image_pii(images)
    except RuntimeError as exc:
        raise LLMExtractionError(str(exc)) from exc
    errors: list[Exception] = []
    timed_out = False
    for api_key, model in _model_chain():
        try:
            return _call_gemini(
                api_key=api_key,
                model=model,
                images=safe_images,
                text=text,
                prompt=prompt,
            )
        except LLMExtractionError as exc:
            timed_out = timed_out or exc.timed_out
            errors.append(exc)
            logger.warning("Extraction model %s failed: %s", model, exc)
    raise LLMExtractionError(
        "Document extraction failed after retries and fallback. "
        + "; ".join(str(err) for err in errors),
        timed_out=timed_out,
    )


def generate_json(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    """Free-form JSON call used for grounded explanations."""
    contents = [
        types.Part.from_text(text=system_prompt),
        types.Part.from_text(text=mask_pii(user_prompt)),
    ]
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        http_options=types.HttpOptions(timeout=settings.llm_timeout_seconds * 1000),
    )
    api_key, model = _model_chain()[0]
    output_text = _generate(api_key, model, contents, config)
    data = json.loads(output_text)
    if not isinstance(data, dict):
        raise LLMExtractionError("Explanation model did not return a JSON object.")
    return data
