from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .budget_forecast_alert.tool import budget_forecast_alert
from .clarify.tool import clarify
from .get_category_breakdown.tool import get_category_breakdown
from .get_summary.tool import get_summary
from .record_transaction.tool import record_transaction
from .search_financial_advice.tool import search_financial_advice


TOOL_FUNCTIONS = {
    "get_summary": get_summary,
    "get_category_breakdown": get_category_breakdown,
    "record_transaction": record_transaction,
    "clarify": clarify,
    "search_financial_advice": search_financial_advice,
    "budget_forecast_alert": budget_forecast_alert,
}


def load_tool_declarations(path: Path) -> list[dict[str, Any]]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))["tools"]


def to_openai_tools(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "type": "function",
        "function": {
            "name": item["name"],
            "description": item.get("description", ""),
            "parameters": item.get("parameters", {"type": "object", "properties": {}}),
        },
    } for item in declarations]
