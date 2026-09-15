from __future__ import annotations

from typing import Any

from tools.smartcharging_shared import find_station, load_network


def check_station_status(station_id: str = "") -> dict[str, Any]:
    if not isinstance(station_id, str):
        return {"tool": "check_station_status", "error": "invalid_station_id_type"}
    wanted = station_id.strip().upper()
    if not wanted:
        return {"tool": "check_station_status", "error": "missing_station_id"}
    data = load_network()
    station = find_station(data, wanted)
    if station is None:
        return {"tool": "check_station_status", "station_id": wanted, "error": "station_not_found"}
    return {"tool": "check_station_status", "station": station, "snapshot_at": data["snapshot_at"]}

