from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .check_compatibility.tool import check_compatibility
from .check_price.tool import check_price
from .clarify.tool import ask_user
from .create_order.tool import create_order
from .format_quote.tool import format_quote
from .lookup_customer.tool import lookup_customer
from .policy.tool import search_store_policy
from .search_catalog.tool import search_catalog


# PC Seller Assistant tool registry. The IT Helpdesk tools are kept on disk for
# reference but are not registered here, so they are not exposed to the model.
# Keep these names identical in artifacts/tools.yaml and in the eval datasets.
TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "search_catalog": search_catalog,
    "check_price": check_price,
    "check_compatibility": check_compatibility,
    "lookup_customer": lookup_customer,
    "format_quote": format_quote,
    "policy": search_store_policy,
    "create_order": create_order,
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
