from __future__ import annotations

import hashlib
import json
import math
from datetime import timedelta
from typing import Any

from tools.smartcharging_shared import (
    OFFER_CACHE,
    find_route,
    find_vehicle,
    load_network,
    parse_datetime,
)


PREFERENCES = {"earliest_finish", "lowest_cost", "shortest_distance"}


def _offer_id(request: dict[str, Any], station_id: str) -> str:
    value = json.dumps({**request, "station_id": station_id}, ensure_ascii=False, sort_keys=True)
    return "OFF-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:12].upper()


def find_charging_offers(
    vehicle_id: str = "",
    current_soc: float | None = None,
    target_soc: float | None = None,
    deadline: str = "",
    origin: str = "",
    preference: str = "earliest_finish",
    top_k: int = 3,
    allow_partial: bool = True,
) -> dict[str, Any]:
    required = {
        "vehicle_id": vehicle_id,
        "current_soc": current_soc,
        "target_soc": target_soc,
        "deadline": deadline,
        "origin": origin,
    }
    missing = [
        name
        for name, value in required.items()
        if value is None or (isinstance(value, str) and not value.strip())
    ]
    if missing:
        return {"tool": "find_charging_offers", "error": "missing_required_fields", "missing_fields": missing}
    if not isinstance(vehicle_id, str) or not isinstance(deadline, str) or not isinstance(origin, str):
        return {"tool": "find_charging_offers", "error": "invalid_input_type"}
    try:
        current = float(current_soc)
        target = float(target_soc)
    except (TypeError, ValueError):
        return {"tool": "find_charging_offers", "error": "invalid_soc_type"}
    if not 0 <= current < target <= 100:
        return {"tool": "find_charging_offers", "error": "invalid_soc_range"}
    preference_value = (preference or "earliest_finish").strip().lower()
    if preference_value not in PREFERENCES:
        return {"tool": "find_charging_offers", "error": "invalid_preference"}
    try:
        limit = min(5, max(1, int(top_k)))
        deadline_at = parse_datetime(deadline.strip())
    except (TypeError, ValueError) as exc:
        return {"tool": "find_charging_offers", "error": "invalid_deadline_or_top_k", "message": str(exc)}

    data = load_network()
    snapshot_at = parse_datetime(data["snapshot_at"])
    if deadline_at <= snapshot_at:
        return {"tool": "find_charging_offers", "error": "deadline_not_after_snapshot"}
    wanted_vehicle = vehicle_id.strip().upper()
    vehicle = find_vehicle(data, wanted_vehicle)
    if vehicle is None:
        return {"tool": "find_charging_offers", "vehicle_id": wanted_vehicle, "error": "vehicle_not_found"}
    if vehicle["owner_id"] != data["authenticated_driver_id"]:
        return {"tool": "find_charging_offers", "vehicle_id": wanted_vehicle, "error": "forbidden_vehicle"}

    request = {
        "vehicle_id": wanted_vehicle,
        "current_soc": current,
        "target_soc": target,
        "deadline": deadline_at.isoformat(),
        "origin": origin.strip(),
        "preference": preference_value,
        "allow_partial": bool(allow_partial),
    }
    full: list[dict[str, Any]] = []
    partial: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    efficiency = 0.90
    requested_energy = vehicle["battery_capacity_kwh"] * (target - current) / 100

    for station in data["stations"]:
        station_id = station["station_id"]
        if station["status"] != "operational":
            excluded.append({"station_id": station_id, "reason": f"station_{station['status']}"})
            continue
        connector = next(
            (item for item in station["connectors"] if item["type"] == vehicle["connector_type"]),
            None,
        )
        if connector is None:
            excluded.append({"station_id": station_id, "reason": "incompatible_connector"})
            continue
        route = find_route(data, origin, station_id)
        if route is None:
            excluded.append({"station_id": station_id, "reason": "missing_route_evidence"})
            continue
        arrival_at = snapshot_at + timedelta(minutes=route["travel_minutes"])
        start_at = max(arrival_at, parse_datetime(connector["next_available_at"]))
        power_kw = min(
            float(vehicle["max_dc_power_kw"]),
            float(connector["max_power_kw"]),
            float(station["site_available_power_kw"]),
        )
        if power_kw <= 0 or start_at >= deadline_at:
            excluded.append({"station_id": station_id, "reason": "no_power_or_time_window"})
            continue
        minutes_for_full = max(1, math.ceil((requested_energy / efficiency) / power_kw * 60))
        full_finish = start_at + timedelta(minutes=minutes_for_full)
        completes_target = full_finish <= deadline_at
        if completes_target:
            expected_soc = target
            finish_at = full_finish
            grid_energy = requested_energy / efficiency
            verdict = "verified_feasible"
        elif allow_partial:
            usable_minutes = max(0, math.floor((deadline_at - start_at).total_seconds() / 60))
            grid_energy = power_kw * usable_minutes / 60
            expected_soc = min(
                target,
                current + grid_energy * efficiency / vehicle["battery_capacity_kwh"] * 100,
            )
            if expected_soc <= current:
                excluded.append({"station_id": station_id, "reason": "no_deliverable_energy"})
                continue
            finish_at = deadline_at
            verdict = "verified_partial"
        else:
            excluded.append({"station_id": station_id, "reason": "target_misses_deadline"})
            continue
        offer = {
            "offer_id": _offer_id(request, station_id),
            "driver_id": data["authenticated_driver_id"],
            "vehicle_id": wanted_vehicle,
            "station_id": station_id,
            "station_name": station["name"],
            "distance_km": route["distance_km"],
            "travel_minutes": route["travel_minutes"],
            "start_time": start_at.isoformat(),
            "finish_time": finish_at.isoformat(),
            "power_kw": power_kw,
            "expected_soc": round(expected_soc, 2),
            "estimated_cost_vnd": int(round(grid_energy * station["price_vnd_per_kwh"])),
            "verified": True,
            "verdict": verdict,
            "route_evidence_id": route["evidence_id"],
            "verification": {
                "solver": "deterministic_lab_optimizer_v0",
                "snapshot_at": data["snapshot_at"],
                "checks": ["ownership", "connector", "route", "port_window", "site_power", "deadline"],
            },
        }
        OFFER_CACHE[offer["offer_id"]] = offer
        (full if completes_target else partial).append(offer)

    offers = full if full else partial
    if preference_value == "lowest_cost":
        offers.sort(key=lambda item: (item["estimated_cost_vnd"], item["finish_time"]))
    elif preference_value == "shortest_distance":
        offers.sort(key=lambda item: (item["distance_km"], item["finish_time"]))
    else:
        offers.sort(key=lambda item: (item["finish_time"], item["distance_km"]))
    selected = offers[:limit]
    return {
        "tool": "find_charging_offers",
        "status": "verified_offers" if selected else "no_verified_offer",
        "request": request,
        "offers": selected,
        "excluded_candidates": excluded,
        "snapshot_at": data["snapshot_at"],
        "decision_boundary": "A verified offer is a proposal, not a reservation.",
    }

