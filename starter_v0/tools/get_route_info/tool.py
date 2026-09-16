from __future__ import annotations

from typing import Any

from tools import _hospital as hospital
from tools._shared import err


TOOL = "get_route_info"


def get_route_info(robot_id: str = "", destination_id: str = "") -> dict[str, Any]:
    try:
        wanted_robot = hospital.normalize_id(robot_id)
        if wanted_robot is None or not hospital.ROBOT_ID_PATTERN.fullmatch(wanted_robot):
            return hospital.fail(TOOL, "invalid_robot_id", "robot_id must look like AMR-02.", robot_id=robot_id)
        robot = hospital.by_id(hospital.load("robots")["robots"], "robot_id").get(wanted_robot)
        if robot is None:
            return hospital.fail(TOOL, "robot_not_found", f"No robot {wanted_robot} in the fleet.", robot_id=wanted_robot)

        locations = hospital.by_id(hospital.load("locations")["locations"], "location_id")
        wanted_destination = hospital.normalize_id(destination_id)
        if wanted_destination not in locations:
            return hospital.fail(
                TOOL,
                "location_not_found",
                f"Unknown destination_id. Valid IDs: {', '.join(locations)}.",
                destination_id=destination_id,
            )

        routes = hospital.load("routes")
        origin = robot["location_id"]
        result = {
            "tool": TOOL,
            "robot_id": wanted_robot,
            "from_location_id": origin,
            "destination_id": wanted_destination,
        }
        if origin == wanted_destination:
            return {**result, "distance_m": 0, "eta_min": 0, "elevator": None, "elevator_status": None,
                    "blocked_segments": [], "snapshot_at": routes["snapshot_at"]}

        route = hospital.find_route(routes, origin, wanted_destination)
        if route is None:
            return hospital.fail(TOOL, "no_route", f"No known route from {origin} to {wanted_destination}.", **result)
        elevators = hospital.by_id(routes["elevators"], "elevator_id")
        segments = hospital.by_id(routes["blocked_segments"], "segment_id")
        return {
            **result,
            "distance_m": route["distance_m"],
            "eta_min": route["eta_min"],
            "elevator": route["elevator"],
            "elevator_status": elevators[route["elevator"]]["status"] if route["elevator"] else None,
            "blocked_segments": [segments[segment_id] for segment_id in route["blocked_segments"]],
            "snapshot_at": routes["snapshot_at"],
        }
    except Exception as exc:
        return err(TOOL, exc)
