from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .clarify.tool import ask_user
from .search_catalog.tool import search_catalog
from .check_price.tool import check_price
from .check_compatibility.tool import check_compatibility
from .lookup_customer.tool import lookup_customer
from .format_quote.tool import format_quote
from .policy.tool import search_company_policy
from .create_order.tool import create_order
from .search_product_info.tool import search_product_info

# Optional backwards-compatibility imports for starter helpdesk
from .check_service_status.tool import check_service_status
from .create_ticket.tool import create_ticket
from .format_incident_report.tool import format_incident_report
from .inspect_device.tool import inspect_device
from .lookup_user.tool import lookup_user
from .search_kb.tool import search_kb
from .search_device_info.tool import search_device_info


TOOL_FUNCTIONS = {
    # Core PC Assistant Tools
    "clarify": ask_user,
    "search_catalog": search_catalog,
    "check_price": check_price,
    "check_compatibility": check_compatibility,
    "lookup_customer": lookup_customer,
    "format_quote": format_quote,
    "policy": search_company_policy,
    "create_order": create_order,
    "search_product_info": search_product_info,

    # Helpdesk fallbacks
    "search_kb": search_kb,
    "search_device_info": search_device_info,
    "check_service_status": check_service_status,
    "inspect_device": inspect_device,
    "lookup_user": lookup_user,
    "format_incident_report": format_incident_report,
    "create_ticket": create_ticket,
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
