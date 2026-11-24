"""Attach knowledge-base passages to flags and optionally rewrite explanations."""

from __future__ import annotations

import json
import logging

from app.api.schemas import Flag, KnowledgePassage
from app.rag.retriever import retrieve_for_flag

logger = logging.getLogger(__name__)


def ground_flags(flags: list[Flag]) -> list[Flag]:
    """Always attach retrieved passages. Keep catalog text if the LLM is skipped."""
    grounded: list[Flag] = []
    for flag in flags:
        rows = retrieve_for_flag(flag.title_en, flag.evidence_snippet, flag.kb_ids)
        passages = [
            KnowledgePassage(
                id=row["id"],
                title=row["title"],
                text=row["text"],
                source=row["source"],
                source_url=row.get("source_url", ""),
            )
            for row in rows
        ]
        extra_en = ""
        extra_bn = ""
        if passages:
            first = passages[0]
            extra_en = f" Official note: {first.text}"
            extra_bn = f" সূত্র: {first.text}"
        grounded.append(
            flag.model_copy(
                update={
                    "passages": passages,
                    "explanation_en": (flag.explanation_en + extra_en).strip(),
                    "explanation_bn": (flag.explanation_bn + extra_bn).strip(),
                }
            )
        )
    return grounded


def try_llm_explanations(flags: list[Flag]) -> list[Flag]:
    """Best-effort rewrite. Any failure leaves the grounded catalog text in place."""
    if not flags:
        return flags
    try:
        from app.llm.client import generate_json
    except Exception:
        return flags

    payload = []
    for flag in flags:
        payload.append(
            {
                "rule_id": flag.rule_id,
                "title_en": flag.title_en,
                "evidence": flag.evidence_snippet,
                "passages": [
                    {
                        "id": p.id,
                        "text": p.text,
                        "source": p.source,
                    }
                    for p in flag.passages
                ],
            }
        )
    prompt_path = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "llm"
        / "prompts"
        / "explain_system.txt"
    )
    try:
        system = prompt_path.read_text(encoding="utf-8")
        data = generate_json(
            system_prompt=system,
            user_prompt=json.dumps(payload, ensure_ascii=False),
        )
    except Exception:
        logger.exception("Explanation LLM call failed; using catalog plus passages.")
        return flags

    by_id = {}
    for item in data.get("flags", []) if isinstance(data, dict) else []:
        if isinstance(item, dict) and item.get("rule_id"):
            by_id[item["rule_id"]] = item

    rewritten: list[Flag] = []
    for flag in flags:
        item = by_id.get(flag.rule_id)
        if not item:
            rewritten.append(flag)
            continue
        en = str(item.get("explanation_en") or "").strip()
        bn = str(item.get("explanation_bn") or "").strip()
        if not en or not bn:
            rewritten.append(flag)
            continue
        rewritten.append(
            flag.model_copy(
                update={
                    "explanation_en": en,
                    "explanation_bn": bn,
                }
            )
        )
    return rewritten


def explain_flags(flags: list[Flag], use_llm: bool = True) -> list[Flag]:
    grounded = ground_flags(flags)
    if use_llm:
        return try_llm_explanations(grounded)
    return grounded
