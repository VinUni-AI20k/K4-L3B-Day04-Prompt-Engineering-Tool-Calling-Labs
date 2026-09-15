from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err


HOTEL_FILE = ROOT / "tourism_data" / "hotels.json"
HOTEL_ID_PATTERN = re.compile(r"^HTL-[A-Z0-9]{3,5}$", re.IGNORECASE)


def lookup_hotel(hotel_id: str = "") -> dict[str, Any]:
    """Return info for a single hotel/resort by HTL-XXX identifier."""
    try:
        wanted_id = (hotel_id or "").strip().upper()
        if not wanted_id:
            return {"tool": "lookup_hotel", "error": "missing_hotel_id"}
        if not HOTEL_ID_PATTERN.fullmatch(wanted_id):
            return {
                "tool": "lookup_hotel",
                "hotel_id": wanted_id,
                "error": "invalid_hotel_id",
                "expected_format": "HTL-XXX (3-5 alphanumeric chars)",
            }
        data = json.loads(HOTEL_FILE.read_text(encoding="utf-8"))
        hotel = next((item for item in data["hotels"] if item["hotel_id"] == wanted_id), None)
        if hotel is None:
            return {"tool": "lookup_hotel", "hotel_id": wanted_id, "error": "hotel_not_found"}
        return {"tool": "lookup_hotel", "hotel": hotel, "snapshot_at": data.get("snapshot_at", "")}
    except Exception as exc:
        return err("lookup_hotel", exc)
