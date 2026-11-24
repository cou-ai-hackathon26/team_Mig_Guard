"""Load official reference files once per process."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

DATA_DIR = Path(__file__).resolve().parent
RULES_CATALOG = Path(__file__).resolve().parent.parent / "rules" / "catalog.yaml"
KB_PATH = Path(__file__).resolve().parent.parent / "rag" / "kb" / "passages.json"


def _read_json(name: str) -> Any:
    path = DATA_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def licensed_agencies() -> dict[str, dict[str, str]]:
    payload = _read_json("licensed_agencies.json")
    index: dict[str, dict[str, str]] = {}
    for row in payload.get("agencies", []):
        key = str(row.get("license_no", "")).upper()
        if key:
            index[key] = row
    return index


@lru_cache(maxsize=1)
def agencies_meta() -> dict[str, Any]:
    payload = _read_json("licensed_agencies.json")
    return {
        "source_url": payload.get("source_url", ""),
        "retrieved": payload.get("retrieved", ""),
        "note": payload.get("note", ""),
        "count": len(payload.get("agencies", [])),
    }


@lru_cache(maxsize=1)
def fee_caps() -> dict[str, Any]:
    return _read_json("fee_caps.json")


@lru_cache(maxsize=1)
def salary_benchmarks() -> dict[str, Any]:
    return _read_json("salary_benchmarks.json")


@lru_cache(maxsize=1)
def helplines() -> list[dict[str, str]]:
    return list(_read_json("helplines.json").get("helplines", []))


@lru_cache(maxsize=1)
def catalog() -> dict[str, Any]:
    return yaml.safe_load(RULES_CATALOG.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def kb_passages() -> list[dict[str, Any]]:
    return json.loads(KB_PATH.read_text(encoding="utf-8"))
