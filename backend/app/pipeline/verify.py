"""Deterministic verification: licence, fee cap, salary band, missing clauses."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.api.schemas import ExtractedField, Flag, OfferExtraction
from app.data.loader import (
    agencies_meta,
    catalog,
    fee_caps,
    licensed_agencies,
    salary_benchmarks,
)
from app.utils.license import normalize_license
from app.utils.money import convert_to_bdt, parse_money, to_monthly

ESSENTIAL_FIELDS = [
    ("employer", "employer name"),
    ("job_title", "job title"),
    ("salary", "salary"),
    ("duration", "contract duration"),
    ("hours", "working hours"),
    ("accommodation", "accommodation"),
    ("destination", "destination"),
    ("visa_type", "visa type"),
    ("fee_asked", "recruitment fee"),
]

KEYWORD_CLAUSES = [
    ("overtime", ("overtime", "ওভারটাইম")),
    ("food", ("food", "meal", "খাওয়া", "খাবার")),
    ("medical", ("medical", "insurance", "চিকিৎসা")),
    ("return ticket", ("return ticket", "return airfare", "ফিরতি টিকিট")),
    ("termination", ("terminat", "notice period", "চুক্তি বাতিল")),
    ("dispute resolution", ("dispute", "arbitration", "বিরোধ")),
    ("repatriation", ("repatriat", "প্রত্যাবাসন")),
]


@dataclass
class VerificationResult:
    flags: list[Flag] = field(default_factory=list)
    missing_clauses: list[str] = field(default_factory=list)
    unverifiable: list[str] = field(default_factory=list)
    questions_to_ask: list[dict[str, str]] = field(default_factory=list)


def _field_value(field: ExtractedField) -> str | None:
    if field.value and field.value.strip():
        return field.value.strip()
    return None


def _rule(rule_id: str) -> dict:
    return catalog()["rules"][rule_id]


def _flag(
    rule_id: str,
    evidence: str,
    extra_en: str = "",
    extra_bn: str = "",
    weight_override: int | None = None,
) -> Flag:
    rule = _rule(rule_id)
    explanation_en = rule["explanation_en"]
    explanation_bn = rule["explanation_bn"]
    if extra_en:
        explanation_en = f"{explanation_en} {extra_en}".strip()
    if extra_bn:
        explanation_bn = f"{explanation_bn} {extra_bn}".strip()
    return Flag(
        rule_id=rule_id,
        severity=rule["severity"],
        weight=int(weight_override if weight_override is not None else rule["weight"]),
        title_en=rule["title_en"],
        title_bn=rule["title_bn"],
        explanation_en=explanation_en,
        explanation_bn=explanation_bn,
        evidence_snippet=evidence[:400],
        question_en=rule["question_en"],
        question_bn=rule["question_bn"],
        kb_ids=list(rule.get("kb_ids") or []),
    )


def _alias_match(haystack: str, aliases: list[str]) -> bool:
    text = haystack.lower()
    return any(alias.lower() in text for alias in aliases)


def check_agency_license(extraction: OfferExtraction, result: VerificationResult) -> None:
    license_raw = _field_value(extraction.license_number)
    agent_raw = _field_value(extraction.agent)
    evidence = (
        extraction.license_number.source_snippet
        or extraction.agent.source_snippet
        or license_raw
        or agent_raw
        or ""
    )

    if not license_raw:
        result.flags.append(
            _flag(
                "R07_license",
                evidence or "No recruiting licence number found in the document.",
                extra_en="No RL number was found in this document.",
                extra_bn="এই কাগজে কোনো আরএল নম্বর পাওয়া যায়নি।",
            )
        )
        result.questions_to_ask.append(
            {
                "en": _rule("R07_license")["question_en"],
                "bn": _rule("R07_license")["question_bn"],
            }
        )
        return

    normalized = normalize_license(license_raw)
    if not normalized:
        result.flags.append(
            _flag(
                "R07_license",
                evidence,
                extra_en=f"The value '{license_raw}' is not an RL licence number.",
                extra_bn=f"'{license_raw}' একটি আরএল লাইসেন্স নম্বর নয়।",
            )
        )
        return

    record = licensed_agencies().get(normalized)
    if record is None:
        meta = agencies_meta()
        result.unverifiable.append(
            "agency_license_not_in_snapshot: "
            f"{normalized} was not in the {meta.get('count', 0)}-row RAIMS snapshot "
            f"retrieved {meta.get('retrieved')}. Check the live list at {meta.get('source_url')}."
        )
        return

    status = str(record.get("status", "")).title()
    registered_name = record.get("name", "")
    if status != "Active":
        result.flags.append(
            _flag(
                "R07_license",
                evidence,
                extra_en=(
                    f"{normalized} ({registered_name}) is listed as {status} "
                    f"until {record.get('valid_until', 'unknown')} on the RAIMS snapshot."
                ),
                extra_bn=(
                    f"{normalized} ({registered_name}) রাইমস স্ন্যাপশটে {status} "
                    f"হিসেবে আছে।"
                ),
            )
        )
        result.questions_to_ask.append(
            {
                "en": _rule("R07_license")["question_en"],
                "bn": _rule("R07_license")["question_bn"],
            }
        )


def check_fee_cap(extraction: OfferExtraction, result: VerificationResult) -> None:
    fee_raw = _field_value(extraction.fee_asked)
    dest_raw = _field_value(extraction.destination)
    if not fee_raw:
        result.unverifiable.append(
            "fee_cap_check: no recruitment fee was extracted, so the ceiling cannot be applied."
        )
        return
    if not dest_raw:
        result.unverifiable.append(
            "fee_cap_check: destination is missing, so the country ceiling cannot be selected."
        )
        return

    parsed = parse_money(fee_raw)
    if parsed is None:
        result.unverifiable.append(
            f"fee_cap_check: could not parse a number from fee text '{fee_raw}'."
        )
        return

    table = fee_caps()
    matched = None
    for row in table.get("caps", []):
        if _alias_match(dest_raw, row.get("aliases", [])):
            matched = row
            break
    if matched is None:
        result.unverifiable.append(
            f"fee_cap_check: no published ceiling in this dataset for destination '{dest_raw}'."
        )
        return

    fx = salary_benchmarks().get("fx_to_bdt_approx", {})
    if parsed.currency == "UNKNOWN":
        result.unverifiable.append(
            f"fee_cap_check: currency could not be read from '{fee_raw}'."
        )
        return

    fee_bdt = convert_to_bdt(parsed.amount, parsed.currency, fx)
    if fee_bdt is None:
        result.unverifiable.append(
            f"fee_cap_check: no conversion rate for currency {parsed.currency}."
        )
        return

    cap = float(matched["cap_bdt"])
    if fee_bdt > cap:
        evidence = extraction.fee_asked.source_snippet or fee_raw
        result.flags.append(
            _flag(
                "R03_fee_cap",
                evidence,
                extra_en=(
                    f"Stated fee is about BDT {fee_bdt:,.0f} for {matched['destination']}; "
                    f"published ceiling in this dataset is BDT {cap:,.0f} "
                    f"({table.get('caveat', '')})"
                ),
                extra_bn=(
                    f"{matched['destination']} এর জন্য উল্লিখিত ফি প্রায় {fee_bdt:,.0f} টাকা; "
                    f"এই ডেটাসেটের প্রকাশিত সীমা {cap:,.0f} টাকা।"
                ),
            )
        )
        result.questions_to_ask.append(
            {
                "en": _rule("R03_fee_cap")["question_en"],
                "bn": _rule("R03_fee_cap")["question_bn"],
            }
        )


def check_salary_benchmark(extraction: OfferExtraction, result: VerificationResult) -> None:
    salary_raw = _field_value(extraction.salary)
    dest_raw = _field_value(extraction.destination)
    job_raw = _field_value(extraction.job_title) or ""
    if not salary_raw:
        result.unverifiable.append(
            "salary_benchmark_check: no salary was extracted."
        )
        return
    if not dest_raw:
        result.unverifiable.append(
            "salary_benchmark_check: destination is missing."
        )
        return

    parsed = parse_money(salary_raw)
    if parsed is None:
        result.unverifiable.append(
            f"salary_benchmark_check: could not parse a number from '{salary_raw}'."
        )
        return
    if parsed.currency == "UNKNOWN":
        result.unverifiable.append(
            f"salary_benchmark_check: currency could not be read from '{salary_raw}'."
        )
        return

    data = salary_benchmarks()
    fx = data.get("fx_to_bdt_approx", {})
    monthly = to_monthly(parsed)
    monthly_bdt = convert_to_bdt(monthly, parsed.currency, fx)
    if monthly_bdt is None:
        result.unverifiable.append(
            f"salary_benchmark_check: no conversion rate for {parsed.currency}."
        )
        return

    matched = None
    for row in data.get("benchmarks", []):
        dest_ok = _alias_match(dest_raw, row.get("destination_aliases", []))
        if not dest_ok:
            continue
        role_aliases = row.get("role_aliases", [])
        role_ok = not job_raw or _alias_match(job_raw, role_aliases)
        if role_ok or not job_raw:
            matched = row
            if job_raw and _alias_match(job_raw, role_aliases):
                break
    if matched is None:
        result.unverifiable.append(
            f"salary_benchmark_check: no screening range for '{dest_raw}' / '{job_raw or 'unknown role'}'."
        )
        return

    high = float(matched["typical_high"])
    high_bdt = convert_to_bdt(high, matched["currency"], fx)
    if high_bdt is None:
        result.unverifiable.append("salary_benchmark_check: could not convert the benchmark currency.")
        return
    limit = high_bdt * float(matched.get("unrealistic_multiplier", 4))
    if monthly_bdt > limit:
        evidence = extraction.salary.source_snippet or salary_raw
        result.flags.append(
            _flag(
                "R05_salary",
                evidence,
                extra_en=(
                    f"Stated pay is about BDT {monthly_bdt:,.0f}/month equivalent; "
                    f"screening high band is about BDT {high_bdt:,.0f} "
                    f"({matched.get('source', '')})."
                ),
                extra_bn=(
                    f"ঘোষিত বেতন মাসে প্রায় {monthly_bdt:,.0f} টাকা সমতুল্য; "
                    f"এই স্ক্রিনিং সীমার উপরের দিক প্রায় {high_bdt:,.0f} টাকা।"
                ),
            )
        )
        result.questions_to_ask.append(
            {
                "en": _rule("R05_salary")["question_en"],
                "bn": _rule("R05_salary")["question_bn"],
            }
        )


def check_missing_clauses(
    extraction: OfferExtraction,
    document_text: str,
    result: VerificationResult,
) -> None:
    missing: list[str] = []
    for field_name, label in ESSENTIAL_FIELDS:
        field: ExtractedField = getattr(extraction, field_name)
        if not _field_value(field):
            missing.append(label)

    haystack = document_text.lower() if document_text else ""
    if not haystack:
        result.unverifiable.append(
            "missing_clause_scan: full document text was not available, "
            "so overtime, medical, return ticket and similar clauses could not be searched."
        )
    else:
        for label, needles in KEYWORD_CLAUSES:
            if not any(needle.lower() in haystack for needle in needles):
                missing.append(label)

    result.missing_clauses = missing
    if not missing:
        return

    rule = _rule("R06_missing_clauses")
    weight = min(int(rule.get("max_weight", 24)), int(rule["weight"]) * len(missing))
    evidence = ", ".join(missing)
    result.flags.append(
        _flag(
            "R06_missing_clauses",
            evidence,
            extra_en=f"Missing: {evidence}.",
            extra_bn=f"অনুপস্থিত: {evidence}।",
            weight_override=weight,
        )
    )
    result.questions_to_ask.append(
        {
            "en": rule["question_en"],
            "bn": rule["question_bn"],
        }
    )


def verify_offer(
    extraction: OfferExtraction,
    document_text: str = "",
) -> VerificationResult:
    result = VerificationResult()
    check_agency_license(extraction, result)
    check_fee_cap(extraction, result)
    check_salary_benchmark(extraction, result)
    check_missing_clauses(extraction, document_text, result)
    return result
