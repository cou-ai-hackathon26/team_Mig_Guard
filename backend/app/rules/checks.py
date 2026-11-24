from typing import Any, Dict, List, Optional


def _get_val(extracted: Dict[str, Any], field: str) -> str:
    """Safely extract lowercase string value from an extracted field object."""
    item = extracted.get(field)
    if isinstance(item, dict) and item.get("value") is not None:
        return str(item["value"]).strip().lower()
    return ""


def _get_num(extracted: Dict[str, Any], field: str) -> Optional[float]:
    """Safely extract numeric value from an extracted number field object."""
    item = extracted.get(field)
    if isinstance(item, dict) and item.get("value") is not None:
        try:
            return float(item["value"])
        except (ValueError, TypeError):
            return None
    return None


def _get_snippet(extracted: Dict[str, Any], field: str) -> str:
    """Safely extract the source snippet for UI evidence highlighting."""
    item = extracted.get(field)
    if isinstance(item, dict) and item.get("source_snippet"):
        return str(item["source_snippet"]).strip()
    return ""


def check_r01_no_written_contract(extracted: Dict[str, Any]) -> Optional[str]:
    doc_type = str(extracted.get("document_type", "")).lower()
    if doc_type in {"chat_screenshot", "social_post"}:
        return f"Document type detected as {doc_type}"
    return None


def check_r02_non_work_visa(extracted: Dict[str, Any]) -> Optional[str]:
    visa = _get_val(extracted, "visa_type")
    bad_visas = ("tourist", "visit", "business", "vistor", "ট্যুরিস্ট", "ভিজিট")
    if any(word in visa for word in bad_visas):
        return _get_snippet(extracted, "visa_type") or visa
    return None


def check_r03_cash_or_unspecified_fee(extracted: Dict[str, Any]) -> Optional[str]:
    method = _get_val(extracted, "payment_method")
    if any(word in method for word in ("cash", "no receipt", "hand to hand", "নগদ")):
        return _get_snippet(extracted, "payment_method") or method
    return None


def check_r04_high_risk_scam_pattern(
    extracted: Dict[str, Any], patterns: Dict[str, Any]
) -> Optional[str]:
    dest = _get_val(extracted, "destination")
    title = _get_val(extracted, "job_title")
    high_risk_countries = [c.lower() for c in patterns.get("high_risk_countries", [])]
    scam_keywords = [k.lower() for k in patterns.get("scam_job_keywords", [])]

    country_match = any(c in dest for c in high_risk_countries)
    job_match = any(k in title for k in scam_keywords)

    if country_match and job_match:
        dest_snip = _get_snippet(extracted, "destination") or dest
        job_snip = _get_snippet(extracted, "job_title") or title
        return f"{dest_snip} | {job_snip}"
    return None


def check_r05_unrealistic_salary(
    extracted: Dict[str, Any], benchmarks_data: Dict[str, Any]
) -> Optional[str]:
    dest = _get_val(extracted, "destination")
    job_title = _get_val(extracted, "job_title")
    salary = _get_num(extracted, "salary_amount")
    if not dest or salary is None:
        return None

    benchmarks = benchmarks_data.get("benchmarks", {})
    if isinstance(benchmarks, list):
        for row in benchmarks:
            destination_aliases = [str(alias).lower() for alias in row.get("destination_aliases", [])]
            if not any(alias in dest for alias in destination_aliases):
                continue
            role_aliases = [str(alias).lower() for alias in row.get("role_aliases", [])]
            if job_title and role_aliases and not any(alias in job_title for alias in role_aliases):
                continue
            high = row.get("typical_high")
            low = row.get("typical_low")
            multiplier = row.get("unrealistic_multiplier", 2.5)
            if high is not None and salary > float(high) * float(multiplier):
                return _get_snippet(extracted, "salary_amount") or f"{salary} (unusually high for {dest})"
            if low is not None and salary < float(low) * 0.6:
                return _get_snippet(extracted, "salary_amount") or f"{salary} (unusually low for {dest})"
        return None

    for country_key, info in benchmarks.items():
        normalized_country = country_key.replace("_", " ").lower()
        if normalized_country not in dest:
            continue
        role_range = None
        for k, v in info.items():
            if isinstance(v, dict) and ("min" in v or "max" in v):
                role_prefix = k.split("_")[0]
                if role_prefix and role_prefix in job_title:
                    role_range = v
                    break
                if "general_worker" in k or role_range is None:
                    role_range = v
        if not role_range:
            continue
        min_sal = role_range.get("min")
        max_sal = role_range.get("max")
        if max_sal is not None and salary > max_sal * 2.5:
            return _get_snippet(extracted, "salary_amount") or f"{salary} (unusually high for {normalized_country})"
        if min_sal is not None and salary < min_sal * 0.6:
            return _get_snippet(extracted, "salary_amount") or f"{salary} (unusually low for {normalized_country})"
    return None

def check_r06_missing_critical_clauses(extracted: Dict[str, Any]) -> Optional[str]:
    required_fields = [
        "employer",
        "job_title",
        "salary_amount",
        "duration",
        "working_hours",
        "accommodation",
        "return_ticket",
    ]
    missing = [f for f in required_fields if not _get_val(extracted, f)]
    if len(missing) >= 2:
        return "Missing: " + ", ".join(missing)
    return None


