from __future__ import annotations

from typing import Any

from tools import _hospital as hospital
from tools._shared import err


TOOL = "list_robots"
STATUSES = ("all", "idle", "on_mission", "charging", "error")


def list_robots(status: str = "all", min_battery: int = 0) -> dict[str, Any]:
    try:
        wanted_status = hospital.normalize_choice(status, "all")
        if wanted_status not in STATUSES:
            return hospital.fail(TOOL, "invalid_status", f"status must be one of: {', '.join(STATUSES)}.", status=status)
        if (
            isinstance(min_battery, bool)
            or not isinstance(min_battery, (int, float))
            or min_battery != int(min_battery)
            or not 0 <= min_battery <= 100
        ):
            return hospital.fail(TOOL, "invalid_min_battery", "min_battery must be a whole number from 0 to 100.", min_battery=min_battery)
        threshold = int(min_battery)

        fleet = hospital.load("robots")
        robots = [
            {
                "robot_id": robot["robot_id"],
                "status": robot["status"],
                "battery_pct": robot["battery_pct"],
                "location_id": robot["location_id"],
            }
            for robot in sorted(fleet["robots"], key=lambda item: item["robot_id"])
            if (wanted_status == "all" or robot["status"] == wanted_status) and robot["battery_pct"] >= threshold
        ]
        return {
            "tool": TOOL,
            "filters": {"status": wanted_status, "min_battery": threshold},
            "count": len(robots),
            "robots": robots,
            "snapshot_at": fleet["snapshot_at"],
        }
    except Exception as exc:
        return err(TOOL, exc)
