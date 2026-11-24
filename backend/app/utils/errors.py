"""User-facing pipeline errors with a stable code and English/Bangla text."""

from __future__ import annotations


class AnalyzePipelineError(Exception):
    """Raised when analysis cannot finish. Routes map this to HTTP errors."""

    def __init__(
        self,
        code: str,
        message_en: str,
        message_bn: str,
        http_status: int = 502,
    ) -> None:
        super().__init__(message_en)
        self.code = code
        self.message_en = message_en
        self.message_bn = message_bn
        self.http_status = http_status

    def as_detail(self) -> dict[str, str]:
        return {
            "code": self.code,
            "en": self.message_en,
            "bn": self.message_bn,
        }


VISION_FAILED = AnalyzePipelineError(
    code="VISION_FAILED",
    message_en=(
        "The document reader could not finish. We tried a backup reader. "
        "Please send a clearer photo or paste the text."
    ),
    message_bn=(
        "কাগজ পড়া যায়নি। ব্যাকআপ পাঠকও কাজ করেনি। "
        "আরও পরিষ্কার ছবি দিন অথবা লেখা পেস্ট করুন।"
    ),
    http_status=502,
)

TIMEOUT = AnalyzePipelineError(
    code="LLM_TIMEOUT",
    message_en="The document reader timed out. Please try again in a moment.",
    message_bn="কাগজ পড়তে দেরি হয়েছে। একটু পরে আবার চেষ্টা করুন।",
    http_status=504,
)

UNREADABLE = AnalyzePipelineError(
    code="UNREADABLE_DOCUMENT",
    message_en=(
        "This image could not be read. Take a photo in good light, "
        "with the full page in frame, or paste the offer text."
    ),
    message_bn=(
        "ছবি পড়া যায়নি। আলোতে পুরো পাতা ধরে ছবি তুলুন, "
        "অথবা অফারের লেখা পেস্ট করুন।"
    ),
    http_status=422,
)

OCR_UNAVAILABLE = AnalyzePipelineError(
    code="OCR_UNAVAILABLE",
    message_en=(
        "The backup text reader is not installed on this server. "
        "Please paste the offer text or try again later."
    ),
    message_bn=(
        "ব্যাকআপ টেক্সট পাঠক এই সার্ভারে নেই। "
        "অফারের লেখা পেস্ট করুন অথবা পরে চেষ্টা করুন।"
    ),
    http_status=503,
)
