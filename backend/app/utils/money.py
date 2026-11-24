"""Parse salary and fee strings into an amount, currency and period."""

from __future__ import annotations

import re
from dataclasses import dataclass

CURRENCY_ALIASES = {
    "tk": "BDT",
    "taka": "BDT",
    "bdt": "BDT",
    "টাকা": "BDT",
    "usd": "USD",
    "us$": "USD",
    "$": "USD",
    "dollar": "USD",
    "dollars": "USD",
    "qar": "QAR",
    "riyal": "QAR",
    "riyals": "QAR",
    "sar": "SAR",
    "aed": "AED",
    "dirham": "AED",
    "dirhams": "AED",
    "myr": "MYR",
    "rm": "MYR",
    "ringgit": "MYR",
    "sgd": "SGD",
    "omr": "OMR",
    "kwd": "KWD",
    "bhd": "BHD",
    "eur": "EUR",
    "euro": "EUR",
}


@dataclass(frozen=True)
class MoneyAmount:
    amount: float
    currency: str
    period: str | None  # month, year, day, or None if unknown
    raw: str


def _normalize_number(token: str) -> float | None:
    cleaned = token.strip().replace(" ", "")
    if not cleaned:
        return None
    # Bangladesh / India grouping: 1,50,000
    if re.fullmatch(r"\d{1,3}(,\d{2})+(,\d{3})?", cleaned):
        return float(cleaned.replace(",", ""))
    # Western grouping: 1,500.00 or 1500.00
    if re.fullmatch(r"\d{1,3}(,\d{3})+(\.\d+)?", cleaned):
        return float(cleaned.replace(",", ""))
    if re.fullmatch(r"\d+(\.\d+)?", cleaned):
        return float(cleaned)
    return None


def parse_money(text: str | None) -> MoneyAmount | None:
    if not text:
        return None
    raw = text.strip()
    if not raw:
        return None

    lower = raw.lower()
    period = None
    if re.search(r"per\s*year|annual|/year|yearly", lower):
        period = "year"
    elif re.search(r"per\s*day|/day|daily", lower):
        period = "day"
    elif re.search(r"per\s*month|monthly|/month|a month", lower):
        period = "month"

    currency = None
    for alias, code in CURRENCY_ALIASES.items():
        if re.search(rf"(?<![a-z]){re.escape(alias)}(?![a-z])", lower):
            currency = code
            break
    if currency is None and "টাকা" in raw:
        currency = "BDT"

    lakh = re.search(r"([\d,.]+)\s*(lakh|lac|লক্ষ)", lower)
    if lakh:
        base = _normalize_number(lakh.group(1).replace(",", ""))
        if base is not None:
            amount = base * 100_000
            return MoneyAmount(amount, currency or "BDT", period, raw)

    candidates = re.findall(r"[\d,]+(?:\.\d+)?", raw)
    amounts: list[float] = []
    for token in candidates:
        value = _normalize_number(token)
        if value is not None and value > 0:
            amounts.append(value)
    if not amounts:
        return None

    amount = max(amounts)
    return MoneyAmount(amount, currency or "UNKNOWN", period, raw)


def to_monthly(amount: MoneyAmount) -> float:
    if amount.period == "year":
        return amount.amount / 12.0
    if amount.period == "day":
        return amount.amount * 30.0
    return amount.amount


def convert_to_bdt(amount: float, currency: str, fx: dict) -> float | None:
    rate = fx.get(currency.upper())
    if not isinstance(rate, (int, float)):
        return None
    return amount * float(rate)
