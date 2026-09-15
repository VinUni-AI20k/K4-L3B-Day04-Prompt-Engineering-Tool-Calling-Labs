from __future__ import annotations

from typing import Any


def clarify(
    question: str,
    response_type: str = "free_text",
    missing_fields: list[str] | None = None,
) -> dict[str, Any]:
    if response_type not in {"yes_no", "free_text"}:
        return {"tool": "clarify", "error": "response_type phải là yes_no hoặc free_text"}
    return {
        "tool": "clarify",
        "question": question,
        "response_type": response_type,
        "missing_fields": missing_fields or [],
        "awaiting_user": True,
    }
