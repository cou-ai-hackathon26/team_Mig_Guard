"""Tiny keyword retriever over the curated knowledge-base passages."""

from __future__ import annotations

import re

from app.data.loader import kb_passages


def _tokens(text: str) -> set[str]:
    return {part for part in re.split(r"[^a-z0-9\u0980-\u09FF]+", text.lower()) if len(part) > 2}


def retrieve_for_flag(flag_title: str, evidence: str, kb_ids: list[str], limit: int = 3) -> list[dict]:
    passages = kb_passages()
    by_id = {row["id"]: row for row in passages}
    selected: list[dict] = []
    seen: set[str] = set()

    for kid in kb_ids:
        row = by_id.get(kid)
        if row and row["id"] not in seen:
            selected.append(row)
            seen.add(row["id"])

    query = _tokens(f"{flag_title} {evidence}")
    ranked: list[tuple[int, dict]] = []
    for row in passages:
        if row["id"] in seen:
            continue
        bag = _tokens(
            " ".join(
                [
                    row.get("title", ""),
                    row.get("text", ""),
                    " ".join(row.get("keywords") or []),
                ]
            )
        )
        overlap = len(query & bag)
        if overlap:
            ranked.append((overlap, row))
    ranked.sort(key=lambda item: item[0], reverse=True)
    for _, row in ranked:
        if len(selected) >= limit:
            break
        selected.append(row)
        seen.add(row["id"])

    return [
        {
            "id": row["id"],
            "title": row.get("title", ""),
            "text": row.get("text", ""),
            "source": row.get("source", ""),
            "source_url": row.get("source_url", ""),
        }
        for row in selected[:limit]
    ]
