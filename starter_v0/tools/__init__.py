from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .clarify.tool import ask_user
from .check_station_status.tool import check_station_status
from .create_reservation.tool import create_reservation
from .find_charging_offers.tool import find_charging_offers
from .lookup_vehicle.tool import lookup_vehicle
from .check_service_status.tool import check_service_status
from .create_ticket.tool import create_ticket
from .format_incident_report.tool import format_incident_report
from .inspect_device.tool import inspect_device
from .lookup_user.tool import lookup_user
from .policy.tool import search_company_policy
from .search_kb.tool import search_kb
from .search_device_info.tool import search_device_info


# Retain the original Helpdesk implementations as the required reference track.
# They are not exposed to the SmartCharging model through artifacts/tools.yaml.
LEGACY_HELPDESK_TOOL_FUNCTIONS = {
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


# Active registry for the chosen SmartCharging domain. These names match the
# declarations and the frozen SmartCharging base evaluation set.
TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "lookup_vehicle": lookup_vehicle,
    "check_station_status": check_station_status,
    "find_charging_offers": find_charging_offers,
    "create_reservation": create_reservation,
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
