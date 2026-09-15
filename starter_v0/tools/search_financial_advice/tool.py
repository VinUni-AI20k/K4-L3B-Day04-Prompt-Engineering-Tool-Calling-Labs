from __future__ import annotations

import re
from typing import Any

from tools._shared import error, fold, read_data


def search_financial_advice(topic: str) -> dict[str, Any]:
    try:
        query_terms = set(re.findall(r"[a-z0-9]+", fold(topic)))
        knowledge = read_data("financial_knowledge.json")
        ranked = []
        for item in knowledge:
            text_terms = set(re.findall(r"[a-z0-9]+", fold(" ".join(map(str, item.values())))))
            score = len(query_terms & text_terms)
            if score:
                ranked.append((score, item))
        matches = [item for _, item in sorted(ranked, key=lambda pair: pair[0], reverse=True)[:3]]
        return {
            "tool": "search_financial_advice", "topic": topic, "results": matches,
            "available_topics": [] if matches else [item["topic"] for item in knowledge],
            "disclaimer": "Thông tin tham khảo, không thay thế tư vấn tài chính chuyên nghiệp.",
        }
    except Exception as exc:
        return error("search_financial_advice", exc)
