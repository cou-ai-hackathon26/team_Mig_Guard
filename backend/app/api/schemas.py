# Pydantic models shared across the whole backend.
# Defines request/response shapes for /api/health and /api/analyze.
# OfferExtraction is also used as the structured-output schema sent to Gemini.
from typing import Literal, Optional
from pydantic import BaseModel, Field

VerdictType = Literal["danger", "caution", "fewer_concerns"]

class HealthResponse(BaseModel):
    status: str = "ok"
    env: str

class ExtractedField(BaseModel):
    value: Optional[str] = Field(
        default=None,
        description="Extracted value from the document. Null if absent."
    )
    confidence: float = Field(
        default=0.0,
        description=(
            "Model-estimated extraction confidence. "
            "Raw value from the LLM; pipeline/extract.py clamps it to [0, 1]."
        )
    )
    source_snippet: str = Field(
        default="",
        description="Exact text from the original document supporting this value."
    )

class OfferExtraction(BaseModel):
    destination: ExtractedField = Field(
        default_factory=ExtractedField
    )

    employer: ExtractedField = Field(
        default_factory=ExtractedField
    )

    job_title: ExtractedField = Field(
        default_factory=ExtractedField
    )

    salary: ExtractedField = Field(
        default_factory=ExtractedField
    )

    fee_asked: ExtractedField = Field(
        default_factory=ExtractedField
    )

    visa_type: ExtractedField = Field(
        default_factory=ExtractedField
    )

    duration: ExtractedField = Field(
        default_factory=ExtractedField
    )

    hours: ExtractedField = Field(
        default_factory=ExtractedField
    )

    accommodation: ExtractedField = Field(
        default_factory=ExtractedField
    )

    agent: ExtractedField = Field(
        default_factory=ExtractedField
    )

    license_number: ExtractedField = Field(
        default_factory=ExtractedField
    )

    payment_method: ExtractedField = Field(
        default_factory=ExtractedField
    )

    contact_channel: ExtractedField = Field(
        default_factory=ExtractedField
    )

class KnowledgePassage(BaseModel):
    id: str
    title: str = ""
    text: str = ""
    source: str = ""
    source_url: str = ""


class Flag(BaseModel):
    rule_id: str
    severity: str
    weight: int = 0
    title_en: str
    title_bn: str
    explanation_en: str
    explanation_bn: str
    evidence_snippet: str = ""
    question_en: str = ""
    question_bn: str = ""
    kb_ids: list[str] = Field(default_factory=list)
    passages: list[KnowledgePassage] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    verdict: VerdictType = "caution"
    score: int = Field(default=50, ge=0, le=100)
    language: str = "bn"
    input_summary: str
    extracted: dict[str, ExtractedField] = Field(default_factory=dict)
    flags: list[Flag] = Field(default_factory=list)
    missing_clauses: list[str] = Field(default_factory=list)
    questions_to_ask: list[dict[str, str]] = Field(default_factory=list)
    unverifiable: list[str] = Field(default_factory=list)
    helplines: list[dict[str, str]] = Field(default_factory=list)
    audio_script_bn: str = ""
    read_method: str = ""