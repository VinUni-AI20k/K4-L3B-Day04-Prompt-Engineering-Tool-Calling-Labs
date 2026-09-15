from __future__ import annotations

from typing import Any

from tools.smartcharging_shared import find_vehicle, load_network


def lookup_vehicle(vehicle_id: str = "") -> dict[str, Any]:
    if not isinstance(vehicle_id, str):
        return {"tool": "lookup_vehicle", "error": "invalid_vehicle_id_type"}
    wanted = vehicle_id.strip().upper()
    if not wanted:
        return {"tool": "lookup_vehicle", "error": "missing_vehicle_id"}
    data = load_network()
    vehicle = find_vehicle(data, wanted)
    if vehicle is None:
        return {"tool": "lookup_vehicle", "vehicle_id": wanted, "error": "vehicle_not_found"}
    if vehicle["owner_id"] != data["authenticated_driver_id"]:
        return {"tool": "lookup_vehicle", "vehicle_id": wanted, "error": "forbidden_vehicle"}
    safe_vehicle = {key: value for key, value in vehicle.items() if key != "owner_id"}
    return {"tool": "lookup_vehicle", "vehicle": safe_vehicle, "snapshot_at": data["snapshot_at"]}

