from app.api.schemas import ExtractedField, OfferExtraction
from app.pipeline.verify import verify_offer


def _field(value: str, snippet: str | None = None) -> ExtractedField:
    return ExtractedField(value=value, confidence=0.9, source_snippet=snippet or value)


def test_active_license_is_not_flagged():
    extraction = OfferExtraction(
        license_number=_field("RL-1857"),
        agent=_field("1 Plus Overseas Limited"),
        employer=_field("Acme"),
        job_title=_field("construction labour"),
        salary=_field("QAR 1500 per month"),
        fee_asked=_field("BDT 50000"),
        destination=_field("Qatar"),
        visa_type=_field("work visa"),
        duration=_field("2 years"),
        hours=_field("8 hours"),
        accommodation=_field("camp provided"),
    )
    result = verify_offer(extraction, document_text="overtime food medical return ticket termination dispute repatriation")
    assert not any(flag.rule_id == "R07_license" for flag in result.flags)


def test_missing_license_flags():
    extraction = OfferExtraction(agent=_field("Random sub agent", "pay my bkash"))
    result = verify_offer(extraction)
    assert any(flag.rule_id == "R07_license" for flag in result.flags)


def test_expired_license_flags():
    extraction = OfferExtraction(license_number=_field("RL2058", "Licence RL2058"))
    result = verify_offer(extraction)
    assert any(flag.rule_id == "R07_license" for flag in result.flags)


def test_unknown_license_is_unverifiable_not_unlicensed():
    extraction = OfferExtraction(license_number=_field("RL9999", "RL9999"))
    result = verify_offer(extraction)
    assert not any(flag.rule_id == "R07_license" for flag in result.flags)
    assert any("agency_license_not_in_snapshot" in item for item in result.unverifiable)


def test_fee_above_cap_flags():
    extraction = OfferExtraction(
        destination=_field("Qatar"),
        fee_asked=_field("Tk 250,000", "Fee Tk 250,000"),
    )
    result = verify_offer(extraction)
    assert any(flag.rule_id == "R03_fee_cap" for flag in result.flags)


def test_fee_under_cap_does_not_flag():
    extraction = OfferExtraction(
        destination=_field("Qatar"),
        fee_asked=_field("BDT 80000"),
    )
    result = verify_offer(extraction)
    assert not any(flag.rule_id == "R03_fee_cap" for flag in result.flags)


def test_unrealistic_salary_flags():
    extraction = OfferExtraction(
        destination=_field("Qatar"),
        job_title=_field("construction labour"),
        salary=_field("USD 8000 per month", "Salary USD 8000 per month"),
    )
    result = verify_offer(extraction)
    assert any(flag.rule_id == "R05_salary" for flag in result.flags)


def test_missing_clauses_lists_essentials():
    result = verify_offer(OfferExtraction())
    assert "employer name" in result.missing_clauses
    assert "job title" in result.missing_clauses
    assert any(flag.rule_id == "R06_missing_clauses" for flag in result.flags)
