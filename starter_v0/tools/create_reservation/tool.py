from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from tools.smartcharging_shared import RESERVATION_DIR, find_offer, find_station, find_vehicle, load_network


def create_reservation(offer_id: str = "", confirmed: bool = False) -> dict[str, Any]:
    if not isinstance(offer_id, str):
        return {"tool": "create_reservation", "error": "invalid_offer_id_type"}
    wanted = offer_id.strip().upper()
    if not wanted:
        return {"tool": "create_reservation", "error": "missing_offer_id"}
    if confirmed is not True:
        return {
            "tool": "create_reservation",
            "offer_id": wanted,
            "status": "needs_confirmation",
        }
    offer = find_offer(wanted)
    if offer is None:
        return {"tool": "create_reservation", "offer_id": wanted, "error": "offer_not_found_or_expired"}
    if offer.get("verified") is not True:
        return {"tool": "create_reservation", "offer_id": wanted, "error": "offer_not_verified"}
    data = load_network()
    if offer.get("driver_id") != data["authenticated_driver_id"]:
        return {"tool": "create_reservation", "offer_id": wanted, "error": "forbidden_offer"}
    vehicle = find_vehicle(data, str(offer.get("vehicle_id") or ""))
    station = find_station(data, str(offer.get("station_id") or ""))
    if vehicle is None or vehicle["owner_id"] != data["authenticated_driver_id"]:
        return {"tool": "create_reservation", "offer_id": wanted, "error": "vehicle_revalidation_failed"}
    if station is None or station["status"] != "operational" or station["site_available_power_kw"] <= 0:
        return {"tool": "create_reservation", "offer_id": wanted, "error": "station_revalidation_failed"}

    now = datetime.now(timezone.utc)
    reservation_id = "RES-" + hashlib.sha256(f"{wanted}|{now.isoformat()}".encode()).hexdigest()[:10].upper()
    payload = {
        "reservation_id": reservation_id,
        "offer_id": wanted,
        "driver_id": data["authenticated_driver_id"],
        "vehicle_id": offer["vehicle_id"],
        "station_id": offer["station_id"],
        "start_time": offer["start_time"],
        "finish_time": offer["finish_time"],
        "expected_soc": offer["expected_soc"],
        "estimated_cost_vnd": offer["estimated_cost_vnd"],
        "status": "confirmed",
        "created_at": now.isoformat(),
        "source": "educational_local_mock",
    }
    RESERVATION_DIR.mkdir(parents=True, exist_ok=True)
    path = RESERVATION_DIR / f"{reservation_id}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "tool": "create_reservation",
        "status": "created",
        "reservation_id": reservation_id,
        "offer_id": wanted,
        "reverified": True,
        "path": str(path),
    }

