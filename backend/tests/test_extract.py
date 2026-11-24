# Tests for extract_offer_fields — the pipeline normalisation step.
# These tests run with pytest from the backend/ directory: pytest tests/
# They do NOT make real LLM calls; they patch extract_structured_fields.

import pytest
from unittest.mock import patch

from app.api.schemas import ExtractedField, OfferExtraction
from app.pipeline.extract import extract_offer_fields


def _make_extraction(**kwargs) -> OfferExtraction:
    """Helper: build an OfferExtraction with sane defaults; override specific fields."""
    defaults = {
        field: ExtractedField()
        for field in OfferExtraction.model_fields
    }
    defaults.update(kwargs)
    return OfferExtraction(**defaults)


@patch("app.pipeline.extract.extract_structured_fields")
def test_valid_field_passes_through(mock_llm):
    """A field with a value and a matching source snippet should be kept as-is."""
    mock_llm.return_value = _make_extraction(
        destination=ExtractedField(
            value="Malaysia",
            confidence=0.95,
            source_snippet="Destination: Malaysia",
        )
    )

    result = extract_offer_fields(images=[], text="Destination: Malaysia")

    dest = result.destination
    assert dest.value == "Malaysia"
    assert dest.confidence == 0.95
    assert dest.source_snippet == "Destination: Malaysia"


@patch("app.pipeline.extract.extract_structured_fields")
def test_value_without_snippet_is_zeroed(mock_llm):
    """A value with no source snippet must be rejected (no evidence rule)."""
    mock_llm.return_value = _make_extraction(
        job_title=ExtractedField(
            value="Data Entry",
            confidence=0.8,
            source_snippet="",   # <-- missing snippet
        )
    )

    result = extract_offer_fields(images=[], text="Job: Data Entry")

    jt = result.job_title
    assert jt.value is None
    assert jt.confidence == 0.0
    assert jt.source_snippet == ""


@patch("app.pipeline.extract.extract_structured_fields")
def test_snippet_without_value_is_zeroed(mock_llm):
    """A source snippet with a null value must also be rejected."""
    mock_llm.return_value = _make_extraction(
        salary=ExtractedField(
            value=None,
            confidence=0.5,
            source_snippet="Salary: 2000 USD",
        )
    )

    result = extract_offer_fields(images=[], text="Salary: 2000 USD")

    sal = result.salary
    assert sal.value is None
    assert sal.confidence == 0.0


@patch("app.pipeline.extract.extract_structured_fields")
def test_confidence_clamped_above_one(mock_llm):
    """Out-of-range confidence (> 1.0) must be clamped down to 1.0."""
    mock_llm.return_value = _make_extraction(
        visa_type=ExtractedField(
            value="Work Permit",
            confidence=1.5,          # out of range
            source_snippet="Visa: Work Permit",
        )
    )

    result = extract_offer_fields(images=[], text="Visa: Work Permit")
    assert result.visa_type.confidence == 1.0


@patch("app.pipeline.extract.extract_structured_fields")
def test_confidence_clamped_below_zero(mock_llm):
    """Out-of-range confidence (< 0) must be clamped up to 0.0."""
    mock_llm.return_value = _make_extraction(
        agent=ExtractedField(
            value="Some Agency",
            confidence=-0.3,         # out of range
            source_snippet="Agent: Some Agency",
        )
    )

    result = extract_offer_fields(images=[], text="Agent: Some Agency")
    assert result.agent.confidence == 0.0


@patch("app.pipeline.extract.extract_structured_fields")
def test_whitespace_stripped(mock_llm):
    """Leading/trailing whitespace in value and source_snippet should be removed."""
    mock_llm.return_value = _make_extraction(
        employer=ExtractedField(
            value="  Acme Corp  ",
            confidence=0.9,
            source_snippet="  Employer: Acme Corp  ",
        )
    )

    result = extract_offer_fields(images=[], text="Employer: Acme Corp")

    assert result.employer.value == "Acme Corp"
    assert result.employer.source_snippet == "Employer: Acme Corp"


@patch("app.pipeline.extract.extract_structured_fields")
def test_empty_extraction_all_null(mock_llm):
    """When the LLM returns all empty fields, the result must have all None values."""
    mock_llm.return_value = OfferExtraction()  # all defaults

    result = extract_offer_fields(images=[], text="")

    for field_name in OfferExtraction.model_fields:
        field = getattr(result, field_name)
        assert field.value is None, f"Expected {field_name}.value to be None"
        assert field.confidence == 0.0
