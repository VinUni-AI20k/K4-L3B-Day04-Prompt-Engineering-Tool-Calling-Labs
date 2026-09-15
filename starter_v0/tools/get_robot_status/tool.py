from __future__ import annotations

from typing import Any

from tools import _hospital as hospital
from tools._shared import err


TOOL = "get_robot_status"
CHECKS = ("all", "location", "battery", "errors", "mission")


def get_robot_status(robot_id: str = "", check: str = "all") -> dict[str, Any]:
    try:
        wanted_id = hospital.normalize_id(robot_id)
        if wanted_id is None or not hospital.ROBOT_ID_PATTERN.fullmatch(wanted_id):
            return hospital.fail(TOOL, "invalid_robot_id", "robot_id must look like AMR-02.", robot_id=robot_id)
        wanted_check = hospital.normalize_choice(check, "all")
        if wanted_check not in CHECKS:
            return hospital.fail(TOOL, "invalid_check", f"check must be one of: {', '.join(CHECKS)}.", check=check)

        fleet = hospital.load("robots")
        robot = hospital.by_id(fleet["robots"], "robot_id").get(wanted_id)
        if robot is None:
            return hospital.fail(TOOL, "robot_not_found", f"No robot {wanted_id} in the fleet.", robot_id=wanted_id)

        location = hospital.by_id(hospital.load("locations")["locations"], "location_id").get(robot["location_id"], {})
        mission_id = robot["current_mission_id"]
        sections = {
            "location": {
                "location_id": robot["location_id"],
                "location_name": location.get("name"),
                "floor": robot["floor"],
            },
            "battery": {
                "battery_pct": robot["battery_pct"],
                "charging": robot["status"] == "charging",
                "dispatch_min_battery_pct": fleet["dispatch_min_battery_pct"],
            },
            "errors": {"errors": robot["errors"]},
            "mission": {"current_mission": hospital.known_missions().get(mission_id) if mission_id else None},
        }
        if wanted_check == "all":
            data = {key: value for section in sections.values() for key, value in section.items()}
        else:
            data = sections[wanted_check]
        return {
            "tool": TOOL,
            "robot_id": wanted_id,
            "check": wanted_check,
            "robot": {"robot_id": wanted_id, "model": robot["model"], "status": robot["status"]},
            "data": data,
            "last_seen": robot["last_seen"],
            "snapshot_at": fleet["snapshot_at"],
        }
    except Exception as exc:
        return err(TOOL, exc)
