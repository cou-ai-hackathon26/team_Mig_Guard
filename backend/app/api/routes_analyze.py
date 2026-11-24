# POST /api/analyze — images or pasted text in, verified verdict out.

from typing import Optional

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from starlette.concurrency import run_in_threadpool

from app.api.schemas import AnalyzeResponse
from app.config import settings
from app.pipeline.orchestrator import analyze_document
from app.utils.errors import AnalyzePipelineError
from app.utils.rate_limit import RateLimiter

router = APIRouter(tags=["analyze"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGES_PER_REQUEST = 4
_rate_limiter = RateLimiter(settings.rate_limit_per_minute)


def _validate_analyze_input(
    cleaned_text: str,
    uploaded_files: list[UploadFile],
    language: str,
) -> None:
    if language not in {"bn", "en"}:
        raise HTTPException(
            status_code=400,
            detail="Language must be 'bn' or 'en'.",
        )

    if not cleaned_text and not uploaded_files:
        raise HTTPException(
            status_code=400,
            detail="Please upload an image or paste offer text.",
        )

    if len(uploaded_files) > MAX_IMAGES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_IMAGES_PER_REQUEST} images are allowed per request.",
        )


async def _read_uploaded_images(
    uploaded_files: list[UploadFile],
) -> list[tuple[bytes, str]]:
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    images: list[tuple[bytes, str]] = []

    for upload in uploaded_files:
        if upload.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type: {upload.content_type}",
            )
        payload = await upload.read(max_bytes + 1)
        if len(payload) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Image exceeds {settings.max_upload_size_mb} MB.",
            )
        if not payload:
            raise HTTPException(
                status_code=400,
                detail="An uploaded image is empty.",
            )
        images.append((payload, upload.content_type))

    return images


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_offer(
    request: Request,
    files: Optional[list[UploadFile]] = File(default=None),
    text: Optional[str] = Form(default=None),
    language: str = Form(default="bn"),
) -> AnalyzeResponse:
    client_host = request.client.host if request.client else "unknown"
    if not _rate_limiter.allow(client_host):
        raise HTTPException(
            status_code=429,
            detail="Too many analysis requests. Please try again in a minute.",
        )
    cleaned_text = (text or "").strip()
    uploaded_files = files or []

    _validate_analyze_input(cleaned_text, uploaded_files, language)
    images = await _read_uploaded_images(uploaded_files)

    try:
        return await run_in_threadpool(
            analyze_document,
            images,
            cleaned_text,
            language,
        )
    except AnalyzePipelineError as exc:
        raise HTTPException(
            status_code=exc.http_status,
            detail=exc.as_detail(),
        ) from exc
