import json
from pathlib import Path
from typing import Any, Dict, List
import yaml

from app.rules import checks

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "rules" / "catalog.yaml"
PATTERNS_PATH = BASE_DIR / "data" / "high_risk_patterns.json"
BENCHMARKS_PATH = BASE_DIR / "data" / "salary_benchmarks.json"
AGENCIES_PATH = BASE_DIR / "data" / "licensed_agencies.json"


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog() -> Dict[str, Any]:
    return yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))


def load_patterns() -> Dict[str, Any]:
    return _load_json(PATTERNS_PATH)


def load_benchmarks() -> Dict[str, Any]:
    return _load_json(BENCHMARKS_PATH)


def load_agencies() -> Dict[str, Any]:
    data = _load_json(AGENCIES_PATH)
    agencies = data.get("agencies", {})
    if isinstance(agencies, list):
        return {
            str(row.get("license_no", "")).lower(): row
            for row in agencies
            if row.get("license_no")
        }
    return agencies


def evaluate_rules(extracted: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs all 15 deterministic red-flag checks on extracted offer fields.
    Returns triggered flags and unverifiable items (never returns 'safe').
    """
    catalog = load_catalog()
    patterns = load_patterns()
    benchmarks = load_benchmarks()
    agencies = load_agencies()

    rule_runners = {
        "R01_NO_WRITTEN_CONTRACT": lambda d: checks.check_r01_no_written_contract(d),
        "R02_NON_WORK_VISA": lambda d: checks.check_r02_non_work_visa(d),
        "R03_CASH_OR_UNSPECIFIED_FEE": lambda d: checks.check_r03_cash_or_unspecified_fee(d),
        "R04_HIGH_RISK_SCAM_PATTERN": lambda d: checks.check_r04_high_risk_scam_pattern(d, patterns),
        "R05_UNREALISTIC_SALARY": lambda d: checks.check_r05_unrealistic_salary(d, benchmarks),
        "R06_MISSING_CRITICAL_CLAUSES": lambda d: checks.check_r06_missing_critical_clauses(d),
        "R07_MISSING_AGENCY_LICENSE": lambda d: checks.check_r07_missing_or_unlisted_agency_license(d, agencies),
        "R08_SIGN_ON_ARRIVAL": lambda d: checks.check_r08_sign_on_arrival(d),
        "R09_PASSPORT_RETENTION": lambda d: checks.check_r09_passport_retention(d),
        "R10_SALARY_DEDUCTION_DEBT_BOND": lambda d: checks.check_r10_salary_deduction_debt_bond(d),
        "R11_PRESSURE_TACTICS": lambda d: checks.check_r11_pressure_tactics(d),
        "R12_PERSONAL_MOBILE_PAYMENT": lambda d: checks.check_r12_personal_mobile_payment(d),
        "R13_SOCIAL_MEDIA_ONLY_NO_OFFICE": lambda d: checks.check_r13_social_media_only_no_office(d),
        "R14_TOO_GOOD_TO_BE_TRUE_BUNDLE": lambda d: checks.check_r14_too_good_to_be_true_bundle(d, benchmarks),
        "R15_UNVERIFIABLE_EMPLOYER": lambda d: checks.check_r15_unverifiable_employer(d),
    }

    flags: List[Dict[str, Any]] = []
    for rule_id, runner in rule_runners.items():
        evidence = runner(extracted)
        if evidence and rule_id in catalog:
            meta = catalog[rule_id]
            flags.append({
                "rule_id": rule_id,
                "severity": meta["severity"],
                "weight": meta["weight"],
                "title_en": meta["title_en"],
                "title_bn": meta["title_bn"],
                "explanation_en": meta["explanation_en"],
                "explanation_bn": meta["explanation_bn"],
                "question_en": meta["question_en"],
                "question_bn": meta["question_bn"],
                "evidence_snippet": evidence,
            })

    unverifiable: List[str] = []
    if not checks._get_val(extracted, "employer"):
        unverifiable.append("Employer identity could not be verified (missing from document).")
    if not checks._get_val(extracted, "license_number"):
        unverifiable.append("Recruiting agency license could not be verified against BMET list.")
    if checks._get_num(extracted, "fee_asked") is None:
        unverifiable.append("Recruitment fee amount not stated; could not compare against official fee cap.")

    return {
        "flags": flags,
        "unverifiable": unverifiable,
    }