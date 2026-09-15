from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .clarify.tool import ask_user
from .check_service_status.tool import check_service_status
from .create_ticket.tool import create_ticket
from .format_incident_report.tool import format_incident_report
from .inspect_device.tool import inspect_device
from .lookup_user.tool import lookup_user
from .policy.tool import search_company_policy
from .search_kb.tool import search_kb
from .search_device_info.tool import search_device_info
from .search_products.tool import search_products
from .get_product_details.tool import get_product_details
from .check_inventory.tool import check_inventory
from .compare_products.tool import compare_products
from .check_promotion.tool import check_promotion
from .search_policy.tool import search_policy
from .lookup_customer.tool import lookup_customer
from .get_order_status.tool import get_order_status
from .create_order.tool import create_order


# These names are part of the fixed evaluation contract. Keep built-in names
# unchanged in tools.yaml, this registry and the supplied datasets. Improve
# descriptions and compatible schemas. Register any team-built bonus tool in
# this registry and tools.yaml, then test it with team-authored cases.
HELPDESK_TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "search_kb": search_kb,
    "search_device_info": search_device_info,
    "check_service_status": check_service_status,
    "inspect_device": inspect_device,
    "lookup_user": lookup_user,
    "format_incident_report": format_incident_report,
    "policy": search_company_policy,
    "create_ticket": create_ticket,
}

# Sales is the active baseline; the IT registry above is retained unchanged.
SALES_TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "search_products": search_products, "get_product_details": get_product_details,
    "check_inventory": check_inventory, "compare_products": compare_products,
    "check_promotion": check_promotion, "search_policy": search_policy,
    "lookup_customer": lookup_customer, "get_order_status": get_order_status,
    "create_order": create_order,
}
TOOL_FUNCTIONS = SALES_TOOL_FUNCTIONS


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
