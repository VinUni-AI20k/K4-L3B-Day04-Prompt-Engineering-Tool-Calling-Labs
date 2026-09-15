from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tools._shared import ROOT

# Built-in IT tools (kept as reference per rubric)
from tools.clarify.tool import ask_user
from tools.check_service_status.tool import check_service_status
from tools.create_ticket.tool import create_ticket as create_it_ticket
from tools.format_incident_report.tool import format_incident_report
from tools.inspect_device.tool import inspect_device
from tools.lookup_user.tool import lookup_user
from tools.policy.tool import search_company_policy
from tools.search_kb.tool import search_kb
from tools.search_device_info.tool import search_device_info

# Tourism domain tools (new in v0+ for the VietTravel Helpdesk)
from tools.search_travel_kb.tool import search_travel_kb
from tools.check_booking_status.tool import check_booking_status
from tools.lookup_customer.tool import lookup_customer
from tools.lookup_hotel.tool import lookup_hotel
from tools.travel_policy.tool import search_travel_policy
from tools.create_support_ticket.tool import create_support_ticket


# Tourism tool registry (used by v0+ runs after the domain switch).
TOURISM_TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "search_travel_kb": search_travel_kb,
    "check_booking_status": check_booking_status,
    "lookup_customer": lookup_customer,
    "lookup_hotel": lookup_hotel,
    "travel_policy": search_travel_policy,
    "create_support_ticket": create_support_ticket,
    # Universal helpers (also registered so reports/transcripts can use them)
    "format_incident_report": format_incident_report,
}

# Backwards-compatible alias used by the existing run_eval.py.
TOOL_FUNCTIONS = TOURISM_TOOL_FUNCTIONS


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
