from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err


CUSTOMER_FILE = ROOT / "tourism_data" / "customers.json"
CUSTOMER_ID_PATTERN = re.compile(r"^CUST-\d{3,6}$", re.IGNORECASE)


def lookup_customer(customer_id: str = "") -> dict[str, Any]:
    """Return a masked profile of a single customer by CUST-XXXX identifier."""
    try:
        wanted_id = (customer_id or "").strip().upper()
        if not wanted_id:
            return {"tool": "lookup_customer", "error": "missing_customer_id"}
        if not CUSTOMER_ID_PATTERN.fullmatch(wanted_id):
            return {
                "tool": "lookup_customer",
                "customer_id": wanted_id,
                "error": "invalid_customer_id",
                "expected_format": "CUST-XXXX (3-6 digits)",
            }
        data = json.loads(CUSTOMER_FILE.read_text(encoding="utf-8"))
        customer = next((item for item in data["customers"] if item["customer_id"] == wanted_id), None)
        if customer is None:
            return {"tool": "lookup_customer", "customer_id": wanted_id, "error": "customer_not_found"}
        # Mask sensitive fields
        safe_view = {
            "customer_id": customer["customer_id"],
            "name": customer.get("name"),
            "loyalty_tier": customer.get("loyalty_tier"),
            "active_booking_ids": customer.get("active_booking_ids", []),
            "pii_masked": True,
        }
        return {"tool": "lookup_customer", "customer": safe_view, "snapshot_at": data.get("snapshot_at", "")}
    except Exception as exc:
        return err("lookup_customer", exc)