def check_r07_missing_or_unlisted_agency_license(
    extracted: Dict[str, Any], agencies_data: Dict[str, Any]
) -> Optional[str]:
    lic = _get_val(extracted, "license_number")
    if not lic or lic in {"none", "n/a", "null"}:
        return "No RL license number found in document"

    raw_agencies = agencies_data.get("agencies", {})
    known_agencies: Dict[str, Any] = {}
    if isinstance(raw_agencies, dict):
        known_agencies = {k.lower(): v for k, v in raw_agencies.items()}
    elif isinstance(raw_agencies, list):
        for entry in raw_agencies:
            if isinstance(entry, dict) and entry.get("license_no"):
                known_agencies[str(entry["license_no"]).lower()] = entry

    # Only flag unlisted if real BMET agencies have been populated (more than the sample entry)
    real_entries = {k: v for k, v in known_agencies.items() if k != "rl-0000"}
    normalized_lic = lic.replace(" ", "").replace("-", "").lower()
    normalized_known = {k.replace(" ", "").replace("-", "").lower(): v for k, v in real_entries.items()}
    if real_entries and normalized_lic in normalized_known:
        status = str(normalized_known[normalized_lic].get("status", ""))
        if status.lower() in {"expired", "cancelled", "suspended"}:
            return f"License {lic.upper()} is {status} in official BMET registry"
    return None


def check_r07_missing_agency_license(extracted: Dict[str, Any]) -> Optional[str]:
    """Backward-compatible alias for check_r07 without external agencies dict."""
    return check_r07_missing_or_unlisted_agency_license(extracted, {})



def check_r08_sign_on_arrival(extracted: Dict[str, Any]) -> Optional[str]:
    clauses: List[str] = extracted.get("raw_red_flag_clauses") or []
    triggers = ("sign on arrival", "contract after arrival", "sign after reaching", "পৌঁছানোর পর চুক্তি")
    for clause in clauses:
        if any(t in clause.lower() for t in triggers):
            return clause
    return None


def check_r09_passport_retention(extracted: Dict[str, Any]) -> Optional[str]:
    clauses: List[str] = extracted.get("raw_red_flag_clauses") or []
    triggers = ("hold passport", "keep passport", "passport retention", "submit passport to employer", "পাসপোর্ট জমা")
    for clause in clauses:
        if any(t in clause.lower() for t in triggers):
            return clause
    return None


def check_r10_salary_deduction_debt_bond(extracted: Dict[str, Any]) -> Optional[str]:
    clauses: List[str] = extracted.get("raw_red_flag_clauses") or []
    triggers = (
        "deduct from salary",
        "salary deduction",
        "deduct visa cost",
        "repay training",
        "debt",
        "বেতন থেকে কাটা",
        "বেতন কেটে",
        "বেতন থেকে টাকা কাটা",
    )
    for clause in clauses:
        if any(t in clause.lower() for t in triggers):
            return clause
    return None


def check_r11_pressure_tactics(extracted: Dict[str, Any]) -> Optional[str]:
    clauses: List[str] = extracted.get("raw_red_flag_clauses") or []
    triggers = ("pay today", "urgent", "limited seats", "last chance", "today only", "আজই টাকা", "সীমিত সিট")
    for clause in clauses:
        if any(t in clause.lower() for t in triggers):
            return clause
    return None


def check_r12_personal_mobile_payment(extracted: Dict[str, Any]) -> Optional[str]:
    method = _get_val(extracted, "payment_method")
    triggers = ("personal", "bkash", "nagad", "rocket", "before visa", "বিকাশ", "নগদ")
    if any(t in method for t in triggers):
        return _get_snippet(extracted, "payment_method") or method
    return None


def check_r13_social_media_only_no_office(extracted: Dict[str, Any]) -> Optional[str]:
    channel = _get_val(extracted, "contact_channel")
    address = _get_val(extracted, "employer_address")
    social_triggers = ("whatsapp", "telegram", "facebook", "messenger", "imo", "হোয়াটসঅ্যাপ", "টেলিগ্রাম", "ফেসবুক")
    if any(s in channel for s in social_triggers) and not address:
        return _get_snippet(extracted, "contact_channel") or channel
    return None


def check_r14_too_good_to_be_true_bundle(
    extracted: Dict[str, Any], benchmarks_data: Dict[str, Any]
) -> Optional[str]:
    fee = _get_num(extracted, "fee_asked")
    ticket = _get_val(extracted, "return_ticket")
    clauses = " ".join(extracted.get("raw_red_flag_clauses") or []).lower()

    free_visa = (fee == 0) or ("free visa" in clauses) or ("ফ্রি ভিসা" in clauses)
    free_ticket = ("free" in ticket) or ("free ticket" in clauses) or ("ফ্রি টিকিট" in clauses)
    high_sal = check_r05_unrealistic_salary(extracted, benchmarks_data) is not None

    if free_visa and free_ticket and high_sal:
        return "Free visa + free ticket + unusually high salary"
    return None


def check_r15_unverifiable_employer(extracted: Dict[str, Any]) -> Optional[str]:
    employer = _get_val(extracted, "employer")
    address = _get_val(extracted, "employer_address")
    if not employer or employer in {"unknown", "n/a", "confidential", "company"}:
        return "Employer name missing or generic"
    if not address:
        return f"No physical address provided for employer: {employer}"
    return None