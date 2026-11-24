"""Turn rule weights into danger / caution / fewer_concerns. Never 'safe'."""

from __future__ import annotations

from app.api.schemas import Flag
from app.data.loader import catalog

VERDICT_LABELS = {
    "danger": {
        "en": "Danger",
        "bn": "বিপদ",
    },
    "caution": {
        "en": "Caution",
        "bn": "সতর্কতা",
    },
    "fewer_concerns": {
        "en": "Fewer concerns found",
        "bn": "কম উদ্বেগ পাওয়া গেছে",
    },
}


def score_flags(flags: list[Flag]) -> tuple[str, int]:
    """Return (verdict, score 0-100). Higher score means more concern."""
    thresholds = catalog().get("verdicts", {})
    danger_min = int(thresholds.get("danger_min_score", 70))
    caution_min = int(thresholds.get("caution_min_score", 35))

    total = sum(max(0, flag.weight) for flag in flags)
    score = max(0, min(100, total))

    has_high = any(flag.severity == "high" for flag in flags)
    if score >= danger_min or (has_high and score >= caution_min + 15):
        verdict = "danger"
    elif score >= caution_min or has_high:
        verdict = "caution"
    else:
        verdict = "fewer_concerns"
    return verdict, score


def audio_script_bn(verdict: str, flags: list[Flag], missing_clauses: list[str]) -> str:
    label = VERDICT_LABELS.get(verdict, VERDICT_LABELS["caution"])["bn"]
    parts = [
        f"ফলাফল: {label}।",
        "এটি নিরাপদ বলে ঘোষণা নয়। বিএমইটি বা প্রবাসবন্ধু ১৬১৩৫ এ নিশ্চিত করুন।",
    ]
    if flags:
        titles = "। ".join(flag.title_bn for flag in flags[:4])
        parts.append(f"প্রধান সতর্কতা: {titles}।")
    if missing_clauses:
        parts.append("চুক্তিতে কিছু বিষয় নেই। টাকা দেওয়ার আগে লিখে নিন।")
    return " ".join(parts)
