from __future__ import annotations

import json
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "smartcharging_data" / "network.json"
RESERVATION_DIR = ROOT / "reservations"
OFFER_CACHE: dict[str, dict[str, Any]] = {}


def load_network() -> dict[str, Any]:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def fold_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn").strip()


def parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timezone_required")
    return parsed


def find_vehicle(data: dict[str, Any], vehicle_id: str) -> dict[str, Any] | None:
    wanted = (vehicle_id or "").strip().upper()
    return next((item for item in data["vehicles"] if item["vehicle_id"] == wanted), None)


def find_station(data: dict[str, Any], station_id: str) -> dict[str, Any] | None:
    wanted = (station_id or "").strip().upper()
    return next((item for item in data["stations"] if item["station_id"] == wanted), None)


def find_route(data: dict[str, Any], origin: str, station_id: str) -> dict[str, Any] | None:
    wanted_origin = fold_text(origin or "")
    wanted_station = (station_id or "").strip().upper()
    return next(
        (
            item
            for item in data["routes"]
            if fold_text(item["origin"]) == wanted_origin and item["station_id"] == wanted_station
        ),
        None,
    )


def find_offer(offer_id: str) -> dict[str, Any] | None:
    wanted = (offer_id or "").strip().upper()
    if wanted in OFFER_CACHE:
        return OFFER_CACHE[wanted]
    data = load_network()
    return next((item for item in data["seed_offers"] if item["offer_id"] == wanted), None)

