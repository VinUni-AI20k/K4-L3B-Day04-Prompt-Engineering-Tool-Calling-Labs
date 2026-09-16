from __future__ import annotations

from typing import Any

from tools import _hospital as hospital
from tools._shared import err


TOOL = "get_location_info"


def get_location_info(location_id: str = "") -> dict[str, Any]:
    try:
        data = hospital.load("locations")
        locations = hospital.by_id(data["locations"], "location_id")
        wanted_id = hospital.normalize_id(location_id)
        location = locations.get(wanted_id) if wanted_id else None
        if location is None:
            return hospital.fail(
                TOOL,
                "location_not_found",
                f"Unknown location_id. Valid IDs: {', '.join(locations)}.",
                location_id=location_id,
            )
        return {
            "tool": TOOL,
            "location_id": wanted_id,
            "location": {
                "name": location["name"],
                "floor": location["floor"],
                "zone": location["zone"],
                "restricted": location["restricted"],
                "amr_access": location["amr_access"],
                "notes": location["notes"],
            },
            "snapshot_at": data["snapshot_at"],
        }
    except Exception as exc:
        return err(TOOL, exc)
