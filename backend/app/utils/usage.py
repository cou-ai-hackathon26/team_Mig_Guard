"""Process-local LLM usage guard to prevent runaway retry costs."""

from __future__ import annotations

import threading
from datetime import datetime, timezone

from app.config import settings


class UsageLimitExceeded(Exception):
    """Raised when the configured daily model budget is exhausted."""


class UsageGuard:
    def __init__(self) -> None:
        self._day = ""
        self._calls = 0
        self._cost = 0.0
        self._lock = threading.Lock()

    def reserve(self) -> None:
        day = datetime.now(timezone.utc).date().isoformat()
        with self._lock:
            if day != self._day:
                self._day = day
                self._calls = 0
                self._cost = 0.0
            next_cost = self._cost + settings.llm_estimated_cost_usd
            if (
                self._calls >= settings.llm_daily_call_limit
                or next_cost > settings.llm_daily_cost_limit_usd
            ):
                raise UsageLimitExceeded("The daily AI usage limit has been reached.")
            self._calls += 1
            self._cost = next_cost


usage_guard = UsageGuard()
