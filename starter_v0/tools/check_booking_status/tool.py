from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err


BOOKING_FILE = ROOT / "tourism_data" / "bookings.json"
BOOKING_ID_PATTERN = re.compile(r"^BK-\d{4,6}$", re.IGNORECASE)


def check_booking_status(booking_id: str = "") -> dict[str, Any]:
    """Return the status of a single booking by its BK-XXXX identifier."""
    try:
        wanted_id = (booking_id or "").strip().upper()
        if not wanted_id:
            return {"tool": "check_booking_status", "error": "missing_booking_id"}
        if not BOOKING_ID_PATTERN.fullmatch(wanted_id):
            return {
                "tool": "check_booking_status",
                "booking_id": wanted_id,
                "error": "invalid_booking_id",
                "expected_format": "BK-XXXX (4-6 digits)",
            }
        data = json.loads(BOOKING_FILE.read_text(encoding="utf-8"))
        booking = next((item for item in data["bookings"] if item["booking_id"] == wanted_id), None)
        if booking is None:
            return {
                "tool": "check_booking_status",
                "booking_id": wanted_id,
                "error": "booking_not_found",
            }
        return {"tool": "check_booking_status", "booking": booking, "snapshot_at": data.get("snapshot_at", "")}
    except Exception as exc:
        return err("check_booking_status", exc)
