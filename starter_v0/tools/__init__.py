from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .cancel_mission.tool import cancel_mission
from .clarify.tool import ask_user
from .check_service_status.tool import check_service_status
from .create_ticket.tool import create_ticket
from .dispatch_mission.tool import dispatch_mission
from .format_incident_report.tool import format_incident_report
from .get_location_info.tool import get_location_info
from .get_robot_status.tool import get_robot_status
from .get_route_info.tool import get_route_info
from .inspect_device.tool import inspect_device
from .list_robots.tool import list_robots
from .lookup_user.tool import lookup_user
from .policy.tool import search_company_policy
from .search_kb.tool import search_kb
from .search_device_info.tool import search_device_info


# These names are part of the fixed evaluation contract. Keep built-in names
# unchanged in tools.yaml, this registry and the supplied datasets. Improve
# descriptions and compatible schemas. Register any team-built bonus tool in
# this registry and tools.yaml, then test it with team-authored cases.
TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "search_kb": search_kb,
    "search_device_info": search_device_info,
    "check_service_status": check_service_status,
    "inspect_device": inspect_device,
    "lookup_user": lookup_user,
    "format_incident_report": format_incident_report,
    "policy": search_company_policy,
    "create_ticket": create_ticket,
    # Hospital AMR Operations Assistant — see docs/AMR_TOOL_CONTRACT.md.
    "get_robot_status": get_robot_status,
    "list_robots": list_robots,
    "get_location_info": get_location_info,
    "get_route_info": get_route_info,
    "dispatch_mission": dispatch_mission,
    "cancel_mission": cancel_mission,
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
