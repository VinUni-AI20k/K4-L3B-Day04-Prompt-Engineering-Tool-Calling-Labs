from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tools import _hospital as hospital
from tools._shared import err


TOOL = "cancel_mission"
FINAL_STATUSES = ("completed", "cancelled")


def cancel_mission(mission_id: str = "", confirmed: bool = False) -> dict[str, Any]:
    try:
        wanted_id = hospital.normalize_id(mission_id)
        if wanted_id is None or not hospital.MISSION_ID_PATTERN.fullmatch(wanted_id):
            return hospital.fail(TOOL, "invalid_mission_id", "mission_id must look like MS-0012.", mission_id=mission_id)
        mission = hospital.known_missions().get(wanted_id)
        if mission is None:
            return hospital.fail(TOOL, "mission_not_found", f"No mission {wanted_id}.", mission_id=wanted_id)
        if mission["status"] in FINAL_STATUSES:
            return hospital.fail(
                TOOL,
                "mission_not_cancellable",
                f"{wanted_id} is already {mission['status']}.",
                mission_id=wanted_id,
                mission_status=mission["status"],
            )

        target = {
            "mission_id": wanted_id,
            "robot_id": mission["robot_id"],
            "destination_id": mission["destination_id"],
        }
        if confirmed is not True:
            return {
                "tool": TOOL,
                "status": "needs_confirmation",
                "message": "Cancel only after the operator explicitly confirms this mission.",
                "pending": target,
            }

        payload = {
            **target,
            "status": "cancelled",
            "previous_status": mission["status"],
            "cancelled_at": datetime.now(timezone.utc).isoformat(),
            "source": "educational_local_mock",
        }
        path = hospital.write_mission_record(f"{wanted_id}.cancelled.json", payload)
        return {"tool": TOOL, "status": "cancelled", **target, "robot_status_after": "idle", "path": str(path)}
    except Exception as exc:
        return err(TOOL, exc)
