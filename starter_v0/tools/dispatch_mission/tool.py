from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tools import _hospital as hospital
from tools._shared import err


TOOL = "dispatch_mission"
MISSION_TYPES = ("delivery", "pickup", "return_to_base")
PRIORITIES = ("normal", "urgent")
BASE_LOCATION_ID = "DOCK_1"
UNAVAILABLE_STATUSES = ("error", "on_mission")


def dispatch_mission(
    robot_id: str = "",
    destination_id: str = "",
    mission_type: str = "delivery",
    priority: str = "normal",
    confirmed: bool = False,
) -> dict[str, Any]:
    try:
        # 1. Input shape.
        wanted_robot = hospital.normalize_id(robot_id)
        if wanted_robot is None or not hospital.ROBOT_ID_PATTERN.fullmatch(wanted_robot):
            return hospital.fail(TOOL, "invalid_robot_id", "robot_id must look like AMR-02.", robot_id=robot_id)
        locations = hospital.by_id(hospital.load("locations")["locations"], "location_id")
        wanted_destination = hospital.normalize_id(destination_id)
        if wanted_destination not in locations:
            return hospital.fail(
                TOOL,
                "invalid_destination_id",
                f"destination_id must be one of: {', '.join(locations)}.",
                destination_id=destination_id,
            )
        wanted_type = hospital.normalize_choice(mission_type, "delivery")
        if wanted_type not in MISSION_TYPES:
            return hospital.fail(TOOL, "invalid_mission_type", f"mission_type must be one of: {', '.join(MISSION_TYPES)}.", mission_type=mission_type)
        wanted_priority = hospital.normalize_choice(priority, "normal")
        if wanted_priority not in PRIORITIES:
            return hospital.fail(TOOL, "invalid_priority", f"priority must be one of: {', '.join(PRIORITIES)}.", priority=priority)

        # 2. Robot exists.
        fleet = hospital.load("robots")
        robot = hospital.by_id(fleet["robots"], "robot_id").get(wanted_robot)
        if robot is None:
            return hospital.fail(TOOL, "robot_not_found", f"No robot {wanted_robot} in the fleet.", robot_id=wanted_robot)

        # 3-6. Operational guards.
        if wanted_type == "return_to_base" and wanted_destination != BASE_LOCATION_ID:
            return hospital.fail(
                TOOL,
                "invalid_destination_for_mission_type",
                f"return_to_base missions must go to {BASE_LOCATION_ID}.",
                destination_id=wanted_destination,
            )
        if locations[wanted_destination]["restricted"]:
            return hospital.fail(
                TOOL,
                "restricted_destination",
                f"{wanted_destination} is a restricted area; the assistant cannot send robots there.",
                destination_id=wanted_destination,
            )
        if robot["status"] in UNAVAILABLE_STATUSES:
            return hospital.fail(
                TOOL,
                "robot_unavailable",
                f"{wanted_robot} is {robot['status']} and cannot take a new mission.",
                robot_id=wanted_robot,
                robot_status=robot["status"],
                current_mission_id=robot["current_mission_id"],
                error_codes=[item["code"] for item in robot["errors"]],
            )
        min_battery = fleet["dispatch_min_battery_pct"]
        if wanted_type != "return_to_base" and robot["battery_pct"] < min_battery:
            return hospital.fail(
                TOOL,
                "low_battery",
                f"{wanted_robot} battery {robot['battery_pct']}% is below the {min_battery}% dispatch minimum.",
                robot_id=wanted_robot,
                battery_pct=robot["battery_pct"],
            )

        # 7. Explicit confirmation.
        request = {
            "robot_id": wanted_robot,
            "destination_id": wanted_destination,
            "mission_type": wanted_type,
            "priority": wanted_priority,
        }
        if confirmed is not True:
            return {
                "tool": TOOL,
                "status": "needs_confirmation",
                "message": "Dispatch only after the operator explicitly confirms this robot, destination and mission.",
                "pending": request,
            }

        # 8. Record the mission.
        origin = robot["location_id"]
        if origin == wanted_destination:
            eta_min = 0
        else:
            route = hospital.find_route(hospital.load("routes"), origin, wanted_destination)
            eta_min = route["eta_min"] if route else None
        mission_id = hospital.next_mission_id()
        payload = {
            "mission_id": mission_id,
            **request,
            "origin_id": origin,
            "status": "created",
            "eta_min": eta_min,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "educational_local_mock",
        }
        path = hospital.write_mission_record(f"{mission_id}.json", payload)
        return {"tool": TOOL, "status": "created", "mission_id": mission_id, **request, "eta_min": eta_min, "path": str(path)}
    except Exception as exc:
        return err(TOOL, exc)
