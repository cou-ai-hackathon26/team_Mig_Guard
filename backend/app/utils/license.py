"""Normalise recruiting-licence numbers such as RL-1857, rl 1857, 1857."""

from __future__ import annotations

import re


def normalize_license(value: str | None) -> str | None:
    if not value:
        return None
    compact = re.sub(r"[^a-zA-Z0-9]", "", value).upper()
    if compact.startswith("RL"):
        digits = compact[2:]
        if digits.isdigit():
            return "RL" + digits.zfill(4)
        return None
    if compact.isdigit() and 3 <= len(compact) <= 5:
        return "RL" + compact.zfill(4)
    return None
