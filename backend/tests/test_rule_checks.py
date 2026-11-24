from app.rules.checks import (
    check_r01_no_written_contract,
    check_r02_non_work_visa,
    check_r03_cash_or_unspecified_fee,
    check_r04_high_risk_scam_pattern,
    check_r06_missing_critical_clauses,
    check_r07_missing_agency_license,
    check_r08_sign_on_arrival,
    check_r09_passport_retention,
    check_r11_pressure_tactics,
    check_r12_personal_mobile_payment,
)
from app.rules.engine import evaluate_rules


def field(value, source_snippet=None):
    return {"value": value, "source_snippet": source_snippet}


def test_document_type_and_visa_checks():
    assert check_r01_no_written_contract({"document_type": "chat_screenshot"})
    assert check_r01_no_written_contract({"document_type": "formal_contract"}) is None
    assert check_r02_non_work_visa({"visa_type": field("tourist visa")})
    assert check_r02_non_work_visa({"visa_type": field("employment visa")}) is None


def test_payment_checks_require_explicit_warning_signs():
    assert check_r03_cash_or_unspecified_fee({"payment_method": field("cash")})
    assert check_r03_cash_or_unspecified_fee({"payment_method": field("bank transfer")}) is None
    assert check_r12_personal_mobile_payment(
        {"payment_method": field("personal bKash account before visa")}
    )
    assert check_r12_personal_mobile_payment(
        {"payment_method": field("bank transfer")}
    ) is None


def test_destination_risk_requires_risky_country_and_job():
    extracted = {
        "destination": field("Cambodia"),
        "job_title": field("Online marketing"),
    }
    patterns = {
        "high_risk_countries": ["cambodia"],
        "scam_job_keywords": ["online marketing"],
    }
    assert check_r04_high_risk_scam_pattern(extracted, patterns)
    extracted["job_title"] = field("Nurse")
    assert check_r04_high_risk_scam_pattern(extracted, patterns) is None


def test_missing_clauses_and_license_are_reported():
    assert check_r06_missing_critical_clauses({}) == (
        "Missing: employer, job_title, salary_amount, duration, working_hours, "
        "accommodation, return_ticket"
    )
    assert check_r07_missing_agency_license({}) == "No RL license number found in document"
    assert check_r07_missing_agency_license({"license_number": field("RL-123")}) is None


def test_text_checks_find_red_flags_in_extracted_clauses():
    assert check_r08_sign_on_arrival(
        {"raw_red_flag_clauses": ["Sign the contract after arrival."]}
    )
    assert check_r09_passport_retention(
        {"raw_red_flag_clauses": ["We will keep passport."]}
    )
    assert check_r11_pressure_tactics(
        {"raw_red_flag_clauses": ["Pay today or lose this offer."]}
    )
    assert check_r11_pressure_tactics(
        {"raw_red_flag_clauses": ["Please review the offer this week."]}
    ) is None


def test_engine_uses_catalog_metadata_and_check_evidence():
    extracted = {
        "document_type": "chat_screenshot",
        "raw_red_flag_clauses": ["Pay today or lose this offer."],
    }

    result = evaluate_rules(extracted)
    flags = result["flags"]

    assert [flag["rule_id"] for flag in flags] == [
        "R01_NO_WRITTEN_CONTRACT",
        "R06_MISSING_CRITICAL_CLAUSES",
        "R07_MISSING_AGENCY_LICENSE",
        "R11_PRESSURE_TACTICS",
        "R15_UNVERIFIABLE_EMPLOYER",
    ]
    assert flags[0]["severity"] == "high"
    assert flags[0]["title_en"] == "No formal written contract"
    flag_map = {f["rule_id"]: f for f in flags}
    assert flag_map["R11_PRESSURE_TACTICS"]["evidence_snippet"] == "Pay today or lose this offer."

